#!/usr/bin/env python3
"""
schema_version_autopatch.py — add placeholder 'schema' and 'version' fields to
JSON files that are missing them.

Reads audit/validation_results.json, patches only the files listed in
schema_version_gaps. Preserves existing fields. Dry-run by default.
"""

import argparse
import json
from pathlib import Path

ROOT = Path(".").resolve()
REPORT = ROOT / "audit" / "validation_results.json"


def infer_schema_from_path(rel: str) -> str:
    """Best-effort guess for a missing schema string from the file path."""
    parts = rel.split("/")
    if len(parts) >= 2:
        domain = parts[0]
        name = Path(parts[-1]).stem
        return f"antahpura.{domain}.{name}"
    return "antahpura.unknown"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    if not REPORT.exists():
        raise SystemExit("Run audit_repo.py first.")

    report = json.loads(REPORT.read_text(encoding="utf-8"))
    gaps = report.get("schema_version_gaps", {})

    targets = set()
    targets.update(gaps.get("missing_both", []))
    targets.update(gaps.get("missing_schema_only", []))
    targets.update(gaps.get("missing_version_only", []))

    if not targets:
        print("No files need patching.")
        return

    patched = 0
    for rel in sorted(targets):
        path = ROOT / rel
        if not path.exists():
            print(f"[skip-missing] {rel}")
            continue

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[skip-parse]   {rel} :: {e}")
            continue

        if not isinstance(data, dict):
            print(f"[skip-shape]   {rel} :: top-level is not an object")
            continue

        changes = []
        if "schema" not in data and "Schema" not in data:
            data["schema"] = infer_schema_from_path(rel)
            changes.append(f"schema={data['schema']}")
        if "version" not in data and "Version" not in data:
            data["version"] = "1.0"
            changes.append("version=1.0")

        if not changes:
            continue

        print(f"[{'APPLY' if args.apply else 'DRY'}] {rel} :: {' '.join(changes)}")
        if args.apply:
            path.write_text(
                json.dumps(data, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        patched += 1

    print()
    print(f"Files {'patched' if args.apply else 'to patch'}: {patched}")
    if not args.apply:
        print("Dry run only. Re-run with --apply to write.")


if __name__ == "__main__":
    main()