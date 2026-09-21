#!/usr/bin/env python3
"""
validate_all.py - Validator matching actual folder layout. BOM-safe.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXPECTED = {
    "canon": ["characters.json", "kalas.json", "domains.json",
              "institutions.json", "locations.json", "occasions.json"],
    "kama": ["kama_registry_v20.json", "kama_families.json", "kama_dimensions.json",
             "kama_association_types.json", "kama_lifecycle_states.json",
             "kama_risk_classes.json"],
    "kalas": ["kala_system_v20.json", "kala_domains.json",
              "kala_mastery_ladder.json", "kala_synergies.json",
              "kala_kama_linkage.json", "kala_prerequisites_graph.json",
              "character_kala_matrix.json"],
    "matrices": ["character_kala_matrix.json", "character_kama_derived.json",
                 "kala_dimension_matrix.json", "dimension_kama_matrix.json",
                 "character_dimension_weights.json", "kala_kama_links.json"],
    "characters": ["archetypes.json", "cultural_profiles.json",
                   "voice_profiles.json", "character_profiles_v20.json",
                   "role_orientation/schema.json",
                   "role_orientation/orientations.json"],
    "relationships": ["relationship_dimensions.json", "relationship_types.json",
                      "relationship_edges.json", "relationship_memory.json",
                      "reputation_matrix.json"],
    "location": ["institution_registry.json", "location_registry.json",
                 "zone_registry.json", "access_rules.json",
                 "environmental_modifiers.json", "location_affinity.json",
                 "occasion_location_map.json"],
    "scenes": ["scene_engine.json", "scene_templates.json",
               "act_structures.json", "scene_validation_rules.json",
               "current_scene.json"],
    "quests": ["quest_registry_v20.json", "quest_types.json", "quest_states.json",
               "quest_branching.json", "quest_rewards.json",
               "quest_prerequisites.json", "quest_availability_rules.json",
               "quest_failure_modes.json", "quest_chains.json",
               "quest_runtime_schema.json", "multiplayer_quest_rules.json",
               "avn_quest_hooks.json"],
    "registries": ["seva_registry.json"],
    "systems": ["task_system.json", "punishment_system.json",
                "dbt_technique_registry.json", "consent_framework_registry.json",
                "traffic_light_system.json", "reward_registry.json",
                "recovery_action_registry.json", "recovery_system.json",
                "intimate_jewelry_system.json", "jewelry_registry.json",
                "aphrodisiacs_substances_registry.json", "toys_registry.json",
                "journaling_system.json", "contract_system.json",
                "daily_protocol_system.json", "collar_ceremony_system.json",
                "scene_negotiation_system.json", "scene_template_registry.json"],
    "runtime": ["world_state.json", "character_states.json", "telemetry.json",
                "relationship_edges.json", "chandra_kala_modifiers.json",
                "current_scene.json", "session_registry.json",
                "save_contract.json", "multiplayer_coordination.json"],
    "archive": ["events.jsonl", "memories.json"],
    "audit": ["provenance.json", "conflicts.json",
              "canon_decisions.json", "schema_versions.json"],
    "world": ["offices.json"],
    "scripts": ["_antahpura_common.py", "apply_task_event.py",
                "apply_dbt_event.py", "apply_punishment_event.py",
                "apply_consent_event.py", "apply_traffic_light_event.py",
                "apply_journal_event.py", "apply_jewelry_event.py",
                "apply_recovery_event.py", "apply_reward_event.py",
                "derive_character_kama.py", "validate_all.py",
                "replay_events.py"]
}


def load(p):
    # utf-8-sig strips BOM if present; also handles plain UTF-8
    with open(p, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def main():
    errors = []
    warnings = []
    present = 0

    print("Antahpura V20 - Validator (BOM-safe, actual folder names)")
    print(f"Root: {ROOT}\n")

    for folder, files in EXPECTED.items():
        for fname in files:
            p = ROOT / folder / fname
            if p.exists():
                present += 1
            else:
                errors.append(f"Missing: {folder}/{fname}")

    invalid = []
    all_json = list(ROOT.rglob("*.json"))
    for p in all_json:
        try:
            load(p)
        except Exception as e:
            invalid.append(f"{p.relative_to(ROOT)}: {e}")
            errors.append(f"Invalid JSON: {p.relative_to(ROOT)}")

    print(f"Files present: {present}")
    print(f"Files expected: {sum(len(v) for v in EXPECTED.values())}")
    print(f"JSON files validated: {len(all_json)}")
    print(f"Invalid JSON: {len(invalid)}")
    print(f"Warnings: {len(warnings)}")
    print(f"Errors: {len(errors)}\n")

    if warnings:
        print("--- WARNINGS ---")
        for w in warnings:
            print(f"  ! {w}")
        print()

    if errors:
        print("--- ERRORS ---")
        for e in errors:
            print(f"  X {e}")
        print()
        return 1

    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())