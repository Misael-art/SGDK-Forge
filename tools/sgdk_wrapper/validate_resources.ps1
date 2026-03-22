[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$WorkDir = "",
    [Parameter(Mandatory = $false)]
    [switch]$Fix
)

try {
    if (-not [string]::IsNullOrWhiteSpace($WorkDir)) {
        Set-Location -LiteralPath $WorkDir
    }
} catch {
    Write-Error ("[ERROR] validate_resources.ps1: failed to Set-Location to '{0}'. Details: {1}" -f $WorkDir, $_.Exception.Message)
    exit 1
}

$LOG_DIR = if ($env:SGDK_LOG_DIR) { $env:SGDK_LOG_DIR } else { Join-Path $pwd.Path "out\logs" }
$DEBUG_LOG = if ($env:SGDK_DEBUG_LOG) { $env:SGDK_DEBUG_LOG } else { Join-Path $LOG_DIR "build_debug.log" }
$MAX_SPRITE_SIZE_TILES = 32
$MAX_INTERNAL_SPRITES = 16
$REPORT_FILE = if ($env:SGDK_VALIDATION_REPORT) { $env:SGDK_VALIDATION_REPORT } else { Join-Path $LOG_DIR "validation_report.json" }

function Write-Log($msg, $level = "INFO") {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $fullMsg = "[$timestamp] [$level] $msg"
    Write-Host $fullMsg
    if (-not (Test-Path -LiteralPath $LOG_DIR)) {
        New-Item -ItemType Directory -Force -Path $LOG_DIR | Out-Null
    }
    Add-Content -LiteralPath $DEBUG_LOG $fullMsg
}

