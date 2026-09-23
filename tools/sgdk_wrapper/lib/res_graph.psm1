<#
.SYNOPSIS
    Shared parser for SGDK .res resource declaration files.
.DESCRIPTION
    Provides Get-SgdkResDeclarations: a single canonical parser that returns
    normalized declarations from one or more .res files. Consumed by
    res_graph_audit.ps1, validate_audio.ps1, and validate_resources.ps1.

    Supported resource kinds: IMAGE, SPRITE, TILESET, MAP, TILEMAP, PALETTE,
    BIN, WAV, XGM, XGM2. Unknown/unrecognized lines are emitted as "unparsed".
.NOTES
    This module does NOT modify any existing wrapper behavior.
#>

Set-StrictMode -Version Latest

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

$script:KnownResourceKinds = @(
    'IMAGE', 'SPRITE', 'TILESET', 'MAP', 'TILEMAP', 'PALETTE',
    'BIN', 'WAV', 'XGM', 'XGM2'
)

$script:AudioKinds = @('WAV', 'XGM', 'XGM2')

$script:AudioBinExtensions = @('.raw', '.pcm', '.dpcm', '.bin')

$script:ImageKinds = @('IMAGE', 'SPRITE', 'TILESET', 'PALETTE')

$script:MapKinds = @('MAP', 'TILEMAP')

# Main pattern: TYPE NAME "path" [options...]  OR  TYPE NAME path [options...]
$script:ResLinePattern = '^\s*(?<kind>[A-Z_][A-Z0-9_]*)\s+(?<name>\w+)\s+(?:"(?<quoted>[^"]+)"|(?<bare>\S+))(?<rest>.*)?$'

# ---------------------------------------------------------------------------
# Resolve-ResReferencePath
# ---------------------------------------------------------------------------
function Resolve-ResReferencePath {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$BaseDir,
        [Parameter(Mandatory)][string]$DeclaredPath
    )

    if ([string]::IsNullOrWhiteSpace($DeclaredPath)) {
        return $null
    }
    if ([System.IO.Path]::IsPathRooted($DeclaredPath)) {
        return [System.IO.Path]::GetFullPath($DeclaredPath)
    }
    return [System.IO.Path]::GetFullPath((Join-Path $BaseDir $DeclaredPath))
}

# ---------------------------------------------------------------------------
# Get-ResourceClassification
# ---------------------------------------------------------------------------
function Get-ResourceClassification {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$Kind,
        [string]$DeclaredPath
    )

    if ($Kind -in $script:AudioKinds) {
        return 'audio'
    }
    if ($Kind -eq 'BIN') {
        $ext = [System.IO.Path]::GetExtension($DeclaredPath).ToLowerInvariant()
        if ($ext -in $script:AudioBinExtensions) {
            return 'audio'
        }
        return 'binary'
    }
    if ($Kind -in $script:ImageKinds) {
        return 'image'
    }
    if ($Kind -in $script:MapKinds) {
        return 'map'
    }
    if ($Kind -eq 'PALETTE') {
        return 'palette'
    }
    return 'unknown'
}

