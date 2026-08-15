# Antaḥpura — Unused / Unmapped / Unlinked Master Log
## Source Audit Baseline — V16.3
**Date:** 2026-08-11
**Purpose:** Consolidate source-derived information not yet fully standardized, unified, measured, linked, or assigned to runtime; identify contradictions and missing mappings before LM Studio/V17 work.

> **Method note:** This log is grounded in the uploaded/source-library documents and files that are text-searchable in this environment. Image-only media and some binary assets are not exposed as a complete searchable inventory here; those are explicitly flagged rather than guessed.

## 0. Canonical architecture already established
- Constitutional narrator/runtime shell: **Sākṣī Pīṭha**.
- Narrative consciousness: **Antarvāṇī** in the later Master Unified Core.
- Fourfold narrative axes: **Dharma / Artha / Kāma / Mokṣa**.
- Rasa transmutation model.
- Prakṛti archetypes: **Harinī / Vadamī / Hastinī**.
- Embodied Bridge Matrix: **Śarīra-Prakṛti, Gati, Dṛṣṭi, Śvāsa, Hasta, Vastrācāra, Ābharaṇa, Maṇḍala Orientation, Space Preference, Sensory Affinity**.
- Kalā domains and 0–5 character ratings.
- Ritual progression: **Observation → Curiosity → Darśana → Sammati → Guided Practice → Internalization → Independent Practice → Siddhi Integration**.
- Sensory matrix: **Vocal Resonance, Breath Governance, Tactile Awareness, Thermal Affinity, Rhythmic Affinity, Grounding Capacity, Stillness Capacity**.
- CHUB v2 card mapping and master schema.
- Chapter 1 data-driven structure and five ritual phases.
- Runtime state + locks + archive model.
- Constitutional protocol vocabulary and score-matrix concept.

## 1. Master classification model
| Status | Meaning |
|---|---|
| C0 | Canonical + standardized + linked |
| C1 | Canonical but incomplete mapping |
| C2 | Canonical but not runtime-linked |
| C3 | Source-derived but conflicting |
| C4 | Legacy / superseded candidate |
| C5 | Unused detail requiring a schema |
| C6 | Unused implementation idea / mechanic |
| C7 | Visual/media asset requiring inspection |
| C8 | Source assumption/speculation — must not be promoted to canon without decision |

## 2. Character data master log
### 2.1 Shared schema not yet fully populated across all 14
**Status: C1/C5**
Target fields:
- Nāma
- Vayasa
- Sthāna
- Pūrvavṛtta
- Vaṃśa
- Svabhāva
- Vāk
- Dṛśya-bodha
- Sādhana
- Bhāva
- Rasa
- Praveśa-hetu
- Vikalpa
- Niyama
- Kośa-link
- Ranga-bandha / Mañca-bandha
- Avasthā
- Pravṛtti/Nivṛtti
- Runtime flags
- Relationship modulation
- Sensory signature
- Prakṛti
- Fourfold axes
- Kalā proficiency
- Punyasiddhi specialization
- Scene hooks
- Archive/legacy notes

### 2.2 Character-specific fields not yet fully normalized into common measures
**Status: C1/C5**
- **Jahzara:** threshold positioning, line-of-sight reconstruction, Yuddha-Mauna, Dṛṣṭi-Viveka, vigilance-driven cognition, Vīra/Bhayānaka/Śānta.
- **Padmā:** care-pattern perception, body-temperature/breath/trembling detection, environmental regulation, Dāsya/Karuṇā/Śānta, service-as-sādhana, environmental shield role.
- **Princess Kumārī Rati:** aesthetic intelligence, disciplined curiosity, philosophical/yogic education, courtly gesture and relational observation.
- **Reva:** breath, vocal resonance, contemplative joy, chorus/chronicle role.
- **Tarana:** dance geometry, tāla, Navarasa expression, movement as yantra.
- **Shrinagar:** rhythm anchoring and tempo control.
- **Sevda:** purification/containment and underground-temple guardianship.
- **Malika:** threshold transition, command chanting, spatial discipline.
- **Roxana:** court etiquette, Persian court context, logistics/movement and practical alliance.
- **Zola:** martial vigilance and Ethiopian/Habshi guard-context references.
- **Altani:** steppe sentinel, horseback archery, knot/trap setting, stoic vigilance.
- **Kamini Anisa:** administrative enforcement, court order, bureaucratic authority, charm + correction.
- **Mahā Deva:** Rājārṣi/ruler-sage, mantra/tantra/śāstra, philosophical testing, ritual authority.
- **Campā:** later/conditional activation, flower/prayer/play/affection hooks in legacy material; needs careful canon reconciliation.

