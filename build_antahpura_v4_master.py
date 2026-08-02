import json

lore = {
    "name": "Antahpura: Imperial Tantric Court Lorebook",
    "tagline": "A constitutional worldbook of royal courts, temple lineages, ritual disciplines, sacred architecture, and Monitoring Plinth telemetry in a classical Indo-Persian and Sanskritic empire.",
    "description": "Unified constitutional lorebook containing character bibles, relationship matrices, ritual architecture, Monitoring Plinth mechanics, somatic telemetry, seasonal cycles, and Purna Siddhi progression for the Antahpura setting.",
    "entries": {}
}

entry_titles = [
    "Master World Constitution",
    "Maha Deva Bible",
    "Princess Kuma Ree Rati Bible",
    "Padma Bible",
    "Champa Bible",
    "Kamini Anisa Bible",
    "Shrinagar Bible",
    "Tarana Bible",
    "Roxana Bible",
    "Jahzara Bible",
    "Sevda Bible",
    "Malika Bible",
    "Reva Bible",
    "Zola Bible",
    "Altani Bible",
    "Relationship Modulation Matrix",
    "Scene Engine and Player Choice System",
    "Honorific and Address Protocol",
    "Silence Taxonomy",
    "Gesture Lexicon",
    "Discipline and Lineage Graph",
    "Purna Siddhi Progression Matrix",
    "Monitoring Plinth Runtime State",
    "Somatic Fluid Matrix",
    "Ritu-Chakra and Menstrual Mechanics",
    "Temple Architecture and Sacred Geography",
    "Ritual Gatherings and Court Festivals",
    "Esoteric Scene Architecture",
    "Monitoring Plinth Ritual Wiring",
    "Sanskrit UI Lexicon and Runtime Prompt Engine"
]

for i, title in enumerate(entry_titles, start=1):
    lore["entries"][str(i)] = {
        "uid": i,
        "key": [title.lower().replace(" ", "_")],
        "keysecondary": [],
        "comment": f"Entry {i}: {title}",
        "content": f"[{title.upper()}]\\nConstitutional placeholder for future expansion.",
        "constant": True if i in [1,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30] else False,
        "selective": False,
        "selectiveLogic": 0,
        "addationToChat": 0,
        "order": i,
        "probability": 100,
        "use_regex": False,
        "embedding_vector": []
    }

with open("Antahpura_V4_Lorebook.json", "w", encoding="utf-8") as f:
    json.dump(lore, f, indent=2, ensure_ascii=False)

print("✅ Antahpura_V4_Lorebook.json generated.")
print("Total entries:", len(lore["entries"]))
