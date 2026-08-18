import copy, json, tempfile, unittest
from pathlib import Path
from v18_6_compile_event_replay import (
    V186IntegrityError, build_v18_6, normalize_canonical, replay_events, sha256_json,
    assert_integrity
)

def canonical_fixture():
    return {
        "characters": {
            "maha_deva": {"canonical_id":"maha_deva","canonical_name":"Mahā Deva",
                "constitutional_office":"Sovereign / High Priest / Ritual Authority",
                "constitutional_authority":{"status":"immutable"}},
            "kumari_rati": {"canonical_id":"kumari_rati","canonical_name":"Princess Kumārī Rati",
                "constitutional_office":"Princess / Dynastic Center / Initiand",
                "constitutional_authority":{"status":"immutable"}},
            "tarana": {"canonical_id":"tarana","canonical_name":"Tarana",
                "constitutional_office":"Pradhāna Nartī / Chief Dancer",
                "constitutional_authority":{"status":"immutable"}},
        },
        "relationships":[
            {"from":"maha_deva","to":"kumari_rati","relation":"marriage"},
            {"from":"maha_deva","to":"kumari_rati","relation":"ritual_authority"},
        ],
        "sovereign_axis":{"type":"constitutional_relationship","status":"newly_wedded",
            "members":["maha_deva","kumari_rati"],"bond":"marriage","dynastic_status":"active"}
    }

def events_fixture():
    return [
        {"event_id":"e1","sequence":1,"event_type":"training_started","character_id":"kumari_rati","skill":"dance","instructor":"tarana"},
        {"event_id":"e2","sequence":2,"event_type":"training_progressed","character_id":"kumari_rati","skill":"dance","progress":0.75},
        {"event_id":"e3","sequence":3,"event_type":"training_completed","character_id":"kumari_rati","skill":"dance","mastery":"trained"},
        {"event_id":"e4","sequence":4,"event_type":"knowledge_acquired","character_id":"kumari_rati","knowledge":"court_dance_protocol","source":"tarana"},
        {"event_id":"e5","sequence":5,"event_type":"kala_training","character_id":"kumari_rati","kala":"nritya","mastery":"initiated"},
        {"event_id":"e6","sequence":6,"event_type":"relationship_update","from":"maha_deva","to":"kumari_rati","relation":"marriage","state":{"affection":1,"trust":1}},
        {"event_id":"e7","sequence":7,"event_type":"flag_set","character_id":"kumari_rati","flag":"dance_training_completed"},
    ]

