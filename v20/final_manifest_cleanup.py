#!/usr/bin/env python3
"""
final_manifest_cleanup.py — one-shot cleanup of REPO_MANIFEST.json.

Removes every entry whose file is missing from disk (regardless of role),
adds every JSON file on disk that isn't yet declared. Safe and idempotent.
"""

import json
import os
from pathlib import Path

SKIP_DIRS = {"node_modules", ".git", "dist", "build", "__pycache__",
             ".venv", "venv", ".mypy_cache", ".pytest_cache", "archive"}

ROOT = Path(".").resolve()
MANIFEST = ROOT / "REPO_MANIFEST.json"


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    # 1. Keep only entries whose file exists on disk
    kept, removed = [], []
    for f in manifest.get("files", []):
        p = f["path"]
        if (ROOT / p).exists():
            kept.append(f)
        else:
            removed.append((p, f.get("role", "unknown")))

    # 2. Add undeclared files
    declared = {f["path"] for f in kept}
    added = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if not fn.lower().endswith(".json"):
                continue
            full = Path(dirpath) / fn
            rel = str(full.relative_to(ROOT)).replace("\\", "/")
            if rel in declared or rel == "REPO_MANIFEST.json":
                continue
            kept.append({
                "path": rel,
                "role": "stub",
                "domain": rel.split("/")[0] if "/" in rel else "root",
                "schema": None,
                "version": None,
                "depends_on": [],
                "referenced_by": [],
                "reference_types": [],
                "note": "Auto-declared by final_manifest_cleanup.py."
            })
            added.append(rel)

    kept.sort(key=lambda f: f["path"])
    manifest["files"] = kept
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False),
                        encoding="utf-8")

    print("=" * 60)
    print("FINAL MANIFEST CLEANUP")
    print("=" * 60)
    print(f"Removed stale entries:   {len(removed)}")
    for p, role in removed:
        print(f"  - {p} (role={role})")
    print(f"Added undeclared files:  {len(added)}")
    for p in added:
        print(f"  + {p}")
    print(f"Total manifest entries:  {len(kept)}")


if __name__ == "__main__":
    main()