#!/usr/bin/env python3
"""
Antahpura V18.2 Constitutional State Compiler

Source of truth:
    V17.1.1 canonical registries.

Purpose:
    Compile canonical character, relationship, jurisdiction,
    affiliation, and phase information into a V18 runtime state.

IMPORTANT:
    This compiler does not invent unsupported relationships,
    personalities, ethnicities, offices, or runtime values.

    Unknown information remains explicitly marked as UNKNOWN.

Canonical constraints:
    - Exactly 14 current constitutional seats.
    - Zola is removed.
    - Svara replaces Zola.
    - Anisa is Abyssinian / Habshi / East African.
    - Tarana is Sogdian / Samarkand / Silk Road.
    - No separate Abyssinian logistics/stables seat.
"""

from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "registry"
OUT = REGISTRY / "V18_RUNTIME"

CHARACTER_FILE = REGISTRY / "V17_1_CHARACTER_REGISTRY.json"
RELATIONSHIP_FILE = REGISTRY / "V17_1_RELATIONSHIP_REGISTRY.json"
PHASE_FILE = REGISTRY / "V17_1_PHASE_REGISTRY.json"
ACOUSTIC_FILE = REGISTRY / "V17_1_ACOUSTIC_JURISDICTION.json"
MIGRATION_FILE = REGISTRY / "V17_1_MIGRATION_REGISTRY.json"


EXPECTED_SEATS = {
    "maha_deva",
    "kumari_rati",
    "roxana",
    "shrinagar",
    "malika",
    "altani",
    "jahzara",
    "anisa",
    "padma",
    "campa",
    "tarana",
    "reva",
    "svara",
    "sevda",
}

FORBIDDEN_RUNTIME_IDS = {
    "zola",
}

CANONICAL_CORRECTIONS = {
    "anisa": {
        "ethnicity_provenance": "Abyssinian / Habshi / East African",
        "canonical_status": "corrected",
    },
    "tarana": {
        "ethnicity_provenance": "Sogdian / Samarkand / Silk Road",
        "canonical_status": "corrected",
    },
    "svara": {
        "canonical_status": "locked_replacement_for_zola",
        "ethnicity_provenance": "UNVERIFIED",
    },
}


def load_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"Missing required registry: {path}")

    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extract_character_list(registry: Any) -> list[dict[str, Any]]:
    """
    Supports the current V17 registry shape without assuming
    every field has the same structure.
    """

    if isinstance(registry, dict):

        if isinstance(registry.get("characters"), list):
            return registry["characters"]

        if isinstance(registry.get("characters"), dict):
            result = []

            for key, value in registry["characters"].items():
                if isinstance(value, dict):
                    item = copy.deepcopy(value)
                    item.setdefault("id", key)
                    result.append(item)

            return result

    raise ValueError(
        "Unable to locate 'characters' collection in V17 character registry."
    )


def normalize_character(character: dict[str, Any]) -> dict[str, Any]:

    cid = character.get("id")

    if not cid:
        raise ValueError(
            f"Character registry entry has no canonical id: {character}"
        )

    result = {
        "id": cid,
        "display_name": character.get(
            "display_name",
            character.get("canonical_name", cid),
        ),
        "canonical_name": character.get(
            "canonical_name",
            character.get("display_name", cid),
        ),
        "status": character.get(
            "status",
            character.get("canonical_status", "CANONICAL_V17.1.1"),
        ),
        "office": character.get("office", "UNKNOWN"),
        "court_tier": character.get("court_tier", "UNKNOWN"),
        "ethnicity_provenance": character.get(
            "ethnicity_provenance",
            "UNKNOWN",
        ),
        "faction": character.get("faction", "UNKNOWN"),
        "jurisdiction": character.get(
            "jurisdiction",
            character.get("function", "UNKNOWN"),
        ),
        "aliases": character.get("aliases", []),
        "phase_presence": character.get("phase_presence", "UNKNOWN"),
        "source_fields": character,
    }

    if cid in CANONICAL_CORRECTIONS:
        result.update(CANONICAL_CORRECTIONS[cid])

    return result


def compile_characters(registry: Any) -> dict[str, dict[str, Any]]:

    characters = extract_character_list(registry)

    compiled = {}

    for character in characters:
        normalized = normalize_character(character)
        cid = normalized["id"]

        if cid in FORBIDDEN_RUNTIME_IDS:
            continue

        compiled[cid] = normalized

    ids = set(compiled)

    missing = EXPECTED_SEATS - ids
    unexpected = ids - EXPECTED_SEATS

    if missing:
        raise ValueError(
            "Canonical V17.1.1 seats missing from registry: "
            + ", ".join(sorted(missing))
        )

    if unexpected:
        raise ValueError(
            "Unexpected current-runtime character IDs detected: "
            + ", ".join(sorted(unexpected))
        )

    if len(compiled) != 14:
        raise ValueError(
            f"Expected exactly 14 current seats; found {len(compiled)}."
        )

    return compiled


def compile_relationships(registry: Any) -> dict[str, Any]:

    if isinstance(registry, dict):
        relationships = registry.get(
            "relationships",
            registry.get("edges", []),
        )

    elif isinstance(registry, list):
        relationships = registry

    else:
        relationships = []

    result = []

    for relation in relationships:

        if not isinstance(relation, dict):
            continue

        source = relation.get(
            "from",
            relation.get("source"),
        )

        target = relation.get(
            "to",
            relation.get("target"),
        )

        if source in FORBIDDEN_RUNTIME_IDS:
            continue

        if target in FORBIDDEN_RUNTIME_IDS:
            continue

        result.append(copy.deepcopy(relation))

    return {
        "status": "compiled_from_v17_registry",
        "relationships": result,
        "count": len(result),
    }


