import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "registry" / "V18_3_RUNTIME" / "V18_3_RELATIONAL_SNAPSHOT.json"

with SNAPSHOT.open("r", encoding="utf-8") as f:
    data = json.load(f)

rati = data["characters"]["kumari_rati"]

print("=== V18.3 CONSTITUTIONAL CHECK ===")
print("characters:", len(data["characters"]))
print("relationships:", data["relationships"]["relationship_count"])
print("affiliations:", len(data["affiliations"]["characters"]))
print("skill_classes:", len(data["skills"]["skill_classes"]))

print("sovereign_axis:",
      data.get("sovereign_axis", ["maha_deva", "kumari_rati"]))

print("zola:", "zola" in data["characters"])
print("svara:", "svara" in data["characters"])

print("rati_office:", rati["constitutional_office"])

dance = data["skills"]["skill_classes"]["dance"]

print("rati_can_learn_dance:", dance["trainable"])

# Constitutional office must NOT be transferable through training.
rati_can_become_dancer = (
    rati["constitutional_office"] == "Pradhāna Nartī / Chief Dancer"
)

print("rati_can_become_dancer:", rati_can_become_dancer)

print()
print("EXPECTED:")
print("rati_can_learn_dance = True")
print("rati_can_become_dancer = False")

if not dance["trainable"]:
    raise SystemExit("FAIL: Dance is not marked trainable.")

if rati_can_become_dancer:
    raise SystemExit(
        "FAIL: Rati has been assigned the constitutional office of Chief Dancer."
    )

print()
print("V18.3 constitutional capability check: PASS")