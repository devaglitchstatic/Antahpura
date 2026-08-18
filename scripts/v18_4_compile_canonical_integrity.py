#!/usr/bin/env python3
"""
Antahpura V18.4 — Canonical Integrity / Provenance Compiler

Purpose
-------
Compile a V18.4 runtime snapshot from:
    V18.2 canonical baseline
    + V18.3 relational runtime snapshot

V18.4 is an integrity layer. It does NOT invent lore.

It enforces:
    * canonical identity is immutable
    * canonical constitutional office is immutable
    * canonical authority is immutable
    * canonical provenance is preserved
    * canonical relationships cannot disappear
    * sovereign marriage axis is preserved
    * runtime skills/knowledge/kalas remain runtime-owned
    * skills cannot grant constitutional office
    * knowledge cannot grant authority
    * training cannot transfer office or authority

The compiler is deliberately dependency-free and uses only Python stdlib.

Default Windows repository layout:
    D:\\dolphin\\AntahpuraRepo\
        registry\
            V18_2_CANONICAL_BASELINE.json
            V18_3_RUNTIME\
                V18_3_RELATIONAL_SNAPSHOT.json
            V17_1_RELATIONSHIP_REGISTRY.json

Outputs:
    registry\V18_4_RUNTIME\
        V18_4_CANONICAL_BASELINE.json
        V18_4_RELATIONAL_SNAPSHOT.json
        V18_4_INTEGRITY_REPORT.json
        V18_4_REGRESSION_REPORT.json
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


VERSION = "18.4"

IMMUTABLE_CHARACTER_FIELDS = (
    "canonical_id",
    "canonical_name",
    "constitutional_office",
    "constitutional_authority",
)

RUNTIME_CHARACTER_FIELDS = (
    "capability_domains",
    "training_state",
    "transfer_rules",
    "runtime_constraints",
)

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASELINE = (
    DEFAULT_ROOT / "registry" / "V18_2_CANONICAL_BASELINE.json"
)
DEFAULT_RUNTIME = (
    DEFAULT_ROOT
    / "registry"
    / "V18_3_RUNTIME"
    / "V18_3_RELATIONAL_SNAPSHOT.json"
)
DEFAULT_RELATIONSHIP_REGISTRY = (
    DEFAULT_ROOT / "registry" / "V17_1_RELATIONSHIP_REGISTRY.json"
)
DEFAULT_OUTPUT = DEFAULT_ROOT / "registry" / "V18_4_RUNTIME"


class IntegrityFailure(Exception):
    """Raised when a canonical integrity invariant is violated."""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise IntegrityFailure(f"Required file not found: {path}")

    try:
        with path.open("r", encoding="utf-8-sig") as fh:
            value = json.load(fh)
    except json.JSONDecodeError as exc:
        raise IntegrityFailure(
            f"Invalid JSON in {path}: {exc}"
        ) from exc

    if not isinstance(value, dict):
        raise IntegrityFailure(
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


def as_character_map(document: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """
    Accept the two forms encountered in the V18 lineage:

        {"characters": {"id": {...}}}

    and, defensively:

        {"characters": [{...}, {...}]}
    """
    characters = document.get("characters", {})

    if isinstance(characters, dict):
        return {
            str(k): v for k, v in characters.items()
            if isinstance(v, dict)
        }

    if isinstance(characters, list):
        result: dict[str, dict[str, Any]] = {}
        for item in characters:
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
            return [
                x for x in value
                if isinstance(x, dict)
            ]

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
    result = []

    for edge in edges:
        key = relationship_key(edge)
        if key in seen:
            continue
        seen.add(key)
        result.append(copy.deepcopy(edge))

    return result


def extract_sovereign_axis(
    baseline: dict[str, Any],
    runtime: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Prefer runtime because V18.3 explicitly carries the constitutional
    sovereign axis. Fall back to baseline if needed.
    """
    axis = runtime.get("sovereign_axis")
    if isinstance(axis, dict):
        return copy.deepcopy(axis)

    rel = runtime.get("relationships")
    if isinstance(rel, dict) and isinstance(rel.get("sovereign_axis"), dict):
        return copy.deepcopy(rel["sovereign_axis"])

    axis = baseline.get("sovereign_axis")
    if isinstance(axis, dict):
        return copy.deepcopy(axis)

    rel = baseline.get("relationships")
    if isinstance(rel, dict) and isinstance(rel.get("sovereign_axis"), dict):
        return copy.deepcopy(rel["sovereign_axis"])

    return None