# ---------------------------------------------------------------------------
# Parse-OptionTokens
# ---------------------------------------------------------------------------
function Parse-OptionTokens {
    [CmdletBinding()]
    param(
        [string]$RestOfLine
    )

    $tokens = @()
    if ([string]::IsNullOrWhiteSpace($RestOfLine)) {
        return @{ tokens = $tokens; normalized = @{} }
    }

    $cleaned = $RestOfLine.Trim()
    # Strip inline comment
    $commentIdx = $cleaned.IndexOf('//')
    if ($commentIdx -ge 0) {
        $cleaned = $cleaned.Substring(0, $commentIdx).Trim()
    }

    if ([string]::IsNullOrWhiteSpace($cleaned)) {
        return @{ tokens = $tokens; normalized = @{} }
    }

    $tokens = @($cleaned -split '\s+' | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

    $normalized = [ordered]@{}
    # Common SGDK .res option positions:
    # WAV: name "path" driver [rate]
    # IMAGE/SPRITE: name "path" [COMPRESSION] [other flags]
    # BIN: name "path" [ALIGN] [COMPRESSION]
    if ($tokens.Count -ge 1) {
        $first = $tokens[0].ToUpperInvariant()
        # Known driver names for audio
        if ($first -in @('XGM2', 'XGM', 'PCM', 'PCM4', 'DPCM2')) {
            $normalized['driver'] = $first
            if ($tokens.Count -ge 2) {
                $rateCandidate = $tokens[1]
                $parsedRate = 0
                if ([int]::TryParse($rateCandidate, [ref]$parsedRate)) {
                    $normalized['rate'] = $parsedRate
                }
            }
        }
        # Known compression flags
        elseif ($first -in @('NONE', 'APLIB', 'LZ4W', 'BEST', 'AUTO')) {
            $normalized['compression'] = $first
        }
    }

    return @{ tokens = $tokens; normalized = $normalized }
}

# ---------------------------------------------------------------------------
# Get-SgdkResDeclarations (Main Export)
# ---------------------------------------------------------------------------
function Get-SgdkResDeclarations {
    <#
    .SYNOPSIS
        Parses one or more .res files and returns a normalized list of declarations.
    .PARAMETER ResFiles
        Array of FileInfo objects pointing to .res files.
    .PARAMETER ProjectRoot
        Absolute path to project root (for relative path display).
    .OUTPUTS
        Array of PSCustomObject with: resource_kind, resource_name, declared_path,
        resolved_path, res_file, res_line, exists, option_tokens, normalized_options,
        source_size_bytes, parser_status, classification.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]$ResFiles,
        [string]$ProjectRoot = ''
    )

    $declarations = [System.Collections.ArrayList]::new()

    foreach ($resFile in $ResFiles) {
        $resPath = $resFile.FullName
        $baseDir = Split-Path -Parent $resPath
        $content = Get-Content -LiteralPath $resPath -ErrorAction SilentlyContinue

        if ($null -eq $content) { continue }

        $lineNumber = 0
        foreach ($line in $content) {
            $lineNumber++
            $trimmed = $line.Trim()

            # Skip empty and comment lines
            if ([string]::IsNullOrWhiteSpace($trimmed) -or $trimmed.StartsWith('//')) {
                continue
            }

            if ($trimmed -notmatch $script:ResLinePattern) {
                # Non-empty, non-comment, non-matching line = unparsed
                [void]$declarations.Add([pscustomobject]@{
                    resource_kind     = 'UNPARSED'
                    resource_name     = $null
                    declared_path     = $null
                    resolved_path     = $null
                    res_file          = $resPath
                    res_line          = $lineNumber
                    exists            = $null
                    option_tokens     = @()
                    normalized_options = @{}
                    source_size_bytes = $null
                    parser_status     = 'unparsed'
                    classification    = 'unknown'
                    raw_line          = $trimmed
                })
                continue
            }

            $kind = $matches['kind'].ToUpperInvariant()
            $name = $matches['name']
            $declaredPath = if ($matches['quoted']) { $matches['quoted'] } else { $matches['bare'] }
            $rest = if ($matches['rest']) { $matches['rest'] } else { '' }

            $resolvedPath = Resolve-ResReferencePath -BaseDir $baseDir -DeclaredPath $declaredPath
            $fileExists = if ($resolvedPath) { Test-Path -LiteralPath $resolvedPath -PathType Leaf } else { $false }

            $sourceSize = $null
            if ($fileExists -and $resolvedPath) {
                try {
                    $sourceSize = (Get-Item -LiteralPath $resolvedPath).Length
                } catch {
                    $sourceSize = $null
                }
            }

            $parsedOptions = Parse-OptionTokens -RestOfLine $rest
            $classification = Get-ResourceClassification -Kind $kind -DeclaredPath $declaredPath

            $parserStatus = 'ok'
            if ($kind -notin $script:KnownResourceKinds) {
                $parserStatus = 'unknown_kind'
            }
            if (-not $fileExists) {
                $parserStatus = 'source_missing'
            }

            # For BIN audio: adjust resource_kind to BIN_AUDIO
            $effectiveKind = $kind
            if ($kind -eq 'BIN' -and $classification -eq 'audio') {
                $effectiveKind = 'BIN_AUDIO'
            }

            [void]$declarations.Add([pscustomobject]@{
                resource_kind      = $effectiveKind
                resource_name      = $name
                declared_path      = $declaredPath
                resolved_path      = $resolvedPath
                res_file           = $resPath
                res_line           = $lineNumber
                exists             = $fileExists
                option_tokens      = $parsedOptions.tokens
                normalized_options = $parsedOptions.normalized
                source_size_bytes  = $sourceSize
                parser_status      = $parserStatus
                classification     = $classification
                raw_line           = $null
            })
        }
    }

    return @($declarations.ToArray())
}

