#!/usr/bin/env python3
"""
fill_stubs.py - Fills the 16 empty stub files with real content.
Quest sub-files (12) + Relationship sub-files (4).
Run once. Idempotent - re-running overwrites.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUESTS = ROOT / "quests"
REL = ROOT / "relationships"
QUESTS.mkdir(parents=True, exist_ok=True)
REL.mkdir(parents=True, exist_ok=True)


def save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"WROTE: {path.relative_to(ROOT)}  ({path.stat().st_size} bytes)")


# =====================================================================
# QUEST SUB-FILES
# =====================================================================

save(QUESTS / "quest_types.json", {
    "schema": "antahpura.quest.types",
    "version": "20.0",
    "total_types": 9,
    "types": {
        "character_quest": {"name": "Character Quest", "description": "Personal arc centered on one character", "issuer": "any", "reward_class": "personal"},
        "institutional_quest": {"name": "Institutional Quest", "description": "Mission on behalf of an institution", "issuer": "institution_leader", "reward_class": "institutional"},
        "kala_quest": {"name": "Kala Quest", "description": "Mastery progression via structured challenge", "issuer": "teacher", "reward_class": "personal"},
        "ritual_quest": {"name": "Ritual Quest", "description": "Ceremony preparation and execution", "issuer": "esoteric_authority", "reward_class": "narrative"},
        "political_quest": {"name": "Political Quest", "description": "Court intrigue, alliance negotiation", "issuer": "high_status_character", "reward_class": "institutional"},
        "investigation_quest": {"name": "Investigation Quest", "description": "Secret discovery, cipher work", "issuer": "cipher_keeper", "reward_class": "narrative"},
        "relationship_quest": {"name": "Relationship Quest", "description": "Deepening or repairing a specific relationship", "issuer": "either_party", "reward_class": "personal"},
        "archival_quest": {"name": "Archival Quest", "description": "Recover or decode historical record", "issuer": "archivist", "reward_class": "narrative"},
        "exploration_quest": {"name": "Exploration Quest", "description": "Discover new location or secret passage", "issuer": "any_curious", "reward_class": "personal"}
    }
})

save(QUESTS / "quest_states.json", {
    "schema": "antahpura.quest.states",
    "version": "20.0",
    "total_states": 9,
    "states": {
        "locked": {"description": "Prerequisites not met"},
        "available": {"description": "Prerequisites met, not yet accepted"},
        "accepted": {"description": "Player has accepted the quest"},
        "in_progress": {"description": "Active work on the quest"},
        "blocked": {"description": "Temporarily stalled pending event or unlock"},
        "completed": {"description": "Successfully finished"},
        "failed": {"description": "Failure condition triggered"},
        "abandoned": {"description": "Player chose to abandon"},
        "expired": {"description": "Time limit passed"}
    }
})

save(QUESTS / "quest_branching.json", {
    "schema": "antahpura.quest.branching",
    "version": "20.0",
    "branch_types": {
        "linear": {"description": "No branching; single path to completion"},
        "diamond": {"description": "Branches and rejoins; different paths reach same ending"},
        "tree": {"description": "Branches do not rejoin; different endings"},
        "web": {"description": "Multiple branch and rejoin points"}
    },
    "branch_resolution": {
        "immediate": {"description": "Branching choice resolves instantly"},
        "deferred": {"description": "Resolves at chapter end"},
        "persistent": {"description": "Choice permanently alters quest line"}
    }
})

save(QUESTS / "quest_rewards.json", {
    "schema": "antahpura.quest.rewards",
    "version": "20.0",
    "total_categories": 10,
    "categories": {
        "kala_mastery": {"effect": "Adds mastery points to one or more kalas", "example": "+2 mastery to kala_granthana"},
        "kama_affinity": {"effect": "Advances one or more kamas in lifecycle", "example": "GRANTHI_KALA advances from mentionable to discussable"},
        "relationship_delta": {"effect": "Modifies dimensions on specific edges", "example": "+5 trust with char_roxana"},
        "institutional_reputation": {"effect": "Changes institutional reputation", "example": "+2 to inst_ritual_chorus"},
        "access_permission": {"effect": "Unlocks a location or increases access level", "example": "Unlocks loc_hidden_archive"},
        "secret_discovery": {"effect": "Reveals a specific secret", "example": "Reveals secret_hidden_archive_1"},
        "item_acquisition": {"effect": "Grants an item or artifact", "example": "Grants cipher key"},
        "scene_unlock": {"effect": "Unlocks a scene template", "example": "Unlocks scene_predynastic_ritual"},
        "quest_unlock": {"effect": "Opens a follow-up quest", "example": "Unlocks quest_full_cipher"},
        "avn_gallery_unlock": {"effect": "Unlocks AVN asset for gallery", "example": "Unlocks asset patala_revelation"}
    }
})

save(QUESTS / "quest_prerequisites.json", {
    "schema": "antahpura.quest.prerequisites",
    "version": "20.0",
    "total_types": 8,
    "types": {
        "kala_requirement": {"type": "kala_mastery", "example": "kala_cipher >= 3"},
        "kama_requirement": {"type": "kama_lifecycle", "example": "NIBANDHA_PRACODANA >= discussable"},
        "relationship_requirement": {"type": "relationship_edge", "example": "char_reva to char_anisa trust >= 60"},
        "institutional_requirement": {"type": "institutional_reputation", "example": "inst_administrative_court >= 4"},
        "location_requirement": {"type": "location_access", "example": "access to loc_archive"},
        "quest_requirement": {"type": "quest_completion", "example": "quest_ledger_investigation completed"},
        "occasion_requirement": {"type": "occasion_trigger", "example": "during cakra_puja"},
        "chandra_kala_requirement": {"type": "lunar_phase", "example": "full_moon"}
    }
})

save(QUESTS / "quest_availability_rules.json", {
    "schema": "antahpura.quest.availability_rules",
    "version": "20.0",
    "total_rules": 5,
    "rules": [
        {"rule_id": "avail_001", "name": "Chapter Gating", "condition": "current_chapter within quest.chapter_range"},
        {"rule_id": "avail_002", "name": "Prerequisite Check", "condition": "all quest.prerequisites satisfied"},
        {"rule_id": "avail_003", "name": "Issuer Availability", "condition": "issuer alive, present, not otherwise engaged"},
        {"rule_id": "avail_004", "name": "Occasion Availability", "condition": "required occasion is active or always-on"},
        {"rule_id": "avail_005", "name": "Chain Position", "condition": "if part of chain, previous step completed"}
    ]
})

save(QUESTS / "quest_failure_modes.json", {
    "schema": "antahpura.quest.failure_modes",
    "version": "20.0",
    "total_modes": 6,
    "modes": [
        {"mode_id": "fail_001", "name": "Time Expired", "trigger": "quest time limit passed"},
        {"mode_id": "fail_002", "name": "Critical Character Loss", "trigger": "required character unavailable"},
        {"mode_id": "fail_003", "name": "Reputation Collapse", "trigger": "issuer institutional reputation below threshold"},
        {"mode_id": "fail_004", "name": "Relationship Rupture", "trigger": "key relationship edge drops below minimum"},
        {"mode_id": "fail_005", "name": "Choice Misalignment", "trigger": "player choice in Act 4 contradicts premise"},
        {"mode_id": "fail_006", "name": "Abandonment", "trigger": "player explicitly abandons quest"}
    ],
    "failure_consequences": [
        "Quest becomes failed state",
        "Partial rewards may still be granted",
        "Relationship penalties applied",
        "Possible redemption quest unlocked"
    ]
})

save(QUESTS / "quest_chains.json", {
    "schema": "antahpura.quest.chains",
    "version": "20.0",
    "total_chains": 3,
    "chains": {
        "cipher_chain": {
            "name": "The Cipher Chain",
            "steps": [
                "quest_side_001 -> unlocks -> quest_side_002",
                "quest_side_002 -> unlocks -> quest_main_002",
                "quest_main_002 -> unlocks (reveal branch) -> quest_full_cipher",
                "quest_full_cipher -> unlocks -> quest_main_003"
            ],
            "narrative_arc": "Discovery of a hidden cipher network spanning generations"
        },
        "initiation_chain": {
            "name": "The Initiation Chain",
            "steps": [
                "quest_main_004 -> unlocks -> quest_main_001",
                "quest_main_001 -> unlocks -> quest_main_006",
                "quest_main_006 -> unlocks -> quest_main_008"
            ],
            "narrative_arc": "Kumari Rati's path through apprenticeship to mastery"
        },
        "political_chain": {
            "name": "The Political Chain",
            "steps": [
                "quest_side_002 -> unlocks -> quest_main_005",
                "quest_main_005 (war) -> unlocks -> quest_war_preparation",
                "quest_main_005 (peace) -> unlocks -> quest_trade_accord"
            ],
            "narrative_arc": "Court intrigue escalating to regional politics"
        }
    }
})

save(QUESTS / "quest_runtime_schema.json", {
    "schema": "antahpura.quest.runtime_schema",
    "version": "20.0",
    "fields": {
        "quest_id": "string",
        "character_id": "char_id",
        "state": "locked|available|accepted|in_progress|blocked|completed|failed|abandoned|expired",
        "current_act": "integer (1-4)",
        "current_objective": "string",
        "branches_taken": ["branch_id"],
        "prerequisites_met": ["string"],
        "prerequisites_pending": ["string"],
        "started_at": "iso_8601 | null",
        "last_updated": "iso_8601",
        "completed_at": "iso_8601 | null",
        "rewards_granted": ["reward_id"],
        "blocking_conditions": ["string"],
        "failed_at": "iso_8601 | null",
        "failure_mode": "string | null"
    }
})

save(QUESTS / "multiplayer_quest_rules.json", {
    "schema": "antahpura.quest.multiplayer",
    "version": "20.0",
    "total_rules": 4,
    "rules": [
        {"rule_id": "mquest_001", "name": "Consent for Shared Quests", "description": "All players must consent before a shared quest activates"},
        {"rule_id": "mquest_002", "name": "Quest State Consensus", "description": "Major branch decisions require consensus or designated decision-maker"},
        {"rule_id": "mquest_003", "name": "POV Leasing During Quest", "description": "Quests may lease POV to specific characters for specific scenes"},
        {"rule_id": "mquest_004", "name": "Reward Distribution", "description": "Rewards distributed per participant based on role and contribution"}
    ]
})

save(QUESTS / "avn_quest_hooks.json", {
    "schema": "antahpura.quest.avn_hooks",
    "version": "20.0",
    "hooks": [
        {"quest_id": "quest_main_001", "unlockable_assets": [
            {"asset_id": "initiation_act1_loop", "unlock": "act_1_complete"},
            {"asset_id": "initiation_act3_loop", "unlock": "act_3_complete"},
            {"asset_id": "initiation_finale", "unlock": "quest_complete"}
        ]},
        {"quest_id": "quest_main_002", "unlockable_assets": [
            {"asset_id": "cipher_extraction", "unlock": "act_2_complete"},
            {"asset_id": "cipher_revelation", "unlock": "act_4_reveal_branch"}
        ]},
        {"quest_id": "quest_main_006", "unlockable_assets": [
            {"asset_id": "saffron_confinement_loop", "unlock": "act_2_complete"},
            {"asset_id": "saffron_integration", "unlock": "quest_complete"}
        ]}
    ]
})

# quest_registry_v20 - the composite already exists as quest_system_v20.json,
# but we create a canonical id-sorted registry for the runtime to consume.
save(QUESTS / "quest_registry_v20.json", {
    "schema": "antahpura.quest.registry_v20",
    "version": "20.0",
    "note": "Full quest definitions live in quest_system_v20.json. This file is the runtime index.",
    "main_quest_ids": [
        "quest_main_001", "quest_main_002", "quest_main_003", "quest_main_004",
        "quest_main_005", "quest_main_006", "quest_main_007", "quest_main_008"
    ],
    "side_quest_ids": [
        "quest_side_001", "quest_side_002", "quest_side_003",
        "quest_side_004", "quest_side_005", "quest_side_006"
    ]
})


# =====================================================================
# RELATIONSHIP SUB-FILES
# =====================================================================

save(REL / "relationship_dimensions.json", {
    "schema": "antahpura.relationship.dimensions",
    "version": "20.0",
    "total_dimensions": 11,
    "dimensions": {
        "affection": {"description": "Warmth, fondness, personal liking", "range": [0, 100], "default": 50},
        "trust": {"description": "Reliance on reliability, safety, honesty", "range": [0, 100], "default": 40},
        "respect": {"description": "Regard for competence, judgment, character", "range": [0, 100], "default": 50},
        "obligation": {"description": "Sense of duty, debt, or binding commitment", "range": [0, 100], "default": 30},
        "rivalry": {"description": "Competitive tension, ambition, friction", "range": [0, 100], "default": 10},
        "loyalty": {"description": "Alignment, faithfulness, willingness to defend", "range": [0, 100], "default": 40},
        "curiosity": {"description": "Interest in knowing the other more deeply", "range": [0, 100], "default": 30},
        "fear": {"description": "Wariness, intimidation, dread", "range": [0, 100], "default": 15},
        "dependency": {"description": "Reliance on the other for emotional/practical needs", "range": [0, 100], "default": 20},
        "resentment": {"description": "Unresolved grievance, bitterness, hidden anger", "range": [0, 100], "default": 5},
        "familiarity": {"description": "Depth of shared history and knowledge of each other", "range": [0, 100], "default": 25}
    }
})

save(REL / "relationship_types.json", {
    "schema": "antahpura.relationship.types",
    "version": "20.0",
    "total_types": 14,
    "types": {
        "authority_to_subordinate": {"power_direction": "downward", "description": "Institutional command"},
        "submissive_to_authority": {"power_direction": "upward", "description": "Submission to authority"},
        "peer_colleague": {"power_direction": "lateral", "description": "Institutional equals"},
        "peer_rival": {"power_direction": "lateral", "description": "Competitive equals"},
        "mentor_to_student": {"power_direction": "downward", "description": "Teaching relationship"},
        "student_to_mentor": {"power_direction": "upward", "description": "Learning relationship"},
        "caregiver_to_charge": {"power_direction": "downward", "description": "Protective relationship"},
        "charge_to_caregiver": {"power_direction": "upward", "description": "Dependent relationship"},
        "intimate_partner": {"power_direction": "bidirectional", "description": "Romantic or erotic bond"},
        "sacred_bond": {"power_direction": "bidirectional", "description": "Ritual kinship"},
        "observer_to_subject": {"power_direction": "directional", "description": "Monitoring relationship"},
        "subject_to_observer": {"power_direction": "directional", "description": "Observed relationship"},
        "allied": {"power_direction": "lateral", "description": "Shared cause"},
        "unknown": {"power_direction": "neutral", "description": "Not yet established"}
    }
})

save(REL / "relationship_memory.json", {
    "schema": "antahpura.relationship.memory",
    "version": "20.0",
    "memory_entry_schema": {
        "memory_id": "string",
        "character": "char_id",
        "relationship_target": "char_id",
        "event_id": "string",
        "timestamp": "iso_8601",
        "event_description": "string",
        "dimension_changes": {"affection": "integer", "trust": "integer", "respect": "integer", "loyalty": "integer"},
        "memory_tag": "string",
        "salience": "float (0-1)",
        "persists": "boolean"
    },
    "memory_tags": [
        "public_praise", "public_criticism",
        "private_confession", "private_trust",
        "sacrifice", "protection",
        "betrayal", "forgiveness",
        "shared_ritual", "shared_grief",
        "rivalry_escalation", "rivalry_resolution",
        "intimacy_milestone", "intimacy_rupture"
    ],
    "standard_event_effects": {
        "public_praise": {"affection": 3, "trust": 2, "respect": 4, "rivalry": -1, "loyalty": 2},
        "public_criticism": {"affection": -4, "trust": -3, "respect": -2, "rivalry": 3, "loyalty": -1},
        "private_confession": {"affection": 5, "trust": 6, "respect": 2, "loyalty": 3},
        "protection_offered": {"affection": 4, "trust": 5, "respect": 4, "loyalty": 5},
        "betrayal_minor": {"affection": -8, "trust": -15, "respect": -5, "rivalry": 10, "loyalty": -10},
        "betrayal_major": {"affection": -20, "trust": -40, "respect": -15, "rivalry": 25, "loyalty": -30},
        "forgiveness_granted": {"affection": 12, "trust": 15, "respect": 8, "rivalry": -15, "loyalty": 10},
        "shared_ritual": {"affection": 4, "trust": 4, "respect": 3, "rivalry": -2, "loyalty": 3},
        "rivalry_escalation": {"affection": -3, "trust": -2, "rivalry": 8, "loyalty": -3},
        "intimacy_milestone": {"affection": 10, "trust": 8, "respect": 5, "rivalry": -5, "loyalty": 8}
    }
})

save(REL / "reputation_matrix.json", {
    "schema": "antahpura.relationship.reputation_matrix",
    "version": "20.0",
    "reputation_layers": {
        "personal_reputation": {"description": "Who the character is privately", "range": [0, 100]},
        "institutional_reputation": {"description": "What each institution thinks of the character", "range": [0, 100], "per_institution": True},
        "public_reputation": {"description": "What the court thinks", "range": [0, 100]},
        "private_reputation": {"description": "What a small trusted circle knows", "range": [0, 100], "per_character": True}
    },
    "institutions_tracked": [
        "inst_throne",
        "inst_zenana",
        "inst_military_perimeter",
        "inst_administrative_court",
        "inst_yogic_pavilion",
        "inst_subterranean_vaults",
        "inst_ritual_chorus"
    ],
    "example_profile": {
        "character_id": "char_svara",
        "personal_reputation": 55,
        "institutional_reputation": {
            "inst_throne": 40,
            "inst_zenana": 55,
            "inst_military_perimeter": 30,
            "inst_administrative_court": 45,
            "inst_yogic_pavilion": 50,
            "inst_subterranean_vaults": 45,
            "inst_ritual_chorus": 78
        },
        "public_reputation": 50,
        "private_reputation": {
            "char_kumari_rati": 72,
            "char_shrinagar": 65,
            "char_reva": 70,
            "char_tarana": 68
        }
    }
})


print("\nAll 16 stub files filled.")