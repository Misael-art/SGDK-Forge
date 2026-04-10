param(
    [string]$resFile,
    [string]$sourceResFile
)

# ==============================================================================
# autofix_sprite_res.ps1
# Corrige sprite.res: dimensões, paths, duplicatas, limite VDP (16 sprites internos).
# Usado na migração SGDK 160 -> 211 e no build resiliente.
# ==============================================================================

# Global configuration
$LOG_DIR = if ($env:SGDK_LOG_DIR) { $env:SGDK_LOG_DIR } else { Join-Path $pwd.Path "out\logs" }
$DEBUG_LOG = if ($env:SGDK_DEBUG_LOG) { $env:SGDK_DEBUG_LOG } else { Join-Path $LOG_DIR "build_debug.log" }
$MAX_SPRITE_SIZE_TILES = 32
$MAX_INTERNAL_SPRITES = 16

# Busca generica de path: tenta localizar arquivo em subdiretorios de res/
# Nao depende de mapeamento hardcoded — descobre estrutura automaticamente.
function Find-SpriteInSubdirs($fileName, $baseDir) {
    # Busca em sprite/, gfx/ e seus subdiretorios
    foreach ($parent in @("sprite", "sprites", "gfx")) {
        $parentPath = Join-Path $baseDir $parent
        if (Test-Path -LiteralPath $parentPath) {
            # Verifica o diretorio pai
            $tryPath = Join-Path $parentPath $fileName
            if (Test-Path -LiteralPath $tryPath) { return "$parent/$fileName" }
            # Verifica subdiretorios
            Get-ChildItem -LiteralPath $parentPath -Directory -ErrorAction SilentlyContinue | ForEach-Object {
                $tryPath = Join-Path $_.FullName $fileName
                if (Test-Path -LiteralPath $tryPath) { return "$parent/$($_.Name)/$fileName" }
            }
        }
    }
    return $null
}

function Write-Log($msg) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $fullMsg = "[$timestamp] $msg"
    Write-Host $fullMsg
    if (-not (Test-Path -LiteralPath $LOG_DIR)) {
        New-Item -ItemType Directory -Force -Path $LOG_DIR | Out-Null
    }
    Add-Content -LiteralPath $DEBUG_LOG $fullMsg
}

function Find-RecoveredPath($relPath, $baseDir) {
    $fileName = Split-Path $relPath -Leaf
    # Busca dinamica em subdiretorios comuns + subdirs reais de sprite/ e gfx/
    $searchDirs = @("sprite", "sprites", "gfx", "bg", "bgs", "sound", "sfx")
    foreach ($parent in @("sprite", "sprites", "gfx", "bg", "bgs")) {
        $parentPath = Join-Path $baseDir $parent
        if (Test-Path -LiteralPath $parentPath) {
            Get-ChildItem -LiteralPath $parentPath -Directory -ErrorAction SilentlyContinue | ForEach-Object {
                $searchDirs += "$parent/$($_.Name)"
            }
        }
    }
    foreach ($dir in $searchDirs) {
        $tryPath = Join-Path $baseDir (Join-Path $dir $fileName)
        if (Test-Path -LiteralPath $tryPath) {
            return $tryPath
        }
    }
    return $null
}

function Estimate-VDPSprites($wTiles, $hTiles) {
    $count = 0
    $remW = $wTiles
    while ($remW -gt 0) {
        $stepW = if ($remW -ge 4) { 4 } else { $remW }
        $remH = $hTiles
        while ($remH -gt 0) {
            $stepH = if ($remH -ge 4) { 4 } else { $remH }
            $count++
            $remH -= $stepH
        }
        $remW -= $stepW
    }
    return $count
}

if (-not $resFile) {
    $resFile = Join-Path $pwd.Path "res/sprite.res"
}

if (-not (Test-Path -LiteralPath $resFile)) {
    Write-Log "[ERROR] Resource file not found: $resFile"
    return
}

