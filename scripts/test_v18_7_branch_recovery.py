import copy
import json
import tempfile
import unittest
from pathlib import Path

from v18_7_compile_branch_recovery import (
    V187IntegrityError, assert_integrity, build_branch, build_v18_7,
    make_checkpoint, normalize_canonical, recover_from_checkpoint,
    replay_prefix, sha256_json, validate_event_chain,
)


def canonical_fixture():
    return {
        "characters": {
            "maha_deva": {"canonical_id":"maha_deva","canonical_name":"Mahā Deva","constitutional_office":"Sovereign / High Priest / Ritual Authority","constitutional_authority":{"status":"immutable"}},
            "kumari_rati": {"canonical_id":"kumari_rati","canonical_name":"Princess Kumārī Rati","constitutional_office":"Princess / Dynastic Center / Initiand","constitutional_authority":{"status":"immutable"}},
            "tarana": {"canonical_id":"tarana","canonical_name":"Tarana","constitutional_office":"Pradhāna Nartī / Chief Dancer","constitutional_authority":{"status":"immutable"}},
        },
        "relationships": [
            {"from":"maha_deva","to":"kumari_rati","relation":"marriage"},
            {"from":"maha_deva","to":"kumari_rati","relation":"ritual_authority"},
        ],
        "sovereign_axis": {"type":"constitutional_relationship","status":"newly_wedded","members":["maha_deva","kumari_rati"],"bond":"marriage","dynastic_status":"active"},
    }


def events_fixture():
    return [
        {"event_id":"e1","sequence":1,"event_type":"training_started","character_id":"kumari_rati","skill":"dance","instructor":"tarana"},
        {"event_id":"e2","sequence":2,"event_type":"training_progressed","character_id":"kumari_rati","skill":"dance","progress":0.75},
        {"event_id":"e3","sequence":3,"event_type":"training_completed","character_id":"kumari_rati","skill":"dance","mastery":"trained"},
        {"event_id":"e4","sequence":4,"event_type":"knowledge_acquired","character_id":"kumari_rati","knowledge":"court_dance_protocol","source":"tarana"},
        {"event_id":"e5","sequence":5,"event_type":"kala_training","character_id":"kumari_rati","kala":"nritya","mastery":"initiated"},
        {"event_id":"e6","sequence":6,"event_type":"flag_set","character_id":"kumari_rati","flag":"dance_training_completed"},
    ]


