<#
.SYNOPSIS
    Regression test for status-only memory-bank synchronization.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$scriptUnderTest = Join-Path $wrapperRoot 'update_project_changelog.ps1'
$fixtureRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("sgdk_status_sync_{0}" -f ([guid]::NewGuid().ToString('N')))
$memoryPath = Join-Path $fixtureRoot 'doc\10-memory-bank.md'
$changelogPath = Join-Path $fixtureRoot 'doc\changelog\changelog.md'
$buildMetaPath = Join-Path $fixtureRoot 'doc\changelog\roms\build_v001\build_meta.json'
$validationPath = Join-Path $fixtureRoot 'out\logs\validation_report.json'
$romPath = Join-Path $fixtureRoot 'out\rom.bin'

function Assert-True {
    param([string]$Name, [bool]$Condition, [string]$Detail = '')
    if (-not $Condition) {
        throw "$Name failed$(if ($Detail) { ": $Detail" } else { '' })"
    }
    Write-Host "  [PASS] $Name"
}

function Write-JsonFile {
    param([string]$Path, $Value)
    $parent = Split-Path $Path -Parent
    if (-not (Test-Path -LiteralPath $parent -PathType Container)) {
        New-Item -ItemType Directory -Force -Path $parent | Out-Null
    }
    [System.IO.File]::WriteAllText($Path, ($Value | ConvertTo-Json -Depth 20), [System.Text.Encoding]::UTF8)
}

function Get-TreeIdentity {
    param([string]$Root)
    if (-not (Test-Path -LiteralPath $Root -PathType Container)) { return '' }
    return (@(Get-ChildItem -LiteralPath $Root -Recurse -File | Sort-Object FullName | ForEach-Object {
        "$($_.FullName)|$((Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash)"
    }) -join "`n")
}

Write-Host ''
Write-Host '=== Changelog Status-Only Sync Test ==='
Write-Host ''

try {
    New-Item -ItemType Directory -Force -Path (Split-Path $memoryPath -Parent), (Split-Path $validationPath -Parent), (Split-Path $buildMetaPath -Parent) | Out-Null
    [System.IO.File]::WriteAllText($memoryPath, "# Memory`r`n", [System.Text.Encoding]::UTF8)
    [System.IO.File]::WriteAllText($changelogPath, "# Changelog`r`n", [System.Text.Encoding]::UTF8)
    [System.IO.File]::WriteAllBytes($romPath, [byte[]](1, 2, 3, 4))
    Write-JsonFile $buildMetaPath ([ordered]@{ build_version = 'build_v001'; rom_sha256 = 'historical' })
    Write-JsonFile $validationPath ([ordered]@{
        summary = [ordered]@{ errors = 2; warnings = 1 }
        blocking_statuses = @('freshness_audit_stale', 'visual_gate_blocked')
        evidence = [ordered]@{ emulator_evidence_reason = 'stale' }
        status_panel = [ordered]@{
            visual_lab_aprovado = $false
            gameplay_rom_aprovada = $false
            ready_for_aaa = $false
        }
        qa_axes = [ordered]@{
            gameplay_basico = 'stale'
            performance = 'nao_testado'
            audio = 'nao_testado'
            hardware_real = 'nao_testado'
        }
    })

    $changelogTree = Split-Path $changelogPath -Parent
    $beforeIdentity = Get-TreeIdentity $changelogTree
    $output = & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $scriptUnderTest -ProjectRoot $fixtureRoot -StatusOnly | Out-String
    Assert-True 'status-only exits successfully' ($LASTEXITCODE -eq 0) $output

    $result = $output | ConvertFrom-Json
    $memory = Get-Content -LiteralPath $memoryPath -Raw
    $afterIdentity = Get-TreeIdentity $changelogTree
    Assert-True 'result declares status-only' ([bool]$result.status_only)
    Assert-True 'no ROM snapshot is created' (-not [bool]$result.rom_snapshot_created)
    Assert-True 'changelog tree is byte-identical' ($beforeIdentity -eq $afterIdentity)
    Assert-True 'memory bank receives current blockers' ($memory.Contains('freshness_audit_stale, visual_gate_blocked'))
    Assert-True 'memory bank receives current gates' ($memory.Contains('ready_for_aaa=False'))
} finally {
    if (Test-Path -LiteralPath $fixtureRoot) {
        Remove-Item -LiteralPath $fixtureRoot -Recurse -Force
    }
}

Write-Host ''
Write-Host '=== Results: 6/6 passed, 0 failed ==='
exit 0
