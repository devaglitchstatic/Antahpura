#!/usr/bin/env python3
"""
freeze_baseline.py — record the current verified state as
audit/BASELINE_V20.json.

Captures:
  - Audit summary at freeze time
  - SHA-256 + size of every canonical file
  - The 14-character roster with chub_card_ids
"""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AUDIT = ROOT / "audit" / "validation_results.json"
OUTPUT = ROOT / "audit" / "BASELINE_V20.json"

HASHED_FILES = [
    "characters/V17_1_CHARACTER_REGISTRY.json",
    "kalas/kala_system_v20.json",
    "kalas/character_kala_matrix.json",
    "kalas/kala_kama_linkage.json",
    "kalas/kala_prerequisites_graph.json",
    "kalas/kala_synergies.json",
    "kalas/kala_mastery_ladder.json",
    "kalas/kala_dimension_matrix.json",
    "kalas/KAMA_KALA_BRIDGE.json",
    "kama/MASTER_KINK_REGISTRY.json",
    "kama/KINK_RELATION_GRAPH.json",
    "relationships/relationship_system_v20.json",
    "world/offices.json",
    "world/ANTAHPURA_KAMA_SYSTEM_V20.json",
    "runtime/ANTAHPURA_RUNTIME_ENGINE_V20.json",
    "runtime/Antarvāṇī.json",
    "scenes/current_scene.json",
    "REPO_MANIFEST.json",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def main():
    if not AUDIT.exists():
        raise SystemExit(f"Audit report missing: {AUDIT}")
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    summary = audit.get("summary", {})

    hashes, missing = {}, []
    for rel in HASHED_FILES:
        p = ROOT / rel
        if not p.exists():
            missing.append(rel)
            continue
        hashes[rel] = {"sha256": sha256(p), "size_bytes": p.stat().st_size}

    registry = json.loads(
        (ROOT / "characters/V17_1_CHARACTER_REGISTRY.json")
        .read_text(encoding="utf-8"))
    characters = [
        {"id": c.get("id"),
         "chub_card_id": c.get("chub_card_id"),
         "display_name": c.get("display_name"),
         "office": c.get("office")}
        for c in registry.get("characters", [])
    ]

    baseline = {
        "schema": "antahpura.baseline",
        "version": "20.0",
        "frozen_at": datetime.now(timezone.utc).isoformat(),
        "description": (
            "Frozen reference baseline of the Antahpura repository. "
            "Hashes below are signatures of the canonical files as verified "
            "by audit_repo.py and smoke_test.py."
        ),
        "audit_summary": {
            "files_scanned":          summary.get("files_scanned"),
            "parse_errors":           summary.get("parse_errors"),
            "files_with_warnings":    summary.get("files_with_warnings"),
            "manifest_errors":        summary.get("manifest_errors"),
            "manifest_warnings":      summary.get("manifest_warnings"),
            "duplicate_schemas":      summary.get("duplicate_schemas"),
            "registries":             summary.get("registries"),
            "dangling_unique_counts": summary.get("dangling_unique_counts"),
        },
        "characters": characters,
        "character_count": len(characters),
        "canonical_file_hashes": hashes,
        "hashed_file_count": len(hashes),
        "missing_hashed_files": missing,
    }

    OUTPUT.write_text(
        json.dumps(baseline, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("=" * 60)
    print("BASELINE FROZEN")
    print("=" * 60)
    print(f"Output:         {OUTPUT.relative_to(ROOT)}")
    print(f"Frozen at:      {baseline['frozen_at']}")
    print(f"Characters:     {baseline['character_count']}")
    print(f"Hashed files:   {baseline['hashed_file_count']}")
    if missing:
        print(f"Missing:        {len(missing)}")
        for m in missing:
            print(f"  - {m}")
    print()
    for k, v in baseline["audit_summary"].items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()