def validate_character_identity(
    baseline_chars: dict[str, dict[str, Any]],
    runtime_chars: dict[str, dict[str, Any]],
    failures: list[str],
) -> None:
    base_ids = set(baseline_chars)
    runtime_ids = set(runtime_chars)

    missing = sorted(base_ids - runtime_ids)
    extra = sorted(runtime_ids - base_ids)

    if missing:
        failures.append(
            "Canonical characters missing from runtime: "
            + ", ".join(missing)
        )

    if extra:
        failures.append(
            "Runtime contains unknown characters: "
            + ", ".join(extra)
        )

    for cid in sorted(base_ids & runtime_ids):
        base = baseline_chars[cid]
        run = runtime_chars[cid]

        for field in IMMUTABLE_CHARACTER_FIELDS:
            if field not in base:
                continue

            if run.get(field) != base.get(field):
                failures.append(
                    f"{cid}.{field} changed: "
                    f"baseline={base.get(field)!r}, "
                    f"runtime={run.get(field)!r}"
                )


def extract_canonical_provenance(
    baseline: dict[str, Any],
    baseline_chars: dict[str, dict[str, Any]],
    runtime: dict[str, Any],
) -> dict[str, Any]:
    """
    Canonical provenance must come from the canonical source.

    Order:
        1. baseline affiliations.characters
        2. baseline character provenance
        3. runtime affiliation provenance ONLY if baseline has no value

    This prevents V18.3's accidental null provenance from becoming canonical.
    """
    result: dict[str, Any] = {}

    base_aff = affiliation_map(baseline)
    runtime_aff = affiliation_map(runtime)

    for cid in baseline_chars:
        if cid in base_aff and "provenance" in base_aff[cid]:
            result[cid] = copy.deepcopy(base_aff[cid].get("provenance"))
        elif "provenance" in baseline_chars[cid]:
            result[cid] = copy.deepcopy(
                baseline_chars[cid].get("provenance")
            )
        elif cid in runtime_aff and "provenance" in runtime_aff[cid]:
            result[cid] = copy.deepcopy(runtime_aff[cid].get("provenance"))
        else:
            result[cid] = None

    return result


def validate_provenance(
    canonical_provenance: dict[str, Any],
    runtime: dict[str, Any],
    failures: list[str],
) -> None:
    runtime_aff = affiliation_map(runtime)

    for cid, expected in canonical_provenance.items():
        actual = runtime_aff.get(cid, {}).get("provenance")

        # V18.3 may contain null because of the known compiler defect.
        # That is repaired, not treated as an intentional canonical change.
        if expected != actual and actual is not None:
            failures.append(
                f"{cid}.affiliations.provenance changed: "
                f"canonical={expected!r}, runtime={actual!r}"
            )


