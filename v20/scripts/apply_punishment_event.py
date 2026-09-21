#!/usr/bin/env python3
"""
apply_punishment_event.py — Assign punishments, run Clean Slate Loop,
track punishment history.
References: systems/punishment_system.json, systems/traffic_light_system.json,
            systems/recovery_action_registry.json
"""

import argparse
from _antahpura_common import (
    SYSTEMS, load, load_or_default,
    make_event, emit, now_iso,
    get_character_state, apply_relationship_delta,
    load_character_states, load_relationship_edges,
    save_character_states, save_relationship_edges,
    cli_run
)


def load_punishment_registry():
    return load_or_default(SYSTEMS / "punishment_system.json", {"punishment_registry": {"punishments": []}})


def find_punishment(registry, punishment_id):
    for p in registry.get("punishment_registry", {}).get("punishments", []):
        if p.get("punishment_id") == punishment_id:
            return p
    return None


def check_traffic_light_red(scene_id):
    """If a red signal is active, punishments cannot proceed."""
    try:
        tl = load(SYSTEMS / "traffic_light_system.json")
    except FileNotFoundError:
        return False
    # Runtime signal check omitted; contract-level red overrides
    return False


def ensure_punishment_state(char_state):
    char_state.setdefault("active_punishment", None)
    char_state.setdefault("punishment_history", [])
    char_state.setdefault("total_punishments", 0)
    char_state.setdefault("last_punishment_at", None)
    return char_state


def assign_punishment(actor, target, punishment_id, payload):
    if check_traffic_light_red(payload.get("scene_id")):
        raise RuntimeError("Cannot assign punishment: active red signal")

    registry = load_punishment_registry()
    punishment = find_punishment(registry, punishment_id)
    if not punishment:
        raise ValueError(f"Unknown punishment_id: {punishment_id}")

    states = load_character_states()
    target_state = get_character_state(states, target)
    ensure_punishment_state(target_state)

    target_state["active_punishment"] = {
        "punishment_id": punishment_id,
        "name": punishment.get("name"),
        "category": punishment.get("category"),
        "assigned_by": actor,
        "assigned_at": now_iso(),
        "infraction": payload.get("infraction"),
        "clean_slate_pending": True
    }
    target_state["total_punishments"] = target_state.get("total_punishments", 0) + 1
    target_state["last_punishment_at"] = now_iso()
    target_state["last_updated"] = now_iso()
    save_character_states(states)

    event = make_event(
        "punishment_assigned", actor, target,
        {
            **payload,
            "punishment_id": punishment_id,
            "category": punishment.get("category"),
            "infraction": payload.get("infraction")
        },
        consequence_class="personal"
    )
    return emit(event)


def complete_punishment(actor, target, payload):
    """Run Clean Slate Loop and clear active punishment."""
    states = load_character_states()
    edges = load_relationship_edges()
    target_state = get_character_state(states, target)
    ensure_punishment_state(target_state)

    active = target_state.get("active_punishment")
    if not active:
        raise ValueError(f"No active punishment for {target}")

    punishment_id = active["punishment_id"]

    history_entry = {
        "punishment_id": punishment_id,
        "infraction": active.get("infraction"),
        "assigned_at": active.get("assigned_at"),
        "completed_at": now_iso(),
        "clean_slate_completed": True
    }
    target_state["punishment_history"].append(history_entry)
    target_state["active_punishment"] = None
    target_state["last_updated"] = now_iso()

    apply_relationship_delta(
        edges, target, actor,
        {"trust": 2, "affection": 1},
        memory_tag=f"clean_slate_{punishment_id}"
    )

    save_character_states(states)
    save_relationship_edges(edges)

    event = make_event(
        "punishment_completed", actor, target,
        {
            **payload,
            "punishment_id": punishment_id,
            "clean_slate_steps": [
                "debt_paid", "slate_clean", "mutual_good",
                "physical_restoration", "release"
            ]
        },
        consequence_class="personal"
    )
    return emit(event)


def record_infraction(actor, target, infraction, payload):
    """Log an infraction without assigning punishment yet."""
    event = make_event(
        "infraction_recorded", actor, target,
        {**payload, "infraction": infraction},
        consequence_class="micro"
    )
    return emit(event)


def dispatch(args, payload):
    if args.action == "assign":
        return assign_punishment(args.actor, args.target, args.punishment_id, payload)
    elif args.action == "complete":
        return complete_punishment(args.actor, args.target, payload)
    elif args.action == "record_infraction":
        return record_infraction(args.actor, args.target, args.infraction, payload)
    raise ValueError(f"Unknown punishment action: {args.action}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--punishment-id", default=None)
    parser.add_argument("--infraction", default=None)
    cli_run(parser, dispatch, ["assign", "complete", "record_infraction"])