<#
.SYNOPSIS
    Evidence comparison functions for the scene regression runner.
.DESCRIPTION
    Provides pluggable comparators for different artifact types:
    exact hash, tolerant image diff, binary exact, and palette snapshot.

    This module does NOT modify any existing wrapper behavior.
#>

Set-StrictMode -Version Latest

# ---------------------------------------------------------------------------
# Compare-ExactHash
# ---------------------------------------------------------------------------
function Compare-ExactHash {
    <#
    .SYNOPSIS
        Compares two files by SHA256 hash.
    .PARAMETER BaselinePath
        Path to the baseline file.
    .PARAMETER CurrentPath
        Path to the current file.
    .OUTPUTS
        Hashtable: Match (bool), BaselineHash, CurrentHash
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$BaselinePath,
        [Parameter(Mandatory)][string]$CurrentPath
    )

    $result = @{ Match = $false; BaselineHash = $null; CurrentHash = $null; Error = $null }

    if (-not (Test-Path -LiteralPath $BaselinePath)) {
        $result.Error = "Baseline file missing: $BaselinePath"
        return $result
    }
    if (-not (Test-Path -LiteralPath $CurrentPath)) {
        $result.Error = "Current file missing: $CurrentPath"
        return $result
    }

    $result.BaselineHash = (Get-FileHash -LiteralPath $BaselinePath -Algorithm SHA256).Hash.ToLower()
    $result.CurrentHash = (Get-FileHash -LiteralPath $CurrentPath -Algorithm SHA256).Hash.ToLower()
    $result.Match = ($result.BaselineHash -eq $result.CurrentHash)

    return $result
}

# ---------------------------------------------------------------------------
# Compare-ImageTolerance
# ---------------------------------------------------------------------------
function Compare-ImageTolerance {
    <#
    .SYNOPSIS
        Compares two PNG images with pixel-level tolerance.
    .DESCRIPTION
        Uses System.Drawing to compare pixel-by-pixel.
        Returns the fraction of pixels that differ.
    .PARAMETER BaselinePath
        Path to the baseline PNG.
    .PARAMETER CurrentPath
        Path to the current PNG.
    .PARAMETER Threshold
        Maximum fraction of differing pixels to consider a match (0.0-1.0).
    .PARAMETER CropRect
        Optional comparison rectangle with x, y, width, and height.
    .OUTPUTS
        Hashtable: Match (bool), DiffFraction (float), DiffPixels (int), TotalPixels (int), Error
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$BaselinePath,
        [Parameter(Mandatory)][string]$CurrentPath,
        [double]$Threshold = 0.0,
        [object]$CropRect = $null
    )

    $result = @{
        Match = $false
        DiffFraction = 1.0
        DiffPixels = 0
        TotalPixels = 0
        CropRect = $null
        Error = $null
    }

    if (-not (Test-Path -LiteralPath $BaselinePath)) {
        $result.Error = "Baseline image missing: $BaselinePath"
        return $result
    }
    if (-not (Test-Path -LiteralPath $CurrentPath)) {
        $result.Error = "Current image missing: $CurrentPath"
        return $result
    }

    try {
        Add-Type -AssemblyName System.Drawing

        $baseSrc = [System.Drawing.Image]::FromFile($BaselinePath)
        $currSrc = [System.Drawing.Image]::FromFile($CurrentPath)

        try {
            if ($baseSrc.Width -ne $currSrc.Width -or $baseSrc.Height -ne $currSrc.Height) {
                $result.Error = "Image dimensions differ: baseline=$($baseSrc.Width)x$($baseSrc.Height) vs current=$($currSrc.Width)x$($currSrc.Height)"
                return $result
            }

            $compareX = 0
            $compareY = 0
            $compareWidth = [int]$baseSrc.Width
            $compareHeight = [int]$baseSrc.Height

            if ($null -ne $CropRect) {
                $readCropValue = {
                    param($Obj, [string]$Name, [int]$Default)

                    if ($Obj -is [System.Collections.IDictionary] -and $Obj.Contains($Name)) {
                        return [int]$Obj[$Name]
                    }

                    $prop = $Obj.PSObject.Properties[$Name]
                    if ($prop) {
                        return [int]$prop.Value
                    }

                    return $Default
                }

                $compareX = & $readCropValue $CropRect 'x' 0
                $compareY = & $readCropValue $CropRect 'y' 0
                $compareWidth = & $readCropValue $CropRect 'width' $compareWidth
                $compareHeight = & $readCropValue $CropRect 'height' $compareHeight

                if ($compareX -lt 0 -or $compareY -lt 0 -or $compareWidth -le 0 -or $compareHeight -le 0 -or
                    ($compareX + $compareWidth) -gt $baseSrc.Width -or ($compareY + $compareHeight) -gt $baseSrc.Height) {
                    $result.Error = "Invalid image crop rectangle: x=$compareX y=$compareY width=$compareWidth height=$compareHeight for image $($baseSrc.Width)x$($baseSrc.Height)"
                    return $result
                }

                $result.CropRect = @{
                    x = $compareX
                    y = $compareY
                    width = $compareWidth
                    height = $compareHeight
                }
            }

            $baseImg = New-Object System.Drawing.Bitmap($baseSrc.Width, $baseSrc.Height, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
            $currImg = New-Object System.Drawing.Bitmap($currSrc.Width, $currSrc.Height, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
            $baseG = [System.Drawing.Graphics]::FromImage($baseImg)
            $currG = [System.Drawing.Graphics]::FromImage($currImg)

            try {
                $baseG.DrawImage($baseSrc, 0, 0, $baseSrc.Width, $baseSrc.Height)
                $currG.DrawImage($currSrc, 0, 0, $currSrc.Width, $currSrc.Height)

                $totalPixels = $compareWidth * $compareHeight
                $diffPixels = 0

                for ($y = $compareY; $y -lt ($compareY + $compareHeight); $y++) {
                    for ($x = $compareX; $x -lt ($compareX + $compareWidth); $x++) {
                        $bp = $baseImg.GetPixel($x, $y)
                        $cp = $currImg.GetPixel($x, $y)
                        if ($bp.ToArgb() -ne $cp.ToArgb()) {
                            $diffPixels++
                        }
                    }
                }

                $result.TotalPixels = $totalPixels
                $result.DiffPixels = $diffPixels
                $result.DiffFraction = if ($totalPixels -gt 0) { [double]$diffPixels / $totalPixels } else { 0.0 }
                $result.Match = ($result.DiffFraction -le $Threshold)
            }
            finally {
                $baseG.Dispose()
                $currG.Dispose()
                $baseImg.Dispose()
                $currImg.Dispose()
            }
        }
        finally {
            $baseSrc.Dispose()
            $currSrc.Dispose()
        }
    }
    catch {
        $result.Error = "Image comparison error: $($_.Exception.Message)"
    }

    return $result
}

# ---------------------------------------------------------------------------
# Compare-BinaryExact
# ---------------------------------------------------------------------------
function Compare-BinaryExact {
    <#
    .SYNOPSIS
        Compares two binary files byte-by-byte.
    .OUTPUTS
        Hashtable: Match (bool), BaselineSize, CurrentSize, Error
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$BaselinePath,
        [Parameter(Mandatory)][string]$CurrentPath
    )

    $result = @{ Match = $false; BaselineSize = 0; CurrentSize = 0; Error = $null }

    if (-not (Test-Path -LiteralPath $BaselinePath)) {
        $result.Error = "Baseline file missing: $BaselinePath"
        return $result
    }
    if (-not (Test-Path -LiteralPath $CurrentPath)) {
        $result.Error = "Current file missing: $CurrentPath"
        return $result
    }

    $baseInfo = Get-Item -LiteralPath $BaselinePath
    $currInfo = Get-Item -LiteralPath $CurrentPath
    $result.BaselineSize = $baseInfo.Length
    $result.CurrentSize = $currInfo.Length

    if ($baseInfo.Length -ne $currInfo.Length) {
        return $result
    }

    # Use hash comparison for efficiency
    $baseHash = (Get-FileHash -LiteralPath $BaselinePath -Algorithm SHA256).Hash
    $currHash = (Get-FileHash -LiteralPath $CurrentPath -Algorithm SHA256).Hash
    $result.Match = ($baseHash -eq $currHash)

    return $result
}

