#!/usr/bin/env python3
"""
apply_dbt_event.py - Apply DBT techniques as recovery actions.

References:
  systems/dbt_technique_registry.json
  systems/recovery_action_registry.json
  systems/aphrodisiacs_substances_registry.json
  systems/toys_registry.json
  systems/jewelry_registry.json
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


def load_dbt_registry():
    return load_or_default(SYSTEMS / "dbt_technique_registry.json", {"dbt_techniques": {}})


def find_dbt_technique(registry, technique_id):
    techniques = registry.get("dbt_techniques", {})
    for key, tech in techniques.items():
        if tech.get("technique_id") == technique_id:
            return tech
    return None


def ensure_dbt_state(char_state):
    char_state.setdefault("dbt_skills_known", [])
    char_state.setdefault("dbt_skills_practiced", [])
    char_state.setdefault("dbt_effectiveness_rating", 50.0)
    return char_state


def apply_dbt_technique(actor, target, technique_id, payload):
    registry = load_dbt_registry()
    technique = find_dbt_technique(registry, technique_id)
    if not technique:
        raise ValueError(f"Unknown DBT technique: {technique_id}")

    states = load_character_states()
    edges = load_relationship_edges()
    target_state = get_character_state(states, target)
    ensure_dbt_state(target_state)

    if technique_id not in target_state["dbt_skills_known"]:
        target_state["dbt_skills_known"].append(technique_id)

    found = None
    for entry in target_state["dbt_skills_practiced"]:
        if entry["skill_id"] == technique_id:
            found = entry
            break
    if found:
        found["practice_count"] += 1
        found["last_practiced"] = now_iso()
    else:
        target_state["dbt_skills_practiced"].append({
            "skill_id": technique_id,
            "practice_count": 1,
            "last_practiced": now_iso(),
            "mastery_level": 0.2
        })

    effects = technique.get("mechanical_effects", {})
    if "emotional_pressure_reduction" in effects:
        current = target_state.get("emotional_pressure", 0.0)
        target_state["emotional_pressure"] = max(0.0, current - effects["emotional_pressure_reduction"])
    if "physical_energy_restore" in effects:
        current = target_state.get("physical_energy", 100.0)
        target_state["physical_energy"] = min(100.0, current + effects["physical_energy_restore"])
    if "physical_energy_cost" in effects:
        current = target_state.get("physical_energy", 100.0)
        target_state["physical_energy"] = max(0.0, current - effects["physical_energy_cost"])

    target_state["last_updated"] = now_iso()

    if actor != target:
        apply_relationship_delta(
            edges, target, actor,
            {"trust": 2},
            memory_tag=f"dbt_{technique_id}"
        )

    save_character_states(states)
    save_relationship_edges(edges)

    return emit(make_event(
        "dbt_technique_applied", actor, target,
        {
            **payload,
            "technique_id": technique_id,
            "module": technique.get("module"),
            "effects": effects
        },
        consequence_class="micro"
    ))


def apply_self_soothing(actor, target, payload):
    states = load_character_states()
    target_state = get_character_state(states, target)

    target_state["emotional_pressure"] = max(0.0, target_state.get("emotional_pressure", 0.0) - 30)
    target_state["physical_energy"] = min(100.0, target_state.get("physical_energy", 100.0) + 10)

    senses_used = payload.get("senses_used", ["smell", "touch"])
    registries_used = []
    if "smell" in senses_used:
        registries_used.append("aphrodisiacs_substances_registry")
    if "touch" in senses_used:
        registries_used.append("toys_registry")
    if "sight" in senses_used:
        registries_used.append("jewelry_registry")

    save_character_states(states)

    return emit(make_event(
        "self_soothing_applied", actor, target,
        {
            **payload,
            "senses_used": senses_used,
            "registries_referenced": registries_used
        },
        consequence_class="micro"
    ))


def dispatch(args, payload):
    if args.action == "apply":
        return apply_dbt_technique(args.actor, args.target, args.technique_id, payload)
    elif args.action == "self_soothing":
        return apply_self_soothing(args.actor, args.target, payload)
    raise ValueError(f"Unknown DBT action: {args.action}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--technique-id", default=None)
    cli_run(parser, dispatch, ["apply", "self_soothing"])