import json
import os

target_path = "/sdcard/Download/Antahpura_v1.json"
output_path = "/sdcard/Download/Antahpura_v2.json"

# In case the file path was saved with a temporary variant name
if not os.path.exists(target_path):
    target_path = "/sdcard/Download/Antahpura_Splitted_Roster.json"

if not os.path.exists(target_path):
    print("⚠️ Base file not found directly. Creating a fresh, pristine 4-Entry Optimized Architecture...")
    base_content = "Initialize Sandbox timeline from chronological zero."
else:
    with open(target_path, "r", encoding="utf-8") as f:
        try:
            old_data = json.load(f)
            base_content = old_data.get("entries", {}).get("1", {}).get("content", "Initialize Sandbox timeline.")
        except:
            base_content = "Initialize Sandbox timeline."

# Clean Entry 1 data core text body by stripping out the old combined chorus block
clean_master_content = base_content
text_markers_to_remove = [
    "12_REVA_ZOLA_ALTANI", "REVA_ZOLA_ALTANI", "REVA, ZOLA, AND ALTANI",
    "CHARACTER 12_REVA", "CHARACTER 13_ZOLA", "CHARACTER 14_ALTANI"
]
lines = clean_master_content.split("\n")
filtered_lines = [l for l in lines if not any(marker in l for marker in text_markers_to_remove)]
clean_master_content = "\n".join(filtered_lines).strip()

# Construct the expanded, individually updated adult character content scripts
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

# Formulate the flat, valid 4-Entry deduplicated structure schema required by Chub AI
pristine_lorebook = {
  "name": "Antahpura Master Unified Core",
  "description": "Cleaned, token-optimized 4-entry layout configuration with split bibles and zero duplication hooks.",
  "entries": {
    "1": {
      "uid": 1,
      "key": ["Vasa-Griha", "basalt", "sandstone", "Jali", "Solstice", "Amavasya", "Bhumigandha", "Nisha-Sadhana", "Maha Deva", "Deva", "Maharaj", "Kuma Ree", "Kuma", "Ree", "Princess", "Padma", "Baha", "Soren", "Champa", "Buda", "Horo", "Anisa", "Kamini", "Shrinagar", "Tarana", "Roxana", "Jahzara", "Sevda", "Malika", "setup"],
      "keysecondary": [],
      "comment": "Entry 1: Master World / Constitutional Data Only",
      "content": clean_master_content,
      "constant": True, "selective": False, "selectiveLogic": 0, "addationToChat": 0, "order": 1, "probability": 100, "use_regex": False, "embedding_vector": []
    },
    "2": {
      "uid": 2,
      "key": ["Reva", "Chorus", "SO-HAM", "breathing", "hum"],
      "keysecondary": [],
      "comment": "Entry 2: Kamini Reva Character Bible",
      "content": reva_content.strip(),
      "constant": False, "selective": False, "selectiveLogic": 0, "addationToChat": 0, "order": 2, "probability": 100, "use_regex": False, "embedding_vector": []
    },
    "3": {
      "uid": 3,
      "key": ["Zola", "Captain", "fortress", "command"],
      "keysecondary": [],
      "comment": "Entry 3: Captain Zola Character Bible",
      "content": zola_content.strip(),
      "constant": False, "selective": False, "selectiveLogic": 0, "addationToChat": 0, "order": 3, "probability": 100, "use_regex": False, "embedding_vector": []
    },
    "4": {
      "uid": 4,
      "key": ["Altani", "Sentinel", "shadow", "watch"],
      "keysecondary": [],
      "comment": "Entry 4: Sentinel Altani Character Bible",
      "content": altani_content.strip(),
      "constant": False, "selective": False, "selectiveLogic": 0, "addationToChat": 0, "order": 4, "probability": 100, "use_regex": False, "embedding_vector": []
    }
  }
}

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(pristine_lorebook, f, indent=2, ensure_ascii=False)

print("\n✅ SUCCESS: Structural cleanup complete! File completely deduplicated and reconstructed.")
print("Saved as: /sdcard/Download/Antahpura_v2.json")
