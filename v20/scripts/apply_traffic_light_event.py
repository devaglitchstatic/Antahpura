#!/usr/bin/env python3
"""
apply_traffic_light_event.py — Record traffic light signals during scenes.
Handles green/yellow/red, non-verbal alternatives, and automatic
state transitions.
References: systems/traffic_light_system.json,
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


def load_traffic_registry():
    return load_or_default(SYSTEMS / "traffic_light_system.json", {"traffic_lights": {}})


def ensure_traffic_state(char_state, scene_id):
    char_state.setdefault("scene_traffic", {})
    if scene_id not in char_state["scene_traffic"]:
        char_state["scene_traffic"][scene_id] = {
            "current_signal": "green",
            "signal_history": [],
            "last_check_at": now_iso()
        }
    return char_state["scene_traffic"][scene_id]


def record_signal(actor, target, payload):
    """Record a traffic light signal. actor is the one giving the signal."""
    signal = payload.get("signal", "green").lower()
    if signal not in ("green", "yellow", "red"):
        raise ValueError(f"Invalid signal: {signal}")

    scene_id = payload.get("scene_id", f"scene_{now_iso()}")

    states = load_character_states()
    edges = load_relationship_edges()
    actor_state = get_character_state(states, actor)

    scene_state = ensure_traffic_state(actor_state, scene_id)
    scene_state["signal_history"].append({
        "signal": signal,
        "timestamp": now_iso(),
        "cause": payload.get("cause"),
        "action_taken": payload.get("action_taken", "pending")
    })
    scene_state["current_signal"] = signal
    scene_state["last_check_at"] = now_iso()
    actor_state["last_updated"] = now_iso()

    # Reactive handling
    reaction = None
    if signal == "yellow":
        reaction = {
            "action_required": "adjust_scene",
            "scene_continues": True,
            "recommended_actions": ["reduce_intensity", "change_position", "pause_for_checkin"]
        }
    elif signal == "red":
        reaction = {
            "action_required": "stop_scene",
            "scene_continues": False,
            "mandatory_actions": [
                "stop_all_stimulation",
                "drop_character",
                "transition_to_aftercare",
                "apply_grounding_technique"
            ]
        }

    # Trust impact
    if signal in ("yellow", "red") and target and target != actor:
        apply_relationship_delta(
            edges, actor, target,
            {"trust": 1 if signal == "yellow" else 3},
            memory_tag=f"traffic_{signal}"
        )
    else:
        save_relationship_edges = True  # no-op marker

    save_character_states(states)
    if signal in ("yellow", "red") and target and target != actor:
        save_relationship_edges(edges)

    event = make_event(
        "traffic_signal", actor, target,
        {
            **payload,
            "signal": signal,
            "scene_id": scene_id,
            "reaction": reaction
        },
        consequence_class="micro"
    )
    return emit(event)


def record_non_verbal(actor, target, payload):
    """Record a non-verbal safe signal (double-tap, squeeze, drop, thumb)."""
    signal_map = {
        "double_tap": "red",
        "drop_signal": "red",
        "one_squeeze": "green",
        "two_squeezes": "yellow",
        "three_squeezes": "red",
        "thumb_up": "green",
        "thumb_sideways": "yellow",
        "thumb_down": "red"
    }

    non_verbal = payload.get("non_verbal_signal")
    if non_verbal not in signal_map:
        raise ValueError(f"Unknown non-verbal signal: {non_verbal}")

    payload["signal"] = signal_map[non_verbal]
    payload["source"] = "non_verbal"
    return record_signal(actor, target, payload)


def check_in(actor, target, payload):
    """Periodic green check-in between scenes."""
    payload["signal"] = "green"
    payload["cause"] = payload.get("cause", "periodic_checkin")
    return record_signal(actor, target, payload)


def dispatch(args, payload):
    if args.action == "signal":
        return record_signal(args.actor, args.target, payload)
    elif args.action == "non_verbal":
        return record_non_verbal(args.actor, args.target, payload)
    elif args.action == "check_in":
        return check_in(args.actor, args.target, payload)
    raise ValueError(f"Unknown traffic action: {args.action}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--signal", default="green", choices=["green", "yellow", "red"])
    parser.add_argument("--cause", default=None)
    parser.add_argument("--non-verbal-signal", default=None,
                        choices=["double_tap", "drop_signal", "one_squeeze",
                                 "two_squeezes", "three_squeezes",
                                 "thumb_up", "thumb_sideways", "thumb_down"])
    cli_run(parser, dispatch, ["signal", "non_verbal", "check_in"])