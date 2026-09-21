#!/usr/bin/env python3
"""
audit_repo.py — Antahpura repository audit tool.

Version 1.9 (2026-09-20)
Changes vs 1.8:
  - detect_duplicate_schemas honors manifest['multi_instance_schemas'].
    Schemas listed there are expected to appear across many files and
    are not flagged as duplicates.

Usage:
    python audit_repo.py --root . --manifest REPO_MANIFEST.json --output audit/validation_results.json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHARACTER_PREFIXED = re.compile(r"^char_[a-z][a-z0-9_]{3,}$")
KALA = re.compile(r"^kala_[0-9]+$")
KAMA = re.compile(r"^[A-Z][A-Z0-9_]{3,}$")

KAMA_FALSE_POSITIVES = {
    "TRUE", "FALSE", "NULL", "NONE", "JSON", "UTF", "HTTP", "HTTPS",
    "OK", "ERROR", "WARN", "INFO", "DEBUG", "API", "URL", "URI",
    "GET", "POST", "PUT", "PATCH", "DELETE", "SCHEMA", "VERSION",
    "VALUE", "TYPE", "NAME", "UNKNOWN", "STOP", "GIVE", "FAST",
    "SSC", "RACK", "PRICK", "TIPP", "SSICK", "DEAR_MAN",
}


def normalize_character(value: str) -> str:
    return value[5:] if value.startswith("char_") else value


def is_kama_context(key_chain: tuple) -> bool:
    return any(isinstance(k, str) and "kama" in k.lower() for k in key_chain)


def load_json(path: Path):
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f), None
    except json.JSONDecodeError as e:
        return None, f"JSONDecodeError line {e.lineno} col {e.colno}: {e.msg}"
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


def walk_json(root: Path):
    skip = {
        "node_modules", ".git", "dist", "build", "__pycache__",
        ".venv", "venv", ".mypy_cache", ".pytest_cache",
        "archive", "runs",
    }
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip]
        for fn in filenames:
            if fn.lower().endswith(".json"):
                yield Path(dirpath) / fn


def extract_identity(data: Any):
    schema = version = None
    if isinstance(data, dict):
        schema = data.get("schema") or data.get("Schema")
        version = data.get("version") or data.get("Version")
    return schema, version


def load_registries(root: Path, manifest: dict):
    regs = {"characters": set(), "character_aliases": {},
            "kalas": set(), "kamas": set()}

    char_path = root / manifest["registries"]["characters"]
    if char_path.exists():
        data, _ = load_json(char_path)
        if isinstance(data, dict):
            block = data.get("characters")
            if isinstance(block, list):
                for item in block:
                    if not isinstance(item, dict):
                        continue
                    cid = item.get("id")
                    if isinstance(cid, str):
                        canon = normalize_character(cid)
                        regs["characters"].add(canon)
                        for alias in item.get("aliases", []) or []:
                            if isinstance(alias, str) and alias:
                                regs["character_aliases"][alias.lower()] = canon
                        for key in ("canonical_name", "display_name"):
                            v = item.get(key)
                            if isinstance(v, str) and v:
                                regs["character_aliases"][v.lower()] = canon
            elif isinstance(block, dict):
                for k, v in block.items():
                    if isinstance(k, str):
                        regs["characters"].add(normalize_character(k))
                    if isinstance(v, dict) and isinstance(v.get("id"), str):
                        regs["characters"].add(normalize_character(v["id"]))

    kala_path = root / manifest["registries"]["kalas"]
    if kala_path.exists():
        data, _ = load_json(kala_path)
        if isinstance(data, dict):
            block = data.get("kalas")
            if isinstance(block, dict):
                for k in block.keys():
                    if isinstance(k, str) and KALA.match(k):
                        regs["kalas"].add(k)
            elif isinstance(block, list):
                for item in block:
                    if isinstance(item, dict) and isinstance(item.get("id"), str):
                        regs["kalas"].add(item["id"])

    kama_path = root / manifest["registries"]["kamas"]
    if kama_path.exists():
        data, _ = load_json(kama_path)
        if isinstance(data, dict):
            for key in ("KINKS", "kamas", "kama_registry"):
                block = data.get(key)
                if isinstance(block, dict):
                    for k in block.keys():
                        if isinstance(k, str) and KAMA.match(k):
                            regs["kamas"].add(k)
                elif isinstance(block, list):
                    for item in block:
                        if isinstance(item, dict) and isinstance(item.get("id"), str):
                            regs["kamas"].add(item["id"])

    return regs


def resolve_character(value: str, regs: dict):
    canon = normalize_character(value)
    if canon in regs["characters"]:
        return canon
    lower = value.lower()
    if lower in regs["character_aliases"]:
        return regs["character_aliases"][lower]
    lower_canon = canon.lower()
    if lower_canon in regs["character_aliases"]:
        return regs["character_aliases"][lower_canon]
    return None


def collect_refs(node, path="$", key_chain=()):
    if isinstance(node, dict):
        for k, v in node.items():
            child_path = f"{path}.{k}"
            child_chain = key_chain + (k,) if isinstance(k, str) else key_chain

            if isinstance(k, str):
                if KALA.match(k):
                    yield ("kala", k, child_path)
                elif CHARACTER_PREFIXED.match(k):
                    yield ("character", normalize_character(k), child_path)

            if isinstance(v, str):
                if KALA.match(v):
                    yield ("kala", v, child_path)
                elif CHARACTER_PREFIXED.match(v):
                    yield ("character", normalize_character(v), child_path)
                elif (is_kama_context(child_chain) and KAMA.match(v)
                      and v not in KAMA_FALSE_POSITIVES):
                    yield ("kama", v, child_path)
            elif isinstance(v, list):
                for i, item in enumerate(v):
                    ip = f"{child_path}[{i}]"
                    if isinstance(item, str):
                        if KALA.match(item):
                            yield ("kala", item, ip)
                        elif CHARACTER_PREFIXED.match(item):
                            yield ("character", normalize_character(item), ip)
                        elif (is_kama_context(child_chain) and KAMA.match(item)
                              and item not in KAMA_FALSE_POSITIVES):
                            yield ("kama", item, ip)
                    else:
                        yield from collect_refs(item, ip, child_chain)
            elif isinstance(v, dict):
                yield from collect_refs(v, child_path, child_chain)
    elif isinstance(node, list):
        for i, item in enumerate(node):
            ip = f"{path}[{i}]"
            if isinstance(item, str):
                if KALA.match(item):
                    yield ("kala", item, ip)
                elif CHARACTER_PREFIXED.match(item):
                    yield ("character", normalize_character(item), ip)
                elif (is_kama_context(key_chain) and KAMA.match(item)
                      and item not in KAMA_FALSE_POSITIVES):
                    yield ("kama", item, ip)
            else:
                yield from collect_refs(item, ip, key_chain)


def check_file(path: Path, root: Path, regs: dict):
    rel = str(path.relative_to(root)).replace("\\", "/")
    result = {"path": rel, "ok": True, "errors": [], "warnings": [], "info": {}}

    data, err = load_json(path)
    if err:
        result["ok"] = False
        result["errors"].append({"check": "parse", "message": err})
        return result

    schema, version = extract_identity(data)
    result["info"]["schema"] = schema
    result["info"]["version"] = version

    if schema is None:
        result["warnings"].append({"check": "schema_presence", "message": "No 'schema'"})
    if version is None:
        result["warnings"].append({"check": "version_presence", "message": "No 'version'"})

    dangling = defaultdict(list)
    for kind, value, jpath in collect_refs(data):
        if kind == "character":
            if not regs["characters"]:
                continue
            if resolve_character(value, regs) is None:
                dangling["character"].append((value, jpath))
        elif kind == "kala":
            if regs["kalas"] and value not in regs["kalas"]:
                dangling["kala"].append((value, jpath))
        elif kind == "kama":
            if regs["kamas"] and value not in regs["kamas"]:
                dangling["kama"].append((value, jpath))

    for kind, items in dangling.items():
        result["warnings"].append({
            "check": "cross_reference",
            "kind": kind,
            "count": len(items),
            "items": [{"value": v, "at": p} for v, p in items],
        })

    return result


def check_manifest(root: Path, manifest: dict, actual_files: list):
    errors, warnings = [], []
    declared_at_all = {f["path"] for f in manifest.get("files", [])}
    declared_and_expected = {
        f["path"] for f in manifest.get("files", [])
        if f.get("role") != "archive"
    }
    actual = {str(p.relative_to(root)).replace("\\", "/") for p in actual_files}

    for m in sorted(declared_and_expected - actual):
        errors.append({"check": "manifest_missing_file",
                       "message": f"Declared but not on disk: {m}"})
    for u in sorted(actual - declared_at_all):
        warnings.append({"check": "undeclared_file",
                         "message": f"On disk but not declared: {u}"})
    return errors, warnings


def detect_duplicate_schemas(results: list, canonical_paths: dict,
                             multi_instance_schemas: set):
    by_schema = defaultdict(list)
    for r in results:
        s = r.get("info", {}).get("schema")
        if s:
            by_schema[s].append(r["path"])

    out = {}
    for s, paths in by_schema.items():
        if s in multi_instance_schemas:
            continue  # explicitly allowed to appear in multiple files
        if len(paths) < 2:
            continue
        canon = canonical_paths.get(s)
        if canon:
            canon_present = canon in paths
            extras = [p for p in paths if p != canon]
            out[s] = {
                "canonical": canon,
                "canonical_present": canon_present,
                "duplicates": extras,
                "all_paths": paths,
                "status": ("ok" if canon_present and not extras
                           else "extra_copies" if canon_present
                           else "canonical_missing"),
            }
        else:
            out[s] = {
                "canonical": None,
                "canonical_present": False,
                "duplicates": paths,
                "all_paths": paths,
                "status": "no_canonical_declared",
            }
    return out


def build_dangling_summary(results: list):
    summary = {"character": Counter(), "kala": Counter(), "kama": Counter()}
    for r in results:
        for w in r["warnings"]:
            if w.get("check") != "cross_reference":
                continue
            for item in w.get("items", []):
                summary[w["kind"]][item["value"]] += 1
    return {k: dict(v.most_common()) for k, v in summary.items()}


def build_schema_version_gaps(results: list):
    no_schema, no_version, no_both = [], [], []
    for r in results:
        s = r.get("info", {}).get("schema")
        v = r.get("info", {}).get("version")
        if s is None and v is None:
            no_both.append(r["path"])
        elif s is None:
            no_schema.append(r["path"])
        elif v is None:
            no_version.append(r["path"])
    return {
        "missing_schema_only": sorted(no_schema),
        "missing_version_only": sorted(no_version),
        "missing_both": sorted(no_both),
        "total_missing_schema": len(no_schema) + len(no_both),
        "total_missing_version": len(no_version) + len(no_both),
    }


def build_dangling_file_index(results: list):
    index = {"character": defaultdict(list), "kala": defaultdict(list),
             "kama": defaultdict(list)}
    for r in results:
        for w in r["warnings"]:
            if w.get("check") != "cross_reference":
                continue
            for item in w.get("items", []):
                index[w["kind"]][item["value"]].append({
                    "file": r["path"], "at": item["at"],
                })
    return {k: dict(v) for k, v in index.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--manifest", default="REPO_MANIFEST.json")
    ap.add_argument("--output", default="audit/validation_results.json")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    manifest_path = root / args.manifest
    if not manifest_path.exists():
        print(f"ERROR: manifest not found: {manifest_path}", file=sys.stderr)
        sys.exit(2)

    manifest, merr = load_json(manifest_path)
    if merr:
        print(f"ERROR: manifest parse failed: {merr}", file=sys.stderr)
        sys.exit(2)

    regs = load_registries(root, manifest)
    files = sorted(walk_json(root))

    results = []
    parse_errors = 0
    for p in files:
        r = check_file(p, root, regs)
        results.append(r)
        if not r["ok"]:
            parse_errors += 1

    manifest_errors, manifest_warnings = check_manifest(root, manifest, files)
    canonical_paths = manifest.get("canonical_paths", {})
    multi_instance_schemas = set(manifest.get("multi_instance_schemas", []))
    duplicates = detect_duplicate_schemas(results, canonical_paths, multi_instance_schemas)
    dangling_summary = build_dangling_summary(results)
    schema_version_gaps = build_schema_version_gaps(results)
    dangling_index = build_dangling_file_index(results)

    report = {
        "schema": "antahpura.validation_results",
        "version": "1.9",
        "generated": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "manifest": args.manifest,
        "summary": {
            "files_scanned": len(files),
            "parse_errors": parse_errors,
            "files_with_warnings": sum(1 for r in results if r["warnings"]),
            "manifest_errors": len(manifest_errors),
            "manifest_warnings": len(manifest_warnings),
            "duplicate_schemas": len(duplicates),
            "registries": {
                "characters_canonical": len(regs["characters"]),
                "characters_aliases": len(regs["character_aliases"]),
                "kalas_loaded": len(regs["kalas"]),
                "kamas_loaded": len(regs["kamas"]),
            },
            "dangling_unique_counts": {
                "character": len(dangling_summary["character"]),
                "kala": len(dangling_summary["kala"]),
                "kama": len(dangling_summary["kama"]),
            },
        },
        "manifest_errors": manifest_errors,
        "manifest_warnings": manifest_warnings,
        "duplicate_schemas": duplicates,
        "dangling_summary": dangling_summary,
        "dangling_file_index": dangling_index,
        "schema_version_gaps": schema_version_gaps,
        "files": results,
    }

    out_path = Path(args.output)
    if not out_path.is_absolute():
        out_path = root / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("=" * 60)
    print("ANTAHPURA REPO AUDIT")
    print("=" * 60)
    print(f"Root:              {root}")
    print(f"Files scanned:     {len(files)}")
    print(f"Parse errors:      {parse_errors}")
    print(f"Files w/ warnings: {report['summary']['files_with_warnings']}")
    print(f"Manifest errors:   {len(manifest_errors)}")
    print(f"Manifest warnings: {len(manifest_warnings)}")
    print(f"Duplicate schemas: {len(duplicates)}")
    print("Registries loaded:")
    print(f"  characters (canonical): {len(regs['characters'])}")
    print(f"  characters (aliases):   {len(regs['character_aliases'])}")
    print(f"  kalas:                  {len(regs['kalas'])}")
    print(f"  kamas:                  {len(regs['kamas'])}")
    print("-" * 60)
    print("Dangling unique IDs:")
    print(f"  characters: {report['summary']['dangling_unique_counts']['character']}")
    print(f"  kalas:      {report['summary']['dangling_unique_counts']['kala']}")
    print(f"  kamas:      {report['summary']['dangling_unique_counts']['kama']}")
    print("-" * 60)
    print("Schema/version gaps:")
    print(f"  missing schema:  {schema_version_gaps['total_missing_schema']}")
    print(f"  missing version: {schema_version_gaps['total_missing_version']}")
    print("=" * 60)
    print(f"Report: {out_path}")

    if parse_errors:
        sys.exit(2)
    if manifest_errors:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()