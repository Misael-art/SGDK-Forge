Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
Import-Module (Join-Path $wrapperRoot 'lib\evidence_compare.psm1') -Force

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

$tmpRoot = Join-Path $env:TEMP "sgdk_evidence_tolerance_$([guid]::NewGuid().ToString('N').Substring(0,8))"
New-Item -ItemType Directory -Force -Path $tmpRoot | Out-Null

try {
    Add-Type -AssemblyName System.Drawing
    $baselinePath = Join-Path $tmpRoot 'baseline.png'
    $currentPath = Join-Path $tmpRoot 'current.png'
    $differentSizePath = Join-Path $tmpRoot 'different_size.png'

    $baseline = New-Object System.Drawing.Bitmap(2, 2)
    $current = New-Object System.Drawing.Bitmap(2, 2)
    $differentSize = New-Object System.Drawing.Bitmap(3, 2)
    try {
        $baseline.SetPixel(0, 0, [System.Drawing.Color]::White)
        $current.SetPixel(0, 0, [System.Drawing.Color]::Black)
        $baseline.Save($baselinePath, [System.Drawing.Imaging.ImageFormat]::Png)
        $current.Save($currentPath, [System.Drawing.Imaging.ImageFormat]::Png)
        $differentSize.Save($differentSizePath, [System.Drawing.Imaging.ImageFormat]::Png)
    }
    finally {
        $baseline.Dispose()
        $current.Dispose()
        $differentSize.Dispose()
    }

    $passResult = Compare-ImageTolerance -BaselinePath $baselinePath -CurrentPath $currentPath -Threshold 0.25
    $failResult = Compare-ImageTolerance -BaselinePath $baselinePath -CurrentPath $currentPath -Threshold 0.24
    $sizeResult = Compare-ImageTolerance -BaselinePath $baselinePath -CurrentPath $differentSizePath -Threshold 1.0

    Assert-True 'Threshold accepts exact diff fraction' ($passResult.Match -eq $true) $passResult.Error
    Assert-True 'Threshold rejects larger diff fraction' ($failResult.Match -eq $false) $failResult.Error
    Assert-True 'Diff fraction is measured as 0.25' ([math]::Abs($passResult.DiffFraction - 0.25) -lt 0.0001) $passResult.DiffFraction
    Assert-True 'Dimension mismatch returns readable error' ($sizeResult.Error -like 'Image dimensions differ:*') $sizeResult.Error
}
finally {
    Remove-Item -Recurse -Force $tmpRoot -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