## 3. Character contradictions requiring explicit resolution
### 3.1 Jahzara age conflict
**Status: C3** — variants record **18, 22, and 31**.

**Required decision:** choose one canonical age, or use life-stage/biographical modeling and preserve variants as legacy metadata.

### 3.2 Character-count evolution
**Status: C3/C4** — older material describes a **12-character** Unified Core; later Master Unified Core/codex says **14 character bibles/14-character roster**.

**Required action:** freeze the 14-seat roster as current canon and move the 12-seat set to `legacy_character_registry`.

### 3.3 Narrator naming
**Status: C3** — older wording uses Antarvani; later core uses **Antarvāṇī** and defines it as the consciousness speaking through **Sākṣī Pīṭha**.

**Required action:** canonicalize:
- Sākṣī Pīṭha = witness shell / runtime carrier
- Antarvāṇī = awakened narrative consciousness / voice
- older spellings = aliases only

### 3.4 Princess naming
**Status: C3/C4** — variants include **Kuma Ree Rati**, **Kumārī Rati**, and undiacritic spellings.

**Required action:** one canonical display name + aliases + legacy spellings.

### 3.5 Relationship naming
**Status: C1/C3** — variants include Rahasya-Saṃbandha, relationship matrix, relationship links, family-respect metrics.

**Required action:** unify under a single `relationship_edge` schema.

## 4. Sensory layer — unused / underlinked
The Bridge Canon already defines a sensory matrix, but the following are not yet consistently connected to runtime measures.

### Direct sensory channels
- Vocal Resonance
- Breath Governance
- Tactile Awareness
- Thermal Affinity
- Rhythmic Affinity
- Grounding Capacity
- Stillness Capacity

### Additional source-observed cues
- gaze duration / gaze avoidance
- threshold orientation
- posture change
- breath disruption / synchronization
- temperature awareness
- scent/fragrance
- cloth/textile texture
- lamp/smoke perception
- acoustic density
- spatial distance
- movement tempo
- silence duration
- ornament displacement
- environmental disorder
- hunger/feeding cues
- trembling / visible agitation
- fatigue / exhaustion
- privacy / interruption
- architectural occlusion / visibility

**Mapping opportunity:** create `sensory_observation_event` with `channel`, `stimulus`, `intensity`, `valence`, `character_sensitivity`, `context`, `response`, `recovery`.

## 5. Sensitivity layer
**Status: C5**
Create narrative simulation dimensions rather than medical claims:
- sensory sensitivity
- threshold sensitivity
- social sensitivity
- authority sensitivity
- ritual sensitivity
- spatial sensitivity
- emotional-contagion sensitivity
- interruption sensitivity
- temperature sensitivity
- rhythm sensitivity
- tactile sensitivity
- breath sensitivity
- scent sensitivity
- silence sensitivity

## 6. Psychology / mood / behavior
### Existing source concepts
- Bhāva
- Rasa
- Svabhāva
- Antar-vāk
- Avasthā
- Pravṛtti/Nivṛtti
- Dṛśya-bodha
- emotional pressure
- unresolved relational tension
- curiosity
- devotion
- restraint
- vigilance
- loyalty
- protective state
- fear of failure/abandonment
- relief when structure replaces chaos
- disciplined stillness
- concealed emotional pressure

