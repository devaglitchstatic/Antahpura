#!/usr/bin/env python3
"""
fix_kama_key.py - Rename top-level KINKS key to kamas in kama registry files.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FILES = [
    ROOT / "kama" / "kama_registry_v20.json",
    ROOT / "kama" / "MASTER_KINK_REGISTRY.json",
]

for p in FILES:
    if not p.exists():
        print(f"SKIP: {p.name} (not found)")
        continue
    with open(p, "r", encoding="utf-8-sig") as f:
        d = json.load(f)
    if "KINKS" in d and "kamas" not in d:
        d["kamas"] = d.pop("KINKS")
        with open(p, "w", encoding="utf-8") as f:
            json.dump(d, f, indent=2, ensure_ascii=False)
        print(f"FIXED: {p.name}  ({len(d['kamas'])} kamas moved KINKS -> kamas)")
    elif "kamas" in d:
        print(f"OK:    {p.name}  (already uses 'kamas' key)")
    else:
        print(f"WARN:  {p.name}  (no KINKS or kamas key found)")