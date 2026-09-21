#!/usr/bin/env python3
"""
Apply recovery events to Antahpura runtime state.
Reads: runtime/character_states.json, runtime/relationship_edges.json
Writes: archive/events.jsonl, runtime/character_states.json, runtime/relationship_edges.json
References: systems/recovery_action_registry.json
"""

import json
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "runtime"
ARCHIVE = ROOT / "archive"
SYSTEMS = ROOT / "systems"


def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def append_event(event):
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    with open(ARCHIVE / "events.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def make_event(event_type, actor, target, payload):
    return {
        "event_id": f"evt_{uuid.uuid4().hex[:12]}",
        "timestamp": now_iso(),
        "chapter": payload.get("chapter", 0),
        "event_type": event_type,
        "actor": actor,
        "target": target,
        "location": payload.get("location"),
        "payload": payload
    }


def get_character_state(states, char_id):
    if char_id not in states["states"]:
        states["states"][char_id] = {
            "physical_energy": 100.0,
            "emotional_pressure": 0.0,
            "social_standing": 100.0,
            "relational_states": {},
            "institutional_reputation": {},
            "unprocessed_events": 0,
            "narrative_weight": 0.0,
            "active_recovery_actions": []
        }
    return states["states"][char_id]


def apply_relationship_delta(edges, from_char, to_char, deltas):
    edge_id = f"rel_{from_char}_{to_char}"
    if edge_id not in edges["edges"]:
        edges["edges"][edge_id] = {
            "edge_id": edge_id,
            "from": from_char,
            "to": to_char,
            "runtime_deltas": [],
            "current": {},
            "status": "runtime_modified"
        }
    edge = edges["edges"][edge_id]
    edge["runtime_deltas"].append({"timestamp": now_iso(), "dimension_changes": deltas})
    for dim, delta in deltas.items():
        edge["current"][dim] = edge["current"].get(dim, 0) + delta
    edge["last_updated"] = now_iso()


def apply_recovery(actor, action_id, payload):
    """
    Apply a recovery action to a character.
    payload must include action_type (physical/emotional/social/relational/institutional/narrative).
    """
    state = load(RUNTIME / "character_states.json")
    edges = load(RUNTIME / "relationship_edges.json")

    states = state.setdefault("states", {})
    actor_state = get_character_state(state, actor)

    action_type = payload.get("action_type", "physical")
    effect = payload.get("effect", {})
    duration = payload.get("duration_minutes", 0)

    # Apply effect based on recovery type
    if action_type == "physical":
        actor_state["physical_energy"] = min(
            100.0,
            actor_state["physical_energy"] + effect.get("energy_restore", 0)
        )
    elif action_type == "emotional":
        actor_state["emotional_pressure"] = max(
            0.0,
            actor_state["emotional_pressure"] - effect.get("pressure_reduce", 0)
        )
    elif action_type == "social":
        actor_state["social_standing"] = min(
            100.0,
            actor_state["social_standing"] + effect.get("standing_restore", 0)
        )
    elif action_type == "relational":
        target = payload.get("target")
        if target:
            delta = effect.get("relationship_delta", {})
            apply_relationship_delta(edges, actor, target, delta)
    elif action_type == "institutional":
        inst = payload.get("institution")
        if inst:
            current = actor_state["institutional_reputation"].get(inst, 0.0)
            actor_state["institutional_reputation"][inst] = min(
                100.0,
                current + effect.get("reputation_restore", 0)
            )
    elif action_type == "narrative":
        actor_state["unprocessed_events"] = max(
            0,
            actor_state["unprocessed_events"] - effect.get("events_processed", 1)
        )
        actor_state["narrative_weight"] = max(
            0.0,
            actor_state["narrative_weight"] - effect.get("weight_reduce", 10.0)
        )

    # Track active recovery action
    if duration > 0:
        started = datetime.now(timezone.utc)
        actor_state["active_recovery_actions"].append({
            "action_id": action_id,
            "action_type": action_type,
            "started_at": started.isoformat(),
            "completes_at": (started + timedelta(minutes=duration)).isoformat(),
            "effect": effect
        })

    save(RUNTIME / "character_states.json", state)
    save(RUNTIME / "relationship_edges.json", edges)

    event = make_event("recovery_action_applied", actor, payload.get("target"), payload)
    append_event(event)
    return event


def apply_aftercare(actor, target, payload):
    """
    Apply standard aftercare protocol between two characters.
    """
    state = load(RUNTIME / "character_states.json")
    edges = load(RUNTIME / "relationship_edges.json")

    states = state.setdefault("states", {})
    actor_state = get_character_state(state, actor)
    target_state = get_character_state(state, target)

    # Both parties benefit
    for st in (actor_state, target_state):
        st["emotional_pressure"] = max(0.0, st["emotional_pressure"] - 20.0)
        st["physical_energy"] = min(100.0, st["physical_energy"] + 10.0)

    apply_relationship_delta(edges, actor, target, {"affection": 3, "trust": 5})
    apply_relationship_delta(edges, target, actor, {"affection": 3, "trust": 5})

    save(RUNTIME / "character_states.json", state)
    save(RUNTIME / "relationship_edges.json", edges)

    event = make_event("aftercare_applied", actor, target, payload)
    append_event(event)
    return event


def dispatch(action, **kwargs):
    handlers = {
        "recovery": apply_recovery,
        "aftercare": apply_aftercare
    }
    if action not in handlers:
        raise ValueError(f"Unknown recovery action: {action}")
    return handlers[action](**kwargs)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["recovery", "aftercare"])
    parser.add_argument("--actor", required=True)
    parser.add_argument("--target", default=None)
    parser.add_argument("--action-id", default=None)
    parser.add_argument("--action-type", default="physical")
    parser.add_argument("--institution", default=None)
    parser.add_argument("--chapter", type=int, default=0)
    args = parser.parse_args()

    payload = {
        "chapter": args.chapter,
        "action_type": args.action_type,
        "institution": args.institution
    }

    kwargs = {"actor": args.actor, "payload": payload}
    if args.target:
        kwargs["target"] = args.target
    if args.action_id:
        kwargs["action_id"] = args.action_id

    event = dispatch(args.action, **kwargs)
    print(json.dumps(event, indent=2, ensure_ascii=False))