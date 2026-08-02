import json
import os

txt_path = "/sdcard/Download/Antahpura.txt"
json_path = "/sdcard/Download/Antahpura.json"

if not os.path.exists(txt_path):
    txt_path = "/sdcard/Download/antahpura.txt"

if not os.path.exists(txt_path):
    print("❌ ERROR: Please make sure the text tree file is saved as 'Antahpura.txt' in your device Download folder.")
    exit(1)

with open(txt_path, "r", encoding="utf-8") as f:
    content_data = f.read()

# Formulate Chub AI's exact, valid V2 Lorebook object registry structure
chub_lorebook = {
  "name": "Antahpura Master Unified Core",
  "description": "Unified Sanskritized Master Data Core & World Database containing all 12 character bibles, relationship matrices, and universal prompt injection rules.",
  "entries": {
    "1": {
      "uid": 1,
      "key": [
        "Kuma Ree", "Ree", "Princess", "Padma", "Baha", "Soren", "Champa", "Buda", "Horo", "Deva", "Maharaj", "Maharaj Deva", "Anisa", "Kamini", "Shrinagar", "Tarana", "Roxana", "Jahzara", "Sevda", "Malika", "Reva", "Zola", "Altani", "lorebook", "manual", "matrix", "style bible", "setup", "prompt", "switch"
      ],
      "keysecondary": [],
      "comment": "Master System Engine Overrides",
      "content": content_data,
      "constant": True,
      "selective": False,
      "selectiveLogic": 0,
      "addationToChat": 0,
      "order": 1,
      "probability": 100,
      "use_regex": False,
      "embedding_vector": []
    }
  }
}

with open(json_path, "w", encoding="utf-8") as f:
    json.dump(chub_lorebook, f, indent=2, ensure_ascii=False)

print("\n✅ SUCCESS: Formatted tree successfully wrapped into valid Chub Lorebook format!")
print("Location: /sdcard/Download/Antahpura.json")
