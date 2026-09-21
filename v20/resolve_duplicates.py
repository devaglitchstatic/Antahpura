#!/usr/bin/env python3
"""
resolve_duplicates.py — move stale duplicate files to archive/duplicates/,
and update REPO_MANIFEST.json to mark them role='archive'.

Reads duplicate_schemas from audit/validation_results.json.
Safe to run multiple times (idempotent).
"""

import json
import shutil
from pathlib import Path

ROOT = Path(".").resolve()
REPORT = ROOT / "audit" / "validation_results.json"
MANIFEST = ROOT / "REPO_MANIFEST.json"
ARCHIVE = ROOT / "archive" / "duplicates"

if not REPORT.exists():
    raise SystemExit(f"Run audit first. Missing: {REPORT}")

report = json.loads(REPORT.read_text(encoding="utf-8"))
manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

duplicates = report.get("duplicate_schemas", {})
to_archive = []

for schema, info in duplicates.items():
    if info.get("status") != "extra_copies":
        continue
    for rel in info.get("duplicates", []):
        to_archive.append(rel)

if not to_archive:
    print("No duplicate files to archive.")
    raise SystemExit(0)

ARCHIVE.mkdir(parents=True, exist_ok=True)
moved = 0
manifest_by_path = {f["path"]: f for f in manifest.get("files", [])}

for rel in sorted(set(to_archive)):
    src = ROOT / rel
    if not src.exists():
        print(f"[skip] missing: {rel}")
        continue

    dst = ARCHIVE / rel
    dst.parent.mkdir(parents=True, exist_ok=True)

    if dst.exists():
        print(f"[skip] already archived: {rel}")
    else:
        shutil.move(str(src), str(dst))
        moved += 1
        print(f"[moved] {rel} -> archive/duplicates/{rel}")

    # Update manifest: mark original as archived
    if rel in manifest_by_path:
        manifest_by_path[rel]["role"] = "archive"
        manifest_by_path[rel]["note"] = (
            "Duplicate of canonical copy. Moved to archive/duplicates/. "
            "Do not reference."
        )
    else:
        manifest["files"].append({
            "path": rel,
            "role": "archive",
            "domain": rel.split("/")[0],
            "schema": None,
            "version": None,
            "depends_on": [],
            "referenced_by": [],
            "reference_types": [],
            "note": "Duplicate of canonical copy. Moved to archive/duplicates/."
        })

    # Also declare the archived copy
    arc_rel = f"archive/duplicates/{rel}"
    if arc_rel not in manifest_by_path:
        manifest["files"].append({
            "path": arc_rel,
            "role": "archive",
            "domain": "archive",
            "schema": None,
            "version": None,
            "depends_on": [],
            "referenced_by": [],
            "reference_types": [],
            "note": f"Archived duplicate of {rel}."
        })
        manifest_by_path[arc_rel] = manifest["files"][-1]

manifest["files"].sort(key=lambda f: f["path"])
MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False),
                    encoding="utf-8")

print(f"\nMoved {moved} files to archive/duplicates/.")
print(f"Manifest updated: {MANIFEST}")
print("Re-run audit_repo.py to confirm duplicate_schemas drops to 0.")