<#
.SYNOPSIS
    VDP state inspection module for the AAA agent ecosystem.
.DESCRIPTION
    Provides functions to parse VDP dumps, analyze palette/tile/sprite state,
    and produce structured inspection artifacts.

    DECISION PENDING: The definitive VDP dump format from BlastEm is not yet
    documented. This module provides a best-effort parser that handles the
    known VRAM layout (64KB). If the dump format changes, only this module
    needs to be updated.

    This module does NOT modify any existing wrapper behavior.
#>

Set-StrictMode -Version Latest

# Mega Drive VDP constants
$script:VRAM_SIZE = 65536        # 64KB
$script:TILE_SIZE = 32           # 8x8 tile = 32 bytes (4bpp)
$script:TOTAL_TILES = 2048       # 64KB / 32 bytes
$script:CRAM_SIZE = 128          # 64 entries * 2 bytes
$script:SAT_SIZE = 640           # 80 sprites * 8 bytes
$script:PALETTES = 4
$script:COLORS_PER_PALETTE = 16

# ---------------------------------------------------------------------------
# Import-VdpDump
# ---------------------------------------------------------------------------
function Import-VdpDump {
    <#
    .SYNOPSIS
        Reads a VDP dump binary file and returns raw byte arrays.
    .DESCRIPTION
        Expected dump layout (best-effort — format not yet canonical):
        - Bytes 0-65535: VRAM (64KB)
        - Bytes 65536-65663: CRAM (128 bytes)
        - If file is only VRAM, CRAM/VSRAM are returned as null.
    .PARAMETER DumpPath
        Absolute path to the VDP dump binary file.
    .OUTPUTS
        Hashtable: Vram (byte[]), Cram (byte[] or null), FileSize, Valid
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$DumpPath
    )

    $result = @{
        Vram     = $null
        Cram     = $null
        FileSize = 0
        Valid    = $false
        Error    = $null
    }

    if (-not (Test-Path -LiteralPath $DumpPath)) {
        $result.Error = "VDP dump not found: $DumpPath"
        return $result
    }

    try {
        $bytes = [System.IO.File]::ReadAllBytes($DumpPath)
        $result.FileSize = $bytes.Length

        if ($bytes.Length -ge $script:VRAM_SIZE) {
            $result.Vram = $bytes[0..($script:VRAM_SIZE - 1)]
            $result.Valid = $true
        }

        if ($bytes.Length -ge ($script:VRAM_SIZE + $script:CRAM_SIZE)) {
            $result.Cram = $bytes[$script:VRAM_SIZE..($script:VRAM_SIZE + $script:CRAM_SIZE - 1)]
        }
    }
    catch {
        $result.Error = "Failed to read VDP dump: $($_.Exception.Message)"
    }

    return $result
}

# ---------------------------------------------------------------------------
# Measure-VdpPaletteUsage
# ---------------------------------------------------------------------------
function Measure-VdpPaletteUsage {
    <#
    .SYNOPSIS
        Analyzes CRAM data and produces palette snapshots.
    .PARAMETER Cram
        128-byte CRAM array (or null for empty palettes).
    .OUTPUTS
        Hashtable matching vdp_palette_snapshot schema.
    #>
    [CmdletBinding()]
    param(
        [byte[]]$Cram
    )

    $palettes = @()

    for ($pal = 0; $pal -lt $script:PALETTES; $pal++) {
        $entries = @()
        $uniqueColors = 0

        for ($c = 0; $c -lt $script:COLORS_PER_PALETTE; $c++) {
            $offset = ($pal * $script:COLORS_PER_PALETTE + $c) * 2
            $rawValue = 0
            $r = 0; $g = 0; $b = 0

            if ($Cram -and $offset + 1 -lt $Cram.Length) {
                # MD CRAM is big-endian: 0x0BBB GGG RRR (each component 0-14 even only)
                # Cast to [int] before shift — [byte] -shl 8 overflows to 0
                $rawValue = ([int]$Cram[$offset] -shl 8) -bor [int]$Cram[$offset + 1]
                $b = ($rawValue -shr 9) -band 0x07
                $g = ($rawValue -shr 5) -band 0x07
                $r = ($rawValue -shr 1) -band 0x07
                $b = $b * 2; $g = $g * 2; $r = $r * 2
            }

            if ($rawValue -ne 0 -and $c -gt 0) { $uniqueColors++ }

            $r8 = [math]::Min(255, [int]($r * 255.0 / 14.0))
            $g8 = [math]::Min(255, [int]($g * 255.0 / 14.0))
            $b8 = [math]::Min(255, [int]($b * 255.0 / 14.0))
            $hexRgb = '#{0:X2}{1:X2}{2:X2}' -f $r8, $g8, $b8

            $entries += [ordered]@{
                index     = $c
                raw_value = $rawValue
                r         = $r
                g         = $g
                b         = $b
                hex_rgb   = $hexRgb
            }
        }

        $palettes += [ordered]@{
            index         = $pal
            entries       = $entries
            unique_colors = $uniqueColors
        }
    }

    return @{ palettes = $palettes }
}

