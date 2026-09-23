<#
.SYNOPSIS
    Verifica que o parser MDRT do scene_capture_gate usa o mesmo layout canônico do runtime.
.DESCRIPTION
    Monta um save.sram sintético com bloco MDRT em 0x200, onde:
    - words[0..1] contêm o probe magic
    - words[5] contém scene_id=2
    O teste garante que o gate não leia o primeiro word como scene_id.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
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
Write-Host '=== Scene Capture Gate MDRT Parser Test ==='
Write-Host ''

$tmpRoot = Join-Path $env:TEMP "sgdk_gate_parser_$([guid]::NewGuid().ToString('N').Substring(0,8))"
$evidenceDir = Join-Path $tmpRoot 'evidence'
New-Item -ItemType Directory -Force -Path $evidenceDir | Out-Null

$sramPath = Join-Path $evidenceDir 'save.sram'
$screenshotPath = Join-Path $evidenceDir 'screenshot.png'

[System.IO.File]::WriteAllBytes($screenshotPath, [byte[]](1,2,3,4))

$bytes = New-Object byte[] 1024
$offset = 0x200
[System.Text.Encoding]::ASCII.GetBytes('MDRT').CopyTo($bytes, $offset)

function Set-U16BE {
    param([byte[]]$Buffer, [int]$At, [int]$Value)
    $Buffer[$At] = [byte](($Value -shr 8) -band 0xFF)
    $Buffer[$At + 1] = [byte]($Value -band 0xFF)
}

$schema = 1
$wordCount = 64
$totalBytes = 10 + ($wordCount * 2)
Set-U16BE -Buffer $bytes -At ($offset + 4) -Value $schema
Set-U16BE -Buffer $bytes -At ($offset + 6) -Value $totalBytes
Set-U16BE -Buffer $bytes -At ($offset + 8) -Value $wordCount

$payloadWords = New-Object int[] $wordCount
$payloadWords[0] = 19780
$payloadWords[1] = 21076
$payloadWords[2] = 1
$payloadWords[4] = 60
$payloadWords[5] = 2

$pos = $offset + 10
for ($i = 0; $i -lt $wordCount; $i++) {
    Set-U16BE -Buffer $bytes -At $pos -Value $payloadWords[$i]
    $pos += 2
}

[System.IO.File]::WriteAllBytes($sramPath, $bytes)

Import-Module (Join-Path $wrapperRoot 'lib\scene_capture_gate.psm1') -Force

$sceneEntry = [pscustomobject]@{
    scene_id = 'scene_multiplane_showcase_v2'
    expected_app_scene_id = 2
    capture_kind = 'evidence_bundle'
}

$gateResult = Test-SceneCaptureSuccess -SceneManifestEntry $sceneEntry -EvidencePath $evidenceDir -RomSha256 'TEST' -RequireHeartbeat:$false

Write-Host '--- Assertions ---'
Assert-True 'MDRT presente' ($gateResult.mdrt_present -eq $true)
Assert-True 'captured_app_scene_id = 2' ($gateResult.captured_app_scene_id -eq 2) "got $($gateResult.captured_app_scene_id)"
Assert-True 'scene_match = true' ($gateResult.scene_match -eq $true)
Assert-True 'capture_status = ok' ($gateResult.capture_status -eq 'ok') "got $($gateResult.capture_status)"

Remove-Item -Recurse -Force $tmpRoot -ErrorAction SilentlyContinue

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
