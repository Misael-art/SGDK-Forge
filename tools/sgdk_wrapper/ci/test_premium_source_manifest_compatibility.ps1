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

function Invoke-PremiumSourceValidator {
    param(
        [string]$FixtureName,
        [string]$OutputName
    )

    $FixturePath = Join-Path $FixtureDir $FixtureName
    Assert-True (Test-Path -LiteralPath $FixturePath) "fixture must exist: $FixtureName"

    $OutputPath = Join-Path $OutDir $OutputName
    & powershell -NoProfile -ExecutionPolicy Bypass -File $ValidatorScript `
        -ManifestPath $FixturePath `
        -OutputPath $OutputPath | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "validator command failed for $FixtureName"
    }

    return Get-Content -Raw -Path $OutputPath | ConvertFrom-Json
}

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$SchemaPath = Join-Path $RepoRoot 'tools\sgdk_wrapper\schemas\premium_source_manifest.schema.json'
$ForbiddenParallelSchema = Join-Path $RepoRoot 'tools\sgdk_wrapper\schemas\premium_visual_source_manifest.schema.json'
$ValidatorScript = Join-Path $RepoRoot 'tools\sgdk_wrapper\validate_premium_source_manifest.ps1'
$FixtureDir = Join-Path $RepoRoot 'tools\sgdk_wrapper\ci\fixtures\premium_source_manifest'
$OutDir = Join-Path $RepoRoot 'out\ci\premium_source_manifest'
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

Assert-True (-not (Test-Path -LiteralPath $ForbiddenParallelSchema)) 'premium_visual_source_manifest schema must not exist'
Assert-True (Test-Path -LiteralPath $SchemaPath) 'canonical premium_source_manifest schema must exist'
Assert-True (Test-Path -LiteralPath $ValidatorScript) 'premium_source_manifest validator must exist'

$V1Single = Invoke-PremiumSourceValidator -FixtureName 'v1_single.json' -OutputName 'v1_single.report.json'
Assert-Equal 'premium_source_manifest_validation_report' $V1Single.report_kind 'v1 single fixture must produce canonical validation report'
Assert-Equal 'v1_single_asset' $V1Single.compatibility_mode 'v1 single fixture must be migrated compatibly'
Assert-Equal 1 $V1Single.normalized.asset_count 'v1 single fixture must preserve one real asset'

$V1Root = Invoke-PremiumSourceValidator -FixtureName 'v1_root.json' -OutputName 'v1_root.report.json'
Assert-Equal 'v1_root_assets' $V1Root.compatibility_mode 'v1 root fixture must be recognized as root legacy assets manifest'
Assert-True ($V1Root.normalized.asset_count -ge 2) 'v1 root fixture must prove compatibility with real legacy assets, not assets.Count=0'
Assert-True (@($V1Root.normalized.assets | Where-Object { $_.source_files.Count -gt 0 }).Count -eq $V1Root.normalized.asset_count) 'legacy assets must preserve source files'

$V2Valid = Invoke-PremiumSourceValidator -FixtureName 'v2_valid.json' -OutputName 'v2_valid.report.json'
Assert-Equal 'v2' $V2Valid.compatibility_mode 'v2 fixture must stay on canonical schema'
Assert-Equal 'passed' $V2Valid.status 'valid v2 fixture must pass'
Assert-True $V2Valid.effective_production_source_ready 'valid v2 fixture must be production source ready'
Assert-Equal 0 @($V2Valid.blockers).Count 'valid v2 fixture must not have blockers'

$V2Unknown = Invoke-PremiumSourceValidator -FixtureName 'v2_unknown.json' -OutputName 'v2_unknown.report.json'
Assert-Equal 'blocked' $V2Unknown.status 'unknown critical source must block production'
Assert-True (@($V2Unknown.blockers) -contains 'blocked_unknown_source_classification') 'unknown classification blocker must be explicit'
Assert-True (-not $V2Unknown.effective_production_source_ready) 'unknown critical asset cannot be production source ready'

$V2Procedural = Invoke-PremiumSourceValidator -FixtureName 'v2_procedural_debug.json' -OutputName 'v2_procedural.report.json'
Assert-Equal 'blocked' $V2Procedural.status 'procedural_debug critical source must block production'
Assert-True (@($V2Procedural.blockers) -contains 'blocked_procedural_debug_critical_asset') 'procedural_debug critical blocker must be explicit'
Assert-True (-not $V2Procedural.effective_production_source_ready) 'procedural_debug cannot be production source ready for critical assets'

Write-Output 'test_premium_source_manifest_compatibility: PASS'
