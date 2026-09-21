#!/usr/bin/env python3
"""
replay_events.py — Rebuild runtime state from events.jsonl.

Reads archive/events.jsonl and, optionally, an existing runtime snapshot.
Produces a fresh runtime state by applying every event in order.

Usage:
  python3 replay_events.py --output /tmp/rebuilt_state
  python3 replay_events.py --compare       # compare rebuilt vs current
"""

import json
import sys
import argparse
from pathlib import Path
from copy import deepcopy

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "runtime"
ARCHIVE = ROOT / "archive"


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def iter_events() -> list[dict]:
    events_path = ARCHIVE / "events.jsonl"
    if not events_path.exists():
        return []
    events = []
    with open(events_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return events


def apply_event(state: dict, event: dict) -> None:
    etype = event.get("event_type")
    actor = event.get("actor")
    target = event.get("target")
    payload = event.get("payload", {})

    chars = state.setdefault("character_states", {}).setdefault("states", {})
    edges = state.setdefault("relationship_edges", {}).setdefault("edges", {})

    def ensure_char(cid: str) -> dict:
        if cid not in chars:
            chars[cid] = {"last_updated": event.get("timestamp")}
        return chars[cid]

    # ---- Character state events ----
    if etype in ("task_assigned", "task_completed", "task_failed"):
        tstate = ensure_char(target or actor)
        tstate.setdefault("tasks_active", [])
        tstate.setdefault("tasks_completed_total", 0)
        tstate.setdefault("tasks_missed_total", 0)
        task_id = payload.get("task_id")
        if etype == "task_assigned" and task_id:
            tstate["tasks_active"].append({
                "task_id": task_id,
                "assigned_by": actor,
                "assigned_at": event.get("timestamp")
            })
        elif etype == "task_completed":
            tstate["tasks_completed_total"] += 1
        elif etype == "task_failed":
            tstate["tasks_missed_total"] += 1
        tstate["last_updated"] = event.get("timestamp")

    elif etype in ("punishment_assigned", "punishment_completed"):
        tstate = ensure_char(target)
        tstate.setdefault("punishment_history", [])
        tstate.setdefault("active_punishment", None)
        if etype == "punishment_assigned":
            tstate["active_punishment"] = {
                "punishment_id": payload.get("punishment_id"),
                "assigned_by": actor,
                "assigned_at": event.get("timestamp")
            }
        else:
            tstate["punishment_history"].append({
                "punishment_id": payload.get("punishment_id"),
                "completed_at": event.get("timestamp")
            })
            tstate["active_punishment"] = None
        tstate["last_updated"] = event.get("timestamp")

    elif etype == "dbt_technique_applied":
        tstate = ensure_char(target)
        tstate.setdefault("dbt_skills_practiced", [])
        tid = payload.get("technique_id")
        found = None
        for e in tstate["dbt_skills_practiced"]:
            if e.get("skill_id") == tid:
                found = e
                break
        if found:
            found["practice_count"] = found.get("practice_count", 0) + 1
            found["last_practiced"] = event.get("timestamp")
        else:
            tstate["dbt_skills_practiced"].append({
                "skill_id": tid,
                "practice_count": 1,
                "last_practiced": event.get("timestamp"),
                "mastery_level": 0.2
            })
        tstate["last_updated"] = event.get("timestamp")

    elif etype == "journal_entry_written":
        astate = ensure_char(actor)
        astate.setdefault("journal_entries", [])
        astate["journal_entries"].append({
            "entry_id": payload.get("entry_id"),
            "journal_type": payload.get("journal_type"),
            "written_at": event.get("timestamp"),
            "shared_with": [target] if target else [],
            "word_count": payload.get("word_count", 0)
        })
        astate["last_entry_at"] = event.get("timestamp")
        astate["last_updated"] = event.get("timestamp")

    elif etype == "journal_entry_annotated":
        tstate = ensure_char(target)
        tstate.setdefault("journal_entries", [])
        entry_id = payload.get("entry_id")
        for e in tstate["journal_entries"]:
            if e.get("entry_id") == entry_id:
                e.setdefault("annotation_ids", []).append(event.get("event_id"))
        tstate["last_updated"] = event.get("timestamp")

    # ---- Relationship events ----
    elif etype in ("reward_given", "jewelry_gifted", "jewelry_accepted",
                   "jewelry_removed", "jewelry_returned", "jewelry_destroyed",
                   "consent_negotiated", "consent_revoked",
                   "traffic_signal", "aftercare_applied"):
        if actor and target:
            edge_id = f"rel_{actor}_{target}"
            edge = edges.setdefault(edge_id, {
                "edge_id": edge_id,
                "from": actor,
                "to": target,
                "runtime_deltas": [],
                "current": {}
            })
            edge["runtime_deltas"].append({
                "timestamp": event.get("timestamp"),
                "event_type": etype,
                "memory_tag": payload.get("memory_tag")
            })
            edge["last_updated"] = event.get("timestamp")

    # ---- Collar / contract ----
    elif etype == "collar_granted":
        tstate = ensure_char(target)
        tstate["active_collar_id"] = payload.get("collar_id")
        tstate["collar_stage"] = payload.get("stage")
        tstate["last_updated"] = event.get("timestamp")

    elif etype == "contract_signed":
        tstate = ensure_char(target)
        tstate.setdefault("active_contracts", []).append({
            "contract_id": payload.get("contract_id"),
            "counterparty": actor,
            "stage": payload.get("stage"),
            "signed_at": event.get("timestamp")
        })
        tstate["last_updated"] = event.get("timestamp")

    # ---- Scene lifecycle ----
    elif etype == "scene_started":
        state.setdefault("current_scene", {})
        state["current_scene"] = {
            "scene_id": event.get("scene_id"),
            "participants": payload.get("participants", []),
            "started_at": event.get("timestamp"),
            "status": "active"
        }

    elif etype == "scene_ended":
        state.setdefault("current_scene", {})
        state["current_scene"] = {}

    # ---- Quest lifecycle ----
    elif etype == "quest_accepted":
        astate = ensure_char(actor)
        astate.setdefault("open_quests", [])
        if payload.get("quest_id") not in astate["open_quests"]:
            astate["open_quests"].append(payload.get("quest_id"))
        astate["last_updated"] = event.get("timestamp")

    elif etype == "quest_completed":
        astate = ensure_char(actor)
        astate.setdefault("open_quests", [])
        astate.setdefault("completed_quests", [])
        qid = payload.get("quest_id")
        if qid in astate["open_quests"]:
            astate["open_quests"].remove(qid)
        if qid not in astate["completed_quests"]:
            astate["completed_quests"].append(qid)
        astate["last_updated"] = event.get("timestamp")

    # ---- World state ----
    elif etype == "chandra_kala_shift":
        state.setdefault("chandra_kala", {})
        state["chandra_kala"]["current_lunar_day"] = payload.get("lunar_day")
        state["chandra_kala"]["phase"] = payload.get("phase")
        state["chandra_kala"]["last_updated"] = event.get("timestamp")

    elif etype == "occasion_started":
        state.setdefault("world_state", {}).setdefault("active_occasions", [])
        oid = payload.get("occasion_id")
        if oid and oid not in state["world_state"]["active_occasions"]:
            state["world_state"]["active_occasions"].append(oid)

    elif etype == "occasion_ended":
        state.setdefault("world_state", {}).setdefault("active_occasions", [])
        oid = payload.get("occasion_id")
        if oid in state["world_state"]["active_occasions"]:
            state["world_state"]["active_occasions"].remove(oid)

    # ---- Unknown event types: log for audit ----
    else:
        state.setdefault("unhandled_events", []).append({
            "event_id": event.get("event_id"),
            "event_type": etype,
            "timestamp": event.get("timestamp")
        })


def build_state() -> dict:
    state: dict = {
        "character_states": {"states": {}},
        "relationship_edges": {"edges": {}},
        "world_state": {"active_occasions": []},
        "current_scene": {},
        "chandra_kala": {},
        "unhandled_events": []
    }
    events = iter_events()
    for event in events:
        apply_event(state, event)
    state["_meta"] = {
        "events_processed": len(events),
                "rebuilt_at": __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc
        ).isoformat()
    }
    return state


