#!/usr/bin/env python3
"""
derive_character_kama.py - BOM-safe version.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRICES = ROOT / "matrices"


def load(p):
    # utf-8-sig handles both BOM and non-BOM
    with open(p, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def compute():
    char_dims = load(MATRICES / "character_dimension_weights.json")["weights"]
    dim_kama = load(MATRICES / "dimension_kama_matrix.json")["matrix"]

    kama_dims = {}
    for dim, kamas in dim_kama.items():
        for kama, w in kamas.items():
            kama_dims.setdefault(kama, {})[dim] = w

    derived = {}
    for cid, dim_weights in char_dims.items():
        derived[cid] = {}
        for kama, dim_w in kama_dims.items():
            num = sum(dim_weights.get(d, 0.0) * w for d, w in dim_w.items())
            den = sum(dim_w.values()) or 1.0
            score = round(num / den, 4)

            if score >= 0.85:
                assoc = "role_owner"
            elif score >= 0.65:
                assoc = "thematic"
            elif score >= 0.45:
                assoc = "curiosity"
            elif score < 0.35:
                assoc = "unsupported"
            else:
                assoc = "unknown"

            derived[cid][kama] = {
                "score": score,
                "association": assoc,
                "derivation": dim_w,
                "status": "derived",
                "source_version": "V20"
            }

    out = {
        "schema": "antahpura.character_kama_derived",
        "version": "20.0",
        "generated_by": "scripts/derive_character_kama.py",
        "source_matrices": [
            "matrices/character_dimension_weights.json",
            "matrices/dimension_kama_matrix.json"
        ],
        "characters": derived
    }

    out_path = MATRICES / "character_kama_derived.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"WROTE: {out_path.relative_to(ROOT)}")
    print(f"  Characters: {len(derived)}")
    total_edges = sum(len(v) for v in derived.values())
    print(f"  Total character-kama edges: {total_edges}")


if __name__ == "__main__":
    compute()