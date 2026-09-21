#!/usr/bin/env python3
"""
generate_kink_relation_graph.py — derive KINK_RELATION_GRAPH.json from
MASTER_KINK_REGISTRY.json.

Every kink's taxonomy.similar/related/secondary becomes an entry in the
corresponding graph bucket. If those fields are empty in the registry,
the resulting graph is empty but structurally valid.

Output: registries/KINK_RELATION_GRAPH.json
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REGISTRY = ROOT / "kama" / "MASTER_KINK_REGISTRY.json"
OUT = ROOT / "registries" / "KINK_RELATION_GRAPH.json"

if not REGISTRY.exists():
    raise SystemExit(f"Registry not found: {REGISTRY}")

data = json.loads(REGISTRY.read_text(encoding="utf-8"))
kinks = data.get("KINKS", {})

similar: dict = {}
related: dict = {}
secondary: dict = {}

for kid, k in kinks.items():
    tax = k.get("taxonomy", {})
    s = tax.get("similar", [])
    r = tax.get("related", [])
    sec = tax.get("secondary", [])
    if isinstance(s, list) and s:
        similar[kid] = s
    if isinstance(r, list) and r:
        related[kid] = r
    if isinstance(sec, list) and sec:
        secondary[kid] = sec

out = {
    "schema": "antahpura.kink_relation_graph",
    "version": "1.0",
    "generated": "2026-09-20",
    "source": "MASTER_KINK_REGISTRY.json → KINKS.*.taxonomy",
    "similar": similar,
    "related": related,
    "secondary": secondary,
    "audit": {
        "total_kinks": len(kinks),
        "similar_edges": sum(len(v) for v in similar.values()),
        "related_edges": sum(len(v) for v in related.values()),
        "secondary_edges": sum(len(v) for v in secondary.values()),
    },
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

print(f"Wrote {OUT.relative_to(ROOT)}")
print(f"Kinks: {len(kinks)}")
print(f"similar:   {out['audit']['similar_edges']} edges across {len(similar)} kinks")
print(f"related:   {out['audit']['related_edges']} edges across {len(related)} kinks")
print(f"secondary: {out['audit']['secondary_edges']} edges across {len(secondary)} kinks")