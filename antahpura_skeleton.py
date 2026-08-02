import json

skeleton = {
  "name": "Antahpura Master Unified Core",
  "tagline": "A Narrative and Dialogue Lexicon for a Classical Indo-Persian Royal Harem Chronicle",
  "description": "Unified Sanskritized Master Data Core & World Database containing all 12 character bibles, relationship matrices, and universal prompt injection rules.",
  "entries": {}
}

with open("/sdcard/Download/Antahpura_V2.json", "w", encoding="utf-8") as f:
    json.dump(skeleton, f, indent=2, ensure_ascii=False)

print("\n✅ SUCCESS: Empty metadata skeleton file generated at /sdcard/Download/Antahpura_V2.json!")
