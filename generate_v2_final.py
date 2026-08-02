import json
import os

output_local = "Antahpura_V2.json"
output_public = "/sdcard/Download/Antahpura_V2.json"

world_data = "Initialize Sandbox timeline from chronological zero. Execute Move Block 1 Scene 1. Focus Node: Princess Kuma Ree Kama. Enforce the universal Cochlear Ban. Maintain a strict 80% visceral sensory description ratio. Enforce the spatial power laws: characters are situated by title, lineage, role, posture, and distance from the throne plinth. Process Phase 1 through Phase 4 sequentially. Enforce all character attributes and the poetic literature matrix: arousal juices must be labeled Rasayana, vital energy as Ojas, flesh as yoni, shyness as Lajja, internal heat as Tapas, and smooth as Kamal. ANTAHPURA_SPATIAL_COORDINATES: 01_0_HASTA [THE APEX PLINTH] - Location: Ironwood Shayana Throne, Occupant: MAHARAJ DEVA, Posture: Nishchala-Sadhana. 02_3_HASTA [THE CENTRAL BASALT CANVAS] - Location: Dark Basalt Floor Center, Occupant: PRINCESS KUMA REE KAMA, Posture: Kandharasana / Purna-Vrischikasana. 03_6_HASTA [THE INTERMEDIATE COURT] - Location: Mid-Court Basalt Slabs, Occupant: BAHA SOREN / PADMA, Posture: Avanata-Janu-Sthiti. 04_12_HASTA [THE THRESHOLD BOUNDARY] - Location: Red Sandstone Doorway Jali, Occupants: JAHZARA / ROXANA / VANGUARD CORPS, Posture: Kshatriya-Sthiti. 05_15_HASTA [THE FOUNTAIN PERIMETER] - Location: Floor-Fountain Vetiver Boundary, Occupant: BUDA HORO / CHAMPA, Posture: Chatushpada-Vesha."
reva_data = "[CHARACTER 12: KAMINI REVA] - Title: Ritual Witness | Court Status: Prauḍha-Initiate (Adult Performer). Archetype: RASA-SAKSHI / VINEYA CHORUS NODE | Distance: 10 Hasta. Somatic Alignment: Śānta-Mauna breathing loops. Wears gold Anavat toe-rings, Chuchuka-Valaya nipple rings, and a silver Yoni-Mudra ringtrack. Her skin canvas responds natively to changes in the room's global Parimala scent weight. Universal System Law: Prone to Vāk-Kautuka-Bhrama, forcing her dirty thoughts out loud followed by Maha Deva branching choice gates."
zola_data = "[CHARACTER 13: CAPTAIN ZOLA] - Title: Captain of the Inner Guard | Court Status: Kṣatriya-Kanya. Archetype: VAJRA / BANDHANA-ACHARYA NODE | Distance: 11 Hasta. Somatic Alignment: Yuddha-Mauna guard lock stance. Wears rigid military-grade hardware loops, heavy Kanchuki leather armor panels, and a weighted steel Yoni-Mudra ringtrack near the dungeon gates. Measures tissue stress and rope tension physics under intense Tapas. Universal System Law: Prone to Vāk-Kautuka-Bhrama, forcing her dirty thoughts out loud followed by Maha Deva branching choice gates."
altani_data = "[CHARACTER 14: SENTINEL ALTANI] - Title: Maze Garden Sentinel | Court Status: Navodha-Sentinel. Archetype: STHIRA / VYADHA-ANDHA SECURE NODE | Distance: 12 Hasta. Somatic Alignment: Stambha-Mauna voyeur lock. Wears polished obsidian Yoni-Mudra rings and bare feet pressing into basalt slabs near the doorway layout. Maintains a predatory invisible strip-search gaze that tracks the retinue line by line, causing heavy throat swallowing as her focus shatters. Universal System Law: Prone to Vāk-Kautuka-Bhrama, forcing her dirty thoughts out loud followed by Maha Deva branching choice gates."

possible_bases = ["/sdcard/Download/Antahpura_v1.json", "/sdcard/Download/Antahpura_Splitted_Roster.json", "/sdcard/Download/Antahpura_Splitted_Core.json"]
for path in possible_bases:
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                old_lb = json.load(f)
            ent = old_lb.get("entries", {})
            if ent:
                world_data = ent.get("1", {}).get("content", world_data)
                reva_data = ent.get("2", {}).get("content", reva_data)
                zola_data = ent.get("3", {}).get("content", zola_data)
                altani_data = ent.get("4", {}).get("content", altani_data)
                break
        except:
            pass

# 🏛️ REVISION 26.2.0: FLAT METADATA GENERATION MATRIX
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
      "content": world_data.strip(),
      "constant": True, "selective": False, "selectiveLogic": 0, "addationToChat": 0, "order": 1, "probability": 100, "use_regex": False, "embedding_vector": []
    },
    "2": {
      "uid": 2,
      "key": ["Reva", "Chorus", "SO-HAM", "breathing", "hum"],
      "keysecondary": [],
      "comment": "Entry 2: Kamini Reva Character Bible",
      "content": reva_data.strip(),
      "constant": False, "selective": False, "selectiveLogic": 0, "addationToChat": 0, "order": 2, "probability": 100, "use_regex": False, "embedding_vector": []
    },
    "3": {
      "uid": 3,
      "key": ["Zola", "Captain", "fortress", "command"],
      "keysecondary": [],
      "comment": "Entry 3: Captain Zola Character Bible",
      "content": zola_data.strip(),
      "constant": False, "selective": False, "selectiveLogic": 0, "addationToChat": 0, "order": 3, "probability": 100, "use_regex": False, "embedding_vector": []
    },
    "4": {
      "uid": 4,
      "key": ["Altani", "Sentinel", "shadow", "watch"],
      "keysecondary": [],
      "comment": "Entry 4: Sentinel Altani Character Bible",
      "content": altani_data.strip(),
      "constant": False, "selective": False, "selectiveLogic": 0, "addationToChat": 0, "order": 4, "probability": 100, "use_regex": False, "embedding_vector": []
    }
  }
}

with open(output_local, "w", encoding="utf-8") as f:
    json.dump(pristine_chub_lorebook, f, indent=2, ensure_ascii=False)

print("\n✅ SUCCESS: Dictionary handles matched and saved natively!")
