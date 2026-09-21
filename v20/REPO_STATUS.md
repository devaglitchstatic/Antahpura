# Antahpura Repository — Status

**Generated:** 2026-09-19
**Root:** `AntahpuraRepo/v20/`
**Audit tool:** `audit_repo.py` v1.4
**Manifest:** `REPO_MANIFEST.json`

## Current Audit State

| Metric | Value |
|---|---|
| Files scanned | 143 |
| Parse errors | 0 |
| Files with warnings | 0 |
| Manifest errors | 0 |
| Manifest warnings | 0 |
| Duplicate schemas | 0 |
| Schema gaps | 0 |
| Version gaps | 0 |
| Dangling characters | 0 |
| Dangling kalas | 0 |
| Dangling kamas | 0 |

**Status: CONSISTENT.**

## Canonical Registries

These three files are the source of truth for all ID resolution.

| Registry | File | Count |
|---|---|---|
| Characters | `characters/V17_1_CHARACTER_REGISTRY.json` | 14 canonical, 43 aliases |
| Kalas | `kalas/kala_system_v20.json` | 64 |
| Kamas | `kama/MASTER_KINK_REGISTRY.json` | 99 |

Every reference to a character, kala, or kama in any file resolves against these three registries. The audit enforces this on every run.

## Canonical Character Roster (14)

| ID | Display Name | Office |
|---|---|---|
| `maha_deva` | Mahā Deva | Sovereign / High Priest / Ritual Authority |
| `kumari_rati` | Princess Kumārī Rati | Princess / Dynastic Center / Initiand |
| `roxana` | Roxana | Persian Consort / Grand Vizier |
| `shrinagar` | Shrinagar | Mahā Vādaka / Chief Musician |
| `malika` | Malikā | Threshold Warden |
| `jahzara` | Jahzara | Agra-Pratihāriṇī / Vanguard Sentinel |
| `altani` | Altani | Outer Perimeter Sentinel |
| `anisa` | Anisa | Chief Court Supervisor |
| `padma` | Padmā | Personal Handmaiden |
| `campa` | Campā | Handmaiden Apprentice |
| `reva` | Reva | Rāja-Kavi / Principal Voice |
| `tarana` | Tarana | Pradhāna Nartī / Chief Dancer |
| `sevda` | Sevda | Subterranean Warden |
| `svara` | Svara | Cultural & Artistic Specialist / Micro-tonal Calibration |

Aliases accepted by the audit: `Champa`, `champa`, `Campā`, `Kuma Ree`, `Kamini`, `Kamini Anisa`, `Aniśā`, `Pahlava`, `Persian`, `Mahā Vādaka`, `Chief Musician`, `Agra-Pratihārīṇī`, `Vanguard Sentinel`, `Sentinel Altani`, `Steppe Sentinel`, `Padmā`, `Rāja Kavi`, `Principal Voice`, `Kamini Tarana`, `Pradhāna Nartī`, `Chief Dancer`, `Subterranean Warden`, `Micro-tonal Specialist`, `Deva`, `Mahadeva`, `Maharaj Deva`, and more.

## Canonical Kala System (64 Kalas)

Distributed across 6 domains:

| Domain | Patron | Kalas | Range |
|---|---|---|---|
| Vocal & Poetic | `char_svara` | 12 | kala_1 – kala_12 |
| Visual & Adornment | `char_shrinagar` | 16 | kala_13 – kala_28 |
| Martial & Physical | `char_roxana` | 12 | kala_29 – kala_40 |
| Occult & Healing | `char_jahzara` | 12 | kala_41 – kala_52 |
| Movement & Dance | `char_tarana` | 5 | kala_53 – kala_57 |
| Sensory & Pleasure | `char_kumari_rati` | 7 | kala_58 – kala_64 |

Split files derived from `kala_system_v20.json`:

| File | Purpose |
|---|---|
| `kalas/kala_dimension_matrix.json` | 64 × dimension weights |
| `kalas/character_kala_matrix.json` | Inverse index (character → kalas) |
| `kalas/kala_mastery_ladder.json` | 11-stage progression |
| `kalas/kala_synergies.json` | 5 cross-kala synergies |
| `kalas/kala_kama_linkage.json` | 74 kala ↔ kama edges |
| `kalas/kala_prerequisites_graph.json` | 23 directed prerequisite edges |

## Canonical Kama Registry (99 Kamas)

`kama/MASTER_KINK_REGISTRY.json` holds the full kama taxonomy. Each entry has:

- `id` — UPPERCASE_SNAKE_CASE identifier
- `name` — Sanskrit + English translation
- `taxonomy` — primary / related / similar / secondary flags
- `progression` — knowledge / training / practice / mastery booleans

98 were originally present; MAITHUNA (Sacred Union / Ritual Intimacy) was added as the 99th, restoring consistency with `kala_64` and its 22 downstream references.

## Relationship Layer

| File | Contents |
|---|---|
| `relationships/relationship_system_v20.json` | Consolidated V20 system: 18 canonical edges + sovereign axis + state |
| `relationships/V17_1_RELATIONSHIP_REGISTRY.json` | Original 18-edge registry |
| `relationships/CONSTITUTIONAL_RELATIONSHIPS.json` | Constitutional + sovereign axis |
| `relationships/RELATIONSHIP_STATE.json` | V18.3 runtime state |

The sovereign axis (maha_deva ↔ kumari_rati, marriage) is preserved as an immutable constitutional relationship. Emergent relational dimensions (trust, intimacy, tension, etc.) are runtime-mutable.

## World Layer

| File | Contents |
|---|---|
| `world/offices.json` | 16 offices (14 filled, 2 vacant) |
| `world/institutions.json` | Institutional structure |
| `world/locations.json` | Location registry |
| `world/occasions.json` | Ritual occasions |
| `world/cultural_profiles.json` | Cultural provenance data |
| `world/ANTAHPURA_KAMA_SYSTEM_V20.json` | 98-kama family taxonomy |
| `world/schema.json` | World schema |

## Runtime Layer

| File | Contents |
|---|---|
| `runtime/ANTAHPURA_RUNTIME_ENGINE_V20.json` | Runtime engine config |
| `runtime/ANTAHPURA_AVN_ASSET_REGISTRY.json` | AVN asset catalog |
| `runtime/character_states.json` | Per-character runtime state |
| `runtime/current_scene.json` | Active scene |

## Scenes & Quests

| File | Contents |
|---|---|
| `scenes/Scene Engine V20.json` | Scene engine definition |
| `scenes/V18_9_SCENE_TRIGGERS.json` | Scene triggers |
| `scenes/scene_templates.json` | Scene templates |
| `quests/quest_system_v20.json` | Quest framework |

## Systems Layer

| File | Contents |
|---|---|
| `systems/aphrodisiacs_substances_registry.json` | Substance registry |
| `systems/consent_framework_registry.json` | Consent framework |
| `systems/punishment_system.json` | Punishment rules |
| `systems/recovery_system.json` | Recovery rules |
| `systems/reward_registry.json` | Reward catalog |
| `systems/task_system.json` | Task assignment |
| `systems/intimate_jewelry_system.json` | Intimate jewelry |

## Audit Workflow

Three scripts govern repository consistency. Run them in this order after any change:

```powershell
# 1. Reconcile manifest with disk
python reconcile_manifest.py

# 2. Dry-run any pending reference fixes
python fix_dangling_refs.py

# 3. Apply if clean
python fix_dangling_refs.py --apply

# 4. Re-run the audit
python audit_repo.py --root . --manifest REPO_MANIFEST.json --output audit/validation_results.json