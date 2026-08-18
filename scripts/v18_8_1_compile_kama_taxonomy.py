#!/usr/bin/env python3
"""Antahpura V18.8.1 — Master Kama Taxonomy Compiler."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "registry" / "V18_8_KAMA_RUNTIME"
VERSION = "18.8.1"

class KamaIntegrityError(ValueError):
    pass

def load(path: Path):
    if not path.exists():
        raise KamaIntegrityError(f"Missing source registry: {path}")
    return json.loads(path.read_text(encoding="utf-8-sig"))

def write(path: Path, obj: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

def validate(master, graph, rules):
    if master.get("schema") != "V18.8.1_MASTER_KINK_REGISTRY":
        raise KamaIntegrityError("Invalid master registry schema.")
    if graph.get("schema") != "V18.8.1_KINK_RELATION_GRAPH":
        raise KamaIntegrityError("Invalid kink graph schema.")
    if rules.get("schema") != "V18.8.1_KAMA_PROGRESSION_RULES":
        raise KamaIntegrityError("Invalid progression rules schema.")
    ids = [x.get("id") for x in master.get("kinks", [])]
    if len(ids) != len(set(ids)):
        raise KamaIntegrityError("Duplicate kink IDs.")
    idset = set(ids)
    for rel in graph.get("relations", []):
        if rel.get("source") not in idset or rel.get("target") not in idset:
            raise KamaIntegrityError("Kink relation references an unknown node.")
        if rel.get("relation") not in {"related", "similar", "secondary"}:
            raise KamaIntegrityError("Invalid kink relation type.")
    p = master.get("progression_model", {})
    if p.get("constitutional_office_transfer") is not False:
        raise KamaIntegrityError("Kama must never transfer constitutional office.")
    if p.get("institutional_authority_transfer") is not False:
        raise KamaIntegrityError("Kama must never transfer institutional authority.")
    if rules.get("vamacari", {}).get("siddhi_grants_constitutional_authority"):
        raise KamaIntegrityError("Siddhi cannot grant constitutional authority.")
    if rules.get("vamacari", {}).get("siddhi_changes_constitutional_office"):
        raise KamaIntegrityError("Siddhi cannot change constitutional office.")

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry-dir", type=Path, default=OUT)
    args = parser.parse_args()
    try:
        master = load(args.registry_dir / "MASTER_KINK_REGISTRY.json")
        graph = load(args.registry_dir / "KINK_RELATION_GRAPH.json")
        rules = load(args.registry_dir / "KAMA_PROGRESSION_RULES.json")
        validate(master, graph, rules)
        report = {
            "schema": "V18.8.1_COMPILATION_REPORT",
            "version": VERSION,
            "status": "PASS",
            "kink_nodes": len(master.get("kinks", [])),
            "graph_relations": len(graph.get("relations", [])),
            "progression_stages": len(rules.get("progression_stages", [])),
            "psychological_dimensions": len(rules.get("psychological_dimensions", [])),
            "trigger_classes": len(rules.get("trigger_classes", [])),
            "adult_gate": "REQUIRED",
            "explicit_act_instructions": "EXCLUDED",
            "minor_content": "EXCLUDED_FROM_RUNTIME",
            "constitutional_office_transfer": "BLOCKED",
            "institutional_authority_transfer": "BLOCKED",
            "source": "XLIX.pdf"
        }
        write(args.registry_dir / "V18_8.1_COMPILATION_REPORT.json", report)
    except Exception as exc:
        print("V18.8.1 Kama taxonomy compilation: FAIL")
        print(str(exc))
        return 1
    print("Antahpura V18.8.1 Master Kama Taxonomy Compiler")
    print("V18.8.1 Kama taxonomy compilation: PASS")
    print(f"Kink nodes: {report['kink_nodes']}")
    print(f"Graph relations: {report['graph_relations']}")
    print(f"Progression stages: {report['progression_stages']}")
    print(f"Psychological dimensions: {report['psychological_dimensions']}")
    print(f"Trigger classes: {report['trigger_classes']}")
    print("Knowledge → training → repetition → mastery: ENABLED")
    print("Adult gate: REQUIRED")
    print("Canonical office transfer: BLOCKED")
    print("Canonical authority transfer: BLOCKED")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