# 0. Load Source Resource for Recovery
$sourceMap = @{}
if ($sourceResFile -and (Test-Path -LiteralPath $sourceResFile)) {
    Write-Log "[INFO] Using source resource for recovery: $sourceResFile"
    $sourceContent = Get-Content -LiteralPath $sourceResFile
    foreach ($line in $sourceContent) {
        if ($line -match '^SPRITE\s+(\w+)\s+"([^"]+)"\s+(\d+)\s+(\d+)\s+(\w+)\s+(\d+)') {
            $sourceMap[$matches[1]] = @{
                path = $matches[2]
                w = [int]$matches[3]
                h = [int]$matches[4]
                flags = $matches[5]
                anim = $matches[6]
            }
        }
    }
}

# Locate ImageMagick
$magickPath = Get-Command magick -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source
if (-not $magickPath) {
    $commonPaths = Get-ChildItem -Path "C:\Program Files\ImageMagick*" -Filter "magick.exe" -Recurse -ErrorAction SilentlyContinue | 
                   Select-Object -ExpandProperty FullName
    if ($commonPaths.Count -gt 0) { $magickPath = $commonPaths[0] }
}

Write-Log "--- Starting Resilient Sprite Fixer for $resFile ---"

$content = Get-Content -LiteralPath $resFile
$newContent = @()
$fixCount = 0
$baseDir = Split-Path $resFile
$seenSprites = @{}  # Remoção de duplicatas: manter apenas primeira ocorrência

