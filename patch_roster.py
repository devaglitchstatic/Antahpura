import json
import os

json_path = "/sdcard/Download/Antahpura_Splitted_Core.json"

if not os.path.exists(json_path):
    print("❌ ERROR: Could not locate your split lorebook file. Please ensure it is saved as 'Antahpura_Splitted_Core.json' inside your Download folder.")
    exit(1)

with open(json_path, "r", encoding="utf-8") as f:
    lorebook = json.load(f)

# Determine the next incremental Entry ID slot in the dictionary to avoid overwriting existing sections
next_id = len(lorebook["entries"]) + 1

# Define our updated character payload strings
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

# Append the new entries cleanly with distinct activation keys
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

with open(json_path, "w", encoding="utf-8") as f:
    json.dump(lorebook, f, indent=2, ensure_ascii=False)

print(f"\n✅ SUCCESS: Reva, Zola, and Altani fully patched as separate characters {next_id}, {next_id+1}, and {next_id+2}!")
print("Updated file saved at: /sdcard/Download/Antahpura_Splitted_Core.json")
