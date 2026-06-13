param(
    [Parameter(Mandatory = $true)]
    [string]$File,
    [Parameter(Mandatory = $false)]
    [switch]$Force,
    [Parameter(Mandatory = $false)]
    [ValidateSet("Auto", "SPRITE", "IMAGE")]
    [string]$AssetKind = "Auto"
)

$LOG_DIR = if ($env:SGDK_LOG_DIR) { $env:SGDK_LOG_DIR } else { Join-Path $pwd.Path "out\logs" }
$DEBUG_LOG = if ($env:SGDK_DEBUG_LOG) { $env:SGDK_DEBUG_LOG } else { Join-Path $LOG_DIR "build_debug.log" }
$PREP_REPORT = Join-Path $LOG_DIR "asset_preparation_report.json"

. (Join-Path $PSScriptRoot "_lib\sgdk_common.ps1")

function Write-Log($msg, $level = "INFO") {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] [$level] $msg"
    if (-not (Test-Path -LiteralPath $LOG_DIR)) {
        New-Item -ItemType Directory -Force -Path $LOG_DIR | Out-Null
    }
    Add-Content -LiteralPath $DEBUG_LOG "[$timestamp] [$level] $msg"
}

function Initialize-BackupSession([string]$workDir) {
    if ($env:SGDK_ENABLE_BACKUP -and $env:SGDK_ENABLE_BACKUP -eq "0") {
        return $null
    }
    if ($script:BackupSessionRoot) {
        return $script:BackupSessionRoot
    }
    $root = Join-Path $workDir "out\.backups"
    if (-not (Test-Path -LiteralPath $root)) {
        New-Item -ItemType Directory -Force -Path $root | Out-Null
    }
    $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $token = [guid]::NewGuid().ToString("N")
    $session = Join-Path $root ("{0}_{1}" -f $stamp, $token)
    New-Item -ItemType Directory -Force -Path $session | Out-Null
    $script:BackupSessionRoot = $session
    return $session
}

function Save-BackupBeforeEdit([string]$workDir, [string]$absPath) {
    $session = Initialize-BackupSession $workDir
    if (-not $session) {
        return
    }
    if (-not (Test-Path -LiteralPath $absPath -PathType Leaf)) {
        return
    }
    $fullWork = [IO.Path]::GetFullPath($workDir).TrimEnd('\')
    $fullFile = [IO.Path]::GetFullPath($absPath)
    $rel = $null
    if ($fullFile.StartsWith($fullWork + "\", [StringComparison]::OrdinalIgnoreCase)) {
        $rel = $fullFile.Substring($fullWork.Length + 1)
    } else {
        $rel = Split-Path -Leaf $fullFile
    }
    $dest = Join-Path $session $rel
    $destDir = Split-Path -Parent $dest
    if (-not (Test-Path -LiteralPath $destDir)) {
        New-Item -ItemType Directory -Force -Path $destDir | Out-Null
    }
    Copy-Item -LiteralPath $fullFile -Destination $dest -Force
}

function Get-MagickPath() {
    return SGDK_GetMagickPath
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

function Resolve-AssetKind($filePath, $requestedKind) {
    if ($requestedKind -ne "Auto") {
        return $requestedKind
    }
    $normalized = $filePath.ToLowerInvariant()
    if ($normalized -match '\\sprites\\' -or $normalized -match '/sprites/') {
        return "SPRITE"
    }
    return "IMAGE"
}

function Get-PreparationMetadata($filePath) {
    if (-not (Test-Path -LiteralPath $PREP_REPORT)) {
        return $null
    }
    try {
        $report = Get-Content -LiteralPath $PREP_REPORT -Raw | ConvertFrom-Json
    } catch {
        return $null
    }
    foreach ($asset in $report.prepared_assets) {
        if (-not $asset.output_file) { continue }
        if ([IO.Path]::GetFullPath($asset.output_file) -eq $filePath) {
            return $asset
        }
    }
    return $null
}

$magickPath = Get-MagickPath
if (-not $magickPath) {
    Write-Log "ImageMagick (magick.exe) não encontrado. Abortando." "ERROR"
    exit 1
}

if (-not (Test-Path -LiteralPath $File)) {
    Write-Log "Arquivo não encontrado: $File" "ERROR"
    exit 1
}

$absFile = [IO.Path]::GetFullPath($File)
$resolvedKind = Resolve-AssetKind $absFile $AssetKind
Write-Log "Processando: $absFile ($resolvedKind)"

try {
    $info = Get-ImageInfo $magickPath $absFile
} catch {
    Write-Log "Falha ao ler metadados da imagem: $($_.Exception.Message)" "ERROR"
    exit 1
}

$newWidth = if (($info.Width % 8) -eq 0) { $info.Width } else { [math]::Ceiling($info.Width / 8) * 8 }
$newHeight = if (($info.Height % 8) -eq 0) { $info.Height } else { [math]::Ceiling($info.Height / 8) * 8 }
$needsFix = $Force -or
    $newWidth -ne $info.Width -or
    $newHeight -ne $info.Height -or
    -not $info.Indexed -or
    $info.Depth -gt 8 -or
    $info.Colors -gt 16

if (-not $needsFix) {
    Write-Log "Imagem já está em conformidade. Nenhuma ação necessária."
    exit 0
}

$metadata = Get-PreparationMetadata $absFile
$transparentColor = $null
if ($metadata -and $metadata.details.background_color) {
    $bg = $metadata.details.background_color
    if ($bg.Count -ge 3 -and $metadata.details.background_strategy -eq "border_color") {
        $transparentColor = "rgb($($bg[0]),$($bg[1]),$($bg[2]))"
    }
}

$tmpFile = Join-Path ([IO.Path]::GetTempPath()) ("sgdk_safe_{0}.png" -f ([guid]::NewGuid().ToString("N")))
try {
    $args = @($absFile)
    if ($transparentColor -and $resolvedKind -eq "SPRITE") {
        Write-Log "Aplicando transparência assistida por metadados: $transparentColor"
        $args += @("-fuzz", "6%", "-transparent", $transparentColor)
    }
    $args += @(
        "-background", "none",
        "-gravity", "NorthWest",
        "-extent", "$($newWidth)x$($newHeight)",
        "-colors", "16"
    )
    if ($resolvedKind -eq "SPRITE") {
        $args += @("-type", "PaletteAlpha")
    } else {
        $args += @("-alpha", "off", "-type", "Palette")
    }
    $args += @("PNG8:$tmpFile")

    & $magickPath @args
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $tmpFile)) {
        Write-Log "Falha na conversão via ImageMagick." "ERROR"
        exit 1
    }

    Save-BackupBeforeEdit $pwd.Path $absFile
    Move-Item -LiteralPath $tmpFile -Destination $absFile -Force
    $revalidated = Get-ImageInfo $magickPath $absFile
    if (-not $revalidated.Indexed -or $revalidated.Depth -gt 8 -or $revalidated.Colors -gt 16) {
        Write-Log "Imagem permaneceu fora do padrão após a sanitização." "ERROR"
        exit 1
    }
    Write-Log "Imagem sanitizada com sucesso." "OK"
} catch {
    Write-Log "Exceção durante o processamento: $($_.Exception.Message)" "ERROR"
    exit 1
} finally {
    if (Test-Path -LiteralPath $tmpFile) {
        Remove-Item -LiteralPath $tmpFile -Force -ErrorAction SilentlyContinue
    }
}
