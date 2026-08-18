import json, tempfile, unittest
from pathlib import Path
import importlib.util

MODULE = Path(__file__).resolve().parent / "v18_8_1_compile_kama_taxonomy.py"
spec = importlib.util.spec_from_file_location("kama_compiler", MODULE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class V1881Tests(unittest.TestCase):
    def setUp(self):
        self.master = {
            "schema":"V18.8.1_MASTER_KINK_REGISTRY",
            "kinks":[{"id":"A"},{"id":"B"},{"id":"C"}],
            "progression_model":{
                "constitutional_office_transfer":False,
                "institutional_authority_transfer":False
            }
        }
        self.graph = {
            "schema":"V18.8.1_KINK_RELATION_GRAPH",
            "relations":[
                {"source":"A","target":"B","relation":"related"},
                {"source":"A","target":"C","relation":"similar"}
            ]
        }
        self.rules = {
            "schema":"V18.8.1_KAMA_PROGRESSION_RULES",
            "progression_stages":[{"stage":"knowledge"},{"stage":"training"},{"stage":"practice"},{"stage":"mastery"}],
            "vamacari":{
                "siddhi_grants_constitutional_authority":False,
                "siddhi_changes_constitutional_office":False
            }
        }
    def test_schema_passes(self):
        mod.validate(self.master, self.graph, self.rules)
    def test_duplicate_ids_fail(self):
        self.master["kinks"].append({"id":"A"})
        with self.assertRaises(mod.KamaIntegrityError):
            mod.validate(self.master, self.graph, self.rules)
    def test_unknown_node_fails(self):
        self.graph["relations"][0]["target"]="Z"
        with self.assertRaises(mod.KamaIntegrityError):
            mod.validate(self.master, self.graph, self.rules)
    def test_office_transfer_fails(self):
        self.master["progression_model"]["constitutional_office_transfer"] = True
        with self.assertRaises(mod.KamaIntegrityError):
            mod.validate(self.master, self.graph, self.rules)
    def test_authority_transfer_fails(self):
        self.master["progression_model"]["institutional_authority_transfer"] = True
        with self.assertRaises(mod.KamaIntegrityError):
            mod.validate(self.master, self.graph, self.rules)
    def test_siddhi_authority_fails(self):
        self.rules["vamacari"]["siddhi_grants_constitutional_authority"] = True
        with self.assertRaises(mod.KamaIntegrityError):
            mod.validate(self.master, self.graph, self.rules)
    def test_valid_relation_types(self):
        self.graph["relations"].append({"source":"B","target":"C","relation":"secondary"})
        mod.validate(self.master, self.graph, self.rules)

if __name__ == "__main__":
    unittest.main(verbosity=2)