# ---------------------------------------------------------------------------
# Get-SgdkResFiles
# ---------------------------------------------------------------------------
function Get-SgdkResFiles {
    <#
    .SYNOPSIS
        Discovers .res files in a project, excluding build output directories.
    .PARAMETER ProjectRoot
        Absolute path to the project root.
    .PARAMETER ResPath
        Optional specific .res file paths to use instead of auto-discovery.
    .OUTPUTS
        Array of FileInfo objects.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$ProjectRoot,
        [string[]]$ResPath = @()
    )

    if ($ResPath.Count -gt 0) {
        $files = @()
        foreach ($p in $ResPath) {
            $resolved = if ([System.IO.Path]::IsPathRooted($p)) { $p } else { Join-Path $ProjectRoot $p }
            if (Test-Path -LiteralPath $resolved -PathType Leaf) {
                $files += Get-Item -LiteralPath $resolved
            }
        }
        return @($files)
    }

    $allRes = Get-ChildItem -LiteralPath $ProjectRoot -Filter '*.res' -Recurse -ErrorAction SilentlyContinue |
        Where-Object {
            $rel = $_.FullName.Substring($ProjectRoot.Length).TrimStart('\', '/')
            $rel -notmatch '^(out[\\/]|build[\\/]|\.)'
        }

    return @($allRes)
}

# ---------------------------------------------------------------------------
# Get-SgdkPngTileStats
# ---------------------------------------------------------------------------
function Get-SgdkPngTileStats {
    <#
    .SYNOPSIS
        Computes conservative 8x8 tile statistics for an indexed or RGB PNG.
    .DESCRIPTION
        Counts total 8x8 cells and unique 8x8 pixel patterns. This mirrors the
        practical VDP residency question better than source file size and catches
        BG_A/B + sprite reserve collisions that rescomp may compile successfully.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }
    if ([System.IO.Path]::GetExtension($Path).ToLowerInvariant() -ne '.png') {
        return $null
    }

    try {
        Add-Type -AssemblyName System.Drawing -ErrorAction Stop
    } catch {
        return [ordered]@{
            status = 'unavailable'
            reason = "System.Drawing unavailable: $($_.Exception.Message)"
        }
    }

    $bitmap = $null
    try {
        $bitmap = [System.Drawing.Bitmap]::new($Path)
        $width = [int]$bitmap.Width
        $height = [int]$bitmap.Height
        $tileColumns = [math]::Ceiling($width / 8.0)
        $tileRows = [math]::Ceiling($height / 8.0)
        $unique = [System.Collections.Generic.HashSet[string]]::new()

        for ($ty = 0; $ty -lt $tileRows; $ty++) {
            for ($tx = 0; $tx -lt $tileColumns; $tx++) {
                $sb = [System.Text.StringBuilder]::new()
                for ($py = 0; $py -lt 8; $py++) {
                    $y = ($ty * 8) + $py
                    for ($px = 0; $px -lt 8; $px++) {
                        $x = ($tx * 8) + $px
                        if ($x -lt $width -and $y -lt $height) {
                            $c = $bitmap.GetPixel($x, $y)
                            [void]$sb.AppendFormat('{0:X2}{1:X2}{2:X2}{3:X2}', $c.A, $c.R, $c.G, $c.B)
                        } else {
                            [void]$sb.Append('00000000')
                        }
                    }
                }
                [void]$unique.Add($sb.ToString())
            }
        }

        return [ordered]@{
            status = 'ok'
            width = $width
            height = $height
            tile_columns = [int]$tileColumns
            tile_rows = [int]$tileRows
            total_tiles = [int]($tileColumns * $tileRows)
            unique_tiles = [int]$unique.Count
        }
    } catch {
        return [ordered]@{
            status = 'error'
            reason = $_.Exception.Message
        }
    } finally {
        if ($bitmap) { $bitmap.Dispose() }
    }
}

