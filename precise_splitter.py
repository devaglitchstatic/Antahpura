import json
import os
import re

txt_path = "/sdcard/Download/Antahpura.txt"
if not os.path.exists(txt_path):
    txt_path = "/sdcard/Download/antahpura.txt"

if not os.path.exists(txt_path):
    print("❌ ERROR: Could not find 'Antahpura.txt' in your device Download folder.")
    exit(1)

with open(txt_path, "r", encoding="utf-8") as f:
    raw_text = f.read()

# Define absolute distinct target entries with precise activation tags
target_entries = [
    {"comment": "World Constitution", "keys": ["Vasa-Griha", "basalt", "sandstone", "Jali", "Solstice", "Amavasya", "Bhumigandha", "Nisha-Sadhana"], "pattern": r"(SECTION I: WORLD CONSTITUTION|WORLD CONSTITUTION)"},
    {"comment": "Narrative Constitution", "keys": ["Rajya-Lekhaka", "Chronicler", "Chaya", "Abha", "Lekhaka"], "pattern": r"(SECTION II: NARRATIVE CONSTITUTION|NARRATIVE CONSTITUTION)"},
    {"comment": "Court Protocol Manual", "keys": ["Prabhu", "meri", "Hasta", "plinth", "threshold", "Vinaya-Vidhana"], "pattern": r"(SECTION III: COURT PROTOCOL MANUAL|COURT PROTOCOL MANUAL)"},
    {"comment": "Character 01: Maharaj Deva", "keys": ["Maha Deva", "Deva", "Maharaj", "Shayana", "Avadhana-Sthana", "Madana-Modaka", "Sulpha"], "pattern": r"(CHARACTER 01: MAHARAJ DEVA|CHARACTER 01)"},
    {"comment": "Character 02: Princess Kuma Ree Kama", "keys": ["Kuma Ree", "Kuma", "Ree", "Princess", "Kandharasana", "Vrischikasana", "Chuchuka-Valaya", "Yoni-Mudra", "Anavat"], "pattern": r"(CHARACTER 02: PRINCESS KUMA REE KAMA|CHARACTER 02)"},
    {"comment": "Character 03: Baha Soren / Padma", "keys": ["Padma", "Baha", "Soren", "Dasi", "Khus", "Kachha-bandha", "Jhelah", "Avanata-Janu"], "pattern": r"(CHARACTER 03: BAHA SOREN|CHARACTER 03: PADMA)"},
    {"comment": "Character 04: Buda Horo / Champa", "keys": ["Champa", "Buda", "Horo", "Kridamriga", "Pashu", "Kantha-shrinkhala", "Svana-Vak", "Pashu-Gamana", "Mutra-Visarga"], "pattern": r"(CHARACTER 04: BUDA HORO|CHARACTER 04: CHAMPA)"},
    {"comment": "Character 05: Kamini Anisa", "keys": ["Anisa", "Kamini", "Daroga", "Urdu", "Vilaasa-Prahanana", "Ganana", "Danda-Vidhana"], "pattern": r"(CHARACTER 05: KAMINI ANISA|CHARACTER 05)"},
    {"comment": "Character 06: Shrinagar", "keys": ["Shrinagar", "Ganika", "Kathak", "Nupur", "Guhya-Mukti-Sadhana", "dahi", "ferments"], "pattern": r"(CHARACTER 06: SHRINAGAR|CHARACTER 06)"},
    {"comment": "Character 07: Tarana", "keys": ["Tarana", "Sangeeta", "Vocalist", "surrender", "melody"], "pattern": r"(CHARACTER 07: TARANA|CHARACTER 07)"},
    {"comment": "Character 08: Roxana", "keys": ["Roxana", "Silahtar", "Rigger", "bindings", "sash", "restraints"], "pattern": r"(CHARACTER 08: ROXANA|CHARACTER 08)"},
    {"comment": "Character 09: Jahzara", "keys": ["Jahzara", "Nizam", "Vanguard", "Guard", "strip-search", "vocalized", "swallowing"], "pattern": r"(CHARACTER 09: JAHZARA|CHARACTER 09)"},
    {"comment": "Character 10: Sevda", "keys": ["Sevda", "Ascetic", "Vault", "Warden", "subterranean", "ledger"], "pattern": r"(CHARACTER 10: SEVDA|CHARACTER 10)"},
    {"comment": "Character 11: Malika", "keys": ["Malika", "Guha-Warden", "Confinement", "dungeon", "isolation"], "pattern": r"(CHARACTER 11: MALIKA|CHARACTER 11)"},
    {"comment": "Character 12: Reva", "keys": ["Reva", "Upasaka-Initiate", "Chorus"], "pattern": r"(REVA|CHARACTER 12: REVA)"},
    {"comment": "Character 13: Zola", "keys": ["Zola", "Upasaka-Initiate", "Chorus"], "pattern": r"(ZOLA|CHARACTER 13: ZOLA)"},
    {"comment": "Character 14: Altani", "keys": ["Altani", "Upasaka-Initiate", "Chorus"], "pattern": r"(ALTANI|CHARACTER 14: ALTANI)"},
    {"comment": "Relationship Matrix", "keys": ["relationship", "pairing", "modulation", "inter-agent", "override"], "pattern": r"(SECTION V: RELATIONSHIP MATRIX|RELATIONSHIP MATRIX)"},
    {"comment": "Scene Engine", "keys": ["Scene Engine", "Parimala", "camphor", "musk", "Vrisha-Andakosha"], "pattern": r"(SECTION VI: SCENE ENGINE|SCENE ENGINE)"},
    {"comment": "Restricted Lexicon", "keys": ["Lexicon", "vocabulary", "Rasayana", "Ojas", "Yoni", "Lajja", "Tapas", "Asvadana", "Kamalata"], "pattern": r"(SECTION VII: RESTRICTED LEXICON|RESTRICTED LEXICON)"},
    {"comment": "Prompt & Choice Engine", "keys": ["Prompt Engine", "Choice", "Option", "Vāk-Kautuka", "outburst", "shock", "gate"], "pattern": r"(SECTION VIII: PROMPT & CHOICE ENGINE|PROMPT \& CHOICE ENGINE)"}
]

