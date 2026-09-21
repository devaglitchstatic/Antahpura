#!/usr/bin/env python3
"""
init_runtime.py
Seeds the runtime layer from canon + matrices + relationship edges.
Run after generate_relationship_edges.py.
"""
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "runtime"
ARCHIVE = ROOT / "archive"


def load(p):
    with open(p, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def save(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"WROTE: {p.relative_to(ROOT)}  ({p.stat().st_size} bytes)")


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def main():
    canon_chars = load(ROOT / "canon" / "characters.json")
    char_ids = list(canon_chars["characters"].keys())

    try:
        kala_matrix = load(ROOT / "matrices" / "character_kala_matrix.json")
        kala_by_char = kala_matrix.get("matrix", {})
    except Exception:
        kala_by_char = {}

    try:
        kama_derived = load(ROOT / "matrices" / "character_kama_derived.json")
        kama_by_char = kama_derived.get("characters", {})
    except Exception:
        kama_by_char = {}

    try:
        orientations = load(ROOT / "characters" / "role_orientation" / "orientations.json")
        orient_by_char = orientations.get("assignments", {})
    except Exception:
        orient_by_char = {}

    try:
        edges_canon = load(ROOT / "relationships" / "relationship_edges.json")
        edges = edges_canon.get("edges", {})
    except Exception:
        edges = {}

    # ---- world_state ----
    world_state = {
        "schema": "antahpura.runtime.world_state",
        "version": "20.0",
        "session_id": None,
        "chapter": 1,
        "lunar_day": 1,
        "lunar_phase": "waxing",
        "season": "spring",
        "time_of_day": "dawn",
        "active_occasions": [],
        "global_flags": {},
        "world_discovered_secrets": [],
        "world_unlocked_locations": [],
        "world_completed_quests": [],
        "world_failed_quests": [],
        "last_updated": now_iso(),
    }
    save(RUNTIME / "world_state.json", world_state)

    # ---- character_states ----
    states = {}
    for cid in char_ids:
        kala_mastery = {}
        for affinity, level in (("primary", 5), ("resonant", 3), ("latent", 1)):
            for k in kala_by_char.get(cid, {}).get(affinity, []):
                kala_mastery[k] = {
                    "level": level,
                    "practice_count": 0,
                    "successful_applications": 0,
                    "failures": 0,
                    "teacher": None,
                    "confidence": 0.5,
                }

        kama_lifecycle = {}
        for kama, info in kama_by_char.get(cid, {}).items():
            assoc = info.get("association", "unknown")
            state_map = {
                "role_owner": "discussable",
                "thematic": "mentionable",
                "curiosity": "discoverable",
                "unsupported": "locked",
                "unknown": "locked",
            }
            kama_lifecycle[kama] = {
                "state": state_map.get(assoc, "locked"),
                "curiosity": info.get("score", 0.0),
                "boundary": False,
                "discovered_at": None,
            }

        states[cid] = {
            "character_id": cid,
            "current_location": None,
            "current_state": {
                "temporal": "baseline",
                "narrative": "observation",
                "headspace": "baseline",
            },
            "kala_mastery": kala_mastery,
            "kama_lifecycle": kama_lifecycle,
            "role_orientation": orient_by_char.get(cid, {}),
            "vak_kautuka_bhrama": {
                "break_threshold": 100,
                "current_pressure": 0,
                "last_trigger": None,
                "whisper_history": [],
            },
            "inventory": [],
            "known_secrets": [],
            "suspected_secrets": [],
            "open_quests": [],
            "completed_quests": [],
            "rewards_received": [],
            "rewards_given": [],
            "reward_history_summary": {
                "total_rewards_received": 0,
                "total_rewards_given": 0,
                "most_common_reward_type": None,
                "last_reward_at": None,
            },
            "punishment_history": [],
            "active_punishment": None,
            "tasks_active": [],
            "tasks_completed_total": 0,
            "tasks_missed_total": 0,
            "current_streak": 0,
            "longest_streak": 0,
            "journal_entries": [],
            "journal_streak_current": 0,
            "journal_streak_longest": 0,
            "last_entry_at": None,
            "dbt_skills_known": [],
            "dbt_skills_practiced": [],
            "dbt_effectiveness_rating": 50.0,
            "consent_records": [],
            "active_framework": "SSC",
            "active_collar_id": None,
            "collar_stage": None,
            "active_contracts": [],
            "physical_energy": 100.0,
            "emotional_pressure": 0.0,
            "social_standing": 100.0,
            "last_updated": now_iso(),
        }

    save(RUNTIME / "character_states.json", {
        "schema": "antahpura.runtime.character_states",
        "version": "20.0",
        "state_count": len(states),
        "states": states,
    })

    # ---- relationship_edges (runtime copy) ----
    runtime_edges = {}
    for eid, edge in edges.items():
        runtime_edges[eid] = {
            "edge_id": eid,
            "from": edge["from"],
            "to": edge["to"],
            "type": edge["type"],
            "power_direction": edge["power_direction"],
            "canonical_initial": edge["dim"],
            "runtime_deltas": [],
            "current": dict(edge["dim"]),
            "status": "canonical_initial",
            "last_updated": now_iso(),
        }

    save(RUNTIME / "relationship_edges.json", {
        "schema": "antahpura.runtime.relationship_edges",
        "version": "20.0",
        "edge_count": len(runtime_edges),
        "edges": runtime_edges,
    })

    # ---- telemetry ----
    save(RUNTIME / "telemetry.json", {
        "schema": "antahpura.runtime.telemetry",
        "version": "20.0",
        "session_id": None,
        "session_started_at": now_iso(),
        "events_since_last_save": 0,
        "events_total": 0,
        "scenes_completed": 0,
        "choices_made_total": 0,
        "kala_practices_total": 0,
        "kala_synergies_unlocked": 0,
        "kama_lifecycles_advanced": 0,
        "relationships_modified": 0,
        "secrets_discovered": 0,
        "quests_completed": 0,
        "quests_failed": 0,
        "last_saved_at": None,
    })

    # ---- chandra_kala_modifiers ----
    save(RUNTIME / "chandra_kala_modifiers.json", {
        "schema": "antahpura.runtime.chandra_kala_modifiers",
        "version": "20.0",
        "current_lunar_day": 1,
        "phase": "waxing",
        "ritual_theme": "grounding",
        "ritu_kala_modifier": {
            "biological_phase": "follicular",
            "arousal_receptivity_modifier": 0.0,
            "sensory_sensitivity_modifier": 0.0,
        },
        "kala_emphasis": {},
        "kama_curiosity_modifier": {},
        "prohibitions": [
            "does_not_override_consent",
            "does_not_determine_preference",
            "does_not_trigger_scenes",
            "does_not_modify_relationship_state",
        ],
        "last_updated": now_iso(),
    })

    # ---- event log ----
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    event = {
        "event_id": f"evt_{uuid.uuid4().hex[:12]}",
        "timestamp": now_iso(),
        "chapter": 1,
        "event_type": "runtime_initialized",
        "actor": "system",
        "target": None,
        "payload": {
            "characters_initialized": len(char_ids),
            "edges_initialized": len(runtime_edges),
            "kala_matrix_loaded": bool(kala_by_char),
            "kama_matrix_loaded": bool(kama_by_char),
        },
    }
    with open(ARCHIVE / "events.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
    print("APPENDED: archive/events.jsonl (init event)")

    print()
    print(f"Initialized {len(char_ids)} characters, {len(runtime_edges)} edges.")


if __name__ == "__main__":
    main()