def compare_to_current(rebuilt: dict) -> None:
    print("Comparing rebuilt state to current runtime...")
    current_chars = load_json(RUNTIME / "character_states.json").get("states", {})
    current_edges = load_json(RUNTIME / "relationship_edges.json").get("edges", {})

    rebuilt_chars = rebuilt.get("character_states", {}).get("states", {})
    rebuilt_edges = rebuilt.get("relationship_edges", {}).get("edges", {})

    print(f"  Characters: rebuilt={len(rebuilt_chars)} current={len(current_chars)}")
    print(f"  Edges:      rebuilt={len(rebuilt_edges)} current={len(current_edges)}")

    rebuilt_set = set(rebuilt_chars.keys())
    current_set = set(current_chars.keys())
    if rebuilt_set != current_set:
        only_rebuilt = rebuilt_set - current_set
        only_current = current_set - rebuilt_set
        if only_rebuilt:
            print(f"  Only in rebuilt: {sorted(only_rebuilt)}")
        if only_current:
            print(f"  Only in current: {sorted(only_current)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=None,
                        help="Output path for rebuilt state directory")
    parser.add_argument("--compare", action="store_true",
                        help="Compare rebuilt state to current runtime")
    args = parser.parse_args()

    print(f"Repository root: {ROOT}")
    state = build_state()
    events = state["_meta"]["events_processed"]
    print(f"Processed {events} events.")

    if args.output:
        out = Path(args.output)
        save_json(out / "character_states.json", state["character_states"])
        save_json(out / "relationship_edges.json", state["relationship_edges"])
        save_json(out / "world_state.json", state["world_state"])
        save_json(out / "chandra_kala_modifiers.json", state["chandra_kala"])
        save_json(out / "replay_meta.json", state["_meta"])
        print(f"Wrote rebuilt state to {out}")

    if args.compare:
        compare_to_current(state)

    if not args.output and not args.compare:
        print(json.dumps(state["_meta"], indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())