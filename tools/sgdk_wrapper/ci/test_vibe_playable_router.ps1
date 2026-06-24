$ErrorActionPreference = 'Stop'

function Assert-True {
    param(
        [bool]$Condition,
        [string]$Message
    )
    if (-not $Condition) {
        throw "ASSERT FAILED: $Message"
    }
}

function Assert-Equal {
    param(
        $Expected,
        $Actual,
        [string]$Message
    )
    if ($Expected -ne $Actual) {
        throw "ASSERT FAILED: $Message. Expected '$Expected', got '$Actual'"
    }
}

function ConvertTo-StableJson {
    param($Object)
    $Clone = $Object | ConvertTo-Json -Depth 100 | ConvertFrom-Json
    if ($Clone.PSObject.Properties.Name -contains 'generated_at') {
        $Clone.PSObject.Properties.Remove('generated_at')
    }
    return ($Clone | ConvertTo-Json -Depth 100 -Compress)
}

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$RouterScript = Join-Path $RepoRoot 'tools\sgdk_wrapper\route_vibe_playable_request.ps1'
$RouteSchema = Join-Path $RepoRoot 'tools\sgdk_wrapper\schemas\vibe_playable_route_report.schema.json'
$OutDir = Join-Path $RepoRoot 'out\ci\vibe_playable_router'
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

Assert-True (Test-Path -LiteralPath $RouteSchema) 'canonical vibe_playable_route_report schema must exist'

$RequestText = 'crie uma fase com um heroi enfrentando um boss'
$ReportA = Join-Path $OutDir 'route_a.json'
$ReportB = Join-Path $OutDir 'route_b.json'
$CompactA = Join-Path $OutDir 'compact_a.json'
$CompactB = Join-Path $OutDir 'compact_b.json'

& powershell -NoProfile -ExecutionPolicy Bypass -File $RouterScript `
    -RequestText $RequestText `
    -ProjectRoot $RepoRoot `
    -OutputPath $ReportA `
    -CompactOutputPath $CompactA `
    -SkipGraphify | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "router command failed for first deterministic run"
}

& powershell -NoProfile -ExecutionPolicy Bypass -File $RouterScript `
    -RequestText $RequestText `
    -ProjectRoot $RepoRoot `
    -OutputPath $ReportB `
    -CompactOutputPath $CompactB `
    -SkipGraphify | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "router command failed for second deterministic run"
}

$RouteA = Get-Content -Raw -Path $ReportA | ConvertFrom-Json
$RouteB = Get-Content -Raw -Path $ReportB | ConvertFrom-Json
$Compact = Get-Content -Raw -Path $CompactA | ConvertFrom-Json

Assert-Equal 'vibe_playable_route_report' $RouteA.report_kind 'report kind must be canonical'
Assert-True $RouteA.visual_route_required 'natural gameplay request must require visual production route'
Assert-True (-not $RouteA.runtime_open_allowed) 'runtime must not open before visual route admission'
Assert-Equal 'blocked_visual_route_required' $RouteA.runtime_admission.status 'route must block runtime until visual gates are satisfied'
Assert-Equal 'explicit_router_dispatch' $RouteA.dispatch.mode 'implicit art-direction-selector skill must be routed through explicit dispatch'

$TargetTypes = @($RouteA.detected_targets | ForEach-Object { $_.type })
Assert-True ($TargetTypes -contains 'scene') 'stage request must create a scene target'
Assert-True ($TargetTypes -contains 'player_character') 'hero request must create a player character target'
Assert-True ($TargetTypes -contains 'boss') 'boss request must create a boss target'

$Hero = @($RouteA.detected_targets | Where-Object { $_.type -eq 'player_character' })[0]
$Boss = @($RouteA.detected_targets | Where-Object { $_.type -eq 'boss' })[0]
Assert-True ($Hero.target_id -ne $Boss.target_id) 'hero and boss must preserve distinct target ids'
Assert-True $Hero.animation_required 'hero must require animation'
Assert-True $Boss.animation_required 'boss must require animation'

$Owners = @($RouteA.required_owners)
Assert-Equal 'skills/art/art-direction-selector' $Owners[0] 'art-direction-selector must be first visual owner despite non-implicit skill lifecycle'
Assert-True ($Owners -contains 'skills/art/art-asset-diagnostic') 'art-asset-diagnostic owner is required'
Assert-True ($Owners -contains 'skills/art/visual-excellence-standards') 'visual excellence owner is required'
Assert-True ($Owners -contains 'skills/operation/emulator-vdp-evidence-curator') 'BlastEm evidence owner is required'

$IntentNames = @($RouteA.detected_intents | ForEach-Object { $_.intent })
Assert-True ($IntentNames -contains 'gameplay_scene') 'gameplay scene intent must be recorded'
Assert-True ($IntentNames -contains 'character') 'character intent must be recorded'
Assert-True ($IntentNames -contains 'boss') 'boss intent must be recorded'
Assert-True ($RouteA.matched_rules.Count -ge 3) 'matched deterministic rules must be recorded'
Assert-True ($RouteA.compact_context_bytes -le 32768) 'compact context must stay bounded'

Assert-True ($Compact.detected_targets.Count -eq $RouteA.detected_targets.Count) 'compact context must preserve target multiplicity'
Assert-True (-not $Compact.runtime_open_allowed) 'compact context must also block runtime'

Assert-Equal (ConvertTo-StableJson $RouteA) (ConvertTo-StableJson $RouteB) 'router output must be deterministic aside from timestamp'

Write-Output 'test_vibe_playable_router: PASS'
