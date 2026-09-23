<#
.SYNOPSIS
    Verifica que visual_delivery_gate_report nao aceita "not_required" em
    evidencias visuais canonicas de entrega.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$workspaceRoot = Split-Path (Split-Path $wrapperRoot -Parent) -Parent
$fixtureRoot = Join-Path $workspaceRoot 'out\ci\visual_gate_not_required_schema_fixture'
$schemaPath = Join-Path $wrapperRoot 'schemas\visual_delivery_gate_report.schema.json'
$validator = Join-Path $wrapperRoot 'validate_artifact_schema.ps1'
$artifactPath = Join-Path $fixtureRoot 'visual_delivery_gate_report.json'

$passed = 0
$failed = 0
$total = 0

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

Write-Host ''
Write-Host '=== Visual Gate not_required Schema Test ==='
Write-Host ''

if (Test-Path -LiteralPath $fixtureRoot) {
    Remove-Item -LiteralPath $fixtureRoot -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $fixtureRoot | Out-Null

$artifact = [ordered]@{
    schema = 'visual_delivery_gate_report.v1'
    ready_for_aaa = $true
    measurement_level = 'vdp_dump_verified'
    leaf_blocker_propagation = $true
    workspace_scope_isolation = $true
    visual_vdp_dump_required = $true
    visual_vdp_dump_status = 'not_required'
    baseline_comparison_status = 'not_required'
    critical_assets = @()
}

$artifact | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $artifactPath -Encoding UTF8

$schemaOutput = & powershell -NoProfile -ExecutionPolicy Bypass -File $validator -SchemaPath $schemaPath -ArtifactPath $artifactPath 2>&1
$exitCode = $LASTEXITCODE
$joinedOutput = ($schemaOutput -join '; ')

Assert-True 'schema rejeita visual_vdp_dump_status=not_required' ($exitCode -ne 0 -and $joinedOutput -match "visual_vdp_dump_status")
Assert-True 'schema rejeita baseline_comparison_status=not_required' ($joinedOutput -match "baseline_comparison_status")

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0

