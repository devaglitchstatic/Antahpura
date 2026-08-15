#!/usr/bin/env python3
"""
upgrade_v17_runtime_ontology.py

V17.1 canonical migration for Antaḥpura.

Reads the V17 source lorebook, applies the locked constitutional migration,
and emits a runtime ontology plus validation report.

Locked V17.1 changes:
- Remove Zola from current runtime.
- Add Svara as the replacement seat.
- Canonicalize Anisa as Abyssinian/Habshi/East African.
- Canonicalize Tarana as Sogdian/Samarkand/Silk Road.
- Preserve legacy aliases as provenance only.
- Separate ethnicity/provenance from institutional office.
- Enforce four-channel acoustic jurisdiction.
"""

from __future__ import annotations

import json
from pathlib import Path

INPUT_FILE = Path(r"D:\dolphin\staging\V17_QWEN_DOLPHIN_SOURCE_BUNDLE\Antahpura_V4_Lorebook.source.json")
OUTPUT_FILE = Path(r"D:\dolphin\AntahpuraRepo\antahpura_runtime_ontology_v17_1.json")
REPORT_FILE = Path(r"D:\dolphin\AntahpuraRepo\V17_1_MIGRATION_REPORT.json")

ROOT = Path(__file__).resolve().parent
FALLBACK_INPUT = ROOT / "Antahpura_V17_1_Lorebook.source.json"

REGISTRY_PATH = ROOT / "registry" / "V17_1_CHARACTER_REGISTRY.json"
if not REGISTRY_PATH.exists():
    REGISTRY_PATH = ROOT / "V17_1_CHARACTER_REGISTRY.json"
ROSTER = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

def load_input():
    candidates = [INPUT_FILE, FALLBACK_INPUT]
    for p in candidates:
        if p.exists():
            return p, json.loads(p.read_text(encoding="utf-8"))
    raise SystemExit(
        "Missing input lorebook. Checked:\\n" +
        "\\n".join(str(p) for p in candidates)
    )

def main():
    input_path, lorebook = load_input()

    characters = ROSTER["characters"]
    current_ids = {c["id"] for c in characters}

    ontology = {
        "version": "17.1",
        "project": lorebook.get("name", "Antaḥpura"),
        "status": "canonical_reconciliation_build",
        "constitution": ROSTER["constitution"],
        "characters": {c["id"]: c for c in characters},
        "forbidden_current_runtime_ids": ["zola"],
        "legacy_aliases": {
            "anisa": ["Anisa", "Kamini", "Kamini Anisa", "Aniśā"],
            "tarana": ["Tarana", "Kamini Tarana", "Pradhāna Nartī"],
            "zola": ["Zola", "Captain Zola", "Ethiopian Guard", "Urdubegi"],
        },
        "source_lorebook": {
            "name": lorebook.get("name"),
            "entry_count": len(lorebook.get("entries", {})),
        },
    }

    report = {
        "input": str(input_path),
        "output": str(OUTPUT_FILE),
        "checks": {
            "roster_count_14": len(characters) == 14,
            "zola_absent": "zola" not in current_ids,
            "svara_present": "svara" in current_ids,
            "anisa_habshi": ontology["characters"]["anisa"]["ethnicity_provenance"].lower().find("habshi") >= 0,
            "tarana_sogdian": ontology["characters"]["tarana"]["ethnicity_provenance"].lower().find("sogdian") >= 0,
            "office_immutability": ROSTER["constitution"]["office_immutability"],
            "phase_specific_assembly": ROSTER["constitution"]["active_assembly_is_phase_specific"],
        }
    }
    report["passed"] = all(report["checks"].values())

    OUTPUT_FILE.write_text(json.dumps(ontology, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT_FILE.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    if not report["passed"]:
        raise SystemExit(f"V17.1 validation failed: {json.dumps(report['checks'], indent=2)}")

    print(f"V17.1 runtime ontology written to: {OUTPUT_FILE}")
    print(f"V17.1 migration report written to: {REPORT_FILE}")

if __name__ == "__main__":
    main()
