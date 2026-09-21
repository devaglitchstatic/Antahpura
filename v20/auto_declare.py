#!/usr/bin/env python3
"""
auto_declare.py — append every undeclared JSON file to REPO_MANIFEST.json
with role='stub'. Safe to run multiple times.
"""

import json
from pathlib import Path

SKIP_DIRS = {"node_modules", ".git", "dist", "build", "__pycache__",
             ".venv", "venv", ".mypy_cache", ".pytest_cache"}

root = Path(".").resolve()
manifest_path = root / "REPO_MANIFEST.json"

manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
declared = {f["path"] for f in manifest.get("files", [])}
added = 0

for p in sorted(root.rglob("*.json")):
    if any(part in SKIP_DIRS for part in p.parts):
        continue
    rel = str(p.relative_to(root)).replace("\\", "/")
    if rel in declared:
        continue

    parts = rel.split("/")
    domain = parts[0] if len(parts) > 1 else "root"

    manifest["files"].append({
        "path": rel,
        "role": "stub",
        "domain": domain,
        "schema": None,
        "version": None,
        "depends_on": [],
        "referenced_by": [],
        "reference_types": [],
        "note": "Auto-declared by auto_declare.py. Promote role when reviewed."
    })
    added += 1

manifest["files"].sort(key=lambda f: f["path"])
manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False),
                         encoding="utf-8")
print(f"Added {added} entries. Total declared: {len(manifest['files'])}")