# ---------------------------------------------------------------------------
# Measure-VdpTileUsage
# ---------------------------------------------------------------------------
function Measure-VdpTileUsage {
    <#
    .SYNOPSIS
        Analyzes VRAM tile usage: used, unique, and duplicate tiles.
    .PARAMETER Vram
        64KB VRAM byte array.
    .OUTPUTS
        Hashtable with total_tiles, used_tiles, unique_tiles, duplicate_tiles, usage_fraction.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][byte[]]$Vram
    )

    $emptyTile = New-Object byte[] $script:TILE_SIZE
    $hashes = @{}
    $usedCount = 0

    for ($i = 0; $i -lt $script:TOTAL_TILES; $i++) {
        $offset = $i * $script:TILE_SIZE
        if ($offset + $script:TILE_SIZE -gt $Vram.Length) { break }

        $tileBytes = $Vram[$offset..($offset + $script:TILE_SIZE - 1)]

        # Check if tile is non-empty
        $isEmpty = $true
        foreach ($byte in $tileBytes) {
            if ($byte -ne 0) { $isEmpty = $false; break }
        }

        if (-not $isEmpty) {
            $usedCount++
            $hash = [System.BitConverter]::ToString($tileBytes)
            if (-not $hashes.ContainsKey($hash)) {
                $hashes[$hash] = 0
            }
            $hashes[$hash]++
        }
    }

    $uniqueTiles = $hashes.Count
    $duplicateTiles = $usedCount - $uniqueTiles

    return @{
        total_tiles     = $script:TOTAL_TILES
        used_tiles      = $usedCount
        unique_tiles    = $uniqueTiles
        duplicate_tiles = $duplicateTiles
        usage_fraction  = if ($script:TOTAL_TILES -gt 0) { [double]$usedCount / $script:TOTAL_TILES } else { 0.0 }
    }
}

# ---------------------------------------------------------------------------
# Measure-VdpSpriteState
# ---------------------------------------------------------------------------
function Measure-VdpSpriteState {
    <#
    .SYNOPSIS
        Parses the Sprite Attribute Table from VRAM.
    .DESCRIPTION
        SAT is typically at VRAM address configured in VDP register 5.
        Without register state, we assume default SAT address (varies).
        This function accepts an explicit SAT offset or defaults to 0xD800.

        DECISION PENDING: SAT address should come from VDP register dump.
    .PARAMETER Vram
        64KB VRAM byte array.
    .PARAMETER SatOffset
        Byte offset of SAT in VRAM. Default 0xD800 (common SGDK default).
    .OUTPUTS
        Hashtable matching vdp_sprite_snapshot schema.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][byte[]]$Vram,
        [int]$SatOffset = 0xD800
    )

    $sprites = @()
    $scanlineCounts = @{}

    for ($i = 0; $i -lt 80; $i++) {
        $offset = $SatOffset + ($i * 8)
        if ($offset + 8 -gt $Vram.Length) { break }

        # SAT entry format (big-endian):
        # Word 0: Y position (10 bits)
        # Word 1: bits 12-11=height, bits 10-9=width, bits 6-0=link
        # Word 2: bits 15=priority, bits 14-13=palette, bit 12=vflip, bit 11=hflip, bits 10-0=tile
        # Word 3: X position (10 bits)
        $yPos = (([int]$Vram[$offset] -shl 8) -bor [int]$Vram[$offset + 1]) -band 0x3FF
        $sizeLink = ([int]$Vram[$offset + 2] -shl 8) -bor [int]$Vram[$offset + 3]
        $attrTile = ([int]$Vram[$offset + 4] -shl 8) -bor [int]$Vram[$offset + 5]
        $xPos = (([int]$Vram[$offset + 6] -shl 8) -bor [int]$Vram[$offset + 7]) -band 0x3FF

        $heightTiles = (($sizeLink -shr 8) -band 0x03) + 1
        $widthTiles = (($sizeLink -shr 10) -band 0x03) + 1
        $link = $sizeLink -band 0x7F
        $priority = ($attrTile -band 0x8000) -ne 0
        $palette = ($attrTile -shr 13) -band 0x03
        $vFlip = ($attrTile -band 0x1000) -ne 0
        $hFlip = ($attrTile -band 0x0800) -ne 0
        $tileIndex = $attrTile -band 0x07FF

        # Y=0 with link=0 on non-first entry means end of list
        if ($i -gt 0 -and $yPos -eq 0 -and $link -eq 0) { break }

        # Adjust Y (MD offsets Y by 128)
        $screenY = $yPos - 128
        $screenX = $xPos - 128

        $sprites += [ordered]@{
            index        = $i
            x            = $screenX
            y            = $screenY
            width_tiles  = $widthTiles
            height_tiles = $heightTiles
            tile_index   = $tileIndex
            palette      = $palette
            priority     = $priority
            h_flip       = $hFlip
            v_flip       = $vFlip
            link         = $link
        }

        # Track per-scanline counts
        $pixelHeight = $heightTiles * 8
        for ($sl = $screenY; $sl -lt ($screenY + $pixelHeight); $sl++) {
            if ($sl -ge 0 -and $sl -lt 224) {
                if (-not $scanlineCounts.ContainsKey($sl)) { $scanlineCounts[$sl] = 0 }
                $scanlineCounts[$sl]++
            }
        }

        if ($link -eq 0) { break }
    }

    $maxPerScanline = 0
    $hotspots = @()
    foreach ($sl in ($scanlineCounts.Keys | Sort-Object { $scanlineCounts[$_] } -Descending | Select-Object -First 5)) {
        $cnt = $scanlineCounts[$sl]
        if ($cnt -gt $maxPerScanline) { $maxPerScanline = $cnt }
        $hotspots += @{ scanline = $sl; sprite_count = $cnt }
    }

    return @{
        sprite_count           = $sprites.Count
        max_sprites_per_scanline = $maxPerScanline
        hotspot_scanlines      = $hotspots
        sprites                = $sprites
    }
}

