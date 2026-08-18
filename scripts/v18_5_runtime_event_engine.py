#!/usr/bin/env python3
"""
Antahpura V18.5 — Runtime Event & State Mutation Engine

V18.5 sits above the V18.4 canonical-integrity layer.

Design contract
---------------
1. V18.4 canonical state is the immutable constitutional baseline.
2. Runtime changes happen only through validated events.
3. Every accepted event is appended to an event log.
4. Mutations are transactional: a rejected event changes nothing.
5. Canonical identity, office, authority, provenance, canonical
   relationships, and the sovereign marriage axis cannot be changed.
6. Skills, knowledge, kalas, training, statuses, flags, and emergent
   relationship dimensions are runtime state.
7. Skill possession never grants another constitutional office.
8. Knowledge never grants institutional authority.
9. Training never transfers office or authority.

The module is dependency-free and uses only the Python standard library.

Default repository layout
-------------------------
registry/
    V18_4_RUNTIME/
        V18_4_RELATIONAL_SNAPSHOT.json
    V18_5_RUNTIME/
        V18_5_RUNTIME_STATE.json
        V18_5_EVENT_LOG.json
        V18_5_RUNTIME_REPORT.json

The compiler can also consume V18.3 directly as a compatibility fallback,
but V18.4 is the preferred and protected source.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VERSION = "18.5"
SCHEMA = "V18.5_RUNTIME_EVENT_STATE"
DEFAULT_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_CANONICAL = (
    DEFAULT_ROOT
    / "registry"
    / "V18_4_RUNTIME"
    / "V18_4_RELATIONAL_SNAPSHOT.json"
)
DEFAULT_V18_3 = (
    DEFAULT_ROOT
    / "registry"
    / "V18_3_RUNTIME"
    / "V18_3_RELATIONAL_SNAPSHOT.json"
)
DEFAULT_OUTPUT = DEFAULT_ROOT / "registry" / "V18_5_RUNTIME"

IMMUTABLE_CHARACTER_FIELDS = (
    "canonical_id",
    "canonical_name",
    "constitutional_office",
    "constitutional_authority",
)

IMMUTABLE_AFFILIATION_FIELDS = (
    "canonical_id",
    "faction",
    "affiliations",
    "provenance",
)

ALLOWED_EVENT_TYPES = {
    "training_started",
    "training_progressed",
    "training_completed",
    "knowledge_acquired",
    "kala_training",
    "relationship_update",
    "status_set",
    "status_clear",
    "flag_set",
    "flag_clear",
}

FORBIDDEN_EVENT_TYPES = {
    "office_changed",
    "authority_changed",
    "constitutional_office_changed",
    "constitutional_authority_changed",
    "provenance_changed",
    "canonical_relationship_removed",
    "canonical_relationship_changed",
    "sovereign_axis_changed",
    "character_removed",
    "character_added_as_canonical",
    "canonical_mutation",
}

RELATIONSHIP_DIMENSIONS = {
    "trust",
    "familiarity",
    "tension",
    "affection",
    "respect",
    "fear",
    "loyalty",
    "intimacy",
}

SKILL_PROGRESSION = {
    "novice": 0,
    "familiar": 25,
    "competent": 50,
    "skilled": 75,
    "mastered": 100,
}


class RuntimeMutationFailure(Exception):
    """Raised when a runtime event violates V18.5 rules."""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeMutationFailure(f"Required file not found: {path}")

    try:
        with path.open("r", encoding="utf-8-sig") as fh:
            value = json.load(fh)
    except json.JSONDecodeError as exc:
        raise RuntimeMutationFailure(
            f"Invalid JSON in {path}: {exc}"
        ) from exc

    if not isinstance(value, dict):
        raise RuntimeMutationFailure(
            f"Expected JSON object at {path}, got {type(value).__name__}"
        )

    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(value, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    tmp.replace(path)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def character_map(document: dict[str, Any]) -> dict[str, dict[str, Any]]:
    value = document.get("characters", {})

    if isinstance(value, dict):
        return {
            str(k): v for k, v in value.items()
            if isinstance(v, dict)
        }

    if isinstance(value, list):
        result: dict[str, dict[str, Any]] = {}
        for item in value:
            if not isinstance(item, dict):
                continue
            cid = item.get("canonical_id") or item.get("id")
            if cid:
                result[str(cid)] = item
        return result

    return {}


def affiliation_map(document: dict[str, Any]) -> dict[str, dict[str, Any]]:
    affiliations = document.get("affiliations", {})
    if isinstance(affiliations, dict):
        chars = affiliations.get("characters", {})
        if isinstance(chars, dict):
            return {
                str(k): v for k, v in chars.items()
                if isinstance(v, dict)
            }
    return {}


def relationship_list(document: dict[str, Any]) -> list[dict[str, Any]]:
    rel = document.get("relationships", {})

    if isinstance(rel, dict):
        value = rel.get("relationships", [])
        if isinstance(value, list):
            return [x for x in value if isinstance(x, dict)]

    if isinstance(rel, list):
        return [x for x in rel if isinstance(x, dict)]

    return []


def relationship_key(edge: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(edge.get("from", "")),
        str(edge.get("to", "")),
        str(edge.get("relation", "")),
    )


def unique_relationships(
    edges: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    seen: set[tuple[str, str, str]] = set()
    result: list[dict[str, Any]] = []

    for edge in edges:
        key = relationship_key(edge)
        if key in seen:
            continue
        seen.add(key)
        result.append(copy.deepcopy(edge))

    return result


def sovereign_axis(document: dict[str, Any]) -> dict[str, Any] | None:
    axis = document.get("sovereign_axis")

    if axis is None:
        rel = document.get("relationships", {})
        if isinstance(rel, dict):
            axis = rel.get("sovereign_axis")

    if isinstance(axis, dict):
        return copy.deepcopy(axis)

    return None


def canonical_signature(
    document: dict[str, Any],
) -> dict[str, Any]:
    chars = character_map(document)
    affiliations = affiliation_map(document)

    character_state = {}
    for cid in sorted(chars):
        item = chars[cid]
        character_state[cid] = {
            field: copy.deepcopy(item.get(field))
            for field in IMMUTABLE_CHARACTER_FIELDS
        }

    affiliation_state = {}
    for cid in sorted(affiliations):
        item = affiliations[cid]
        affiliation_state[cid] = {
            field: copy.deepcopy(item.get(field))
            for field in IMMUTABLE_AFFILIATION_FIELDS
        }

    relationships = [
        relationship_key(edge)
        for edge in unique_relationships(relationship_list(document))
    ]

    return {
        "characters": character_state,
        "affiliations": affiliation_state,
        "relationships": sorted(relationships),
        "sovereign_axis": sovereign_axis(document),
    }


def assert_canonical_integrity(
    canonical: dict[str, Any],
    runtime: dict[str, Any],
) -> None:
    expected = canonical_signature(canonical)
    actual = canonical_signature(runtime)

    if expected["characters"] != actual["characters"]:
        raise RuntimeMutationFailure(
            "Canonical character identity, office, or authority was mutated."
        )

    if expected["affiliations"] != actual["affiliations"]:
        raise RuntimeMutationFailure(
            "Canonical affiliation or provenance was mutated."
        )

    if not set(expected["relationships"]).issubset(
        set(actual["relationships"])
    ):
        raise RuntimeMutationFailure(
            "A canonical relationship disappeared from runtime state."
        )

    if expected["sovereign_axis"] != actual["sovereign_axis"]:
        raise RuntimeMutationFailure(
            "The sovereign marriage axis was mutated."
        )


def skill_registry(document: dict[str, Any]) -> dict[str, dict[str, Any]]:
    skills = document.get("skills", {})
    if not isinstance(skills, dict):
        return {}

    classes = skills.get("skill_classes", {})
    if isinstance(classes, dict):
        return {
            str(k): v for k, v in classes.items()
            if isinstance(v, dict)
        }

    return {}


def initialize_runtime(
    canonical: dict[str, Any],
) -> dict[str, Any]:
    """Create a V18.5 runtime state from an already-integrity-checked source."""
    assert_canonical_integrity(canonical, canonical)

    state = copy.deepcopy(canonical)
    state["schema"] = SCHEMA
    state["version"] = VERSION
    state["initialized_at_utc"] = utc_now()
    state["canonical_source"] = "V18.4_CANONICAL_INTEGRITY_RUNTIME"
    state["canonical_locked"] = True

    state["runtime"] = {
        "event_count": 0,
        "last_event_id": None,
        "last_event_at_utc": None,
        "statuses": {},
        "flags": {},
        "emergent_relationships": {},
    }

    chars = character_map(state)
    for cid, item in chars.items():
        item.setdefault(
            "capability_domains",
            {"skills": {}, "knowledge": {}, "kalas": {}},
        )
        item.setdefault(
            "training_state",
            {
                "active_training": [],
                "completed_training": [],
                "instructors": [],
            },
        )

    state["event_log"] = []
    state["v18_5_principles"] = {
        "event_sourced": True,
        "transactional_mutations": True,
        "canonical_state_locked": True,
        "office_immutable": True,
        "authority_nontransferable": True,
        "provenance_immutable": True,
        "canonical_relationships_preserved": True,
        "sovereign_axis_immutable": True,
        "skills_trainable": True,
        "knowledge_transferable": True,
        "kalas_trainable": True,
        "skill_to_office_transfer": False,
        "knowledge_to_authority_transfer": False,
    }

    assert_canonical_integrity(canonical, state)
    return state


def _require_character(
    state: dict[str, Any],
    cid: str,
) -> dict[str, Any]:
    chars = character_map(state)
    if cid not in chars:
        raise RuntimeMutationFailure(
            f"Unknown character: {cid}"
        )
    return chars[cid]


def _require_skill(
    state: dict[str, Any],
    skill: str,
) -> None:
    registry = skill_registry(state)
    if skill not in registry:
        raise RuntimeMutationFailure(
            f"Unknown skill: {skill}"
        )


def _ensure_event_shape(event: dict[str, Any]) -> None:
    if not isinstance(event, dict):
        raise RuntimeMutationFailure("Event must be a JSON object.")

    event_id = event.get("event_id")
    event_type = event.get("event_type")
    actor = event.get("actor")

    if not isinstance(event_id, str) or not event_id.strip():
        raise RuntimeMutationFailure("Event requires a non-empty event_id.")

    if not isinstance(event_type, str) or not event_type.strip():
        raise RuntimeMutationFailure("Event requires a non-empty event_type.")

    if not isinstance(actor, str) or not actor.strip():
        raise RuntimeMutationFailure("Event requires a non-empty actor.")

    if event_type in FORBIDDEN_EVENT_TYPES:
        raise RuntimeMutationFailure(
            f"Forbidden constitutional mutation event: {event_type}"
        )

    if event_type not in ALLOWED_EVENT_TYPES:
        raise RuntimeMutationFailure(
            f"Unsupported runtime event type: {event_type}"
        )


def _existing_event_ids(state: dict[str, Any]) -> set[str]:
    return {
        str(item.get("event_id"))
        for item in state.get("event_log", [])
        if isinstance(item, dict) and item.get("event_id")
    }


def _event_payload(event: dict[str, Any]) -> dict[str, Any]:
    payload = event.get("payload", {})
    if not isinstance(payload, dict):
        raise RuntimeMutationFailure("Event payload must be a JSON object.")
    return payload


def _training_entries(character: dict[str, Any]) -> list[dict[str, Any]]:
    training = character.setdefault("training_state", {})
    active = training.setdefault("active_training", [])
    if not isinstance(active, list):
        raise RuntimeMutationFailure(
            "training_state.active_training must be a list."
        )
    return active


def _completed_training(character: dict[str, Any]) -> list[dict[str, Any]]:
    training = character.setdefault("training_state", {})
    completed = training.setdefault("completed_training", [])
    if not isinstance(completed, list):
        raise RuntimeMutationFailure(
            "training_state.completed_training must be a list."
        )
    return completed


def _skill_state(character: dict[str, Any]) -> dict[str, Any]:
    domains = character.setdefault("capability_domains", {})
    skills = domains.setdefault("skills", {})
    if not isinstance(skills, dict):
        raise RuntimeMutationFailure(
            "capability_domains.skills must be an object."
        )
    return skills


def _knowledge_state(character: dict[str, Any]) -> dict[str, Any]:
    domains = character.setdefault("capability_domains", {})
    knowledge = domains.setdefault("knowledge", {})
    if not isinstance(knowledge, dict):
        raise RuntimeMutationFailure(
            "capability_domains.knowledge must be an object."
        )
    return knowledge


def _kala_state(character: dict[str, Any]) -> dict[str, Any]:
    domains = character.setdefault("capability_domains", {})
    kalas = domains.setdefault("kalas", {})
    if not isinstance(kalas, dict):
        raise RuntimeMutationFailure(
            "capability_domains.kalas must be an object."
        )
    return kalas


def _apply_training_started(
    state: dict[str, Any],
    event: dict[str, Any],
) -> None:
    actor = event["actor"]
    payload = _event_payload(event)
    character = _require_character(state, actor)
    skill = payload.get("skill")

    if not isinstance(skill, str) or not skill:
        raise RuntimeMutationFailure(
            "training_started requires payload.skill."
        )

    _require_skill(state, skill)

    active = _training_entries(character)
    if any(
        item.get("skill") == skill
        for item in active
        if isinstance(item, dict)
    ):
        raise RuntimeMutationFailure(
            f"{actor} is already training skill: {skill}"
        )

    instructor = payload.get("instructor")
    if instructor is not None:
        if not isinstance(instructor, str):
            raise RuntimeMutationFailure(
                "training_started instructor must be a character id."
            )
        _require_character(state, instructor)

    active.append(
        {
            "skill": skill,
            "instructor": instructor,
            "progress": 0,
            "started_at_utc": event.get("occurred_at_utc") or utc_now(),
        }
    )

    if instructor:
        instructors = character.setdefault(
            "training_state", {}
        ).setdefault("instructors", [])
        if instructor not in instructors:
            instructors.append(instructor)


def _find_training(
    character: dict[str, Any],
    skill: str,
) -> dict[str, Any]:
    active = _training_entries(character)
    for item in active:
        if isinstance(item, dict) and item.get("skill") == skill:
            return item
    raise RuntimeMutationFailure(
        f"No active training found for skill: {skill}"
    )


def _apply_training_progressed(
    state: dict[str, Any],
    event: dict[str, Any],
) -> None:
    actor = event["actor"]
    payload = _event_payload(event)
    character = _require_character(state, actor)
    skill = payload.get("skill")

    if not isinstance(skill, str) or not skill:
        raise RuntimeMutationFailure(
            "training_progressed requires payload.skill."
        )

    _require_skill(state, skill)
    entry = _find_training(character, skill)

    if "delta" in payload:
        delta = payload["delta"]
        if not isinstance(delta, (int, float)) or isinstance(delta, bool):
            raise RuntimeMutationFailure(
                "training_progressed delta must be numeric."
            )
    elif "progress" in payload:
        progress = payload["progress"]
        if not isinstance(progress, (int, float)) or isinstance(progress, bool):
            raise RuntimeMutationFailure(
                "training_progressed progress must be numeric."
            )
        delta = progress - float(entry.get("progress", 0))
    else:
        raise RuntimeMutationFailure(
            "training_progressed requires delta or progress."
        )

    new_progress = float(entry.get("progress", 0)) + float(delta)
    if new_progress < 0 or new_progress > 100:
        raise RuntimeMutationFailure(
            "Training progress must remain between 0 and 100."
        )

    entry["progress"] = int(new_progress) if new_progress.is_integer() else new_progress


def _apply_training_completed(
    state: dict[str, Any],
    event: dict[str, Any],
) -> None:
    actor = event["actor"]
    payload = _event_payload(event)
    character = _require_character(state, actor)
    skill = payload.get("skill")

    if not isinstance(skill, str) or not skill:
        raise RuntimeMutationFailure(
            "training_completed requires payload.skill."
        )

    _require_skill(state, skill)
    entry = _find_training(character, skill)

    if float(entry.get("progress", 0)) < 100:
        raise RuntimeMutationFailure(
            f"Training for {skill} is not complete."
        )

    active = _training_entries(character)
    active.remove(entry)

    completed = _completed_training(character)
    completed.append(
        {
            "skill": skill,
            "instructor": entry.get("instructor"),
            "completed_at_utc": event.get("occurred_at_utc") or utc_now(),
        }
    )

    skills = _skill_state(character)
    previous = skills.get(skill, {})
    if not isinstance(previous, dict):
        previous = {}

    skills[skill] = {
        **previous,
        "learned": True,
        "proficiency": 100,
        "authority_transfer": False,
        "constitutional_office_transfer": False,
    }


def _apply_knowledge_acquired(
    state: dict[str, Any],
    event: dict[str, Any],
) -> None:
    actor = event["actor"]
    payload = _event_payload(event)
    character = _require_character(state, actor)

    key = payload.get("knowledge")
    if not isinstance(key, str) or not key:
        raise RuntimeMutationFailure(
            "knowledge_acquired requires payload.knowledge."
        )

    knowledge = _knowledge_state(character)
    value = copy.deepcopy(payload.get("value", True))
    knowledge[key] = {
        "acquired": True,
        "value": value,
        "source": payload.get("source"),
        "acquired_at_utc": event.get("occurred_at_utc") or utc_now(),
        "authority_transfer": False,
    }


def _apply_kala_training(
    state: dict[str, Any],
    event: dict[str, Any],
) -> None:
    actor = event["actor"]
    payload = _event_payload(event)
    character = _require_character(state, actor)

    kala = payload.get("kala")
    if not isinstance(kala, str) or not kala:
        raise RuntimeMutationFailure(
            "kala_training requires payload.kala."
        )

    progress = payload.get("progress", 0)
    if not isinstance(progress, (int, float)) or isinstance(progress, bool):
        raise RuntimeMutationFailure(
            "kala_training progress must be numeric."
        )
    if progress < 0 or progress > 100:
        raise RuntimeMutationFailure(
            "Kala progress must remain between 0 and 100."
        )

    kalas = _kala_state(character)
    kalas[kala] = {
        "progress": int(progress) if float(progress).is_integer() else progress,
        "trainable": True,
        "authority_transfer": False,
        "constitutional_office_transfer": False,
    }


def _edge_exists(
    state: dict[str, Any],
    from_id: str,
    to_id: str,
    relation: str,
) -> bool:
    wanted = (from_id, to_id, relation)
    return any(
        relationship_key(edge) == wanted
        for edge in relationship_list(state)
    )


def _apply_relationship_update(
    state: dict[str, Any],
    event: dict[str, Any],
) -> None:
    actor = event["actor"]
    payload = _event_payload(event)
    _require_character(state, actor)

    target = payload.get("target")
    relation = payload.get("relation")

    if not isinstance(target, str) or not target:
        raise RuntimeMutationFailure(
            "relationship_update requires payload.target."
        )
    if not isinstance(relation, str) or not relation:
        raise RuntimeMutationFailure(
            "relationship_update requires payload.relation."
        )

    _require_character(state, target)

    dimension = payload.get("dimension")
    value = payload.get("value")

    if dimension not in RELATIONSHIP_DIMENSIONS:
        raise RuntimeMutationFailure(
            "relationship_update dimension must be one of: "
            + ", ".join(sorted(RELATIONSHIP_DIMENSIONS))
        )

    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise RuntimeMutationFailure(
            "relationship_update value must be numeric."
        )

    if value < -100 or value > 100:
        raise RuntimeMutationFailure(
            "relationship dimension must remain between -100 and 100."
        )

    key = "|".join((actor, target, relation))
    emergent = state.setdefault("runtime", {}).setdefault(
        "emergent_relationships", {}
    )
    item = emergent.setdefault(
        key,
        {
            "from": actor,
            "to": target,
            "relation": relation,
            "canonical": _edge_exists(
                state, actor, target, relation
            ),
            "dimensions": {},
        },
    )

    item["dimensions"][dimension] = value


def _apply_status(
    state: dict[str, Any],
    event: dict[str, Any],
    clear: bool,
) -> None:
    actor = event["actor"]
    payload = _event_payload(event)
    _require_character(state, actor)

    status = payload.get("status")
    if not isinstance(status, str) or not status:
        raise RuntimeMutationFailure(
            "status event requires payload.status."
        )

    statuses = state.setdefault("runtime", {}).setdefault("statuses", {})
    actor_statuses = statuses.setdefault(actor, [])

    if clear:
        if status in actor_statuses:
            actor_statuses.remove(status)
    elif status not in actor_statuses:
        actor_statuses.append(status)


def _apply_flag(
    state: dict[str, Any],
    event: dict[str, Any],
    clear: bool,
) -> None:
    actor = event["actor"]
    payload = _event_payload(event)
    _require_character(state, actor)

    flag = payload.get("flag")
    if not isinstance(flag, str) or not flag:
        raise RuntimeMutationFailure(
            "flag event requires payload.flag."
        )

    flags = state.setdefault("runtime", {}).setdefault("flags", {})
    actor_flags = flags.setdefault(actor, {})

    if clear:
        actor_flags.pop(flag, None)
    else:
        actor_flags[flag] = copy.deepcopy(payload.get("value", True))


def _dispatch_event(
    state: dict[str, Any],
    event: dict[str, Any],
) -> None:
    handlers = {
        "training_started": _apply_training_started,
        "training_progressed": _apply_training_progressed,
        "training_completed": _apply_training_completed,
        "knowledge_acquired": _apply_knowledge_acquired,
        "kala_training": _apply_kala_training,
        "relationship_update": _apply_relationship_update,
        "status_set": lambda s, e: _apply_status(s, e, False),
        "status_clear": lambda s, e: _apply_status(s, e, True),
        "flag_set": lambda s, e: _apply_flag(s, e, False),
        "flag_clear": lambda s, e: _apply_flag(s, e, True),
    }

    handlers[event["event_type"]](state, event)


def apply_event(
    canonical: dict[str, Any],
    state: dict[str, Any],
    event: dict[str, Any],
) -> dict[str, Any]:
    """
    Apply one event transactionally.

    The original state is never modified. A deep copy is mutated and then
    checked against the immutable canonical signature before being returned.
    """
    _ensure_event_shape(event)

    if event["event_id"] in _existing_event_ids(state):
        raise RuntimeMutationFailure(
            f"Duplicate event_id: {event['event_id']}"
        )

    assert_canonical_integrity(canonical, state)

    candidate = copy.deepcopy(state)
    candidate.setdefault("event_log", [])

    normalized = copy.deepcopy(event)
    normalized.setdefault("occurred_at_utc", utc_now())
    normalized["sequence"] = len(candidate["event_log"]) + 1

    _dispatch_event(candidate, normalized)

    # The event log is append-only and belongs to the candidate transaction.
    candidate["event_log"].append(normalized)

    runtime_meta = candidate.setdefault("runtime", {})
    runtime_meta["event_count"] = len(candidate["event_log"])
    runtime_meta["last_event_id"] = normalized["event_id"]
    runtime_meta["last_event_at_utc"] = normalized["occurred_at_utc"]

    # Constitutional firewall.
    assert_canonical_integrity(canonical, candidate)

    candidate["schema"] = SCHEMA
    candidate["version"] = VERSION

    return candidate


def apply_events(
    canonical: dict[str, Any],
    state: dict[str, Any],
    events: list[dict[str, Any]],
) -> dict[str, Any]:
    current = state
    for event in events:
        current = apply_event(canonical, current, event)
    return current


def build_runtime_report(
    canonical: dict[str, Any],
    state: dict[str, Any],
) -> dict[str, Any]:
    chars = character_map(state)
    skills = skill_registry(state)

    learned_skills = 0
    knowledge_items = 0
    kala_items = 0
    active_training = 0
    completed_training = 0

    for character in chars.values():
        domains = character.get("capability_domains", {})
        if isinstance(domains, dict):
            value = domains.get("skills", {})
            if isinstance(value, dict):
                learned_skills += sum(
                    1
                    for item in value.values()
                    if isinstance(item, dict) and item.get("learned") is True
                )

            value = domains.get("knowledge", {})
            if isinstance(value, dict):
                knowledge_items += len(value)

            value = domains.get("kalas", {})
            if isinstance(value, dict):
                kala_items += len(value)

        training = character.get("training_state", {})
        if isinstance(training, dict):
            active = training.get("active_training", [])
            completed = training.get("completed_training", [])
            if isinstance(active, list):
                active_training += len(active)
            if isinstance(completed, list):
                completed_training += len(completed)

    return {
        "schema": "V18.5_RUNTIME_REPORT",
        "version": VERSION,
        "generated_at_utc": utc_now(),
        "status": "PASS",
        "constitutional_firewall": "ACTIVE",
        "canonical_source_version": canonical.get("version"),
        "counts": {
            "characters": len(chars),
            "registered_skill_classes": len(skills),
            "events": len(state.get("event_log", [])),
            "learned_skills": learned_skills,
            "knowledge_items": knowledge_items,
            "kala_items": kala_items,
            "active_training": active_training,
            "completed_training": completed_training,
            "emergent_relationships": len(
                state.get("runtime", {}).get(
                    "emergent_relationships", {}
                )
                if isinstance(
                    state.get("runtime", {}).get(
                        "emergent_relationships", {}
                    ),
                    dict,
                )
                else {}
            ),
        },
        "invariants": {
            "canonical_identity": "PASS",
            "constitutional_office": "PASS",
            "constitutional_authority": "PASS",
            "canonical_provenance": "PASS",
            "canonical_relationships": "PASS",
            "sovereign_marriage_axis": "PASS",
            "event_log_append_only": "PASS",
            "transactional_mutation": "PASS",
            "skill_to_office_transfer": "BLOCKED",
            "knowledge_to_authority_transfer": "BLOCKED",
        },
        "event_types": sorted(
            {
                item.get("event_type")
                for item in state.get("event_log", [])
                if isinstance(item, dict)
                and item.get("event_type")
            }
        ),
    }


def compile_v18_5(
    canonical_path: Path = DEFAULT_CANONICAL,
    output_dir: Path = DEFAULT_OUTPUT,
    events_path: Path | None = None,
    allow_v18_3_fallback: bool = True,
) -> dict[str, Path]:
    source = canonical_path

    if not source.exists() and allow_v18_3_fallback:
        source = DEFAULT_V18_3

    canonical = load_json(source)

    # A V18.3 fallback is accepted only as an input compatibility path.
    # The resulting V18.5 state still receives the same firewall.
    state = initialize_runtime(canonical)

    if events_path is not None:
        events_document = load_json(events_path)
        events = events_document.get("events", events_document)
        if not isinstance(events, list):
            raise RuntimeMutationFailure(
                "Event source must contain an 'events' array."
            )
        state = apply_events(canonical, state, events)

    report = build_runtime_report(canonical, state)

    output_dir.mkdir(parents=True, exist_ok=True)

    state_path = output_dir / "V18_5_RUNTIME_STATE.json"
    event_log_path = output_dir / "V18_5_EVENT_LOG.json"
    report_path = output_dir / "V18_5_RUNTIME_REPORT.json"

    write_json(state_path, state)
    write_json(
        event_log_path,
        {
            "schema": "V18.5_EVENT_LOG",
            "version": VERSION,
            "event_count": len(state.get("event_log", [])),
            "events": state.get("event_log", []),
        },
    )

    report["source_sha256"] = sha256_file(source)
    report["output_sha256"] = {
        "V18_5_RUNTIME_STATE.json": sha256_file(state_path),
        "V18_5_EVENT_LOG.json": sha256_file(event_log_path),
    }
    report["source_file"] = str(source)
    write_json(report_path, report)

    return {
        "output_dir": output_dir,
        "state": state_path,
        "event_log": event_log_path,
        "report": report_path,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compile and mutate Antahpura V18.5 runtime state."
    )
    parser.add_argument(
        "--canonical",
        type=Path,
        default=DEFAULT_CANONICAL,
        help="Path to V18.4 canonical-integrity runtime snapshot.",
    )
    parser.add_argument(
        "--events",
        type=Path,
        default=None,
        help="Optional JSON event stream.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="V18.5 output directory.",
    )
    parser.add_argument(
        "--no-v18-3-fallback",
        action="store_true",
        help="Do not fall back to V18.3 when V18.4 source is absent.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    print("Antahpura V18.5 Runtime Event & State Mutation Engine")

    try:
        paths = compile_v18_5(
            canonical_path=args.canonical,
            output_dir=args.output,
            events_path=args.events,
            allow_v18_3_fallback=not args.no_v18_3_fallback,
        )
    except RuntimeMutationFailure as exc:
        print("\nV18.5 runtime compilation: FAIL")
        print(str(exc))
        return 1
    except Exception as exc:
        print("\nV18.5 compiler error:")
        print(f"{type(exc).__name__}: {exc}")
        return 2

    report = load_json(paths["report"])
    counts = report["counts"]

    print("V18.5 runtime compilation: PASS")
    print(f"Characters: {counts['characters']}")
    print(f"Events: {counts['events']}")
    print(f"Registered skill classes: {counts['registered_skill_classes']}")
    print(f"Learned skills: {counts['learned_skills']}")
    print(f"Knowledge items: {counts['knowledge_items']}")
    print(f"Kala items: {counts['kala_items']}")
    print("Canonical state: LOCKED")
    print("Office mutation: BLOCKED")
    print("Authority transfer: BLOCKED")
    print("Provenance mutation: BLOCKED")
    print("Canonical relationship deletion: BLOCKED")
    print("Sovereign marriage mutation: BLOCKED")
    print("Transactional event application: ACTIVE")
    print(f"\nRuntime directory: {paths['output_dir']}")
    print(f"State: {paths['state']}")
    print(f"Event log: {paths['event_log']}")
    print(f"Report: {paths['report']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