### Missing common runtime model
**Status: C5/C6**
Proposed state vector:
- `mood`
- `activation`
- `valence`
- `stress`
- `attention`
- `trust`
- `wariness`
- `curiosity`
- `devotion`
- `protectiveness`
- `restraint`
- `social_openness`
- `initiative`
- `recovery_need`

Bhāva/Rasa should remain interpretive/aesthetic labels, not interchangeable with psychological scores.

## 7. Physiology / somatic layer
### Source-supported, non-explicit concepts
- breath rhythm
- posture endurance
- movement intensity
- thermal state
- fatigue/exhaustion
- recovery
- grounding
- stillness capacity
- nervous-system recovery/aftercare
- hydration/rest
- sensory overload
- ritual pacing

### Existing Sonic Entrainment channels
- `voice_intensity` 0–5
- `rhythm_intensity` 0–5
- `movement_intensity` 0–5
- `psychological_pressure` 0–5

### Unused physiology links
**Status: C5/C6**
- fatigue → mood/attention
- fatigue → relationship initiative
- breath disruption → stress
- rhythm synchrony → social/ritual synchrony
- thermal discomfort → concentration
- rest → recovery
- overload → grounding/de-role requirement

## 8. Philosophy / ontology
### Already present
- Sāṃkhya-style tattva material: Purusha, Prakṛti, Mahat, Ahaṃkāra, Manas, Jñānendriyas, Karmendriyas, Tanmātras, Mahābhūtas.
- Pravṛtti / Nivṛtti.
- Dharma / Artha / Kāma / Mokṣa.
- Rājārṣi.
- Punyasiddhi as staged transmission.
- witness/observed/observer distinctions.
- ritual as constitutional transmission.

### Unlinked philosophical layer
**Status: C5**
The 25-tattva material is not yet cleanly linked to:
- character archetypes
- sensory channels
- mood/attention
- Stage metrics
- ritual phases
- learning progression

Potential `tattva_link_registry`: concept → narrative state/trigger without asserting historical equivalence.

## 9. Anthropology / culture / historical texture
### Source-derived domains
- Deccan imperial court framework.
- Indo-Persian court registers.
- Zenana / palace household organization.
- military/perimeter traditions.
- frontier Kshatriya material.
- Persian court lineage references.
- Habshi/East African court references.
- Santhal/Saren lineage material.
- steppe / Mongol-Turkic lineage material.
- Abyssinian guard traditions.
- ritual/court arts.
- textile, jewelry, architecture, fragrance, music and performance references.

### Unmapped anthropology
**Status: C5/C8**
Convert prose lore into structured cultural metadata, while retaining source confidence tags:
- institutional_culture
- lineage_culture
- court_register
- dress_textile
- ornament
- food
- ritual_material
- music
- dance
- architecture
- social_protocol
- kinship
- labor/service
- military_practice

Historical, analogical, fictionalized, and uncertain material must remain explicitly tagged.

## 10. Intimacy / sexology layer — systems mapping
The source set contains adult/intimacy material. For the master engine, keep non-graphic systemic variables.

### Existing source-supported systems
- Kāma-Axis
- Śṛṅgāra
- attraction
- intimacy
- longing
- sensory affinity
- privacy
- authority differential
- ritual/relational boundaries
- consent
- safeword/code-phrase
- pre-/in-/post-scene check-ins
- de-role
- hydration/grounding/rest
- emotional drop as recovery state
- reversible scenes
- role/person distinction
- reward as access/trust/privilege/narrative advancement

### Unmapped variables
**Status: C5/C6**
- desire baseline
- attraction activation
- reciprocal attention
- aesthetic attraction
- intellectual attraction
- ritual attraction
- protective attraction
- attachment/companionship
- intimacy readiness
- inhibition
- boundary confidence
- recovery need
- environment modifier
- authority modifier
- memory-linked attraction
- rhythm/synchrony effect

