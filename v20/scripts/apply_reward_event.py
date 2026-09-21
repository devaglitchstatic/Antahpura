#!/usr/bin/env python3
"""
Apply reward events to Antahpura runtime state.
Reads: runtime/character_states.json, runtime/relationship_edges.json
Writes: archive/events.jsonl, runtime/character_states.json, runtime/relationship_edges.json
References: systems/reward_registry.json, systems/jewelry_registry.json, systems/aphrodisiacs_substances_registry.json, systems/toys_registry.json
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
        states["states"][char_id] = {}
    char = states["states"][char_id]
    char.setdefault("rewards_received", [])
    char.setdefault("rewards_given", [])
    char.setdefault("reward_history_summary", {
        "total_rewards_received": 0,
        "total_rewards_given": 0,
        "most_common_reward_type": None,
        "last_reward_at": None,
    })
    return char


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


def load_reward_registry():
    try:
        return load(SYSTEMS / "reward_registry.json")
    except FileNotFoundError:
        return {"reward_categories": {}}


def find_reward(registry, reward_id):
    for cat_name, cat in registry.get("reward_categories", {}).items():
        for item in cat.get("items", []):
            if item.get("reward_id") == reward_id:
                return item, cat_name
    return None, None


def apply_give_reward(actor, target, reward_id, payload):
    """
    actor gives reward to target.
    """
    state = load(RUNTIME / "character_states.json")
    edges = load(RUNTIME / "relationship_edges.json")
    registry = load_reward_registry()

    states = state.setdefault("states", {})
    actor_state = get_character_state(state, actor)
    target_state = get_character_state(state, target)

    reward, category = find_reward(registry, reward_id)

    # Record
    timestamp = now_iso()
    actor_state["rewards_given"].append({
        "reward_id": reward_id,
        "reward_type": category,
        "to_char": target,
        "timestamp": timestamp,
        "effect_applied": True
    })
    target_state["rewards_received"].append({
        "reward_id": reward_id,
        "reward_type": category,
        "from_char": actor,
        "timestamp": timestamp,
        "effect_applied": True
    })

    actor_state["reward_history_summary"]["total_rewards_given"] += 1
    target_state["reward_history_summary"]["total_rewards_received"] += 1
    target_state["reward_history_summary"]["last_reward_at"] = timestamp

    # Apply relationship delta
    if reward:
        deltas = {}
        for dim in ("affection_delta", "trust_delta", "respect_delta", "loyalty_delta"):
            if dim in reward:
                key = dim.replace("_delta", "")
                deltas[key] = reward[dim]
        if deltas:
            apply_relationship_delta(edges, target, actor, deltas)

    save(RUNTIME / "character_states.json", state)
    save(RUNTIME / "relationship_edges.json", edges)

    event = make_event("reward_given", actor, target, {**payload, "reward_id": reward_id, "category": category})
    append_event(event)
    return event


def apply_receive_reward(actor, source, reward_id, payload):
    """
    actor receives reward from source.
    """
    return apply_give_reward(source, actor, reward_id, payload)


def apply_apply_aphrodisiac(actor, target, substance_id, payload):
    """
    Reference aphrodisiacs_substances_registry.json.
    Applies a substance to a target, with delta effects.
    """
    state = load(RUNTIME / "character_states.json")
    states = state.setdefault("states", {})
    target_state = get_character_state(state, target)

    timestamp = now_iso()
    target_state.setdefault("active_substances", []).append({
        "substance_id": substance_id,
        "administered_by": actor,
        "timestamp": timestamp,
        "duration_minutes": payload.get("duration_minutes", 30)
    })
    target_state["last_updated"] = timestamp

    save(RUNTIME / "character_states.json", state)

    event = make_event("aphrodisiac_administered", actor, target, {**payload, "substance_id": substance_id})
    append_event(event)
    return event


def apply_use_toy(actor, target, toy_id, payload):
    """
    Reference toys_registry.json.
    Applies a toy-based reward.
    """
    state = load(RUNTIME / "character_states.json")
    edges = load(RUNTIME / "relationship_edges.json")
    states = state.setdefault("states", {})
    actor_state = get_character_state(state, actor)
    target_state = get_character_state(state, target)

    timestamp = now_iso()
    actor_state["rewards_given"].append({
        "reward_id": toy_id,
        "reward_type": "toy",
        "to_char": target,
        "timestamp": timestamp
    })
    target_state["rewards_received"].append({
        "reward_id": toy_id,
        "reward_type": "toy",
        "from_char": actor,
        "timestamp": timestamp
    })

    apply_relationship_delta(edges, target, actor, {"affection": 4, "trust": 3})

    save(RUNTIME / "character_states.json", state)
    save(RUNTIME / "relationship_edges.json", edges)

    event = make_event("toy_reward_used", actor, target, {**payload, "toy_id": toy_id})
    append_event(event)
    return event


def dispatch(action, **kwargs):
    handlers = {
        "give_reward": apply_give_reward,
        "receive_reward": apply_receive_reward,
        "apply_aphrodisiac": apply_apply_aphrodisiac,
        "use_toy": apply_use_toy
    }
    if action not in handlers:
        raise ValueError(f"Unknown reward action: {action}")
    return handlers[action](**kwargs)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["give_reward", "receive_reward", "apply_aphrodisiac", "use_toy"])
    parser.add_argument("--actor", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--reward-id", default=None)
    parser.add_argument("--substance-id", default=None)
    parser.add_argument("--toy-id", default=None)
    parser.add_argument("--duration-minutes", type=int, default=30)
    parser.add_argument("--chapter", type=int, default=0)
    args = parser.parse_args()

    payload = {"chapter": args.chapter, "duration_minutes": args.duration_minutes}

    if args.action in ("give_reward", "receive_reward"):
        kwargs = {"actor": args.actor, "target": args.target, "reward_id": args.reward_id, "payload": payload}
    elif args.action == "apply_aphrodisiac":
        kwargs = {"actor": args.actor, "target": args.target, "substance_id": args.substance_id, "payload": payload}
    elif args.action == "use_toy":
        kwargs = {"actor": args.actor, "target": args.target, "toy_id": args.toy_id, "payload": payload}

    event = dispatch(args.action, **kwargs)
    print(json.dumps(event, indent=2, ensure_ascii=False))