function Find-RecoveredPath($relPath, $baseDir) {
    $fileName = Split-Path $relPath -Leaf
    $searchDirs = @("sprite", "sprites", "gfx", "bg", "bgs", "sound", "sfx", "music")
    foreach ($parent in @("sprite", "sprites", "gfx", "bg", "bgs")) {
        $parentPath = Join-Path $baseDir $parent
        if (Test-Path -LiteralPath $parentPath) {
            Get-ChildItem -LiteralPath $parentPath -Directory -ErrorAction SilentlyContinue | ForEach-Object {
                $searchDirs += "$parent/$($_.Name)"
            }
        }
    }
    foreach ($dir in $searchDirs | Select-Object -Unique) {
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

function Get-MagickPath() {
    $magickPath = Get-Command magick -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source
    if (-not $magickPath) {
        $commonPaths = Get-ChildItem -Path "C:\Program Files\ImageMagick*" -Filter "magick.exe" -Recurse -ErrorAction SilentlyContinue |
            Select-Object -ExpandProperty FullName
        if ($commonPaths.Count -gt 0) { $magickPath = $commonPaths[0] }
    }
    return $magickPath
}

function Get-ImageInfo($magickPath, $filePath) {
    $identify = & $magickPath identify -format "%w|%h|%z|%k|%r" "$filePath"
    if ($identify -match '^(\d+)\|(\d+)\|(\d+)\|(\d+)\|(.+)$') {
        return [pscustomobject]@{
            Width = [int]$matches[1]
            Height = [int]$matches[2]
            Depth = [int]$matches[3]
            Colors = [int]$matches[4]
            Class = $matches[5]
            Indexed = ($matches[5] -match '^PseudoClass')
        }
    }
    throw "Unable to parse ImageMagick identify output: $identify"
}

function Add-Detail($results, $type, $level, $message, $resource, $file, $extra = @{}) {
    $detail = @{
        type = $type
        level = $level
        message = $message
        resource = $resource
        file = $file
    }
    foreach ($key in $extra.Keys) {
        $detail[$key] = $extra[$key]
    }
    $results.details += $detail
}

function Invoke-AutoFix($fixScript, $filePath, $assetKind) {
    if (-not (Test-Path -LiteralPath $fixScript)) {
        return $false
    }
    & $fixScript -File $filePath -AssetKind $assetKind
    return ($LASTEXITCODE -eq 0)
}

Write-Log "--- Starting Resource Validation Suite ---"
$results = @{
    timestamp = Get-Date -Format "o"
    summary = @{ errors = 0; warnings = 0; checked = 0; recovered = 0 }
    details = @()
}

$magickPath = Get-MagickPath
$fixScript = Join-Path $PSScriptRoot "ensure_safe_image.ps1"

$resFiles = Get-ChildItem -LiteralPath (Join-Path $pwd.Path "res") -Filter "*.res" -Recurse -ErrorAction SilentlyContinue
if (-not $resFiles) {
    Write-Log "Nenhum arquivo .res encontrado em res/ (projeto pode não ter recursos)." "INFO"
} else {
    Write-Log "Encontrados $($resFiles.Count) arquivo(s) .res para validar." "INFO"
}

foreach ($res in $resFiles) {
    Write-Log "Validando $($res.FullName)..."
    $content = Get-Content -LiteralPath $res.FullName
    $baseDir = Split-Path $res.FullName
    $resourceNames = @{}
    $lineNumber = 0

    foreach ($line in $content) {
        $lineNumber++
        if ($line -match '^\s*//') { continue }
        if ($line -match '^\s*(SPRITE|IMAGE)\s+(\w+)') {
            $resourceName = $matches[2]
            if ($resourceNames.ContainsKey($resourceName)) {
                $firstLine = $resourceNames[$resourceName]
                $msg = "Definição duplicada: recurso '$resourceName' definido na linha $firstLine e novamente na linha $lineNumber."
                Write-Log $msg "ERROR"
                $results.summary.errors++
                Add-Detail $results "DUPLICATE_RESOURCE" "ERROR" $msg $resourceName $res.FullName @{ firstLine = $firstLine; duplicateLine = $lineNumber }
            } else {
                $resourceNames[$resourceName] = $lineNumber
            }
        }
    }

    foreach ($line in $content) {
        if ($line -match '^\s*//') { continue }

        $kind = $null
        $name = $null
        $path = $null
        $w = $null
        $h = $null
        $hasOptType = $false

        if ($line -match '^\s*SPRITE\s+(\w+)\s+"([^"]+)"\s+(\d+)\s+(\d+)') {
            $kind = "SPRITE"
            $name = $matches[1]
            $path = $matches[2]
            $w = [int]$matches[3]
            $h = [int]$matches[4]
            $hasOptType = $line -match 'NONE\s+1\s+1\s*$'
        } elseif ($line -match '^\s*IMAGE\s+(\w+)\s+"([^"]+)"') {
            $kind = "IMAGE"
            $name = $matches[1]
            $path = $matches[2]
        } else {
            continue
        }

        $results.summary.checked++
        $absPath = Join-Path $baseDir $path

        if (-not (Test-Path -LiteralPath $absPath)) {
            $recovered = Find-RecoveredPath $path $baseDir
            if ($recovered) {
                $newRelPath = (Resolve-Path -LiteralPath $recovered -Relative).Replace(".\", "").Replace("\", "/")
                $msg = "Arquivo recuperado: $name ($path -> $newRelPath)"
                Write-Log $msg "WARN"
                $results.summary.recovered++
                Add-Detail $results "PATH_RECOVERY" "WARN" $msg $name $path @{ newPath = $newRelPath }
                $absPath = $recovered
            } else {
                $msg = "Arquivo ausente: $path (referenciado por $name)"
                Write-Log $msg "ERROR"
                $results.summary.errors++
                Add-Detail $results "MISSING_FILE" "ERROR" $msg $name $path
                continue
            }
        }

        if ($kind -eq "SPRITE") {
            $estSprites = Estimate-VDPSprites $w $h
            if ($estSprites -gt $MAX_INTERNAL_SPRITES -and -not $hasOptType) {
                $suggestion = "Adicione 'NONE 1 1' ao final da linha ou reduza o tamanho do frame."
                $msg = "Sprite $name ($w x $h tiles) usa ~$estSprites sprites internos, excedendo o limite SGDK ($MAX_INTERNAL_SPRITES). $suggestion"
                Write-Log $msg "ERROR"
                $results.summary.errors++
                Add-Detail $results "VDP_SPRITE_LIMIT" "ERROR" $msg $name $path @{ estimated = $estSprites; suggestion = $suggestion }
            }
            if ($w -gt $MAX_SPRITE_SIZE_TILES -or $h -gt $MAX_SPRITE_SIZE_TILES) {
                $msg = "Sprite $name tem dimensões ($w, $h) excedendo o limite SGDK (32x32 tiles)."
                Write-Log $msg "ERROR"
                $results.summary.errors++
                Add-Detail $results "SPRITE_LIMIT" "ERROR" $msg $name $path
            }
        }

        if (-not $magickPath) {
            Write-Log "ImageMagick não encontrado; validação de imagem será parcial." "WARN"
            $results.summary.warnings++
            continue
        }

        try {
            $info = Get-ImageInfo $magickPath $absPath
        } catch {
            $msg = "Falha ao inspecionar ${path}: $($_.Exception.Message)"
            Write-Log $msg "ERROR"
            $results.summary.errors++
            Add-Detail $results "IDENTIFY_FAILED" "ERROR" $msg $name $path
            continue
        }

        if (($info.Width % 8) -ne 0 -or ($info.Height % 8) -ne 0) {
            $msg = "Imagem $path tem dimensões ($($info.Width) x $($info.Height)) que não são múltiplas de 8."
            Write-Log $msg "WARN"
            $results.summary.warnings++
            Add-Detail $results "ALIGNMENT" "WARNING" $msg $name $path
        }

        $invalidReasons = @()
        if (-not $info.Indexed) { $invalidReasons += "imagem não indexada" }
        if ($info.Depth -gt 8) { $invalidReasons += "depth $($info.Depth) bits" }
        if ($info.Colors -gt 16) { $invalidReasons += "$($info.Colors) cores" }

        if ($invalidReasons.Count -gt 0) {
            $msg = "Imagem $path é incompatível com SGDK ($($invalidReasons -join ', ')). Requer <=16 cores indexadas (PseudoClass) em 4bpp/8bpp."
            Write-Log $msg "ERROR"
            $results.summary.errors++
            Add-Detail $results "IMAGE_FORMAT" "ERROR" $msg $name $path @{
                depth = $info.Depth
                colors = $info.Colors
                imageClass = $info.Class
                resourceKind = $kind
            }

            if ($Fix) {
                Write-Log "Tentando fix automático para $name..." "INFO"
                if (Invoke-AutoFix $fixScript $absPath $kind) {
                    $fixed = $null
                    try {
                        $fixed = Get-ImageInfo $magickPath $absPath
                    } catch {
                        $fixed = $null
                    }

                    if ($fixed -and $fixed.Indexed -and $fixed.Depth -le 8 -and $fixed.Colors -le 16) {
                        Write-Log "Fix aplicado com sucesso para $name." "OK"
                        $results.summary.errors--
                        $results.summary.recovered++
                    } else {
                        $revalidationMsg = "Fix automático não deixou $name em conformidade; revalidação falhou."
                        Write-Log $revalidationMsg "ERROR"
                        Add-Detail $results "FIX_REVALIDATION_FAILED" "ERROR" $revalidationMsg $name $path
                    }
                } else {
                    $fixMsg = "Fix automático falhou para $name."
                    Write-Log $fixMsg "ERROR"
                    Add-Detail $results "FIX_FAILED" "ERROR" $fixMsg $name $path
                }
            }
        }
    }
}

$romPath = Join-Path $pwd.Path "out/rom.bin"
if (Test-Path -LiteralPath $romPath) {
    $size = (Get-Item -LiteralPath $romPath).Length
    if ($size -gt 4MB) {
        $msg = "ROM size ($([math]::Round($size / 1MB, 2)) MB) exceeds Mega Drive limit (4MB)."
        Write-Log $msg "ERROR"
        $results.summary.errors++
        Add-Detail $results "ROM_SIZE" "ERROR" $msg "rom" $romPath
    }
}

$results | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $REPORT_FILE
Write-Log "Validation finished. Errors: $($results.summary.errors), Warnings: $($results.summary.warnings), Checked: $($results.summary.checked), Recovered: $($results.summary.recovered)"

if ($results.summary.errors -gt 0) { exit 1 }
exit 0