class V186Tests(unittest.TestCase):
    def setUp(self):
        self.c = normalize_canonical(canonical_fixture())
        self.e = events_fixture()

    def test_empty_replay_deterministic(self):
        a,_=replay_events(self.c,[]); b,_=replay_events(self.c,[])
        self.assertEqual(a,b); self.assertEqual(sha256_json(a),sha256_json(b))

    def test_replay_mutations(self):
        s,chain=replay_events(self.c,self.e)
        self.assertEqual(len(chain),7)
        self.assertIn("dance",s["runtime"]["skills"]["kumari_rati"])
        self.assertIn("court_dance_protocol",s["runtime"]["knowledge"]["kumari_rati"])
        self.assertIn("nritya",s["runtime"]["kalas"]["kumari_rati"])
        self.assertTrue(s["runtime"]["flags"]["kumari_rati"]["dance_training_completed"])

    def test_repeat_same_hash(self):
        a,_=replay_events(self.c,self.e); b,_=replay_events(self.c,self.e)
        self.assertEqual(sha256_json(a),sha256_json(b))

    def test_duplicate_event_fails(self):
        e=copy.deepcopy(self.e); e.append(copy.deepcopy(e[0])); e[-1]["sequence"]=8
        with self.assertRaises(V186IntegrityError): replay_events(self.c,e)

    def test_sequence_gap_fails(self):
        e=copy.deepcopy(self.e); e[2]["sequence"]=99
        with self.assertRaises(V186IntegrityError): replay_events(self.c,e)

    def test_reordered_sequence_fails(self):
        e=copy.deepcopy(self.e); e[1],e[2]=e[2],e[1]
        with self.assertRaises(V186IntegrityError): replay_events(self.c,e)

    def test_unknown_character_fails(self):
        e=[copy.deepcopy(self.e[0])]; e[0]["character_id"]="unknown"
        with self.assertRaises(V186IntegrityError): replay_events(self.c,e)

    def test_unknown_event_type_fails(self):
        e=[copy.deepcopy(self.e[0])]; e[0]["event_type"]="rewrite_constitution"
        with self.assertRaises(V186IntegrityError): replay_events(self.c,e)

    def test_office_mutation_fails(self):
        e=[copy.deepcopy(self.e[0])]; e[0]["constitutional_office"]="Pradhāna Nartī"
        with self.assertRaises(V186IntegrityError): replay_events(self.c,e)

    def test_authority_mutation_fails(self):
        e=[copy.deepcopy(self.e[0])]; e[0]["authority"]="transferred"
        with self.assertRaises(V186IntegrityError): replay_events(self.c,e)

    def test_provenance_mutation_fails(self):
        e=[copy.deepcopy(self.e[0])]; e[0]["provenance"]="forged"
        with self.assertRaises(V186IntegrityError): replay_events(self.c,e)

    def test_rati_learns_dance_not_office(self):
        s,_=replay_events(self.c,self.e[:3])
        self.assertIn("dance",s["runtime"]["skills"]["kumari_rati"])
        self.assertEqual(s["characters"]["kumari_rati"]["constitutional_office"],
                         "Princess / Dynastic Center / Initiand")
        self.assertNotEqual(s["characters"]["kumari_rati"]["constitutional_office"],
                            "Pradhāna Nartī / Chief Dancer")

    def test_unknown_skill_still_cannot_change_office(self):
        e=[{"event_id":"x","sequence":1,"event_type":"training_completed",
            "character_id":"kumari_rati","skill":"unknown_skill"}]
        s,_=replay_events(self.c,e)
        self.assertIn("unknown_skill",s["runtime"]["skills"]["kumari_rati"])
        self.assertEqual(s["characters"]["kumari_rati"]["constitutional_office"],
                         "Princess / Dynastic Center / Initiand")

    def test_canonical_relationship_preserved(self):
        s,_=replay_events(self.c,self.e)
        self.assertTrue({("maha_deva","kumari_rati","marriage"),
                         ("maha_deva","kumari_rati","ritual_authority")}.issubset(
                         {(r["from"],r["to"],r["relation"]) for r in s["relationships"]}))

    def test_sovereign_axis_preserved(self):
        s,_=replay_events(self.c,self.e)
        self.assertEqual(s["sovereign_axis"],self.c["sovereign_axis"])

    def test_tampered_snapshot_detected(self):
        s,_=replay_events(self.c,[])
        s["relationships"].pop()
        with self.assertRaises(V186IntegrityError): assert_integrity(s,self.c)

    def test_chain_hashes_present(self):
        _,chain=replay_events(self.c,self.e)
        self.assertEqual(len(chain),7)
        for x in chain:
            self.assertTrue(x["before_hash"]); self.assertTrue(x["after_hash"])

    def test_hash_changes_after_event(self):
        a,_=replay_events(self.c,[]); b,_=replay_events(self.c,self.e)
        self.assertNotEqual(sha256_json(a),sha256_json(b))

    def test_build_artifacts(self):
        with tempfile.TemporaryDirectory() as td:
            repo=Path(td)
            (repo/"registry/V18_RUNTIME").mkdir(parents=True)
            (repo/"registry/V18_5_RUNTIME").mkdir(parents=True)
            (repo/"registry/V18_RUNTIME/V18_2_CANONICAL_BASELINE.json").write_text(
                json.dumps(canonical_fixture(),ensure_ascii=False),encoding="utf-8")
            (repo/"registry/V18_5_RUNTIME/V18_5_EVENT_LOG.json").write_text(
                json.dumps({"events":events_fixture()},ensure_ascii=False),encoding="utf-8")
            s,r=build_v18_6(repo)
            out=repo/"registry/V18_6_RUNTIME"
            self.assertTrue((out/"V18_6_RUNTIME_STATE.json").exists())
            self.assertTrue((out/"V18_6_REPLAY_CHAIN.json").exists())
            self.assertTrue((out/"V18_6_EVENT_REPLAY_REPORT.json").exists())
            self.assertEqual(r["status"],"PASS")
            self.assertEqual(r["event_count"],7)
            self.assertEqual(r["replayed_state_hash"],sha256_json(s))

if __name__=="__main__":
    unittest.main(verbosity=2)
