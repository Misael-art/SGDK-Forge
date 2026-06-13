Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
Import-Module (Join-Path $wrapperRoot 'lib\scene_regression.psm1') -Force

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
        Write-Host "  [FAIL] $Name -- $Detail"
    }
}

function Read-U16BE {
    param([byte[]]$Bytes, [int]$Offset)
    return ([int]$Bytes[$Offset] -shl 8) -bor [int]$Bytes[$Offset + 1]
}

$config = [pscustomobject]@{
    scene_id = 'capture_hold_scene'
    boot_mode = 'sram_bootstrap'
    expected_app_scene_id = 4
    capture_hold_frame = 120
}

$bootstrap = Invoke-SceneBootstrap -SceneConfig $config -ProjectRoot $env:TEMP
$bytes = [byte[]]$bootstrap.InitialSramBytes
$offset = 0x120

Assert-True 'Bootstrap succeeds' ($bootstrap.Bootstrapped -eq $true) $bootstrap.Note
Assert-True 'SBIS v2 schema emitted' ((Read-U16BE $bytes ($offset + 4)) -eq 2)
Assert-True 'SBIS v2 length emitted' ((Read-U16BE $bytes ($offset + 6)) -eq 16)
Assert-True 'Scene id emitted' ((Read-U16BE $bytes ($offset + 8)) -eq 4)
Assert-True 'Capture hold frame emitted' ((Read-U16BE $bytes ($offset + 10)) -eq 120)
Assert-True 'Capture hold flag emitted' ((Read-U16BE $bytes ($offset + 12)) -eq 1)

Write-Host ""
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
