#!/usr/bin/env python3
"""
Antahpura V18.5 — Runtime Event & State Mutation Engine Tests

Dependency-free unittest suite.

Run:
    python -m scripts.test_v18_5_runtime_event_engine

or:
    python -m unittest .\scripts\test_v18_5_runtime_event_engine.py -v
"""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

try:
    from v18_5_runtime_event_engine import (
        RuntimeMutationFailure,
        apply_event,
        apply_events,
        build_runtime_report,
        compile_v18_5,
        initialize_runtime,
    )
except ImportError:
    from scripts.v18_5_runtime_event_engine import (
        RuntimeMutationFailure,
        apply_event,
        apply_events,
        build_runtime_report,
        compile_v18_5,
        initialize_runtime,
    )


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


def make_canonical() -> dict:
    chars = {}
    affiliations = {}

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
        }
        affiliations[cid] = {
            "canonical_id": cid,
            "faction": None,
            "affiliations": [],
            "provenance": f"canonical provenance: {cid}",
        }

    skill_classes = {
        "dance": {
            "trainable": True,
            "associated_office": "pradhana_narti",
            "authority_transfer": False,
        },
        "rhythm": {
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
        "breath_control": {
            "trainable": True,
            "associated_office": None,
            "authority_transfer": False,
        },
        "languages": {
            "trainable": True,
            "associated_office": None,
            "authority_transfer": False,
        },
    }

    return {
        "schema": "V18.4_CANONICAL_INTEGRITY_RUNTIME_SNAPSHOT",
        "version": "18.4",
        "canonical_baseline": "V18.2",
        "constitutional_preservation": True,
        "characters": chars,
        "affiliations": {
            "schema": "V18.4_AFFILIATION_STATE",
            "characters": affiliations,
        },
        "relationships": {
            "relationships": [
                edge(*item) for item in RELATIONSHIPS
            ],
        },
        "sovereign_axis": {
            "type": "constitutional_relationship",
            "status": "newly_wedded",
            "members": ["maha_deva", "kumari_rati"],
            "bond": "marriage",
            "dynastic_status": "active",
            "source": "V17.1.1 canonical reconciliation",
        },
        "skills": {
            "schema": "V18.4_SKILL_KALA_REGISTRY",
            "skill_classes": skill_classes,
        },
    }


def event(event_id: str, event_type: str, actor: str, **payload) -> dict:
    return {
        "event_id": event_id,
        "event_type": event_type,
        "actor": actor,
        "payload": payload,
    }


class V185RuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.canonical = make_canonical()
        self.state = initialize_runtime(self.canonical)

    def test_initialization_locks_canon(self):
        self.assertEqual(self.state["schema"], "V18.5_RUNTIME_EVENT_STATE")
        self.assertTrue(self.state["canonical_locked"])
        self.assertEqual(self.state["runtime"]["event_count"], 0)
        self.assertEqual(self.state["event_log"], [])

    def test_training_lifecycle(self):
        state = apply_event(
            self.canonical,
            self.state,
            event(
                "evt-001",
                "training_started",
                "kumari_rati",
                skill="dance",
                instructor="tarana",
            ),
        )
        self.assertEqual(
            state["characters"]["kumari_rati"]["training_state"]
            ["active_training"][0]["skill"],
            "dance",
        )

        state = apply_event(
            self.canonical,
            state,
            event(
                "evt-002",
                "training_progressed",
                "kumari_rati",
                skill="dance",
                progress=100,
            ),
        )

        state = apply_event(
            self.canonical,
            state,
            event(
                "evt-003",
                "training_completed",
                "kumari_rati",
                skill="dance",
            ),
        )

        rati = state["characters"]["kumari_rati"]
        self.assertEqual(rati["training_state"]["active_training"], [])
        self.assertEqual(
            rati["capability_domains"]["skills"]["dance"]["proficiency"],
            100,
        )
        self.assertTrue(
            rati["capability_domains"]["skills"]["dance"]["learned"]
        )
        self.assertEqual(
            rati["constitutional_office"],
            OFFICES["kumari_rati"],
        )

    def test_rati_can_learn_dance_but_cannot_become_dancer(self):
        state = apply_events(
            self.canonical,
            self.state,
            [
                event(
                    "evt-r1",
                    "training_started",
                    "kumari_rati",
                    skill="dance",
                    instructor="tarana",
                ),
                event(
                    "evt-r2",
                    "training_progressed",
                    "kumari_rati",
                    skill="dance",
                    progress=100,
                ),
                event(
                    "evt-r3",
                    "training_completed",
                    "kumari_rati",
                    skill="dance",
                ),
            ],
        )

        rati = state["characters"]["kumari_rati"]
        self.assertIn("dance", rati["capability_domains"]["skills"])
        self.assertEqual(
            rati["constitutional_office"],
            OFFICES["kumari_rati"],
        )
        self.assertNotEqual(
            rati["constitutional_office"],
            OFFICES["tarana"],
        )

    def test_office_mutation_is_blocked(self):
        before = copy.deepcopy(self.state)
        with self.assertRaises(RuntimeMutationFailure):
            apply_event(
                self.canonical,
                self.state,
                event(
                    "evt-office",
                    "office_changed",
                    "kumari_rati",
                    office=OFFICES["tarana"],
                ),
            )
        self.assertEqual(self.state, before)

    def test_authority_mutation_is_blocked(self):
        with self.assertRaises(RuntimeMutationFailure):
            apply_event(
                self.canonical,
                self.state,
                event(
                    "evt-authority",
                    "authority_changed",
                    "kumari_rati",
                    authority="dance_authority",
                ),
            )

    def test_provenance_mutation_is_blocked(self):
        with self.assertRaises(RuntimeMutationFailure):
            apply_event(
                self.canonical,
                self.state,
                event(
                    "evt-prov",
                    "provenance_changed",
                    "kumari_rati",
                    provenance="fabricated",
                ),
            )

    def test_sovereign_axis_cannot_change(self):
        with self.assertRaises(RuntimeMutationFailure):
            apply_event(
                self.canonical,
                self.state,
                event(
                    "evt-axis",
                    "sovereign_axis_changed",
                    "maha_deva",
                    members=["maha_deva", "roxana"],
                ),
            )

    def test_canonical_relationship_deletion_is_blocked(self):
        with self.assertRaises(RuntimeMutationFailure):
            apply_event(
                self.canonical,
                self.state,
                event(
                    "evt-rel-delete",
                    "canonical_relationship_removed",
                    "maha_deva",
                    target="kumari_rati",
                ),
            )

    def test_emergent_relationship_update_is_allowed(self):
        state = apply_event(
            self.canonical,
            self.state,
            event(
                "evt-rel",
                "relationship_update",
                "maha_deva",
                target="kumari_rati",
                relation="ritual_authority",
                dimension="trust",
                value=35,
            ),
        )
        key = "maha_deva|kumari_rati|ritual_authority"
        item = state["runtime"]["emergent_relationships"][key]
        self.assertTrue(item["canonical"])
        self.assertEqual(item["dimensions"]["trust"], 35)

    def test_noncanonical_emergent_relationship_is_allowed(self):
        state = apply_event(
            self.canonical,
            self.state,
            event(
                "evt-rel-new",
                "relationship_update",
                "kumari_rati",
                target="reva",
                relation="private_affinity",
                dimension="familiarity",
                value=20,
            ),
        )
        key = "kumari_rati|reva|private_affinity"
        self.assertFalse(
            state["runtime"]["emergent_relationships"][key]["canonical"]
        )

    def test_knowledge_transfer_is_allowed_without_authority(self):
        state = apply_event(
            self.canonical,
            self.state,
            event(
                "evt-know",
                "knowledge_acquired",
                "kumari_rati",
                knowledge="court_ritual_protocol",
                value={"level": "advanced"},
                source="maha_deva",
            ),
        )
        rati = state["characters"]["kumari_rati"]
        self.assertIn(
            "court_ritual_protocol",
            rati["capability_domains"]["knowledge"],
        )
        self.assertEqual(
            rati["constitutional_authority"],
            self.canonical["characters"]["kumari_rati"]
            ["constitutional_authority"],
        )

    def test_kala_training_is_allowed(self):
        state = apply_event(
            self.canonical,
            self.state,
            event(
                "evt-kala",
                "kala_training",
                "kumari_rati",
                kala="lasya",
                progress=65,
            ),
        )
        self.assertEqual(
            state["characters"]["kumari_rati"]
            ["capability_domains"]["kalas"]["lasya"]["progress"],
            65,
        )

    def test_unknown_skill_is_rejected(self):
        with self.assertRaises(RuntimeMutationFailure):
            apply_event(
                self.canonical,
                self.state,
                event(
                    "evt-unknown-skill",
                    "training_started",
                    "kumari_rati",
                    skill="invented_office_skill",
                ),
            )

    def test_duplicate_event_id_is_rejected(self):
        first = event(
            "evt-dup",
            "status_set",
            "kumari_rati",
            status="studying",
        )
        state = apply_event(self.canonical, self.state, first)

        with self.assertRaises(RuntimeMutationFailure):
            apply_event(
                self.canonical,
                state,
                event(
                    "evt-dup",
                    "status_set",
                    "kumari_rati",
                    status="different",
                ),
            )

    def test_transactional_failure_does_not_mutate_state(self):
        before = copy.deepcopy(self.state)

        with self.assertRaises(RuntimeMutationFailure):
            apply_event(
                self.canonical,
                self.state,
                event(
                    "evt-bad",
                    "training_progressed",
                    "kumari_rati",
                    skill="dance",
                    progress=100,
                ),
            )

        self.assertEqual(self.state, before)

    def test_event_log_is_append_only(self):
        state = apply_event(
            self.canonical,
            self.state,
            event(
                "evt-status",
                "status_set",
                "kumari_rati",
                status="initiand_training",
            ),
        )
        self.assertEqual(len(state["event_log"]), 1)
        self.assertEqual(state["event_log"][0]["sequence"], 1)
        self.assertEqual(state["runtime"]["last_event_id"], "evt-status")

    def test_status_and_flag_lifecycle(self):
        state = apply_event(
            self.canonical,
            self.state,
            event(
                "evt-s1",
                "status_set",
                "kumari_rati",
                status="observing",
            ),
        )
        self.assertIn(
            "observing",
            state["runtime"]["statuses"]["kumari_rati"],
        )

        state = apply_event(
            self.canonical,
            state,
            event(
                "evt-s2",
                "status_clear",
                "kumari_rati",
                status="observing",
            ),
        )
        self.assertNotIn(
            "observing",
            state["runtime"]["statuses"]["kumari_rati"],
        )

        state = apply_event(
            self.canonical,
            state,
            event(
                "evt-f1",
                "flag_set",
                "kumari_rati",
                flag="dance_training_started",
                value=True,
            ),
        )
        self.assertTrue(
            state["runtime"]["flags"]["kumari_rati"]
            ["dance_training_started"]
        )

        state = apply_event(
            self.canonical,
            state,
            event(
                "evt-f2",
                "flag_clear",
                "kumari_rati",
                flag="dance_training_started",
            ),
        )
        self.assertNotIn(
            "dance_training_started",
            state["runtime"]["flags"]["kumari_rati"],
        )

    def test_canonical_relationships_remain_after_runtime_events(self):
        state = apply_events(
            self.canonical,
            self.state,
            [
                event(
                    "evt-a",
                    "status_set",
                    "kumari_rati",
                    status="alert",
                ),
                event(
                    "evt-b",
                    "relationship_update",
                    "maha_deva",
                    target="kumari_rati",
                    relation="ritual_authority",
                    dimension="respect",
                    value=90,
                ),
            ],
        )
        canonical_keys = {
            (
                item["from"],
                item["to"],
                item["relation"],
            )
            for item in self.canonical["relationships"]["relationships"]
        }
        runtime_keys = {
            (
                item["from"],
                item["to"],
                item["relation"],
            )
            for item in state["relationships"]["relationships"]
        }
        self.assertTrue(canonical_keys.issubset(runtime_keys))

    def test_canonical_character_mutation_in_source_is_detected(self):
        corrupted = copy.deepcopy(self.canonical)
        corrupted["characters"]["kumari_rati"][
            "constitutional_office"
        ] = OFFICES["tarana"]

        with self.assertRaises(RuntimeMutationFailure):
            apply_event(
                self.canonical,
                corrupted,
                event(
                    "evt-detect",
                    "status_set",
                    "kumari_rati",
                    status="x",
                ),
            )

    def test_compile_writes_three_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            canonical_path = tmp_path / "canonical.json"
            output = tmp_path / "V18_5_RUNTIME"

            canonical_path.write_text(
                json.dumps(self.canonical, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            paths = compile_v18_5(
                canonical_path=canonical_path,
                output_dir=output,
            )

            self.assertTrue(paths["state"].exists())
            self.assertTrue(paths["event_log"].exists())
            self.assertTrue(paths["report"].exists())

            report = json.loads(
                paths["report"].read_text(encoding="utf-8")
            )
            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report["counts"]["events"], 0)

    def test_compile_with_event_stream(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            canonical_path = tmp_path / "canonical.json"
            events_path = tmp_path / "events.json"
            output = tmp_path / "V18_5_RUNTIME"

            canonical_path.write_text(
                json.dumps(self.canonical, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            events = {
                "schema": "V18.5_EVENT_STREAM",
                "version": "18.5",
                "events": [
                    event(
                        "evt-compile-1",
                        "training_started",
                        "kumari_rati",
                        skill="dance",
                        instructor="tarana",
                    ),
                    event(
                        "evt-compile-2",
                        "training_progressed",
                        "kumari_rati",
                        skill="dance",
                        progress=100,
                    ),
                    event(
                        "evt-compile-3",
                        "training_completed",
                        "kumari_rati",
                        skill="dance",
                    ),
                ],
            }

            events_path.write_text(
                json.dumps(events, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            paths = compile_v18_5(
                canonical_path=canonical_path,
                output_dir=output,
                events_path=events_path,
            )

            state = json.loads(
                paths["state"].read_text(encoding="utf-8")
            )
            self.assertEqual(len(state["event_log"]), 3)
            self.assertIn(
                "dance",
                state["characters"]["kumari_rati"]
                ["capability_domains"]["skills"],
            )
            self.assertEqual(
                state["characters"]["kumari_rati"]
                ["constitutional_office"],
                OFFICES["kumari_rati"],
            )

    def test_runtime_report(self):
        state = apply_event(
            self.canonical,
            self.state,
            event(
                "evt-report",
                "knowledge_acquired",
                "kumari_rati",
                knowledge="dance_theory",
            ),
        )
        report = build_runtime_report(self.canonical, state)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["counts"]["events"], 1)
        self.assertEqual(report["counts"]["knowledge_items"], 1)
        self.assertEqual(
            report["invariants"]["skill_to_office_transfer"],
            "BLOCKED",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
