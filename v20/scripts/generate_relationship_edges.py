#!/usr/bin/env python3
"""
generate_relationship_edges.py
Generates relationships/relationship_edges.json with all 182 directed edges
for the 14 canonical characters. Deterministic and idempotent.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "relationships" / "relationship_edges.json"

CHARACTERS = [
    "char_maha_deva", "char_kumari_rati", "char_padma", "char_champa",
    "char_anisa", "char_shrinagar", "char_tarana", "char_roxana",
    "char_jahzara", "char_altani", "char_sevda", "char_malika",
    "char_reva", "char_svara",
]

BASE = {
    "a": 50, "t": 40, "r": 50, "o": 20, "rv": 5, "ly": 30,
    "c": 30, "f": 10, "d": 15, "rs": 3, "fm": 15,
}

# Specific pair rules. First match wins per direction.
# Format: (from_pattern, to_pattern, deltas) — "any" matches any character.
RULES = [
    # Sovereign relations
    ("char_maha_deva", "any",           {"t":+30,"r":+25,"o":-5,"ly":+40,"f":+15,"c":-10,"d":-5,"fm":+20}),
    ("any",            "char_maha_deva",{"a":+5,"t":+25,"r":+30,"o":+35,"ly":+40,"c":-10,"f":+15,"d":+20,"fm":+25}),

    # Kumari_rati <-> Padma (very close)
    ("char_kumari_rati","char_padma",   {"a":+30,"t":+40,"r":+20,"o":+25,"ly":+50,"c":+20,"f":-5,"d":+20,"fm":+60}),
    ("char_padma",     "char_kumari_rati",{"a":+40,"t":+50,"r":+35,"o":+70,"ly":+65,"c":+20,"d":+55,"fm":+70}),

    # Kumari_rati <-> Champa
    ("char_kumari_rati","char_champa",  {"a":+25,"t":+40,"r":+10,"o":+15,"ly":+45,"c":+30,"f":-5,"d":+5,"fm":+55}),
    ("char_champa",    "char_kumari_rati",{"a":+30,"t":+50,"r":+30,"o":+65,"ly":+55,"c":+20,"d":+40,"fm":+60}),

    # Padma <-> Champa
    ("char_padma",     "char_champa",   {"a":+28,"t":+45,"r":+15,"o":+45,"ly":+52,"c":+30,"f":-5,"d":+25,"fm":+60}),
    ("char_champa",    "char_padma",    {"a":+32,"t":+48,"r":+20,"o":+40,"ly":+55,"c":+25,"f":-5,"d":+40,"fm":+63}),

    # Military triad (Roxana / Jahzara / Altani)
    ("char_roxana",    "char_jahzara",  {"a":+12,"t":+35,"r":+35,"o":+35,"rv":+3,"ly":+42,"c":+10,"f":+3,"d":+10,"fm":+42}),
    ("char_jahzara",   "char_roxana",   {"a":+10,"t":+38,"r":+38,"o":+42,"rv":+2,"ly":+45,"c":+8,"f":+5,"d":+15,"fm":+38}),
    ("char_roxana",    "char_altani",   {"a":+10,"t":+35,"r":+38,"o":+30,"rv":+5,"ly":+40,"c":+8,"f":+3,"d":+8,"fm":+38}),
    ("char_altani",    "char_roxana",   {"a":+8,"t":+38,"r":+40,"o":+40,"rv":+3,"ly":+42,"c":+5,"f":+5,"d":+12,"fm":+35}),
    ("char_jahzara",   "char_altani",   {"a":+18,"t":+42,"r":+32,"o":+30,"rv":+2,"ly":+42,"c":+15,"f":0,"d":+8,"fm":+48}),
    ("char_altani",    "char_jahzara",  {"a":+15,"t":+40,"r":+30,"o":+28,"rv":+2,"ly":+40,"c":+12,"f":+2,"d":+8,"fm":+45}),

    # Administrative
    ("char_anisa",     "char_malika",   {"a":+8,"t":+32,"r":+32,"o":+20,"rv":+3,"ly":+35,"c":+15,"f":+3,"d":+10,"fm":+45}),
    ("char_malika",    "char_anisa",    {"a":+5,"t":+35,"r":+35,"o":+18,"rv":+2,"ly":+35,"c":+12,"f":+5,"d":+12,"fm":+42}),

    # Performance trio
    ("char_shrinagar", "char_tarana",   {"a":+18,"t":+32,"r":+32,"o":+8,"rv":+3,"ly":+32,"c":+35,"f":-5,"d":+5,"fm":+45}),
    ("char_tarana",    "char_shrinagar",{"a":+22,"t":+30,"r":+30,"o":+5,"rv":+5,"ly":+30,"c":+40,"f":-5,"d":+5,"fm":+48}),
    ("char_shrinagar", "char_svara",    {"a":+15,"t":+30,"r":+32,"o":+8,"rv":+5,"ly":+32,"c":+40,"f":-5,"d":+5,"fm":+42}),
    ("char_svara",     "char_shrinagar",{"a":+18,"t":+32,"r":+34,"o":+6,"rv":+4,"ly":+35,"c":+42,"f":-5,"d":+6,"fm":+45}),
    ("char_tarana",    "char_svara",    {"a":+22,"t":+34,"r":+32,"o":+6,"rv":+3,"ly":+35,"c":+38,"f":-5,"d":+5,"fm":+48}),
    ("char_svara",     "char_tarana",   {"a":+20,"t":+32,"r":+34,"o":+5,"rv":+2,"ly":+38,"c":+35,"f":-5,"d":+4,"fm":+45}),

    # Cipher pair
    ("char_reva",      "char_anisa",    {"a":+18,"t":+36,"r":+32,"o":+22,"rv":+3,"ly":+38,"c":+42,"f":-3,"d":+10,"fm":+48}),
    ("char_anisa",     "char_reva",     {"a":+15,"t":+38,"r":+32,"o":+18,"rv":+2,"ly":+40,"c":+40,"f":-3,"d":+12,"fm":+45}),

    # Reva <-> Shrinagar
    ("char_reva",      "char_shrinagar",{"a":+20,"t":+34,"r":+30,"o":+10,"rv":+2,"ly":+34,"c":+35,"f":-5,"d":+8,"fm":+48}),
    ("char_shrinagar", "char_reva",     {"a":+22,"t":+32,"r":+32,"o":+8,"rv":+3,"ly":+36,"c":+38,"f":-5,"d":+8,"fm":+45}),

    # Sevda <-> Jahzara
    ("char_sevda",     "char_jahzara",  {"a":+10,"t":+32,"r":+28,"o":+25,"rv":+2,"ly":+36,"c":+22,"f":+2,"d":+10,"fm":+42}),
    ("char_jahzara",   "char_sevda",    {"a":+8,"t":+34,"r":+30,"o":+28,"rv":+2,"ly":+38,"c":+20,"f":+3,"d":+12,"fm":+40}),

    # Sevda <-> Reva
    ("char_sevda",     "char_reva",     {"a":+14,"t":+36,"r":+30,"o":+20,"rv":+2,"ly":+36,"c":+30,"f":+2,"d":+12,"fm":+44}),
    ("char_reva",      "char_sevda",    {"a":+12,"t":+38,"r":+30,"o":+18,"rv":+2,"ly":+38,"c":+32,"f":+2,"d":+10,"fm":+42}),

    # Kumari_rati toward / from others
    ("char_kumari_rati","any",          {"a":+15,"t":+22,"r":+18,"o":+15,"ly":+28,"c":+8,"f":-3,"d":+5,"fm":+30}),
    ("any",            "char_kumari_rati",{"a":+18,"t":+28,"r":+25,"o":+32,"ly":+35,"c":+12,"f":+5,"d":+15,"fm":+35}),

    # Shrinagar toward / from others
    ("char_shrinagar", "any",           {"a":+10,"t":+25,"r":+30,"o":+15,"ly":+28,"c":+20,"d":+5,"fm":+35}),
    ("any",            "char_shrinagar",{"a":+12,"t":+28,"r":+32,"o":+15,"ly":+30,"c":+22,"d":+8,"fm":+38}),

    # Roxana toward / from others
    ("char_roxana",    "any",           {"a":+5,"t":+25,"r":+30,"o":+15,"ly":+28,"c":+8,"f":+2,"d":+5,"fm":+30}),
    ("any",            "char_roxana",   {"a":+5,"t":+28,"r":+35,"o":+22,"ly":+32,"c":+8,"f":+8,"d":+10,"fm":+32}),

    # Jahzara toward / from others
    ("char_jahzara",   "any",           {"a":+5,"t":+25,"r":+28,"o":+18,"ly":+30,"c":+8,"f":+2,"d":+8,"fm":+30}),
    ("any",            "char_jahzara",  {"a":+5,"t":+25,"r":+30,"o":+22,"ly":+32,"c":+8,"f":+5,"d":+10,"fm":+32}),

    # Altani toward / from others
    ("char_altani",    "any",           {"a":0,"t":+20,"r":+28,"o":+12,"ly":+25,"c":+3,"d":+5,"fm":+20}),
    ("any",            "char_altani",   {"a":+2,"t":+20,"r":+28,"o":+18,"ly":+28,"c":+5,"f":+3,"d":+8,"fm":+22}),

    # Sevda toward / from others
    ("char_sevda",     "any",           {"a":+5,"t":+25,"r":+28,"o":+22,"ly":+28,"c":+18,"d":+8,"fm":+30}),
    ("any",            "char_sevda",    {"a":+5,"t":+25,"r":+28,"o":+22,"ly":+28,"c":+18,"d":+10,"fm":+32}),

    # Anisa toward / from others
    ("char_anisa",     "any",           {"a":+8,"t":+25,"r":+32,"o":+15,"ly":+28,"c":+15,"f":+3,"d":+5,"fm":+32}),
    ("any",            "char_anisa",    {"a":+8,"t":+28,"r":+32,"o":+18,"ly":+30,"c":+15,"f":+3,"d":+8,"fm":+32}),

    # Malika toward / from others
    ("char_malika",    "any",           {"a":+5,"t":+25,"r":+28,"o":+22,"ly":+28,"c":+12,"f":+3,"d":+8,"fm":+30}),
    ("any",            "char_malika",   {"a":+5,"t":+25,"r":+28,"o":+22,"ly":+28,"c":+12,"f":+5,"d":+10,"fm":+32}),

    # Tarana toward / from others
    ("char_tarana",    "any",           {"a":+15,"t":+25,"r":+28,"o":+10,"ly":+28,"c":+25,"d":+5,"fm":+38}),
    ("any",            "char_tarana",   {"a":+18,"t":+25,"r":+28,"o":+12,"ly":+28,"c":+22,"d":+5,"fm":+38}),

    # Reva toward / from others
    ("char_reva",      "any",           {"a":+12,"t":+28,"r":+28,"o":+15,"ly":+30,"c":+30,"d":+8,"fm":+35}),
    ("any",            "char_reva",     {"a":+12,"t":+28,"r":+28,"o":+15,"ly":+30,"c":+30,"d":+8,"fm":+38}),

    # Svara toward / from others
    ("char_svara",     "any",           {"a":+12,"t":+25,"r":+28,"o":+10,"ly":+28,"c":+25,"d":+5,"fm":+35}),
    ("any",            "char_svara",    {"a":+12,"t":+25,"r":+28,"o":+12,"ly":+28,"c":+25,"d":+5,"fm":+35}),
]


def classify(src, dst):
    pair = frozenset([src, dst])
    if pair == frozenset(["char_maha_deva", "char_kumari_rati"]):
        return "intimate_partner"
    if pair in (frozenset(["char_kumari_rati", "char_padma"]),
                frozenset(["char_kumari_rati", "char_champa"])):
        return "caregiver_to_charge" if src == "char_kumari_rati" else "charge_to_caregiver"
    if pair == frozenset(["char_padma", "char_champa"]):
        return "mentor_to_student" if src == "char_padma" else "student_to_mentor"
    if pair in (frozenset(["char_sevda", "char_jahzara"]),
                frozenset(["char_sevda", "char_reva"])):
        return "sacred_bond"
    if src == "char_maha_deva":
        return "authority_to_subordinate"
    if dst == "char_maha_deva":
        return "submissive_to_authority"
    if src == "char_kumari_rati":
        return "authority_to_subordinate"
    if dst == "char_kumari_rati":
        return "submissive_to_authority"
    return "peer_colleague"


POWER = {
    "authority_to_subordinate": "downward",
    "submissive_to_authority": "upward",
    "peer_colleague": "lateral",
    "mentor_to_student": "downward",
    "student_to_mentor": "upward",
    "caregiver_to_charge": "downward",
    "charge_to_caregiver": "upward",
    "intimate_partner": "bidirectional",
    "sacred_bond": "bidirectional",
}


def apply_rules(src, dst):
    dims = dict(BASE)
    for ps, pd, deltas in RULES:
        if (ps == "any" or ps == src) and (pd == "any" or pd == dst):
            for k, v in deltas.items():
                dims[k] = dims.get(k, 0) + v
            break
    # Clamp to [0, 100]
    return {k: max(0, min(100, v)) for k, v in dims.items()}


def main():
    edges = {}
    for src in CHARACTERS:
        for dst in CHARACTERS:
            if src == dst:
                continue
            edge_id = f"rel_{src[5:]}_{dst[5:]}"
            rtype = classify(src, dst)
            edges[edge_id] = {
                "from": src,
                "to": dst,
                "type": rtype,
                "power_direction": POWER.get(rtype, "neutral"),
                "dim": apply_rules(src, dst),
            }

    out = {
        "schema": "antahpura.relationship.edges_canonical",
        "version": "20.0",
        "description": "All 182 directed relationship edges for the 14 canonical characters.",
        "total_edges": len(edges),
        "dimension_keys": {
            "a": "affection", "t": "trust", "r": "respect", "o": "obligation",
            "rv": "rivalry", "ly": "loyalty", "c": "curiosity", "f": "fear",
            "d": "dependency", "rs": "resentment", "fm": "familiarity",
        },
        "edges": edges,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"WROTE: {OUT.relative_to(ROOT)}")
    print(f"  Edges: {len(edges)}")
    print(f"  Size:  {OUT.stat().st_size} bytes")


if __name__ == "__main__":
    main()