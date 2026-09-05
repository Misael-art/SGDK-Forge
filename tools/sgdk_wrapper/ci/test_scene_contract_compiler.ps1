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
$cutsceneRoot = $null

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

    $cutsceneRoot = Join-Path $env:TEMP "sgdk_scene_contract_compiler_cutscene_$([guid]::NewGuid().ToString('N'))"
    New-Item -ItemType Directory -Force -Path (Join-Path $cutsceneRoot 'doc\contracts') | Out-Null
    New-Item -ItemType Directory -Force -Path (Join-Path $cutsceneRoot 'out\logs') | Out-Null

    @'
# Scene Contract Compiler Cutscene Fixture

### Cena 1 - `intro_cutscene`

- Papel: cutscene
'@ | Set-Content -LiteralPath (Join-Path $cutsceneRoot 'doc\13-spec-cenas.md') -Encoding UTF8

    $cutsceneContract = [ordered]@{
        schema_version                  = '1.0.0'
        scene_id                        = 'intro_cutscene'
        scene_role                      = 'cutscene'
        cutscene_mode                   = 'panel_sequence'
        fsm_script                      = 'doc/contracts/intro_fsm.json'
        resource_plan                   = 'doc/contracts/intro_resource_plan.json'
        panel_layout                    = 'doc/contracts/intro_panel_layout.json'
        text_timing_map                 = 'doc/contracts/intro_text_timing.json'
        glyph_manifest                  = 'doc/contracts/intro_glyph_manifest.json'
        advance_model                   = 'MIXED'
        teardown_plan                   = 'doc/contracts/intro_teardown_plan.json'
        evidence_plan                   = 'doc/contracts/intro_evidence_plan.json'
        uses_fullscreen_bitmap          = $false
        dynamic_fx                      = @('palette_cycling')
        cinematic_storyboard_contract   = 'doc/contracts/intro_cinematic_storyboard_contract.json'
    }
    $cutsceneContract |
        ConvertTo-Json -Depth 8 |
        Set-Content -LiteralPath (Join-Path $cutsceneRoot 'doc\contracts\intro_cutscene_contract.json') -Encoding UTF8

    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $compilerScript -ProjectRoot $cutsceneRoot -Mode production -WarnOnly | Out-Null
    $cutsceneCompiled = Get-Content -LiteralPath (Join-Path $cutsceneRoot 'doc\scene-contracts.json') -Raw -Encoding UTF8 | ConvertFrom-Json
    $cutsceneReport = Get-Content -LiteralPath (Join-Path $cutsceneRoot 'out\logs\scene_contract_report.json') -Raw -Encoding UTF8 | ConvertFrom-Json
    $introScene = @($cutsceneCompiled.scenes | Where-Object { $_.scene_id -eq 'intro_cutscene' })[0]
    $introSc100 = @($cutsceneReport.findings | Where-Object { $_.scene_id -eq 'intro_cutscene' -and $_.code -eq 'SC100' })

    Assert-True 'cutscene contract file is projected into compiled scene contract' (
        $null -ne $introScene -and
        $introScene.PSObject.Properties['cutscene_contract'] -and
        $introScene.cutscene_contract.fsm_script -eq 'doc/contracts/intro_fsm.json'
    )
    Assert-True 'projected cutscene contract removes SC100 in production lint' ($introSc100.Count -eq 0)
}
finally {
    Remove-Item -LiteralPath $tempRoot -Recurse -Force -ErrorAction SilentlyContinue
    if ($cutsceneRoot) {
        Remove-Item -LiteralPath $cutsceneRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
