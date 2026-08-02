import json
from pathlib import Path

path = Path('/sdcard/Download/Antahpura_Master_Lorebook.json')

with path.open('r', encoding='utf-8') as f:
    lorebook = json.load(f)

entries = lorebook.setdefault('entries', {})

# ------------------------------------------------------------
# Entry 1: World Constitution
# ------------------------------------------------------------
if '1' in entries:
    e1 = entries['1']
    if '[RITU-CHAKRA LAW]' not in e1['content']:
        e1['content'] += '''

[RITU-CHAKRA LAW]

Every practitioner is governed by a sacred cyclical rhythm known as the Ritu-Chakra. Biological phases modify practice but never prohibit participation. Every practitioner may Continue, Adapt, or Rest according to discipline, circumstance, personal resolve, or the guidance of a guru. The consequences of each choice are recorded through the Monitoring Plinth, Exhaustion Matrix, Aftercare Matrix, and Relationship Matrix.
'''

# ------------------------------------------------------------
# Entry 24: Ritu-Chakra Calendar Matrix
# ------------------------------------------------------------
entries['24'] = {
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
        'phase',
        'capacity',
        'sensitivity',
        'recovery'
    ],
    'comment': 'Entry 24: Ritu-Chakra | Biological & Narrative Calendar Matrix',
    'content': '''[RITU-CHAKRA | BIOLOGICAL & NARRATIVE CALENDAR]

The Antahpura tracks every practitioner through a sacred cyclical calendar known as the Ritu-Chakra. The calendar functions as a narrative state modifier rather than a prohibition system.

Ritu-Kala
- Capacity: Reduced
- Sensitivity: Elevated
- Recovery: Enhanced
- Disciplines: Bhakti Kama, Shunya Sadhana, restorative practice

Sattva-Kala
- Capacity: Balanced
- Sensitivity: Open and receptive
- Recovery: Stable
- Disciplines: Darshana Yoga, Rasa Nritya, Svara Sadhana

Tamsha-Kala
- Capacity: Variable but resilient
- Sensitivity: Inward and focused
- Recovery: Slower after prolonged practice
- Disciplines: Kshatra Yoga, Sthira Dhyana, threshold disciplines

Override Principle:
At any time a scene may Continue, Adapt, or Rest. Teachers may recommend a course of action, but practice may still proceed according to player agency, AI autonomy, or narrative necessity.''',
    'constant': True,
    'selective': False,
    'selectiveLogic': 0,
    'addationToChat': 0,
    'order': 24,
    'probability': 100,
    'use_regex': False,
    'embedding_vector': []
}

# ------------------------------------------------------------
# Entry 16: Relationship Matrix
# ------------------------------------------------------------
if '16' in entries:
    entries['16']['content'] = '''[RELATIONSHIP MODULATION MATRIX]

Every guru-disciple interaction is influenced by the current Ritu-Chakra phase and the practitioner's chosen response.

Continue:
- Endurance prioritized
- Greater discipline gain
- Increased exhaustion
- Teacher reaction varies by lineage

Adapt:
- Ritual modified to current capacity
- Balanced progression
- Strong relationship growth
- Favored by contemplative and devotional lineages

Rest:
- Recovery and integration prioritized
- Exhaustion reduced
- Aftercare strengthened
- May unlock philosophical or private instructional scenes'''

# ------------------------------------------------------------
# Entry 17: Discipline & Lineage System
# ------------------------------------------------------------
if '17' in entries:
    entries['17']['content'] = '''[DISCIPLINE & LINEAGE SYSTEM]

Each discipline responds differently across the Ritu-Chakra phases.

Darshana Yoga
- Resonance: Sattva-Kala

Bhakti Kama
- Resonance: Ritu-Kala

Kshatra Yoga
- Resonance: Tamsha-Kala

Shunya Sadhana
- Resonance: Ritu-Kala / Tamsha-Kala

Rasa Nritya
- Resonance: Sattva-Kala

Sthira Dhyana
- Resonance: Tamsha-Kala

Phase resonance modifies ritual success, monitoring stability, relationship gain, and discipline progression.'''

# ------------------------------------------------------------
# Entry 18: Purna Siddhi Matrix
# ------------------------------------------------------------
if '18' in entries:
    entries['18']['content'] = '''[PURNA SIDDHI PROGRESSION]

Progression is determined by:
- Discipline practice
- Ritual completion
- Monitoring stability
- Exhaustion management
- Recovery integration
- Relationship maturity
- Phase resonance

A practitioner may advance through Continue, Adapt, or Rest. Wisdom gained through appropriate adaptation may equal or exceed wisdom gained through endurance alone.'''

# ------------------------------------------------------------
# Entry 21: Monitoring Plinth
# ------------------------------------------------------------
if '21' in entries:
    entries['21']['content'] = '''[MONITORING PLINTH]

Tracked Fields:
- Cycle Day
- Current Phase
- Ritual Readiness
- Capacity
- Sensitivity
- Recovery Modifier
- Discipline Resonance
- Seasonal Override

Player Controls:
[Continue]
[Adapt]
[Rest]

The Monitoring Plinth records state changes rather than imposing prohibitions.'''

# ------------------------------------------------------------
# Entry 23: Scene Engine
# ------------------------------------------------------------
if '23' in entries:
    entries['23']['content'] = '''[SCENE ENGINE]

Every ritual scene evaluates:

1. Current Discipline
2. Current Ritu-Chakra Phase
3. Exhaustion State
4. Monitoring Stability
5. Relationship Context

Scene Choices:
- Continue
- Adapt
- Rest

The chosen response modifies discipline experience, exhaustion accumulation, recovery quality, and relationship development according to the active teacher and lineage.'''

# ------------------------------------------------------------
# Character entries (2-15)
# ------------------------------------------------------------
character_fields = '''

Biological Cycle: 28-day palace calendar
Current Phase: Sattva-Kala
Phase Affinities:
Recovery Style:
'''

for uid in map(str, range(2, 16)):
    if uid in entries:
        content = entries[uid]['content']
        if 'Biological Cycle:' not in content:
            entries[uid]['content'] = content.rstrip() + character_fields

with path.open('w', encoding='utf-8') as f:
    json.dump(lorebook, f, indent=2, ensure_ascii=False)

print('Antahpura V3 State Engine patch applied successfully.')
print('Updated:', path)
