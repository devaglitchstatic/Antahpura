#!/usr/bin/env python3
"""
final_two_edits.py — clean up the last two manifest issues.

  1. Remove the stale entry for archive/memories.json
  2. Add the undeclared entry for audit/Antahpura_V17_1_Lorebook.source.json
"""

import json
from pathlib import Path

ROOT = Path(".").resolve()
MANIFEST = ROOT / "REPO_MANIFEST.json"

STALE_ENTRY = "archive/memories.json"
UNDECLARED_ENTRY = {
    "path": "audit/Antahpura_V17_1_Lorebook.source.json",
    "role": "archive",
    "domain": "audit",
    "schema": "antahpura.audit.Antahpura_V17_1_Lorebook.source",
    "version": "1.0",
    "depends_on": [],
    "referenced_by": [],
    "reference_types": [],
    "note": "V17.1 lorebook source. Historical reference only.",
}


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    # 1. Remove stale entry
    before = len(manifest["files"])
    manifest["files"] = [
        f for f in manifest["files"]
        if f["path"] != STALE_ENTRY
    ]
    removed = before - len(manifest["files"])

    # 2. Add undeclared entry if not present
    existing_paths = {f["path"] for f in manifest["files"]}
    added = 0
    if UNDECLARED_ENTRY["path"] not in existing_paths:
        manifest["files"].append(UNDECLARED_ENTRY)
        added = 1

    manifest["files"].sort(key=lambda f: f["path"])
    MANIFEST.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("=" * 60)
    print("FINAL TWO EDITS")
    print("=" * 60)
    print(f"Removed stale entries:   {removed}")
    if removed:
        print(f"  - {STALE_ENTRY}")
    print(f"Added undeclared:        {added}")
    if added:
        print(f"  + {UNDECLARED_ENTRY['path']}")
    print(f"Total manifest entries:  {len(manifest['files'])}")


if __name__ == "__main__":
    main()