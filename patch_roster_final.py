import json
import os

# Directly target the file name you verified
json_path = "/sdcard/Download/Antahpura_Splitted_Roster.json"

if not os.path.exists(json_path):
    # Try lowercase variation just in case
    json_path = "/sdcard/Download/antahpura_splitted_roster.json"

if not os.path.exists(json_path):
    print("❌ ERROR: Could not find your base file. Please make sure 'Antahpura_Splitted_Roster.json' is located inside your device Download folder.")
    exit(1)

with open(json_path, "r", encoding="utf-8") as f:
    lorebook = json.load(f)

# Initialize entries sub-dictionary if missing or wrapped as a flat object
if "entries" not in lorebook:
    lorebook["entries"] = {}

# Determine the next sequential index number to prevent overwriting existing sections
next_id = len(lorebook["entries"]) + 1

# Define our updated character payload strings with masked adult statuses
reva_content = """[CHARACTER 12: KAMINI REVA]
- Title: Ritual Witness | Court Status: Prauḍha-Initiate (Adult Performer)
- Archetype: RASA-SAKSHI / VINEYA CHORUS NODE | Distance: 10 Hasta
- Somatic Alignment: Śānta-Mauna breathing loops. Wears gold Anavat toe-rings, Chuchuka-Valaya nipple rings, and a silver Yoni-Mudra ringtrack. Her skin canvas responds natively to changes in the room's global Parimala scent weight. 
- Universal System Law: Prone to Vāk-Kautuka-Bhrama, forcing her dirty thoughts out loud followed by Maha Deva branching choice gates."""

zola_content = """[CHARACTER 13: CAPTAIN ZOLA]
- Title: Captain of the Inner Guard | Court Status: Kṣatriya-Kanya
- Archetype: VAJRA / BANDHANA-ACHARYA NODE | Distance: 11 Hasta
- Somatic Alignment: Yuddha-Mauna guard lock stance. Wears rigid military-grade hardware loops, heavy Kanchuki leather armor panels, and a weighted steel Yoni-Mudra ringtrack near the dungeon gates. Measures tissue stress and rope tension physics under intense Tapas.
- Universal System Law: Prone to Vāk-Kautuka-Bhrama, forcing her dirty thoughts out loud followed by Maha Deva branching choice gates."""

altani_content = """[CHARACTER 14: SENTINEL ALTANI]
- Title: Maze Garden Sentinel | Court Status: Navodha-Sentinel
- Archetype: STHIRA / VYADHA-ANDHA SECURE NODE | Distance: 12 Hasta
- Somatic Alignment: Stambha-Mauna voyeur lock. Wears polished obsidian Yoni-Mudra rings and bare feet pressing into basalt slabs near the doorway layout. Maintains a predatory invisible strip-search gaze that tracks the retinue line by line, causing heavy throat swallowing as her focus shatters.
- Universal System Law: Prone to Vāk-Kautuka-Bhrama, forcing her dirty thoughts out loud followed by Maha Deva branching choice gates."""

# Append the separate entry slots cleanly with their respective unique activation keys
lorebook["entries"][str(next_id)] = {
    "uid": next_id, "key": ["Reva", "Chorus", "SO-HAM", "breathing"], "keysecondary": [],
    "comment": "Sub-System: CHARACTER 12: KAMINI REVA", "content": reva_content,
    "constant": False, "selective": False, "selectiveLogic": 0, "addationToChat": 0, "order": next_id, "probability": 100, "use_regex": False, "embedding_vector": []
}

lorebook["entries"][str(next_id + 1)] = {
    "uid": next_id + 1, "key": ["Zola", "Captain", "fortress", "command"], "keysecondary": [],
    "comment": "Sub-System: CHARACTER 13: CAPTAIN ZOLA", "content": zola_content,
    "constant": False, "selective": False, "selectiveLogic": 0, "addationToChat": 0, "order": next_id + 1, "probability": 100, "use_regex": False, "embedding_vector": []
}

lorebook["entries"][str(next_id + 2)] = {
    "uid": next_id + 2, "key": ["Altani", "Sentinel", "shadow", "watch"], "keysecondary": [],
    "comment": "Sub-System: CHARACTER 14: SENTINEL ALTANI", "content": altani_content,
    "constant": False, "selective": False, "selectiveLogic": 0, "addationToChat": 0, "order": next_id + 2, "probability": 100, "use_regex": False, "embedding_vector": []
}

# Overwrite and export back into your public Downloads folder track
target_output = "/sdcard/Download/Antahpura_Splitted_Roster.json"
with open(target_output, "w", encoding="utf-8") as f:
    json.dump(lorebook, f, indent=2, ensure_ascii=False)

print(f"\n✅ SUCCESS: Reva, Zola, and Altani fully patched as separate characters into your master roster json!")
print(f"Location: {target_output}")