# ---------------------------------------------------------------------------
# Compare-PaletteSnapshot
# ---------------------------------------------------------------------------
function Compare-PaletteSnapshot {
    <#
    .SYNOPSIS
        Compares two palette snapshot JSON files.
    .DESCRIPTION
        Reads palette arrays from JSON and compares entry-by-entry.
        Palette files are expected to have a "palettes" array of arrays.
    .OUTPUTS
        Hashtable: Match (bool), DiffEntries (int), TotalEntries (int), Error
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$BaselinePath,
        [Parameter(Mandatory)][string]$CurrentPath
    )

    $result = @{ Match = $false; DiffEntries = 0; TotalEntries = 0; Error = $null }

    if (-not (Test-Path -LiteralPath $BaselinePath)) {
        $result.Error = "Baseline palette missing: $BaselinePath"
        return $result
    }
    if (-not (Test-Path -LiteralPath $CurrentPath)) {
        $result.Error = "Current palette missing: $CurrentPath"
        return $result
    }

    try {
        $basePal = (Get-Content -LiteralPath $BaselinePath -Raw -Encoding UTF8 | ConvertFrom-Json)
        $currPal = (Get-Content -LiteralPath $CurrentPath -Raw -Encoding UTF8 | ConvertFrom-Json)

        $baseJson = $basePal | ConvertTo-Json -Depth 10 -Compress
        $currJson = $currPal | ConvertTo-Json -Depth 10 -Compress

        $result.Match = ($baseJson -eq $currJson)

        # Count entries for reporting
        if ($basePal.PSObject.Properties['palettes']) {
            $result.TotalEntries = @($basePal.palettes | ForEach-Object { @($_) }).Count
        }
        if (-not $result.Match -and $result.TotalEntries -gt 0) {
            $result.DiffEntries = 1  # simplified — at least one palette differs
        }
    }
    catch {
        $result.Error = "Palette comparison error: $($_.Exception.Message)"
    }

    return $result
}

# ---------------------------------------------------------------------------
# Exports
# ---------------------------------------------------------------------------
Export-ModuleMember -Function @(
    'Compare-ExactHash',
    'Compare-ImageTolerance',
    'Compare-BinaryExact',
    'Compare-PaletteSnapshot'
)
