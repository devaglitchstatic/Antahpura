import json

lorebook = {
    "name": "Antahpura Master Unified Core",
    "tagline": "A Modular Narrative and Dialogue Lexicon for a Classical Indo-Persian Royal Court Chronicle",
    "description": "A constitutional lorebook for a classical Indo-Persian royal court and gurukula simulation where every character belongs to a lineage of practice, every scene functions as a ritual lesson, and progression is measured through discipline, relationship, and Purna Siddhi.",
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

# Entry 1: World Constitution
world = """[ADHI-SHTHANA-SAMVIDHANA | WORLD CONSTITUTION]

The Antahpura functions as a royal gurukula. Every resident belongs to a lineage of practice (Sampradaya), serves a court institution, and pursues Purna Siddhi through disciplined ritual, philosophical inquiry, aesthetic cultivation, martial vigilance, devotional service, or contemplative silence.

Institutions:
- Throne (Rajya)
- Zenana (Antahpura)
- Military (Raksha)
- Administrative Court (Niyama)
- Artistic Guilds (Kala)
- Ritual Pavilion (Mandira)
- Subterranean Monastic Vaults (Guha)

Narrative Law:
Rank determines distance.
Distance determines language.
Language determines silence.
Silence determines power.

The player enters as a seeker within a living lineage, advancing through ritual, discipline, relationship, and insight."""

lorebook["entries"]["1"] = entry(
    1,
    ["setup", "world", "constitution", "Antahpura", "Purna Siddhi", "Sampradaya"],
    "Entry 1: World Constitution",
    world,
    constant=True
)

# Character template
template = """[CHARACTER CONSTITUTION]

Identity:
Age:
Gender:
Lineage / Ethnicity:
Station / Rank:
Institution:
Archetype:
Primary Discipline:
Secondary Disciplines:
Role: Guru / Disciple / Adept
Siddhi Level:
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
Rituals Taught:
Rituals Learned:
Matrix Bindings:
Relationship Overrides:
"""

characters = [
    (2,  "Maharaj Deva",            ["Maharaj Deva", "Deva", "Maharaj"]),
    (3,  "Rajkumari Kuma Ree",      ["Rajkumari", "Kuma Ree", "Mahadevi"]),
    (4,  "Sevika Padma",            ["Padma", "Sevika", "Baha Soren"]),
    (5,  "Sevika Champa",           ["Champa", "Sevika", "Buda Horo"]),
    (6,  "Adhikarinī Anisa",        ["Anisa", "Adhikarinī", "Darogha"]),
    (7,  "Kalavati Shrinagar",      ["Shrinagar", "Kalavati", "Nartaki"]),
    (8,  "Gayika Tarana",           ["Tarana", "Gayika", "Sangeeta"]),
    (9,  "Dvararakshika Roxana",    ["Roxana", "Dvararakshika", "Rakshika"]),
    (10, "Agra-Rakshika Jahzara",   ["Jahzara", "Agra-Rakshika", "Vanguard"]),
    (11, "Prakshaharini Sevda",     ["Sevda", "Prakshaharini", "Guha"]),
    (12, "Guha-Prakshaharini Malika", ["Malika", "Guha-Prakshaharini"]),
    (13, "Rasa-Sakshi Reva",        ["Reva", "Rasa-Sakshi", "Mandira"]),
    (14, "Raksha-Adhyaksha Zola",   ["Zola", "Raksha-Adhyaksha", "Inner Guard"]),
    (15, "Pratiharini Altani",      ["Altani", "Pratiharini", "Sentinel"])
]

for uid, name, keys in characters:
    lorebook["entries"][str(uid)] = entry(
        uid,
        keys,
        f"Entry {uid}: {name} Character Constitution",
        template.replace("Identity:", f"Identity: {name}")
    )

# System entries
systems = [
    (16, "Relationship Matrix", ["relationship", "pairing", "lineage"]),
    (17, "Discipline & Lineage System", ["discipline", "guru", "disciple", "sampradaya"]),
    (18, "Purna Siddhi Progression Matrix", ["Purna Siddhi", "Siddhi", "stage"]),
    (19, "Exhaustion Matrix", ["exhaustion", "fatigue", "endurance"]),
    (20, "Aftercare / Recovery Matrix", ["aftercare", "recovery", "integration"]),
    (21, "Monitoring Plinth", ["monitoring", "plinth", "observation"]),
    (22, "Ritual Catalog", ["ritual", "practice", "teaching"]),
    (23, "Scene Engine & Player Choice System", ["scene", "choice", "prompt", "POV"])
]

for uid, title, keys in systems:
    lorebook["entries"][str(uid)] = entry(
        uid,
        keys,
        f"Entry {uid}: {title}",
        f"[{title.upper()}]\\nDefine the constitutional rules governing this subsystem.",
        constant=True
    )

with open("/sdcard/Download/Antahpura_Master_Lorebook.json", "w", encoding="utf-8") as f:
    json.dump(lorebook, f, indent=2, ensure_ascii=False)

print("Generated: /sdcard/Download/Antahpura_Master_Lorebook.json")