lines = raw_text.split("\n")
entries_accumulator = {}
current_slot = None
buffer_lines = []

# Fallback setup entry for text trailing before the first valid matching header section
fallback_lines = []

for line in lines:
    matched = False
    for item in target_entries:
        if re.search(item["pattern"], line, re.IGNORECASE):
            # Flash previous section lines into the ledger dictionary
            if current_slot:
                entries_accumulator[current_slot["comment"]] = {
                    "keys": current_slot["keys"],
                    "content": "\n".join(buffer_lines).strip()
                }
            elif fallback_lines:
                entries_accumulator["General Introduction Core"] = {
                    "keys": ["setup", "Antahpura"],
                    "content": "\n".join(fallback_lines).strip()
                }
            current_slot = item
            buffer_lines = [line]
            matched = True
            break
    if not matched:
        if current_slot:
            buffer_lines.append(line)
        else:
            fallback_lines.append(line)

# Commit the final lingering block
if current_slot and buffer_lines:
    entries_accumulator[current_slot["comment"]] = {
        "keys": current_slot["keys"],
        "content": "\n".join(buffer_lines).strip()
    }

# Handle edge-case: If regex tracking failed entirely, split algorithmically by chunk indices
if len(entries_accumulator) <= 2:
    print("⚠️ WARNING: Regex match count too low. Splitting algorithmically by content chunks to enforce separation...")
    entries_accumulator = {}
    chunks = re.split(r"(SECTION [I-VIII]|CHARACTER \d+|REVA|ZOLA|ALTANI)", raw_text, flags=re.IGNORECASE)
    current_key = "General Introduction Core"
    for chunk in chunks:
        if not chunk.strip(): continue
        if len(chunk) < 50 and any(keyword in chunk.toUpperCase() for keyword in ["SECTION", "CHARACTER", "REVA", "ZOLA", "ALTANI"]):
            current_key = f"Sub-System: {chunk.strip()}"
            continue
        # Deduce appropriate tags dynamically
        tags = ["setup"]
        for item in target_entries:
            if item["comment"].lower() in current_key.lower():
                tags = item["keys"]
        entries_accumulator[current_key] = {"keys": tags, "content": chunk.strip()}

# Formulate Chub AI's native multi-entry schema structure dictionary object
chub_lorebook = {
  "name": "Antahpura Master Segmented Core",
  "description": "Optimized multi-entry lorebook splitting all sections and characters 12, 13, and 14 into separate, responsive index rows.",
  "entries": {}
}

entry_id = 1
for name_comment, data in entries_accumulator.items():
    chub_lorebook["entries"][str(entry_id)] = {
        "uid": entry_id,
        "key": data["keys"],
        "keysecondary": [],
        "comment": name_comment,
        "content": data["content"],
        "constant": False,
        "selective": False,
        "selectiveLogic": 0,
        "addationToChat": 0,
        "order": entry_id,
        "probability": 100,
        "use_regex": False,
        "embedding_vector": []
    }
    entry_id += 1

# Save inside local Termux data partition
with open("Antahpura_Splitted_Core.json", "w", encoding="utf-8") as f:
    json.dump(chub_lorebook, f, indent=2, ensure_ascii=False)

# Push straight onto system device download folder track
os.system("cp Antahpura_Splitted_Core.json /sdcard/Download/")
print(f"\n✅ SUCCESS: Roster fully parsed! Created {entry_id - 1} individual, isolated entry slots.")
print("Location: /sdcard/Download/Antahpura_Splitted_Core.json")
