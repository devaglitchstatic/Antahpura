import json
from pathlib import Path

SOURCE = Path('Antahpura_V2.json')
OUTPUT = Path('Antahpura_V4_Lorebook.json')

if not SOURCE.exists():
    raise SystemExit('❌ Antahpura_V2.json not found in ~/Antahpura')

with SOURCE.open('r', encoding='utf-8') as f:
    data = json.load(f)

# --------------------------------------------------
# Metadata
# --------------------------------------------------
data['name'] = 'Antahpura: Imperial Tantric Court Lorebook'
data['tagline'] = (
    'A constitutional worldbook of royal courts, temple lineages, ritual disciplines, '
    'sacred architecture, and Monitoring Plinth telemetry in a classical Indo-Persian '
    'and Sanskritic empire.'
)
data['description'] = (
    'Unified lorebook containing character constitutions, relationship matrices, '
    'temple architecture, ritual gatherings, esoteric scene templates, seasonal cycles, '
    'Monitoring Plinth mechanics, somatic telemetry, and Purna Siddhi progression '
    'for a classical imperial Indian fantasy chronicle.'
)

# --------------------------------------------------
# Global rename helper
# --------------------------------------------------
def deep_replace(obj):
    if isinstance(obj, str):
        replacements = {
            'Maharaj Deva': 'Maha Deva',
            'Maharaja Deva': 'Maha Deva',
            'Maharaj': 'Maha Deva',
            'Maharaja': 'Maha Deva',
            'Princess Kuma Ree Kama': 'Princess Kuma Ree Rati',
            'Kuma Ree Kama': 'Kuma Ree Rati'
        }
        for old, new in replacements.items():
            obj = obj.replace(old, new)
        return obj
    elif isinstance(obj, list):
        return [deep_replace(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: deep_replace(v) for k, v in obj.items()}
    return obj

data = deep_replace(data)

entries = data.setdefault('entries', {})

# --------------------------------------------------
# Canonical character patch
# --------------------------------------------------
if '2' in entries:
    entries['2']['comment'] = 'Entry 2: Maha Deva Bible Node'
    content = entries['2'].get('content', '')
    content = content.replace('Identity: [Name]', 'Identity: Maha Deva')
    entries['2']['content'] = content

if '3' in entries:
    entries['3']['comment'] = 'Entry 3: Princess Kuma Ree Rati Bible Node'
    content = entries['3'].get('content', '')
    content = content.replace('Identity: [Name]', 'Identity: Kuma Ree Rati')
    entries['3']['content'] = content

# --------------------------------------------------
# New constitutional entries
# --------------------------------------------------
new_entries = {
    '26': {
        'uid': 26,
        'key': ['temple','devalaya','garbhagriha','mandapa','khajuraho','konark','kamakhya','tarapith','ghat','forest shrine','cremation ground'],
        'keysecondary': [],
        'comment': 'Temple Architecture and Sacred Geography',
        'content': 'Antahpura recognizes multiple ritual environments: the Garbhagriha (inner sanctum), the Mandapa (ritual pavilion), the Vasa-Griha courtyard, river ghats for ceremonial bathing, forest Kaula shrines, cremation-ground meditation fields, subterranean Guha chambers, palace zenana halls, and royal procession routes. Khajuraho, Konark, Kamakhya, and Tarapith function as architectural archetypes that shape scene generation and ritual progression.',
        'constant': True,
        'selective': False,
        'selectiveLogic': 0,
        'addationToChat': 0,
        'order': 26,
        'probability': 100,
        'use_regex': False,
        'embedding_vector': []
    },
    '27': {
        'uid': 27,
        'key': ['mahashivaratri','abhisheka','shahi snan','rasa lila','kaula gathering','panchamakara','festival','pilgrimage','procession'],
        'keysecondary': [],
        'comment': 'Ritual Gatherings and Court Festivals',
        'content': 'Major gatherings include the Royal Mahashivaratri Abhisheka, Shahi Snan river ceremonies, Rasa-Lila devotional festivals, Kaula forest convocations, Panchamakara initiation feasts, temple music assemblies, pilgrimage receptions, seasonal equinox rites, monsoon consecration ceremonies, and royal torch processions. Public gatherings emphasize architecture, chant, procession, and political legitimacy; hidden gatherings emphasize initiation, discipline, secrecy, and lineage transmission.',
        'constant': True,
        'selective': False,
        'selectiveLogic': 0,
        'addationToChat': 0,
        'order': 27,
        'probability': 100,
        'use_regex': False,
        'embedding_vector': []
    },
    '28': {
        'uid': 28,
        'key': ['scene engine','ritual template','consecration','pranayama','mantra','yantra','grounding'],
        'keysecondary': [],
        'comment': 'Esoteric Scene Architecture',
        'content': 'All major ritual scenes follow five movements: Act I - Material and Spatial Consecration; Act II - Somatic Regulation and Activation; Act III - Sonic and Geometric Resonance; Act IV - Metaphysical Threshold; Act V - Grounding and Integration. Scene generation selects a location, season, active guru, active disciple, discipline, monitoring roles, and current Purna Siddhi stage before narrative execution.',
        'constant': True,
        'selective': False,
        'selectiveLogic': 0,
        'addationToChat': 0,
        'order': 28,
        'probability': 100,
        'use_regex': False,
        'embedding_vector': []
    },
    '29': {
        'uid': 29,
        'key': ['monitoring plinth','nirikshana','telemetry','exhaustion','aftercare','purna siddhi'],
        'keysecondary': [],
        'comment': 'Monitoring Plinth Ritual Wiring',
        'content': 'The Antahpura Monitoring Plinth is administered through the constitutional roles of the characters according to rank and discipline. Maha Deva holds sovereign confirmation authority; Princess Kuma Ree Rati oversees Darshana metrics; Padma governs recovery and aftercare; Tarana monitors voice and breath resonance; Roxana monitors posture and restraint integrity; Jahzara monitors threshold vigilance; Sevda and Malika monitor stillness and spatial transition. All readings update Purna Siddhi progression, exhaustion, relationship values, and ritual availability.',
        'constant': True,
        'selective': False,
        'selectiveLogic': 0,
        'addationToChat': 0,
        'order': 29,
        'probability': 100,
        'use_regex': False,
        'embedding_vector': []
    },
    '30': {
        'uid': 30,
        'key': ['somatic matrix','rakta','gharmah','bodhi lalika','ojas','lajja avarana','svairini rasa','bhairavi avesha','samarasa laya'],
        'keysecondary': [],
        'comment': 'Somatic Telemetry and Character Monitoring Roles',
        'content': 'The Monitoring Plinth tracks four observable domains: Rakta-Chalan (circulatory rhythm), Gharmah-Bindu (perspiration distribution), Bodhi-Lalika (breath and vocal moisture), and Ojas-Vindu (posture, abdominal stability, ocular clarity, and stillness). The four progression phases remain Lajja-Avarana, Svairini-Rasa, Bhairavi-Avesha, and Samarasa-Laya. Characters interpret these readings through their own lineages and disciplines rather than through anonymous institutional authority.',
        'constant': True,
        'selective': False,
        'selectiveLogic': 0,
        'addationToChat': 0,
        'order': 30,
        'probability': 100,
        'use_regex': False,
        'embedding_vector': []
    }
}

for k, v in new_entries.items():
    entries.setdefault(k, v)

with OUTPUT.open('w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print('✅ Antahpura_V4_Lorebook.json generated successfully.')
print(f'Entries: {len(entries)}')
print(f'Output: {OUTPUT.resolve()}')