def compile_jurisdiction(registry: Any) -> dict[str, Any]:

    if isinstance(registry, dict):
        entries = registry.get(
            "jurisdictions",
            registry.get("entries", registry),
        )
    else:
        entries = registry

    return {
        "status": "compiled_from_v17_acoustic_registry",
        "entries": entries,
    }


def compile_affiliations(characters: dict[str, dict[str, Any]]) -> dict[str, Any]:

    factions: dict[str, list[str]] = {}

    for cid, character in characters.items():

        faction = character.get("faction", "UNKNOWN")

        factions.setdefault(faction, [])

        if cid not in factions[faction]:
            factions[faction].append(cid)

    return {
        "status": "derived_only_from_canonical_character_registry",
        "factions": factions,
    }


def compile_phases(registry: Any) -> dict[str, Any]:

    if isinstance(registry, dict):

        participants = registry.get("participants", {})

        return {
            "status": "compiled_from_v17_phase_registry",
            "participants": participants,
            "source": registry,
        }

    return {
        "status": "compiled_from_v17_phase_registry",
        "participants": {},
        "source": registry,
    }


def compile_sovereign_axis(
    characters: dict[str, dict[str, Any]],
    relationships: dict[str, Any],
) -> dict[str, Any]:

    required = {
        "maha_deva",
        "kumari_rati",
    }

    if not required.issubset(characters):
        raise ValueError(
            "Sovereign Axis characters are missing."
        )

    """
    Marriage is treated as constitutional state, not an emergent event.

    These values are structural labels only. The compiler does not invent
    psychological values that are not explicitly supplied by the registry.
    """

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


def build_snapshot(
    characters,
    relationships,
    jurisdictions,
    affiliations,
    phases,
    sovereign_axis,
):

    return {
        "runtime_version": "18.2",
        "compiled_at": datetime.now(timezone.utc).isoformat(),
        "canonical_source": "V17.1.1",
        "constitutional_invariants": {
            "seat_count": 14,
            "zola_present": False,
            "svara_present": True,
            "anisa_provenance": (
                "Abyssinian / Habshi / East African"
            ),
            "tarana_provenance": (
                "Sogdian / Samarkand / Silk Road"
            ),
            "separate_abyssinian_logistics_seat": False,
        },
        "characters": characters,
        "constitutional_relationships": relationships,
        "jurisdictions": jurisdictions,
        "affiliations": affiliations,
        "phases": phases,
        "sovereign_axis": sovereign_axis,
    }


def main():

    OUT.mkdir(parents=True, exist_ok=True)

    character_registry = load_json(CHARACTER_FILE)
    relationship_registry = load_json(RELATIONSHIP_FILE)
    phase_registry = load_json(PHASE_FILE)
    acoustic_registry = load_json(ACOUSTIC_FILE)
    migration_registry = load_json(MIGRATION_FILE)

    characters = compile_characters(character_registry)

    relationships = compile_relationships(
        relationship_registry
    )

    jurisdictions = compile_jurisdiction(
        acoustic_registry
    )

    affiliations = compile_affiliations(
        characters
    )

    phases = compile_phases(
        phase_registry
    )

    sovereign_axis = compile_sovereign_axis(
        characters,
        relationships,
    )

    snapshot = build_snapshot(
        characters,
        relationships,
        jurisdictions,
        affiliations,
        phases,
        sovereign_axis,
    )

    write_json(
        OUT / "CHARACTER_STATE.json",
        characters,
    )

    write_json(
        OUT / "CONSTITUTIONAL_RELATIONSHIPS.json",
        {
            "sovereign_axis": sovereign_axis,
            **relationships,
        },
    )

    write_json(
        OUT / "JURISDICTION_GRAPH.json",
        jurisdictions,
    )

    write_json(
        OUT / "AFFILIATION_GRAPH.json",
        affiliations,
    )

    write_json(
        OUT / "PHASE_STATE.json",
        phases,
    )

    write_json(
        OUT / "V18_CANONICAL_SNAPSHOT.json",
        snapshot,
    )

    report = {
        "compiler": "v18_compile_constitutional_state.py",
        "version": "18.2",
        "status": "PASS",
        "characters": len(characters),
        "relationships": relationships["count"],
        "zola_removed": "zola" not in characters,
        "svara_present": "svara" in characters,
        "anisa_habshi": (
            "habshi"
            in characters["anisa"]["ethnicity_provenance"].lower()
        ),
        "tarana_sogdian": (
            "sogdian"
            in characters["tarana"]["ethnicity_provenance"].lower()
        ),
        "separate_abyssinian_logistics_seat": False,
        "source_hashes": {
            "character_registry": sha256_file(
                CHARACTER_FILE
            ),
            "relationship_registry": sha256_file(
                RELATIONSHIP_FILE
            ),
            "phase_registry": sha256_file(
                PHASE_FILE
            ),
            "acoustic_registry": sha256_file(
                ACOUSTIC_FILE
            ),
            "migration_registry": sha256_file(
                MIGRATION_FILE
            ),
        },
    }

    write_json(
        OUT / "V18_COMPILATION_REPORT.json",
        report,
    )

    print(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2,
        )
    )

    print()
    print(
        "V18.2 constitutional state compilation: PASS"
    )


if __name__ == "__main__":
    main()