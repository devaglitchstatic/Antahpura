import json

lorebook = {
    "name": "Antahpura Master Unified Core",
    "tagline": "A Modular Narrative and Dialogue Lexicon for a Classical Indo-Persian Royal Court Chronicle",
    "description": "Unified constitutional world database containing court law, character bibles, relationship matrices, and scene-generation systems.",
    "entries": {}
}

def entry(uid, keys, comment, content, constant=False):
    return {
        "uid": uid,
        "key": keys,
        "keysecondary": [],
        "comment": comment,
        "content": content,
        "constant": constant,
        "selective": False,
        "selectiveLogic": 0,
        "addationToChat": 0,
        "order": uid,
        "probability": 100,
        "use_regex": False,
        "embedding_vector": []
    }

world_constitution = """[SECTION I: ADHI-SHTHANA-SAMVIDHANA (WORLD CONSTITUTION)]
- Sovereign Dynasty: Solar Suryavanshi core intersecting with Lunar Chandravanshi lineages.
- Palace Architecture: Red-basalt and perforated sandstone Vasa-Griha courtyards with jali screens, plinths, thresholds, and ritual axes.
- Institutions: Throne, Zenana, Military, Administrative Court, Monastic Vaults, Artistic Guilds, Ritual Pavilion.
- Narrative Law: Rank determines distance; distance determines language; language determines silence; silence determines power.
- Seasonal Cycle: Varsha Ritu, Amavasya observances, Solstice rites, and Nisha-Sadhana ceremonial periods.
- Atmospheric Anchors: Bhumigandha (earth scent), Parimala (incense and oils), lamp smoke, stone acoustics, and courtyard resonance.
- POV Engine: Architecture -> Atmosphere -> Hierarchy -> Gaze -> Dialogue -> Interior -> Verdict.
- Relationship Engine: Pairwise modulation of diction, honorifics, gesture, and silence according to court hierarchy and institutional allegiance.
"""

lorebook["entries"]["1"] = entry(
    1,
    ["setup", "world", "constitution", "Varsha Ritu", "Amavasya", "Solstice", "Nisha-Sadhana", "Bhumigandha", "Parimala", "Lekhaka"],
    "Entry 1: Master World Constitution",
    world_constitution,
    constant=True
)

schema = """[CHARACTER BIBLE]
Identity:
Age:
Gender:
Lineage / Ethnicity:
Station / Rank:
Institution:
Archetype:
Court Function:
Public Voice:
Relational Voice:
Interior Voice:
Emotional Temperature:
Primary Weapon:
Primary Vulnerability:
Forbidden Subject:
Honorifics Received:
Honorifics Given:
Gesture Signature:
Silence Signature:
Spatial Behavior:
POV Lexicon:
"""

characters = [
    (2,  "Maharaj Deva",       ["Maha Deva", "Deva", "Maharaj"]),
    (3,  "Princess Kuma Ree",  ["Kuma Ree", "Kuma", "Ree", "Princess"]),
    (4,  "Padma",              ["Padma", "Baha", "Soren", "Dasi"]),
    (5,  "Champa",             ["Champa", "Buda", "Horo"]),
    (6,  "Kamini Anisa",       ["Anisa", "Kamini", "Darogha"]),
    (7,  "Shrinagar",          ["Shrinagar", "Kathak", "Kalavati"]),
    (8,  "Tarana",             ["Tarana", "Sangeeta", "Gayika"]),
    (9,  "Roxana",             ["Roxana", "Silahtar", "Rakshika"]),
    (10, "Jahzara",            ["Jahzara", "Vanguard", "Guard"]),
    (11, "Sevda",              ["Sevda", "Vault", "Warden"]),
    (12, "Malika",             ["Malika", "Guha-Warden", "Confinement"]),
    (13, "Kamini Reva",        ["Reva", "Ritual", "Witness"]),
    (14, "Captain Zola",       ["Zola", "Captain", "Bahadur"]),
    (15, "Sentinel Altani",    ["Altani", "Sentinel", "Shadow"]),
]

for uid, name, keys in characters:
    lorebook["entries"][str(uid)] = entry(
        uid,
        keys,
        f"Entry {uid}: {name} Character Bible",
        schema.replace("Identity:", f"Identity: {name}")
    )

lorebook["entries"]["16"] = entry(
    16,
    ["relationship", "pairing", "modulation", "inter-agent"],
    "Entry 16: Relationship Matrix",
    "[RELATIONSHIP MATRIX]\\nDefine pairwise modulation rules for rank, honorifics, silence, gesture, spatial distance, and linguistic register.",
    constant=True
)

lorebook["entries"]["17"] = entry(
    17,
    ["Prompt Engine", "Choice", "Option", "POV"],
    "Entry 17: Scene Engine & Player Choice System",
    "[SCENE ENGINE]\\nDefine POV switching, scene architecture, atmospheric anchors, and player choice vectors.",
    constant=True
)

with open("/sdcard/Download/Antahpura_V3.json", "w", encoding="utf-8") as f:
    json.dump(lorebook, f, indent=2, ensure_ascii=False)

print("Generated: /sdcard/Download/Antahpura_V3.json")
