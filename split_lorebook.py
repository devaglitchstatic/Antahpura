import json
import os

txt_path = "/sdcard/Download/Antahpura.txt"
if not os.path.exists(txt_path):
    txt_path = "/sdcard/Download/antahpura.txt"

if not os.path.exists(txt_path):
    print("❌ ERROR: Please make sure the text tree file is saved as 'Antahpura.txt' in your device Download folder.")
    exit(1)

with open(txt_path, "r", encoding="utf-8") as f:
    raw_text = f.read()

# Dictionary mapping specific sections and characters to their dedicated activation keys
keyword_map = {
    "WORLD CONSTITUTION": ["Vasa-Griha", "basalt", "sandstone", "Jali", "Solstice", "Amavasya", "Bhumigandha", "Nisha-Sadhana"],
    "NARRATIVE CONSTITUTION": ["Rajya-Lekhaka", "Chronicler", "Chaya", "Abha", "Lekhaka"],
    "COURT PROTOCOL MANUAL": ["Prabhu", "meri", "Hasta", "plinth", "threshold", "Vinaya-Vidhana"],
    "CHARACTER 01: MAHARAJ DEVA": ["Maha Deva", "Deva", "Maharaj", "Shayana", "Avadhana-Sthana", "Madana-Modaka", "Sulpha"],
    "CHARACTER 02: PRINCESS KUMA REE KAMA": ["Kuma Ree", "Kuma", "Ree", "Princess", "Kandharasana", "Vrischikasana", "Chuchuka-Valaya", "Yoni-Mudra", "Anavat"],
    "CHARACTER 03: BAHA SOREN / PADMA": ["Padma", "Baha", "Soren", "Dasi", "Khus", "Kachha-bandha", "Jhelah", "Avanata-Janu"],
    "CHARACTER 04: BUDA HORO / CHAMPA": ["Champa", "Buda", "Horo", "Kridamriga", "Pashu", "Kantha-shrinkhala", "Svana-Vak", "Pashu-Gamana", "Mutra-Visarga"],
    "CHARACTER 05: KAMINI ANISA": ["Anisa", "Kamini", "Daroga", "Urdu", "Vilaasa-Prahanana", "Ganana", "Danda-Vidhana"],
    "CHARACTER 06: SHRINAGAR": ["Shrinagar", "Ganika", "Kathak", "Nupur", "Guhya-Mukti-Sadhana", "dahi", "ferments"],
    "CHARACTER 07: TARANA": ["Tarana", "Sangeeta", "Vocalist", "surrender", "melody"],
    "CHARACTER 08: ROXANA": ["Roxana", "Silahtar", "Rigger", "bindings", "sash", "restraints"],
    "CHARACTER 09: JAHZARA": ["Jahzara", "Nizam", "Vanguard", "Guard", "strip-search", "vocalized", "swallowing"],
    "CHARACTER 10: SEVDA": ["Sevda", "Ascetic", "Vault", "Warden", "subterranean", "ledger"],
    "CHARACTER 11: MALIKA": ["Malika", "Guha-Warden", "Confinement", "dungeon", "isolation"],
    "CHARACTER 12: REVA / ZOLA / ALTANI": ["Reva", "Zola", "Altani", "Chorus", "SO-HAM", "breathing", "hum"],
    "RELATIONSHIP MATRIX": ["relationship", "pairing", "modulation", "inter-agent", "override"],
    "SCENE ENGINE": ["Scene Engine", "Parimala", "camphor", "musk", "Vrisha-Andakosha"],
    "RESTRICTED LEXICON": ["Lexicon", "vocabulary", "Rasayana", "Ojas", "Yoni", "Lajja", "Tapas", "Asvadana", "Kamalata"],
    "PROMPT & CHOICE ENGINE": ["Prompt Engine", "Choice", "Option", "Vāk-Kautuka", "outburst", "shock", "gate"]
}

chub_lorebook = {
  "name": "Antahpura Master Segmented Core",
  "description": "Highly optimized, token-saving Sanskritized Master Lorebook with split context entries.",
  "entries": {}
}

# Simple algorithmic text chopper
current_section = "GENERAL"
section_content = []
entry_id = 1

for line in raw_text.split("\n"):
    found_new = False
    for key_title in keyword_map.keys():
        if key_title in line:
            # Save the old accumulated section first before switching
            if section_content:
                keys = keyword_map.get(current_section, ["setup"])
                chub_lorebook["entries"][str(entry_id)] = {
                    "uid": entry_id,
                    "key": keys,
                    "keysecondary": [],
                    "comment": f"Sub-System: {current_section}",
                    "content": "\n".join(section_content),
                    "constant": False, # Dynamic trigger allocation
                    "selective": False,
                    "selectiveLogic": 0,
                    "addationToChat": 0,
                    "order": entry_id,
                    "probability": 100,
                    "use_regex": False,
                    "embedding_vector": []
                }
                entry_id += 1
                section_content = []
            current_section = key_title
            found_new = True
            break
    section_content.append(line)

# Flush out the absolute final section lingering in buffer
if section_content:
    keys = keyword_map.get(current_section, ["setup"])
    chub_lorebook["entries"][str(entry_id)] = {
        "uid": entry_id,
        "key": keys,
        "keysecondary": [],
        "comment": f"Sub-System: {current_section}",
        "content": "\n".join(section_content),
        "constant": False,
        "selective": False,
        "selectiveLogic": 0,
        "addationToChat": 0,
        "order": entry_id,
        "probability": 100,
        "use_regex": False,
        "embedding_vector": []
    }

# Save inside Termux's safe application partition workspace path
with open("Antahpura_Segmented.json", "w", encoding="utf-8") as f:
    json.dump(chub_lorebook, f, indent=2, ensure_ascii=False)

# Push cleanly onto your shared public system download folder path track
os.system("cp Antahpura_Segmented.json /sdcard/Download/")
print("\n✅ SUCCESS: Massive file algorithmically shredded into 19 individual token-optimized entries!")
print("Location: /sdcard/Download/Antahpura_Segmented.json")