# ---------------------------------------------------------------------------
# Get-SgdkSpriteEngineReservation
# ---------------------------------------------------------------------------
function Get-SgdkSpriteEngineReservation {
    <#
    .SYNOPSIS
        Detects the sprite engine VRAM reservation from SGDK source code.
    .DESCRIPTION
        SGDK 2.11 SPR_init() maps to the default sprite engine allocation. For
        fighting games with large actors, this reserve must be included in the
        same residency budget as BG tiles and the font region.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$ProjectRoot
    )

    $srcRoot = Join-Path $ProjectRoot 'src'
    if (-not (Test-Path -LiteralPath $srcRoot -PathType Container)) {
        return [ordered]@{
            tiles = 0
            method = 'no_src_detected'
            evidence = $null
        }
    }

    $files = @(Get-ChildItem -LiteralPath $srcRoot -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object { $_.Extension.ToLowerInvariant() -in @('.c', '.h') })
    foreach ($file in $files) {
        $content = Get-Content -LiteralPath $file.FullName -Raw -ErrorAction SilentlyContinue
        if (-not $content) { continue }
        $match = [regex]::Match($content, 'SPR_initEx\s*\(\s*(?<tiles>\d+)\s*\)')
        if ($match.Success) {
            return [ordered]@{
                tiles = [int]$match.Groups['tiles'].Value
                method = 'SPR_initEx'
                evidence = $file.FullName
            }
        }
    }

    foreach ($file in $files) {
        $content = Get-Content -LiteralPath $file.FullName -Raw -ErrorAction SilentlyContinue
        if (-not $content) { continue }
        if ($content -match 'SPR_init\s*\(') {
            return [ordered]@{
                tiles = 420
                method = 'SPR_init_default_sgdk_211'
                evidence = $file.FullName
            }
        }
    }

    return [ordered]@{
        tiles = 0
        method = 'not_detected'
        evidence = $null
    }
}

