# inventory_repo.ps1
# Antahpura V20 Repository Inventory
# Usage:  .\inventory_repo.ps1
# Or:     .\inventory_repo.ps1 -Root "D:\dolphin\AntahpuraRepo" -OutFile "inventory-report.txt"

param(
    [string]$Root = "D:\dolphin\AntahpuraRepo",
    [string]$OutFile = ""
)

# ---- Expected structure ----
$Expected = @{
    "canon" = @(
        "characters.json", "kalas.json", "domains.json",
        "institutions.json", "locations.json", "occasions.json"
    )
    "kama" = @(
        "kama_registry_v20.json", "kama_families.json", "kama_dimensions.json",
        "kama_association_types.json", "kama_lifecycle_states.json",
        "kama_risk_classes.json"
    )
    "kala" = @(
        "kala_registry_v20.json", "kala_domains.json",
        "kala_mastery_ladder.json", "kala_synergies.json",
        "kala_kama_linkage.json", "kala_prerequisites_graph.json",
        "character_kala_matrix.json"
    )
    "seva" = @("seva_registry.json")
    "character" = @(
        "character_profiles_v20.json",
        "cultural_profiles.json",
        "role_orientation\schema.json",
        "role_orientation\orientations.json",
        "archetypes.json",
        "voice_profiles.json"
    )
    "relationship" = @(
        "relationship_dimensions.json",
        "relationship_types.json",
        "relationship_edges.json",
        "relationship_memory.json",
        "reputation_matrix.json"
    )
    "location" = @(
        "institution_registry.json",
        "location_registry.json",
        "zone_registry.json",
        "access_rules.json",
        "environmental_modifiers.json",
        "location_affinity.json",
        "occasion_location_map.json"
    )
    "scene" = @(
        "scene_engine.json",
        "scene_templates.json",
        "act_structures.json",
        "scene_validation_rules.json"
    )
    "quest" = @(
        "quest_registry_v20.json",
        "quest_types.json",
        "quest_states.json",
        "quest_branching.json",
        "quest_rewards.json",
        "quest_prerequisites.json",
        "quest_availability_rules.json",
        "quest_failure_modes.json",
        "quest_chains.json",
        "quest_runtime_schema.json",
        "multiplayer_quest_rules.json",
        "avn_quest_hooks.json"
    )
    "matrices" = @(
        "character_kala_matrix.json",
        "kala_dimension_matrix.json",
        "dimension_kama_matrix.json",
        "character_dimension_weights.json",
        "kala_kama_links.json",
        "character_kama_derived.json"
    )
    "systems" = @(
        "task_system.json",
        "punishment_system.json",
        "dbt_technique_registry.json",
        "consent_framework_registry.json",
        "traffic_light_system.json",
        "reward_registry.json",
        "recovery_action_registry.json",
        "recovery_system.json",
        "intimate_jewelry_system.json",
        "jewelry_registry.json",
        "aphrodisiacs_substances_registry.json",
        "toys_registry.json",
        "journaling_system.json",
        "contract_system.json",
        "daily_protocol_system.json",
        "collar_ceremony_system.json",
        "scene_negotiation_system.json",
        "scene_template_registry.json"
    )
    "world" = @(
        "institutions.json",
        "occasions.json",
        "offices.json"
    )
    "runtime" = @(
        "world_state.json",
        "character_states.json",
        "telemetry.json",
        "relationship_edges.json",
        "chandra_kala_modifiers.json",
        "current_scene.json",
        "session_registry.json",
        "save_contract.json",
        "multiplayer_coordination.json"
    )
    "archive" = @("events.jsonl", "memories.json")
    "audit" = @(
        "provenance.json",
        "conflicts.json",
        "canon_decisions.json",
        "schema_versions.json"
    )
    "scripts" = @(
        "_antahpura_common.py",
        "apply_task_event.py",
        "apply_punishment_event.py",
        "apply_dbt_event.py",
        "apply_consent_event.py",
        "apply_traffic_light_event.py",
        "apply_journal_event.py",
        "apply_jewelry_event.py",
        "apply_recovery_event.py",
        "apply_reward_event.py",
        "derive_character_kama.py",
        "validate_all.py",
        "replay_events.py",
        "inventory_repo.ps1"
    )
}

# ---- Locate the v20 directory (case-insensitive) ----
if (-not (Test-Path $Root)) {
    Write-Host "ERROR: Root path does not exist: $Root" -ForegroundColor Red
    exit 1
}

$v20 = Get-ChildItem -Path $Root -Directory |
    Where-Object { $_.Name -ieq "v20" } |
    Select-Object -First 1

if (-not $v20) {
    Write-Host "ERROR: Could not find 'v20' directory under $Root" -ForegroundColor Red
    exit 1
}

$V20Path = $v20.FullName
Write-Host "Scanning: $V20Path"
Write-Host ""

# ---- Start report ----
$Report = New-Object System.Collections.Generic.List[string]

