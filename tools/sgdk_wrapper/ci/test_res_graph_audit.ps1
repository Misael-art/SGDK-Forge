Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$auditScript = Join-Path $wrapperRoot 'res_graph_audit.ps1'

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

$tempRoot = Join-Path $env:TEMP "sgdk_res_graph_audit_$([guid]::NewGuid().ToString('N'))"

try {
    $resDir = Join-Path $tempRoot 'res'
    $assetsDir = Join-Path $resDir 'assets'
    $audioDir = Join-Path $resDir 'audio'
    $mapsDir = Join-Path $resDir 'maps'
    $logsDir = Join-Path $tempRoot 'out\logs'

    New-Item -ItemType Directory -Force -Path $assetsDir, $audioDir, $mapsDir, $logsDir | Out-Null
    Set-Content -LiteralPath (Join-Path $assetsDir 'hero.png') -Value 'PNGDATA' -Encoding ASCII
    Set-Content -LiteralPath (Join-Path $audioDir 'theme.xgm') -Value 'XGMDATA' -Encoding ASCII
    Set-Content -LiteralPath (Join-Path $audioDir 'hit.raw') -Value 'RAWDATA' -Encoding ASCII
    Set-Content -LiteralPath (Join-Path $mapsDir 'stage.map') -Value 'MAPDATA' -Encoding ASCII
    Set-Content -LiteralPath (Join-Path $resDir 'resources.res') -Encoding ASCII -Value @(
        'IMAGE hero "assets/hero.png" BEST'
        'XGM theme "audio/theme.xgm"'
        'BIN hit_raw "audio/hit.raw"'
        'MAP stage_map "maps/stage.map"'
    )

    Write-Host ''
    Write-Host '=== Res Graph Audit Host Smoke Test ==='
    Write-Host ''

    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $auditScript -ProjectRoot $tempRoot -WarnOnly | Out-Null
    $exitCode = $LASTEXITCODE

    $reportPath = Join-Path $logsDir 'res_graph_report.json'
    $summaryPath = Join-Path $logsDir 'res_graph_summary.md'
    $report = $null
    if (Test-Path -LiteralPath $reportPath -PathType Leaf) {
        $report = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json
    }

    Assert-True 'audit exits cleanly in powershell.exe' ($exitCode -eq 0) "exit=$exitCode"
    Assert-True 'json report is generated' (Test-Path -LiteralPath $reportPath -PathType Leaf)
    Assert-True 'markdown summary is generated' (Test-Path -LiteralPath $summaryPath -PathType Leaf)
    Assert-True 'report contains declarations' ($null -ne $report -and [int]$report.summary.declarations_total -ge 4)
    Assert-True 'report has no missing-source errors in fixture' ($null -ne $report -and [int]$report.summary.declarations_missing -eq 0)
}
finally {
    Remove-Item -LiteralPath $tempRoot -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
