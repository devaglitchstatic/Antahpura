#!/usr/bin/env python3
"""
Antahpura V18.4 — Canonical Integrity Regression Tests

Dependency-free unittest suite.

The suite uses temporary synthetic fixtures so it can run on any machine.
It also contains an optional real-repository integration test when the
expected D:\\dolphin\\AntahpuraRepo layout exists.

Run:
    python .\scripts\test_v18_4_integrity.py

or:
    python -m unittest .\scripts\test_v18_4_integrity.py -v
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

# Allow execution both as:
#   python scripts\test_v18_4_integrity.py
# and:
#   python -m unittest scripts.test_v18_4_integrity
try:
    from v18_4_compile_canonical_integrity import (
        IntegrityFailure,
        build_v18_4_snapshot,
        compile_v18_4,
    )
except ImportError:
    from scripts.v18_4_compile_canonical_integrity import (
        IntegrityFailure,
        build_v18_4_snapshot,
        compile_v18_4,
    )


PROVENANCE = {
    "maha_deva": "Maratha–Rajput border lineage",
    "kumari_rati": "Deccani royal house",
    "roxana": "Persian / Indo-Persian court context",
    "shrinagar": "Kashmiri scholarly lineage",
    "malika": "Turkic / chancellery-guard context",
    "jahzara": "Indo-Persian frontier / Kshatriya military lineage",
    "altani": "Mongol–Turkic / Steppe lineage",
    "anisa": "Abyssinian / Habshi / East African",
    "padma": "Santhal / Adivasi environmental lineage",
    "campa": "Munda lineage",
    "reva": "Dravidian / South Indian cultural lineage",
    "tarana": "Sogdian / Samarkand / Silk Road",
    "sevda": "Turkic / ascetic custodial lineage",
    "svara": (
        "Constitutional replacement seat; cultural provenance "
        "to be separately documented"
    ),
}

OFFICES = {
    "maha_deva": "Sovereign / High Priest / Ritual Authority",
    "kumari_rati": "Princess / Dynastic Center / Initiand",
    "roxana": "Persian Consort / Grand Vizier / Diwan & Diplomatic Authority",
    "shrinagar": "Mahā Vādaka / Chief Musician",
    "malika": "Threshold Warden / Transitional Rite Commander",
    "jahzara": "Agra-Pratihāriṇī / Vanguard Sentinel",
    "altani": "Outer Perimeter Sentinel / Reconnaissance Commander",
    "anisa": "Chief Court Supervisor / Administrative Enforcer",
    "padma": "Personal Handmaiden / Nourishment & Environmental Protection",
    "campa": "Handmaiden Apprentice / Non-Verbal Companion",
    "reva": "Rāja-Kavi / Principal Voice / Breathkeeper",
    "tarana": "Pradhāna Nartī / Chief Dancer",
    "sevda": "Subterranean Warden / Ritual Containment Matron",
    "svara": "Cultural & Artistic Specialist / Micro-tonal Calibration",
}


RELATIONSHIPS = [
    ("maha_deva", "kumari_rati", "ritual_authority"),
    ("maha_deva", "roxana", "civil_authority"),
    ("maha_deva", "anisa", "administrative_authority"),
    ("kumari_rati", "padma", "attendant_care"),
    ("kumari_rati", "campa", "attendant_companionship"),
    ("jahzara", "kumari_rati", "royal_protection"),
    ("jahzara", "roxana", "security_coordination"),
    ("jahzara", "anisa", "administrative_security_compliance"),
    ("malika", "maha_deva", "threshold_subordination"),
    ("malika", "kumari_rati", "threshold_protection"),
    ("altani", "jahzara", "perimeter_synchronization"),
    ("shrinagar", "reva", "acoustic_coordination"),
    ("reva", "tarana", "acoustic_movement_coordination"),
    ("svara", "shrinagar", "microtonal_tuning_coordination"),
    ("svara", "reva", "intonation_coordination"),
    ("svara", "tarana", "movement_pitch_coordination"),
    ("sevda", "maha_deva", "ritual_containment"),
    ("anisa", "reva", "archive_chronicle_duality"),
]


def edge(a: str, b: str, relation: str) -> dict:
    return {
        "from": a,
        "to": b,
        "relation": relation,
        "status": "canonical",
    }


def make_baseline() -> dict:
    chars = {}
    aff = {}

    for cid, office in OFFICES.items():
        chars[cid] = {
            "canonical_id": cid,
            "canonical_name": cid,
            "constitutional_office": office,
            "constitutional_authority": {
                "status": "immutable",
                "may_change_through_runtime_skill": False,
                "may_change_through_training": False,
                "may_change_through_knowledge": False,
            },
        }
        aff[cid] = {
            "canonical_id": cid,
            "faction": None,
            "affiliations": [],
            "provenance": PROVENANCE[cid],
        }

    return {
        "schema": "V18.2_CANONICAL_BASELINE",
        "version": "18.2",
        "characters": chars,
        "affiliations": {
            "schema": "V18.2_AFFILIATION_STATE",
            "characters": aff,
        },
        "relationships": {
            "relationships": [
                edge(*x) for x in RELATIONSHIPS
            ]
        },
        "sovereign_axis": {
            "type": "constitutional_relationship",
            "status": "newly_wedded",
            "members": ["maha_deva", "kumari_rati"],
            "bond": "marriage",
            "dynastic_status": "active",
        },
    }


def make_runtime(provenance_null: bool = True) -> dict:
    baseline = make_baseline()

    runtime_chars = {}
    for cid, value in baseline["characters"].items():
        runtime_chars[cid] = dict(value)
        runtime_chars[cid]["capability_domains"] = {
            "skills": {},
            "knowledge": {},
            "kalas": {},
        }
        runtime_chars[cid]["training_state"] = {
            "active_training": [],
            "completed_training": [],
            "instructors": [],
        }

    runtime_aff = {}
    for cid in baseline["affiliations"]["characters"]:
        item = dict(baseline["affiliations"]["characters"][cid])
        if provenance_null:
            item["provenance"] = None
        runtime_aff[cid] = item

    runtime_edges = [
        edge(*x) for x in RELATIONSHIPS
    ]

    return {
        "schema": "V18.3_RELATIONAL_RUNTIME_SNAPSHOT",
        "version": "18.3",
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
        "sovereign_axis": baseline["sovereign_axis"],
        "characters": runtime_chars,
        "relationships": {
            "schema": "V18.3_RELATIONSHIP_STATE",
            "relationship_count": len(runtime_edges),
            "relationships": runtime_edges,
        },
        "affiliations": {
            "schema": "V18.3_AFFILIATION_STATE",
            "characters": runtime_aff,
        },
        "skills": {
            "schema": "V18.3_SKILL_KALA_REGISTRY",
            "skill_classes": {
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
            },
            "office_skill_examples": {
                "kumari_rati": {
                    "may_learn": ["dance", "vocal_music"],
                    "may_not_acquire_by_training": [
                        "pradhana_narti",
                        "high_priest",
                    ],
                }
            },
        },
        "jurisdiction": {
            "rules": [
                {
                    "rule": "office_skill_separation",
                    "description": "Skills do not transfer office.",
                }
            ]
        },
    }


class V184CanonicalIntegrityTests(unittest.TestCase):

    def test_full_baseline_compiles(self):
        baseline = make_baseline()
        runtime = make_runtime()

        snapshot, failures, reports = build_v18_4_snapshot(
            baseline, runtime, None
        )

        self.assertEqual(failures, [])
        self.assertEqual(snapshot["version"], "18.4")
        self.assertEqual(len(snapshot["characters"]), 14)
        self.assertEqual(
            snapshot["relationships"]["relationship_count"], 18
        )
        self.assertEqual(
            reports["integrity_report"]["status"], "PASS"
        )

    def test_provenance_is_repaired_from_canonical_baseline(self):
        baseline = make_baseline()
        runtime = make_runtime(provenance_null=True)

        snapshot, _, _ = build_v18_4_snapshot(
            baseline, runtime, None
        )

        actual = snapshot["affiliations"]["characters"]
        for cid, expected in PROVENANCE.items():
            self.assertEqual(
                actual[cid]["provenance"],
                expected,
                cid,
            )

    def test_provenance_cannot_be_changed_to_a_different_value(self):
        baseline = make_baseline()
        runtime = make_runtime(provenance_null=False)
        runtime["affiliations"]["characters"]["padma"][
            "provenance"
        ] = "invented provenance"

        with self.assertRaises(IntegrityFailure):
            build_v18_4_snapshot(
                baseline, runtime, None
            )

    def test_missing_character_fails(self):
        baseline = make_baseline()
        runtime = make_runtime()
        del runtime["characters"]["svara"]

        with self.assertRaises(IntegrityFailure):
            build_v18_4_snapshot(
                baseline, runtime, None
            )

    def test_unknown_character_fails(self):
        baseline = make_baseline()
        runtime = make_runtime()
        runtime["characters"]["zola"] = {
            "canonical_id": "zola",
            "constitutional_office": "Unknown",
        }

        with self.assertRaises(IntegrityFailure):
            build_v18_4_snapshot(
                baseline, runtime, None
            )

    def test_office_mutation_fails(self):
        baseline = make_baseline()
        runtime = make_runtime()
        runtime["characters"]["kumari_rati"][
            "constitutional_office"
        ] = "Pradhāna Nartī / Chief Dancer"

        with self.assertRaises(IntegrityFailure):
            build_v18_4_snapshot(
                baseline, runtime, None
            )

    def test_authority_mutation_fails(self):
        baseline = make_baseline()
        runtime = make_runtime()
        runtime["characters"]["kumari_rati"][
            "constitutional_authority"
        ]["status"] = "transferable"

        with self.assertRaises(IntegrityFailure):
            build_v18_4_snapshot(
                baseline, runtime, None
            )

    def test_canonical_relationship_cannot_disappear(self):
        baseline = make_baseline()
        runtime = make_runtime()
        runtime["relationships"]["relationships"] = (
            runtime["relationships"]["relationships"][:-1]
        )

        with self.assertRaises(IntegrityFailure):
            build_v18_4_snapshot(
                baseline, runtime, None
            )

    def test_unknown_skill_cannot_enable_authority_transfer(self):
        baseline = make_baseline()
        runtime = make_runtime()
        runtime["skills"]["skill_classes"]["dance"][
            "authority_transfer"
        ] = True

        with self.assertRaises(IntegrityFailure):
            build_v18_4_snapshot(
                baseline, runtime, None
            )

    def test_rati_can_learn_dance_but_cannot_become_dancer(self):
        baseline = make_baseline()
        runtime = make_runtime()

        snapshot, _, _ = build_v18_4_snapshot(
            baseline, runtime, None
        )

        rati = snapshot["characters"]["kumari_rati"]

        self.assertEqual(
            rati["constitutional_office"],
            "Princess / Dynastic Center / Initiand",
        )

        rules = snapshot["skills"]["office_skill_examples"][
            "kumari_rati"
        ]

        self.assertIn("dance", rules["may_learn"])
        self.assertIn(
            "pradhana_narti",
            rules["may_not_acquire_by_training"],
        )

    def test_sovereign_marriage_axis_is_preserved(self):
        baseline = make_baseline()
        runtime = make_runtime()

        snapshot, _, _ = build_v18_4_snapshot(
            baseline, runtime, None
        )

        axis = snapshot["sovereign_axis"]

        self.assertEqual(
            axis["members"],
            ["maha_deva", "kumari_rati"],
        )
        self.assertEqual(axis["bond"], "marriage")
        self.assertEqual(axis["dynastic_status"], "active")

    def test_relationship_registry_fallback(self):
        baseline = make_baseline()
        baseline["relationships"] = {
            "relationships": []
        }
        runtime = make_runtime()

        registry = {
            "version": "17.1",
            "edges": [
                edge(*RELATIONSHIPS[0]),
            ],
        }

        # Only one canonical edge is asserted in this synthetic fallback.
        runtime["relationships"]["relationships"] = [
            edge(*RELATIONSHIPS[0])
        ]

        snapshot, _, _ = build_v18_4_snapshot(
            baseline, runtime, registry
        )

        self.assertEqual(
            snapshot["relationships"]["relationship_count"],
            1,
        )

    def test_runtime_output_does_not_change_canonical_office(self):
        baseline = make_baseline()
        runtime = make_runtime()

        runtime["characters"]["kumari_rati"][
            "capability_domains"
        ]["skills"]["dance"] = {
            "level": "master"
        }

        snapshot, _, _ = build_v18_4_snapshot(
            baseline, runtime, None
        )

        self.assertEqual(
            snapshot["characters"]["kumari_rati"][
                "constitutional_office"
            ],
            "Princess / Dynastic Center / Initiand",
        )

    def test_real_repository_compile_if_available(self):
        repo = Path(r"D:\\dolphin\\AntahpuraRepo")
        baseline = (
            repo / "registry" / "V18_2_CANONICAL_BASELINE.json"
        )
        runtime = (
            repo
            / "registry"
            / "V18_3_RUNTIME"
            / "V18_3_RELATIONAL_SNAPSHOT.json"
        )

        if not (baseline.exists() and runtime.exists()):
            self.skipTest(
                "Real Antahpura V18.2/V18.3 repository not available "
                "on this machine."
            )

        relationship = (
            repo / "registry" / "V17_1_RELATIONSHIP_REGISTRY.json"
        )
        output = repo / "registry" / "V18_4_RUNTIME_TEST"

        paths = compile_v18_4(
            baseline,
            runtime,
            relationship,
            output,
        )

        self.assertTrue(paths["snapshot"].exists())
        self.assertTrue(paths["integrity_report"].exists())

        with paths["snapshot"].open(
            "r", encoding="utf-8-sig"
        ) as fh:
            snapshot = json.load(fh)

        self.assertEqual(snapshot["version"], "18.4")
        self.assertEqual(
            len(snapshot["characters"]),
            14,
        )
        self.assertEqual(
            snapshot["relationships"]["relationship_count"],
            18,
        )

        self.assertEqual(
            snapshot["affiliations"]["characters"][
                "kumari_rati"
            ]["provenance"],
            PROVENANCE["kumari_rati"],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
