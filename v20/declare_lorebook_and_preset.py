#!/usr/bin/env python3
"""
declare_lorebook_and_preset.py — one-shot script.

  1. Adds 'schema' and 'version' to:
       - lorebook/Antahpura V18.9 — Unified Lorebook.json
       - runtime/Antarvāṇī.json
  2. Adds both files to REPO_MANIFEST.json if not already present.

Safe to run multiple times.
"""

import json
from pathlib import Path

ROOT = Path(".").resolve()
MANIFEST = ROOT / "REPO_MANIFEST.json"

# (relative path, schema string, version string, role, domain, note)
TARGETS = [
    (
        "lorebook/Antahpura V18.9 — Unified Lorebook.json",
        "antahpura.lorebook.unified",
        "18.9",
        "canonical",
        "lorebook",
        "Live V18.9 unified lorebook. Supersedes the V17.1 placeholder in audit/.",
    ),
    (
        "runtime/Antarvāṇī.json",
        "antahpura.runtime.preset",
        "1.0",
        "canonical",
        "runtime",
        "Chat Completion preset for Antarvāṇī (Royal Chronicler).",
    ),
]


def add_fields(path: Path, schema: str, version: str) -> str:
    """Add schema/version if missing. Return a status string."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return f"parse error: {e}"
    if not isinstance(data, dict):
        return f"top-level is {type(data).__name__}, not object"

    changed = []
    if "schema" not in data and "Schema" not in data:
        data["schema"] = schema
        changed.append(f"schema={schema}")
    if "version" not in data and "Version" not in data:
        data["version"] = version
        changed.append(f"version={version}")

    if not changed:
        return "already has schema and version"

    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return "added " + ", ".join(changed)


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest_paths = {f["path"] for f in manifest.get("files", [])}

    print("=" * 60)
    print("DECLARE LOREBOOK AND PRESET")
    print("=" * 60)

    added = 0
    for rel, schema, version, role, domain, note in TARGETS:
        path = ROOT / rel

        if not path.exists():
            print(f"[missing] {rel}")
            continue

        status = add_fields(path, schema, version)
        print(f"[fields]  {rel} — {status}")

        if rel not in manifest_paths:
            manifest["files"].append({
                "path": rel,
                "role": role,
                "domain": domain,
                "schema": schema,
                "version": version,
                "depends_on": [],
                "referenced_by": [],
                "reference_types": [],
                "note": note,
            })
            manifest_paths.add(rel)
            added += 1
            print(f"[manifest] added {rel}")
        else:
            print(f"[manifest] already declared: {rel}")

    manifest["files"].sort(key=lambda f: f["path"])
    MANIFEST.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print()
    print(f"Added {added} entries to manifest.")
    print(f"Total manifest entries: {len(manifest['files'])}")


if __name__ == "__main__":
    main()