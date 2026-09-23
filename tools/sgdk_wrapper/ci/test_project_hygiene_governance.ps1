<#
.SYNOPSIS
    Regression suite for project isolation, organized scratch data, and external input copies.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$workspaceRoot = Split-Path (Split-Path $wrapperRoot -Parent) -Parent
$validator = Join-Path $wrapperRoot 'validate_project_hygiene.ps1'
$fixtureRoot = Join-Path $workspaceRoot 'out\ci\project_hygiene_fixture'
$reportPath = Join-Path $fixtureRoot 'out\logs\project_hygiene_report.json'

$script:passed = 0
$script:failed = 0
$script:total = 0

function Assert-True {
    param([string]$Name, [bool]$Condition, [string]$Detail = '')
    $script:total++
    if ($Condition) {
        $script:passed++
        Write-Host "  [PASS] $Name"
    } else {
        $script:failed++
        $msg = "  [FAIL] $Name"
        if ($Detail) { $msg += " -- $Detail" }
        Write-Host $msg
    }
}

function Write-JsonFile {
    param([string]$Path, $Value)
    $parent = Split-Path $Path -Parent
    if (-not (Test-Path -LiteralPath $parent -PathType Container)) {
        New-Item -ItemType Directory -Force -Path $parent | Out-Null
    }
    [System.IO.File]::WriteAllText($Path, ($Value | ConvertTo-Json -Depth 20), [System.Text.Encoding]::UTF8)
}

function Reset-Fixture {
    if (Test-Path -LiteralPath $fixtureRoot) {
        Remove-Item -LiteralPath $fixtureRoot -Recurse -Force
    }
    New-Item -ItemType Directory -Force -Path (Join-Path $fixtureRoot 'doc') | Out-Null
    New-Item -ItemType Directory -Force -Path (Join-Path $fixtureRoot 'src') | Out-Null
    New-Item -ItemType Directory -Force -Path (Join-Path $fixtureRoot 'out\logs') | Out-Null
    New-Item -ItemType Directory -Force -Path (Join-Path $fixtureRoot 'rascunho') | Out-Null
}

function New-HygieneManifest {
    param($ExternalInputs = @())
    return [ordered]@{
        schema_version = '1.0.0'
        project_root_policy = 'all_project_material_inside_project'
        naming_policy = 'portable_descriptive_v1'
        scratch_policy = [ordered]@{
            root = 'rascunho'
            raw_inputs = 'rascunho/entrada_bruta'
            processed_inputs = 'rascunho/processado'
            temporary = 'rascunho/temporario'
        }
        allowed_root_entries = @(
            '.agent', '.cursor', '.mddev', '.vscode', 'data', 'doc', 'inc',
            'out', 'rascunho', 'rds', 'res', 'src', 'README.md', 'build.bat',
            'clean.bat', 'rebuild.bat', 'resolve_wrapper.bat', 'run.bat',
            'sgdk_wrapper_env.bat'
        )
        canonical_shared_dependencies = @(
            'tools/sgdk_wrapper',
            'sdk/sgdk-2.11',
            'tools/emuladores'
        )
        external_inputs = $ExternalInputs
    }
}

