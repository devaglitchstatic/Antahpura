#!/usr/bin/env python3
"""
prompt_assembler.py — Antahpura runtime prompt assembler.

Loads a chat preset, a world_info lorebook, and a character card V2, then
assembles a complete prompt for a single turn.

Contract:
  - Preset provides: system/impersonation framing + sampling parameters
  - World_info provides: shared canonical lorebook entries (keyword-matched)
  - Character card provides: identity, voice, scenario, and private lorebook
  - Scene provides: current chapter, phase, location, participants
  - Chat history provides: prior turns
  - User message provides: this turn's input

Output:
  {
    "prompt": "<full assembled prompt string>",
    "sampling_parameters": {...},
    "sections": [{"role": "...", "label": "...", "content": "..."}],
    "diagnostics": {"world_entries_matched": N, ...}
  }

Usage:
    python prompt_assembler.py \
        --preset path/to/Antarvani.json \
        --world-info path/to/world_info.json \
        --card path/to/main_princess-kumari-rati_...json \
        --scene runtime/current_scene.json \
        --user "My lord, may I ask about the mandala?" \
        --output assembled_prompt.json
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ============================================================================
# Token counting (approximation)
# ============================================================================

def count_tokens(text: str) -> int:
    """
    Approximate token count. Real tokenizers vary; for budgeting, use
    words * 1.3 which is close enough for English and Sanskritized prose.
    """
    if not text:
        return 0
    return int(len(text.split()) * 1.3)


# ============================================================================
# Entry matching
# ============================================================================

def normalize(text: str) -> str:
    return re.sub(r"[^\w\s]", " ", text.lower()).split()


def matches_entry(entry: dict, haystack: str, scan_depth: int = 999) -> bool:
    """
    Return True if any of entry['keys'] appears in the haystack.
    scan_depth is applied at the caller level (see match_entries).
    """
    if not entry.get("enabled", True):
        return False

    keys = [k for k in entry.get("key", []) if k]
    if not keys:
        return False

    hay = haystack.lower()
    return any(k.lower() in hay for k in keys)


def match_entries(entries: dict | list, haystack: str,
                  scan_depth: int, token_budget: int) -> list[dict]:
    """
    Filter entries by keyword match, sort by insertion_order then priority,
    and truncate to fit token_budget.

    SillyTavern-like behavior:
      - constant=True entries always fire
      - selective=True entries require a secondary match (we skip secondary
        checking; primary key match is sufficient for the assembler MVP)
    """
    if isinstance(entries, dict):
        items = list(entries.values())
    else:
        items = list(entries)

    matched = []
    for e in items:
        if not e.get("enabled", True):
            continue
        if e.get("constant", False):
            matched.append(e)
            continue
        if matches_entry(e, haystack, scan_depth):
            matched.append(e)

    # Sort: lower insertion_order first, then higher priority first
    matched.sort(key=lambda e: (
        e.get("insertion_order", 0),
        -e.get("priority", 0),
    ))

    # Truncate by token budget
    out = []
    budget = token_budget
    for e in matched:
        content = e.get("content", "")
        cost = count_tokens(content)
        if cost <= budget:
            out.append(e)
            budget -= cost
        # else skip

    return out


# ============================================================================
# Section rendering
# ============================================================================

def render_world_entries(entries: list[dict]) -> str:
    parts = []
    for e in entries:
        name = e.get("name") or e.get("comment") or ""
        content = e.get("content", "")
        if name and not content.lstrip().startswith(f"[{name}]"):
            parts.append(f"[{name}]\n{content}")
        else:
            parts.append(content)
    return "\n\n".join(parts)


def render_character_book(entries: list[dict]) -> str:
    """Character book entries: prepend entry name for private entries."""
    parts = []
    for e in entries:
        name = e.get("name", "")
        content = e.get("content", "")
        if not content:
            continue
        if name:
            parts.append(f"[{name}]\n{content}")
        else:
            parts.append(content)
    return "\n\n".join(parts)


# ============================================================================
# Assembler
# ============================================================================

@dataclass
class AssembledPrompt:
    prompt: str
    sampling_parameters: dict
    sections: list
    diagnostics: dict


class PromptAssembler:
    def __init__(self, preset: dict, world_info: dict, card: dict,
                 scene: dict | None = None):
        self.preset = preset
        self.world_info = world_info
        self.card = card
        self.scene = scene or {}

        self.card_data = card.get("data", card)
        self.character_book = self.card_data.get("character_book", {})

    # ------------------------------------------------------------------
    def _build_haystack(self, user_message: str, chat_history: list[str]) -> str:
        """Combine recent chat + user message for keyword matching."""
        recent = " ".join(chat_history[-3:]) if chat_history else ""
        return f"{recent} {user_message}"

    # ------------------------------------------------------------------
    def _scene_header(self) -> str:
        if not self.scene:
            return ""
        parts = []
        for key in ("chapter", "title", "ritual", "phase"):
            v = self.scene.get(key)
            if v:
                parts.append(f"{key}: {v}")
        return "\n".join(parts)

    # ------------------------------------------------------------------
    def assemble(self, user_message: str,
                 chat_history: list[str] | None = None) -> AssembledPrompt:
        chat_history = chat_history or []
        haystack = self._build_haystack(user_message, chat_history)

        # --- Match world_info entries ---
        wi_scan_depth = self.world_info.get("scan_depth", 2)
        wi_budget = self.world_info.get("token_budget", 512)
        wi_entries = match_entries(
            self.world_info.get("entries", {}),
            haystack, wi_scan_depth, wi_budget,
        )

        # --- Match character_book entries ---
        cb_scan_depth = self.character_book.get("scan_depth", 4)
        cb_budget = self.character_book.get("token_budget", 2000)
        cb_entries = match_entries(
            self.character_book.get("entries", []),
            haystack, cb_scan_depth, cb_budget,
        )

        # --- Build layers ---
        sections = []

        # 1. Preset main prompt
        if self.preset.get("main_prompt"):
            sections.append({
                "role": "system",
                "label": "preset.main_prompt",
                "content": self.preset["main_prompt"],
            })

        # 2. Preset impersonation prompt (the chronicler voice)
        if self.preset.get("impersonation_prompt"):
            sections.append({
                "role": "system",
                "label": "preset.impersonation_prompt",
                "content": self.preset["impersonation_prompt"],
            })

        # 3. Card system prompt
        if self.card_data.get("system_prompt"):
            sections.append({
                "role": "system",
                "label": "card.system_prompt",
                "content": self.card_data["system_prompt"],
            })

        # 4. Scene header
        scene_hdr = self._scene_header()
        if scene_hdr:
            sections.append({
                "role": "system",
                "label": "scene.header",
                "content": scene_hdr,
            })

        # 5. Character description
        if self.card_data.get("description"):
            sections.append({
                "role": "system",
                "label": "card.description",
                "content": self.card_data["description"],
            })

        # 6. Scenario
        if self.card_data.get("scenario"):
            sections.append({
                "role": "system",
                "label": "card.scenario",
                "content": self.card_data["scenario"],
            })

        # 7. World info entries (shared lorebook)
        if wi_entries:
            sections.append({
                "role": "system",
                "label": f"world_info ({len(wi_entries)} entries)",
                "content": render_world_entries(wi_entries),
            })

        # 8. Character book entries (private lorebook)
        if cb_entries:
            sections.append({
                "role": "system",
                "label": f"character_book ({len(cb_entries)} entries)",
                "content": render_character_book(cb_entries),
            })

        # 9. Chat history
        for i, turn in enumerate(chat_history):
            sections.append({
                "role": "user" if i % 2 == 0 else "assistant",
                "label": f"history[{i}]",
                "content": turn,
            })

        # 10. First message + examples (only if no history)
        if not chat_history and self.card_data.get("first_mes"):
            sections.append({
                "role": "assistant",
                "label": "card.first_mes",
                "content": self.card_data["first_mes"],
            })

        # 11. User message
        sections.append({
            "role": "user",
            "label": "user",
            "content": user_message,
        })

        # 12. Post-history instructions
        if self.card_data.get("post_history_instructions"):
            sections.append({
                "role": "system",
                "label": "card.post_history_instructions",
                "content": self.card_data["post_history_instructions"],
            })

        # 13. Jailbreak / continuation prompt
        if self.preset.get("jailbreak_prompt"):
            sections.append({
                "role": "system",
                "label": "preset.jailbreak_prompt",
                "content": self.preset["jailbreak_prompt"],
            })

        # --- Serialize ---
        prompt_lines = []
        for s in sections:
            prompt_lines.append(f"### {s['label']}\n{s['content']}")
        prompt = "\n\n".join(prompt_lines)

        # --- Sampling parameters ---
        sampling = {
            k: self.preset.get(k) for k in (
                "temperature", "frequency_penalty", "presence_penalty",
                "top_p", "top_k", "top_a", "min_p", "repetition_penalty",
                "names_in_completion",
            ) if k in self.preset
        }

        # --- Diagnostics ---
        diagnostics = {
            "total_tokens_approx": count_tokens(prompt),
            "world_entries_matched": len(wi_entries),
            "world_entries_available": len(
                self.world_info.get("entries", {}) if isinstance(self.world_info.get("entries"), dict)
                else self.world_info.get("entries", [])
            ),
            "character_book_entries_matched": len(cb_entries),
            "character_book_entries_available": len(self.character_book.get("entries", [])),
            "chat_history_turns": len(chat_history),
            "sections": len(sections),
        }

        return AssembledPrompt(
            prompt=prompt,
            sampling_parameters=sampling,
            sections=sections,
            diagnostics=diagnostics,
        )


# ============================================================================
# CLI
# ============================================================================

def load_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preset", required=True)
    ap.add_argument("--world-info", required=True)
    ap.add_argument("--card", required=True)
    ap.add_argument("--scene", default=None)
    ap.add_argument("--user", required=True)
    ap.add_argument("--history", default=None,
                    help="Path to JSON array of prior turns (strings)")
    ap.add_argument("--output", default="assembled_prompt.json")
    args = ap.parse_args()

    preset = load_json(args.preset)
    world_info = load_json(args.world_info)
    card = load_json(args.card)
    scene = load_json(args.scene) if args.scene else {}
    history = load_json(args.history) if args.history else []

    assembler = PromptAssembler(preset, world_info, card, scene)
    result = assembler.assemble(args.user, history)

    out = {
        "schema": "antahpura.assembled_prompt",
        "version": "1.0",
        "prompt": result.prompt,
        "sampling_parameters": result.sampling_parameters,
        "sections": result.sections,
        "diagnostics": result.diagnostics,
    }

    Path(args.output).write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print("=" * 60)
    print("PROMPT ASSEMBLED")
    print("=" * 60)
    print(f"Approx tokens:     {result.diagnostics['total_tokens_approx']}")
    print(f"Sections:          {result.diagnostics['sections']}")
    print(f"World entries:     {result.diagnostics['world_entries_matched']} / "
          f"{result.diagnostics['world_entries_available']}")
    print(f"Character book:    {result.diagnostics['character_book_entries_matched']} / "
          f"{result.diagnostics['character_book_entries_available']}")
    print(f"History turns:     {result.diagnostics['chat_history_turns']}")
    print(f"Output:            {args.output}")
    print("=" * 60)


if __name__ == "__main__":
    main()