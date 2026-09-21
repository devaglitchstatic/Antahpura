#!/usr/bin/env python3
"""
extract_all_composites.py - Splits composite files into canonical sub-files.

Reads composites:
  location/location_system_v20.json
  quests/quest_system_v20.json
  scenes/Scene Engine V20.json
  relationships/relationship_system_v20.json + V17_1_RELATIONSHIP_REGISTRY.json
  characters/main_*.json + cultural_profiles.json + voice_profiles.json + archetypes.json

Writes sub-files into their respective folders. Never overwrites composites.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def save(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"WROTE: {p.relative_to(ROOT)}  ({p.stat().st_size} bytes)")


def try_load(*paths):
    for p in paths:
        if p.exists():
            return load(p)
    return None


# ============================================================
# 1. LOCATION SUB-FILES
# ============================================================
print("\n=== LOCATION SUB-FILES ===")
loc = try_load(
    ROOT / "location" / "location_system_v20.json",
    ROOT / "location" / "Location System V20 - Complete Registry.json",
)
if loc:
    out_dir = ROOT / "location"
    save(out_dir / "institution_registry.json", {
        "schema": "antahpura.location.institution_registry",
        "version": "20.0",
        "institutions": loc.get("institutions", {})
    })
    save(out_dir / "location_registry.json", {
        "schema": "antahpura.location.location_registry",
        "version": "20.0",
        "total_locations": len(loc.get("locations", {})),
        "locations": loc.get("locations", {})
    })
    save(out_dir / "zone_registry.json", {
        "schema": "antahpura.location.zone_registry",
        "version": "20.0",
        "zones": loc.get("zones", {})
    })
    save(out_dir / "access_rules.json", {
        "schema": "antahpura.location.access_rules",
        "version": "20.0",
        "access_rules": loc.get("access_rules", {})
    })
    save(out_dir / "environmental_modifiers.json", {
        "schema": "antahpura.location.environmental_modifiers",
        "version": "20.0",
        "modifiers": loc.get("environmental_modifiers", {})
    })
    save(out_dir / "location_affinity.json", {
        "schema": "antahpura.location.location_affinity",
        "version": "20.0",
        "affinity": loc.get("character_location_affinity", {})
    })
    save(out_dir / "occasion_location_map.json", {
        "schema": "antahpura.location.occasion_location_map",
        "version": "20.0",
        "map": loc.get("occasion_location_map", {})
    })


# ============================================================
# 2. QUEST SUB-FILES
# ============================================================
print("\n=== QUEST SUB-FILES ===")
qs = try_load(ROOT / "quests" / "quest_system_v20.json")
if qs:
    out_dir = ROOT / "quests"
    sub = qs.get("quest_system", {})
    save(out_dir / "quest_types.json", {
        "schema": "antahpura.quest.types",
        "version": "20.0",
        "types": sub.get("quest_types", {})
    })
    save(out_dir / "quest_states.json", {
        "schema": "antahpura.quest.states",
        "version": "20.0",
        "states": sub.get("quest_states", {})
    })
    save(out_dir / "quest_branching.json", {
        "schema": "antahpura.quest.branching",
        "version": "20.0",
        "branching": sub.get("quest_branching", {})
    })
    save(out_dir / "quest_rewards.json", {
        "schema": "antahpura.quest.rewards",
        "version": "20.0",
        "rewards": sub.get("quest_rewards", {})
    })
    save(out_dir / "quest_prerequisites.json", {
        "schema": "antahpura.quest.prerequisites",
        "version": "20.0",
        "prerequisites": sub.get("quest_prerequisites", {})
    })
    save(out_dir / "quest_availability_rules.json", {
        "schema": "antahpura.quest.availability_rules",
        "version": "20.0",
        "rules": sub.get("quest_availability_rules", {})
    })
    save(out_dir / "quest_failure_modes.json", {
        "schema": "antahpura.quest.failure_modes",
        "version": "20.0",
        "modes": sub.get("quest_failure_modes", {})
    })
    save(out_dir / "quest_chains.json", {
        "schema": "antahpura.quest.chains",
        "version": "20.0",
        "chains": sub.get("quest_chain_examples", {})
    })
    save(out_dir / "quest_runtime_schema.json", {
        "schema": "antahpura.quest.runtime_schema",
        "version": "20.0",
        "runtime": sub.get("runtime_quest_state", {})
    })
    save(out_dir / "multiplayer_quest_rules.json", {
        "schema": "antahpura.quest.multiplayer",
        "version": "20.0",
        "rules": sub.get("multiplayer_quest_coordination", {})
    })
    save(out_dir / "avn_quest_hooks.json", {
        "schema": "antahpura.quest.avn_hooks",
        "version": "20.0",
        "hooks": sub.get("avn_quest_hooks", {})
    })
    # quest_registry_v20.json is the composite itself - copy under canonical name
    save(out_dir / "quest_registry_v20.json", {
        "schema": "antahpura.quest.registry_v20",
        "version": "20.0",
        "main_quests": sub.get("quest_registry", {}).get("main_quests", []),
        "side_quests": sub.get("quest_registry", {}).get("side_quests", [])
    })


# ============================================================
# 3. SCENE SUB-FILES
# ============================================================
print("\n=== SCENE SUB-FILES ===")
se = try_load(
    ROOT / "scenes" / "Scene Engine V20.json",
    ROOT / "scenes" / "scene_engine.json"
)
if se:
    out_dir = ROOT / "scenes"
    engine = se.get("scene_engine", se)
    save(out_dir / "scene_engine.json", {
        "schema": "antahpura.scene.engine",
        "version": "20.0",
        "scene_types": engine.get("scene_types", {}),
        "act_structure": engine.get("act_structure", {})
    })
    save(out_dir / "act_structures.json", {
        "schema": "antahpura.scene.act_structures",
        "version": "20.0",
        "acts": engine.get("act_structure", {}).get("acts", {})
    })
    save(out_dir / "scene_validation_rules.json", {
        "schema": "antahpura.scene.validation_rules",
        "version": "20.0",
        "rules": engine.get("scene_validation_rules", {}).get("rules", [])
    })
    # scene_templates.json comes from systems/scene_template_registry.json
    tmpl_src = ROOT / "systems" / "scene_template_registry.json"
    if tmpl_src.exists():
        tmpl = load(tmpl_src)
        save(out_dir / "scene_templates.json", {
            "schema": "antahpura.scene.templates",
            "version": "20.0",
            "total_templates": tmpl.get("total_templates", 0),
            "templates": tmpl.get("scene_templates", [])
        })


# ============================================================
# 4. RELATIONSHIP SUB-FILES
# ============================================================
print("\n=== RELATIONSHIP SUB-FILES ===")
rs = try_load(ROOT / "relationships" / "relationship_system_v20.json")
if rs:
    out_dir = ROOT / "relationships"
    body = rs.get("relationship_system", rs)
    save(out_dir / "relationship_dimensions.json", {
        "schema": "antahpura.relationship.dimensions",
        "version": "20.0",
        "dimensions": body.get("relationship_dimensions", {})
    })
    save(out_dir / "relationship_types.json", {
        "schema": "antahpura.relationship.types",
        "version": "20.0",
        "types": body.get("relationship_types", {})
    })
    save(out_dir / "relationship_memory.json", {
        "schema": "antahpura.relationship.memory",
        "version": "20.0",
        "memory_schema": body.get("relationship_memory", {})
    })
    save(out_dir / "reputation_matrix.json", {
        "schema": "antahpura.relationship.reputation_matrix",
        "version": "20.0",
        "matrix": body.get("reputation_matrix", {}),
        "institutional_profile_example": body.get("institutional_allegiance_profile", {})
    })


# ============================================================
# 5. CHARACTER PROFILES AGGREGATE
# ============================================================
print("\n=== CHARACTER PROFILES AGGREGATE ===")
chars_dir = ROOT / "characters"
profiles = {}
for spec in sorted(chars_dir.glob("main_*.json")):
    try:
        d = load(spec)
        # Try to extract a char id from spec content, else derive from filename
        cid = None
        for k in ("character_id", "id", "canon_id", "slug"):
            if isinstance(d, dict) and k in d:
                cid = d[k]
                break
        if not cid:
            # derive from filename: main_anisa-xxxx_spec_v2.json -> char_anisa
            name = spec.stem.replace("main_", "").split("-")[0]
            cid = f"char_{name.lower()}"
        profiles[cid] = {
            "spec_source": spec.name,
            "content": d
        }
    except Exception as e:
        print(f"  SKIP {spec.name}: {e}")

save(chars_dir / "character_profiles_v20.json", {
    "schema": "antahpura.character.profiles_v20",
    "version": "20.0",
    "source": "aggregated from main_*_spec_v2.json",
    "total_profiles": len(profiles),
    "profiles": profiles
})


# ============================================================
# 6. WORLD LOCATIONS ALIAS
# ============================================================
print("\n=== WORLD LOCATIONS ALIAS ===")
canon_loc = ROOT / "canon" / "locations.json"
if canon_loc.exists():
    save(ROOT / "world" / "locations.json", load(canon_loc))


print("\nAll extractions complete.")