function Invoke-HygieneValidator {
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $validator `
        -ProjectRoot $fixtureRoot `
        -WorkspaceRoot $workspaceRoot `
        -OutputPath $reportPath | Out-Null
    $exitCode = $LASTEXITCODE
    $report = if (Test-Path -LiteralPath $reportPath) {
        Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json
    } else {
        $null
    }
    return [pscustomobject]@{
        exit_code = $exitCode
        report = $report
        statuses = if ($report) { @($report.blocking_statuses) } else { @() }
    }
}

Write-Host ''
Write-Host '=== Project Hygiene Governance Test ==='
Write-Host ''

try {
    Reset-Fixture
    $run = Invoke-HygieneValidator
    Assert-True 'missing hygiene manifest is blocked' ($run.statuses -contains 'project_hygiene_manifest_missing')

    Write-JsonFile (Join-Path $fixtureRoot 'doc\project_hygiene_manifest.json') (New-HygieneManifest)
    $run = Invoke-HygieneValidator
    Assert-True 'organized project with rascunho passes hygiene' ($run.exit_code -eq 0) ($run.statuses -join ',')

    Set-Content -LiteralPath (Join-Path $fixtureRoot 'src\Bad Name.c') -Value 'int main(void) { return 0; }' -Encoding UTF8
    $run = Invoke-HygieneValidator
    Assert-True 'noncanonical active file name is blocked' ($run.statuses -contains 'noncanonical_project_entry_name')
    Remove-Item -LiteralPath (Join-Path $fixtureRoot 'src\Bad Name.c') -Force

    Set-Content -LiteralPath (Join-Path $fixtureRoot 'notes.tmp') -Value 'orphan' -Encoding UTF8
    $run = Invoke-HygieneValidator
    Assert-True 'temporary file outside rascunho/out is blocked' ($run.statuses -contains 'orphan_project_artifact')

    Reset-Fixture
    Write-JsonFile (Join-Path $fixtureRoot 'doc\project_hygiene_manifest.json') (
        New-HygieneManifest -ExternalInputs @(
            @{
                source = 'C:/external/source.png'
                copied_to = 'rascunho/entrada_bruta/source.png'
                purpose = 'source study'
                license_or_authorization = 'human supplied'
                sha256 = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
            }
        )
    )
    $run = Invoke-HygieneValidator
    Assert-True 'external input without local copy is blocked' ($run.statuses -contains 'external_input_not_copied')

    $localCopy = Join-Path $fixtureRoot 'rascunho\entrada_bruta\source.png'
    New-Item -ItemType Directory -Force -Path (Split-Path $localCopy -Parent) | Out-Null
    Set-Content -LiteralPath $localCopy -Value 'local copy' -Encoding UTF8
    $hash = (Get-FileHash -LiteralPath $localCopy -Algorithm SHA256).Hash.ToLowerInvariant()
    Write-JsonFile (Join-Path $fixtureRoot 'doc\project_hygiene_manifest.json') (
        New-HygieneManifest -ExternalInputs @(
            @{
                source = 'C:/external/source.png'
                copied_to = 'rascunho/entrada_bruta/source.png'
                purpose = 'source study'
                license_or_authorization = 'human supplied'
                sha256 = $hash
            }
        )
    )
    $run = Invoke-HygieneValidator
    Assert-True 'external input with verified local copy passes' ($run.exit_code -eq 0) ($run.statuses -join ',')

    Set-Content -LiteralPath (Join-Path $fixtureRoot 'doc\legacy-path.md') -Value 'Active dependency: C:\external\source.png' -Encoding UTF8
    $run = Invoke-HygieneValidator
    Assert-True 'active absolute path outside project is blocked' ($run.statuses -contains 'external_path_reference_outside_project')

    Reset-Fixture
    $inventoryRoot = Join-Path $fixtureRoot 'rascunho\entrada_bruta\external_bundle'
    New-Item -ItemType Directory -Force -Path $inventoryRoot | Out-Null
    $inventoryData = Join-Path $inventoryRoot 'source.png'
    Set-Content -LiteralPath $inventoryData -Value 'inventory tracked copy' -Encoding UTF8
    $inventoryDataHash = (Get-FileHash -LiteralPath $inventoryData -Algorithm SHA256).Hash.ToLowerInvariant()
    $inventoryPath = Join-Path $inventoryRoot '_external_input_inventory.json'
    Write-JsonFile $inventoryPath ([ordered]@{
        schema_version = '1.0.0'
        source = 'C:/external/bundle'
        copied_root = 'rascunho/entrada_bruta/external_bundle'
        file_count = 1
        total_bytes = (Get-Item -LiteralPath $inventoryData).Length
        files = @(
            @{
                path = 'rascunho/entrada_bruta/external_bundle/source.png'
                bytes = (Get-Item -LiteralPath $inventoryData).Length
                sha256 = $inventoryDataHash
            }
        )
    })
    $inventoryHash = (Get-FileHash -LiteralPath $inventoryPath -Algorithm SHA256).Hash.ToLowerInvariant()
    Write-JsonFile (Join-Path $fixtureRoot 'doc\project_hygiene_manifest.json') (
        New-HygieneManifest -ExternalInputs @(
            @{
                source = 'C:/external/bundle'
                copied_to = 'rascunho/entrada_bruta/external_bundle/_external_input_inventory.json'
                copied_root = 'rascunho/entrada_bruta/external_bundle'
                purpose = 'source bundle'
                license_or_authorization = 'human supplied'
                sha256 = $inventoryHash
            }
        )
    )
    $run = Invoke-HygieneValidator
    Assert-True 'verified directory inventory passes' ($run.exit_code -eq 0) ($run.statuses -join ',')

    Set-Content -LiteralPath $inventoryData -Value 'mutated after inventory' -Encoding UTF8
    $run = Invoke-HygieneValidator
    Assert-True 'mutated inventory file is blocked' ($run.statuses -contains 'external_input_inventory_invalid')
} finally {
    if (Test-Path -LiteralPath $fixtureRoot) {
        Remove-Item -LiteralPath $fixtureRoot -Recurse -Force
    }
}

Write-Host ''
Write-Host ("=== Results: {0}/{1} passed, {2} failed ===" -f $script:passed, $script:total, $script:failed)
if ($script:failed -gt 0) { exit 1 }
exit 0
