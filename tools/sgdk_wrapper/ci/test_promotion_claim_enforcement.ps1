<#
.SYNOPSIS
    Pressure tests for canonical claim-to-evidence enforcement.
#>
[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path -Parent $PSScriptRoot
$auditScript = Join-Path $wrapperRoot 'audit_promotion_claims.ps1'
$fixtureRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('sgdk_claim_gate_' + [guid]::NewGuid().ToString('N'))
$script:passed = 0
$script:failed = 0

function Write-JsonFile {
    param([string]$Path, $Value)
    $parent = Split-Path -Parent $Path
    if ($parent) { [System.IO.Directory]::CreateDirectory($parent) | Out-Null }
    $Value | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $Path -Encoding UTF8
}

function New-Fixture {
    param([string]$Name, [hashtable]$Manifest, [hashtable]$Files = @{})
    $root = Join-Path $fixtureRoot $Name
    [System.IO.Directory]::CreateDirectory((Join-Path $root 'out\logs')) | Out-Null
    [System.IO.Directory]::CreateDirectory((Join-Path $root 'doc')) | Out-Null
    [System.IO.File]::WriteAllBytes((Join-Path $root 'out\rom.bin'), [byte[]](1..64))
    $romHash = (Get-FileHash -LiteralPath (Join-Path $root 'out\rom.bin') -Algorithm SHA256).Hash.ToLowerInvariant()
    if (-not $Manifest.ContainsKey('rom_sha256')) { $Manifest.rom_sha256 = $romHash }
    Write-JsonFile (Join-Path $root 'doc\promotion_claim_manifest.json') $Manifest
    foreach ($entry in $Files.GetEnumerator()) {
        Write-JsonFile (Join-Path $root $entry.Key) $entry.Value
    }
    return [ordered]@{ root = $root; rom_hash = $romHash }
}

function Assert-Blocked {
    param([string]$Name, [hashtable]$Manifest, [hashtable]$Files, [string[]]$ExpectedCodes)
    $fixture = New-Fixture -Name $Name -Manifest $Manifest -Files $Files
    $reportPath = Join-Path $fixture.root 'out\logs\promotion_claim_audit_report.json'
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $auditScript -ProjectRoot $fixture.root -OutputPath $reportPath *> $null
    $exitCode = $LASTEXITCODE
    if (-not (Test-Path -LiteralPath $reportPath)) {
        Write-Host "[FAIL] $Name report missing"
        $script:failed++
        return
    }
    $report = Get-Content -LiteralPath $reportPath -Raw | ConvertFrom-Json
    $codes = @($report.blocker_codes)
    $missing = @($ExpectedCodes | Where-Object { $codes -notcontains $_ })
    if ($exitCode -ne 0 -and $missing.Count -eq 0) {
        Write-Host "[PASS] $Name -> $($ExpectedCodes -join ', ')"
        $script:passed++
    } else {
        Write-Host "[FAIL] $Name exit=$exitCode missing=$($missing -join ', ') actual=$($codes -join ', ')"
        $script:failed++
    }
}

try {
    Assert-Blocked 'old_hash_screenshot' @{
        claims = @(@{ id = 'first_playable'; scope = 'full_route' })
        evidence = @(@{ kind = 'screenshot'; rom_sha256 = ('a' * 64); scope = 'gameplay' })
    } @{} @('claim_rom_hash_mismatch')

    Assert-Blocked 'title_only_gameplay' @{
        claims = @(@{ id = 'gameplay_rom_aprovada'; scope = 'gameplay' })
        evidence = @(@{ kind = 'screenshot'; scope = 'boot_title_only' })
    } @{} @('claim_scope_not_observed')

    Assert-Blocked 'critical_warning' @{
        claims = @(@{ id = 'first_playable'; scope = 'full_route' })
        build = @{ critical_warnings = @('comparison is always false due to limited range of data type') }
    } @{} @('critical_compiler_warning')

    Assert-Blocked 'procedural_high_score' @{
        claims = @(@{ id = 'assets_premium'; scope = 'visual_delivery' })
        assets = @(@{ id = 'hero'; generation_channel = 'procedural_renderer'; technical_score = 99; artistic_approval = 'approved' })
    } @{} @('procedural_asset_quarantined', 'technical_score_not_artistic_approval')

    Assert-Blocked 'modules_unreachable' @{
        claims = @(@{ id = 'first_playable'; scope = 'full_route' })
        modules = @(
            @{ id = 'player'; status = 'runtime_proven' },
            @{ id = 'pursuer'; status = 'integrated' },
            @{ id = 'pressure_gate'; status = 'module_present' }
        )
    } @{} @('runtime_feature_not_proven')

    Assert-Blocked 'manual_closeout_only' @{
        claims = @(@{ id = 'scene_closeout'; scope = 'scene' })
    } @{
        'doc\scene_closeout_report.json' = @{ status = 'ok' }
    } @('executed_closeout_gate_missing')

    Assert-Blocked 'mtr_as_mdrt' @{
        claims = @(@{ id = 'performance_estavel'; scope = 'performance' })
        metrics = @{ format = 'MTR'; fps_observed = 60 }
    } @{} @('mdrt_performance_evidence_missing')

    Assert-Blocked 'crash_before_result' @{
        claims = @(@{ id = 'first_playable'; scope = 'full_route' })
        runtime = @{ route_status = 'crash'; result_reached = $false }
    } @{} @('runtime_route_crashed', 'route_result_not_proven')

    Assert-Blocked 'optimistic_report_conflict' @{
        claims = @(@{ id = 'ready_for_aaa'; scope = 'delivery' })
        reconciliation = @{
            statuses = @(
                @{ source = 'memory'; status = 'ready_for_aaa' },
                @{ source = 'validation'; status = 'buildado' },
                @{ source = 'evidence'; status = 'implementado' }
            )
        }
    } @{} @('canonical_status_conflict', 'claim_exceeds_consistent_ceiling')

    Assert-Blocked 'advance_after_crash' @{
        claims = @(@{ id = 'advance_next_phase'; scope = 'phase' })
        phase = @{ current = 'sector_01'; requested = 'sector_02' }
        runtime = @{ route_status = 'crash' }
        visual = @{ corruption = $true }
        review = @{ decision = 'review_blocked' }
    } @{} @('phase_advance_blocked')
}
finally {
    if (Test-Path -LiteralPath $fixtureRoot) {
        Remove-Item -LiteralPath $fixtureRoot -Recurse -Force
    }
}

Write-Host "passed=$script:passed failed=$script:failed"
if ($script:failed -gt 0) { exit 1 }
exit 0
