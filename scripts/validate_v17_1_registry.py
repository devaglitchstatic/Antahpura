#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = json.loads((ROOT/"registry"/"V17_1_CHARACTER_REGISTRY.json").read_text(encoding="utf-8"))
PH = json.loads((ROOT/"registry"/"V17_1_PHASE_REGISTRY.json").read_text(encoding="utf-8"))

ids={c["id"] for c in REG["characters"]}
checks={
    "exactly_14_seats":len(ids)==14,
    "zola_removed":"zola" not in ids,
    "svara_present":"svara" in ids,
    "anisa_habshi":"habshi" in next(c for c in REG["characters"] if c["id"]=="anisa")["ethnicity_provenance"].lower(),
    "tarana_sogdian":"sogdian" in next(c for c in REG["characters"] if c["id"]=="tarana")["ethnicity_provenance"].lower(),
    "svara_in_sonic":"svara" in PH["participants"]["Sonic Entrainment"],
    "zola_nowhere_in_phase":"zola" not in {x for v in PH["participants"].values() for x in v},
}
print(json.dumps(checks, indent=2))
if not all(checks.values()):
    raise SystemExit(1)
print("V17.1 registry validation: PASS")
