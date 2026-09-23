Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$gateScript = Join-Path $wrapperRoot 'scene_capture_gate.ps1'

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

function New-TestSram {
    param(
        [Parameter(Mandatory)][string]$Path,
        [Parameter(Mandatory)][int]$SceneId,
        [Parameter(Mandatory)][bool]$Ready
    )

    $bytes = New-Object byte[] 1024
    if ($Ready) {
        [System.Text.Encoding]::ASCII.GetBytes('READY').CopyTo($bytes, 0x100)
    }

    [System.Text.Encoding]::ASCII.GetBytes('MDRT').CopyTo($bytes, 0x200)
    $bytes[0x204] = 0x00
    $bytes[0x205] = 0x01
    $bytes[0x206] = 0x00
    $bytes[0x207] = 0x16
    $bytes[0x208] = 0x00
    $bytes[0x209] = 0x06

    $payloadOffset = 0x20A
    $words = @(0, 0, 1, 0, 0, $SceneId)
    for ($i = 0; $i -lt $words.Count; $i++) {
        $wordOffset = $payloadOffset + ($i * 2)
        $bytes[$wordOffset] = [byte](($words[$i] -shr 8) -band 0xFF)
        $bytes[$wordOffset + 1] = [byte]($words[$i] -band 0xFF)
    }

    [System.IO.File]::WriteAllBytes($Path, $bytes)
}

function New-SceneEvidence {
    param(
        [Parameter(Mandatory)][string]$Root,
        [Parameter(Mandatory)][string]$SceneKey,
        [Parameter(Mandatory)][bool]$IncludeScreenshot,
        [Parameter(Mandatory)][bool]$IncludeSram,
        [Parameter(Mandatory)][int]$CapturedSceneId,
        [Parameter(Mandatory)][bool]$Ready,
        [Parameter(Mandatory)][bool]$WriteContradictoryBundle
    )

    $sceneDir = Join-Path $Root ("out\\evidence\\scenes\\" + $SceneKey)
    New-Item -ItemType Directory -Force -Path $sceneDir | Out-Null

    if ($IncludeScreenshot) {
        Set-Content -LiteralPath (Join-Path $sceneDir 'screenshot.png') -Value 'PNGDATA' -Encoding ASCII
    }
    if ($IncludeSram) {
        New-TestSram -Path (Join-Path $sceneDir 'save.sram') -SceneId $CapturedSceneId -Ready:$Ready
    }
    if ($WriteContradictoryBundle) {
        Set-Content -LiteralPath (Join-Path $sceneDir 'bundle.json') -Encoding UTF8 -Value (@{
            capture_status = 'failed'
            failure_reason = 'synthetic contradiction'
        } | ConvertTo-Json -Depth 4)
    }
}

$tempRoot = Join-Path $env:TEMP "sgdk_scene_capture_gate_$([guid]::NewGuid().ToString('N'))"

try {
    $docDir = Join-Path $tempRoot 'doc'
    $logsDir = Join-Path $tempRoot 'out\logs'
    New-Item -ItemType Directory -Force -Path $docDir, $logsDir | Out-Null

    $manifest = [ordered]@{
        schema_version = '1.0.0'
        project = 'synthetic_gate'
        scenes = @(
            [ordered]@{
                scene_id = 'scene_ok'
                expected_app_scene_id = 2
                required_artifacts = @('screenshot', 'sram')
            },
            [ordered]@{
                scene_id = 'scene_wrong'
                expected_app_scene_id = 2
                required_artifacts = @('screenshot', 'sram')
            },
            [ordered]@{
                scene_id = 'scene_degraded'
                expected_app_scene_id = 2
                required_artifacts = @('screenshot', 'sram')
            },
            [ordered]@{
                scene_id = 'scene_failed'
                expected_app_scene_id = 2
                required_artifacts = @('screenshot', 'sram')
            }
        )
    }
    Set-Content -LiteralPath (Join-Path $docDir 'scene-regression.json') -Encoding UTF8 -Value ($manifest | ConvertTo-Json -Depth 8)

    New-SceneEvidence -Root $tempRoot -SceneKey 'scene_ok' -IncludeScreenshot:$true -IncludeSram:$true -CapturedSceneId 2 -Ready:$true -WriteContradictoryBundle:$true
    New-SceneEvidence -Root $tempRoot -SceneKey 'scene_wrong' -IncludeScreenshot:$true -IncludeSram:$true -CapturedSceneId 7 -Ready:$true -WriteContradictoryBundle:$false
    New-SceneEvidence -Root $tempRoot -SceneKey 'scene_degraded' -IncludeScreenshot:$true -IncludeSram:$true -CapturedSceneId 2 -Ready:$false -WriteContradictoryBundle:$false
    New-SceneEvidence -Root $tempRoot -SceneKey 'scene_failed' -IncludeScreenshot:$false -IncludeSram:$true -CapturedSceneId 2 -Ready:$true -WriteContradictoryBundle:$false

    Write-Host ''
    Write-Host '=== Scene Capture Gate Test ==='
    Write-Host ''

    $cases = @(
        @{ scene = 'scene_ok'; expected = 'ok' },
        @{ scene = 'scene_wrong'; expected = 'wrong_scene' },
        @{ scene = 'scene_degraded'; expected = 'degraded' },
        @{ scene = 'scene_failed'; expected = 'failed' }
    )

    foreach ($case in $cases) {
        & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $gateScript -ProjectRoot $tempRoot -SceneId $case.scene -WarnOnly | Out-Null
        $exitCode = $LASTEXITCODE
        $report = Get-Content -LiteralPath (Join-Path $logsDir 'scene_capture_gate_report.json') -Raw -Encoding UTF8 | ConvertFrom-Json
        $gateResult = $report.gate_result

        Assert-True "$($case.scene) returns expected capture_status" ($gateResult.capture_status -eq $case.expected) $gateResult.failure_reason
        Assert-True "$($case.scene) exits cleanly in warn mode" ($exitCode -eq 0) "exit=$exitCode"
    }

    $okReport = Get-Content -LiteralPath (Join-Path $logsDir 'scene_capture_gate_report.json') -Raw -Encoding UTF8 | ConvertFrom-Json
    Assert-True 'last report remains structured' ($null -ne $okReport.gate_result)

    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $gateScript -ProjectRoot $tempRoot -SceneId 'scene_ok' -WarnOnly | Out-Null
    $okReport = Get-Content -LiteralPath (Join-Path $logsDir 'scene_capture_gate_report.json') -Raw -Encoding UTF8 | ConvertFrom-Json
    Assert-True 'bundle.json contradiction does not beat raw evidence' ($okReport.gate_result.capture_status -eq 'ok')
}
finally {
    Remove-Item -LiteralPath $tempRoot -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