function Add-Line {
    param([string]$Text)
    $Report.Add($Text) | Out-Null
    Write-Host $Text
}

Add-Line "=" * 72
Add-Line "ANTAHPURA V20 REPOSITORY INVENTORY"
Add-Line "Root: $V20Path"
Add-Line "Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Add-Line "=" * 72
Add-Line ""

# ---- Present files ----
Add-Line "--- PRESENT FILES ---"
$present = @{}
$totalPresent = 0
foreach ($dir in $Expected.Keys | Sort-Object) {
    $dirPath = Join-Path $V20Path $dir
    $present[$dir] = @()
    if (Test-Path $dirPath) {
        foreach ($file in $Expected[$dir]) {
            $filePath = Join-Path $dirPath $file
            if (Test-Path $filePath) {
                $size = (Get-Item $filePath).Length
                $sizeKB = [math]::Round($size / 1KB, 1)
                $present[$dir] += $file
                $totalPresent++
                Add-Line ("  [OK]   {0}/{1}  ({2} KB)" -f $dir, $file, $sizeKB)
            }
        }
    }
}
Add-Line ""
Add-Line "Total present: $totalPresent"
Add-Line ""

# ---- Missing files ----
Add-Line "--- MISSING FILES ---"
$missing = @{}
$totalMissing = 0
foreach ($dir in $Expected.Keys | Sort-Object) {
    $missing[$dir] = @()
    $dirPath = Join-Path $V20Path $dir
    foreach ($file in $Expected[$dir]) {
        $filePath = Join-Path $dirPath $file
        if (-not (Test-Path $filePath)) {
            $missing[$dir] += $file
            $totalMissing++
            Add-Line ("  [MISS] {0}/{1}" -f $dir, $file)
        }
    }
}
Add-Line ""
Add-Line "Total missing: $totalMissing"
Add-Line ""

# ---- Unexpected files (present but not in expected list) ----
Add-Line "--- UNEXPECTED FILES (present but not in expected list) ---"
$unexpectedTotal = 0
foreach ($dir in $Expected.Keys | Sort-Object) {
    $dirPath = Join-Path $V20Path $dir
    if (-not (Test-Path $dirPath)) { continue }
    $actualFiles = Get-ChildItem -Path $dirPath -File -Recurse |
        ForEach-Object { $_.FullName.Substring($dirPath.Length).TrimStart('\') }
    foreach ($af in $actualFiles) {
        if ($Expected[$dir] -notcontains $af) {
            Add-Line ("  [EXTRA] {0}/{1}" -f $dir, $af)
            $unexpectedTotal++
        }
    }
}
Add-Line ""
Add-Line "Total unexpected: $unexpectedTotal"
Add-Line ""

# ---- Full directory tree ----
Add-Line "--- DIRECTORY TREE (all files) ---"
Get-ChildItem -Path $V20Path -Recurse |
    Where-Object { -not $_.PSIsContainer } |
    Sort-Object FullName |
    ForEach-Object {
        $rel = $_.FullName.Substring($V20Path.Length).TrimStart('\')
        $sizeKB = [math]::Round($_.Length / 1KB, 1)
        Add-Line ("  {0}  ({1} KB)" -f $rel, $sizeKB)
    }
Add-Line ""

# ---- JSON validation ----
Add-Line "--- JSON VALIDATION ---"
$jsonFiles = Get-ChildItem -Path $V20Path -Recurse -Filter *.json
$validJson = 0
$invalidJson = 0
foreach ($jf in $jsonFiles) {
    try {
        $null = Get-Content $jf.FullName -Raw | ConvertFrom-Json
        $validJson++
    } catch {
        Add-Line ("  [INVALID JSON] {0}: {1}" -f $jf.FullName.Substring($V20Path.Length), $_.Exception.Message)
        $invalidJson++
    }
}
Add-Line "Valid JSON: $validJson"
Add-Line "Invalid JSON: $invalidJson"
Add-Line ""

# ---- Summary ----
Add-Line "=" * 72
Add-Line "SUMMARY"
Add-Line "=" * 72
Add-Line ("  Present:    {0}" -f $totalPresent)
Add-Line ("  Missing:    {0}" -f $totalMissing)
Add-Line ("  Unexpected: {0}" -f $unexpectedTotal)
Add-Line ("  Valid JSON: {0}" -f $validJson)
Add-Line ("  Invalid:    {0}" -f $invalidJson)
Add-Line ""

if ($totalMissing -eq 0) {
    Add-Line "  STATUS: COMPLETE" -ForegroundColor Green
} else {
    Add-Line "  STATUS: INCOMPLETE — see missing files above"
}
Add-Line "=" * 72

# ---- Write to file if requested ----
if ($OutFile -ne "") {
    $Report | Out-File -FilePath $OutFile -Encoding UTF8
    Write-Host ""
    Write-Host "Report written to: $OutFile"
}