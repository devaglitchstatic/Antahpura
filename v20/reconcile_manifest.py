#!/usr/bin/env python3
"""
reconcile_manifest.py — bring REPO_MANIFEST.json into full agreement with disk.

Actions:
  1. Remove manifest entries whose files no longer exist (excluding role='archive')
  2. Add entries for files on disk that are not declared
  3. Add canonical_paths entries for duplicate schemas, when unambiguous
  4. Archive stale duplicate files (move to archive/duplicates/) when a canonical
     is declared and the duplicate lives in a known legacy folder

Safe to run multiple times. Idempotent.
"""

import json
import shutil
from collections import defaultdict
from pathlib import Path

SKIP_DIRS = {"node_modules", ".git", "dist", "build", "__pycache__",
             ".venv", "venv", ".mypy_cache", ".pytest_cache", "archive"}

# Legacy folders that hold duplicates of canonical files.
LEGACY_ROOTS = ("canon", "matrices", "location", "runtime-replayed", "world/schema.json")


def walk_json(root: Path):
    import os
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if fn.lower().endswith(".json"):
                yield Path(dirpath) / fn


def infer_role(path_str: str) -> str:
    if "/runtime/" in path_str or path_str.endswith("current_scene.json"):
        return "runtime_state"
    if path_str.startswith("archive/"):
        return "archive"
    return "stub"


def infer_domain(path_str: str) -> str:
    parts = path_str.split("/")
    return parts[0] if len(parts) > 1 else "root"


def main():
    root = Path(".").resolve()
    manifest_path = root / "REPO_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    # --- 1. Remove stale entries ---
    kept, removed = [], []
    for f in manifest.get("files", []):
        p = f["path"]
        if f.get("role") == "archive":
            kept.append(f)
            continue
        if (root / p).exists():
            kept.append(f)
        else:
            removed.append(p)

    # --- 2. Add undeclared files ---
    declared = {f["path"] for f in kept}
    added = []
    for path in sorted(walk_json(root)):
        rel = str(path.relative_to(root)).replace("\\", "/")
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
            "note": "Auto-declared by reconcile_manifest.py."
        })
        added.append(rel)

    # --- 3. Declare canonical paths for duplicate schemas ---
    canonical_paths = manifest.get("canonical_paths", {})

    # kala_dimension_matrix: kalas/ is canonical, matrices/ is stale
    canonical_paths.setdefault(
        "antahpura.kala_dimension_matrix",
        "kalas/kala_dimension_matrix.json"
    )

    # --- 4. Archive stale duplicate files ---
    by_schema = defaultdict(list)
    for f in kept:
        rel = f["path"]
        if not rel.endswith(".json"):
            continue
        full = root / rel
        if not full.exists():
            continue
        try:
            data = json.loads(full.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(data, dict):
            s = data.get("schema")
            if s:
                by_schema[s].append(rel)

    archived = []
    manifest_by_path = {f["path"]: f for f in kept}
    for schema, paths in by_schema.items():
        if len(paths) < 2:
            continue
        canon = canonical_paths.get(schema)
        if not canon or canon not in paths:
            continue
        for rel in paths:
            if rel == canon:
                continue
            # Only archive if the duplicate lives in a legacy root
            if not any(rel.startswith(r) for r in LEGACY_ROOTS):
                continue

            src = root / rel
            dst = root / "archive" / "duplicates" / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            if src.exists() and not dst.exists():
                shutil.move(str(src), str(dst))
                archived.append(rel)
                print(f"[archived] {rel} -> archive/duplicates/{rel}")

            # Update manifest
            if rel in manifest_by_path:
                manifest_by_path[rel]["role"] = "archive"
                manifest_by_path[rel]["note"] = (
                    f"Duplicate of {canon}. Moved to archive/duplicates/."
                )

    kept.sort(key=lambda f: f["path"])
    manifest["files"] = kept
    manifest["canonical_paths"] = canonical_paths
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("=" * 60)
    print("MANIFEST RECONCILIATION")
    print("=" * 60)
    print(f"Removed stale entries:     {len(removed)}")
    for r in removed:
        print(f"  - {r}")
    print(f"Added undeclared files:    {len(added)}")
    for a in added:
        print(f"  + {a}")
    print(f"Archived duplicate files:  {len(archived)}")
    print(f"Total manifest entries:    {len(kept)}")
    print(f"Canonical paths declared:  {len(canonical_paths)}")


if __name__ == "__main__":
    main()