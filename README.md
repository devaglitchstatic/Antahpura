# Antahpura

Stateful world model for the Antahpura game.

## Governance

| Layer | Rule |
|---|---|
| `canon/` | Immutable. Definitions only. No computed values. |
| `kama/` | Taxonomy. Immutable within a version. |
| `seva/` | Office registry. Immutable within a version. |
| `character/` | Character definitions. Versioned edits via audit. |
| `matrices/` | Derived relationships. Recomputable. Never hand-edited. |
| `runtime/` | Current session state. Append-derived. |
| `archive/` | Append-only event log. Never mutated. |
| `audit/` | Justification layer. Explains why canon believes what it believes. |

## Dependency Graph

    CANON
      ↓
    Characters → Kalas → Domains
      ↓            ↓
    Seva/Roles   Dimensions
      ↓            ↓
      Kama Matrix
          ↓
    Character-Kama Derivation
          ↓
      RUNTIME
          ↓
       EVENTS
          ↓
       ARCHIVE

    AUDIT sits across all layers.

## Principle

Canonical files are facts. Matrices are relationships. Derived files are
calculations. Runtime is state. Archive is history. Audit is justification.

## Active Schema Versions

See `audit/schema_versions.json`.