#!/usr/bin/env python3
"""
apply_consent_event.py — Record consent negotiation, framework selection,
and consent state changes.
References: systems/consent_framework_registry.json,
            systems/traffic_light_system.json
"""

import argparse
from _antahpura_common import (
    SYSTEMS, load, load_or_default,
    make_event, emit, now_iso,
    get_character_state,
    load_character_states, save_character_states,
    cli_run
)


def load_consent_registry():
    return load_or_default(SYSTEMS / "consent_framework_registry.json", {"frameworks": {}})


def ensure_consent_state(char_state):
    char_state.setdefault("active_framework", "SSC")
    char_state.setdefault("consent_records", [])
    return char_state


def record_negotiation(actor, target, payload):
    """Record a completed pre-scene negotiation."""
    registry = load_consent_registry()
    framework = payload.get("framework", "SSC")
    if framework not in registry.get("frameworks", {}):
        raise ValueError(f"Unknown consent framework: {framework}")

    states = load_character_states()
    actor_state = get_character_state(states, actor)
    target_state = get_character_state(states, target)
    ensure_consent_state(actor_state)
    ensure_consent_state(target_state)

    record = {
        "scene_id": payload.get("scene_id", f"scene_{now_iso()}"),
        "partner": target,
        "framework": framework,
        "negotiation_completed": True,
        "traffic_light_system_active": True,
        "hard_limits": payload.get("hard_limits", []),
        "soft_limits": payload.get("soft_limits", []),
        "aftercare_plan": payload.get("aftercare_plan", {}),
        "consent_given_at": now_iso(),
        "consent_revoked_at": None
    }

    actor_state["consent_records"].append(record)
    mirror = dict(record)
    mirror["partner"] = actor
    target_state["consent_records"].append(mirror)
    actor_state["active_framework"] = framework
    target_state["active_framework"] = framework
    actor_state["last_updated"] = now_iso()
    target_state["last_updated"] = now_iso()
    save_character_states(states)

    event = make_event(
        "consent_negotiated", actor, target,
        {
            **payload,
            "framework": framework,
            "hard_limits": record["hard_limits"],
            "soft_limits": record["soft_limits"]
        },
        consequence_class="personal"
    )
    return emit(event)


def revoke_consent(actor, target, payload):
    """Revoke consent for a specific scene or ongoing dynamic."""
    states = load_character_states()
    actor_state = get_character_state(states, actor)
    ensure_consent_state(actor_state)

    scene_id = payload.get("scene_id")
    for record in reversed(actor_state["consent_records"]):
        if scene_id is None or record.get("scene_id") == scene_id:
            record["consent_revoked_at"] = now_iso()
            record["revoked"] = True
            break

    actor_state["last_updated"] = now_iso()
    save_character_states(states)

    event = make_event(
        "consent_revoked", actor, target,
        {**payload, "scene_id": scene_id},
        consequence_class="narrative"
    )
    return emit(event)


def set_framework(actor, target, payload):
    """Change the active consent framework for the dynamic."""
    framework = payload.get("framework")
    registry = load_consent_registry()
    if framework not in registry.get("frameworks", {}):
        raise ValueError(f"Unknown framework: {framework}")

    states = load_character_states()
    actor_state = get_character_state(states, actor)
    ensure_consent_state(actor_state)
    actor_state["active_framework"] = framework
    actor_state["last_updated"] = now_iso()
    save_character_states(states)

    event = make_event(
        "consent_framework_changed", actor, target,
        {**payload, "framework": framework},
        consequence_class="personal"
    )
    return emit(event)


def dispatch(args, payload):
    if args.action == "negotiate":
        return record_negotiation(args.actor, args.target, payload)
    elif args.action == "revoke":
        return revoke_consent(args.actor, args.target, payload)
    elif args.action == "set_framework":
        return set_framework(args.actor, args.target, payload)
    raise ValueError(f"Unknown consent action: {args.action}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--framework", default="SSC")
    parser.add_argument("--hard-limits", nargs="*", default=[])
    parser.add_argument("--soft-limits", nargs="*", default=[])
    cli_run(parser, dispatch, ["negotiate", "revoke", "set_framework"])