# ---------------------------------------------------------------------------
# Get-SgdkCodeLoadedTileFootprint
# ---------------------------------------------------------------------------
function Get-SgdkCodeLoadedTileFootprint {
    <#
    .SYNOPSIS
        Estimates tiles loaded directly by SGDK C code outside .res files.
    .DESCRIPTION
        Detects common hardcoded/procedural tile paths such as VDP_loadTileData,
        static tile arrays and nametable drawing helpers. TILE_USER_INDEX is
        recorded as context, but by itself is only a normal SGDK resource base
        index reference for IMAGE/TILESET draws.
        This is intentionally conservative: it marks the footprint as estimated
        so a no-.res project cannot claim validated VDP budget from absence of
        declarations.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$ProjectRoot
    )

    $srcRoot = Join-Path $ProjectRoot 'src'
    $detections = [System.Collections.ArrayList]::new()
    $tileLoads = [System.Collections.ArrayList]::new()
    $tileArrayEstimates = [System.Collections.ArrayList]::new()

    if (-not (Test-Path -LiteralPath $srcRoot -PathType Container)) {
        return [ordered]@{
            status = 'not_detected'
            measurement_level = 'not_measured'
            method = 'no_src_detected'
            tile_load_calls = @()
            tile_array_estimates = @()
            estimated_tiles = 0
            uses_tile_user_index = $false
            nametable_draw_calls = 0
            files_scanned = 0
        }
    }

    $files = @(Get-ChildItem -LiteralPath $srcRoot -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object { $_.Extension.ToLowerInvariant() -in @('.c', '.h') })

    foreach ($file in $files) {
        $content = Get-Content -LiteralPath $file.FullName -Raw -ErrorAction SilentlyContinue
        if (-not $content) { continue }

        if ($content -match '\bTILE_USER_INDEX\b') {
            [void]$detections.Add([ordered]@{
                file = $file.FullName
                kind = 'TILE_USER_INDEX'
                evidence = 'TILE_USER_INDEX'
            })
        }

        foreach ($match in [regex]::Matches($content, 'VDP_loadTileData\s*\((?<args>[^;]+?)\)\s*;', 'Singleline')) {
            $argsText = $match.Groups['args'].Value
            $args = @($argsText -split ',' | ForEach-Object { $_.Trim() })
            $tiles = $null
            if ($args.Count -ge 3) {
                $tilesText = $args[2]
                $parsedTiles = 0
                if ([int]::TryParse($tilesText, [ref]$parsedTiles)) {
                    $tiles = $parsedTiles
                }
            }
            [void]$tileLoads.Add([ordered]@{
                file = $file.FullName
                call = ($match.Value -replace '\s+', ' ').Trim()
                estimated_tiles = $tiles
                measurement_level = if ($null -ne $tiles) { 'estimated' } else { 'declared_unknown' }
            })
        }

        foreach ($match in [regex]::Matches($content, '(?:static\s+)?(?:const\s+)?(?:u32|u16|u8)\s+(?<name>[A-Za-z_][A-Za-z0-9_]*)\s*\[\s*(?<tiles>\d+)\s*\]\s*\[\s*8\s*\]', 'IgnoreCase')) {
            [void]$tileArrayEstimates.Add([ordered]@{
                file = $file.FullName
                symbol = $match.Groups['name'].Value
                estimated_tiles = [int]$match.Groups['tiles'].Value
                pattern = 'tile_array_rows_x_8_words'
            })
        }

        foreach ($match in [regex]::Matches($content, '\bVDP_(?:fillTileMapRect|setTileMapXY|setTileMapEx|setTileMapData)\s*\(', 'IgnoreCase')) {
            [void]$detections.Add([ordered]@{
                file = $file.FullName
                kind = 'NAMETABLE_DRAW'
                evidence = $match.Value.Trim()
            })
        }
    }

    $loadedTileSum = 0
    foreach ($entry in $tileLoads) {
        if ($null -ne $entry.estimated_tiles) {
            $loadedTileSum += [int]$entry.estimated_tiles
        }
    }
    $arrayTileSum = 0
    foreach ($entry in $tileArrayEstimates) {
        $arrayTileSum += [int]$entry.estimated_tiles
    }
    $estimatedTiles = [math]::Max($loadedTileSum, $arrayTileSum)
    $nametableDrawCalls = @($detections | Where-Object { $_.kind -eq 'NAMETABLE_DRAW' }).Count
    $usesTileUserIndex = @($detections | Where-Object { $_.kind -eq 'TILE_USER_INDEX' }).Count -gt 0
    $hasCodeLoadedTiles = ($tileLoads.Count -gt 0) -or ($tileArrayEstimates.Count -gt 0) -or ($nametableDrawCalls -gt 0)

    return [ordered]@{
        status = if ($hasCodeLoadedTiles) { 'code_loaded_tiles_unmeasured' } else { 'not_detected' }
        measurement_level = if ($hasCodeLoadedTiles) { 'estimated' } else { 'not_measured' }
        method = 'static_code_scan'
        tile_load_calls = @($tileLoads.ToArray())
        tile_array_estimates = @($tileArrayEstimates.ToArray())
        estimated_tiles = [int]$estimatedTiles
        uses_tile_user_index = [bool]$usesTileUserIndex
        nametable_draw_calls = [int]$nametableDrawCalls
        files_scanned = [int]$files.Count
        detections = @($detections.ToArray())
    }
}

# ---------------------------------------------------------------------------
# Exports
# ---------------------------------------------------------------------------
Export-ModuleMember -Function @(
    'Get-SgdkResDeclarations',
    'Get-SgdkResFiles',
    'Resolve-ResReferencePath',
    'Get-SgdkPngTileStats',
    'Get-SgdkSpriteEngineReservation',
    'Get-SgdkCodeLoadedTileFootprint'
)
