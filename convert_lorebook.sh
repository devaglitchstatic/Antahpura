#!/bin/bash

# Define clear local file storage path tracks
TXT_FILE="/sdcard/Download/Antahpura.txt"
JSON_FILE="/sdcard/Download/Antahpura.json"

# Check lowercase variation if uppercase folder selector fails
if [ ! -f "$TXT_FILE" ]; then
    TXT_FILE="/sdcard/Download/antahpura.txt"
fi

if [ ! -f "$TXT_FILE" ]; then
    echo -e "\n❌ ERROR: Could not find Antahpura.txt inside your device Download folder."
    exit 1
fi

echo "🔄 Initializing flat Chub V2 JSON structure string conversion loop..."

# Read plain text document layers and cleanly escape double quotes and line breaks
CLEAN_TEXT=$(cat "$TXT_FILE" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | awk '{printf "%s\\n", $0}' | sed 's/\r//g')

# Build a pristine flat template container matching Chub AI's database requirements
cat << OUT_EOF > "$JSON_FILE"
{
  "name": "Antahpura Master Unified Core",
  "description": "Unified Sanskritized Master Lorebook Core containing all 12 character bibles, relationship matrices, and universal prompt rules.",
  "entries": [
    {
      "id": 1,
      "keys": ["Kuma Ree", "Ree", "Princess", "Padma", "Baha", "Soren", "Champa", "Buda", "Horo", "Deva", "Maharaj", "Maharaj Deva", "Anisa", "Kamini", "Shrinagar", "Tarana", "Roxana", "Jahzara", "Sevda", "Malika", "Reva", "Zola", "Altani", "lorebook", "manual", "matrix", "style bible", "setup", "prompt", "switch"],
      "content": "${CLEAN_TEXT}"
    }
  ]
}
OUT_EOF

echo -e "\n✅ SUCCESS: File converted and saved as /sdcard/Download/Antahpura.json"
