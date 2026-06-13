<#
.SYNOPSIS
    Verifica que projeto .mddev com category=lab/debug_lab nao pode herdar
    claim_ceiling=ready_for_aaa por padrao.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$workspaceRoot = Split-Path (Split-Path $wrapperRoot -Parent) -Parent
$projectRoot = Join-Path $workspaceRoot 'out\ci\lab_category_product_taxonomy_fixture'
$validateScript = Join-Path $wrapperRoot 'validate_resources.ps1'
$reportPath = Join-Path $projectRoot 'out\logs\validation_report.json'

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
Write-Host '=== Lab Category Product Taxonomy Test ==='
Write-Host ''

if (Test-Path -LiteralPath $projectRoot) {
    Remove-Item -LiteralPath $projectRoot -Recurse -Force
}
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot '.mddev') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'res\data') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'src') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'doc\changelog') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'out\logs') | Out-Null

@{
    display_name = 'Lab taxonomy fixture'
    kind = 'game'
    category = 'lab'
    layout = 'flat'
    schema_version = 1
} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $projectRoot '.mddev\project.json') -Encoding UTF8

Set-Content -LiteralPath (Join-Path $projectRoot 'doc\changelog\changelog.md') -Value '# CI fixture' -Encoding UTF8
Set-Content -LiteralPath (Join-Path $projectRoot 'res\data\dummy.bin') -Value 'dummy resource bytes' -Encoding UTF8
Set-Content -LiteralPath (Join-Path $projectRoot 'res\resources.res') -Value 'BIN dummy_blob "data/dummy.bin"' -Encoding UTF8
Set-Content -LiteralPath (Join-Path $projectRoot 'src\main.c') -Value '#include <genesis.h>' -Encoding UTF8

& powershell -NoProfile -ExecutionPolicy Bypass -File $validateScript -WorkDir $projectRoot | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "validate_resources.ps1 failed with exit code $LASTEXITCODE"
}

$report = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json

Assert-True 'category=lab vira technical_lab_validated' ([string]$report.product_taxonomy.product_status -eq 'technical_lab_validated') ([string]$report.product_taxonomy.product_status)
Assert-True 'category=lab limita claim ceiling' ([string]$report.product_taxonomy.claim_ceiling -eq 'vertical_slice_candidate') ([string]$report.product_taxonomy.claim_ceiling)
Assert-True 'ready_for_aaa continua falso' (-not [bool]$report.status_panel.ready_for_aaa)

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0

