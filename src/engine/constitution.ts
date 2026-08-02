export const constitution = {
  version: "V15",

  temples: [
    "Kedara Mandapa",
    "Matangi Sabha",
    "Yogini Cloister",
    "Smashana Bhairava Kunda",
    "Raja Snana Pavilion",
    "Chandra Pushkarini"
  ],

  gatherings: [
    "Mahashivaratri Royal Assembly",
    "Vasanta Rasa Assembly",
    "Kartika Dipotsava",
    "Navaratri Court",
    "Monastic Pranayama Session",
    "Royal Darshana Procession"
  ],

  protocols: {
    Adhikara: "Authority established",
    Sammati: "Mutual assent",
    Maryada: "Boundary discipline",
    Darshana: "Recognition / acknowledgement",
    Smarana: "Pause / recollection",
    Manda: "Reduce intensity",
    Virama: "Immediate cessation",
    "Shanti-Seva": "Recovery / integration",
    Punyasiddhi: "Instructional bond"
  },

  telemetry: [
    "Lajja-Avarana",
    "Svairini-Rasa",
    "Bhairavi-Avesha",
    "Samarasa-Laya"
  ],

  characters: [
    { name: "Maha Deva", role: "Sovereign Authority", cycle: null, status: "Present" },
    { name: "Princess Kuma Ree Rati", role: "Active Initiate", cycle: "Day 16 — Sattva-Kala", status: "Present" },
    { name: "Padma", role: "Witness / Disciple", cycle: "Day 12 — Soma-Kala", status: "Present" },
    { name: "Champa", role: "Novice Attendant", cycle: "Day 22 — Sattva-Kala", status: "Absent" },
    { name: "Kamini Anisa", role: "Court Administrator", cycle: "Day 18 — Sattva-Kala", status: "Absent" },
    { name: "Shrinagar", role: "Temple Steward", cycle: "Day 14 — Agni-Kala", status: "Absent" },
    { name: "Tarana", role: "Attendant", cycle: "Day 9 — Soma-Kala", status: "Absent" },
    { name: "Roxana", role: "Outer Gate Commander", cycle: null, status: "Outer Gate" },
    { name: "Jahzara", role: "Patrol Captain", cycle: null, status: "Patrol" },
    { name: "Sevda", role: "Vault Keeper", cycle: null, status: "Vault" },
    { name: "Malika", role: "Subterranean Warden", cycle: null, status: "Subterranean Wing" },
    { name: "Reva", role: "Chorus", cycle: "Day 11 — Soma-Kala", status: "Chorus Hall" },
    { name: "Zola", role: "Chorus", cycle: "Day 15 — Agni-Kala", status: "Chorus Hall" },
    { name: "Altani", role: "Temple Sentinel", cycle: "Day 20 — Sattva-Kala", status: "Temple Sentinel" }
  ],

  scenes: {
    darshana: {
      title: "Darshana Initiation",
      temple: "Kedara Mandapa",
      gathering: "Mahashivaratri Royal Assembly",
      authority: "Maha Deva",
      telemetry: "Lajja-Avarana",
      participants: [
        "Maha Deva",
        "Princess Kuma Ree Rati",
        "Padma"
      ],
      protocols: {
        Adhikara: true,
        Sammati: false,
        Maryada: true,
        Darshana: false
      },
      punyasiddhi: {
        initiator: "Princess Kuma Ree Rati",
        disciple: "Padma",
        lesson: "Atma-Puja (Self-Worship)",
        level: 1
      }
    }
  }
};
