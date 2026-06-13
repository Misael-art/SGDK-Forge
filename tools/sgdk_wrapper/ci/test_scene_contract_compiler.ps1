Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$compilerScript = Join-Path $wrapperRoot 'scene_contract_compiler.ps1'
$templateRoot = Join-Path $wrapperRoot 'modelo'

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

$tempRoot = Join-Path $env:TEMP "sgdk_scene_contract_compiler_$([guid]::NewGuid().ToString('N'))"

try {
    Copy-Item -LiteralPath $templateRoot -Destination $tempRoot -Recurse -Force

    Write-Host ''
    Write-Host '=== Scene Contract Compiler Host Smoke Test ==='
    Write-Host ''

    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $compilerScript -ProjectRoot $tempRoot -WarnOnly | Out-Null
    $exitCode = $LASTEXITCODE

    $contractPath = Join-Path $tempRoot 'doc\scene-contracts.json'
    $reportPath = Join-Path $tempRoot 'out\logs\scene_contract_compile_report.json'

    $report = $null
    if (Test-Path -LiteralPath $reportPath -PathType Leaf) {
        $report = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json
    }

    Assert-True 'compiler exits cleanly in powershell.exe' ($exitCode -eq 0) "exit=$exitCode"
    Assert-True 'compiled contract is generated' (Test-Path -LiteralPath $contractPath -PathType Leaf)
    Assert-True 'compile report is generated' (Test-Path -LiteralPath $reportPath -PathType Leaf)
    Assert-True 'lint ran in warn mode' ($null -ne $report -and [bool]$report.lint_result.lint_ran)
    Assert-True 'compiler produced at least one scene' ($null -ne $report -and [int]$report.scenes_compiled -gt 0)

    $firstWriteUtc = (Get-Item -LiteralPath $contractPath).LastWriteTimeUtc
    Start-Sleep -Milliseconds 1100
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $compilerScript -ProjectRoot $tempRoot -WarnOnly | Out-Null
    $secondWriteUtc = (Get-Item -LiteralPath $contractPath).LastWriteTimeUtc
    Assert-True 'unchanged contract preserves timestamp' ($secondWriteUtc -eq $firstWriteUtc) "first=$firstWriteUtc second=$secondWriteUtc"
}
finally {
    Remove-Item -LiteralPath $tempRoot -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
