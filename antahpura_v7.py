import json

# 🏛️ VERIFIED HEAD METADATA SCHEMA FORMAT FOR CHUB AI AUTO-INGESTION
v7_skeleton = {
  "name": "Antahpura Master Unified Core",
  "tagline": "A Modular Narrative and Dialogue Lexicon for a Classical Indo-Persian Royal Harem Chronicle",
  "description": "Unified Sanskritized Master Data Core & World Database containing all 12 character bibles structured via a strict 20-point constitutional schema, relationship matrices, and universal prompt injection rules.",
  "entries": {
    "1": {
      "uid": 1,
      "key": ["setup", "world", "constitution", "Varsha Ritu", "Amavasya", "Solstice", "Nisha-Sadhana", "Bhumigandha", "Parimala", "Lekhaka"],
      "keysecondary": [],
      "comment": "Entry 1: Master World Constitution Only",
      "content": "[SECTION I: ADHI-SHTHANA-SAMVIDHANA (WORLD CONSTITUTION)]\\n- Sovereign Dynasty: Solar Suryavanshi Core intersecting with Lunar Chandravanshi Lineages.\\n- Palace Architecture: Red-basalt and perforated sandstone Vasa-Griha courtyard layout with Jali screens cool against Niravaranapada-Tala.\\n- Institutions: Throne (Absolute command), Zenana (Poetic courtly intimacy & modesty), Military (Restraint physics & Urdu command), Monastic (Left-Hand Path purification rules), Chorus (Collective drone loops managing room exhaustion tracks).\\n- Honorific System: Strict token overrides. All submissives must utilize 'meri' instead of my/mine and 'Prabhu' instead of Lord.\\n- Silence Taxonomy: Śānta-Mauna (Devotional stillness), Yuddha-Mauna (Rigid military tactical vigilance), Stambha-Mauna (Immovable voyeuristic surveillance lock).\\n- Gesture Lexicon: Avanata-Janu-Sthiti (kneeling face bowed), Kshatriya-Sthiti (fist-to-chest guard lock), Chatushpada-Vesha (quadrupedal floor stance).\\n- Scene Engine & POV Switching Rules: Loops perspective tracking whenever cosmetic smudging, fluid melting (Rasayana/Madana-Jala), or physical canvas markings occur across the roster assets.\\n- Relationship Engine Rules: Automates pairwise structural scaling, instantly shifting syntax boundaries when designated nodes interlock within the thread context.",
      "constant": True, "selective": False, "selectiveLogic": 0, "addationToChat": 0, "order": 1, "probability": 100, "use_regex": False, "embedding_vector": []
    }
  }
}

# Generate placeholder entry slots for 2 to 17 matching your recommended schema layout structure
entry_purposes = [
    (2, "Maha Deva", ["Maha Deva", "Deva", "Maharaj"]),
    (3, "Princess Kuma Ree", ["Kuma Ree", "Kuma", "Ree", "Princess"]),
    (4, "Padma", ["Padma", "Baha", "Soren", "Dasi"]),
    (5, "Champa", ["Champa", "Buda", "Horo", "Kridamriga"]),
    (6, "Kamini Anisa", ["Anisa", "Kamini", "Daroga"]),
    (7, "Shrinagar", ["Shrinagar", "Ganika", "Kathak", "Nupur"]),
    (8, "Tarana", ["Tarana", "Sangeeta", "Vocalist"]),
    (9, "Roxana", ["Roxana", "Silahtar", "Rigger"]),
    (10, "Jahzara", ["Jahzara", "Nizam", "Vanguard", "Guard"]),
    (11, "Sevda", ["Sevda", "Ascetic", "Vault", "Warden"]),
    (12, "Malika", ["Malika", "Guha-Warden", "Confinement"]),
    (13, "Kamini Reva", ["Reva", "Chorus", "SO-HAM"]),
    (14, "Captain Zola", ["Zola", "Captain", "fortress"]),
    (15, "Sentinel Altani", ["Altani", "Sentinel", "shadow"]),
    (16, "Relationship Matrix", ["relationship", "pairing", "modulation", "inter-agent"]),
    (17, "Scene Engine & Player Choice System", ["Prompt Engine", "Choice", "Option", "Vāk-Kautuka"])
]

# Uniform 20-Point Constitutional Schema Template
schema_template = """Identity: [Name]
Age: [Masked Court Status]
Lineage / Ethnicity: [Data]
Station / Rank: [Data]
Institution: [Data]
Archetype: [Data]
Court Function: [Data]
Public Voice: [Data]
Relational Voice: [Data]
Interior Voice: [Data]
Emotional Temperature: [Data]
Primary Weapon: [Data]
Primary Vulnerability: [Data]
Forbidden Subject: [Data]
Honorifics Received: [Data]
Honorifics Given: [Data]
Gesture Signature: [Data]
Silence Signature: [Data]
Spatial Behavior: [Data]
POV Lexicon: [Data]"""

for uid, name, keys in entry_purposes:
    content_body = f"[RELATIONSHIP MATRIX / SCENE ENGINE]" if uid >= 16 else f"[CHARACTER BIBLES SCHEMA]\\n{schema_template.replace('[Name]', name)}"
    v7_skeleton["entries"][str(uid)] = {
        "uid": uid,
        "key": keys,
        "keysecondary": [],
        "comment": f"Entry {uid}: {name} Bible Node",
        "content": content_body,
        "constant": True if uid >= 16 else False,
        "selective": False, "selectiveLogic": 0, "addationToChat": 0, "order": uid, "probability": 100, "use_regex": False, "embedding_vector": []
    }

with open("/sdcard/Download/Antahpura_V2.json", "w", encoding="utf-8") as f:
    json.dump(v7_skeleton, f, indent=2, ensure_ascii=False)

print("\n✅ SUCCESS: 17-Entry Structural Skeleton file successfully generated with matching object handles!")
print("Location: /sdcard/Download/Antahpura_V2.json")
