#!/usr/bin/env python3
"""
run_scene.py — Antahpura runtime scene execution (Track B), v4.

v4 changes:
  - build_character_definition constructs nested dataclass instances
    (AxisConfig, SuppressionConfig, RecoveryConfig, Provenance) rather
    than passing plain dicts. Fixes the "'dict' object has no attribute
    'validate'" error in apply_event.
  - Provenance includes required compiler_version field.
  - Default --scene-file now points to scenes/current_scene.json
    (the declared canonical).
  - apply_event result is serialised through a to_serializable helper
    that handles dataclasses, enums, and plain dicts.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import traceback
from contextlib import contextmanager
from dataclasses import dataclass, field, asdict, is_dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
RUNS_DIR = ROOT / "runtime" / "runs"

PASS = "\033[92m✓\033[0m"
WARN = "\033[93m!\033[0m"
ERR  = "\033[91m✗\033[0m"
INFO = "\033[94mi\033[0m"


# ============================================================================
# Utilities
# ============================================================================

def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def now_ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


try:
    import tiktoken
    _enc = tiktoken.get_encoding("cl100k_base")
    def count_tokens(text: str) -> int:
        return len(_enc.encode(text)) if text else 0
except ImportError:
    def count_tokens(text: str) -> int:
        return int(len(text.split()) * 1.3) if text else 0


SKIP_DIRS = {"node_modules", ".git", "dist", "build", "__pycache__",
             ".venv", "venv", ".mypy_cache", ".pytest_cache", "runs",
             "archive"}


def find_file(name: str, roots: list[Path]) -> Path | None:
    for root in roots:
        if not root.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            if name in filenames:
                return Path(dirpath) / name
    return None


def import_module_from_path(path: Path, name: str):
    if name in sys.modules:
        del sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@contextmanager
def chdir(path: Path):
    old = Path.cwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(old)


def to_serializable(obj):
    """Best-effort JSON-serializable conversion of engine outputs."""
    if obj is None or isinstance(obj, (bool, int, float, str)):
        return obj
    if isinstance(obj, Enum):
        return obj.value if hasattr(obj, "value") else obj.name
    if is_dataclass(obj) and not isinstance(obj, type):
        try:
            return {k: to_serializable(v) for k, v in asdict(obj).items()}
        except Exception:
            return repr(obj)
    if isinstance(obj, dict):
        return {str(k): to_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [to_serializable(v) for v in obj]
    return repr(obj)


# ============================================================================
# Scene context
# ============================================================================

@dataclass
class SceneContext:
    scene_id: str = "scene_001"
    chapter: str = ""
    title: str = ""
    ritual: str = ""
    phase: str = ""
    pov: str = "kumari_rati"
    participants: list = field(default_factory=list)
    kala_focus: list = field(default_factory=list)
    kama_focus: list = field(default_factory=list)
    event_type: str = "scene_entered"
    trigger_intensity: float = 0.5
    salience: float = 0.7
    user_message: str = "My lord, I am ready."
    history: list = field(default_factory=list)


def build_scene(cli_args) -> SceneContext:
    scene = SceneContext()
    scene_file = Path(cli_args.scene_file)
    if not scene_file.is_absolute():
        scene_file = ROOT / cli_args.scene_file
    if scene_file.exists():
        data = load_json(scene_file) or {}
        for k in ("scene_id", "chapter", "title", "ritual", "phase", "pov",
                  "participants", "kala_focus", "kama_focus", "event_type",
                  "trigger_intensity", "salience", "user_message", "history"):
            if k in data and data[k] is not None:
                setattr(scene, k, data[k])

    if cli_args.pov: scene.pov = cli_args.pov
    if cli_args.user: scene.user_message = cli_args.user
    if cli_args.scene_id: scene.scene_id = cli_args.scene_id
    if cli_args.chapter: scene.chapter = cli_args.chapter
    if cli_args.phase: scene.phase = cli_args.phase
    if cli_args.event_type: scene.event_type = cli_args.event_type
    if cli_args.trigger_intensity is not None:
        scene.trigger_intensity = cli_args.trigger_intensity
    if cli_args.salience is not None:
        scene.salience = cli_args.salience
    if cli_args.kala: scene.kala_focus = cli_args.kala
    if cli_args.kama: scene.kama_focus = cli_args.kama
    if cli_args.participants: scene.participants = cli_args.participants
    if cli_args.history: scene.history = cli_args.history
    if not scene.participants:
        scene.participants = [scene.pov]
    return scene


# ============================================================================
# Character definition construction
# ============================================================================

DEFENSE_STYLES = {
    "maha_deva":    "calculated",
    "kumari_rati":  "pride",
    "roxana":       "calculated",
    "shrinagar":    "pride",
    "malika":       "militance",
    "jahzara":      "militance",
    "altani":       "withdrawal",
    "anisa":        "calculated",
    "padma":        "compliance",
    "campa":        "withdrawal",
    "reva":         "calculated",
    "tarana":       "militance",
    "sevda":        "withdrawal",
    "svara":        "calculated",
}


def build_character_definition(module, char_id: str):
    """
    Build a fully-typed CharacterDefinition using the engine's own
    nested dataclass types.

    Required classes on the engine module:
      AxisConfig, SuppressionConfig, RecoveryConfig, Provenance,
      CharacterDefinition
    """
    AxisConfig = module.AxisConfig
    SuppressionConfig = module.SuppressionConfig
    RecoveryConfig = module.RecoveryConfig
    Provenance = module.Provenance
    CharacterDefinition = module.CharacterDefinition

    krodha = AxisConfig(
        starting=15,
        sensitivity=0.8,
        trigger_weights={
            "authority_challenged": 1.5,
            "public_humiliation": 1.2,
            "protocol_breach": 1.0,
        },
        critical_threshold=70,
    )
    dvesha = AxisConfig(
        starting=10,
        sensitivity=1.2,
        trigger_weights={
            "forced_vulnerability": 1.4,
            "seen_unprepared": 1.1,
            "loss_of_control": 1.0,
        },
        critical_threshold=60,
    )
    suppression = SuppressionConfig(
        baseline_capacity=70,
        sensitivity=0.9,
        decay_rate=0.05,
    )
    recovery = RecoveryConfig(
        resolution_weights={
            "validation": {"krodha_relief": 15, "dvesha_relief": 25},
            "status_restoration": {"krodha_relief": 30, "dvesha_relief": 10},
        },
        memory_retention_weight=0.7,
    )
    provenance = Provenance(
        source_id="character_registry_v17_1",
        source_version="17.1",
        schema_version="3.1-rc2",
        generated_at=now_iso(),
        compiler_version="run_scene_v4",
    )
    return CharacterDefinition(
        character_id=char_id,
        version="3.1-rc2",
        krodha_config=krodha,
        dvesha_config=dvesha,
        suppression_config=suppression,
        defense_style=DEFENSE_STYLES.get(char_id, "calculated"),
        recovery_config=recovery,
        phase_effects={
            "suppression_penalty": {
                "1": 0.00, "2": -0.05, "3": -0.15, "4": 0.10,
            }
        },
        provenance=provenance,
    )


def construct_definition(module, char_id: str):
    """Returns (definition_or_None, source_label, attempts_list)."""
    attempts = []
    cd_cls = getattr(module, "CharacterDefinition", None)

    if cd_cls is None:
        attempts.append("no CharacterDefinition class on engine module")
        return None, "none", attempts

    # Primary path: build via nested dataclasses
    try:
        definition = build_character_definition(module, char_id)
        if isinstance(definition, cd_cls):
            attempts.append("build_character_definition → CharacterDefinition ✓")
            return definition, "build_character_definition", attempts
        attempts.append(
            f"build_character_definition → {type(definition).__name__} "
            f"(not CharacterDefinition)"
        )
    except AttributeError as e:
        attempts.append(f"build_character_definition → missing attribute: {e}")
    except TypeError as e:
        attempts.append(f"build_character_definition → TypeError: {e}")
    except Exception as e:
        attempts.append(f"build_character_definition → {type(e).__name__}: {e}")

    return None, "none", attempts


# ============================================================================
# Emotional engine
# ============================================================================

def run_emotional_engine(scene: SceneContext) -> dict:
    result = {
        "status": "skipped",
        "character_id": scene.pov,
        "message": None,
        "loader_attempts": [],
    }

    engine_path = find_file("antapura_v31_rc2.py", [ROOT, REPO, REPO / "scripts"])
    if not engine_path:
        engine_path = find_file("antapura_emotional_engine_v3_2.py",
                                [ROOT, REPO, REPO / "scripts"])
    if not engine_path:
        result["message"] = "engine not found"
        return result

    result["engine_path"] = str(engine_path)

    try:
        module = import_module_from_path(engine_path, "antapura_emotional_engine")
    except Exception as e:
        result["message"] = f"import failed: {type(e).__name__}: {e}"
        return result

    definition, source, attempts = construct_definition(module, scene.pov)
    result["definition_source"] = source
    result["loader_attempts"] = attempts

    if definition is None:
        result["status"] = "skipped"
        result["message"] = (
            f"could not construct CharacterDefinition; "
            f"{len(attempts)} attempts recorded"
        )
        return result

    try:
        engine = module.AntapuraEngine(definition)
        result["engine_constructed"] = True
    except Exception as e:
        result["status"] = "error"
        result["message"] = (
            f"engine construction failed: {type(e).__name__}: {e}"
        )
        result["traceback"] = traceback.format_exc()
        return result

    try:
        event = module.Event(
            event_type=scene.event_type,
            scene_id=scene.scene_id,
            trigger_intensity=scene.trigger_intensity,
            salience=scene.salience,
            relationship_intimacy=0.5,
            emotional_signature="unspecified",
        )
    except Exception as e:
        result["status"] = "error"
        result["message"] = f"Event construction failed: {type(e).__name__}: {e}"
        return result

    try:
        apply_result = engine.apply_event(event)
        result["status"] = "ok"
        result["event"] = {
            "event_type": scene.event_type,
            "scene_id": scene.scene_id,
            "trigger_intensity": scene.trigger_intensity,
            "salience": scene.salience,
        }

        # Engine may return a dataclass, dict, or tuple. Serialize robustly.
        if is_dataclass(apply_result) and not isinstance(apply_result, type):
            result["apply_result"] = to_serializable(apply_result)
        elif isinstance(apply_result, dict):
            result["apply_result"] = to_serializable(apply_result)
        else:
            result["apply_result"] = {"repr": repr(apply_result)[:400]}

        # If the engine exposes runtime_to_dict, use it for the state snapshot
        if hasattr(module, "runtime_to_dict"):
            try:
                snapshot = module.runtime_to_dict(engine.state)
                result["state_snapshot"] = to_serializable(snapshot)
            except Exception:
                pass

    except Exception as e:
        result["status"] = "error"
        result["message"] = f"apply_event failed: {type(e).__name__}: {e}"
        result["traceback"] = traceback.format_exc()

    return result


# ============================================================================
# Kama engine
# ============================================================================

def _extract_states_block(state_data: dict) -> dict:
    for key in ("characters", "states", "character_states"):
        block = state_data.get(key)
        if isinstance(block, dict):
            return block
    return {k: v for k, v in state_data.items() if isinstance(v, dict)}


def run_kama_engine(scene: SceneContext) -> dict:
    result = {"status": "skipped", "applied": [], "errors": [], "message": None}
    engine_path = find_file("v18_9_compile_kama_engine.py",
                            [ROOT, REPO, REPO / "V18_9_KamaEngine"])
    if not engine_path:
        result["message"] = "engine not found"
        return result
    result["engine_path"] = str(engine_path)
    engine_dir = engine_path.parent

    inputs = {
        "MASTER_KINK_REGISTRY.json": find_file(
            "MASTER_KINK_REGISTRY.json", [ROOT, REPO]),
        "KINK_RELATION_GRAPH.json": find_file(
            "KINK_RELATION_GRAPH.json", [ROOT, REPO]),
        "KAMA_CHARACTER_STATE.json": find_file(
            "KAMA_CHARACTER_STATE.json", [ROOT, REPO]),
    }
    if not inputs["MASTER_KINK_REGISTRY.json"]:
        result["message"] = "MASTER_KINK_REGISTRY.json not found"
        return result
    if not inputs["KAMA_CHARACTER_STATE.json"]:
        result["message"] = "KAMA_CHARACTER_STATE.json not found"
        return result

    staged: list[Path] = []
    try:
        for name, src in inputs.items():
            if not src: continue
            dst = engine_dir / name
            if not dst.exists():
                dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
                staged.append(dst)

        with chdir(engine_dir):
            try:
                module = import_module_from_path(engine_path, "kama_engine")
            except Exception as e:
                result["message"] = f"import failed: {type(e).__name__}: {e}"
                return result

            reg_data = json.loads(
                Path("MASTER_KINK_REGISTRY.json").read_text(encoding="utf-8"))
            registry = {
                kid: module.KinkDefinition(
                    id=d["id"], name=d["name"],
                    taxonomy=d["taxonomy"], progression=d["progression"])
                for kid, d in reg_data.get("KINKS", {}).items()
            }

            graph_path = Path("KINK_RELATION_GRAPH.json")
            graph_data = (json.loads(graph_path.read_text(encoding="utf-8"))
                          if graph_path.exists()
                          else {"similar": {}, "related": {}, "secondary": {}})
            graph = module.KinkRelationGraph(
                similar=graph_data.get("similar", {}),
                related=graph_data.get("related", {}),
                secondary=graph_data.get("secondary", {}),
            )

            raw_states = json.loads(
                Path("KAMA_CHARACTER_STATE.json").read_text(encoding="utf-8"))
            states_block = _extract_states_block(raw_states)

            states = {}
            for cid, block in states_block.items():
                if not isinstance(block, dict): continue
                kinks_data = block.get("kinks", {})
                if not isinstance(kinks_data, dict): continue
                kinks = {}
                for kid, s in kinks_data.items():
                    if not isinstance(s, dict): continue
                    try:
                        kinks[kid] = module.KinkState(
                            knowledge=s.get("knowledge", 0.0),
                            training=s.get("training", 0.0),
                            repetition=s.get("repetition", 0),
                            mastery=s.get("mastery", 0.0),
                            preference=module.Preference(
                                s.get("preference", "neutral")),
                            limits=s.get("limits", {"soft": [], "hard": []}),
                            consent=module.Consent(s.get("consent", "orange")),
                            locked=s.get("locked", True),
                        )
                    except Exception:
                        pass
                states[cid] = module.CharacterKamaState(
                    character_id=cid, kinks=kinks)

            engine = module.KamaEngine(registry, graph, states)
            result["engine_constructed"] = True

            probes: list[tuple[str, str]] = []
            focus_kama = set(scene.kama_focus)
            for cid in scene.participants:
                if cid not in states: continue
                kinks = states[cid].kinks
                chosen = None
                for k in focus_kama:
                    if k in kinks and not kinks[k].locked and kinks[k].knowledge < 1.0:
                        chosen = k; break
                if chosen is None:
                    for kid, ks in kinks.items():
                        if not ks.locked and ks.knowledge < 1.0:
                            chosen = kid; break
                if chosen:
                    probes.append((cid, chosen))

            for cid, kid in probes:
                before = states[cid].kinks[kid].knowledge
                outcome = engine.apply_event(cid, {
                    "kink_id": kid, "knowledge_delta": 0.10,
                    "training_delta": 0.00, "repetition_delta": 1,
                })
                after = states[cid].kinks[kid].knowledge
                if "error" in outcome:
                    result["errors"].append({
                        "character_id": cid, "kink_id": kid,
                        "error": outcome["error"],
                    })
                else:
                    result["applied"].append({
                        "character_id": cid, "kink_id": kid,
                        "before": round(before, 4), "after": round(after, 4),
                        "hash": outcome.get("hash"),
                    })

            result["status"] = "ok" if not result["errors"] else "partial"
    finally:
        for p in staged:
            if p.exists():
                try: p.unlink()
                except Exception: pass

    return result


# ============================================================================
# Prompt assembly
# ============================================================================

def entry_matches(entry: dict, haystack: str, keys_field: str = "keys") -> bool:
    if not entry.get("enabled", True):
        return False
    if entry.get("constant", False):
        return True
    keys = entry.get(keys_field) or entry.get("key") or []
    if not keys:
        return False
    hay_lower = haystack.lower()
    for k in keys:
        if isinstance(k, str) and k.lower() in hay_lower:
            return True
    return False


def gather_entries(container, keys_field: str) -> list[dict]:
    if isinstance(container, dict):
        return list(container.values())
    if isinstance(container, list):
        return list(container)
    return []


def filter_and_sort(entries: list[dict], haystack: str, keys_field: str,
                    budget: int) -> list[dict]:
    matched = [e for e in entries
               if isinstance(e, dict) and entry_matches(e, haystack, keys_field)]
    matched.sort(key=lambda e: (
        e.get("insertion_order", e.get("order", 0)),
        -e.get("priority", 0),
    ))
    out, remaining = [], budget
    for e in matched:
        cost = count_tokens(e.get("content", ""))
        if cost <= remaining:
            out.append(e); remaining -= cost
    return out


def render_world_entries(entries: list[dict]) -> str:
    parts = []
    for e in entries:
        name = e.get("name") or e.get("comment") or ""
        content = e.get("content", "")
        parts.append(f"[{name}]\n{content}" if name else content)
    return "\n\n".join(parts)


def run_prompt_assembly(scene: SceneContext, registry: dict) -> dict:
    result = {"status": "skipped", "sections": [],
              "sampling_parameters": {}, "diagnostics": {}}

    pov_entry = None
    for c in registry.get("characters", []):
        if c.get("id") == scene.pov:
            pov_entry = c; break
    if not pov_entry:
        result["message"] = f"POV {scene.pov} not in registry"
        return result

    card_id = pov_entry.get("chub_card_id")
    card_path = ROOT / "characters" / f"main_{card_id}_spec_v2.json"
    if not card_path.exists():
        result["message"] = f"card not found: {card_path}"
        return result
    card = load_json(card_path)
    if not card:
        result["message"] = "card failed to parse"
        return result
    card_data = card.get("data", card)

    preset_path = ROOT / "runtime" / "Antarvāṇī.json"
    preset = load_json(preset_path) or {}

    lore_path = None
    for candidate in ROOT.glob("lorebook/*Unified Lorebook*.json"):
        lore_path = candidate; break
    lorebook = load_json(lore_path) if lore_path else {}

    recent = " ".join(scene.history[-3:]) if scene.history else ""
    haystack = f"{recent} {scene.user_message} {scene.title} {scene.ritual}"

    world_entries_all = gather_entries(lorebook.get("entries", {}), "key")
    world_budget = lorebook.get("token_budget", 512)
    world_matched = filter_and_sort(world_entries_all, haystack, "key", world_budget)

    cb = card_data.get("character_book", {})
    cb_entries_all = gather_entries(cb.get("entries", []), "keys")
    cb_budget = cb.get("token_budget", 2000)
    cb_matched = filter_and_sort(cb_entries_all, haystack, "keys", cb_budget)

    sections: list[dict] = []
    if preset.get("main_prompt"):
        sections.append({"role": "system", "label": "preset.main_prompt",
                         "content": preset["main_prompt"]})
    if preset.get("impersonation_prompt"):
        sections.append({"role": "system", "label": "preset.impersonation_prompt",
                         "content": preset["impersonation_prompt"]})
    if card_data.get("system_prompt"):
        sections.append({"role": "system", "label": "card.system_prompt",
                         "content": card_data["system_prompt"]})

    scene_hdr_parts = []
    for k, v in (("Chapter", scene.chapter), ("Title", scene.title),
                 ("Ritual", scene.ritual), ("Phase", scene.phase)):
        if v: scene_hdr_parts.append(f"{k}: {v}")
    if scene_hdr_parts:
        sections.append({"role": "system", "label": "scene.header",
                         "content": "\n".join(scene_hdr_parts)})

    if card_data.get("description"):
        sections.append({"role": "system", "label": "card.description",
                         "content": card_data["description"]})
    if card_data.get("scenario"):
        sections.append({"role": "system", "label": "card.scenario",
                         "content": card_data["scenario"]})
    if world_matched:
        sections.append({
            "role": "system",
            "label": f"world_info ({len(world_matched)} entries)",
            "content": render_world_entries(world_matched),
        })
    if cb_matched:
        sections.append({
            "role": "system",
            "label": f"character_book ({len(cb_matched)} entries)",
            "content": render_world_entries(cb_matched),
        })

    for i, turn in enumerate(scene.history):
        sections.append({
            "role": "user" if i % 2 == 0 else "assistant",
            "label": f"history[{i}]", "content": turn,
        })
    if not scene.history and card_data.get("first_mes"):
        sections.append({"role": "assistant", "label": "card.first_mes",
                         "content": card_data["first_mes"]})

    sections.append({"role": "user", "label": "user",
                     "content": scene.user_message})

    if card_data.get("post_history_instructions"):
        sections.append({
            "role": "system", "label": "card.post_history_instructions",
            "content": card_data["post_history_instructions"],
        })
    if preset.get("jailbreak_prompt"):
        sections.append({"role": "system", "label": "preset.jailbreak_prompt",
                         "content": preset["jailbreak_prompt"]})

    prompt_lines = [f"### {s['label']}\n{s['content']}" for s in sections]
    prompt_text = "\n\n".join(prompt_lines)

    sampling = {k: preset.get(k) for k in (
        "temperature", "frequency_penalty", "presence_penalty",
        "top_p", "top_k", "top_a", "min_p", "repetition_penalty",
        "names_in_completion") if k in preset}

    result.update({
        "status": "ok",
        "prompt": prompt_text,
        "sections": sections,
        "sampling_parameters": sampling,
        "diagnostics": {
            "total_tokens_approx": count_tokens(prompt_text),
            "sections_count": len(sections),
            "world_entries_matched": len(world_matched),
            "world_entries_available": len(world_entries_all),
            "character_book_entries_matched": len(cb_matched),
            "character_book_entries_available": len(cb_entries_all),
            "history_turns": len(scene.history),
            "card": card_path.name,
            "preset": preset_path.name,
            "lorebook": lore_path.name if lore_path else None,
        },
    })
    return result


# ============================================================================
# Orchestration
# ============================================================================

def write_artifacts(scene, emotional, kama, prompt, ts):
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = RUNS_DIR / f"scene_run_{ts}.json"
    prompt_path = RUNS_DIR / f"scene_run_{ts}.txt"
    deltas_path = RUNS_DIR / f"state_deltas_{ts}.json"

    report = {
        "schema": "antahpura.scene_run",
        "version": "1.0",
        "generated": now_iso(),
        "scene": asdict(scene),
        "emotional_engine": emotional,
        "kama_engine": kama,
        "prompt": {
            "sampling_parameters": prompt.get("sampling_parameters", {}),
            "diagnostics": prompt.get("diagnostics", {}),
            "sections": prompt.get("sections", []),
        },
    }
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False),
                           encoding="utf-8")
    prompt_path.write_text(prompt.get("prompt", "(no prompt)"), encoding="utf-8")

    deltas = {
        "schema": "antahpura.state_deltas",
        "version": "1.0",
        "generated": now_iso(),
        "scene_id": scene.scene_id,
        "committed": False,
        "emotional_deltas": None,
        "kama_deltas": [],
    }
    if emotional.get("status") == "ok":
        deltas["emotional_deltas"] = {
            "target_file": "characters/CHARACTER_STATE.json",
            "character_id": scene.pov,
            "event": emotional.get("event"),
            "result": emotional.get("apply_result"),
            "state_snapshot": emotional.get("state_snapshot"),
        }
    if kama.get("status") in ("ok", "partial"):
        deltas["kama_deltas"] = kama.get("applied", [])
    deltas_path.write_text(json.dumps(deltas, indent=2, ensure_ascii=False),
                           encoding="utf-8")

    return {"report": report_path, "prompt": prompt_path, "deltas": deltas_path}


def print_summary(scene, em, km, pm, paths, elapsed_s):
    print()
    print("=" * 66)
    print("SCENE RUN SUMMARY")
    print("=" * 66)
    print(f"Scene:        {scene.scene_id}")
    print(f"POV:          {scene.pov}")
    print(f"Participants: {', '.join(scene.participants)}")
    print(f"User:         {scene.user_message[:72]}")
    print()

    print(f"Emotional engine:  {em['status']}")
    if em.get("status") == "ok":
        print(f"  definition source: {em.get('definition_source')}")
        print(f"  engine path:       {Path(em['engine_path']).name}")
        snap = em.get("state_snapshot")
        if isinstance(snap, dict):
            k = snap.get("krodha", "?")
            d = snap.get("dvesha", "?")
            s = snap.get("current_state", "?")
            print(f"  krodha={k}  dvesha={d}  state={s}")
    else:
        if em.get("message"):
            print(f"  message: {em['message']}")
        attempts = em.get("loader_attempts") or []
        if attempts:
            print(f"  attempts ({len(attempts)}):")
            for line in attempts[:8]:
                print(f"    {line}")
    print()

    print(f"Kama engine:       {km['status']}")
    if km.get("applied"):
        for item in km["applied"]:
            print(f"  {item['character_id']:14s}  {item['kink_id']:28s}  "
                  f"{item['before']:.3f} -> {item['after']:.3f}")
    if km.get("errors"):
        for err in km["errors"][:3]:
            print(f"  ERROR: {err}")
    if km.get("message"):
        print(f"  message: {km['message']}")
    print()

    if pm.get("status") == "ok":
        d = pm["diagnostics"]
        print(f"Prompt:            {d['total_tokens_approx']} tokens")
        print(f"  sections:        {d['sections_count']}")
        print(f"  world entries:   {d['world_entries_matched']} / {d['world_entries_available']}")
        print(f"  character book:  {d['character_book_entries_matched']} / {d['character_book_entries_available']}")
        print(f"  card:            {d['card']}")
        print(f"  preset:          {d['preset']}")
    else:
        print(f"Prompt:            {pm['status']}")
        if pm.get("message"):
            print(f"  message: {pm['message']}")
    print()

    print(f"Elapsed:           {elapsed_s:.2f}s")
    print()
    print("Outputs:")
    for label, path in paths.items():
        try: rel = path.relative_to(ROOT)
        except ValueError: rel = path
        print(f"  {label:8s}  {rel}")
    print("=" * 66)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene-file", default="scenes/current_scene.json")
    ap.add_argument("--pov", default=None)
    ap.add_argument("--user", default=None)
    ap.add_argument("--scene-id", default=None)
    ap.add_argument("--chapter", default=None)
    ap.add_argument("--phase", default=None)
    ap.add_argument("--event-type", default=None)
    ap.add_argument("--trigger-intensity", type=float, default=None)
    ap.add_argument("--salience", type=float, default=None)
    ap.add_argument("--kala", nargs="*", default=None)
    ap.add_argument("--kama", nargs="*", default=None)
    ap.add_argument("--participants", nargs="*", default=None)
    ap.add_argument("--history", nargs="*", default=None)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    t_start = datetime.now()

    print()
    print("+" + "-" * 64 + "+")
    print("|" + " ANTAHPURA — SCENE RUN ".center(64) + "|")
    print("+" + "-" * 64 + "+")

    registry = load_json(ROOT / "characters" / "V17_1_CHARACTER_REGISTRY.json")
    if not registry:
        print(f"{ERR} character registry failed to load")
        sys.exit(2)

    scene = build_scene(args)
    print(f"\n{INFO} scene assembled: {scene.scene_id} (POV: {scene.pov})")
    print(f"{INFO} participants: {', '.join(scene.participants)}")

    print(f"\n{INFO} running emotional engine...")
    emotional = run_emotional_engine(scene)
    print(f"  {PASS if emotional['status'] == 'ok' else WARN} "
          f"emotional: {emotional['status']}")

    print(f"\n{INFO} running kama engine...")
    kama = run_kama_engine(scene)
    print(f"  {PASS if kama['status'] in ('ok', 'partial') else WARN} "
          f"kama: {kama['status']} ({len(kama.get('applied', []))} mutations)")

    print(f"\n{INFO} assembling prompt...")
    prompt = run_prompt_assembly(scene, registry)
    print(f"  {PASS if prompt['status'] == 'ok' else WARN} "
          f"prompt: {prompt['status']}")

    ts = now_ts()
    paths = write_artifacts(scene, emotional, kama, prompt, ts)

    elapsed = (datetime.now() - t_start).total_seconds()
    print_summary(scene, emotional, kama, prompt, paths, elapsed)

    any_error = (
        emotional.get("status") == "error"
        or kama.get("status") == "error"
        or prompt.get("status") == "skipped"
    )
    sys.exit(1 if any_error else 0)


if __name__ == "__main__":
    main()