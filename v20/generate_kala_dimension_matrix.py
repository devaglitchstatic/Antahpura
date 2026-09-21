#!/usr/bin/env python3
"""Derive kala_dimension_matrix.json from kala_system_v20.json."""
import json
from pathlib import Path

root = Path(".").resolve()
ks = json.loads((root / "kalas/kala_system_v20.json").read_text(encoding="utf-8"))

matrix = {}
observed = set()
for kid, kdata in ks.get("kalas", {}).items():
    dims = kdata.get("dimensions", {})
    matrix[kid] = dims
    observed.update(dims.keys())

out = {
    "schema": "antahpura.kala_dimension_matrix",
    "version": "20.1",
    "generated": "2026-09-19",
    "source": "kala_system_v20.json → kalas.*.dimensions",
    "dimensions_observed_in_kalas": sorted(observed),
    "matrix": matrix,
    "audit": {
        "total_kalas": len(matrix),
        "unique_dimensions": len(observed),
        "note": "Kala dimension vocabulary is independent of the 20 kama dimensions. Add a mapping layer later if needed."
    }
}

out_path = root / "kalas/kala_dimension_matrix.json"
out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Wrote {out_path}")
print(f"Kalas: {len(matrix)}, unique dims: {len(observed)}")