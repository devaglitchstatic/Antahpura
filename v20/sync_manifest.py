#!/usr/bin/env python3
"""
sync_manifest.py — bring REPO_MANIFEST.json into agreement with disk (v2).

Adds:
  - All runtime/character_states/*.json as role 'derived'
  - antahpura.character_state_derived to multi_instance_schemas

Also declares any other undeclared JSON as role 'stub'.
Removes stale entries (except role='archive').
"""

import json
import os
from pathlib import Path

ROOT = Path(".").resolve()
MANIFEST = ROOT / "REPO_MANIFEST.json"

SKIP_DIRS = {"node_modules", ".git", "dist", "build", "__pycache__",
             ".venv", "venv", ".mypy_cache", ".pytest_cache",
             "archive", "runs"}

# Schemas explicitly allowed to appear in many files.
MULTI_INSTANCE = {
    "antahpura.character_state_derived",
}


def walk_json(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if fn.lower().endswith(".json"):
                yield Path(dirpath) / fn


def infer_role(rel: str) -> str:
    if rel.startswith("runtime/character_states/"):
        return "derived"
    if rel.startswith("runtime/runs/"):
        return "archive"
    if rel.startswith("runtime/") or rel.endswith("current_scene.json"):
        return "runtime_state"
    if rel.startswith("audit/"):
        return "canonical"
    return "stub"


def infer_domain(rel: str) -> str:
    parts = rel.split("/")
    return parts[0] if len(parts) > 1 else "root"


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    # 1. Remove stale entries (except archive)
    kept, removed = [], []
    for f in manifest.get("files", []):
        if f.get("role") == "archive":
            kept.append(f)
            continue
        if (ROOT / f["path"]).exists():
            kept.append(f)
        else:
            removed.append((f["path"], f.get("role", "unknown")))

    # 2. Add undeclared
    declared = {f["path"] for f in kept}
    added = []
    for path in sorted(walk_json(ROOT)):
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        if rel in declared or rel == "REPO_MANIFEST.json":
            continue
        kept.append({
            "path": rel,
            "role": infer_role(rel),
            "domain": infer_domain(rel),
            "schema": None,
            "version": None,
            "depends_on": [],
            "referenced_by": [],
            "reference_types": [],
            "note": "Auto-declared by sync_manifest.py v2.",
        })
        added.append(rel)
        declared.add(rel)

    # 3. Ensure multi_instance_schemas includes our derived set
    mis = set(manifest.get("multi_instance_schemas", []))
    mis |= MULTI_INSTANCE
    manifest["multi_instance_schemas"] = sorted(mis)

    kept.sort(key=lambda f: f["path"])
    manifest["files"] = kept
    MANIFEST.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("=" * 60)
    print("SYNC MANIFEST v2")
    print("=" * 60)
    print(f"Removed stale entries:    {len(removed)}")
    for p, role in removed:
        print(f"  - {p} (role={role})")
    print(f"Added undeclared files:   {len(added)}")
    for p in added:
        print(f"  + {p}")
    print(f"multi_instance_schemas:   {manifest['multi_instance_schemas']}")
    print(f"Total manifest entries:   {len(kept)}")


if __name__ == "__main__":
    main()