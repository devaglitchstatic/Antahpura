#!/usr/bin/env python3
"""
diagnose_dangling.py — print every dangling reference with its file and JSON path.
"""

import json
from pathlib import Path

report = json.loads(Path("audit/validation_results.json").read_text(encoding="utf-8"))
idx = report.get("dangling_file_index", {})

for kind, items in idx.items():
    if not items:
        continue
    print(f"=== {kind.upper()} ({len(items)} unique IDs) ===")
    for value, hits in items.items():
        print(f"  {value}  ({len(hits)} refs)")
        for h in hits:
            print(f"      {h['file']}")
            print(f"          at {h['at']}")
    print()