class V187Tests(unittest.TestCase):
    def setUp(self):
        self.c = normalize_canonical(canonical_fixture())
        self.e = events_fixture()

    def test_empty_branch_deterministic(self):
        a = build_branch(self.c, [], "main")
        b = build_branch(self.c, [], "main")
        self.assertEqual(a["state_hash"], b["state_hash"])

    def test_main_branch_replays_all_events(self):
        b = build_branch(self.c, self.e, "main")
        self.assertEqual(b["event_count"], 6)
        self.assertIn("dance", b["state"]["runtime"]["skills"]["kumari_rati"])
        self.assertTrue(b["state"]["runtime"]["flags"]["kumari_rati"]["dance_training_completed"])

    def test_prefix_is_rollback(self):
        full = build_branch(self.c, self.e, "main", 6)
        rolled = build_branch(self.c, self.e, "rollback", 3)
        self.assertNotEqual(full["state_hash"], rolled["state_hash"])
        self.assertNotIn("court_dance_protocol", rolled["state"]["runtime"]["knowledge"].get("kumari_rati", {}))

    def test_fork_has_distinct_identity_but_same_prefix_state(self):
        a = build_branch(self.c, self.e, "main", 3)
        b = build_branch(self.c, self.e, "dance_training_review", 3)
        self.assertEqual(a["state_hash"], b["state_hash"])
        self.assertNotEqual(a["branch_id"], b["branch_id"])

    def test_checkpoint_recovery(self):
        b = build_branch(self.c, self.e, "main", 4)
        recovered = recover_from_checkpoint(self.c, self.e, b["checkpoint"])
        self.assertEqual(recovered["state_hash"], b["state_hash"])
        self.assertEqual(recovered["checkpoint"], b["checkpoint"])

    def test_tampered_checkpoint_fails(self):
        b = build_branch(self.c, self.e, "main", 4)
        cp = copy.deepcopy(b["checkpoint"])
        cp["state_hash"] = "tampered"
        with self.assertRaises(V187IntegrityError):
            recover_from_checkpoint(self.c, self.e, cp)

    def test_chain_integrity(self):
        b = build_branch(self.c, self.e, "main")
        validate_event_chain(b["replay_chain"], self.e)

    def test_tampered_chain_fails(self):
        b = build_branch(self.c, self.e, "main")
        chain = copy.deepcopy(b["replay_chain"])
        chain[2]["before_hash"] = "tampered"
        with self.assertRaises(V187IntegrityError):
            validate_event_chain(chain, self.e)

    def test_sequence_gap_fails(self):
        e = copy.deepcopy(self.e)
        e[2]["sequence"] = 99
        with self.assertRaises(V187IntegrityError):
            replay_prefix(self.c, e)

    def test_duplicate_event_fails(self):
        e = copy.deepcopy(self.e)
        e[-1]["event_id"] = e[0]["event_id"]
        with self.assertRaises(V187IntegrityError):
            replay_prefix(self.c, e)

    def test_unknown_character_fails(self):
        e = copy.deepcopy(self.e)
        e[0]["character_id"] = "unknown"
        with self.assertRaises(V187IntegrityError):
            replay_prefix(self.c, e)

    def test_unknown_event_type_fails(self):
        e = copy.deepcopy(self.e)
        e[0]["event_type"] = "rewrite_constitution"
        with self.assertRaises(V187IntegrityError):
            replay_prefix(self.c, e)

    def test_office_mutation_blocked(self):
        e = copy.deepcopy(self.e)
        e[0]["constitutional_office"] = "Pradhāna Nartī"
        with self.assertRaises(V187IntegrityError):
            replay_prefix(self.c, e)

    def test_authority_mutation_blocked(self):
        e = copy.deepcopy(self.e)
        e[0]["authority"] = "transferred"
        with self.assertRaises(V187IntegrityError):
            replay_prefix(self.c, e)

    def test_provenance_mutation_blocked(self):
        e = copy.deepcopy(self.e)
        e[0]["provenance"] = "forged"
        with self.assertRaises(V187IntegrityError):
            replay_prefix(self.c, e)

    def test_sovereign_axis_locked(self):
        b = build_branch(self.c, self.e, "main")
        self.assertEqual(b["state"]["sovereign_axis"], self.c["sovereign_axis"])

    def test_canonical_relationships_locked(self):
        b = build_branch(self.c, self.e, "main")
        canonical = {(r["from"],r["to"],r["relation"]) for r in self.c["relationships"]}
        actual = {(r["from"],r["to"],r["relation"]) for r in b["state"]["relationships"]}
        self.assertTrue(canonical.issubset(actual))

    def test_rati_learns_dance_not_office(self):
        b = build_branch(self.c, self.e, "main", 3)
        rati = b["state"]["characters"]["kumari_rati"]
        self.assertIn("dance", b["state"]["runtime"]["skills"]["kumari_rati"])
        self.assertEqual(rati["constitutional_office"], "Princess / Dynastic Center / Initiand")

    def test_tampered_state_detected(self):
        b = build_branch(self.c, self.e, "main")
        b["state"]["characters"]["kumari_rati"]["constitutional_office"] = "Pradhāna Nartī / Chief Dancer"
        with self.assertRaises(V187IntegrityError):
            assert_integrity(b["state"], self.c)

    def test_invalid_branch_id(self):
        with self.assertRaises(V187IntegrityError):
            build_branch(self.c, self.e, "bad/name")

    def test_build_artifacts(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "registry/V18_RUNTIME").mkdir(parents=True)
            (repo / "registry/V18_6_RUNTIME").mkdir(parents=True)
            (repo / "registry/V18_RUNTIME/V18_2_CANONICAL_BASELINE.json").write_text(json.dumps(canonical_fixture(), ensure_ascii=False), encoding="utf-8")
            (repo / "registry/V18_6_RUNTIME/V18_6_REPLAY_CHAIN.json").write_text(json.dumps({"events": self.e}, ensure_ascii=False), encoding="utf-8")
            branch, report = build_v18_7(repo)
            out = repo / "registry/V18_7_RUNTIME"
            self.assertTrue((out / "V18_7_MAIN_BRANCH.json").exists())
            self.assertTrue((out / "V18_7_CHECKPOINT.json").exists())
            self.assertTrue((out / "V18_7_BRANCH_RECOVERY_REPORT.json").exists())
            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report["events"], 6)
            self.assertEqual(branch["state_hash"], sha256_json(branch["state"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