foreach ($line in $content) {
    # 0. Uncomment potentially needed sprites
    if ($line -match '^\/\/\s*SPRITE\s+(\w+)\s+"([^"]+)"\s+(\d+)\s+(\d+)\s+(\w+)\s+(\d+)') {
        $potentialName = $matches[1]
        Write-Log "[INFO] Uncommenting sprite definition for $potentialName"
        $line = $line -replace '^\/\/\s*', ''
        $fixCount++
    }

    if ($line -match '^SPRITE\s+(\w+)\s+"([^"]*)"\s+(\d+)\s+(\d+)\s+(\w+)\s+(\d+)') {
        $name = $matches[1]
        
        # 0.0 Remoção de duplicatas: manter apenas a primeira definição de cada sprite
        if ($seenSprites.ContainsKey($name)) {
            Write-Log "[FIX] Removendo definição duplicada de $name (mantida primeira ocorrência)"
            $fixCount++
            continue
        }
        $seenSprites[$name] = $true
        
        $path = $matches[2]
        $w = [int]$matches[3]
        $h = [int]$matches[4]
        $flags = $matches[5]
        $anim = [int]$matches[6]

        # 0.1 Clean up any leading "res/" in current path (ResComp requirement)
        if ($path -match '^res[/\\]') {
            $oldPath = $path
            $path = $path -replace '^res[/\\]', ''
            Write-Log "[FIX] Removing 'res/' prefix from $($name) path: $oldPath -> $path"
            $fixCount++
        }

        # 0.2 Resilience: If path is empty or a directory, treat as missing
        $absPath = Join-Path $baseDir $path
        $baseDirObj = Get-Item -LiteralPath $baseDir
        $isMissing = $false
        if (-not $path -or $path -eq "" -or -not (Test-Path -LiteralPath $absPath) -or (Test-Path -LiteralPath $absPath -PathType Container)) {
            $isMissing = $true
        }

        # 0.3 Busca generica de path (se arquivo esta ausente no path declarado)
        if ($isMissing) {
            $fileName = Split-Path $path -Leaf
            $foundPath = Find-SpriteInSubdirs $fileName $baseDir
            if ($foundPath) {
                $correctAbsPath = Join-Path $baseDir $foundPath
                Write-Log "[FIX] Arquivo encontrado em local alternativo para $name : $path -> $foundPath"
                $path = $foundPath
                $absPath = $correctAbsPath
                $isMissing = $false
                $fixCount++
            }
        }

        # 1. Source Recovery (if current is missing, suspicious, or generic fallback)
        if ($sourceMap.ContainsKey($name)) {
            $src = $sourceMap[$name]
            $isRecoverable = $false
            
            # Case A: Path is missing
            if ($isMissing) { $isRecoverable = $true }
            
            # Case B: Current dimensions exceed VDP limit
            $estSprites = Estimate-VDPSprites $w $h
            if ($estSprites -gt $MAX_INTERNAL_SPRITES) { $isRecoverable = $true }
            
            # Case C: Current dimensions are the generic fallback (4x4) but source is different
            if ($w -eq 4 -and $h -eq 4 -and ($src.w -ne 4 -or $src.h -ne 4)) { $isRecoverable = $true }

            # Case D: Dimensions are different from source (more aggressive recovery)
            # Migration often corrupts dimensions, so if they differ, the source is likely correct.
            # Recuperamos mesmo se source exceder 16 sprites; opt_type=1 sera adicionado na saida.
            if ($w -ne $src.w -or $h -ne $src.h) {
                $isRecoverable = $true
            }

            if ($isRecoverable) {
                # Clean up source path (remove res/ prefix if present as rescomp is relative to .res file)
                $cleanSrcPath = $src.path -replace '^res[/\\]', ''
                $srcAbsPath = Join-Path $baseDir $cleanSrcPath

                # Recover path if missing or different in source (but only if source path exists)
                if ($isMissing -or ($path -ne $cleanSrcPath)) {
                    if (Test-Path -LiteralPath $srcAbsPath -PathType Leaf) {
                        Write-Log "[FIX] Recovering path from source for $($name): $($path) -> $($cleanSrcPath)"
                        $path = $cleanSrcPath
                        $absPath = $srcAbsPath
                        $isMissing = $false # No longer missing
                        $fixCount++
                    }
                }
                
                # Recover dimensions if source is valid
                if ($src.w -ne $w -or $src.h -ne $h) {
                    Write-Log "[FIX] Recovering dimensions from source for $($name): $w $h -> $($src.w) $($src.h)"
                    $w = $src.w
                    $h = $src.h
                    $fixCount++
                }
            }
        }

        # 2. Path Recovery (Generic Search)
        if ($isMissing) {
            $recovered = Find-RecoveredPath $path $baseDir
            if ($recovered) {
                # Get path relative to baseDir (robustly)
                $relPath = $recovered.Replace($baseDirObj.FullName, "").TrimStart("\").TrimStart("/")
                if ($relPath -and $relPath -ne "") {
                    Write-Log "[FIX] Recovered path for $($name): $($path) -> $($relPath)"
                    $path = $relPath.Replace("\", "/")
                    $absPath = $recovered
                    $isMissing = $false
                    $fixCount++
                }
            }
        }

        # 2.1 Fallback to dummy if still missing (Resilience against missing assets)
        if ($isMissing) {
            $dummyPath = "sprite/spr_point.png"
            $absDummy = Join-Path $baseDir $dummyPath
            if (Test-Path -LiteralPath $absDummy) {
                Write-Log "[WARN] Resource $($name) missing ($path). Falling back to dummy: $dummyPath"
                $path = $dummyPath
                $absPath = $absDummy
                $w = 1; $h = 1; # Dummy is 1x1
                $isMissing = $false
                $fixCount++
            } else {
                # If even dummy is missing, we must comment it out as a last resort
                Write-Log "[ERROR] Resource $($name) missing and no dummy available. Commenting out."
                $line = "// SPRITE $name ""$path"" $w $h $flags $anim"
                $newContent += $line
                continue
            }
        }

        # 2.2 Final Path Cleanup: Ensure no "res/" prefix and no empty paths
        $path = $path -replace '^res[/\\]', ''
        if (-not $path -or $path -eq "" -or $path -eq '""' -or $path -eq "sprite/") {
            $path = "sprite/spr_point.png" # Emergency fallback for empty paths
            $absPath = Join-Path $baseDir $path
        }
        if (Test-Path -LiteralPath $absPath -PathType Leaf) {
            try {
                if ($magickPath) {
                    $dims = & $magickPath identify -format "%w %h" $absPath
                    if ($dims -match '(\d+)\s+(\d+)') {
                        $actualW = [int]$matches[1]
                        $actualH = [int]$matches[2]
                        
                        $imgW_tiles = [math]::Ceiling($actualW / 8)
                        $imgH_tiles = [math]::Ceiling($actualH / 8)
                        
                        # Fix A: If current dimensions are larger than image, they are definitely wrong
                        if ($w -gt $imgW_tiles -or $h -gt $imgH_tiles) {
                            Write-Log "[FIX] Capping $name dimensions to image size: $w $h -> $imgW_tiles $imgH_tiles"
                            $w = $imgW_tiles
                            $h = $imgH_tiles
                            $fixCount++
                        }

                        # Fix B: Check "multiple of cell width" (SGDK requirement)
                        # image_width must be multiple of (frame_width_tiles * 8)
                        if (($actualW % ($w * 8)) -ne 0) {
                            Write-Log "[WARN] $name width ($actualW) is not a multiple of cell width ($($w * 8)). Searching valid divisor..."
                            # Find the largest divisor of imgW_tiles that is <= current w
                            $found = $false
                            for ($tw = $w; $tw -ge 1; $tw--) {
                                if (($actualW % ($tw * 8)) -eq 0) {
                                    Write-Log "[FIX] Adjusting $name width: $w -> $tw"
                                    $w = $tw
                                    $found = $true
                                    $fixCount++
                                    break
                                }
                            }
                        }

                        if (($actualH % ($h * 8)) -ne 0) {
                            Write-Log "[WARN] $name height ($actualH) is not a multiple of cell height ($($h * 8)). Searching valid divisor..."
                            for ($th = $h; $th -ge 1; $th--) {
                                if (($actualH % ($th * 8)) -eq 0) {
                                    Write-Log "[FIX] Adjusting $name height: $h -> $th"
                                    $h = $th
                                    $fixCount++
                                    break
                                }
                            }
                        }

                        # Fix C: VDP Internal Sprite Limit - usar opt_type=1 (SPRITE) em vez de reduzir dimensões
                        # opt_type=1 prioriza menos sprites de hardware (rescomp usa blocos maiores)
                        $estSprites = Estimate-VDPSprites $w $h
                        if ($estSprites -gt $MAX_INTERNAL_SPRITES) {
                            Write-Log "[FIX] $name excede limite VDP (~$estSprites sprites). Adicionando opt_type=SPRITE (NONE 1 1)."
                            $fixCount++
                        }

                        # Final Hardware limit check
                        if ($w -gt $MAX_SPRITE_SIZE_TILES) { $w = 8; $fixCount++ }
                        if ($h -gt $MAX_SPRITE_SIZE_TILES) { $h = 8; $fixCount++ }
                    }
                }
            } catch {
                Write-Log "[ERROR] Failed to identify dimensions for $($path): $($_.Exception.Message)"
            }
        }
        
        # Output: adicionar opt_type=1 opt_level=1 quando exceder limite de 16 sprites internos
        $estSprites = Estimate-VDPSprites $w $h
        $optSuffix = ""
        if ($estSprites -gt $MAX_INTERNAL_SPRITES) {
            $optSuffix = " NONE 1 1"  # collision=NONE, opt_type=SPRITE, opt_level=MEDIUM
        }
        $line = "SPRITE $name ""$path"" $w $h $flags $anim$optSuffix"
    }
    $newContent += $line
}

# 4. Final Verification: Ensure no SPRITE "" remains
 $finalContent = @()
 foreach ($l in $newContent) {
     if ($l -match '^SPRITE\s+(\w+)\s+"(sprite/|)"\s+(\d+)\s+(\d+)\s+(\w+)\s+(\d+)') {
         $n = $matches[1]
         $tw = $matches[2] # Not needed
         $tw = $matches[3]
         $th = $matches[4]
         $tf = $matches[5]
         $ta = $matches[6]
         Write-Log "[ERROR] Final verification found invalid path for $n. Forcing spr_point."
         $l = "SPRITE $n ""sprite/spr_point.png"" 1 1 $tf $ta"
     }
     $finalContent += $l
 }

if ($fixCount -gt 0) {
    $finalContent | Set-Content -LiteralPath $resFile
    Write-Log "[OK] Applied $fixCount fixes to $resFile"
} else {
    Write-Log "No fixes needed for $resFile"
}

Write-Log "--- Resilient Sprite Fixer Finished ---"
