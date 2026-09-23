<#
.SYNOPSIS
    Verifies CRAM byte parsing in vdp_inspection.psm1 using a fixed fixture.
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
Write-Host '=== VDP Inspection CRAM Fixture Test ==='
Write-Host ''

$module = Import-Module (Join-Path $wrapperRoot 'lib\vdp_inspection.psm1') -Force -PassThru
$MeasureVdpPaletteUsage = $module.ExportedCommands['Measure-VdpPaletteUsage']

$cram = New-Object byte[] 128

# Palette 0, entry 1 = red, entry 2 = green, entry 3 = blue.
$cram[2] = 0x00; $cram[3] = 0x0E
$cram[4] = 0x00; $cram[5] = 0xE0
$cram[6] = 0x0E; $cram[7] = 0x00

$snapshot = & $MeasureVdpPaletteUsage -Cram $cram
$palette0 = @($snapshot.palettes)[0]
$entries = @($palette0.entries)

Assert-True 'Palette 0 unique_colors=3' ($palette0.unique_colors -eq 3) "got $($palette0.unique_colors)"
Assert-True 'Entry 1 raw_value keeps low-byte red' ($entries[1].raw_value -eq 0x000E) "got $($entries[1].raw_value)"
Assert-True 'Entry 2 raw_value keeps green' ($entries[2].raw_value -eq 0x00E0) "got $($entries[2].raw_value)"
Assert-True 'Entry 3 raw_value keeps high-byte blue' ($entries[3].raw_value -eq 0x0E00) "got $($entries[3].raw_value)"
Assert-True 'Entry 1 hex_rgb is red' ($entries[1].hex_rgb -eq '#FF0000') "got $($entries[1].hex_rgb)"
Assert-True 'Entry 2 hex_rgb is green' ($entries[2].hex_rgb -eq '#00FF00') "got $($entries[2].hex_rgb)"
Assert-True 'Entry 3 hex_rgb is blue' ($entries[3].hex_rgb -eq '#0000FF') "got $($entries[3].hex_rgb)"

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
