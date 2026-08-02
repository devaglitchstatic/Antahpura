import json
import os

target_path = "/sdcard/Download/Antahpura_v1.json"
output_path = "/sdcard/Download/Antahpura_V2.json"

if not os.path.exists(target_path):
    target_path = "/sdcard/Download/Antahpura_Splitted_Roster.json"

if not os.path.exists(target_path):
    print("⚠️ Base JSON file not found. Generating fresh, pristine data layers directly...")
    with open("/sdcard/Download/Antahpura.txt", "r", encoding="utf-8") as f:
        clean_master_content = f.read()
    reva_content = "[CHARACTER 12: KAMINI REVA]"
    zola_content = "[CHARACTER 13: CAPTAIN ZOLA]"
    altani_content = "[CHARACTER 14: SENTINEL ALTANI]"
else:
    with open(target_path, "r", encoding="utf-8") as f:
        old_data = json.load(f)
    entries = old_data.get("entries", {})
    clean_master_content = entries.get("1", {}).get("content", "Initialize Sandbox timeline.")
    reva_content = entries.get("2", {}).get("content", "[CHARACTER 12: KAMINI REVA]")
    zola_content = entries.get("3", {}).get("content", "[CHARACTER 13: CAPTAIN ZOLA]")
    altani_content = entries.get("4", {}).get("content", "[CHARACTER 14: SENTINEL ALTANI]")

# 🏛️ FIXED VERSION 26.2.0 ARRAYS: Direct root metadata alignment
pristine_chub_lorebook = {
  "name": "Antahpura Master Unified Core",
  "tagline": "A Narrative and Dialogue Lexicon for a Classical Indo-Persian Royal Harem Chronicle",
  "description": "Unified Sanskritized Master Data Core & World Database containing all 12 character bibles, relationship matrices, and universal prompt injection rules.",
  "entries": {
    "1": {
      "uid": 1,
      "key": ["Vasa-Griha", "basalt", "sandstone", "Jali", "Solstice", "Amavasya", "Bhumigandha", "Nisha-Sadhana", "Maha Deva", "Deva", "Maharaj", "Kuma Ree", "Kuma", "Ree", "Princess", "Padma", "Baha", "Soren", "Champa", "Buda", "Horo", "Anisa", "Kamini", "Shrinagar", "Tarana", "Roxana", "Jahzara", "Sevda", "Malika", "setup"],
      "keysecondary": [],
      "comment": "Entry 1: Master World / Constitutional Data Only",
      "content": clean_master_content.strip(),
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
    json.dump(pristine_chub_lorebook, f, indent=2, ensure_ascii=False)

print("\n✅ SUCCESS: Structural fields map and split profile logic completed!")
print("Location: /sdcard/Download/Antahpura_V2.json")
