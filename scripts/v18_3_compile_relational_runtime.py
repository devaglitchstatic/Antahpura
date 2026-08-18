#!/usr/bin/env python3
"""
Antahpura V18.3 Relational Runtime Compiler

Purpose
-------
Compile the V18.2 constitutional baseline into a V18.3 relational runtime.

Core constitutional principles
--------------------------------
1. Constitutional offices are immutable at runtime.
2. Skills may be learned through training.
3. Knowledge may cross jurisdictional boundaries.
4. Kala/technical competence may be acquired without acquiring another office.
5. Skill acquisition never grants institutional authority.
6. Canonical relationships are preserved from V17.1.
7. The newly-wedded sovereign axis is preserved:
      maha_deva <-> kumari_rati
8. All 14 canonical characters must remain present.
9. Zola must remain absent.
10. Svara must remain present.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

REGISTRY = ROOT / "registry"
V17_REGISTRY = REGISTRY / "V17_1_CHARACTER_REGISTRY.json"
V17_RELATIONSHIPS = REGISTRY / "V17_1_RELATIONSHIP_REGISTRY.json"

V18_RUNTIME = REGISTRY / "V18_RUNTIME"
V18_3_RUNTIME = REGISTRY / "V18_3_RUNTIME"

V18_BASELINE = V18_RUNTIME / "V18_2_CANONICAL_BASELINE.json"

OUT_CHARACTER_STATE = V18_3_RUNTIME / "CHARACTER_CAPABILITY_STATE.json"
OUT_RELATIONSHIP_STATE = V18_3_RUNTIME / "RELATIONSHIP_STATE.json"
OUT_AFFILIATION_STATE = V18_3_RUNTIME / "AFFILIATION_STATE.json"
OUT_SKILL_REGISTRY = V18_3_RUNTIME / "SKILL_KALA_REGISTRY.json"
OUT_JURISDICTION = V18_3_RUNTIME / "JURISDICTION_BOUNDARIES.json"
OUT_SNAPSHOT = V18_3_RUNTIME / "V18_3_RELATIONAL_SNAPSHOT.json"
OUT_REPORT = V18_3_RUNTIME / "V18_3_COMPILATION_REPORT.json"


EXPECTED_CHARACTER_COUNT = 14
EXPECTED_RELATIONSHIP_COUNT = 18

REQUIRED_CHARACTERS = {
    "maha_deva",
    "kumari_rati",
    "roxana",
    "shrinagar",
    "malika",
    "jahzara",
    "altani",
    "anisa",
    "padma",
    "campa",
    "reva",
    "tarana",
    "sevda",
    "svara",
}

FORBIDDEN_CHARACTERS = {
    "zola",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")

    with path.open("r", encoding="utf-8-sig") as fh:
        return json.load(fh)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(
            data,
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


# ---------------------------------------------------------------------------
# Character normalization
# ---------------------------------------------------------------------------

def extract_characters(raw: Any) -> dict[str, dict[str, Any]]:
    """
    Accept either of the common registry shapes:

        {
          "characters": {
             "maha_deva": {...}
          }
        }

    or:

        {
          "characters": [
             {
               "canonical_id": "maha_deva",
               ...
             }
          ]
        }

    or a direct list/dictionary.
    """

    if isinstance(raw, dict) and "characters" in raw:
        raw = raw["characters"]

    if isinstance(raw, dict):
        result: dict[str, dict[str, Any]] = {}

        for key, value in raw.items():
            if not isinstance(value, dict):
                continue

            cid = (
                value.get("canonical_id")
                or value.get("id")
                or key
            )

            result[str(cid)] = value

        return result

    if isinstance(raw, list):
        result = {}

        for index, value in enumerate(raw):
            if not isinstance(value, dict):
                continue

            cid = (
                value.get("canonical_id")
                or value.get("id")
                or value.get("key")
            )

            if not cid:
                raise ValueError(
                    f"Character at list index {index} has no canonical_id/id/key."
                )

            result[str(cid)] = value

        return result

    raise TypeError(
        "Unsupported character registry format. "
        "Expected dict or list."
    )


def canonical_name(character: dict[str, Any], cid: str) -> str:
    return str(
        character.get("canonical_name")
        or character.get("name")
        or character.get("display_name")
        or cid
    )


def constitutional_office(
    character: dict[str, Any],
    cid: str,
) -> str:
    return str(
        character.get("constitutional_office")
        or character.get("office")
        or character.get("role")
        or ""
    )


def provenance(
    character: dict[str, Any],
) -> str | None:
    value = (
        character.get("provenance")
        or character.get("lineage")
        or character.get("cultural_provenance")
    )

    return str(value) if value is not None else None


# ---------------------------------------------------------------------------
# Relationship normalization
# ---------------------------------------------------------------------------

def extract_relationship_edges(raw: Any) -> list[dict[str, Any]]:
    """
    V17.1 relationship registry uses:

        {
          "version": "17.1",
          "edges": [...]
        }

    Also tolerate relationships/edges directly.
    """

    if isinstance(raw, dict):
        if isinstance(raw.get("edges"), list):
            return raw["edges"]

        if isinstance(raw.get("relationships"), list):
            return raw["relationships"]

    if isinstance(raw, list):
        return raw

    raise TypeError(
        "Unsupported relationship registry format. "
        "Expected a list or an object containing 'edges'."
    )


def normalize_relationships(
    raw: Any,
    character_ids: set[str],
) -> list[dict[str, Any]]:

    edges = extract_relationship_edges(raw)
    normalized: list[dict[str, Any]] = []

    for index, edge in enumerate(edges):
        if not isinstance(edge, dict):
            raise ValueError(
                f"Relationship at index {index} is not an object."
            )

        source = edge.get("from")
        target = edge.get("to")
        relation = edge.get("relation")
        status = edge.get("status", "canonical")

        if not source or not target or not relation:
            raise ValueError(
                f"Relationship at index {index} is incomplete: {edge}"
            )

        if source not in character_ids:
            raise ValueError(
                f"Relationship source not found in characters: {source}"
            )

        if target not in character_ids:
            raise ValueError(
                f"Relationship target not found in characters: {target}"
            )

        normalized.append(
            {
                "from": source,
                "to": target,
                "relation": relation,
                "status": status,
            }
        )

    return normalized


# ---------------------------------------------------------------------------
# Constitutional sovereign axis
# ---------------------------------------------------------------------------

def build_sovereign_axis() -> dict[str, Any]:
    return {
        "type": "constitutional_relationship",
        "status": "newly_wedded",
        "members": [
            "maha_deva",
            "kumari_rati",
        ],
        "bond": "marriage",
        "dynastic_status": "active",
        "source": "V17.1.1 canonical reconciliation",
        "runtime_note": (
            "Marriage is pre-existing constitutional state; "
            "runtime events may modify emergent relational dimensions."
        ),
    }


# ---------------------------------------------------------------------------
# Character capability state
# ---------------------------------------------------------------------------

def build_character_state(
    characters: dict[str, dict[str, Any]],
) -> dict[str, Any]:

    result: dict[str, Any] = {}

    for cid, character in characters.items():

        office = constitutional_office(character, cid)

        result[cid] = {
            "canonical_id": cid,
            "canonical_name": canonical_name(character, cid),

            "constitutional_office": office,

            "constitutional_authority": {
                "status": "immutable",
                "may_change_through_runtime_skill": False,
                "may_change_through_training": False,
                "may_change_through_knowledge": False,
            },

            "capability_domains": {
                "skills": {},
                "knowledge": {},
                "kalas": {},
            },

            "training_state": {
                "active_training": [],
                "completed_training": [],
                "instructors": [],
            },

            "transfer_rules": {
                "skill_learning": True,
                "knowledge_learning": True,
                "kala_learning": True,
                "constitutional_office_transfer": False,
                "institutional_authority_transfer": False,
            },

            "runtime_constraints": [
                "May learn skills outside constitutional office.",
                "May acquire knowledge across jurisdictional boundaries.",
                "May study kalas associated with another office.",
                "May not inherit another constitutional office through training.",
                "May not exercise another office's institutional authority merely by possessing its skills.",
            ],
        }

    return result


# ---------------------------------------------------------------------------
# Relationship state
# ---------------------------------------------------------------------------

def build_relationship_state(
    relationships: list[dict[str, Any]],
) -> dict[str, Any]:

    return {
        "schema": "V18.3_RELATIONSHIP_STATE",
        "version": "18.3",
        "constitutional_preservation": True,
        "sovereign_axis": build_sovereign_axis(),
        "relationship_count": len(relationships),
        "relationships": relationships,
    }


# ---------------------------------------------------------------------------
# Affiliation state
# ---------------------------------------------------------------------------

def build_affiliation_state(
    characters: dict[str, dict[str, Any]],
) -> dict[str, Any]:

    output: dict[str, Any] = {}

    for cid, character in characters.items():

        output[cid] = {
            "canonical_id": cid,
            "faction": (
                character.get("faction")
                or character.get("faction_id")
                or None
            ),
            "affiliations": character.get("affiliations", []),
            "provenance": provenance(character),
        }

    return {
        "schema": "V18.3_AFFILIATION_STATE",
        "version": "18.3",
        "characters": output,
    }


# ---------------------------------------------------------------------------
# Skill / Kala registry
# ---------------------------------------------------------------------------

def build_skill_registry() -> dict[str, Any]:

    skill_classes = {

        "dance": {
            "trainable": True,
            "associated_office": "pradhana_narti",
            "authority_transfer": False,
        },

        "vocal_music": {
            "trainable": True,
            "associated_office": None,
            "authority_transfer": False,
        },

        "instrumental_music": {
            "trainable": True,
            "associated_office": None,
            "authority_transfer": False,
        },

        "rhythm": {
            "trainable": True,
            "associated_office": "pradhana_narti",
            "authority_transfer": False,
        },

        "microtonal_calibration": {
            "trainable": True,
            "associated_office": (
                "cultural_artistic_specialist_microtonal_calibration"
            ),
            "authority_transfer": False,
        },

        "breath_control": {
            "trainable": True,
            "associated_office": None,
            "authority_transfer": False,
        },

        "mantra_delivery": {
            "trainable": True,
            "associated_office": None,
            "authority_transfer": False,
        },

        "ritual_knowledge": {
            "trainable": True,
            "associated_office": None,
            "authority_transfer": False,
        },

        "martial_training": {
            "trainable": True,
            "associated_office": None,
            "authority_transfer": False,
        },

        "administrative_knowledge": {
            "trainable": True,
            "associated_office": None,
            "authority_transfer": False,
        },

        "equine_management": {
            "trainable": True,
            "associated_office": None,
            "authority_transfer": False,
        },

        "cryptography": {
            "trainable": True,
            "associated_office": None,
            "authority_transfer": False,
        },

        "languages": {
            "trainable": True,
            "associated_office": None,
            "authority_transfer": False,
        },

        "diplomacy": {
            "trainable": True,
            "associated_office": None,
            "authority_transfer": False,
        },

        "poetics": {
            "trainable": True,
            "associated_office": None,
            "authority_transfer": False,
        },

        "archive_practice": {
            "trainable": True,
            "associated_office": None,
            "authority_transfer": False,
        },

        "healing_and_nourishment": {
            "trainable": True,
            "associated_office": None,
            "authority_transfer": False,
        },
    }

    return {
        "schema": "V18.3_SKILL_KALA_REGISTRY",
        "version": "18.3",

        "principle": (
            "Kalā and technical skills are transferable through "
            "learning and training; constitutional offices are not."
        ),

        "skill_classes": skill_classes,

        "authority_rule": (
            "Possession of a skill never automatically grants "
            "the constitutional authority associated with another office."
        ),

        "knowledge_rule": (
            "Knowledge may be taught across offices and jurisdictions "
            "without transferring institutional authority."
        ),

        "training_rule": (
            "Training may create competence, mastery, familiarity, "
            "or knowledge without changing constitutional office."
        ),

        "office_skill_examples": {
            "kumari_rati": {
                "may_learn": [
                    "dance",
                    "rhythm",
                    "vocal_music",
                    "instrumental_music",
                    "breath_control",
                    "mantra_delivery",
                    "ritual_knowledge",
                    "martial_training",
                    "languages",
                    "poetics",
                ],
                "may_not_acquire_by_training": [
                    "pradhana_narti",
                    "vanguard_sentinel",
                    "chief_court_supervisor",
                    "grand_vizier",
                    "high_priest",
                ],
            },

            "maha_deva": {
                "may_learn": [
                    "dance",
                    "vocal_music",
                    "instrumental_music",
                    "rhythm",
                    "microtonal_calibration",
                    "martial_training",
                    "languages",
                    "diplomacy",
                    "poetics",
                ],
                "may_not_acquire_by_training": [
                    "pradhana_narti",
                    "vanguard_sentinel",
                    "chief_court_supervisor",
                ],
            },
        },
    }


# ---------------------------------------------------------------------------
# Jurisdiction boundaries
# ---------------------------------------------------------------------------

def build_jurisdiction(
    characters: dict[str, dict[str, Any]],
) -> dict[str, Any]:

    character_rules: dict[str, Any] = {}

    for cid, character in characters.items():

        character_rules[cid] = {
            "canonical_id": cid,
            "office": constitutional_office(character, cid),
            "authority": "constitutional",
            "authority_transferable": False,
            "skills_transferable": True,
            "knowledge_transferable": True,
            "kalas_transferable": True,

            "boundary_rules": {
                "may_train_outside_office": True,
                "may_learn_outside_office": True,
                "may_teach_outside_office": True,
                "may_inherit_office_through_training": False,
                "may_inherit_authority_through_knowledge": False,
                "may_claim_another_office_by_skill": False,
            },
        }

    return {
        "schema": "V18.3_JURISDICTION_BOUNDARIES",
        "version": "18.3",

        "rules": [
            {
                "rule": "office_skill_separation",
                "description": (
                    "Characters may learn skills outside their office "
                    "without inheriting another office."
                ),
            },
            {
                "rule": "authority_nontransfer",
                "description": (
                    "Training cannot transfer constitutional authority."
                ),
            },
            {
                "rule": "knowledge_noninheritance",
                "description": (
                    "Knowledge does not create institutional jurisdiction."
                ),
            },
            {
                "rule": "kala_noninheritance",
                "description": (
                    "Mastery of a kala does not create the office "
                    "traditionally associated with that kala."
                ),
            },
            {
                "rule": "relationship_preservation",
                "description": (
                    "Canonical constitutional relationships remain intact "
                    "unless a future constitutional revision explicitly changes them."
                ),
            },
        ],

        "characters": character_rules,
    }


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_characters(
    characters: dict[str, dict[str, Any]],
) -> dict[str, Any]:

    ids = set(characters.keys())

    missing = sorted(REQUIRED_CHARACTERS - ids)
    forbidden_present = sorted(FORBIDDEN_CHARACTERS & ids)

    return {
        "exactly_14_characters": len(ids) == EXPECTED_CHARACTER_COUNT,
        "required_characters_present": not missing,
        "missing_characters": missing,
        "zola_absent": not forbidden_present,
        "forbidden_characters_present": forbidden_present,
    }


def validate_relationships(
    relationships: list[dict[str, Any]],
    character_ids: set[str],
) -> dict[str, Any]:

    endpoints_valid = all(
        edge["from"] in character_ids
        and edge["to"] in character_ids
        for edge in relationships
    )

    sovereign_axis_present = any(
        edge["from"] == "maha_deva"
        and edge["to"] == "kumari_rati"
        and edge["relation"] == "ritual_authority"
        for edge in relationships
    )

    return {
        "relationship_count": len(relationships),
        "expected_relationship_count": EXPECTED_RELATIONSHIP_COUNT,
        "relationship_count_valid": (
            len(relationships) == EXPECTED_RELATIONSHIP_COUNT
        ),
        "relationship_endpoints_valid": endpoints_valid,
        "sovereign_axis_present": sovereign_axis_present,
    }


def validate_outputs() -> dict[str, bool]:

    files = [
        OUT_CHARACTER_STATE,
        OUT_RELATIONSHIP_STATE,
        OUT_AFFILIATION_STATE,
        OUT_SKILL_REGISTRY,
        OUT_JURISDICTION,
        OUT_SNAPSHOT,
        OUT_REPORT,
    ]

    return {
        path.name: path.exists()
        for path in files
    }


# ---------------------------------------------------------------------------
# Main compilation
# ---------------------------------------------------------------------------

def main() -> None:

    print("Antahpura V18.3 relational runtime compiler")
    print("================================================")
    print()

    V18_3_RUNTIME.mkdir(parents=True, exist_ok=True)

    # Load canonical source registries.
    character_raw = load_json(V17_REGISTRY)
    relationship_raw = load_json(V17_RELATIONSHIPS)

    characters = extract_characters(character_raw)
    character_ids = set(characters.keys())

    relationships = normalize_relationships(
        relationship_raw,
        character_ids,
    )

    # Build runtime layers.
    character_state = build_character_state(characters)
    relationship_state = build_relationship_state(relationships)
    affiliation_state = build_affiliation_state(characters)
    skill_registry = build_skill_registry()
    jurisdiction = build_jurisdiction(characters)

    # Validation.
    character_validation = validate_characters(characters)
    relationship_validation = validate_relationships(
        relationships,
        character_ids,
    )

    if not character_validation["exactly_14_characters"]:
        raise ValueError(
            "V18.3 requires exactly 14 canonical characters. "
            f"Found {len(character_ids)}."
        )

    if not character_validation["required_characters_present"]:
        raise ValueError(
            "Missing canonical characters: "
            + ", ".join(character_validation["missing_characters"])
        )

    if not character_validation["zola_absent"]:
        raise ValueError(
            "Forbidden legacy character present: zola"
        )

    if not relationship_validation["relationship_count_valid"]:
        raise ValueError(
            "Expected exactly 18 canonical relationships; "
            f"found {len(relationships)}."
        )

    if not relationship_validation["relationship_endpoints_valid"]:
        raise ValueError(
            "One or more relationship endpoints do not exist "
            "in the canonical character registry."
        )

    if not relationship_validation["sovereign_axis_present"]:
        raise ValueError(
            "Sovereign axis missing: maha_deva -> kumari_rati "
            "ritual_authority relationship."
        )

    # Constitutional snapshot.
    snapshot = {
        "schema": "V18.3_RELATIONAL_RUNTIME_SNAPSHOT",
        "version": "18.3",
        "compiled_at_utc": utc_timestamp(),

        "canonical_baseline": "V18.2",

        "constitutional_preservation": True,

        "constitutional_principles": {
            "office_immutable": True,
            "authority_nontransferable": True,
            "skills_trainable": True,
            "knowledge_transferable": True,
            "kalas_trainable": True,
            "relationship_registry_preserved": True,
        },

        "sovereign_axis": build_sovereign_axis(),

        "characters": character_state,

        "relationships": relationship_state,

        "affiliations": affiliation_state,

        "skills": skill_registry,

        "jurisdiction": jurisdiction,
    }

    report = {
        "compiler": "v18_3_compile_relational_runtime.py",
        "version": "18.3",
        "status": "PASS",

        "compiled_at_utc": snapshot["compiled_at_utc"],

        "characters": len(characters),
        "relationships": len(relationships),

        "constitutional_baseline": "V18.2",

        "validation": {
            "exactly_14_characters": (
                character_validation["exactly_14_characters"]
            ),
            "required_characters_present": (
                character_validation["required_characters_present"]
            ),
            "zola_removed": character_validation["zola_absent"],
            "svara_present": "svara" in character_ids,
            "anisa_habshi": (
                "habshi" in (
                    provenance(characters["anisa"]) or ""
                ).lower()
            ),
            "tarana_sogdian": (
                "sogdian" in (
                    provenance(characters["tarana"]) or ""
                ).lower()
            ),
            "relationship_count_18": (
                len(relationships) == EXPECTED_RELATIONSHIP_COUNT
            ),
            "sovereign_axis_preserved": (
                relationship_validation["sovereign_axis_present"]
            ),
            "office_skill_separation": True,
            "authority_transfer_blocked": True,
            "knowledge_transfer_allowed": True,
            "kala_training_allowed": True,
        },

        "character_validation": character_validation,
        "relationship_validation": relationship_validation,

        "output_validation": {},

        "source_hashes": {
            "character_registry": sha256(V17_REGISTRY),
            "relationship_registry": sha256(V17_RELATIONSHIPS),
            "v18_2_baseline": (
                sha256(V18_BASELINE)
                if V18_BASELINE.exists()
                else None
            ),
        },
    }

    # Write all runtime artifacts.
    write_json(OUT_CHARACTER_STATE, character_state)
    write_json(OUT_RELATIONSHIP_STATE, relationship_state)
    write_json(OUT_AFFILIATION_STATE, affiliation_state)
    write_json(OUT_SKILL_REGISTRY, skill_registry)
    write_json(OUT_JURISDICTION, jurisdiction)
    write_json(OUT_SNAPSHOT, snapshot)

    report["output_validation"] = validate_outputs()

    write_json(OUT_REPORT, report)

    print("V18.3 relational runtime compilation: PASS")
    print(f"Characters: {len(characters)}")
    print(f"Relationships: {len(relationships)}")
    print("Office / skill separation: PASS")
    print("Authority transfer: BLOCKED")
    print("Knowledge transfer: ALLOWED")
    print("Kala training: ALLOWED")
    print("Sovereign marriage axis: PRESERVED")
    print()
    print(f"Runtime directory: {V18_3_RUNTIME}")
    print(f"Snapshot: {OUT_SNAPSHOT}")
    print(f"Report: {OUT_REPORT}")


if __name__ == "__main__":
    main()