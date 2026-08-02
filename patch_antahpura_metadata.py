import json
from pathlib import Path

path = Path('/sdcard/Download/Antahpura_Master_Lorebook.json')

with path.open('r', encoding='utf-8') as f:
    lorebook = json.load(f)

# ------------------------------------------------------------------
# Chub-facing metadata
# ------------------------------------------------------------------
lorebook['name'] = 'Antahpura: Purna Siddhi Engine'
lorebook['tagline'] = (
    'A classical Indo-Persian royal court and gurukula simulation driven by '
    'ritual practice, lineage, discipline, and dynamic state progression.'
)
lorebook['description'] = (
    'Antahpura is a modular lorebook for a historical-fantasy royal court and '
    'gurukula simulation. Every character belongs to a lineage of practice, '
    'every scene functions as a ritual lesson or philosophical encounter, and '
    'progression is governed by discipline, relationship, monitoring, '
    'exhaustion, recovery, and the Ritu-Chakra calendar.'
)

# Chub-compatible tags (many frontends read either "tags" or ignore it harmlessly)
lorebook['tags'] = [
    'historical fantasy',
    'indian classical',
    'indo-persian',
    'royal court',
    'harem politics',
    'gurukula',
    'ritual',
    'philosophy',
    'sanskrit',
    'character progression',
    'state machine',
    'dynamic scenes',
    'lorebook'
]

# ------------------------------------------------------------------
# Entry 24: Ritu-Chakra (Biological & Narrative Calendar)
# ------------------------------------------------------------------
entry24 = {
    'uid': 24,
    'key': [
        'Ritu-Chakra',
        'Ritu-Kala',
        'Sattva-Kala',
        'Tamsha-Kala',
        'calendar',
        'cycle',
        'Varsha Ritu',
        'Amavasya'
    ],
    'keysecondary': [
        'biological rhythm',
        'ritual timing',
        'practice calendar',
        'phase',
        'capacity',
        'sensitivity',
        'recovery'
    ],
    'comment': 'Entry 24: Ritu-Chakra | Biological & Narrative Calendar Matrix',
    'content': '''[RITU-CHAKRA | BIOLOGICAL & NARRATIVE CALENDAR]

The Antahpura tracks every practitioner through a sacred cyclical calendar known as the Ritu-Chakra. The calendar functions as a narrative state modifier rather than a prohibition system.

Core Principle:
No phase prevents participation. A phase alters the texture, cost, endurance, recovery, and philosophical emphasis of practice.

PHASES

Ritu-Kala
- Emphasis: purification, breathwork, restoration, introspection.
- Capacity: reduced endurance.
- Sensitivity: elevated.
- Recovery: enhanced.
- Disciplines: Bhakti Kama, Shunya Sadhana, restorative yoga.

Sattva-Kala
- Emphasis: study, movement, artistic practice, temple ritual.
- Capacity: balanced.
- Sensitivity: open and receptive.
- Recovery: normal.
- Disciplines: Darshana Yoga, Rasa Nritya, Svara Sadhana.

Tamsha-Kala
- Emphasis: vigil, endurance, contemplation, silence.
- Capacity: variable but resilient.
- Sensitivity: inward and focused.
- Recovery: slower after prolonged practice.
- Disciplines: Kshatra Yoga, Sthira Dhyana, threshold disciplines.

Player / AI Override:
At any time a scene may Continue, Adapt, or Rest. Teachers may recommend a course of action, but practice may still proceed according to player agency, AI autonomy, or narrative necessity.

Monitoring Plinth Fields:
- Cycle Day
- Current Phase
- Ritual Readiness
- Capacity
- Sensitivity
- Recovery Modifier
- Discipline Resonance
- Seasonal Override''',
    'constant': True,
    'selective': False,
    'selectiveLogic': 0,
    'addationToChat': 0,
    'order': 24,
    'probability': 100,
    'use_regex': False,
    'embedding_vector': []
}

lorebook.setdefault('entries', {})['24'] = entry24

with path.open('w', encoding='utf-8') as f:
    json.dump(lorebook, f, indent=2, ensure_ascii=False)

print('Patched lorebook metadata and added Entry 24.')
print('Saved:', path)