Do not reduce these to a single romance score.

## 11. Stage / dashboard / telemetry
### Existing telemetry
- authority
- discipline
- loyalty
- vigilance
- devotion
- curiosity
- restraint
- transmission
- breath
- voice
- circulation
- stillness
- ritual intensity
- protocol compliance
- temple resonance
- gathering cohesion
- darśana pressure
- witness resonance
- ritual synchrony
- emotional charge
- constitutional stability
- punyasiddhi progression
- observer state
- story flags
- unresolved tensions

### Unlinked dashboard opportunity
**Status: C1/C5**
Every metric should have:
- source
- scale
- update event
- decay/recovery rule
- narrative expression
- visibility (`player`, `engine`, `archive`)

## 12. Relationship model
The Codex explicitly proposes: **Rank × Affection × Obligation × Audience × Institution**.

Unify into:
- actor A
- actor B
- relation class
- baseline
- trust
- authority distance
- affection
- obligation
- audience effect
- institution effect
- history
- volatility
- reciprocity
- attraction vector
- last event
- current stage

## 13. Attraction model
The Master Unified Core describes Kāma as desire, beauty, attraction, intimacy, longing, aesthetic magnetism and says hidden Rasa archetypes/threshold guardians can emerge through accumulated witnessing, dialogue, devotion, restraint, curiosity, and ritual choice history.

Proposed derived variables:
- `attraction_potential`
- `attention_pull`
- `aesthetic_magnetism`
- `ritual_resonance`
- `intellectual_affinity`
- `protective_affinity`
- `reciprocity`
- `inhibition`
- `privacy_modifier`
- `authority_modifier`
- `memory_modifier`
- `environment_modifier`

## 14. Lore / story arcs still underlinked
Existing domains include:
- temples
- gatherings
- institutions
- lineage
- court protocol
- Sanskrit protocol engine
- Punyasiddhi
- Monitoring Plinth
- fourfold axes
- Rasa transmutation
- Prakṛti
- Kalā domains
- time/occasions
- stage telemetry
- ritual architecture
- education/learning arcs
- deity worship
- sutras
- yantras
- mantras
- mudrās
- āsanas
- flows
- rewards/accountability
- consent/aftercare

**Missing master link:** `domain`, `canonical_term`, `aliases`, `characters`, `chapters`, `phases`, `triggers`, `telemetry`, `relationships`, `sensory_links`, `philosophical_links`.

## 15. Story / chapter layer
Canonical Chapter 1: `chapter_01_guhya_garbhagriha`

Five phases:
1. Bāhya-Sādhana
2. De-conditioning
3. Sonic Entrainment
4. Peak and Gnosis
5. Integration

Unmapped story mechanics:
- phase-specific sensory profiles
- phase-specific mood baselines
- phase-specific relationship changes
- phase-specific attraction modifiers
- phase-specific learning objectives
- phase-specific environmental states
- phase-specific off-screen events
- return-from-absence information hierarchy
- chapter-wide omen eligibility
- chapter-specific lore unlocks
- chapter-specific character availability

## 16. Visual / media layer
**Status: C7**
Searchable sources clearly reference:
- Sākṣī Pīṭha visual theme
- black basalt yantra / temple seal / manuscript emblem
- red-sandstone jālī architecture
- dark marble
- bronze lamps
- camphor/sesame oil
- blue resinous smoke
- ceremonial attire
- Persian/Deccan visual fusion
- Santhal visual/cultural details
- character portrait/avatar concepts

A complete image-by-image audit of every media upload is not verifiable from the current file-search interface. Create a media registry:
`asset_id | source_chat | file | visual_subject | canonical_status | character | location | phase | prompt_status | linked_asset | unresolved_questions`

## 17. Legacy / high-risk source material
Some older source files contain explicit, fetish-oriented, and highly specific somatic material, including separate exhaustion and somatic-alchemy systems. These should **not** be blindly merged into the constitutional/runtime canon.