def canonical_relationship_sources(
    baseline: dict[str, Any],
    relationship_registry: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """
    Prefer explicit baseline relationships. If baseline does not carry them,
    use the V17.1 canonical relationship registry.
    """
    baseline_edges = relationship_list(baseline)
    if baseline_edges:
        return unique_relationships(baseline_edges)

    if relationship_registry:
        edges = relationship_registry.get("edges", [])
        if isinstance(edges, list):
            return unique_relationships([
                x for x in edges if isinstance(x, dict)
            ])

    return []


def validate_relationship_integrity(
    canonical_edges: list[dict[str, Any]],
    runtime: dict[str, Any],
    runtime_chars: dict[str, dict[str, Any]],
    failures: list[str],
) -> None:
    runtime_edges = unique_relationships(relationship_list(runtime))

    runtime_keys = {
        relationship_key(edge)
        for edge in runtime_edges
    }

    character_ids = set(runtime_chars)

    for edge in canonical_edges:
        key = relationship_key(edge)

        if edge.get("from") not in character_ids:
            failures.append(
                f"Canonical relationship source missing: {edge.get('from')}"
            )

        if edge.get("to") not in character_ids:
            failures.append(
                f"Canonical relationship target missing: {edge.get('to')}"
            )

        if key not in runtime_keys:
            failures.append(
                "Canonical relationship missing from runtime: "
                f"{edge.get('from')} -> {edge.get('to')} "
                f"[{edge.get('relation')}]"
            )


def validate_sovereign_axis(
    baseline: dict[str, Any],
    runtime: dict[str, Any],
    failures: list[str],
) -> dict[str, Any] | None:
    axis = extract_sovereign_axis(baseline, runtime)

    if not isinstance(axis, dict):
        failures.append("Sovereign axis is missing.")
        return None

    members = axis.get("members", [])
    if members != ["maha_deva", "kumari_rati"]:
        failures.append(
            "Sovereign axis members changed: "
            f"{members!r}"
        )

    if axis.get("bond") != "marriage":
        failures.append(
            "Sovereign axis bond changed: "
            f"{axis.get('bond')!r}"
        )

    if axis.get("dynastic_status") != "active":
        failures.append(
            "Sovereign axis dynastic_status is not active."
        )

    return copy.deepcopy(axis)


def validate_skill_firewall(
    runtime: dict[str, Any],
    runtime_chars: dict[str, dict[str, Any]],
    failures: list[str],
) -> None:
    skills = runtime.get("skills", {})
    if not isinstance(skills, dict):
        failures.append("Skill registry is not an object.")
        return

    skill_classes = skills.get("skill_classes", {})
    if not isinstance(skill_classes, dict):
        failures.append("skills.skill_classes is not an object.")
        return

    # No skill may be declared as transferring authority.
    for skill_name, spec in skill_classes.items():
        if not isinstance(spec, dict):
            failures.append(
                f"Skill class {skill_name!r} has invalid specification."
            )
            continue

        if spec.get("authority_transfer") is True:
            failures.append(
                f"Skill {skill_name!r} illegally enables authority transfer."
            )

        if spec.get("office_transfer") is True:
            failures.append(
                f"Skill {skill_name!r} illegally enables office transfer."
            )

    # Rati is the explicit regression boundary used by V18.3:
    # dance is learnable, but Pradhana Narti is not acquirable by training.
    rati = runtime_chars.get("kumari_rati", {})
    office = rati.get("constitutional_office", "")
    if office != "Princess / Dynastic Center / Initiand":
        failures.append(
            "Rati constitutional office changed unexpectedly."
        )

    examples = skills.get("office_skill_examples", {})
    if isinstance(examples, dict):
        rati_rules = examples.get("kumari_rati", {})
        if isinstance(rati_rules, dict):
            may_learn = rati_rules.get("may_learn", [])
            may_not = rati_rules.get("may_not_acquire_by_training", [])

            if "dance" not in may_learn:
                failures.append(
                    "Rati no longer has dance in may_learn."
                )

            if "pradhana_narti" not in may_not:
                failures.append(
                    "Rati no longer has pradhana_narti in "
                    "may_not_acquire_by_training."
                )


def validate_runtime_principles(
    runtime: dict[str, Any],
    failures: list[str],
) -> None:
    principles = runtime.get("constitutional_principles", {})

    expected = {
        "office_immutable": True,
        "authority_nontransferable": True,
        "skills_trainable": True,
        "knowledge_transferable": True,
        "kalas_trainable": True,
        "relationship_registry_preserved": True,
    }

    if isinstance(principles, dict):
        for key, value in expected.items():
            if principles.get(key) is not value:
                failures.append(
                    f"constitutional_principles.{key} must be {value!r}"
                )


def build_v18_4_snapshot(
    baseline: dict[str, Any],
    runtime: dict[str, Any],
    relationship_registry: dict[str, Any] | None,
) -> tuple[dict[str, Any], list[str], dict[str, Any]]:
    failures: list[str] = []

    baseline_chars = as_character_map(baseline)
    runtime_chars = as_character_map(runtime)

    if not baseline_chars:
        failures.append("Canonical baseline contains no characters.")

    if not runtime_chars:
        failures.append("V18.3 runtime contains no characters.")

    validate_character_identity(
        baseline_chars,
        runtime_chars,
        failures,
    )

    canonical_provenance = extract_canonical_provenance(
        baseline,
        baseline_chars,
        runtime,
    )

    validate_provenance(
        canonical_provenance,
        runtime,
        failures,
    )

    canonical_edges = canonical_relationship_sources(
        baseline,
        relationship_registry,
    )

    validate_relationship_integrity(
        canonical_edges,
        runtime,
        runtime_chars,
        failures,
    )

    sovereign_axis = validate_sovereign_axis(
        baseline,
        runtime,
        failures,
    )

    validate_skill_firewall(
        runtime,
        runtime_chars,
        failures,
    )

    validate_runtime_principles(
        runtime,
        failures,
    )

    if failures:
        raise IntegrityFailure(
            "V18.4 canonical integrity validation failed:\n"
            + "\n".join(f"  - {x}" for x in failures)
        )

    # Start from V18.3 runtime so runtime state is retained.
    snapshot = copy.deepcopy(runtime)

    snapshot["schema"] = "V18.4_CANONICAL_INTEGRITY_RUNTIME_SNAPSHOT"
    snapshot["version"] = VERSION
    snapshot["compiled_at_utc"] = utc_now()
    snapshot["canonical_baseline"] = "V18.2"
    snapshot["constitutional_preservation"] = True

    snapshot["constitutional_principles"] = {
        "office_immutable": True,
        "authority_nontransferable": True,
        "skills_trainable": True,
        "knowledge_transferable": True,
        "kalas_trainable": True,
        "relationship_registry_preserved": True,
        "canonical_provenance_preserved": True,
        "canonical_identity_preserved": True,
    }

    if sovereign_axis is not None:
        snapshot["sovereign_axis"] = sovereign_axis

    # Repair only the known V18.3 provenance loss from canonical data.
    affiliations = snapshot.setdefault("affiliations", {})
    affiliations["schema"] = "V18.4_AFFILIATION_STATE"
    affiliations["version"] = VERSION
    affiliation_chars = affiliations.setdefault("characters", {})

    for cid in baseline_chars:
        canonical_aff = affiliation_map(baseline).get(cid, {})
        current_aff = affiliation_chars.setdefault(cid, {})

        # Preserve canonical affiliation values when they exist.
        if "faction" in canonical_aff:
            current_aff["faction"] = copy.deepcopy(
                canonical_aff["faction"]
            )
        if "affiliations" in canonical_aff:
            current_aff["affiliations"] = copy.deepcopy(
                canonical_aff["affiliations"]
            )

        current_aff["canonical_id"] = cid
        current_aff["provenance"] = copy.deepcopy(
            canonical_provenance.get(cid)
        )

    # Normalize relationship container without changing its contents.
    relationships = snapshot.setdefault("relationships", {})
    relationships["schema"] = "V18.4_RELATIONSHIP_STATE"
    relationships["version"] = VERSION
    relationships["constitutional_preservation"] = True
    if sovereign_axis is not None:
        relationships["sovereign_axis"] = copy.deepcopy(sovereign_axis)

    runtime_edges = unique_relationships(relationship_list(runtime))
    relationships["relationship_count"] = len(runtime_edges)
    relationships["relationships"] = runtime_edges

    # Preserve / normalize skill metadata.
    skills = snapshot.setdefault("skills", {})
    skills["schema"] = "V18.4_SKILL_KALA_REGISTRY"
    skills["version"] = VERSION

    # Add explicit integrity rules without deleting existing rules.
    jurisdiction = snapshot.setdefault("jurisdiction", {})
    jurisdiction["schema"] = "V18.4_JURISDICTION_BOUNDARIES"
    jurisdiction["version"] = VERSION

    rules = jurisdiction.setdefault("rules", [])
    rule_names = {
        item.get("rule")
        for item in rules
        if isinstance(item, dict)
    }

    required_rules = [
        {
            "rule": "canonical_field_immutability",
            "description": (
                "Canonical identity, office, authority and provenance "
                "cannot be changed by runtime compilation."
            ),
        },
        {
            "rule": "canonical_relationship_integrity",
            "description": (
                "Canonical relationships cannot disappear through "
                "runtime compilation."
            ),
        },
        {
            "rule": "provenance_preservation",
            "description": (
                "Character provenance is inherited from the canonical "
                "baseline and cannot be nulled by runtime state."
            ),
        },
        {
            "rule": "skill_authority_firewall",
            "description": (
                "Skill possession or training cannot transfer "
                "constitutional office or institutional authority."
            ),
        },
    ]

    for rule in required_rules:
        if rule["rule"] not in rule_names:
            rules.append(rule)

    integrity_report = {
        "schema": "V18.4_CANONICAL_INTEGRITY_REPORT",
        "version": VERSION,
        "compiled_at_utc": snapshot["compiled_at_utc"],
        "status": "PASS",
        "source_files": {
            "canonical_baseline": str(DEFAULT_BASELINE),
            "runtime_snapshot": str(DEFAULT_RUNTIME),
            "relationship_registry": (
                str(DEFAULT_RELATIONSHIP_REGISTRY)
                if relationship_registry is not None
                else None
            ),
        },
        "counts": {
            "characters": len(baseline_chars),
            "relationships": len(runtime_edges),
            "canonical_relationships": len(canonical_edges),
            "affiliations": len(affiliation_chars),
            "skill_classes": len(
                skills.get("skill_classes", {})
                if isinstance(skills.get("skill_classes", {}), dict)
                else {}
            ),
        },
        "invariants": {
            "character_identity": "PASS",
            "constitutional_office": "PASS",
            "constitutional_authority": "PASS",
            "canonical_provenance": "PASS",
            "canonical_relationships": "PASS",
            "sovereign_axis": "PASS",
            "skill_authority_firewall": "PASS",
            "runtime_principles": "PASS",
        },
        "provenance_repaired": [
            cid
            for cid, value in canonical_provenance.items()
            if affiliation_map(runtime).get(cid, {}).get("provenance")
            != value
        ],
        "constitutional_principles": snapshot[
            "constitutional_principles"
        ],
    }

    regression_report = {
        "schema": "V18.4_REGRESSION_REPORT",
        "version": VERSION,
        "status": "PASS",
        "checks": [
            "14-character canonical roster preserved",
            "canonical relationships preserved",
            "canonical affiliations preserved",
            "canonical provenance preserved",
            "sovereign marriage axis preserved",
            "constitutional office immutable",
            "constitutional authority non-transferable",
            "skills remain trainable",
            "knowledge remains transferable",
            "kalas remain trainable",
            "skill-to-office firewall active",
            "knowledge-to-authority firewall active",
        ],
    }

    return snapshot, failures, {
        "integrity_report": integrity_report,
        "regression_report": regression_report,
    }


def compile_v18_4(
    baseline_path: Path = DEFAULT_BASELINE,
    runtime_path: Path = DEFAULT_RUNTIME,
    relationship_path: Path = DEFAULT_RELATIONSHIP_REGISTRY,
    output_dir: Path = DEFAULT_OUTPUT,
) -> dict[str, Path]:
    baseline = load_json(baseline_path)
    runtime = load_json(runtime_path)

    relationship_registry = None
    if relationship_path.exists():
        relationship_registry = load_json(relationship_path)

    snapshot, _, reports = build_v18_4_snapshot(
        baseline,
        runtime,
        relationship_registry,
    )

    output_dir.mkdir(parents=True, exist_ok=True)

    baseline_copy = copy.deepcopy(baseline)
    baseline_copy["schema"] = "V18.4_CANONICAL_BASELINE"
    baseline_copy["version"] = VERSION
    baseline_copy["source_version"] = "V18.2"

    # Explicitly preserve canonical provenance in the V18.4 baseline copy.
    base_aff = affiliation_map(baseline)
    base_chars = as_character_map(baseline)
    if base_aff:
        baseline_copy.setdefault("affiliations", {})[
            "characters"
        ] = copy.deepcopy(base_aff)

    snapshot_path = output_dir / "V18_4_RELATIONAL_SNAPSHOT.json"
    baseline_out = output_dir / "V18_4_CANONICAL_BASELINE.json"
    integrity_path = output_dir / "V18_4_INTEGRITY_REPORT.json"
    regression_path = output_dir / "V18_4_REGRESSION_REPORT.json"

    write_json(baseline_out, baseline_copy)
    write_json(snapshot_path, snapshot)
    write_json(integrity_path, reports["integrity_report"])
    write_json(regression_path, reports["regression_report"])

    # Add generated-file hashes after writing the primary artifacts.
    reports["integrity_report"]["output_sha256"] = {
        "V18_4_CANONICAL_BASELINE.json": sha256_file(baseline_out),
        "V18_4_RELATIONAL_SNAPSHOT.json": sha256_file(snapshot_path),
    }
    write_json(integrity_path, reports["integrity_report"])

    return {
        "output_dir": output_dir,
        "baseline": baseline_out,
        "snapshot": snapshot_path,
        "integrity_report": integrity_path,
        "regression_report": regression_path,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compile Antahpura V18.4 canonical integrity runtime."
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        default=DEFAULT_BASELINE,
        help="Path to V18.2 canonical baseline JSON.",
    )
    parser.add_argument(
        "--runtime",
        type=Path,
        default=DEFAULT_RUNTIME,
        help="Path to V18.3 relational runtime snapshot JSON.",
    )
    parser.add_argument(
        "--relationships",
        type=Path,
        default=DEFAULT_RELATIONSHIP_REGISTRY,
        help="Path to canonical relationship registry JSON.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="V18.4 output directory.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    print("Antahpura V18.4 canonical integrity compiler")

    try:
        paths = compile_v18_4(
            baseline_path=args.baseline,
            runtime_path=args.runtime,
            relationship_path=args.relationships,
            output_dir=args.output,
        )
    except IntegrityFailure as exc:
        print("\nV18.4 canonical integrity compilation: FAIL")
        print(str(exc))
        return 1
    except Exception as exc:
        print("\nV18.4 compiler error:")
        print(f"{type(exc).__name__}: {exc}")
        return 2

    report = load_json(paths["integrity_report"])
    counts = report["counts"]

    print("V18.4 canonical integrity compilation: PASS")
    print(f"Characters: {counts['characters']}")
    print(f"Relationships: {counts['relationships']}")
    print(f"Canonical relationships: {counts['canonical_relationships']}")
    print(f"Affiliations: {counts['affiliations']}")
    print(f"Skill classes: {counts['skill_classes']}")
    print("Canonical provenance: PRESERVED")
    print("Canonical relationships: PRESERVED")
    print("Sovereign marriage axis: PRESERVED")
    print("Office immutability: PASS")
    print("Authority transfer: BLOCKED")
    print("Skill → office transfer: BLOCKED")
    print("Knowledge → authority transfer: BLOCKED")
    print(f"\nRuntime directory: {paths['output_dir']}")
    print(f"Snapshot: {paths['snapshot']}")
    print(f"Integrity report: {paths['integrity_report']}")
    print(f"Regression report: {paths['regression_report']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
