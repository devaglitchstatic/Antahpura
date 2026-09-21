#!/usr/bin/env python3
"""
Apply jewelry events to Antahpura runtime state.
Reads: runtime/character_states.json, runtime/relationship_edges.json
Writes: archive/events.jsonl, runtime/character_states.json, runtime/relationship_edges.json
References: systems/jewelry_registry.json, systems/intimate_jewelry_system.json
"""

import json
import uuid
from datetime import datetime, timezone
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


def make_event(event_type, actor, target, jewelry_id, payload, consequence_class="personal"):
    return {
        "event_id": f"evt_{uuid.uuid4().hex[:12]}",
        "timestamp": now_iso(),
        "chapter": payload.get("chapter", 0),
        "scene_id": payload.get("scene_id"),
        "event_type": event_type,
        "actor": actor,
        "target": target,
        "location": payload.get("location"),
        "payload": payload,
        "visibility": payload.get("visibility", 2),
        "audience": payload.get("audience", "private"),
        "consequence_class": consequence_class,
        "jewelry_id": jewelry_id
    }


def get_character_state(states, char_id):
    if char_id not in states["states"]:
        states["states"][char_id] = {
            "jewelry_worn": [],
            "jewelry_owned": [],
            "jewelry_gifted": [],
            "jewelry_received": [],
            "jewelry_destroyed": [],
            "jewelry_returned": []
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


def apply_craft(actor, jewelry_id, payload):
    state = load(RUNTIME / "character_states.json")
    states = state.setdefault("states", {})
    actor_state = get_character_state(state, actor)

    if jewelry_id not in actor_state["jewelry_owned"]:
        actor_state["jewelry_owned"].append(jewelry_id)
    actor_state["last_updated"] = now_iso()

    save(RUNTIME / "character_states.json", state)

    event = make_event("jewelry_crafted", actor, None, jewelry_id, payload)
    append_event(event)
    return event


def apply_gift(actor, target, jewelry_id, payload):
    state = load(RUNTIME / "character_states.json")
    edges = load(RUNTIME / "relationship_edges.json")

    states = state.setdefault("states", {})
    actor_state = get_character_state(state, actor)
    target_state = get_character_state(state, target)

    if jewelry_id not in actor_state["jewelry_owned"]:
        actor_state["jewelry_owned"].append(jewelry_id)
    actor_state["jewelry_gifted"].append(jewelry_id)
    if jewelry_id in actor_state["jewelry_owned"]:
        actor_state["jewelry_owned"].remove(jewelry_id)
    target_state["jewelry_received"].append(jewelry_id)
    target_state["jewelry_owned"].append(jewelry_id)
    actor_state["last_updated"] = now_iso()
    target_state["last_updated"] = now_iso()

    apply_relationship_delta(
        edges, actor, target,
        {"affection": 5, "trust": 5, "loyalty": 3}
    )
    apply_relationship_delta(
        edges, target, actor,
        {"affection": 3, "trust": 4, "obligation": 2}
    )

    save(RUNTIME / "character_states.json", state)
    save(RUNTIME / "relationship_edges.json", edges)

    event = make_event("jewelry_gifted", actor, target, jewelry_id, payload)
    append_event(event)
    return event


def apply_accept(actor, target, jewelry_id, payload):
    state = load(RUNTIME / "character_states.json")
    edges = load(RUNTIME / "relationship_edges.json")

    states = state.setdefault("states", {})
    actor_state = get_character_state(state, actor)

    if jewelry_id not in actor_state["jewelry_owned"]:
        actor_state["jewelry_owned"].append(jewelry_id)
    actor_state["last_updated"] = now_iso()

    apply_relationship_delta(
        edges, actor, target,
        {"affection": 3, "trust": 4, "obligation": 2}
    )

    save(RUNTIME / "character_states.json", state)
    save(RUNTIME / "relationship_edges.json", edges)

    event = make_event("jewelry_accepted", actor, target, jewelry_id, payload)
    append_event(event)
    return event


def apply_wear(actor, jewelry_id, payload):
    state = load(RUNTIME / "character_states.json")
    states = state.setdefault("states", {})
    actor_state = get_character_state(state, actor)

    already_worn = any(j["jewelry_id"] == jewelry_id for j in actor_state["jewelry_worn"])
    if not already_worn:
        actor_state["jewelry_worn"].append({
            "jewelry_id": jewelry_id,
            "worn_since": now_iso(),
            "mechanical_effects_active": True
        })
    actor_state["last_updated"] = now_iso()

    save(RUNTIME / "character_states.json", state)

    event = make_event("jewelry_worn", actor, None, jewelry_id, payload)
    append_event(event)
    return event


def apply_remove(actor, jewelry_id, payload):
    state = load(RUNTIME / "character_states.json")
    edges = load(RUNTIME / "relationship_edges.json")
    states = state.setdefault("states", {})
    actor_state = get_character_state(state, actor)

    actor_state["jewelry_worn"] = [
        j for j in actor_state["jewelry_worn"] if j["jewelry_id"] != jewelry_id
    ]
    actor_state["last_updated"] = now_iso()

    gifter = payload.get("gifter")
    if gifter:
        apply_relationship_delta(edges, actor, gifter, {"affection": -3, "trust": -2, "resentment": 2})
        save(RUNTIME / "relationship_edges.json", edges)

    save(RUNTIME / "character_states.json", state)

    event = make_event("jewelry_removed", actor, gifter, jewelry_id, payload)
    append_event(event)
    return event


def apply_return(actor, gifter, jewelry_id, payload):
    state = load(RUNTIME / "character_states.json")
    edges = load(RUNTIME / "relationship_edges.json")
    states = state.setdefault("states", {})
    actor_state = get_character_state(state, actor)
    gifter_state = get_character_state(state, gifter)

    actor_state["jewelry_worn"] = [
        j for j in actor_state["jewelry_worn"] if j["jewelry_id"] != jewelry_id
    ]
    if jewelry_id in actor_state["jewelry_owned"]:
        actor_state["jewelry_owned"].remove(jewelry_id)
    actor_state["jewelry_returned"].append(jewelry_id)
    gifter_state["jewelry_owned"].append(jewelry_id)
    actor_state["last_updated"] = now_iso()
    gifter_state["last_updated"] = now_iso()

    apply_relationship_delta(
        edges, actor, gifter,
        {"affection": -10, "trust": -8, "resentment": 5, "obligation": -5}
    )

    save(RUNTIME / "character_states.json", state)
    save(RUNTIME / "relationship_edges.json", edges)

    event = make_event("jewelry_returned", actor, gifter, jewelry_id, payload, consequence_class="narrative")
    append_event(event)
    return event


def apply_destroy(actor, jewelry_id, payload):
    state = load(RUNTIME / "character_states.json")
    edges = load(RUNTIME / "relationship_edges.json")
    states = state.setdefault("states", {})
    actor_state = get_character_state(state, actor)

    actor_state["jewelry_worn"] = [
        j for j in actor_state["jewelry_worn"] if j["jewelry_id"] != jewelry_id
    ]
    if jewelry_id in actor_state["jewelry_owned"]:
        actor_state["jewelry_owned"].remove(jewelry_id)
    actor_state["jewelry_destroyed"].append(jewelry_id)
    actor_state["last_updated"] = now_iso()

    gifter = payload.get("gifter")
    if gifter:
        apply_relationship_delta(
            edges, actor, gifter,
            {"affection": -20, "trust": -25, "resentment": 15, "rivalry": 10}
        )
        save(RUNTIME / "relationship_edges.json", edges)

    save(RUNTIME / "character_states.json", state)

    event = make_event("jewelry_destroyed", actor, gifter, jewelry_id, payload, consequence_class="narrative")
    append_event(event)
    return event


def dispatch(action, **kwargs):
    handlers = {
        "craft": apply_craft,
        "gift": apply_gift,
        "accept": apply_accept,
        "wear": apply_wear,
        "remove": apply_remove,
        "return": apply_return,
        "destroy": apply_destroy
    }
    if action not in handlers:
        raise ValueError(f"Unknown jewelry action: {action}")
    return handlers[action](**kwargs)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["craft", "gift", "accept", "wear", "remove", "return", "destroy"])
    parser.add_argument("--actor", required=True)
    parser.add_argument("--target", default=None)
    parser.add_argument("--jewelry-id", required=True)
    parser.add_argument("--gifter", default=None)
    parser.add_argument("--chapter", type=int, default=0)
    parser.add_argument("--visibility", type=int, default=2)
    parser.add_argument("--audience", default="private")
    args = parser.parse_args()

    payload = {
        "chapter": args.chapter,
        "visibility": args.visibility,
        "audience": args.audience,
        "gifter": args.gifter
    }

    kwargs = {"actor": args.actor, "jewelry_id": args.jewelry_id, "payload": payload}
    if args.target:
        kwargs["target"] = args.target
    if args.gifter:
        kwargs["gifter"] = args.gifter

    event = dispatch(args.action, **kwargs)
    print(json.dumps(event, indent=2, ensure_ascii=False))