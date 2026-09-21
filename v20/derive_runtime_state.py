#!/usr/bin/env python3
"""
derive_runtime_state.py — derive per-character runtime state from the
canonical Chub card private character_book.

For each of the 14 canonical characters:
  1. Load the registry entry
  2. Load the card at characters/main_<chub_card_id>_spec_v2.json
  3. Extract every private character_book entry (Rahasya-*)
  4. Extract the teaching profile if present
  5. Cross-reference KAMA_CHARACTER_STATE.json
  6. Cross-reference character_kala_matrix.json
  7. Cross-reference relationship_system_v20.json
  8. Write a structured state file per character

Output directory: runtime/character_states/<char_id>.json
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "runtime" / "character_states"

RAHASYA_MAP = {
    "Rahasya-Pūrvavṛtta":      "origin",
    "Rahasya-Vaṃśa":           "lineage",
    "Rahasya-Saṃbandha":       "relationships",
    "Rahasya-Dṛśya-bodha":     "observation",
    "Rahasya-Sādhana":         "training",
    "Rahasya-Bhāva":           "hidden_current",
    "Rahasya-Rasa":            "rasa_profile",
    "Rahasya-Raṅga":           "scene_hooks",
    "Rahasya-Niyama":          "boundaries",
    "Rahasya-Vāk":             "voice_profile",
    "Rahasya-Citta":           "cognition",
    "Rahasya-Abhilāṣa":        "desire",
    "Rahasya-Smaraṇa":         "memory",
    "Rahasya-Pravṛtti":        "autonomous",
    "Rahasya-Saṃvidhāna":      "constitutional",
    "Rahasya-Mañca-bandha":    "stage",
    "Rahasya-Runtime":         "runtime",
    "Rahasya-Virodha":         "conflict",
    "Rahasya-Archive":         "archive",
    "Rahasya-Stage-Awareness": "stage_awareness",
}

KV_FIELDS = {"voice_profile", "cognition", "desire"}


def load(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def parse_rasa_profile(text: str) -> dict:
    out = {}
    for key, field in (
        ("Primary", "primary"),
        ("Secondary", "secondary"),
        ("Stabilizing undertone", "stabilizing"),
        ("Stabilizing", "stabilizing"),
    ):
        m = re.search(rf"{key}:\s*([^.\n]+)", text)
        if m and field not in out:
            out[field] = m.group(1).strip()
    return out


def parse_kv_block(text: str) -> dict:
    out = {}
    for part in re.split(r"[;\n]", text):
        if ":" in part:
            k, _, v = part.partition(":")
            out[k.strip()] = v.strip()
    return out


def extract_teaching_profile(entries: list[dict]):
    for e in entries:
        if e.get("name") == "Teaching Profile":
            body = e.get("content", "")
            try:
                return json.loads(body)
            except Exception:
                return {"raw": body}
    return None


def derive_character(entry: dict, card: dict, kama_state: dict,
                     kala_matrix: dict, rel_system: dict) -> dict:
    char_id = entry["id"]
    chub_id = entry.get("chub_card_id")
    card_data = card.get("data", card) if card else {}
    entries = card_data.get("character_book", {}).get("entries", []) or []

    private_constitution = {}
    raw_entries = {}
    for e in entries:
        name = e.get("name", "")
        if name in RAHASYA_MAP:
            field = RAHASYA_MAP[name]
            content = e.get("content", "")
            if field == "rasa_profile":
                private_constitution[field] = parse_rasa_profile(content)
            elif field in KV_FIELDS:
                private_constitution[field] = parse_kv_block(content)
            else:
                private_constitution[field] = content
            raw_entries[name] = content

    kala_block = None
    if kala_matrix:
        kala_block = kala_matrix.get("characters", {}).get(char_id)

    kama_block = None
    if kama_state:
        if char_id in kama_state:
            kama_block = kama_state[char_id]
        elif isinstance(kama_state.get("characters"), dict):
            kama_block = kama_state["characters"].get(char_id)

    rels = []
    axis = None
    if rel_system:
        for r in rel_system.get("relationships", []):
            if r.get("from") == char_id or r.get("to") == char_id:
                rels.append(r)
        ax = rel_system.get("sovereign_axis", {})
        if char_id in (ax.get("members") or []):
            axis = ax

    return {
        "schema": "antahpura.character_state_derived",
        "version": "1.0",
        "generated": datetime.now(timezone.utc).isoformat(),
        "character_id": char_id,
        "chub_card_id": chub_id,
        "display_name": entry.get("display_name"),
        "source_card": f"characters/main_{chub_id}_spec_v2.json" if chub_id else None,
        "identity": {
            "canonical_name": entry.get("canonical_name"),
            "ethnicity_provenance": entry.get("ethnicity_provenance"),
            "office": entry.get("office"),
            "institution": entry.get("institution"),
            "function": entry.get("function"),
            "phase_presence": entry.get("phase_presence", {}),
        },
        "private_constitution": private_constitution,
        "raw_private_entries": raw_entries,
        "teaching_profile": extract_teaching_profile(entries),
        "kala_ownership": kala_block,
        "kama_state": kama_block,
        "constitutional_relationships": rels,
        "sovereign_axis": axis,
    }


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    registry = load(ROOT / "characters" / "V17_1_CHARACTER_REGISTRY.json")
    if not registry:
        raise SystemExit("Character registry not found or invalid.")

    kama_state = load(ROOT / "characters" / "KAMA_CHARACTER_STATE.json") or {}
    kala_matrix = load(ROOT / "kalas" / "character_kala_matrix.json") or {}
    rel_system = load(ROOT / "relationships" / "relationship_system_v20.json") or {}

    print("=" * 60)
    print("DERIVE RUNTIME STATE FROM CARDS")
    print("=" * 60)

    written = 0
    failed = []
    for entry in registry.get("characters", []):
        char_id = entry.get("id")
        chub_id = entry.get("chub_card_id")
        if not chub_id:
            failed.append((char_id, "no chub_card_id"))
            continue

        card_path = ROOT / "characters" / f"main_{chub_id}_spec_v2.json"
        if not card_path.exists():
            failed.append((char_id, f"missing {card_path.name}"))
            continue

        card = load(card_path)
        if not card:
            failed.append((char_id, "unparseable card"))
            continue

        state = derive_character(entry, card, kama_state, kala_matrix, rel_system)
        out = OUT_DIR / f"{char_id}.json"
        out.write_text(json.dumps(state, indent=2, ensure_ascii=False),
                       encoding="utf-8")
        written += 1
        print(f"  OK   {char_id:16s} -> {out.relative_to(ROOT)}")

    print()
    print(f"Written:  {written}")
    print(f"Failed:   {len(failed)}")
    for cid, reason in failed:
        print(f"  FAIL {cid}: {reason}")
    print(f"Output:   {OUT_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()