# ---------------------------------------------------------------------------
# New-VdpInspectionArtifact
# ---------------------------------------------------------------------------
function New-VdpInspectionArtifact {
    <#
    .SYNOPSIS
        Assembles a complete VDP inspection artifact from component analyses.
    .PARAMETER SceneId
        Scene identifier.
    .PARAMETER PaletteData
        Output from Measure-VdpPaletteUsage.
    .PARAMETER TileData
        Output from Measure-VdpTileUsage.
    .PARAMETER SpriteData
        Output from Measure-VdpSpriteState.
    .OUTPUTS
        Hashtable ready for JSON serialization.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$SceneId,
        [hashtable]$PaletteData,
        [hashtable]$TileData,
        [hashtable]$SpriteData
    )

    $status = 'ok'
    $notes = @()

    if ($SpriteData -and $SpriteData.sprite_count -ge 80) {
        $status = 'error'; $notes += 'Sprite table full (80)'
    }
    if ($SpriteData -and $SpriteData.max_sprites_per_scanline -ge 20) {
        $status = 'error'; $notes += "Sprite overflow on scanline ($($SpriteData.max_sprites_per_scanline) sprites)"
    }
    if ($TileData -and $TileData.usage_fraction -ge 0.95) {
        if ($status -ne 'error') { $status = 'warn' }
        $notes += "VRAM tile usage at $([math]::Round($TileData.usage_fraction * 100, 1))%"
    }

    return [ordered]@{
        scene_id          = $SceneId
        palette_snapshots = $PaletteData
        tile_usage        = $TileData
        sprite_snapshot   = $SpriteData
        plane_usage       = [ordered]@{
            bg_a   = @{ nametable_address = $null; width_tiles = $null; height_tiles = $null; unique_tiles_used = $null }
            bg_b   = @{ nametable_address = $null; width_tiles = $null; height_tiles = $null; unique_tiles_used = $null }
            window = @{ nametable_address = $null; active = $null }
        }
        inspection_status = $status
        inspection_notes  = if ($notes.Count -gt 0) { $notes -join '; ' } else { $null }
    }
}

# ---------------------------------------------------------------------------
# Exports
# ---------------------------------------------------------------------------
Export-ModuleMember -Function @(
    'Import-VdpDump',
    'Measure-VdpPaletteUsage',
    'Measure-VdpTileUsage',
    'Measure-VdpSpriteState',
    'New-VdpInspectionArtifact'
)