**Status: C4/C8**
Treat as:
- legacy research
- restricted source material
- possible inspiration for abstract physiological variables
- NOT canonical until explicitly reviewed

## 18. Priority backlog
### Priority A — normalize now
1. 14-character canonical schema
2. name/alias registry
3. age/status conflict register
4. relationship edge schema
5. sensory signature registry
6. telemetry registry
7. lore-to-runtime link registry
8. phase modifier registry
9. stage visibility matrix
10. legacy/superseded source registry

### Priority B — map next
11. psychology/mood state vector
12. physiological abstract state vector
13. attraction vector
14. philosophical/tattva links
15. anthropology/culture metadata
16. Kalā proficiency matrix
17. time/ritu/weather modifiers
18. autonomous event triggers
19. chronicle information classes
20. learning/Punyasiddhi skill graph

### Priority C — media/experience
21. image asset registry
22. avatar/portrait consistency
23. dashboard visual semantics
24. scene/architecture image references
25. CHUB presentation mapping

## 19. Conflict / review queue
| ID | Issue | Action |
|---|---|---|
| CF-001 | Jahzara age appears as 18, 22, 31 | Canon decision required |
| CF-002 | 12-character legacy core vs 14-character current core | Freeze 14-seat current registry; preserve legacy |
| CF-003 | Antarvani / Antarvāṇī terminology | Canonicalize spelling + role |
| CF-004 | Sākṣī Pīṭha vs Antarvāṇī relationship | Keep shell vs consciousness distinction |
| CF-005 | Kuma Ree Rati vs Kumārī Rati naming | Canonical display + aliases |
| CF-006 | Multiple versions of same character cards | Mark authoritative version; archive others |
| CF-007 | Early phase participant lists vs later 14-character universe | Reconcile phase-specific presence |
| CF-008 | Assumptions mixed with canonical statements | Tag `assumption` |
| CF-009 | Legacy explicit somatic/sexual systems | Abstract or archive; don't auto-merge |
| CF-010 | Image/media uploads not fully enumerable here | Separate visual audit |

## 20. Unified data graph target
`LORE → CHARACTER → CONSTITUTION → BRIDGE → SENSORY → PHYSIOLOGY → PSYCHOLOGY → MOOD → BEHAVIOR → RELATIONSHIP → ATTRACTION → RITUAL → TIME/RITU/WEATHER → STAGE → TELEMETRY → MEMORY → CHRONICLE → QUEST/CHOICE → CHAPTER`

Every node should be linked by IDs, not free-text duplication.

## 21. Recommended master files
- `registry/canonical_entity_registry.json`
- `registry/character_schema_v2.json`
- `registry/relationship_edge_registry.json`
- `registry/sensory_signature_registry.json`
- `registry/telemetry_registry.json`
- `registry/lore_link_registry.json`
- `registry/phase_modifier_registry.json`
- `registry/time_ritu_weather_registry.json`
- `registry/legacy_source_registry.json`
- `registry/conflict_registry.json`
- `registry/media_asset_registry.json`
- `logs/unmapped_master_log_v1.md`

## 22. Audit conclusion
The source set is substantially richer than the current unified runtime. The highest-value unused material is not simply more lore; it is the **cross-linking of existing dimensions**: body/breath/gaze → sensory response → mood → behavior → relationship → attraction → ritual progress → telemetry → memory → chronicle.

The Master Unified Core explicitly positions the Bridge Canon as the layer between constitutional identity and embodied behavior/gameplay, and states that the Stage should read bridge values for dashboard telemetry. The Constitutional Codex likewise identifies the Monitoring Plinth, score matrices, time/occasion system, Punyasiddhi progression, and scene architecture as master entries.

**Recommended next engineering goal:** integration rather than adding isolated mechanics. Make the existing source richness machine-addressable, traceable, and cross-linked before expanding V17.
