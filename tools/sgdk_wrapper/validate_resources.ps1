[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$WorkDir = "",
    [Parameter(Mandatory = $false)]
    [switch]$Fix,
    [Parameter(Mandatory = $false)]
    [switch]$CloseoutGate
)

try {
    if (-not [string]::IsNullOrWhiteSpace($WorkDir)) {
        Set-Location -LiteralPath $WorkDir
    }
} catch {
    Write-Error ("[ERROR] validate_resources.ps1: failed to Set-Location to '{0}'. Details: {1}" -f $WorkDir, $_.Exception.Message)
    exit 1
}

. (Join-Path $PSScriptRoot "_lib\sgdk_common.ps1")

function Write-Log($msg, $level = "INFO") {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $fullMsg = "[$timestamp] [$level] $msg"
    Write-Host $fullMsg
    if (-not (Test-Path -LiteralPath $LOG_DIR)) {
        New-Item -ItemType Directory -Force -Path $LOG_DIR | Out-Null
    }
    [System.IO.File]::AppendAllText($DEBUG_LOG, $fullMsg + [Environment]::NewLine, [System.Text.Encoding]::UTF8)
}

function Get-EnvIntOrDefault($envName, $defaultValue) {
    $rawValue = [System.Environment]::GetEnvironmentVariable($envName)
    if ([string]::IsNullOrWhiteSpace($rawValue)) {
        return $defaultValue
    }

    $parsedValue = 0
    if ([int]::TryParse($rawValue, [ref]$parsedValue)) {
        return $parsedValue
    }

    return $defaultValue
}

function Get-EnvDoubleOrDefault($envName, $defaultValue) {
    $rawValue = [System.Environment]::GetEnvironmentVariable($envName)
    if ([string]::IsNullOrWhiteSpace($rawValue)) {
        return $defaultValue
    }

    $parsedValue = 0.0
    if ([double]::TryParse($rawValue, [System.Globalization.NumberStyles]::Float, [System.Globalization.CultureInfo]::InvariantCulture, [ref]$parsedValue)) {
        return $parsedValue
    }

    return $defaultValue
}

function Get-EnvSettingSnapshot($envName, $defaultValue, $kind) {
    $rawValue = [System.Environment]::GetEnvironmentVariable($envName)
    $hasOverride = -not [string]::IsNullOrWhiteSpace($rawValue)

    if ($kind -eq "int") {
        $effectiveValue = Get-EnvIntOrDefault $envName $defaultValue
    } else {
        $effectiveValue = Get-EnvDoubleOrDefault $envName $defaultValue
    }

    $isValidOverride = $false
    if ($hasOverride) {
        if ($kind -eq "int") {
            $parsedValue = 0
            $isValidOverride = [int]::TryParse($rawValue, [ref]$parsedValue)
        } else {
            $parsedValue = 0.0
            $isValidOverride = [double]::TryParse($rawValue, [System.Globalization.NumberStyles]::Float, [System.Globalization.CultureInfo]::InvariantCulture, [ref]$parsedValue)
        }
    }

    return [pscustomobject]@{
        env = $envName
        kind = $kind
        default = $defaultValue
        raw = $rawValue
        has_override = $hasOverride
        override_valid = $isValidOverride
        source = if ($hasOverride -and $isValidOverride) { "env" } elseif ($hasOverride) { "default_invalid_env" } else { "default" }
        effective = $effectiveValue
    }
}

$LOG_DIR = if ($env:SGDK_LOG_DIR) { $env:SGDK_LOG_DIR } else { Join-Path $pwd.Path "out\logs" }
$DEBUG_LOG = if ($env:SGDK_DEBUG_LOG) { $env:SGDK_DEBUG_LOG } else { Join-Path $LOG_DIR "build_debug.log" }
$MAX_SPRITE_SIZE_TILES = 32
$MAX_INTERNAL_SPRITES = 16
$REPORT_FILE = if ($env:SGDK_VALIDATION_REPORT) { $env:SGDK_VALIDATION_REPORT } else { Join-Path $LOG_DIR "validation_report.json" }
$Index0VisibleWarnMinPixelsSetting = Get-EnvSettingSnapshot "SGDK_INDEX0_VISIBLE_WARN_MIN_PIXELS" 8 "int"
$Index0VisibleWarnMinRatioSetting = Get-EnvSettingSnapshot "SGDK_INDEX0_VISIBLE_WARN_MIN_RATIO" 0.0005 "double"
$Index0VisibleErrorMinPixelsSetting = Get-EnvSettingSnapshot "SGDK_INDEX0_VISIBLE_ERROR_MIN_PIXELS" 128 "int"
$Index0VisibleErrorMinRatioSetting = Get-EnvSettingSnapshot "SGDK_INDEX0_VISIBLE_ERROR_MIN_RATIO" 0.01 "double"
$Index0TransparentCoverageInfoMinPixelsSetting = Get-EnvSettingSnapshot "SGDK_INDEX0_TRANSPARENT_COVERAGE_INFO_MIN_PIXELS" 2048 "int"
$Index0TransparentCoverageInfoMinRatioSetting = Get-EnvSettingSnapshot "SGDK_INDEX0_TRANSPARENT_COVERAGE_INFO_MIN_RATIO" 0.35 "double"
$IndexedTransparencyAuditSettings = @(
    $Index0VisibleWarnMinPixelsSetting
    $Index0VisibleWarnMinRatioSetting
    $Index0VisibleErrorMinPixelsSetting
    $Index0VisibleErrorMinRatioSetting
    $Index0TransparentCoverageInfoMinPixelsSetting
    $Index0TransparentCoverageInfoMinRatioSetting
)
$INDEX0_VISIBLE_WARN_MIN_PIXELS = $Index0VisibleWarnMinPixelsSetting.effective
$INDEX0_VISIBLE_WARN_MIN_RATIO = $Index0VisibleWarnMinRatioSetting.effective
$INDEX0_VISIBLE_ERROR_MIN_PIXELS = $Index0VisibleErrorMinPixelsSetting.effective
$INDEX0_VISIBLE_ERROR_MIN_RATIO = $Index0VisibleErrorMinRatioSetting.effective
$INDEX0_TRANSPARENT_COVERAGE_INFO_MIN_PIXELS = $Index0TransparentCoverageInfoMinPixelsSetting.effective
$INDEX0_TRANSPARENT_COVERAGE_INFO_MIN_RATIO = $Index0TransparentCoverageInfoMinRatioSetting.effective

function Find-RecoveredPath($relPath, $baseDir) {
    return SGDK_FindRecoveredPath $relPath $baseDir
}

function Estimate-VDPSprites($wTiles, $hTiles) {
    return SGDK_EstimateVDPSprites $wTiles $hTiles
}

function Get-MagickPath() {
    return SGDK_GetMagickPath
}

function Get-PngHeaderInfo($filePath) {
    $bytes = [System.IO.File]::ReadAllBytes($filePath)
    if ($bytes.Length -lt 29) { throw "File too small to be a valid PNG" }
    if ($bytes[0] -ne 0x89 -or $bytes[1] -ne 0x50) { throw "Not a PNG file (bad signature)" }

    $w = [int]$bytes[16] * 16777216 + [int]$bytes[17] * 65536 + [int]$bytes[18] * 256 + [int]$bytes[19]
    $h = [int]$bytes[20] * 16777216 + [int]$bytes[21] * 65536 + [int]$bytes[22] * 256 + [int]$bytes[23]
    $bitDepth = [int]$bytes[24]
    $colorType = [int]$bytes[25]

    $palEntries = 0
    $i = 8
    while ($i -lt ($bytes.Length - 12)) {
        $chunkLen = [int]$bytes[$i] * 16777216 + [int]$bytes[$i+1] * 65536 + [int]$bytes[$i+2] * 256 + [int]$bytes[$i+3]
        $chunkType = [System.Text.Encoding]::ASCII.GetString($bytes, $i + 4, 4)
        if ($chunkType -eq 'PLTE') { $palEntries = [int]($chunkLen / 3); break }
        if ($chunkType -eq 'IDAT') { break }
        $i += 12 + $chunkLen
    }

    $isIndexed = ($colorType -eq 3)
    $typeName = switch ($colorType) { 0 { 'Grayscale' } 2 { 'DirectClassRGB' } 3 { 'PseudoClass' } 4 { 'GrayscaleAlpha' } 6 { 'DirectClassRGBA' } default { "Unknown" } }

    $uniqueColors = 0
    if ($isIndexed) {
        try {
            Add-Type -AssemblyName System.Drawing -ErrorAction Stop
            $bmp = [System.Drawing.Bitmap]::FromFile($filePath)
            try {
                $pf = $bmp.PixelFormat
                $bpp = [System.Drawing.Image]::GetPixelFormatSize($pf)
                if ($bpp -eq 4 -or $bpp -eq 8) {
                    $rect = [System.Drawing.Rectangle]::new(0, 0, $bmp.Width, $bmp.Height)
                    $bd = $bmp.LockBits($rect, [System.Drawing.Imaging.ImageLockMode]::ReadOnly, $pf)
                    try {
                        $stride = [Math]::Abs($bd.Stride)
                        $buf = New-Object byte[] ($stride * $bmp.Height)
                        [System.Runtime.InteropServices.Marshal]::Copy($bd.Scan0, $buf, 0, $buf.Length)
                        $seen = New-Object bool[] 256
                        for ($y = 0; $y -lt $bmp.Height; $y++) {
                            $rowOff = $y * $stride
                            for ($x = 0; $x -lt $bmp.Width; $x++) {
                                if ($bpp -eq 8) {
                                    $idx = [int]$buf[$rowOff + $x]
                                } else {
                                    $bv = [int]$buf[$rowOff + [int][Math]::Floor($x / 2)]
                                    $idx = if (($x % 2) -eq 0) { ($bv -shr 4) -band 0x0F } else { $bv -band 0x0F }
                                }
                                $seen[$idx] = $true
                            }
                        }
                        for ($k = 0; $k -lt 256; $k++) { if ($seen[$k]) { $uniqueColors++ } }
                    } finally {
                        $bmp.UnlockBits($bd)
                    }
                }
            } finally {
                $bmp.Dispose()
            }
        } catch {
            $uniqueColors = 0
        }
    }

    $effectiveColors = if ($uniqueColors -gt 0) { $uniqueColors } elseif ($isIndexed -and $palEntries -gt 0) { $palEntries } elseif ($isIndexed) { [Math]::Pow(2, $bitDepth) } else { 0 }

    return [pscustomobject]@{
        Width = $w
        Height = $h
        Depth = $bitDepth
        Colors = [int]$effectiveColors
        PaletteEntries = $palEntries
        Class = $typeName
        Indexed = $isIndexed
        Source = "dotnet_png_header"
    }
}

function Get-ImageInfo($magickPath, $filePath) {
    if (-not $magickPath -or -not (Test-Path -LiteralPath $magickPath)) {
        throw "ImageMagick executable invalid or missing: $magickPath"
    }
    if (-not (Test-Path -LiteralPath $filePath)) {
        throw "Image file not found: $filePath"
    }
    # Start-Process evita falhas do operador & com caminhos contendo espacos (erro "O termo 'C' nao e reconhecido").
    $stdout = [System.IO.Path]::GetTempFileName()
    $stderr = [System.IO.Path]::GetTempFileName()
    try {
        $p = Start-Process -FilePath $magickPath -ArgumentList @(
            'identify', '-format', '%w|%h|%z|%k|%r', $filePath
        ) -NoNewWindow -Wait -PassThru -RedirectStandardOutput $stdout -RedirectStandardError $stderr
        $identifyText = ([System.IO.File]::ReadAllText($stdout)).Trim()
        if ($p.ExitCode -ne 0) {
            $errText = [System.IO.File]::ReadAllText($stderr)
            throw "ImageMagick identify exit $($p.ExitCode): $errText"
        }
        if ($identifyText -match '^(\d+)\|(\d+)\|(\d+)\|(\d+)\|(.+)$') {
            return [pscustomobject]@{
                Width = [int]$matches[1]
                Height = [int]$matches[2]
                Depth = [int]$matches[3]
                Colors = [int]$matches[4]
                Class = $matches[5]
                Indexed = ($matches[5] -match '^PseudoClass')
                Source = "imagemagick"
            }
        }
        throw "Unable to parse ImageMagick identify output: $identifyText"
    }
    finally {
        Remove-Item -LiteralPath $stdout -ErrorAction SilentlyContinue
        Remove-Item -LiteralPath $stderr -ErrorAction SilentlyContinue
    }
}

function Get-ImageOptionTokens($line) {
    if ($line -match '^\s*IMAGE\s+\w+\s+"[^"]+"\s*(.*)$') {
        $tail = $matches[1].Trim()
        if ([string]::IsNullOrWhiteSpace($tail)) {
            return @()
        }
        return , @($tail -split '\s+')
    }
    return @()
}

function Resolve-ResReferencePath($baseDir, $declaredPath) {
    if ([string]::IsNullOrWhiteSpace($declaredPath)) {
        return $null
    }
    if ([System.IO.Path]::IsPathRooted($declaredPath)) {
        return [System.IO.Path]::GetFullPath($declaredPath)
    }
    return [System.IO.Path]::GetFullPath((Join-Path $baseDir $declaredPath))
}

function Get-DeclaredAudioEntries($resFiles) {
    $entries = @()
    $pattern = '^\s*(?<kind>WAV|XGM2|XGM|BIN)\s+(?<name>\w+)\s+(?:"(?<quoted>[^"]+)"|(?<bare>\S+))(?:\s+(?<arg1>[A-Za-z0-9_]+))?(?:\s+(?<arg2>\d+))?'

    foreach ($resFile in $resFiles) {
        $baseDir = Split-Path -Parent $resFile.FullName
        $lineNumber = 0
        foreach ($line in (Get-Content -LiteralPath $resFile.FullName -ErrorAction SilentlyContinue)) {
            $lineNumber++
            $trimmed = $line.Trim()
            if ([string]::IsNullOrWhiteSpace($trimmed) -or $trimmed.StartsWith("//")) {
                continue
            }
            if ($trimmed -notmatch $pattern) {
                continue
            }

            $kind = $matches["kind"].ToUpperInvariant()
            $declaredPath = if ($matches["quoted"]) { $matches["quoted"] } else { $matches["bare"] }
            if ($kind -eq "BIN") {
                $ext = [System.IO.Path]::GetExtension($declaredPath).ToLowerInvariant()
                if ($ext -notin @(".raw", ".pcm", ".dpcm")) {
                    continue
                }
            }

            $resolvedPath = Resolve-ResReferencePath $baseDir $declaredPath
            $entries += [pscustomobject]@{
                kind = if ($kind -eq "BIN") { "BIN_AUDIO" } else { $kind }
                resource_name = $matches["name"]
                declared_path = $declaredPath
                resolved_path = $resolvedPath
                res_file = $resFile.FullName
                res_line = $lineNumber
                exists = Test-Path -LiteralPath $resolvedPath -PathType Leaf
            }
        }
    }

    return @($entries)
}

function Get-LatestExistingWriteUtc($paths) {
    $latest = $null
    foreach ($path in $paths) {
        if (-not $path) { continue }
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { continue }
        $candidate = (Get-Item -LiteralPath $path).LastWriteTimeUtc
        if (($null -eq $latest) -or ($candidate -gt $latest)) {
            $latest = $candidate
        }
    }
    return $latest
}

function Test-SceneScaleImage($resourceName, $resourcePath, $info) {
    $fingerprint = ("{0} {1}" -f $resourceName, $resourcePath).ToLowerInvariant()
    if ($fingerprint -match 'bg[_\- ]?[ab]|scene|parallax|compare[_\- ]?flat|foreground|land|forest|stage|level') {
        return $true
    }
    return (($info.Width -ge 256) -and ($info.Height -ge 112))
}

function Test-StructuralAlphaExpected($resourceKind, $resourceName, $resourcePath) {
    if ($resourceKind -ne "IMAGE") {
        return $false
    }
    $fingerprint = ("{0} {1}" -f $resourceName, $resourcePath).ToLowerInvariant()
    return ($fingerprint -match 'bg[_\- ]?a|foreground|overlay|occlusion|mask|front|midground|plate|layer')
}

function Get-IndexedTransparencyAudit($filePath) {
    try {
        Add-Type -AssemblyName System.Drawing -ErrorAction Stop
    } catch {
        return $null
    }

    $bitmap = $null
    $bitmapData = $null
    try {
        $bitmap = [System.Drawing.Bitmap]::FromFile($filePath)
        $pixelFormat = $bitmap.PixelFormat
        $indexedFlag = [System.Drawing.Imaging.PixelFormat]::Indexed
        if (([int]$pixelFormat -band [int]$indexedFlag) -eq 0) {
            return $null
        }

        $bitsPerPixel = [System.Drawing.Image]::GetPixelFormatSize($pixelFormat)
        if ($bitsPerPixel -ne 4 -and $bitsPerPixel -ne 8) {
            return $null
        }

        $rect = [System.Drawing.Rectangle]::new(0, 0, $bitmap.Width, $bitmap.Height)
        $bitmapData = $bitmap.LockBits($rect, [System.Drawing.Imaging.ImageLockMode]::ReadOnly, $pixelFormat)
        $stride = [Math]::Abs($bitmapData.Stride)
        $bufferLength = $stride * $bitmap.Height
        $buffer = New-Object byte[] $bufferLength
        [System.Runtime.InteropServices.Marshal]::Copy($bitmapData.Scan0, $buffer, 0, $bufferLength)

        $zeroIndexPixelCount = 0
        for ($y = 0; $y -lt $bitmap.Height; $y++) {
            $rowOffset = $y * $stride
            for ($x = 0; $x -lt $bitmap.Width; $x++) {
                if ($bitsPerPixel -eq 8) {
                    $pixelIndex = $buffer[$rowOffset + $x]
                } else {
                    $byteValue = $buffer[$rowOffset + [int][Math]::Floor($x / 2)]
                    if (($x % 2) -eq 0) {
                        $pixelIndex = ($byteValue -shr 4) -band 0x0F
                    } else {
                        $pixelIndex = $byteValue -band 0x0F
                    }
                }

                if ($pixelIndex -eq 0) {
                    $zeroIndexPixelCount++
                }
            }
        }

        $paletteAlpha = 255
        if ($bitmap.Palette -and $bitmap.Palette.Entries.Count -gt 0) {
            $paletteAlpha = [int]$bitmap.Palette.Entries[0].A
        }

        return [pscustomobject]@{
            bitsPerPixel = $bitsPerPixel
            totalPixels = ($bitmap.Width * $bitmap.Height)
            zeroIndexPixelCount = $zeroIndexPixelCount
            zeroIndexCoverage = if (($bitmap.Width * $bitmap.Height) -gt 0) { $zeroIndexPixelCount / ($bitmap.Width * $bitmap.Height) } else { 0.0 }
            paletteZeroAlpha = $paletteAlpha
            hasVisibleZeroIndexRisk = ($zeroIndexPixelCount -gt 0 -and $paletteAlpha -gt 0)
        }
    } catch {
        return $null
    } finally {
        if ($bitmapData -and $bitmap) {
            $bitmap.UnlockBits($bitmapData)
        }
        if ($bitmap) {
            $bitmap.Dispose()
        }
    }
}

function Get-IndexedTransparencySeverity($audit) {
    if (-not $audit) {
        return $null
    }

    if ($audit.paletteZeroAlpha -le 0) {
        $highCoverageTransparent = (
            $audit.zeroIndexPixelCount -ge $INDEX0_TRANSPARENT_COVERAGE_INFO_MIN_PIXELS -and
            $audit.zeroIndexCoverage -ge $INDEX0_TRANSPARENT_COVERAGE_INFO_MIN_RATIO
        )

        return [pscustomobject]@{
            level = if ($highCoverageTransparent) { "INFO" } else { "OK" }
            code = if ($highCoverageTransparent) { "INDEX0_TRANSPARENT_HEAVY" } else { "INDEX0_TRANSPARENT_OK" }
            message = if ($highCoverageTransparent) {
                "Slot indexado 0 esta transparente e cobre uma area grande; revisar se a matte estrutural continua intencional no recorte final."
            } else {
                "Slot indexado 0 esta transparente e consistente com o papel estrutural esperado."
            }
        }
    }

    if ($audit.zeroIndexPixelCount -le 0) {
        return [pscustomobject]@{
            level = "INFO"
            code = "INDEX0_OPAQUE_UNUSED"
            message = "Slot indexado 0 esta opaco, mas nao foi usado por pixels da imagem."
        }
    }

    $errorRisk = (
        $audit.zeroIndexPixelCount -ge $INDEX0_VISIBLE_ERROR_MIN_PIXELS -and
        $audit.zeroIndexCoverage -ge $INDEX0_VISIBLE_ERROR_MIN_RATIO
    )
    if ($errorRisk) {
        return [pscustomobject]@{
            level = "ERROR"
            code = "INDEX0_VISIBLE_HIGH_RISK"
            message = "Slot indexado 0 esta visivel e cobre massa significativa; risco alto de perder forma util quando a transparencia estrutural for aplicada."
        }
    }

    $warningRisk = (
        $audit.zeroIndexPixelCount -ge $INDEX0_VISIBLE_WARN_MIN_PIXELS -and
        $audit.zeroIndexCoverage -ge $INDEX0_VISIBLE_WARN_MIN_RATIO
    )
    if ($warningRisk) {
        return [pscustomobject]@{
            level = "WARNING"
            code = "INDEX0_VISIBLE_MEDIUM_RISK"
            message = "Slot indexado 0 esta visivel em area relevante; revisar se pixels estruturais nao cairam no indice reservado a transparencia."
        }
    }

    return [pscustomobject]@{
        level = "INFO"
        code = "INDEX0_VISIBLE_LOW_RISK"
        message = "Slot indexado 0 esta visivel apenas em area residual; conferir se a presenca e intencional antes da promocao final."
    }
}

function Normalize-RiskTaxonomyLevel($Level) {
    $normalized = (Get-SafeString $Level "").ToUpperInvariant()
    switch ($normalized) {
        "WARN" { return "WARNING" }
        "WARNING" { return "WARNING" }
        "ERROR" { return "ERROR" }
        "INFO" { return "INFO" }
        default { return "OTHER" }
    }
}

function New-RiskTaxonomyBucket() {
    return [ordered]@{
        count = 0
        levels = [ordered]@{
            INFO = 0
            WARNING = 0
            ERROR = 0
            OTHER = 0
        }
        types = @()
    }
}

function New-RiskTaxonomy() {
    return [ordered]@{
        asset_risk = (New-RiskTaxonomyBucket)
        validator_config_risk = (New-RiskTaxonomyBucket)
        runtime_risk = (New-RiskTaxonomyBucket)
    }
}

function Resolve-RiskDomain($type, $resource, $file) {
    $normalizedType = (Get-SafeString $type "").ToUpperInvariant()
    $normalizedResource = (Get-SafeString $resource "").ToLowerInvariant()
    $normalizedFile = (Get-SafeString $file "").ToLowerInvariant()

    if (
        $normalizedResource -eq "validator_config" -or
        $normalizedType -eq "INDEX0_THRESHOLD_INVALID_OVERRIDE" -or
        $normalizedType -eq "RUNTIME_THRESHOLDS"
    ) {
        return "validator_config_risk"
    }

    if (
        $normalizedResource -in @("runtime", "emulator", "rom", "code", "heap") -or
        $normalizedType -like "RUNTIME_*" -or
        $normalizedType -like "EMULATOR_*" -or
        $normalizedType -in @("ROM_SIZE", "AGENT_BOOTSTRAP", "BANNED_API", "CODE_SCAN") -or
        $normalizedFile.EndsWith("runtime_metrics.json") -or
        $normalizedFile.EndsWith("emulator_session.json") -or
        $normalizedFile.EndsWith("rom.bin")
    ) {
        return "runtime_risk"
    }

    return "asset_risk"
}

function Add-RiskTaxonomyEntry($results, $detail) {
    if (-not $results -or -not $detail) {
        return
    }

    if (-not $results.risk_taxonomy) {
        $results.risk_taxonomy = New-RiskTaxonomy
    }

    $riskDomain = Get-SafeString $detail.risk_domain "asset_risk"
    if (-not $results.risk_taxonomy.Contains($riskDomain)) {
        $results.risk_taxonomy[$riskDomain] = New-RiskTaxonomyBucket
    }

    $bucket = $results.risk_taxonomy[$riskDomain]
    $bucket.count = [int]$bucket.count + 1

    $normalizedLevel = Normalize-RiskTaxonomyLevel $detail.level
    if (-not $bucket.levels.Contains($normalizedLevel)) {
        $bucket.levels[$normalizedLevel] = 0
    }
    $bucket.levels[$normalizedLevel] = [int]$bucket.levels[$normalizedLevel] + 1

    $detailType = Get-SafeString $detail.type ""
    if ($detailType) {
        $existingTypes = @($bucket.types)
        if ($existingTypes -notcontains $detailType) {
            $bucket.types = @($existingTypes + $detailType)
        }
    }
}

function Add-Detail($results, $type, $level, $message, $resource, $file, $extra = @{}) {
    $riskDomain = $null
    if ($extra -is [hashtable] -and $extra.ContainsKey("risk_domain")) {
        $riskDomain = Get-SafeString $extra["risk_domain"] ""
    }
    if (-not $riskDomain) {
        $riskDomain = Resolve-RiskDomain -type $type -resource $resource -file $file
    }

    $detail = @{
        type = $type
        level = $level
        message = $message
        resource = $resource
        file = $file
        risk_domain = $riskDomain
    }
    foreach ($key in $extra.Keys) {
        $detail[$key] = $extra[$key]
    }
    $results.details += $detail
    Add-RiskTaxonomyEntry -results $results -detail $detail
}

function Test-CloseoutOnlyBlockingStatus($status) {
    $normalizedStatus = Get-SafeString $status ""
    return $normalizedStatus -in @(
        "agent_context_degraded",
        "audio_validation_missing",
        "audio_validation_stale",
        "budget_doc_mismatch",
        "changelog_missing",
        "emulator_evidence_stale",
        "gameplay_gate_incomplete",
        "scene_regression_incomplete",
        "visual_gate_blocked"
    )
}

function Get-BlockingStatusLogLevel($status) {
    if (Test-CloseoutOnlyBlockingStatus $status) {
        if ($CloseoutGate) {
            return "ERROR"
        }
        return "WARN"
    }

    return "ERROR"
}

function Add-BlockingStatus($results, $status, $message, $resource, $file, $extra = @{}) {
    $normalizedStatus = Get-SafeString $status ""
    if (-not $normalizedStatus) {
        return
    }

    if (-not $results.ContainsKey("blocking_statuses")) {
        $results.blocking_statuses = @()
    }

    if ($normalizedStatus -notin $results.blocking_statuses) {
        $results.blocking_statuses += $normalizedStatus
    }

    $closeoutOnly = Test-CloseoutOnlyBlockingStatus $normalizedStatus
    $enforcedAsError = (-not $closeoutOnly) -or $CloseoutGate
    if ($enforcedAsError) {
        $results.summary.errors++
    } else {
        $results.summary.warnings++
    }

    $payload = @{}
    foreach ($key in $extra.Keys) {
        $payload[$key] = $extra[$key]
    }
    $payload.blocking_status = $normalizedStatus
    $payload.closeout_only = $closeoutOnly
    $payload.closeout_gate_enforced = [bool]$CloseoutGate
    Add-Detail $results "BLOCKING_STATUS" $(if ($enforcedAsError) { "ERROR" } else { "WARNING" }) $message $resource $file $payload
}

function Get-PythonPath() {
    return SGDK_GetPythonPath
}

function Get-AestheticRole($resourceKind, $resourceName, $resourcePath) {
    $fingerprint = ("{0} {1}" -f $resourceName, $resourcePath).ToLowerInvariant()
    if ($resourceKind -eq "SPRITE") {
        return "sprite"
    }
    if ($fingerprint -match 'hud|ui|font|icon|score|life|timer') {
        return "hud"
    }
    if ($fingerprint -match 'bg[_\- ]?b|parallax|far|distant|sky|back') {
        return "bg_b"
    }
    if ($fingerprint -match 'bg[_\- ]?a|foreground|near|front|ground|stage|level|map|bg') {
        return "bg_a"
    }
    return "bg_a"
}

function Test-CriticalVisual($resourceKind, $resourceName, $resourcePath) {
    $fingerprint = ("{0} {1}" -f $resourceName, $resourcePath).ToLowerInvariant()
    if ($resourceKind -eq "SPRITE" -and $fingerprint -match 'player|hero|main|boss|protagon|jogador') {
        return $true
    }
    return $false
}

function Invoke-AestheticAnalysis {
    param(
        [Parameter(Mandatory = $true)][string]$PythonPath,
        [Parameter(Mandatory = $true)][string]$AnalyzerPath,
        [Parameter(Mandatory = $true)][string]$AssetPath,
        [Parameter(Mandatory = $true)][string]$Role,
        [Parameter(Mandatory = $true)][string]$ReferenceProfile,
        [Parameter(Mandatory = $true)][string]$OutputPath,
        [Parameter(Mandatory = $false)][string]$PairedBg,
        [Parameter(Mandatory = $false)][bool]$CriticalVisual = $false
    )

    $args = @(
        $AnalyzerPath,
        "--asset", $AssetPath,
        "--role", $Role,
        "--reference-profile", $ReferenceProfile,
        "--output", $OutputPath
    )

    if (-not [string]::IsNullOrWhiteSpace($PairedBg)) {
        $args += @("--paired-bg", $PairedBg)
    }
    if ($CriticalVisual) {
        $args += "--critical-visual"
    }

    & $PythonPath @args | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "analyze_aesthetic.py falhou para '$AssetPath' com exit code $LASTEXITCODE."
    }

    return Get-Content -LiteralPath $OutputPath -Raw | ConvertFrom-Json
}

function Invoke-VisualLabCaseAnalysis {
    param(
        [Parameter(Mandatory = $true)][string]$PythonPath,
        [Parameter(Mandatory = $true)][string]$AnalyzerPath,
        [Parameter(Mandatory = $true)][string]$ManifestPath,
        [Parameter(Mandatory = $true)][string]$OutputPath
    )

    $args = @(
        $AnalyzerPath,
        "--manifest", $ManifestPath,
        "--output", $OutputPath
    )

    & $PythonPath @args | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "analyze_visual_lab_case.py falhou para '$ManifestPath' com exit code $LASTEXITCODE."
    }

    return Get-Content -LiteralPath $OutputPath -Raw | ConvertFrom-Json
}

function Invoke-AutoFix($fixScript, $filePath, $assetKind) {
    if (-not (Test-Path -LiteralPath $fixScript)) {
        return $false
    }
    & $fixScript -File $filePath -AssetKind $assetKind
    return ($LASTEXITCODE -eq 0)
}

function Get-SafeString($value, $default = "") {
    if ($null -eq $value) {
        return $default
    }

    $text = [string]$value
    if ([string]::IsNullOrWhiteSpace($text)) {
        return $default
    }

    return $text
}

function Get-ObjectPropertyValue($object, $name, $default = $null) {
    if ($null -eq $object) {
        return $default
    }
    $prop = $object.PSObject.Properties[$name]
    if ($null -eq $prop) {
        return $default
    }
    return $prop.Value
}

function Get-SafeNumberOrNull($value) {
    if ($null -eq $value) {
        return $null
    }
    $text = [string]$value
    if ([string]::IsNullOrWhiteSpace($text)) {
        return $null
    }
    $parsedValue = 0.0
    if ([double]::TryParse($text, [System.Globalization.NumberStyles]::Float, [System.Globalization.CultureInfo]::InvariantCulture, [ref]$parsedValue)) {
        return $parsedValue
    }
    return $null
}

function Test-TruthyValue($value) {
    if ($null -eq $value) {
        return $false
    }
    if ($value -is [bool]) {
        return [bool]$value
    }
    $text = ([string]$value).Trim().ToLowerInvariant()
    if ([string]::IsNullOrWhiteSpace($text)) {
        return $false
    }
    return $text -in @("1", "true", "yes", "sim", "ok", "passed", "pass", "elite_ready")
}

function Test-EmptyOrNoneValue($value) {
    if ($null -eq $value) {
        return $true
    }
    $text = ([string]$value).Trim().ToLowerInvariant()
    if ([string]::IsNullOrWhiteSpace($text)) {
        return $true
    }
    return $text -in @("none", "nenhum", "nao", "nao_aplicavel", "not_applicable", "n/a", "original")
}

function Test-ApprovedDerivativeLicenseStatus($value, [bool]$HasDerivative) {
    if ($null -eq $value) {
        return $false
    }

    $text = ([string]$value).Trim().ToLowerInvariant()
    if ([string]::IsNullOrWhiteSpace($text)) {
        return $false
    }

    $approvedDerivedStatuses = @(
        "authorized",
        "authorised",
        "licensed",
        "cc0",
        "cc-by-ok",
        "cc_by_ok",
        "explicit_permission",
        "permitted",
        "approved"
    )

    if ($HasDerivative) {
        return $text -in $approvedDerivedStatuses
    }

    return $text -in (@("original", "own_authorial", "none", "not_applicable", "nao_aplicavel", "n/a") + $approvedDerivedStatuses)
}

function Test-AssetFlagPresent($asset, [string[]]$Needles) {
    $haystack = New-Object System.Collections.ArrayList
    foreach ($field in @("flags", "issues", "visual_issues", "blocking_statuses", "palette_findings", "delivery_findings")) {
        $value = Get-ObjectPropertyValue $asset $field $null
        if ($null -eq $value) { continue }
        foreach ($entry in @($value)) {
            if ($null -ne $entry) {
                [void]$haystack.Add(([string]$entry).ToLowerInvariant())
            }
        }
    }
    foreach ($needle in $Needles) {
        $needleText = $needle.ToLowerInvariant()
        foreach ($entry in $haystack) {
            if ($entry -eq $needleText -or $entry -match [regex]::Escape($needleText)) {
                return $true
            }
        }
    }
    return $false
}

function Test-ExistingArtifactReference($value, [string]$BaseDir) {
    if ($null -eq $value) {
        return $false
    }

    $candidate = $value
    if ($value.PSObject.Properties["path"]) {
        $candidate = $value.path
    }

    $text = Get-SafeString $candidate ""
    if (-not $text) {
        return $false
    }
    if ($text.ToLowerInvariant() -in @("inline", "embedded", "n/a", "not_applicable", "nao_aplicavel")) {
        return $false
    }

    $resolved = if ([System.IO.Path]::IsPathRooted($text)) { $text } else { Join-Path $BaseDir $text }
    return Test-Path -LiteralPath $resolved
}

function Resolve-ArtifactReference($value, [string]$BaseDir) {
    if ($null -eq $value) {
        return ""
    }

    $candidate = $value
    if ($value.PSObject.Properties["path"]) {
        $candidate = $value.path
    }

    $text = Get-SafeString $candidate ""
    if (-not $text -or $text.ToLowerInvariant() -in @("inline", "embedded", "n/a", "not_applicable", "nao_aplicavel")) {
        return ""
    }

    if ([System.IO.Path]::IsPathRooted($text)) {
        return $text
    }
    return Join-Path $BaseDir $text
}

function Get-ArtifactJsonOrNull($value, [string]$BaseDir) {
    $resolved = Resolve-ArtifactReference $value $BaseDir
    if (-not $resolved -or -not (Test-Path -LiteralPath $resolved -PathType Leaf)) {
        return $null
    }
    return Get-JsonOrNull -Path $resolved
}

function Test-HudVisualAsset($asset, [string]$AssetId) {
    $role = Get-SafeString (Get-ObjectPropertyValue $asset "role" "") ""
    $kind = Get-SafeString (Get-ObjectPropertyValue $asset "asset_kind" "") ""
    $fingerprint = ("{0} {1} {2}" -f $AssetId, $role, $kind).ToLowerInvariant()
    return $fingerprint -match "hud|ui|lifebar|life_bar|timer|score|overlay"
}

function Test-AnimatedCriticalAsset($asset, [string]$AssetId) {
    $role = Get-SafeString (Get-ObjectPropertyValue $asset "role" "") ""
    $kind = Get-SafeString (Get-ObjectPropertyValue $asset "asset_kind" "") ""
    $fingerprint = ("{0} {1} {2}" -f $AssetId, $role, $kind).ToLowerInvariant()
    if (Test-TruthyValue (Get-ObjectPropertyValue $asset "requires_animation_gate" $false)) {
        return $true
    }
    return $fingerprint -match "player_character|fighter|character|sprite|animation_strip|final_sprite_sheet"
}

function Get-StatusRank {
    param([Parameter(Mandatory = $true)][string]$Status)

    switch ($Status) {
        "aprovado" { return 1 }
        "alerta" { return 2 }
        "alerta_forte" { return 3 }
        "reprovado" { return 4 }
        default { return 0 }
    }
}

function Merge-Status {
    param(
        [Parameter(Mandatory = $true)][string]$Left,
        [Parameter(Mandatory = $true)][string]$Right
    )

    if ((Get-StatusRank $Right) -gt (Get-StatusRank $Left)) {
        return $Right
    }

    return $Left
}

function Resolve-WorkspaceRoot($startPath) {
    if ($env:MD_ROOT -and (Test-Path -LiteralPath $env:MD_ROOT)) {
        return [System.IO.Path]::GetFullPath($env:MD_ROOT)
    }

    $current = Get-Item -LiteralPath $startPath -ErrorAction SilentlyContinue
    while ($current) {
        $candidateManifest = Join-Path $current.FullName "tools\sgdk_wrapper\.agent\framework_manifest.json"
        if (Test-Path -LiteralPath $candidateManifest) {
            return $current.FullName
        }
        $parent = $current.Parent
        if (-not $parent) {
            break
        }
        $current = $parent
    }

    return $null
}

function Get-FileIdentity {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }

    $item = Get-Item -LiteralPath $Path
    $stream = [System.IO.File]::OpenRead($Path)
    try {
        $sha256 = [System.Security.Cryptography.SHA256]::Create()
        try {
            $hashBytes = $sha256.ComputeHash($stream)
            $hash = ([System.BitConverter]::ToString($hashBytes).Replace("-", "")).ToLowerInvariant()
        } finally {
            $sha256.Dispose()
        }
    } finally {
        $stream.Dispose()
    }
    return [ordered]@{
        path = $item.FullName
        size_bytes = [int64]$item.Length
        last_write_utc = $item.LastWriteTimeUtc.ToString("o")
        sha256 = $hash
    }
}

function Get-NormalizedTextHashOrNull {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }

    $content = Get-Content -LiteralPath $Path -Raw
    $normalized = $content.Replace("`r`n", "`n")
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($normalized)
    $sha256 = [System.Security.Cryptography.SHA256]::Create()
    try {
        $hashBytes = $sha256.ComputeHash($bytes)
        return ([System.BitConverter]::ToString($hashBytes).Replace("-", "")).ToLowerInvariant()
    } finally {
        $sha256.Dispose()
    }
}

function Get-BinaryFileHashOrNull {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }

    $stream = [System.IO.File]::OpenRead($Path)
    $sha256 = [System.Security.Cryptography.SHA256]::Create()
    try {
        $hashBytes = $sha256.ComputeHash($stream)
        return ([System.BitConverter]::ToString($hashBytes).Replace("-", "")).ToLowerInvariant()
    } finally {
        $sha256.Dispose()
        $stream.Dispose()
    }
}

function Get-AgentPathDigestOrNull {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        return $null
    }

    $item = Get-Item -LiteralPath $Path -Force
    if (-not $item.PSIsContainer) {
        $extension = [System.IO.Path]::GetExtension($Path).ToLowerInvariant()
        if ($extension -in @(".md", ".json", ".yaml", ".yml", ".ps1", ".py", ".bat")) {
            return Get-NormalizedTextHashOrNull -Path $Path
        }
        return Get-BinaryFileHashOrNull -Path $Path
    }

    $root = [System.IO.Path]::GetFullPath($Path).TrimEnd('\')
    $entries = New-Object System.Collections.Generic.List[string]
    foreach ($file in @(Get-ChildItem -LiteralPath $Path -Recurse -File -Force -ErrorAction SilentlyContinue | Sort-Object FullName)) {
        $full = [System.IO.Path]::GetFullPath($file.FullName)
        $relative = $full.Substring($root.Length).TrimStart('\') -replace '\\', '/'
        $hash = Get-AgentPathDigestOrNull -Path $full
        $entries.Add(("{0}={1}" -f $relative, $hash))
    }

    $payload = [string]::Join("`n", $entries)
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($payload)
    $sha256 = [System.Security.Cryptography.SHA256]::Create()
    try {
        $hashBytes = $sha256.ComputeHash($bytes)
        return ([System.BitConverter]::ToString($hashBytes).Replace("-", "")).ToLowerInvariant()
    } finally {
        $sha256.Dispose()
    }
}

function Get-JsonOrNull {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }

    try {
        return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
    } catch {
        return $null
    }
}

function Get-ObservedReportStatus {
    param(
        [Parameter(Mandatory = $true)][string]$ReportPath,
        [string[]]$DependencyPaths = @()
    )

    $result = [ordered]@{
        report_path = $ReportPath
        report_present = $false
        stale = $false
        generated_at = $null
        latest_dependency_utc = $null
    }

    if (-not (Test-Path -LiteralPath $ReportPath -PathType Leaf)) {
        return $result
    }

    $result.report_present = $true
    $reportItem = Get-Item -LiteralPath $ReportPath
    $reportWriteUtc = $reportItem.LastWriteTimeUtc
    $reportJson = Get-JsonOrNull $ReportPath

    if ($reportJson) {
        if ($reportJson.PSObject.Properties['generated_at']) {
            $result.generated_at = Get-SafeString $reportJson.generated_at ""
        } elseif ($reportJson.PSObject.Properties['timestamp']) {
            $result.generated_at = Get-SafeString $reportJson.timestamp ""
        }
    }

    $latestDependencyUtc = $null
    foreach ($dependencyPath in @($DependencyPaths | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) } | Select-Object -Unique)) {
        if (-not (Test-Path -LiteralPath $dependencyPath -PathType Leaf)) {
            continue
        }

        $dependencyWriteUtc = (Get-Item -LiteralPath $dependencyPath).LastWriteTimeUtc
        if ($null -eq $latestDependencyUtc -or $dependencyWriteUtc -gt $latestDependencyUtc) {
            $latestDependencyUtc = $dependencyWriteUtc
        }
    }

    if ($null -ne $latestDependencyUtc) {
        $result.latest_dependency_utc = $latestDependencyUtc.ToString("o")
        if ($latestDependencyUtc -gt $reportWriteUtc) {
            $result.stale = $true
        }
    }

    return $result
}

function Normalize-ResourceRelativePath {
    param([Parameter(Mandatory = $true)][string]$Path)

    $normalized = $Path.Trim()
    if (-not $normalized) {
        return ""
    }

    $normalized = $normalized.Replace("\", "/")
    while ($normalized.StartsWith("./")) {
        $normalized = $normalized.Substring(2)
    }

    return $normalized.ToLowerInvariant()
}

function Get-VisualReviewVariantPairs {
    param([Parameter(Mandatory = $true)][string]$ProjectRoot)

    $manifestPath = Join-Path $ProjectRoot ".mddev\project.json"
    $manifest = Get-JsonOrNull $manifestPath
    if (-not $manifest) {
        return @()
    }

    $visualReviewProp = $manifest.PSObject.Properties['visual_review']
    if (-not $visualReviewProp -or -not $visualReviewProp.Value) {
        return @()
    }

    $variantPairsProp = $visualReviewProp.Value.PSObject.Properties['variant_pairs']
    if (-not $variantPairsProp -or -not $variantPairsProp.Value) {
        return @()
    }

    $pairs = @()
    foreach ($entry in @($variantPairsProp.Value)) {
        if (-not $entry) {
            continue
        }

        $bgARel = Normalize-ResourceRelativePath ([string]$entry.bg_a)
        $bgBRel = Normalize-ResourceRelativePath ([string]$entry.bg_b)
        $mode = Get-SafeString $entry.mode "paired_bg"
        $sceneName = Get-SafeString $entry.scene ""
        $variantName = Get-SafeString $entry.variant ""

        if ([string]::IsNullOrWhiteSpace($bgARel) -or [string]::IsNullOrWhiteSpace($bgBRel)) {
            continue
        }

        $variantSlug = if ($variantName) { $variantName } else { "{0}_{1}" -f $bgARel, $bgBRel }
        $variantKey = ($variantSlug.ToLowerInvariant() -replace '[^a-z0-9_-]', '_')
        $pairs += [pscustomobject]@{
            scene = $sceneName
            variant = $variantName
            mode = $mode
            bg_a = $bgARel
            bg_b = $bgBRel
            bg_a_abs = Join-Path $ProjectRoot ("res\" + ($bgARel -replace '/', '\'))
            bg_b_abs = Join-Path $ProjectRoot ("res\" + ($bgBRel -replace '/', '\'))
            variant_key = $variantKey
        }
    }

    return @($pairs)
}

function Get-SceneRegressionSpec {
    param([Parameter(Mandatory = $true)][string]$ProjectRoot)

    $manifestPath = Join-Path $ProjectRoot ".mddev\project.json"
    $manifest = Get-JsonOrNull $manifestPath
    if (-not $manifest -or -not $manifest.scene_regression) {
        return [ordered]@{
            required = $false
            scenes = @()
            report_path = Join-Path $ProjectRoot "out\logs\scene_regression_report.json"
        }
    }

    $required = $false
    try {
        if ($null -ne $manifest.scene_regression.required) {
            $required = [bool]$manifest.scene_regression.required
        }
    } catch {
        $required = $false
    }

    return [ordered]@{
        required = $required
        scenes = @($manifest.scene_regression.scenes)
        report_path = Join-Path $ProjectRoot "out\logs\scene_regression_report.json"
    }
}

function Get-SceneRegressionStatus {
    param(
        [Parameter(Mandatory = $true)][string]$ProjectRoot,
        $RomIdentity
    )

    $spec = Get-SceneRegressionSpec -ProjectRoot $ProjectRoot
    $expectedScenes = @($spec.scenes)
    $reportPath = $spec.report_path
    $result = [ordered]@{
        required = [bool]$spec.required
        expected_scene_count = $expectedScenes.Count
        report_path = $reportPath
        report_present = $false
        complete = $false
        stale = $false
        rom_sha256 = $null
        report_scene_count = 0
        failed_scenes = @()
        missing_scenes = @()
    }

    if ($expectedScenes.Count -eq 0) {
        $result.complete = (-not $result.required)
        return $result
    }

    $report = Get-JsonOrNull $reportPath
    if (-not $report) {
        return $result
    }

    $result.report_present = $true
    $result.rom_sha256 = Get-SafeString $report.rom_sha256 ""
    $reportScenes = @()
    if ($report.PSObject.Properties['scenes']) {
        $reportScenes = @($report.scenes)
    } elseif ($report.PSObject.Properties['results']) {
        $reportScenes = @($report.results | ForEach-Object {
            [ordered]@{
                scene_key = Get-SafeString $_.scene_id ""
                status = if ((Get-SafeString $_.status "") -eq "passed" -and (Get-SafeString $_.capture_status "") -eq "ok") { "captured" } else { "failed" }
            }
        })
    }
    $result.report_scene_count = $reportScenes.Count

    $currentSha = if ($RomIdentity) { Get-SafeString $RomIdentity.rom_sha256 "" } else { "" }
    if ($currentSha -and $result.rom_sha256 -and ($currentSha -ne $result.rom_sha256)) {
        $result.stale = $true
    }

    $reportedKeys = @{}
    foreach ($scene in $reportScenes) {
        $sceneKey = Get-SafeString $scene.scene_key ""
        if ($sceneKey) {
            $reportedKeys[$sceneKey] = $true
        }
        if ((Get-SafeString $scene.status "") -ne "captured") {
            $result.failed_scenes += if ($sceneKey) { $sceneKey } else { "scene_desconhecida" }
        }
    }

    foreach ($expected in $expectedScenes) {
        $expectedKey = Get-SafeString $expected.scene_key ""
        if ($expectedKey -and (-not $reportedKeys.ContainsKey($expectedKey))) {
            $result.missing_scenes += $expectedKey
        }
    }

    $result.complete =
        (-not $result.stale) -and
        ($result.failed_scenes.Count -eq 0) -and
        ($result.missing_scenes.Count -eq 0) -and
        ($reportScenes.Count -ge $expectedScenes.Count)

    return $result
}

function Get-VisualPairContextsForResource {
    param(
        [object[]]$VariantPairs = @(),
        [Parameter(Mandatory = $true)][string]$ResourcePath
    )

    $normalizedResource = Normalize-ResourceRelativePath $ResourcePath
    $contexts = @()

    foreach ($pair in $VariantPairs) {
        if ((Get-SafeString $pair.mode "") -ne "paired_bg") {
            continue
        }

        if ($pair.bg_a -eq $normalizedResource) {
            $contexts += [pscustomobject]@{
                scene = $pair.scene
                variant = $pair.variant
                mode = $pair.mode
                variant_key = $pair.variant_key
                paired_bg_rel = $pair.bg_b
                paired_bg_abs = $pair.bg_b_abs
            }
        } elseif ($pair.bg_b -eq $normalizedResource) {
            $contexts += [pscustomobject]@{
                scene = $pair.scene
                variant = $pair.variant
                mode = $pair.mode
                variant_key = $pair.variant_key
                paired_bg_rel = $pair.bg_a
                paired_bg_abs = $pair.bg_a_abs
            }
        }
    }

    return @($contexts)
}

function Get-RomIdentityFromSession {
    param($Session)

    if (-not $Session) {
        return $null
    }

    $sessionRomPath = Resolve-ExistingPathOrNull $Session.rom_path
    $sessionSha = Get-SafeString $Session.rom_sha256 ""
    $sessionLastWriteUtc = $null
    $sessionLastWriteUtcValue = Get-DateOrNull $Session.rom_last_write_utc
    if ($sessionLastWriteUtcValue) {
        $sessionLastWriteUtc = $sessionLastWriteUtcValue.ToString("o")
    } else {
        $sessionLastWriteUtc = Get-SafeString $Session.rom_last_write_utc ""
    }
    $sessionSizeBytes = $null
    if ($null -ne $Session.rom_size_bytes -and [string]$Session.rom_size_bytes -ne "") {
        try {
            $sessionSizeBytes = [int64]$Session.rom_size_bytes
        } catch {
            $sessionSizeBytes = $null
        }
    }

    if (-not $sessionRomPath -and -not $sessionSha -and -not $sessionLastWriteUtc -and $null -eq $sessionSizeBytes) {
        return $null
    }

    return [ordered]@{
        path = $sessionRomPath
        size_bytes = $sessionSizeBytes
        last_write_utc = if ($sessionLastWriteUtc) { $sessionLastWriteUtc } else { $null }
        sha256 = if ($sessionSha) { $sessionSha } else { $null }
    }
}

function Get-DateOrNull {
    param($Value)

    if ($null -eq $Value) {
        return $null
    }

    if ($Value -is [datetimeoffset]) {
        return [datetimeoffset]$Value
    }

    if ($Value -is [datetime]) {
        return [datetimeoffset]$Value
    }

    $text = [string]$Value
    if ([string]::IsNullOrWhiteSpace($text)) {
        return $null
    }

    try {
        return [datetimeoffset]::Parse($text, [System.Globalization.CultureInfo]::InvariantCulture, [System.Globalization.DateTimeStyles]::RoundtripKind)
    } catch {
        try {
            return [datetimeoffset]::Parse($text, [System.Globalization.CultureInfo]::CurrentCulture, [System.Globalization.DateTimeStyles]::AllowWhiteSpaces)
        } catch {
            return $null
        }
    }
}

function Test-SessionCaptured {
    param($LaunchStatus)

    $status = Get-SafeString $LaunchStatus ""
    if (-not $status) {
        return $false
    }

    return $status -match '(?i)captur|closed|encerr|finaliz'
}

function Resolve-ExistingPathOrNull {
    param($PathValue)

    $text = Get-SafeString $PathValue ""
    if (-not $text) {
        return $null
    }

    try {
        if (Test-Path -LiteralPath $text) {
            return [System.IO.Path]::GetFullPath((Resolve-Path -LiteralPath $text).Path)
        }
    } catch {
    }

    return [System.IO.Path]::GetFullPath($text)
}

function Test-PathUnderRoot {
    param(
        $CandidatePath,
        $RootPath
    )

    $candidate = Resolve-ExistingPathOrNull $CandidatePath
    $root = Resolve-ExistingPathOrNull $RootPath
    if (-not $candidate -or -not $root) {
        return $false
    }

    $candidateFull = [System.IO.Path]::GetFullPath($candidate)
    $rootFull = [System.IO.Path]::GetFullPath($root).TrimEnd('\', '/')
    $rootWithSep = $rootFull + [System.IO.Path]::DirectorySeparatorChar

    return (
        $candidateFull.Equals($rootFull, [System.StringComparison]::OrdinalIgnoreCase) -or
        $candidateFull.StartsWith($rootWithSep, [System.StringComparison]::OrdinalIgnoreCase)
    )
}

function Get-AgentBootstrapStatus {
    param(
        [Parameter(Mandatory = $true)][string]$ProjectRoot,
        [Parameter(Mandatory = $false)][string]$WorkspaceRoot
    )

    $result = [ordered]@{
        agent_bootstrapped = $false
        bootstrap_degradado = $false
        reason = "missing_local_agent"
        canonical_version = Get-SafeString $env:SGDK_AGENT_CANONICAL_VERSION "desconhecida"
        local_version = Get-SafeString $env:SGDK_AGENT_LOCAL_VERSION ""
        local_agent_dir = Join-Path $ProjectRoot ".agent"
        local_agent = [ordered]@{
            path = Join-Path $ProjectRoot ".agent"
            present = $false
            ok = $false
            link_type = ""
            expected_target = ""
            actual_target = ""
            reason = ""
            physical_materialization = $false
            tracked_git_paths_count = 0
            tracked_git_path_examples = @()
        }
        agents_bridge = [ordered]@{
            path = ""
            present = $false
            ok = $false
            link_type = ""
            expected_target = ""
            actual_target = ""
            reason = ""
            tracked_git_paths_count = 0
            tracked_git_path_examples = @()
        }
        tracked_path_drift = @()
    }

    if ($env:SGDK_AGENT_BOOTSTRAPPED -eq "1") {
        $result.agent_bootstrapped = $true
    }
    if ($env:SGDK_AGENT_BOOTSTRAP_DEGRADED -eq "1") {
        $result.bootstrap_degradado = $true
        $result.reason = Get-SafeString $env:SGDK_AGENT_BOOTSTRAP_REASON "degradado"
    }

    $localAgentDir = $result.local_agent_dir
    if (-not (Test-Path -LiteralPath $localAgentDir -PathType Container)) {
        return $result
    }

    $result.agent_bootstrapped = $true
    if (-not $result.reason -or $result.reason -eq "missing_local_agent") {
        $result.reason = "existing"
    }

    $localManifestPath = Join-Path $localAgentDir "framework_manifest.json"
    $localArchitecturePath = Join-Path $localAgentDir "ARCHITECTURE.md"
    if (-not (Test-Path -LiteralPath $localManifestPath -PathType Leaf)) {
        $result.bootstrap_degradado = $true
        $result.reason = "missing_manifest"
        return $result
    }

    try {
        $localManifest = Get-Content -LiteralPath $localManifestPath -Raw | ConvertFrom-Json
        $localVersion = Get-SafeString $localManifest.framework_version "desconhecida"
        $result.local_version = $localVersion
    } catch {
        $result.bootstrap_degradado = $true
        $result.reason = "invalid_manifest"
        return $result
    }

    if (-not (Test-Path -LiteralPath $localArchitecturePath -PathType Leaf)) {
        $result.bootstrap_degradado = $true
        $result.reason = "missing_architecture"
        return $result
    }

    if ($WorkspaceRoot) {
        $canonicalAgentDir = Join-Path $WorkspaceRoot "tools\sgdk_wrapper\.agent"
        $canonicalManifestPath = Join-Path $canonicalAgentDir "framework_manifest.json"
        $canonicalArchitecturePath = Join-Path $canonicalAgentDir "ARCHITECTURE.md"

        $result.local_agent.expected_target = $canonicalAgentDir
        $result.local_agent.present = $true
        try {
            $localAgentItem = Get-Item -LiteralPath $localAgentDir -Force
            $result.local_agent.link_type = Get-SafeString $localAgentItem.LinkType ""
            $localTargets = @()
            if ($localAgentItem.Target) { $localTargets = @($localAgentItem.Target) }
            $localActualTarget = if ($localTargets.Count -gt 0) { [string]$localTargets[0] } else { "" }
            $result.local_agent.actual_target = $localActualTarget
            $localIsReparsePoint = ($localAgentItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0
            $localIsLink = $localIsReparsePoint -and ($result.local_agent.link_type -in @("Junction", "SymbolicLink"))
            $canonicalFull = [System.IO.Path]::GetFullPath($canonicalAgentDir)
            $localActualFull = if ($localActualTarget) { [System.IO.Path]::GetFullPath($localActualTarget) } else { "" }

            if (-not $localIsLink) {
                $result.local_agent.physical_materialization = $true
                $result.local_agent.reason = "physical_materialization"
                $result.bootstrap_degradado = $true
                if ($result.reason -eq "existing") { $result.reason = "local_agent_physical" }
            } elseif ($localActualFull -ne $canonicalFull) {
                $result.local_agent.reason = "target_mismatch"
                $result.bootstrap_degradado = $true
                if ($result.reason -eq "existing") { $result.reason = "local_agent_target_mismatch" }
            } else {
                $result.local_agent.ok = $true
                $result.local_agent.reason = "ok"
            }
        } catch {
            $result.local_agent.reason = "inspection_failed"
            $result.bootstrap_degradado = $true
            if ($result.reason -eq "existing") { $result.reason = "local_agent_inspection_failed" }
        }

        try {
            $workspaceFull = [System.IO.Path]::GetFullPath($WorkspaceRoot).TrimEnd('\')
            $projectFull = [System.IO.Path]::GetFullPath($ProjectRoot).TrimEnd('\')
            if (($projectFull + '\').StartsWith($workspaceFull + '\', [System.StringComparison]::OrdinalIgnoreCase)) {
                $projectRelative = ($projectFull.Substring($workspaceFull.Length).TrimStart('\') -replace '\\', '/')
                if ($projectRelative) {
                    $trackedLocalAgentPaths = @(git -C $WorkspaceRoot ls-files "$projectRelative/.agent/**" 2>$null)
                    $result.local_agent.tracked_git_paths_count = $trackedLocalAgentPaths.Count
                    $result.local_agent.tracked_git_path_examples = @($trackedLocalAgentPaths | Select-Object -First 8)
                    if ($trackedLocalAgentPaths.Count -gt 0) {
                        $result.bootstrap_degradado = $true
                        if ($result.reason -eq "existing") { $result.reason = "local_agent_tracked_content" }
                        if ($result.local_agent.reason -eq "ok") { $result.local_agent.reason = "tracked_content" }
                    }
                }
            }
        } catch {
            # Git may be unavailable in export-only environments; link shape still carries the primary gate.
        }

        # Repo-native skill discovery bridge. This should be a junction to the canonical skills tree.
        $bridgePath = Join-Path $WorkspaceRoot ".agents\skills"
        $expectedTarget = Join-Path $WorkspaceRoot "tools\sgdk_wrapper\.agent\skills"
        $result.agents_bridge.path = $bridgePath
        $result.agents_bridge.expected_target = $expectedTarget
        if (Test-Path -LiteralPath $bridgePath) {
            $result.agents_bridge.present = $true
            try {
                $bridgeItem = Get-Item -LiteralPath $bridgePath -Force
                $result.agents_bridge.link_type = Get-SafeString $bridgeItem.LinkType ""
                $targets = @()
                if ($bridgeItem.Target) { $targets = @($bridgeItem.Target) }
                $actualTarget = if ($targets.Count -gt 0) { [string]$targets[0] } else { "" }
                $result.agents_bridge.actual_target = $actualTarget

                $isReparsePoint = ($bridgeItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0
                $isLink = $isReparsePoint -and ($result.agents_bridge.link_type -in @("Junction", "SymbolicLink"))
                $expectedFull = [System.IO.Path]::GetFullPath($expectedTarget)
                $actualFull = if ($actualTarget) { [System.IO.Path]::GetFullPath($actualTarget) } else { "" }

                if (-not $isLink) {
                    $result.bootstrap_degradado = $true
                    $result.reason = "agents_bridge_broken"
                    $result.agents_bridge.reason = "not_a_link"
                }
                elseif ($actualFull -ne $expectedFull) {
                    $result.bootstrap_degradado = $true
                    $result.reason = "agents_bridge_broken"
                    $result.agents_bridge.reason = "target_mismatch"
                }
                else {
                    $result.agents_bridge.ok = $true
                    $result.agents_bridge.reason = "ok"
                }
            } catch {
                $result.bootstrap_degradado = $true
                $result.reason = "agents_bridge_broken"
                $result.agents_bridge.reason = "inspection_failed"
            }
        } else {
            $result.agents_bridge.present = $false
            $result.agents_bridge.ok = $false
            $result.agents_bridge.reason = "missing"
        }

        try {
            $trackedBridgePaths = @(git -C $WorkspaceRoot ls-files ".agents/skills/**" 2>$null)
            $result.agents_bridge.tracked_git_paths_count = $trackedBridgePaths.Count
            $result.agents_bridge.tracked_git_path_examples = @($trackedBridgePaths | Select-Object -First 8)
            if ($trackedBridgePaths.Count -gt 0) {
                $result.bootstrap_degradado = $true
                if ($result.reason -eq "existing") { $result.reason = "agents_bridge_tracked_content" }
                if ($result.agents_bridge.reason -eq "ok") { $result.agents_bridge.reason = "tracked_content" }
            }
        } catch {
            # Git may be unavailable in export-only environments; link shape still carries the primary gate.
        }

        if (Test-Path -LiteralPath $canonicalManifestPath -PathType Leaf) {
            try {
                $canonicalManifest = Get-Content -LiteralPath $canonicalManifestPath -Raw | ConvertFrom-Json
                $canonicalVersion = Get-SafeString $canonicalManifest.framework_version $result.canonical_version
                $result.canonical_version = $canonicalVersion
                if ($result.local_version -and $canonicalVersion -and $result.local_version -ne $canonicalVersion) {
                    $result.bootstrap_degradado = $true
                    $result.reason = "version_mismatch"
                }
                if ($canonicalManifest.tracked_paths) {
                    foreach ($trackedPath in $canonicalManifest.tracked_paths) {
                        $localTracked = Join-Path $localAgentDir ([string]$trackedPath)
                        $canonicalTracked = Join-Path $canonicalAgentDir ([string]$trackedPath)
                        if (-not (Test-Path -LiteralPath $localTracked)) {
                            $result.bootstrap_degradado = $true
                            $result.reason = "missing_tracked_path"
                            break
                        }
                        if (Test-Path -LiteralPath $canonicalTracked) {
                            $localTrackedHash = Get-AgentPathDigestOrNull -Path $localTracked
                            $canonicalTrackedHash = Get-AgentPathDigestOrNull -Path $canonicalTracked
                            if ($localTrackedHash -and $canonicalTrackedHash -and $localTrackedHash -ne $canonicalTrackedHash) {
                                $result.tracked_path_drift += [ordered]@{
                                    path = [string]$trackedPath
                                    local_hash = $localTrackedHash
                                    canonical_hash = $canonicalTrackedHash
                                }
                                $result.bootstrap_degradado = $true
                                if ($result.reason -eq "existing") {
                                    $result.reason = "tracked_path_drift"
                                }
                            }
                        }
                    }
                }
            } catch {
                if (-not $result.bootstrap_degradado) {
                    $result.bootstrap_degradado = $true
                    $result.reason = "canonical_manifest_invalid"
                }
            }
        }

        if ((Test-Path -LiteralPath $canonicalArchitecturePath -PathType Leaf) -and (Test-Path -LiteralPath $localArchitecturePath -PathType Leaf)) {
            $localHash = Get-NormalizedTextHashOrNull -Path $localArchitecturePath
            $canonicalHash = Get-NormalizedTextHashOrNull -Path $canonicalArchitecturePath
            if ($localHash -ne $canonicalHash -and -not $result.bootstrap_degradado) {
                $result.bootstrap_degradado = $true
                $result.reason = "architecture_drift"
            }
        }
    }

    return $result
}

function Normalize-AssetId {
    param([Parameter(Mandatory = $true)][string]$Value)

    $normalized = $Value.ToLowerInvariant() -replace '[^a-z0-9_-]', '_'
    $normalized = $normalized.Trim('_')
    if ([string]::IsNullOrWhiteSpace($normalized)) {
        return "asset"
    }
    return $normalized
}

function Get-ResourceEntriesForChangelog {
    param([Parameter(Mandatory = $true)][string]$ProjectRoot)

    $entries = @()
    $resRoot = Join-Path $ProjectRoot "res"
    if (-not (Test-Path -LiteralPath $resRoot -PathType Container)) {
        return $entries
    }

    $seen = @{}
    $resFiles = Get-ChildItem -LiteralPath $resRoot -Recurse -Filter "*.res" -File -ErrorAction SilentlyContinue
    foreach ($resFile in $resFiles) {
        $baseDir = Split-Path $resFile.FullName
        foreach ($line in Get-Content -LiteralPath $resFile.FullName) {
            if ($line -match '^\s*(IMAGE|SPRITE|MAP|TILESET|PALETTE|BIN|OBJECT)\s+([A-Za-z0-9_]+)\s+"([^"]+)"') {
                $resourceKind = $matches[1]
                $resourceName = $matches[2]
                $assetPath = Join-Path $baseDir $matches[3]
                if (-not (Test-Path -LiteralPath $assetPath -PathType Leaf)) {
                    continue
                }

                $key = "{0}|{1}" -f $resourceName, $assetPath.ToLowerInvariant()
                if ($seen.ContainsKey($key)) {
                    continue
                }
                $seen[$key] = $true

                $entries += [pscustomobject]@{
                    asset_id = Normalize-AssetId $resourceName
                    resource_name = $resourceName
                    resource_kind = $resourceKind
                    source_path = $assetPath
                    source_identity = Get-FileIdentity -Path $assetPath
                }
            }
        }
    }

    return $entries
}

function Get-LatestVersionMetadata {
    param(
        [Parameter(Mandatory = $true)][string]$Root,
        [Parameter(Mandatory = $true)][string]$Prefix,
        [Parameter(Mandatory = $true)][string]$MetaName
    )

    if (-not (Test-Path -LiteralPath $Root -PathType Container)) {
        return $null
    }

    $matchesFound = @()
    foreach ($dir in Get-ChildItem -LiteralPath $Root -Directory -ErrorAction SilentlyContinue) {
        if ($dir.Name -match "^$Prefix(\d{3})$") {
            $metaPath = Join-Path $dir.FullName $MetaName
            if (-not (Test-Path -LiteralPath $metaPath -PathType Leaf)) {
                continue
            }

            $meta = Get-JsonOrNull $metaPath
            if ($meta) {
                $matchesFound += [pscustomobject]@{
                    version = $dir.Name
                    ordinal = [int]$matches[1]
                    dir = $dir.FullName
                    meta = $meta
                    meta_path = $metaPath
                }
            }
        }
    }

    if (-not $matchesFound) {
        return $null
    }

    return $matchesFound | Sort-Object ordinal -Descending | Select-Object -First 1
}

function Get-ChangelogStatus {
    param(
        [Parameter(Mandatory = $true)][string]$ProjectRoot,
        [Parameter(Mandatory = $false)]$RomIdentity
    )

    $changelogRoot = Join-Path $ProjectRoot "doc\changelog"
    $assetsRoot = Join-Path $changelogRoot "assets"
    $romsRoot = Join-Path $changelogRoot "roms"
    $changelogPath = Join-Path $changelogRoot "changelog.md"

    $result = [ordered]@{
        changelog_path = $changelogPath
        present = (Test-Path -LiteralPath $changelogPath -PathType Leaf)
        assets_missing = @()
        assets_outdated = @()
        rom_outdated = $false
        latest_build_version = $null
        latest_build_meta_path = $null
        latest_build_sha256 = $null
    }

    if (-not $result.present) {
        return $result
    }

    foreach ($entry in (Get-ResourceEntriesForChangelog -ProjectRoot $ProjectRoot)) {
        if (-not $entry.source_identity) {
            continue
        }

        $assetRoot = Join-Path $assetsRoot $entry.asset_id
        $latestAsset = Get-LatestVersionMetadata -Root $assetRoot -Prefix "v" -MetaName "meta.json"
        if (-not $latestAsset) {
            $result.assets_missing += [ordered]@{
                asset_id = $entry.asset_id
                resource_name = $entry.resource_name
                source_path = $entry.source_path
            }
            continue
        }

        $metaSha = Get-SafeString $latestAsset.meta.source_sha256 ""
        if (-not $metaSha -or $metaSha -ne $entry.source_identity.sha256) {
            $result.assets_outdated += [ordered]@{
                asset_id = $entry.asset_id
                resource_name = $entry.resource_name
                source_path = $entry.source_path
                latest_version = $latestAsset.version
            }
        }
    }

    if ($RomIdentity) {
        $latestBuild = Get-LatestVersionMetadata -Root $romsRoot -Prefix "build_v" -MetaName "build_meta.json"
        if (-not $latestBuild) {
            $result.rom_outdated = $true
        } else {
            $result.latest_build_version = $latestBuild.version
            $result.latest_build_meta_path = $latestBuild.meta_path
            $result.latest_build_sha256 = Get-SafeString $latestBuild.meta.rom_sha256 ""
            if ($result.latest_build_sha256 -ne $RomIdentity.sha256) {
                $result.rom_outdated = $true
            }
        }
    }

    return $result
}

function New-CanonicalValidationSummary {
    param(
        [Parameter(Mandatory = $true)]$Results,
        $RuntimeMetrics,
        $EmulatorSession,
        $SceneRegressionStatus,
        $AudioValidationStatus,
        $ChangelogStatus,
        $SceneContractCompileStatus,
        $ResGraphStatus,
        $FreshnessAuditStatus,
        $SceneCloseoutGateStatus
    )

    $runtimeSceneId = $null
    if ($RuntimeMetrics -and $RuntimeMetrics.PSObject.Properties['scene_id']) {
        try {
            $runtimeSceneId = [int]$RuntimeMetrics.scene_id
        } catch {
            $runtimeSceneId = $RuntimeMetrics.scene_id
        }
    }

    $sceneRegressionSnapshot = [ordered]@{
        required = if ($SceneRegressionStatus) { [bool]$SceneRegressionStatus.required } else { $false }
        ready = [bool]$Results.status_panel.scene_regression_ready
        report_present = if ($SceneRegressionStatus) { [bool]$SceneRegressionStatus.report_present } else { $false }
        stale = if ($SceneRegressionStatus) { [bool]$SceneRegressionStatus.stale } else { $false }
        expected_scene_count = if ($SceneRegressionStatus) { [int]$SceneRegressionStatus.expected_scene_count } else { 0 }
        report_scene_count = if ($SceneRegressionStatus) { [int]$SceneRegressionStatus.report_scene_count } else { 0 }
        failed_scenes = if ($SceneRegressionStatus) { @($SceneRegressionStatus.failed_scenes) } else { @() }
        missing_scenes = if ($SceneRegressionStatus) { @($SceneRegressionStatus.missing_scenes) } else { @() }
    }

    $audioState = "not_required"
    if ($AudioValidationStatus -and $AudioValidationStatus.required) {
        if (-not $AudioValidationStatus.report_present) {
            $audioState = "missing"
        } elseif ($AudioValidationStatus.stale) {
            $audioState = "stale"
        } elseif ($AudioValidationStatus.pass) {
            $audioState = "ok"
        } else {
            $audioState = "failed"
        }
    }

    $emulatorState = "missing"
    if ([bool]$Results.status_panel.emulator_evidence_stale) {
        $emulatorState = "stale"
    } elseif ([bool]$Results.status_panel.blastem_gate) {
        $emulatorState = "blastem_gate_ok"
    } elseif ([bool]$Results.status_panel.testado_em_emulador) {
        $emulatorState = "captured_no_blastem_gate"
    }

    return [ordered]@{
        schema_version = "1.0.0"
        generated_from = "validation_report"
        build = [ordered]@{
            rom_present = [bool]$Results.status_panel.buildado
            qa_axis = $Results.qa_axes.build
        }
        runtime_capture = [ordered]@{
            present = [bool]$Results.status_panel.runtime_capture_present
            stale = [bool]$Results.status_panel.emulator_evidence_stale
            samples_recorded = [int]$Results.evidence.runtime_samples_recorded
            scene_id = $runtimeSceneId
            frame_stability = $Results.runtime_profile.frame_stability
            sprite_pressure = $Results.runtime_profile.sprite_pressure
            fx_load = $Results.runtime_profile.fx_load
            perceptual_quality = $Results.runtime_profile.perceptual_quality
        }
        emulator = [ordered]@{
            state = $emulatorState
            qa_axis = $Results.qa_axes.boot_emulador
            reference = $Results.evidence.emulator_reference
            blastem_gate = [bool]$Results.status_panel.blastem_gate
            fresh_sram_confirmed = $Results.evidence.emulator_fresh_sram_confirmed
        }
        scene_regression = $sceneRegressionSnapshot
        audio_validation = [ordered]@{
            ready = [bool]$Results.status_panel.audio_validation_ready
            state = $audioState
            required = if ($AudioValidationStatus) { [bool]$AudioValidationStatus.required } else { $false }
            report_present = if ($AudioValidationStatus) { [bool]$AudioValidationStatus.report_present } else { $false }
            stale = if ($AudioValidationStatus) { [bool]$AudioValidationStatus.stale } else { $false }
        }
        changelog = [ordered]@{
            ready = [bool]$Results.status_panel.changelog_ready
            present = if ($ChangelogStatus) { [bool]$ChangelogStatus.present } else { $false }
            rom_outdated = if ($ChangelogStatus) { [bool]$ChangelogStatus.rom_outdated } else { $false }
            assets_missing = if ($ChangelogStatus) { @($ChangelogStatus.assets_missing) } else { @() }
            assets_outdated = if ($ChangelogStatus) { @($ChangelogStatus.assets_outdated) } else { @() }
        }
        gates = [ordered]@{
            validado_budget = [bool]$Results.status_panel.validado_budget
            visual_lab_aprovado = [bool]$Results.status_panel.visual_lab_aprovado
            gameplay_rom_aprovada = [bool]$Results.status_panel.gameplay_rom_aprovada
            ready_for_aaa = [bool]$Results.status_panel.ready_for_aaa
        }
        wrapper_reports = [ordered]@{
            scene_contract_compile = [ordered]@{
                report_present = if ($SceneContractCompileStatus) { [bool]$SceneContractCompileStatus.report_present } else { $false }
                stale = if ($SceneContractCompileStatus) { [bool]$SceneContractCompileStatus.stale } else { $false }
                generated_at = if ($SceneContractCompileStatus) { $SceneContractCompileStatus.generated_at } else { $null }
                latest_dependency_utc = if ($SceneContractCompileStatus) { $SceneContractCompileStatus.latest_dependency_utc } else { $null }
                report_path = if ($SceneContractCompileStatus) { $SceneContractCompileStatus.report_path } else { $null }
            }
            res_graph = [ordered]@{
                report_present = if ($ResGraphStatus) { [bool]$ResGraphStatus.report_present } else { $false }
                stale = if ($ResGraphStatus) { [bool]$ResGraphStatus.stale } else { $false }
                generated_at = if ($ResGraphStatus) { $ResGraphStatus.generated_at } else { $null }
                latest_dependency_utc = if ($ResGraphStatus) { $ResGraphStatus.latest_dependency_utc } else { $null }
                report_path = if ($ResGraphStatus) { $ResGraphStatus.report_path } else { $null }
            }
            freshness_audit = [ordered]@{
                report_present = if ($FreshnessAuditStatus) { [bool]$FreshnessAuditStatus.report_present } else { $false }
                stale = if ($FreshnessAuditStatus) { [bool]$FreshnessAuditStatus.stale } else { $false }
                generated_at = if ($FreshnessAuditStatus) { $FreshnessAuditStatus.generated_at } else { $null }
                latest_dependency_utc = if ($FreshnessAuditStatus) { $FreshnessAuditStatus.latest_dependency_utc } else { $null }
                report_path = if ($FreshnessAuditStatus) { $FreshnessAuditStatus.report_path } else { $null }
            }
            scene_closeout_gate = [ordered]@{
                report_present = if ($SceneCloseoutGateStatus) { [bool]$SceneCloseoutGateStatus.report_present } else { $false }
                stale = if ($SceneCloseoutGateStatus) { [bool]$SceneCloseoutGateStatus.stale } else { $false }
                generated_at = if ($SceneCloseoutGateStatus) { $SceneCloseoutGateStatus.generated_at } else { $null }
                latest_dependency_utc = if ($SceneCloseoutGateStatus) { $SceneCloseoutGateStatus.latest_dependency_utc } else { $null }
                report_path = if ($SceneCloseoutGateStatus) { $SceneCloseoutGateStatus.report_path } else { $null }
            }
        }
        blocking_status_codes = @($Results.blocking_statuses | Select-Object -Unique)
        source_artifacts = @($Results.status_panel.source_artifacts)
    }
}

function Resolve-SprInitExValue {
    param([Parameter(Mandatory = $true)][string]$ProjectRoot)

    $srcRoot = Join-Path $ProjectRoot "src"
    if (-not (Test-Path -LiteralPath $srcRoot -PathType Container)) {
        return $null
    }

    foreach ($file in Get-ChildItem -LiteralPath $srcRoot -Recurse -File -Include *.c,*.h -ErrorAction SilentlyContinue) {
        $content = Get-Content -LiteralPath $file.FullName -Raw
        if ($content -match 'SPR_initEx\s*\(\s*([A-Za-z_][A-Za-z0-9_]*|\d+)\s*\)') {
            $token = $matches[1]
            if ($token -match '^\d+$') {
                return [ordered]@{ value = [int]$token; file = $file.FullName; token = $token }
            }

            $definePattern = "(?m)^\s*#define\s+$([regex]::Escape($token))\s+(\d+)\b"
            if ($content -match $definePattern) {
                return [ordered]@{ value = [int]$matches[1]; file = $file.FullName; token = $token }
            }
        }
    }

    return $null
}

function Get-BudgetDocumentationMismatch {
    param([Parameter(Mandatory = $true)][string]$ProjectRoot)

    $runtimeSprInit = Resolve-SprInitExValue -ProjectRoot $ProjectRoot
    if (-not $runtimeSprInit) {
        return $null
    }

    $docPaths = @(
        (Join-Path $ProjectRoot "doc\hardware_budget_review.md"),
        (Join-Path $ProjectRoot "doc\10-memory-bank.md")
    )

    $mismatches = @()
    foreach ($docPath in $docPaths) {
        if (-not (Test-Path -LiteralPath $docPath -PathType Leaf)) {
            continue
        }

        $content = Get-Content -LiteralPath $docPath -Raw
        $docValues = @([regex]::Matches($content, 'SPR_initEx\s*\(?\s*(\d+)\s*\)?') | ForEach-Object { [int]$_.Groups[1].Value })
        if ($docValues.Count -eq 0) {
            continue
        }

        if ($runtimeSprInit.value -notin $docValues) {
            $mismatches += [ordered]@{
                file = $docPath
                runtime_spr_init_ex = $runtimeSprInit.value
                documented_values = @($docValues | Select-Object -Unique)
            }
        }
    }

    if ($mismatches.Count -eq 0) {
        return $null
    }

    return [ordered]@{
        runtime = $runtimeSprInit
        mismatches = $mismatches
    }
}

function Set-RuntimeProfileFromMetrics($results, $runtimeMetrics, $thresholds, $runtimePath) {
    if (-not $runtimeMetrics) {
        return
    }

    $samplesRecorded = [int]($runtimeMetrics.samples_recorded | ForEach-Object { $_ })
    if ($samplesRecorded -le 0) {
        Add-Detail $results "RUNTIME_CAPTURE" "WARNING" "Arquivo de runtime existe, mas nao contem amostras validas." "runtime" $runtimePath
        $results.summary.warnings++
        return
    }

    $budgetThreshold = [double]$runtimeMetrics.budget_threshold
    $cpuLoadMax = [double]$runtimeMetrics.cpu_load_max
    $cpuLoadP95 = [double]$runtimeMetrics.frame_cpu_ratio_p95
    $cpuLoadJitterMax = [double]$runtimeMetrics.cpu_load_jitter_max
    $overBudgetFrames = [double]$runtimeMetrics.over_budget_frames
    $overBudgetRatio = if ($samplesRecorded -gt 0) { $overBudgetFrames / $samplesRecorded } else { 0 }
    $maxScanlineSprites = [int]$runtimeMetrics.max_scanline_sprites
    $fxPeakConcurrency = [int]$runtimeMetrics.fx_peak_concurrency
    $perceptual = $runtimeMetrics.perceptual_check
    $perceptualSum = 0

    foreach ($axis in @("fluidez", "leitura", "naturalidade", "impacto")) {
        if ($null -ne $perceptual.$axis) {
            $perceptualSum += [int]$perceptual.$axis
        }
    }

    $results.runtime_profile.frame_stability =
        if (
            $overBudgetRatio -le [double]$thresholds.frame_stability.stable_over_budget_ratio_max -and
            $cpuLoadMax -le [double]$thresholds.frame_stability.stable_cpu_load_max -and
            $cpuLoadP95 -le [double]$thresholds.frame_stability.stable_cpu_load_p95_max -and
            $cpuLoadJitterMax -le [double]$thresholds.frame_stability.stable_cpu_jitter_max
        ) { "estavel" } else { "instavel" }

    $results.runtime_profile.sprite_pressure =
        if ($maxScanlineSprites -le [int]$thresholds.sprite_pressure.low_max) { "baixo" }
        elseif ($maxScanlineSprites -le [int]$thresholds.sprite_pressure.medium_max) { "medio" }
        elseif ($maxScanlineSprites -le [int]$thresholds.sprite_pressure.high_max) { "alto" }
        else { "critico" }

    $results.runtime_profile.fx_load =
        if ($fxPeakConcurrency -le [int]$thresholds.fx_load.light_max) { "leve" }
        elseif ($fxPeakConcurrency -le [int]$thresholds.fx_load.heavy_max) { "moderado" }
        else { "pesado" }

    $results.runtime_profile.perceptual_quality =
        if ($perceptualSum -ge [int]$thresholds.perceptual_quality.aaa_min_score) { "aaa" }
        elseif ($perceptualSum -ge [int]$thresholds.perceptual_quality.acceptable_min_score) { "aceitavel" }
        elseif ($perceptualSum -gt 0) { "fraco" }
        else { "nao_medido" }

    Add-Detail $results "RUNTIME_CAPTURE" "INFO" ("Runtime capturado com {0} amostras, pico CPU {1}, scanline {2}, FX {3}." -f $samplesRecorded, $cpuLoadMax, $maxScanlineSprites, $fxPeakConcurrency) "runtime" $runtimePath @{
        overBudgetRatio = [math]::Round($overBudgetRatio, 4)
        cpuLoadP95 = $cpuLoadP95
        budgetThreshold = $budgetThreshold
    }

    if ($maxScanlineSprites -gt [int]$thresholds.sprite_pressure.critical_block_above) {
        $msg = "Pressao de sprite critica: $maxScanlineSprites sprites na mesma scanline."
        Write-Log $msg "ERROR"
        $results.summary.errors++
        Add-Detail $results "RUNTIME_SPRITE_PRESSURE" "ERROR" $msg "runtime" $runtimePath
    }
}

Write-Log "--- Starting Resource Validation Suite ---"
$results = @{
    timestamp = Get-Date -Format "o"
    summary = @{ errors = 0; warnings = 0; checked = 0; recovered = 0; closeout_gate = [bool]$CloseoutGate }
    blocking_statuses = @()
    risk_taxonomy = New-RiskTaxonomy
    validator_config = @{
        indexed_transparency_audit = @{
            visible_warn_min_pixels = $Index0VisibleWarnMinPixelsSetting
            visible_warn_min_ratio = $Index0VisibleWarnMinRatioSetting
            visible_error_min_pixels = $Index0VisibleErrorMinPixelsSetting
            visible_error_min_ratio = $Index0VisibleErrorMinRatioSetting
            transparent_coverage_info_min_pixels = $Index0TransparentCoverageInfoMinPixelsSetting
            transparent_coverage_info_min_ratio = $Index0TransparentCoverageInfoMinRatioSetting
        }
    }
    runtime_profile = @{
        frame_stability = if ($env:SGDK_FRAME_STABILITY) { $env:SGDK_FRAME_STABILITY } else { "nao_medido" }
        sprite_pressure = if ($env:SGDK_SPRITE_PRESSURE) { $env:SGDK_SPRITE_PRESSURE } else { "nao_medido" }
        fx_load = if ($env:SGDK_FX_LOAD) { $env:SGDK_FX_LOAD } else { "nao_medido" }
        perceptual_quality = if ($env:SGDK_PERCEPTUAL_QUALITY) { $env:SGDK_PERCEPTUAL_QUALITY } else { "nao_medido" }
    }
    qa_axes = @{
        build = "falha"
        validation_report = "com_erros"
        boot_emulador = "nao_testado"
        gameplay_basico = if ($env:SGDK_GAMEPLAY_BASICO) { $env:SGDK_GAMEPLAY_BASICO } else { "nao_testado" }
        performance = if ($env:SGDK_PERFORMANCE_STATUS) { $env:SGDK_PERFORMANCE_STATUS } else { "nao_testado" }
        audio = if ($env:SGDK_AUDIO_STATUS) { $env:SGDK_AUDIO_STATUS } else { "nao_testado" }
        hardware_real = if ($env:SGDK_HARDWARE_REAL_STATUS) { $env:SGDK_HARDWARE_REAL_STATUS } else { "nao_testado" }
        visual_elite = if ($env:SGDK_VISUAL_ELITE_STATUS) { $env:SGDK_VISUAL_ELITE_STATUS } else { "nao_medido" }
    }
    status_panel = @{
        documentado = $false
        implementado = $false
        buildado = $false
        testado_em_emulador = $false
        validado_budget = $false
        audio_validation_ready = $false
        agent_bootstrapped = $false
        bootstrap_degradado = $false
        placeholder = $false
        parcial = $false
        futuro_arquitetural = $false
        runtime_capture_present = $false
        blastem_gate = $false
        emulator_evidence_stale = $false
        scene_regression_ready = $false
        visual_gate_ready = $false
        visual_lab_aprovado = $false
        gameplay_rom_aprovada = $false
        changelog_ready = $false
        ready_for_aaa = $false
        closing_blockers = @()
        primary_source = "validation_report"
        source_artifacts = @()
    }
    evidence = @{
        validation_report_path = $REPORT_FILE
        runtime_metrics_path = $null
        emulator_session_path = $null
        rom_path = $null
        runtime_samples_recorded = 0
        emulator_reference = "nenhum"
        memory_artifact = $null
        rom_identity = $null
        emulator_session_rom_identity = $null
        emulator_session_rom_path = $null
        emulator_session_timestamp = $null
        emulator_evidence_reason = "nao_avaliado"
        emulator_sandbox_root = $null
        emulator_save_root = $null
        emulator_log_path = $null
        emulator_fresh_sram_confirmed = $null
        emulator_outside_sandbox_candidate = $null
        emulator_stale_sandbox_candidate = $null
        scene_regression_report_path = $null
        scene_regression_status = $null
        audio_validation_report_path = $null
        audio_validation_status = $null
        agent_bootstrap = $null
        visual_aesthetic_report_path = $null
        changelog_status = $null
    }
    visual_profile = @{
        status = "nao_medido"
        analyzed_assets = 0
        elite_ready = 0
        needs_review = 0
        rework = 0
        critical_rework = 0
        assets = @()
        benchmark = $null
    }
    details = @()
}

foreach ($setting in $IndexedTransparencyAuditSettings) {
    if ($setting.source -eq "default_invalid_env") {
        $msg = "Override invalido para $($setting.env): valor bruto '$($setting.raw)' ignorado; usando default $($setting.default)."
        Write-Log $msg "WARN"
        $results.summary.warnings++
        Add-Detail $results "INDEX0_THRESHOLD_INVALID_OVERRIDE" "WARNING" $msg "validator_config" $REPORT_FILE @{
            env = $setting.env
            kind = $setting.kind
            raw = $setting.raw
            default = $setting.default
            effective = $setting.effective
        }
    }
}

$magickPath = Get-MagickPath
$fixScript = Join-Path $PSScriptRoot "ensure_safe_image.ps1"
$runtimeMetricsPath = Join-Path $LOG_DIR "runtime_metrics.json"
$emulatorSessionPath = Join-Path $LOG_DIR "emulator_session.json"
$visualAestheticReportPath = Join-Path $LOG_DIR "visual_aesthetic_report.json"
$visualDeliveryGateReportPath = Join-Path $LOG_DIR "visual_delivery_gate_report.json"
$sceneRegressionReportPath = Join-Path $LOG_DIR "scene_regression_report.json"
$runtimeThresholdsPath = Join-Path $PSScriptRoot "runtime_thresholds.json"
$aestheticAnalyzerPath = $null
$visualLabAnalyzerPath = $null
$visualLabManifestPath = Join-Path $pwd.Path "res\data\visual_lab_case.json"
$aestheticReferenceProfile = if ($env:SGDK_AESTHETIC_REFERENCE_PROFILE) { $env:SGDK_AESTHETIC_REFERENCE_PROFILE } else { "generic-megadrive-elite" }
$pythonPath = Get-PythonPath
$visualAnalyses = @()
$visualLabBenchmark = $null
$visualAnalyzerAvailable = $false
$visualDeliveryGateReport = $null
$runtimeMetrics = $null
$emulatorSession = $null
$runtimeThresholds = $null
$workspaceRoot = Resolve-WorkspaceRoot $pwd.Path
$visualReviewVariantPairs = Get-VisualReviewVariantPairs -ProjectRoot $pwd.Path
$sceneRegressionStatus = $null
$audioValidationReportPath = Join-Path $LOG_DIR "audio_validation_report.json"
$audioValidationReport = $null
$audioDeclarations = @()

if ($workspaceRoot) {
    $aestheticAnalyzerPath = Join-Path $workspaceRoot "tools\image-tools\analyze_aesthetic.py"
    $visualLabAnalyzerPath = Join-Path $workspaceRoot "tools\image-tools\analyze_visual_lab_case.py"
    if ($pythonPath -and (Test-Path -LiteralPath $aestheticAnalyzerPath)) {
        $visualAnalyzerAvailable = $true
    }
}

if (Test-Path -LiteralPath $runtimeThresholdsPath) {
    try {
        $runtimeThresholds = Get-Content -LiteralPath $runtimeThresholdsPath -Raw | ConvertFrom-Json
    } catch {
        Write-Log ("Falha ao carregar runtime_thresholds.json: {0}" -f $_.Exception.Message) "WARN"
        $results.summary.warnings++
        Add-Detail $results "RUNTIME_THRESHOLDS" "WARNING" "Falha ao carregar thresholds de runtime." "runtime" $runtimeThresholdsPath
    }
}

if (Test-Path -LiteralPath $runtimeMetricsPath) {
    try {
        $runtimeMetrics = Get-Content -LiteralPath $runtimeMetricsPath -Raw | ConvertFrom-Json
    } catch {
        Write-Log ("Falha ao carregar runtime_metrics.json: {0}" -f $_.Exception.Message) "WARN"
        $results.summary.warnings++
        Add-Detail $results "RUNTIME_CAPTURE" "WARNING" "Falha ao carregar runtime_metrics.json." "runtime" $runtimeMetricsPath
    }
}

if (Test-Path -LiteralPath $emulatorSessionPath) {
    try {
        $emulatorSession = Get-Content -LiteralPath $emulatorSessionPath -Raw | ConvertFrom-Json
    } catch {
        Write-Log ("Falha ao carregar emulator_session.json: {0}" -f $_.Exception.Message) "WARN"
        $results.summary.warnings++
        Add-Detail $results "EMULATOR_SESSION" "WARNING" "Falha ao carregar emulator_session.json." "runtime" $emulatorSessionPath
    }
}

if (Test-Path -LiteralPath $visualDeliveryGateReportPath) {
    try {
        $visualDeliveryGateReport = Get-Content -LiteralPath $visualDeliveryGateReportPath -Raw | ConvertFrom-Json
    } catch {
        $msg = ("Falha ao carregar visual_delivery_gate_report.json: {0}" -f $_.Exception.Message)
        Write-Log $msg "WARN"
        $results.summary.warnings++
        Add-Detail $results "VISUAL_DELIVERY_GATE" "WARNING" $msg "visual" $visualDeliveryGateReportPath
    }
}

$resFiles = Get-ChildItem -LiteralPath (Join-Path $pwd.Path "res") -Filter "*.res" -Recurse -ErrorAction SilentlyContinue
if (-not $resFiles) {
    Write-Log "Nenhum arquivo .res encontrado em res/ (projeto pode não ter recursos)." "INFO"
} else {
    Write-Log "Encontrados $($resFiles.Count) arquivo(s) .res para validar." "INFO"
}
$audioDeclarations = Get-DeclaredAudioEntries -resFiles $resFiles

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
        $imageOptionTokens = @()
        $imageCompression = $null
        $imageMapOptimization = $null
        $structuralAlphaExpected = $false

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
            $imageOptionTokens = Get-ImageOptionTokens $line
            if ($imageOptionTokens.Count -ge 1) {
                $imageCompression = $imageOptionTokens[0].ToUpperInvariant()
            }
            if ($imageOptionTokens.Count -ge 2) {
                $imageMapOptimization = $imageOptionTokens[1].ToUpperInvariant()
            }
            $structuralAlphaExpected = Test-StructuralAlphaExpected -resourceKind $kind -resourceName $name -resourcePath $path
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

        $info = $null
        if ($magickPath) {
            try {
                $info = Get-ImageInfo $magickPath $absPath
            } catch {
                Write-Log "ImageMagick falhou para ${path}: $($_.Exception.Message). Tentando fallback .NET..." "WARN"
            }
        }

        if (-not $info) {
            try {
                $info = Get-PngHeaderInfo $absPath
                Write-Log ("Inspecao via fallback .NET para {0}: {1}x{2} bitDepth={3} palette={4}" -f $path, $info.Width, $info.Height, $info.Depth, $info.PaletteEntries) "INFO"
            } catch {
                $msg = "Falha ao inspecionar ${path} (ImageMagick e fallback .NET): $($_.Exception.Message)"
                Write-Log $msg "ERROR"
                $results.summary.errors++
                Add-Detail $results "IDENTIFY_FAILED" "ERROR" $msg $name $path
                continue
            }
        }

        if ($info.Source -eq "imagemagick" -and $info.Indexed) {
            try {
                $pngHeader = Get-PngHeaderInfo $absPath
                $info | Add-Member -NotePropertyName PaletteEntries -NotePropertyValue $pngHeader.PaletteEntries -Force
            } catch { }
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

        $paletteInflatedHandledColors = $false
        if ($info.Indexed -and $info.PSObject.Properties.Name -contains 'PaletteEntries' -and $info.PaletteEntries -gt 16) {
            if ($info.Colors -gt 16) {
                $paletteInflatedHandledColors = $true
                $msg = "Imagem $path tem $($info.PaletteEntries) entradas de paleta PLTE e $($info.Colors) cores unicas (max 16). ResComp rejeitara esta imagem."
                Write-Log $msg "ERROR"
                $results.summary.errors++
                Add-Detail $results "PALETTE_INFLATED" "ERROR" $msg $name $path @{
                    paletteEntries = $info.PaletteEntries
                    bitDepth = $info.Depth
                    uniqueColors = $info.Colors
                }
            } else {
                $msg = "Imagem $path tem $($info.PaletteEntries) entradas de paleta PLTE (max 16), mas apenas $($info.Colors) cores unicas. ResComp re-indexa automaticamente; considere re-quantizar para limpeza."
                Write-Log $msg "WARN"
                $results.summary.warnings++
                Add-Detail $results "PALETTE_INFLATED" "WARNING" $msg $name $path @{
                    paletteEntries = $info.PaletteEntries
                    bitDepth = $info.Depth
                    uniqueColors = $info.Colors
                }
            }
        }

        if (-not $paletteInflatedHandledColors -and $info.Colors -gt 16) {
            $invalidReasons += "$($info.Colors) cores"
        }

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

        if ($kind -eq "IMAGE" -and $info.Indexed) {
            $sceneScaleImage = Test-SceneScaleImage -resourceName $name -resourcePath $path -info $info
            if ($sceneScaleImage -and $imageCompression -eq "NONE" -and $imageMapOptimization -eq "NONE") {
                $warnMsg = "Imagem de cena $name usa `IMAGE ... NONE NONE`, configuracao de alto risco para prova em ROM por manter compressao e otimizacao de tiles desligadas numa promocao estruturalmente pesada."
                Write-Log $warnMsg "WARN"
                $results.summary.warnings++
                Add-Detail $results "IMAGE_SCENE_RISK" "WARNING" $warnMsg $name $path @{
                    width = $info.Width
                    height = $info.Height
                    compression = $imageCompression
                    mapOptimization = $imageMapOptimization
                }
            }

            if ($structuralAlphaExpected) {
                $transparencyAudit = Get-IndexedTransparencyAudit -filePath $absPath
                $transparencySeverity = Get-IndexedTransparencySeverity -audit $transparencyAudit
                if ($transparencySeverity -and $transparencySeverity.level -ne "OK") {
                    $effectiveLevel = $transparencySeverity.level
                    if ($kind -eq "IMAGE" -and $effectiveLevel -eq "ERROR") {
                        $effectiveLevel = "WARNING"
                    }
                    $logLevel = switch ($effectiveLevel) {
                        "ERROR" { "ERROR" }
                        "WARNING" { "WARN" }
                        default { "INFO" }
                    }
                    $auditMsg = "Imagem ${name}: $($transparencySeverity.message)"
                    Write-Log $auditMsg $logLevel
                    if ($effectiveLevel -eq "ERROR") {
                        $results.summary.errors++
                    } elseif ($effectiveLevel -eq "WARNING") {
                        $results.summary.warnings++
                    }
                    Add-Detail $results $transparencySeverity.code $effectiveLevel $auditMsg $name $path @{
                        bitsPerPixel = $transparencyAudit.bitsPerPixel
                        totalPixels = $transparencyAudit.totalPixels
                        zeroIndexPixelCount = $transparencyAudit.zeroIndexPixelCount
                        zeroIndexCoverage = $transparencyAudit.zeroIndexCoverage
                        paletteZeroAlpha = $transparencyAudit.paletteZeroAlpha
                    }
                }
            }
        }

        if ($visualAnalyzerAvailable -and ([System.IO.Path]::GetExtension($absPath).ToLowerInvariant() -eq ".png")) {
            $visualRole = Get-AestheticRole -resourceKind $kind -resourceName $name -resourcePath $path
            $criticalVisual = Test-CriticalVisual -resourceKind $kind -resourceName $name -resourcePath $path
            $safeVariantPairs = if ($null -ne $visualReviewVariantPairs) { $visualReviewVariantPairs } else { @() }
            $analysisContexts = Get-VisualPairContextsForResource -VariantPairs $safeVariantPairs -ResourcePath $path
            if (-not $analysisContexts -or $analysisContexts.Count -eq 0) {
                $analysisContexts = @(
                    [pscustomobject]@{
                        scene = $null
                        variant = $null
                        mode = $null
                        variant_key = $name.ToLowerInvariant()
                        paired_bg_rel = $null
                        paired_bg_abs = $null
                    }
                )
            }

            foreach ($analysisContext in $analysisContexts) {
                $analysisSuffix = if ($analysisContext.variant) { "_{0}" -f $analysisContext.variant_key } else { "" }
                $visualOutputPath = Join-Path $LOG_DIR ("aesthetic_{0}{1}.json" -f $name.ToLowerInvariant(), $analysisSuffix)
                try {
                    $pairedBgPath = $null
                    if ($analysisContext.paired_bg_abs -and (Test-Path -LiteralPath $analysisContext.paired_bg_abs)) {
                        $pairedBgPath = $analysisContext.paired_bg_abs
                    }

                    $analysis = Invoke-AestheticAnalysis `
                        -PythonPath $pythonPath `
                        -AnalyzerPath $aestheticAnalyzerPath `
                        -AssetPath $absPath `
                        -Role $visualRole `
                        -ReferenceProfile $aestheticReferenceProfile `
                        -OutputPath $visualOutputPath `
                        -PairedBg $pairedBgPath `
                        -CriticalVisual $criticalVisual

                    $analysis | Add-Member -NotePropertyName resource_name -NotePropertyValue $name -Force
                    $analysis | Add-Member -NotePropertyName resource_kind -NotePropertyValue $kind -Force
                    $analysis | Add-Member -NotePropertyName resource_path -NotePropertyValue $path -Force
                    $analysis | Add-Member -NotePropertyName scene_name -NotePropertyValue $analysisContext.scene -Force
                    $analysis | Add-Member -NotePropertyName variant_name -NotePropertyValue $analysisContext.variant -Force
                    $analysis | Add-Member -NotePropertyName pair_mode -NotePropertyValue $analysisContext.mode -Force
                    $analysis | Add-Member -NotePropertyName paired_bg_declared -NotePropertyValue $analysisContext.paired_bg_rel -Force
                    $analysis | Add-Member -NotePropertyName analysis_key -NotePropertyValue $analysisContext.variant_key -Force
                    $visualAnalyses += $analysis
                } catch {
                    $contextSuffix = if ($analysisContext.variant) { " ($($analysisContext.variant))" } else { "" }
                    $warnMsg = "Falha ao executar juiz estetico para ${name}${contextSuffix}: $($_.Exception.Message)"
                    Write-Log $warnMsg "WARN"
                    $results.summary.warnings++
                    Add-Detail $results "VISUAL_ANALYSIS" "WARNING" $warnMsg $name $absPath
                }
            }
        }
    }
}

if ($visualAnalyzerAvailable -and $visualLabAnalyzerPath -and (Test-Path -LiteralPath $visualLabAnalyzerPath) -and (Test-Path -LiteralPath $visualLabManifestPath)) {
    try {
        $visualLabBenchmark = Invoke-VisualLabCaseAnalysis `
            -PythonPath $pythonPath `
            -AnalyzerPath $visualLabAnalyzerPath `
            -ManifestPath $visualLabManifestPath `
            -OutputPath $visualAestheticReportPath
    } catch {
        $warnMsg = "Falha ao executar benchmark visual composto: $($_.Exception.Message)"
        Write-Log $warnMsg "WARN"
        $results.summary.warnings++
        Add-Detail $results "VISUAL_BENCHMARK" "WARNING" $warnMsg "visual" $visualLabManifestPath
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

$memoryArtifactCandidates = @(
    (Join-Path $pwd.Path "doc\10-memory-bank.md")
)
if ($workspaceRoot) {
    $workspaceMemoryArtifact = Join-Path $workspaceRoot "doc\06_AI_MEMORY_BANK.md"
    if ($workspaceMemoryArtifact -notin $memoryArtifactCandidates) {
        $memoryArtifactCandidates += $workspaceMemoryArtifact
    }
    $workspaceVisualFeedbackArtifact = Join-Path $workspaceRoot "doc\03_art\02_visual_feedback_bank.md"
    if ($workspaceVisualFeedbackArtifact -notin $memoryArtifactCandidates) {
        $memoryArtifactCandidates += $workspaceVisualFeedbackArtifact
    }
}
$memoryArtifactPath = $memoryArtifactCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if ($memoryArtifactPath) {
    $results.evidence.memory_artifact = $memoryArtifactPath
}

$agentBootstrapStatus = Get-AgentBootstrapStatus -ProjectRoot $pwd.Path -WorkspaceRoot $workspaceRoot
$results.status_panel.agent_bootstrapped = [bool]$agentBootstrapStatus.agent_bootstrapped
$results.status_panel.bootstrap_degradado = [bool]$agentBootstrapStatus.bootstrap_degradado
$results.evidence.agent_bootstrap = $agentBootstrapStatus

if ($agentBootstrapStatus.bootstrap_degradado) {
    $msg = ("Bootstrap local da .agent em modo degradado: {0}." -f $agentBootstrapStatus.reason)
    if ($agentBootstrapStatus.reason -eq "agents_bridge_broken") {
        $bridge = $agentBootstrapStatus.agents_bridge
        $msg = ("Bootstrap local da .agent em modo degradado: agents_bridge_broken (path='{0}', expected='{1}', actual='{2}', link_type='{3}', reason='{4}')." -f `
            (Get-SafeString $bridge.path ""), (Get-SafeString $bridge.expected_target ""), (Get-SafeString $bridge.actual_target ""), (Get-SafeString $bridge.link_type ""), (Get-SafeString $bridge.reason ""))
    }
    Write-Log $msg "ERROR"
    Add-BlockingStatus $results "agent_context_degraded" $msg ".agent" $agentBootstrapStatus.local_agent_dir @{
        canonicalVersion = $agentBootstrapStatus.canonical_version
        localVersion = $agentBootstrapStatus.local_version
        reason = $agentBootstrapStatus.reason
    }
}
elseif ($agentBootstrapStatus.agents_bridge -and -not $agentBootstrapStatus.agents_bridge.present) {
    $bridge = $agentBootstrapStatus.agents_bridge
    $msg = ("Ponte repo-native de skills ausente: '{0}'. A descoberta por `.agents/skills` pode ficar incompleta neste ambiente." -f (Get-SafeString $bridge.path ""))
    Write-Log $msg "WARN"
    Add-Detail $results "AGENTS_BRIDGE_MISSING" "WARNING" $msg "validator_config" (Get-SafeString $bridge.path "") @{
        expectedTarget = (Get-SafeString $bridge.expected_target "")
    }
}

try {
    $srcDir = Join-Path $pwd.Path "src"
    if (Test-Path -LiteralPath $srcDir) {
        $cFiles = Get-ChildItem -LiteralPath $srcDir -Recurse -File -ErrorAction SilentlyContinue | Where-Object { $_.Extension -in @(".c", ".h") }
        if ($cFiles) {
            $enforceNoHeap = $false
            if ($env:SGDK_ENFORCE_NO_HEAP -and ($env:SGDK_ENFORCE_NO_HEAP -in @("1","true","TRUE","True"))) { $enforceNoHeap = $true }
            foreach ($f in $cFiles) {
                try {
                    $content = Get-Content -LiteralPath $f.FullName
                    $lineIdx = 0
                    foreach ($line in $content) {
                        $lineIdx++
                        if ($line -match '\b(malloc|calloc|realloc|free)\s*\(') {
                            $lvl = if ($enforceNoHeap) { "ERROR" } else { "WARNING" }
                            if ($enforceNoHeap) { $results.summary.errors++ } else { $results.summary.warnings++ }
                            Add-Detail $results "BANNED_API" $lvl ("Uso de API de heap detectado: " + $Matches[1]) "heap" $f.FullName @{ line = $lineIdx }
                        }
                    }
                } catch {
                    Write-Log ("Falha ao ler arquivo de codigo: {0}" -f $f.FullName) "WARN"
                    $results.summary.warnings++
                    Add-Detail $results "CODE_SCAN" "WARNING" "Falha ao ler arquivo para varredura de heap" "code" $f.FullName
                }
            }
        }
    }
} catch {
    Write-Log ("Varredura de heap falhou: {0}" -f $_.Exception.Message) "WARN"
    $results.summary.warnings++
    Add-Detail $results "CODE_SCAN" "WARNING" "Varredura de heap interrompida" "code" $pwd.Path
}

if ($visualAnalyses.Count -gt 0) {
    $eliteReadyCount = @($visualAnalyses | Where-Object { $_.status -eq "elite_ready" }).Count
    $needsReviewCount = @($visualAnalyses | Where-Object { $_.status -eq "needs_review" }).Count
    $reworkCount = @($visualAnalyses | Where-Object { $_.status -eq "rework" }).Count
    $criticalReworkCount = @($visualAnalyses | Where-Object { $_.status -eq "rework" -and $_.critical_visual }).Count
    $criticalNotReadyCount = @($visualAnalyses | Where-Object { $_.critical_visual -and $_.status -ne "elite_ready" }).Count

    $visualStatusRaw =
        if ($criticalReworkCount -gt 0) { "reprovado" }
        elseif ($reworkCount -gt 0) { "alerta_forte" }
        elseif ($needsReviewCount -gt 0) { "alerta" }
        else { "aprovado" }

    $visualStatus = $visualStatusRaw
    $benchmarkSection = $null

    if ($visualLabBenchmark) {
        $benchmarkSection = @{
            benchmark_id = Get-SafeString $visualLabBenchmark.benchmark_id ""
            benchmark_status = Get-SafeString $visualLabBenchmark.benchmark_status "nao_medido"
            comparison = $visualLabBenchmark.comparison
            lane_scores = $visualLabBenchmark.lane_scores
            evidence = $visualLabBenchmark.evidence
            benchmark_assets = @($visualLabBenchmark.assets)
        }

        $visualStatus = Get-SafeString $visualLabBenchmark.status $visualStatusRaw
    }

    $visualGateReady = ($reworkCount -eq 0 -and $criticalNotReadyCount -eq 0)
    if ($visualLabBenchmark -and $visualLabBenchmark.comparison) {
        $benchmarkPassed = $false
        if ($null -ne $visualLabBenchmark.comparison.passed_delta) {
            $benchmarkPassed = [bool]($visualLabBenchmark.comparison.passed_delta | ForEach-Object { $_ })
        }
        $visualGateReady = $visualGateReady -and $benchmarkPassed
    }

    $results.visual_profile = @{
        status = $visualStatus
        analyzed_assets = $visualAnalyses.Count
        elite_ready = $eliteReadyCount
        needs_review = $needsReviewCount
        rework = $reworkCount
        critical_rework = $criticalReworkCount
        assets = @($visualAnalyses)
        benchmark = $benchmarkSection
    }
    $results.evidence.visual_aesthetic_report_path = $visualAestheticReportPath
    $results.qa_axes.visual_elite = $visualStatus
    $results.status_panel.visual_gate_ready = $visualGateReady

    $reportPayload = @{
        generated_at = (Get-Date -Format "o")
        reference_profile = $aestheticReferenceProfile
        status = $visualStatus
        analyzed_assets = $visualAnalyses.Count
        elite_ready = $eliteReadyCount
        needs_review = $needsReviewCount
        rework = $reworkCount
        critical_rework = $criticalReworkCount
        assets = @($visualAnalyses)
    }
    if ($visualLabBenchmark) {
        $reportPayload.benchmark_id = Get-SafeString $visualLabBenchmark.benchmark_id ""
        $reportPayload.reference_asset = $visualLabBenchmark.reference_asset
        $reportPayload.minimum_delta = $visualLabBenchmark.minimum_delta
        $reportPayload.benchmark_status = Get-SafeString $visualLabBenchmark.benchmark_status "nao_medido"
        $reportPayload.comparison = $visualLabBenchmark.comparison
        $reportPayload.lane_scores = $visualLabBenchmark.lane_scores
        $reportPayload.evidence = $visualLabBenchmark.evidence
        $reportPayload.benchmark_assets = @($visualLabBenchmark.assets)
        $reportPayload.raw_asset_summary = @{
            status = $visualStatusRaw
            analyzed_assets = $visualAnalyses.Count
            elite_ready = $eliteReadyCount
            needs_review = $needsReviewCount
            rework = $reworkCount
            critical_rework = $criticalReworkCount
        }
    }
    [System.IO.File]::WriteAllText(
        $visualAestheticReportPath,
        ($reportPayload | ConvertTo-Json -Depth 12),
        [System.Text.Encoding]::UTF8
    )

    if ($visualLabBenchmark) {
        Add-Detail $results "VISUAL_ELITE" "INFO" "Projeto em modo benchmark composto: o gate visual principal usa o delta BASIC vs ELITE." "visual" $visualAestheticReportPath @{
            benchmarkStatus = $visualLabBenchmark.benchmark_status
            rawStatus = $visualStatusRaw
            finalStatus = $visualStatus
        }
    } elseif ($criticalReworkCount -gt 0) {
        $msg = "Gate visual reprovado: asset critico em rework detectado pelo juiz estetico."
        Write-Log $msg (Get-BlockingStatusLogLevel "visual_gate_blocked")
        Add-BlockingStatus $results "visual_gate_blocked" $msg "visual" $visualAestheticReportPath @{
            criticalRework = $criticalReworkCount
            totalAssets = $visualAnalyses.Count
        }
    } elseif ($reworkCount -gt 0) {
        $msg = "Gate visual bloqueado: existem assets em rework no juiz estetico."
        Write-Log $msg (Get-BlockingStatusLogLevel "visual_gate_blocked")
        Add-BlockingStatus $results "visual_gate_blocked" $msg "visual" $visualAestheticReportPath @{
            rework = $reworkCount
            totalAssets = $visualAnalyses.Count
        }
    } elseif ($criticalNotReadyCount -gt 0) {
        $msg = "Gate visual bloqueado: existe asset critico sem status elite_ready."
        Write-Log $msg (Get-BlockingStatusLogLevel "visual_gate_blocked")
        Add-BlockingStatus $results "visual_gate_blocked" $msg "visual" $visualAestheticReportPath @{
            criticalNotReady = $criticalNotReadyCount
            totalAssets = $visualAnalyses.Count
        }
    } elseif ($needsReviewCount -gt 0) {
        $msg = "Gate visual bloqueado: qualquer asset em needs_review impede Elite/AAA ate curadoria canonica."
        Write-Log $msg (Get-BlockingStatusLogLevel "visual_gate_blocked")
        Add-BlockingStatus $results "visual_gate_blocked" $msg "visual" $visualAestheticReportPath @{
            needsReview = $needsReviewCount
            totalAssets = $visualAnalyses.Count
        }
    } else {
        Add-Detail $results "VISUAL_ELITE" "INFO" "Todos os assets analisados passaram no gate visual desta validacao." "visual" $visualAestheticReportPath @{
            eliteReady = $eliteReadyCount
            totalAssets = $visualAnalyses.Count
        }
    }

    if ($visualLabBenchmark -and $visualLabBenchmark.comparison) {
        $benchmarkPassed = $false
        if ($null -ne $visualLabBenchmark.comparison.passed_delta) {
            $benchmarkPassed = [bool]($visualLabBenchmark.comparison.passed_delta | ForEach-Object { $_ })
        }

        if (-not $benchmarkPassed) {
            $msg = "Benchmark visual composto nao atingiu o delta minimo entre BASIC e ELITE."
            Write-Log $msg (Get-BlockingStatusLogLevel "visual_gate_blocked")
            Add-BlockingStatus $results "visual_gate_blocked" $msg "visual" $visualAestheticReportPath @{
                benchmarkStatus = $visualLabBenchmark.benchmark_status
                eliteMinusBasic = $visualLabBenchmark.comparison.elite_minus_basic
                minimumDelta = $visualLabBenchmark.comparison.minimum_delta
            }
        } else {
            Add-Detail $results "VISUAL_BENCHMARK" "INFO" "Benchmark visual confirmou delta canonico entre BASIC e ELITE." "visual" $visualAestheticReportPath @{
                benchmarkStatus = $visualLabBenchmark.benchmark_status
                eliteMinusBasic = $visualLabBenchmark.comparison.elite_minus_basic
                minimumDelta = $visualLabBenchmark.comparison.minimum_delta
            }
        }
    }
}
else {
    $msg = "Gate visual sem medicao canonica: nenhum asset visual foi analisado e o laboratorio visual nao pode ser promovido."
    Write-Log $msg (Get-BlockingStatusLogLevel "visual_gate_blocked")
    Add-BlockingStatus $results "visual_gate_blocked" $msg "visual" $visualAestheticReportPath @{
        reason = "no_visual_analysis"
        totalAssets = 0
        benchmarkStatus = if ($visualLabBenchmark) { Get-SafeString $visualLabBenchmark.benchmark_status "nao_medido" } else { "nao_configurado" }
    }
}

if ($visualDeliveryGateReport) {
    $results.evidence.visual_delivery_gate_report_path = $visualDeliveryGateReportPath
    $gateFindings = @()

    $schemaValue = Get-SafeString (Get-ObjectPropertyValue $visualDeliveryGateReport "schema" "") ""
    if ($schemaValue -ne "visual_delivery_gate_report.v1") {
        $gateFindings += "schema_missing_or_invalid"
    }

    foreach ($routeField in @("visual_route_status", "route_status", "pipeline_status", "delivery_status")) {
        $routeStatus = Get-SafeString (Get-ObjectPropertyValue $visualDeliveryGateReport $routeField "") ""
        if (-not $routeStatus) { continue }
        $routeStatusNormalized = $routeStatus.ToLowerInvariant()
        if ($routeStatusNormalized -in @("blocked_image_tooling", "blocked_no_premium_source", "blocked_no_visual_source")) {
            $gateFindings += $routeStatusNormalized
        }
        if ($routeStatusNormalized -eq "lab_not_delivery") {
            $gateFindings += "lab_not_delivery"
        }
    }

    $readyForAaaValue = Get-ObjectPropertyValue $visualDeliveryGateReport "ready_for_aaa" $null
    if ($null -ne $readyForAaaValue -and -not (Test-TruthyValue $readyForAaaValue)) {
        $gateFindings += "ready_for_aaa_false"
    }

    $reportAuthorialityGate = Get-SafeString (Get-ObjectPropertyValue $visualDeliveryGateReport "authoriality_gate" "") ""
    if ($reportAuthorialityGate -and $reportAuthorialityGate.ToLowerInvariant() -notin @("passed", "pass", "ok")) {
        $gateFindings += ("authoriality_gate_{0}" -f $reportAuthorialityGate)
    }

    $blockingStatus = Get-SafeString (Get-ObjectPropertyValue $visualDeliveryGateReport "blocking_status" "") ""
    if ($blockingStatus -and $blockingStatus -notin @("none", "ok", "passed")) {
        $gateFindings += $blockingStatus
    }

    $visualDeliveryCandidate =
        (Test-TruthyValue $readyForAaaValue) -or
        ((Get-SafeString (Get-ObjectPropertyValue $visualDeliveryGateReport "visual_route_status" "") "").ToLowerInvariant() -eq "delivery_candidate") -or
        ((Get-SafeString (Get-ObjectPropertyValue $visualDeliveryGateReport "delivery_classification" "") "").ToLowerInvariant() -match "aaa|delivery")

    $vramResidencyStatus = (Get-SafeString (Get-ObjectPropertyValue $visualDeliveryGateReport "vram_residency_status" "") "").ToLowerInvariant()
    $vramResidencyReportRef = Get-ObjectPropertyValue $visualDeliveryGateReport "vram_residency_report" $null
    if ($vramResidencyStatus -in @("failed", "blocked", "nao_medido", "unmeasured", "not_measured", "missing")) {
        $gateFindings += ("vram_residency_status_{0}" -f $vramResidencyStatus)
    }
    if ($visualDeliveryCandidate) {
        if (-not $vramResidencyStatus) {
            $gateFindings += "vram_residency_status_missing"
        }
        if ($null -eq $vramResidencyReportRef -or -not (Test-ExistingArtifactReference $vramResidencyReportRef $pwd.Path)) {
            $gateFindings += "vram_residency_report_missing"
        }
    }
    if ($vramResidencyReportRef -and (Test-ExistingArtifactReference $vramResidencyReportRef $pwd.Path)) {
        $vramResidencyReport = Get-ArtifactJsonOrNull $vramResidencyReportRef $pwd.Path
        if ($null -eq $vramResidencyReport) {
            $gateFindings += "vram_residency_report_invalid"
        } else {
            $reportedVramStatus = (Get-SafeString (Get-ObjectPropertyValue (Get-ObjectPropertyValue $vramResidencyReport "vram" $null) "status" "") "").ToLowerInvariant()
            if ($reportedVramStatus -in @("collision_risk", "failed", "blocked", "error")) {
                $gateFindings += ("vram_residency_report_{0}" -f $reportedVramStatus)
            }
            $reportedOverlaps = @(Get-ObjectPropertyValue (Get-ObjectPropertyValue $vramResidencyReport "vram" $null) "overlaps" @())
            if ($reportedOverlaps.Count -gt 0) {
                $gateFindings += ("vram_residency_overlap_count_{0}" -f $reportedOverlaps.Count)
            }
        }
    }

    $runtimeVisualCorruptionStatus = (Get-SafeString (Get-ObjectPropertyValue $visualDeliveryGateReport "runtime_visual_corruption_status" "") "").ToLowerInvariant()
    if ($runtimeVisualCorruptionStatus -in @("detected", "failed", "blocked", "garbage_tiles", "corrupted")) {
        $gateFindings += ("runtime_visual_corruption_{0}" -f $runtimeVisualCorruptionStatus)
    }
    if ($visualDeliveryCandidate -and -not $runtimeVisualCorruptionStatus) {
        $gateFindings += "runtime_visual_corruption_status_missing"
    }

    $visualVdpDumpStatus = (Get-SafeString (Get-ObjectPropertyValue $visualDeliveryGateReport "visual_vdp_dump_status" "") "").ToLowerInvariant()
    if ($visualDeliveryCandidate -and ($visualVdpDumpStatus -match "required|missing|blocked")) {
        $vdpDumpPath = Join-Path $pwd.Path "out\evidence\blastem\visual_vdp_dump.bin"
        if (-not (Test-Path -LiteralPath $vdpDumpPath -PathType Leaf)) {
            $gateFindings += "visual_vdp_dump_missing_required"
        }
    }

    $criticalAssets = @(Get-ObjectPropertyValue $visualDeliveryGateReport "critical_assets" @())
    if ($criticalAssets.Count -eq 0) {
        $gateFindings += "critical_assets_missing"
    }
    foreach ($asset in $criticalAssets) {
        $assetId = Get-SafeString (Get-ObjectPropertyValue $asset "asset_id" "") "unknown_asset"
        $status = Get-SafeString (Get-ObjectPropertyValue $asset "visual_status" "") ""
        if (-not $status) { $status = Get-SafeString (Get-ObjectPropertyValue $asset "status" "") "" }
        if ($status -in @("needs_review", "rework", "placeholder", "debug_lab", "benchmark-derived", "benchmark_derived")) {
            $gateFindings += ("{0}:{1}" -f $assetId, $status)
        }
        if ($status -eq "debug_lab" -and -not (Test-TruthyValue (Get-ObjectPropertyValue $asset "lab_not_delivery" $false))) {
            $gateFindings += ("{0}:lab_not_delivery_missing" -f $assetId)
        }
        if (Test-TruthyValue (Get-ObjectPropertyValue $asset "lab_not_delivery" $false)) {
            $gateFindings += ("{0}:lab_not_delivery" -f $assetId)
        }

        if (-not (Test-TruthyValue (Get-ObjectPropertyValue $asset "source_validity" $false))) {
            $gateFindings += ("{0}:source_validity_failed" -f $assetId)
        }

        $assetAuthorialityGate = Get-SafeString (Get-ObjectPropertyValue $asset "authoriality_gate" "") ""
        if (-not $assetAuthorialityGate) {
            $gateFindings += ("{0}:authoriality_gate_missing" -f $assetId)
        } elseif ($assetAuthorialityGate.ToLowerInvariant() -notin @("passed", "pass", "ok")) {
            $gateFindings += ("{0}:authoriality_gate_{1}" -f $assetId, $assetAuthorialityGate)
        }

        foreach ($requiredField in @("license", "authorial_source", "derivative_of", "derivative_license_status", "clone_risk_score", "clone_risk_method", "benchmark_used_as")) {
            $fieldValue = Get-ObjectPropertyValue $asset $requiredField $null
            if ($null -eq $fieldValue -or [string]::IsNullOrWhiteSpace([string]$fieldValue)) {
                $gateFindings += ("{0}:{1}_missing" -f $assetId, $requiredField)
            }
        }

        $benchmarkUsedAs = Get-SafeString (Get-ObjectPropertyValue $asset "benchmark_used_as" "") ""
        if ($benchmarkUsedAs -and $benchmarkUsedAs.ToLowerInvariant() -notin @("technical_reference", "technical_benchmark", "scale_density_timing_budget_quality", "escala_densidade_timing_budget_qualidade")) {
            $gateFindings += ("{0}:benchmark_used_as_{1}" -f $assetId, $benchmarkUsedAs)
        }

        $derivativeOf = Get-ObjectPropertyValue $asset "derivative_of" $null
        $hasDerivative = -not (Test-EmptyOrNoneValue $derivativeOf)
        $derivativeLicenseStatus = Get-ObjectPropertyValue $asset "derivative_license_status" $null
        if (-not (Test-ApprovedDerivativeLicenseStatus $derivativeLicenseStatus $hasDerivative)) {
            $gateFindings += ("{0}:derivative_license_status_invalid" -f $assetId)
        }

        $cloneRiskScore = Get-SafeNumberOrNull (Get-ObjectPropertyValue $asset "clone_risk_score" $null)
        $cloneRiskThreshold = Get-SafeNumberOrNull (Get-ObjectPropertyValue $asset "clone_risk_max" $null)
        if ($null -eq $cloneRiskThreshold) { $cloneRiskThreshold = 0.35 }
        if ($null -eq $cloneRiskScore) {
            $gateFindings += ("{0}:clone_risk_score_missing" -f $assetId)
        } elseif ($cloneRiskScore -gt $cloneRiskThreshold) {
            $gateFindings += ("{0}:clone_risk_score_{1}" -f $assetId, $cloneRiskScore)
        }

        $benchmarkSimilarityIndex = Get-SafeNumberOrNull (Get-ObjectPropertyValue $asset "benchmark_similarity_index" $null)
        $benchmarkMaxSimilarity = Get-SafeNumberOrNull (Get-ObjectPropertyValue $asset "benchmark_profile_max_similarity" $null)
        if ($null -eq $benchmarkMaxSimilarity) { $benchmarkMaxSimilarity = Get-SafeNumberOrNull (Get-ObjectPropertyValue $asset "benchmark_max_similarity" $null) }
        if ($null -eq $benchmarkMaxSimilarity) { $benchmarkMaxSimilarity = 0.35 }
        $benchmarkProfileId = Get-SafeString (Get-ObjectPropertyValue $asset "benchmark_profile_id" "") ""
        if (-not $benchmarkProfileId) { $benchmarkProfileId = Get-SafeString (Get-ObjectPropertyValue $asset "benchmark_profile" "") "" }
        if ($benchmarkProfileId -and $null -eq $benchmarkSimilarityIndex) {
            $gateFindings += ("{0}:benchmark_similarity_index_missing" -f $assetId)
        } elseif ($null -ne $benchmarkSimilarityIndex -and $benchmarkSimilarityIndex -gt $benchmarkMaxSimilarity) {
            $gateFindings += ("{0}:benchmark_similarity_index_{1}" -f $assetId, $benchmarkSimilarityIndex)
        }

        $cloneRiskStatus = Get-SafeString (Get-ObjectPropertyValue $asset "clone_risk_status" "") ""
        if ($cloneRiskStatus -and $cloneRiskStatus.ToLowerInvariant() -notin @("passed", "pass", "ok", "low", "baixo")) {
            $gateFindings += ("{0}:clone_risk_status_{1}" -f $assetId, $cloneRiskStatus)
        }

        if (Get-ObjectPropertyValue $asset "rom_asset_path" $null) {
            if (-not (Test-TruthyValue (Get-ObjectPropertyValue $asset "elite_ready" $false))) {
                $gateFindings += ("{0}:elite_ready_missing" -f $assetId)
            }
        }

        $perceptualQuality = Get-SafeString (Get-ObjectPropertyValue $asset "perceptual_quality" "") ""
        if ($perceptualQuality -in @("nao_medido", "unmeasured", "not_measured")) {
            $gateFindings += ("{0}:perceptual_quality_unmeasured" -f $assetId)
        }

        $hasRomAssetPath = -not [string]::IsNullOrWhiteSpace((Get-SafeString (Get-ObjectPropertyValue $asset "rom_asset_path" "") ""))
        $sourceMatch = Get-SafeNumberOrNull (Get-ObjectPropertyValue $asset "source_to_rom_visual_match" $null)
        if ($hasRomAssetPath -and $null -eq $sourceMatch) {
            $gateFindings += ("{0}:source_to_rom_visual_match_missing" -f $assetId)
        } elseif ($null -ne $sourceMatch -and $sourceMatch -lt 8.0) {
            $gateFindings += ("{0}:source_to_rom_visual_match_{1}" -f $assetId, $sourceMatch)
        }

        $benchmarkRequiredMatch = Get-SafeNumberOrNull (Get-ObjectPropertyValue $asset "benchmark_profile_required_match" $null)
        if ($null -eq $benchmarkRequiredMatch) { $benchmarkRequiredMatch = Get-SafeNumberOrNull (Get-ObjectPropertyValue $asset "benchmark_required_match" $null) }
        if ($null -eq $benchmarkRequiredMatch) { $benchmarkRequiredMatch = Get-SafeNumberOrNull (Get-ObjectPropertyValue $asset "required_benchmark_match" $null) }
        $benchmarkMatch = Get-SafeNumberOrNull (Get-ObjectPropertyValue $asset "benchmark_match" $null)
        $hamoopigMatch = Get-SafeNumberOrNull (Get-ObjectPropertyValue $asset "HAMOOPIG_benchmark_match" $null)
        if ($null -eq $benchmarkMatch -and $null -ne $hamoopigMatch) { $benchmarkMatch = $hamoopigMatch }
        if ($null -ne $benchmarkRequiredMatch) {
            if ($null -eq $benchmarkMatch) {
                $gateFindings += ("{0}:benchmark_match_missing" -f $assetId)
            } elseif ($benchmarkMatch -lt $benchmarkRequiredMatch) {
                $gateFindings += ("{0}:benchmark_match_{1}_below_required_{2}" -f $assetId, $benchmarkMatch, $benchmarkRequiredMatch)
            }
        } elseif ($null -ne $hamoopigMatch -and $hamoopigMatch -lt 8.0) {
            $gateFindings += ("{0}:HAMOOPIG_benchmark_match_{1}" -f $assetId, $hamoopigMatch)
        }

        $generationChannel = Get-SafeString (Get-ObjectPropertyValue $asset "generation_channel" "") ""
        $sourceKind = Get-SafeString (Get-ObjectPropertyValue $asset "source_kind" "") ""
        if ($generationChannel -in @("local_author_pixel_rasterization", "procedural_renderer") -or $sourceKind -in @("procedural_debug_lab", "debug_lab")) {
            $gateFindings += ("{0}:local_rasterization_used_as_final" -f $assetId)
        }

        $sourceLineageKind = Get-SafeString (Get-ObjectPropertyValue $asset "source_lineage_kind" "") ""
        if ($sourceLineageKind -in @("benchmark-derived", "benchmark_derived", "clone", "unauthored", "unknown_authority")) {
            $gateFindings += ("{0}:source_lineage_{1}" -f $assetId, $sourceLineageKind)
        }

        $paletteStatus = Get-SafeString (Get-ObjectPropertyValue $asset "palette_status" "") ""
        if ($paletteStatus -eq "PALETTE_WASTE" -or (Test-AssetFlagPresent $asset @("PALETTE_WASTE"))) {
            $gateFindings += ("{0}:PALETTE_WASTE" -f $assetId)
        }

        if (Test-TruthyValue (Get-ObjectPropertyValue $asset "quantization_only" $false)) {
            $gateFindings += ("{0}:quantization_only_palette_pass" -f $assetId)
        }

        if (Test-TruthyValue (Get-ObjectPropertyValue $asset "manual_palette_pass_required" $false)) {
            if (-not (Test-TruthyValue (Get-ObjectPropertyValue $asset "manual_palette_pass" $false))) {
                $gateFindings += ("{0}:manual_palette_pass_missing" -f $assetId)
            }
        }

        $materialProfile = Get-SafeString (Get-ObjectPropertyValue $asset "material_profile" "") ""
        $requiresWhiteMaterialContract =
            (Test-TruthyValue (Get-ObjectPropertyValue $asset "white_material_palette_contract_required" $false)) -or
            ($materialProfile.ToLowerInvariant() -match "white_gi|white_fabric|tecido_claro|gi_branco")
        if ($requiresWhiteMaterialContract) {
            $contractValue = Get-ObjectPropertyValue $asset "white_material_palette_contract" $null
            $contractPath = Get-SafeString (Get-ObjectPropertyValue $asset "white_material_palette_contract_path" "") ""
            $contractPassed = Test-TruthyValue $contractValue
            if ($contractValue -and $contractValue.PSObject.Properties["status"]) {
                $contractPassed = ((Get-SafeString $contractValue.status "") -in @("passed", "ok", "pass"))
            }
            if ($contractPath) {
                $resolvedContractPath = if ([System.IO.Path]::IsPathRooted($contractPath)) { $contractPath } else { Join-Path $pwd.Path $contractPath }
                $contractPassed = $contractPassed -or (Test-Path -LiteralPath $resolvedContractPath)
            }
            if (-not $contractPassed) {
                $gateFindings += ("{0}:white_material_palette_contract_missing" -f $assetId)
            }
            foreach ($slotField in @("hue_shifted_shadows", "warm_clean_highlights", "minimum_tonal_distance", "palette_slot_functions_declared")) {
                if (-not (Test-TruthyValue (Get-ObjectPropertyValue $asset $slotField $false))) {
                    $gateFindings += ("{0}:{1}_missing" -f $assetId, $slotField)
                }
            }
        }

        if (Test-HudVisualAsset $asset $assetId) {
            foreach ($hudField in @("ui_attention_profile", "hud_density", "visual_hierarchy", "hud_screen_area", "contrast_profile", "gameplay_interference")) {
                $hudValue = Get-ObjectPropertyValue $asset $hudField $null
                if ($null -eq $hudValue -or [string]::IsNullOrWhiteSpace([string]$hudValue)) {
                    $gateFindings += ("{0}:{1}_missing" -f $assetId, $hudField)
                }
            }
            if (Test-TruthyValue (Get-ObjectPropertyValue $asset "debug_hud" $false)) {
                $gateFindings += ("{0}:debug_hud_promoted" -f $assetId)
            }
        }

        if (Test-AnimatedCriticalAsset $asset $assetId) {
            foreach ($animationField in @("animation_preview_evidence", "contact_sheet", "pivot_overlay", "foot_contact_report", "motion_phase_map", "frame_delta_report", "slicing_cell_contract")) {
                $animationValue = Get-ObjectPropertyValue $asset $animationField $null
                if ($null -eq $animationValue -or [string]::IsNullOrWhiteSpace([string]$animationValue)) {
                    $gateFindings += ("{0}:{1}_missing" -f $assetId, $animationField)
                } elseif (-not (Test-ExistingArtifactReference $animationValue $pwd.Path)) {
                    $gateFindings += ("{0}:{1}_file_missing" -f $assetId, $animationField)
                }
            }
            $cellContractSource = (Get-SafeString (Get-ObjectPropertyValue $asset "cell_contract_source" "") "").ToLowerInvariant()
            if ($cellContractSource -in @("hardcoded", "hardcoded_default", "unknown", "none")) {
                $gateFindings += ("{0}:cell_contract_source_{1}" -f $assetId, $cellContractSource)
            }
            if (-not (Test-TruthyValue (Get-ObjectPropertyValue $asset "state_belongs_to_character_fantasy" $false))) {
                $gateFindings += ("{0}:state_belongs_to_character_fantasy_false" -f $assetId)
            }
            if (Test-TruthyValue (Get-ObjectPropertyValue $asset "has_attack_states" $false)) {
                $activeRecoveryMap = Get-ObjectPropertyValue $asset "active_recovery_map" $null
                if ($null -eq $activeRecoveryMap -or [string]::IsNullOrWhiteSpace([string]$activeRecoveryMap)) {
                    $gateFindings += ("{0}:active_recovery_map_missing" -f $assetId)
                }
            }
            if (Test-TruthyValue (Get-ObjectPropertyValue $asset "bjj_state" $false)) {
                if (-not (Test-TruthyValue (Get-ObjectPropertyValue $asset "bjj_body_language_declared" $false))) {
                    $gateFindings += ("{0}:bjj_body_language_missing" -f $assetId)
                }
            }

            foreach ($premiumMotionField in @(
                "scale_lock_report",
                "animation_direction_contract",
                "timing_spacing_report",
                "impact_frame_contract",
                "recovery_curve_report",
                "shading_motion_report",
                "palette_flash_policy",
                "palette_domain_report"
            )) {
                $premiumValue = Get-ObjectPropertyValue $asset $premiumMotionField $null
                if ($null -eq $premiumValue -or [string]::IsNullOrWhiteSpace([string]$premiumValue)) {
                    $gateFindings += ("{0}:{1}_missing" -f $assetId, $premiumMotionField)
                } elseif (-not (Test-ExistingArtifactReference $premiumValue $pwd.Path)) {
                    $gateFindings += ("{0}:{1}_file_missing" -f $assetId, $premiumMotionField)
                }
            }

            foreach ($reactionField in @("hit_reaction_contract", "smear_frame_manifest")) {
                $reactionValue = Get-ObjectPropertyValue $asset $reactionField $null
                if ($null -ne $reactionValue -and -not [string]::IsNullOrWhiteSpace([string]$reactionValue)) {
                    if (-not (Test-ExistingArtifactReference $reactionValue $pwd.Path)) {
                        $gateFindings += ("{0}:{1}_file_missing" -f $assetId, $reactionField)
                    }
                } elseif ($reactionField -eq "hit_reaction_contract") {
                    $gateFindings += ("{0}:{1}_missing" -f $assetId, $reactionField)
                }
            }

            $scaleLockReportRef = Get-ObjectPropertyValue $asset "scale_lock_report" $null
            if ($scaleLockReportRef -and (Test-ExistingArtifactReference $scaleLockReportRef $pwd.Path)) {
                $scaleLockReport = Get-ArtifactJsonOrNull $scaleLockReportRef $pwd.Path
                if ($null -eq $scaleLockReport) {
                    $gateFindings += ("{0}:scale_lock_report_invalid" -f $assetId)
                } else {
                    foreach ($state in @((Get-ObjectPropertyValue $scaleLockReport "states" @{}).PSObject.Properties)) {
                        $stateValue = $state.Value
                        if (Test-TruthyValue (Get-ObjectPropertyValue $stateValue "per_frame_scaling" $false)) {
                            $gateFindings += ("{0}:scale_lock_report_per_frame_scaling_{1}" -f $assetId, $state.Name)
                        }
                        $stateStatus = (Get-SafeString (Get-ObjectPropertyValue $stateValue "status" "") "").ToLowerInvariant()
                        if ($stateStatus -and $stateStatus -notin @("passed", "pass", "ok")) {
                            $gateFindings += ("{0}:scale_lock_report_{1}_{2}" -f $assetId, $state.Name, $stateStatus)
                        }
                    }
                }
            }

            $footContactReportRef = Get-ObjectPropertyValue $asset "foot_contact_report" $null
            if ($footContactReportRef -and (Test-ExistingArtifactReference $footContactReportRef $pwd.Path)) {
                $footContactReport = Get-ArtifactJsonOrNull $footContactReportRef $pwd.Path
                if ($null -ne $footContactReport) {
                    foreach ($footFrame in @($footContactReport)) {
                        $method = Get-SafeString (Get-ObjectPropertyValue $footFrame "measurement_method" "") ""
                        $contact = (Get-SafeString (Get-ObjectPropertyValue $footFrame "foot_contact" "") "").ToLowerInvariant()
                        if (-not $method -or $contact -in @("grounded_or_intended", "arc_or_landing")) {
                            $gateFindings += ("{0}:synthetic_foot_contact_report" -f $assetId)
                            break
                        }
                    }
                }
            }

            $spriteArtifactReportRef = Get-ObjectPropertyValue $asset "sprite_artifact_report" $null
            if ($hasRomAssetPath -and ($null -eq $spriteArtifactReportRef -or [string]::IsNullOrWhiteSpace([string]$spriteArtifactReportRef))) {
                $gateFindings += ("{0}:sprite_artifact_report_missing" -f $assetId)
            } elseif ($spriteArtifactReportRef -and -not (Test-ExistingArtifactReference $spriteArtifactReportRef $pwd.Path)) {
                $gateFindings += ("{0}:sprite_artifact_report_file_missing" -f $assetId)
            } elseif ($spriteArtifactReportRef) {
                $spriteArtifactReport = Get-ArtifactJsonOrNull $spriteArtifactReportRef $pwd.Path
                if ($null -eq $spriteArtifactReport) {
                    $gateFindings += ("{0}:sprite_artifact_report_invalid" -f $assetId)
                } else {
                    $spriteArtifactStatus = (Get-SafeString (Get-ObjectPropertyValue $spriteArtifactReport "status" "") "").ToLowerInvariant()
                    if ($spriteArtifactStatus -and $spriteArtifactStatus -notin @("passed", "pass", "ok", "elite_ready")) {
                        $gateFindings += ("{0}:sprite_artifact_report_{1}" -f $assetId, $spriteArtifactStatus)
                    }
                    foreach ($spriteFinding in @($spriteArtifactReport.findings)) {
                        $spriteCode = Get-SafeString (Get-ObjectPropertyValue $spriteFinding "code" "") ""
                        $spriteSeverity = (Get-SafeString (Get-ObjectPropertyValue $spriteFinding "severity" "") "").ToLowerInvariant()
                        if ($spriteCode -in @("FRAME_EDGE_CLIPPING", "FRAME_EMPTY", "NON_INDEX0_BACKGROUND_MATTE", "SMALL_ISLAND_DEBRIS", "STRAY_LARGE_COMPONENT", "SCALE_INCONSISTENCY", "BAKED_FX_IN_CHARACTER_SHEET")) {
                            $gateFindings += ("{0}:{1}" -f $assetId, $spriteCode)
                        } elseif ($spriteSeverity -eq "error") {
                            $gateFindings += ("{0}:sprite_artifact_error_{1}" -f $assetId, $spriteCode)
                        }
                    }
                }
            }

            foreach ($booleanGate in @(
                @{ name = "frame_envelope_integrity"; code = "frame_envelope_integrity_failed" },
                @{ name = "index0_transparency_clean"; code = "index0_transparency_dirty" },
                @{ name = "scale_consistency"; code = "scale_consistency_failed" },
                @{ name = "baked_fx_separated"; code = "baked_fx_not_separated" }
            )) {
                $rawGateValue = Get-ObjectPropertyValue $asset $booleanGate.name $null
                if ($null -ne $rawGateValue -and -not (Test-TruthyValue $rawGateValue)) {
                    $gateFindings += ("{0}:{1}" -f $assetId, $booleanGate.code)
                }
            }
        }

        $premiumSourcePath = Get-SafeString (Get-ObjectPropertyValue $asset "premium_source_path" "") ""
        if ($premiumSourcePath) {
            $resolvedPremiumSourcePath = if ([System.IO.Path]::IsPathRooted($premiumSourcePath)) { $premiumSourcePath } else { Join-Path $pwd.Path $premiumSourcePath }
            if (-not (Test-Path -LiteralPath $resolvedPremiumSourcePath)) {
                $gateFindings += ("{0}:premium_source_missing" -f $assetId)
            }
        } else {
            $gateFindings += ("{0}:premium_source_missing" -f $assetId)
        }
    }

    if ($gateFindings.Count -gt 0) {
        $results.status_panel.visual_gate_ready = $false
        $msg = "visual_delivery_gate_report bloqueou a promocao visual AAA."
        Write-Log $msg (Get-BlockingStatusLogLevel "visual_gate_blocked")
        Add-BlockingStatus $results "visual_gate_blocked" $msg "visual" $visualDeliveryGateReportPath @{
            findings = @($gateFindings | Select-Object -Unique)
        }
    } else {
        Add-Detail $results "VISUAL_DELIVERY_GATE" "INFO" "visual_delivery_gate_report presente e sem blockers." "visual" $visualDeliveryGateReportPath
    }
}

if ($runtimeMetrics -and $runtimeThresholds) {
    Set-RuntimeProfileFromMetrics $results $runtimeMetrics $runtimeThresholds $runtimeMetricsPath
}

$runtimeSamplesRecorded = 0
if ($runtimeMetrics -and $null -ne $runtimeMetrics.samples_recorded) {
    $runtimeSamplesRecorded = [int]($runtimeMetrics.samples_recorded | ForEach-Object { $_ })
}

$romIdentity = Get-FileIdentity -Path $romPath
$sessionEvidenceFiles = @()
if ($emulatorSession) {
    foreach ($entry in @($emulatorSession.evidence_files + $emulatorSession.captures)) {
        $candidate = Get-SafeString $entry ""
        if ($candidate) {
            $sessionEvidenceFiles += $candidate
        }
    }
}
$sessionEvidenceFiles = $sessionEvidenceFiles | Select-Object -Unique
$sessionLaunchStatus = if ($emulatorSession) { Get-SafeString $emulatorSession.launch_status "" } else { "" }
$sessionCaptured = Test-SessionCaptured -LaunchStatus $sessionLaunchStatus
$existingSessionEvidence = @($sessionEvidenceFiles | Where-Object { Test-Path -LiteralPath $_ })
$sessionTimestamp = if ($emulatorSession) { Get-DateOrNull $emulatorSession.timestamp } else { $null }
$sessionRomPath = if ($emulatorSession) { Resolve-ExistingPathOrNull $emulatorSession.rom_path } else { $null }
$sessionRomIdentity = if ($emulatorSession) { Get-RomIdentityFromSession -Session $emulatorSession } else { $null }
$emulatorName = if ($emulatorSession) { Get-SafeString $emulatorSession.emulator (Get-SafeString $emulatorSession.reference_emulator "") } else { "" }
$sessionSandboxRoot = if ($emulatorSession) { Resolve-ExistingPathOrNull $emulatorSession.sandbox_root } else { $null }
$sessionSaveRoot = if ($emulatorSession) { Resolve-ExistingPathOrNull $emulatorSession.save_root } else { $null }
$sessionLogPath = if ($emulatorSession) { Resolve-ExistingPathOrNull $emulatorSession.emulator_log_path } else { $null }
$outsideSandboxCandidate = if ($emulatorSession) { Resolve-ExistingPathOrNull $emulatorSession.outside_sandbox_candidate } else { $null }
$staleSandboxCandidate = if ($emulatorSession) { Resolve-ExistingPathOrNull $emulatorSession.stale_sandbox_candidate } else { $null }
$sessionFreshSramConfirmed = $null
if ($emulatorSession -and $null -ne $emulatorSession.fresh_sram_confirmed) {
    try {
        $sessionFreshSramConfirmed = [bool]$emulatorSession.fresh_sram_confirmed
    } catch {
        $sessionFreshSramConfirmed = $null
    }
}
$isBlastEmSession = $emulatorName -match '(?i)blastem'
$evidenceOutsideSandbox = $false
if ($sessionSandboxRoot) {
    foreach ($evidencePath in $existingSessionEvidence) {
        if (-not (Test-PathUnderRoot -CandidatePath $evidencePath -RootPath $sessionSandboxRoot)) {
            $evidenceOutsideSandbox = $true
            break
        }
    }
}
$currentRomPath = if ($romIdentity) { Resolve-ExistingPathOrNull $romIdentity.path } else { $null }
$runtimeMetricsItem = if (Test-Path -LiteralPath $runtimeMetricsPath) { Get-Item -LiteralPath $runtimeMetricsPath } else { $null }
$runtimeMetricsFresh = $false
if ($runtimeMetricsItem -and $romIdentity) {
    $runtimeMetricsFresh = ($runtimeMetricsItem.LastWriteTimeUtc -ge ([datetimeoffset]::Parse($romIdentity.last_write_utc)).UtcDateTime)
}

$emulatorEvidenceStale = $false
$emulatorEvidenceReason = "sem_sessao"
if ($emulatorSession) {
    $emulatorEvidenceReason = "ok"
    if (-not $sessionCaptured) {
        $emulatorEvidenceStale = $true
        $emulatorEvidenceReason = "session_not_captured"
    } elseif ($existingSessionEvidence.Count -eq 0 -and $runtimeSamplesRecorded -le 0) {
        $emulatorEvidenceStale = $true
        $emulatorEvidenceReason = "missing_evidence_files"
    } elseif ($isBlastEmSession -and $outsideSandboxCandidate) {
        $emulatorEvidenceStale = $true
        $emulatorEvidenceReason = "outside_sandbox_candidate"
    } elseif ($isBlastEmSession -and $staleSandboxCandidate) {
        $emulatorEvidenceStale = $true
        $emulatorEvidenceReason = "stale_sandbox_candidate"
    } elseif ($isBlastEmSession -and (-not $sessionSandboxRoot)) {
        $emulatorEvidenceStale = $true
        $emulatorEvidenceReason = "missing_sandbox_root"
    } elseif ($isBlastEmSession -and $sessionSaveRoot -and (-not (Test-PathUnderRoot -CandidatePath $sessionSaveRoot -RootPath $sessionSandboxRoot))) {
        $emulatorEvidenceStale = $true
        $emulatorEvidenceReason = "save_root_outside_sandbox"
    } elseif ($isBlastEmSession -and $evidenceOutsideSandbox) {
        $emulatorEvidenceStale = $true
        $emulatorEvidenceReason = "evidence_outside_sandbox"
    } elseif ($isBlastEmSession -and $null -ne $sessionFreshSramConfirmed -and (-not $sessionFreshSramConfirmed)) {
        $emulatorEvidenceStale = $true
        $emulatorEvidenceReason = "fresh_sram_unconfirmed"
    } elseif ($currentRomPath -and $sessionRomPath -and $currentRomPath -ne $sessionRomPath) {
        $emulatorEvidenceStale = $true
        $emulatorEvidenceReason = "rom_path_mismatch"
    } elseif ($romIdentity -and $sessionRomIdentity) {
        $shaMismatch = $sessionRomIdentity.sha256 -and $romIdentity.sha256 -and ($sessionRomIdentity.sha256 -ne $romIdentity.sha256)
        $sizeMismatch = ($null -ne $sessionRomIdentity.size_bytes) -and ($null -ne $romIdentity.size_bytes) -and ([int64]$sessionRomIdentity.size_bytes -ne [int64]$romIdentity.size_bytes)
        $writeMismatch = $sessionRomIdentity.last_write_utc -and $romIdentity.last_write_utc -and ($sessionRomIdentity.last_write_utc -ne $romIdentity.last_write_utc)
        $hasComparableHash = $sessionRomIdentity.sha256 -and $romIdentity.sha256
        if ($shaMismatch -or $sizeMismatch -or ((-not $hasComparableHash) -and $writeMismatch)) {
            $emulatorEvidenceStale = $true
            $emulatorEvidenceReason = "rom_identity_mismatch"
        }
    } elseif ($romIdentity -and $sessionTimestamp) {
        $romLastWrite = [datetimeoffset]::Parse($romIdentity.last_write_utc)
        if ($sessionTimestamp -lt $romLastWrite) {
            $emulatorEvidenceStale = $true
            $emulatorEvidenceReason = "session_older_than_rom"
        }
    }
}

if ($runtimeSamplesRecorded -gt 0 -and -not $runtimeMetricsFresh -and $romIdentity) {
    $emulatorEvidenceStale = $true
    $emulatorEvidenceReason = "runtime_metrics_stale"
}

$results.evidence.runtime_metrics_path = if (Test-Path -LiteralPath $runtimeMetricsPath) { $runtimeMetricsPath } else { $null }
$results.evidence.emulator_session_path = if (Test-Path -LiteralPath $emulatorSessionPath) { $emulatorSessionPath } else { $null }
$results.evidence.rom_path = if (Test-Path -LiteralPath $romPath) { $romPath } else { $null }
$results.evidence.runtime_samples_recorded = $runtimeSamplesRecorded
$results.evidence.emulator_reference = Get-SafeString $emulatorSession.emulator (Get-SafeString $emulatorSession.reference_emulator "nenhum")
$results.evidence.rom_identity = $romIdentity
$results.evidence.emulator_session_rom_identity = $sessionRomIdentity
$results.evidence.emulator_session_rom_path = $sessionRomPath
$results.evidence.emulator_session_timestamp = if ($sessionTimestamp) { $sessionTimestamp.ToString("o") } else { $null }
$results.evidence.emulator_evidence_reason = $emulatorEvidenceReason
$results.evidence.emulator_sandbox_root = $sessionSandboxRoot
$results.evidence.emulator_save_root = $sessionSaveRoot
$results.evidence.emulator_log_path = $sessionLogPath
$results.evidence.emulator_fresh_sram_confirmed = $sessionFreshSramConfirmed
$results.evidence.emulator_outside_sandbox_candidate = $outsideSandboxCandidate
$results.evidence.emulator_stale_sandbox_candidate = $staleSandboxCandidate
$results.evidence.scene_regression_report_path = if (Test-Path -LiteralPath $sceneRegressionReportPath) { $sceneRegressionReportPath } else { $null }
$results.evidence.audio_validation_report_path = if (Test-Path -LiteralPath $audioValidationReportPath) { $audioValidationReportPath } else { $null }
$budgetDocMismatch = Get-BudgetDocumentationMismatch -ProjectRoot $pwd.Path
$changelogStatus = Get-ChangelogStatus -ProjectRoot $pwd.Path -RomIdentity $romIdentity
$sceneRegressionStatus = Get-SceneRegressionStatus -ProjectRoot $pwd.Path -RomIdentity $romIdentity
$results.evidence.changelog_status = $changelogStatus
$results.evidence.scene_regression_status = $sceneRegressionStatus

$audioValidationStatus = [ordered]@{
    required = ($audioDeclarations.Count -gt 0)
    declared_resources = $audioDeclarations.Count
    report_present = Test-Path -LiteralPath $audioValidationReportPath
    stale = $false
    pass = $null
    budget_status = $null
}

if (-not $audioValidationStatus.required) {
    $audioValidationStatus.pass = $true
    $audioValidationStatus.budget_status = "NOT_REQUIRED"
    if ($audioValidationStatus.report_present) {
        Add-Detail $results "AUDIO_VALIDATION" "INFO" "Projeto sem audio declarado em .res; audio_validation_report.json segue como evidencia canonicamente opcional." "audio" $audioValidationReportPath @{
            declaredResources = 0
            budgetStatus = $audioValidationStatus.budget_status
        }
    }
}
elseif ($audioValidationStatus.required) {
    $latestAudioInputUtc = Get-LatestExistingWriteUtc (@($audioDeclarations.res_file) + @($audioDeclarations.resolved_path))

    if ($audioValidationStatus.report_present) {
        try {
            $audioValidationReport = Get-Content -LiteralPath $audioValidationReportPath -Raw | ConvertFrom-Json
            $audioValidationStatus.pass = [bool]$audioValidationReport.summary.pass
            $audioValidationStatus.budget_status = Get-SafeString $audioValidationReport.summary.budget_status ""
            if ($latestAudioInputUtc) {
                $reportWriteUtc = (Get-Item -LiteralPath $audioValidationReportPath).LastWriteTimeUtc
                $audioValidationStatus.stale = ($reportWriteUtc -lt $latestAudioInputUtc)
            }
        } catch {
            $msg = ("Falha ao carregar audio_validation_report.json: {0}" -f $_.Exception.Message)
            Write-Log $msg "ERROR"
            Add-BlockingStatus $results "audio_validation_failed" $msg "audio" $audioValidationReportPath @{
                reportPresent = [bool]$audioValidationStatus.report_present
                declaredResources = $audioDeclarations.Count
            }
        }
    } else {
        $msg = ("Projeto declara {0} recurso(s) de audio em .res, mas out/logs/audio_validation_report.json esta ausente." -f $audioDeclarations.Count)
        Write-Log $msg (Get-BlockingStatusLogLevel "audio_validation_missing")
        Add-BlockingStatus $results "audio_validation_missing" $msg "audio" $audioValidationReportPath @{
            declaredResources = $audioDeclarations.Count
        }
    }

    if ($audioValidationStatus.report_present -and $audioValidationStatus.stale) {
        $msg = "audio_validation_report.json esta stale em relacao aos .res/inputs de audio declarados."
        Write-Log $msg (Get-BlockingStatusLogLevel "audio_validation_stale")
        Add-BlockingStatus $results "audio_validation_stale" $msg "audio" $audioValidationReportPath @{
            declaredResources = $audioDeclarations.Count
        }
    } elseif ($audioValidationStatus.report_present -and $null -ne $audioValidationStatus.pass -and (-not $audioValidationStatus.pass)) {
        $msg = "audio_validation_report.json reportou falha em recursos de audio declarados."
        Write-Log $msg "ERROR"
        Add-BlockingStatus $results "audio_validation_failed" $msg "audio" $audioValidationReportPath @{
            declaredResources = $audioDeclarations.Count
            budgetStatus = $audioValidationStatus.budget_status
        }
    } elseif ($audioValidationStatus.report_present -and (-not $audioValidationStatus.stale) -and $audioValidationStatus.pass) {
        Add-Detail $results "AUDIO_VALIDATION" "INFO" "audio_validation_report.json presente e coerente com os recursos de audio declarados." "audio" $audioValidationReportPath @{
            declaredResources = $audioDeclarations.Count
            budgetStatus = $audioValidationStatus.budget_status
        }
    }
}

$results.evidence.audio_validation_status = $audioValidationStatus

if ($budgetDocMismatch) {
    $firstMismatch = $budgetDocMismatch.mismatches | Select-Object -First 1
    $msg = ("Documento de budget inconsistente com o runtime: SPR_initEx real = {0}, docs = {1}." -f $budgetDocMismatch.runtime.value, (($firstMismatch.documented_values | ForEach-Object { $_ }) -join ", "))
    Write-Log $msg (Get-BlockingStatusLogLevel "budget_doc_mismatch")
    Add-BlockingStatus $results "budget_doc_mismatch" $msg "budget" $firstMismatch.file @{
        runtimeFile = $budgetDocMismatch.runtime.file
        runtimeValue = $budgetDocMismatch.runtime.value
        documentedValues = @($firstMismatch.documented_values)
    }
}

if (-not $changelogStatus.present) {
    $msg = "Changelog canonico ausente: doc/changelog/changelog.md."
    Write-Log $msg (Get-BlockingStatusLogLevel "changelog_missing")
    Add-BlockingStatus $results "changelog_missing" $msg "changelog" $changelogStatus.changelog_path
} elseif ($changelogStatus.assets_missing.Count -gt 0 -or $changelogStatus.assets_outdated.Count -gt 0 -or $changelogStatus.rom_outdated) {
    $parts = @()
    if ($changelogStatus.assets_missing.Count -gt 0) { $parts += ("assets_sem_snapshot={0}" -f $changelogStatus.assets_missing.Count) }
    if ($changelogStatus.assets_outdated.Count -gt 0) { $parts += ("assets_desatualizados={0}" -f $changelogStatus.assets_outdated.Count) }
    if ($changelogStatus.rom_outdated) { $parts += "rom_desatualizada=1" }
    $msg = ("Changelog canonico desatualizado: {0}." -f ($parts -join ", "))
    Write-Log $msg (Get-BlockingStatusLogLevel "changelog_missing")
    Add-BlockingStatus $results "changelog_missing" $msg "changelog" $changelogStatus.changelog_path @{
        assetsMissing = @($changelogStatus.assets_missing)
        assetsOutdated = @($changelogStatus.assets_outdated)
        romOutdated = [bool]$changelogStatus.rom_outdated
    }
}

if ($sceneRegressionStatus.required -and (-not $sceneRegressionStatus.complete) -and ($env:SGDK_SCENE_REGRESSION_BUILDING -ne "1")) {
    $parts = @()
    if (-not $sceneRegressionStatus.report_present) {
        $parts += "report_ausente"
    }
    if ($sceneRegressionStatus.stale) {
        $parts += "report_stale"
    }
    if ($sceneRegressionStatus.missing_scenes.Count -gt 0) {
        $parts += ("cenas_sem_captura={0}" -f $sceneRegressionStatus.missing_scenes.Count)
    }
    if ($sceneRegressionStatus.failed_scenes.Count -gt 0) {
        $parts += ("cenas_falhas={0}" -f $sceneRegressionStatus.failed_scenes.Count)
    }
    if ($parts.Count -eq 0) {
        $parts += "report_incompleto"
    }
    $msg = ("Matriz canonica de regressao por cena ausente, stale ou incompleta: {0}." -f ($parts -join ", "))
    Write-Log $msg (Get-BlockingStatusLogLevel "scene_regression_incomplete")
    Add-BlockingStatus $results "scene_regression_incomplete" $msg "runtime" $sceneRegressionStatus.report_path @{
        missingScenes = @($sceneRegressionStatus.missing_scenes)
        failedScenes = @($sceneRegressionStatus.failed_scenes)
        stale = [bool]$sceneRegressionStatus.stale
        reportPresent = [bool]$sceneRegressionStatus.report_present
    }
}

$results.status_panel.documentado =
    (Test-Path -LiteralPath (Join-Path $pwd.Path "README.md")) -or
    (Test-Path -LiteralPath (Join-Path $pwd.Path "doc")) -or
    (Test-Path -LiteralPath (Join-Path $pwd.Path "docs"))
$results.status_panel.implementado =
    (Test-Path -LiteralPath (Join-Path $pwd.Path "src")) -or
    (Test-Path -LiteralPath (Join-Path $pwd.Path "inc")) -or
    (Test-Path -LiteralPath (Join-Path $pwd.Path "res"))
$results.status_panel.buildado = Test-Path -LiteralPath $romPath
$results.status_panel.audio_validation_ready = if ($audioValidationStatus.required) {
    [bool]($audioValidationStatus.report_present -and (-not $audioValidationStatus.stale) -and $audioValidationStatus.pass)
} else {
    $true
}
$results.status_panel.runtime_capture_present = (($runtimeSamplesRecorded -gt 0) -or ($existingSessionEvidence.Count -gt 0)) -and (-not $emulatorEvidenceStale)
$results.status_panel.emulator_evidence_stale = $emulatorEvidenceStale
$results.status_panel.scene_regression_ready = if ($sceneRegressionStatus) { ((-not $sceneRegressionStatus.required) -or $sceneRegressionStatus.complete) } else { $true }

if ($emulatorEvidenceStale -and $emulatorSession) {
    $msg = ("Evidencia de emulador obsoleta ou insuficiente: {0}." -f $emulatorEvidenceReason)
    Write-Log $msg (Get-BlockingStatusLogLevel "emulator_evidence_stale")
    Add-BlockingStatus $results "emulator_evidence_stale" $msg "emulator" $emulatorSessionPath @{
        reason = $emulatorEvidenceReason
        launchStatus = $sessionLaunchStatus
        evidenceFiles = $existingSessionEvidence.Count
        sandboxRoot = $sessionSandboxRoot
        freshSramConfirmed = $sessionFreshSramConfirmed
    }
}

$blastEmGate = $false
if ($emulatorSession) {
    $bootStatus = Get-SafeString $emulatorSession.boot_emulador (Get-SafeString $emulatorSession.status "nao_testado")
    $results.qa_axes.boot_emulador = $bootStatus
    if ($emulatorName -match '(?i)blastem' -and $bootStatus -eq "ok" -and $sessionCaptured -and -not $emulatorEvidenceStale) {
        $blastEmGate = $true
    }
    $gameplayStatus = Get-SafeString $emulatorSession.gameplay_basico ""
    if ($gameplayStatus) {
        $results.qa_axes.gameplay_basico = $gameplayStatus
    }
    $audioStatus = Get-SafeString $emulatorSession.audio ""
    if ($audioStatus) {
        $results.qa_axes.audio = $audioStatus
    }
    $performanceStatus = Get-SafeString $emulatorSession.performance ""
    if ($performanceStatus) {
        $results.qa_axes.performance = $performanceStatus
    }
    $hardwareRealStatus = Get-SafeString $emulatorSession.hardware_real ""
    if ($hardwareRealStatus) {
        $results.qa_axes.hardware_real = $hardwareRealStatus
    }
} elseif ($runtimeSamplesRecorded -gt 0 -and -not $emulatorEvidenceStale) {
    $results.qa_axes.boot_emulador = "ok"
}

if ($emulatorEvidenceStale) {
    if ($results.qa_axes.boot_emulador -eq "ok") {
        $results.qa_axes.boot_emulador = "stale"
    }
    if ($results.qa_axes.gameplay_basico -eq "funcional") {
        $results.qa_axes.gameplay_basico = "stale"
    }
}

$results.status_panel.blastem_gate = $blastEmGate
$results.status_panel.testado_em_emulador = ($blastEmGate -or ($runtimeSamplesRecorded -gt 0)) -and (-not $emulatorEvidenceStale)
$results.status_panel.changelog_ready = $changelogStatus.present -and ($changelogStatus.assets_missing.Count -eq 0) -and ($changelogStatus.assets_outdated.Count -eq 0) -and (-not $changelogStatus.rom_outdated)
$results.status_panel.validado_budget =
    $results.status_panel.buildado -and
    $results.status_panel.audio_validation_ready -and
    ($results.summary.errors -eq 0) -and
    (
        $results.runtime_profile.frame_stability -eq "estavel" -and
        $results.runtime_profile.sprite_pressure -notin @("alto", "critico") -and
        $results.runtime_profile.fx_load -ne "nao_medido"
    )

$results.qa_axes.build =
    if (-not $results.status_panel.buildado) { "falha" }
    elseif ($results.summary.warnings -gt 0) { "sucesso_com_warnings" }
    else { "sucesso" }

$results.qa_axes.validation_report =
    if ($results.summary.errors -gt 0) { "com_erros" }
    elseif ($results.summary.warnings -gt 0) { "com_alertas" }
    else { "limpo" }

if ($results.qa_axes.performance -eq "nao_testado" -and $results.runtime_profile.frame_stability -ne "nao_medido") {
    $results.qa_axes.performance = if ($results.runtime_profile.frame_stability -eq "estavel") { "estavel" } else { "com_drops" }
}

$sceneContractCompileReportPath = Join-Path $pwd.Path "out\logs\scene_contract_compile_report.json"
$sceneContractCompileDependencies = @(
    (Join-Path $pwd.Path "doc\13-spec-cenas.md"),
    (Join-Path $pwd.Path "doc\scene-regression.json"),
    (Join-Path $pwd.Path "doc\scene-contracts.json")
)
$sceneContractCompileStatus = Get-ObservedReportStatus `
    -ReportPath $sceneContractCompileReportPath `
    -DependencyPaths $sceneContractCompileDependencies

$resGraphReportPath = Join-Path $pwd.Path "out\logs\res_graph_report.json"
$resGraphDependencies = @()
$resRoot = Join-Path $pwd.Path "res"
if (Test-Path -LiteralPath $resRoot -PathType Container) {
    $resGraphDependencies = @(Get-ChildItem -LiteralPath $resRoot -Filter "*.res" -Recurse -File -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName)
}
$resGraphStatus = Get-ObservedReportStatus `
    -ReportPath $resGraphReportPath `
    -DependencyPaths $resGraphDependencies

$freshnessAuditReportPath = Join-Path $pwd.Path "out\logs\freshness_audit_report.json"
$freshnessAuditDependencies = @(
    (Join-Path $pwd.Path "doc\10-memory-bank.md"),
    (Join-Path $pwd.Path "doc\13-spec-cenas.md"),
    (Join-Path $pwd.Path "doc\14-plano-de-provas-qa.md"),
    (Join-Path $pwd.Path "doc\scene-regression.json"),
    (Join-Path $pwd.Path "doc\scene-contracts.json"),
    (Join-Path $pwd.Path "out\rom.bin"),
    $runtimeMetricsPath,
    $emulatorSessionPath,
    $visualAestheticReportPath,
    $sceneRegressionReportPath,
    $audioValidationReportPath,
    $sceneContractCompileReportPath,
    $resGraphReportPath
)
$freshnessAuditStatus = Get-ObservedReportStatus `
    -ReportPath $freshnessAuditReportPath `
    -DependencyPaths $freshnessAuditDependencies

$sceneCloseoutGateReportPath = Join-Path $pwd.Path "out\logs\scene_closeout_gate_report.json"
$sceneCloseoutGateDependencies = @(
    (Join-Path $pwd.Path "out\rom.bin"),
    $runtimeMetricsPath,
    $emulatorSessionPath,
    $sceneRegressionReportPath,
    $audioValidationReportPath,
    $sceneContractCompileReportPath,
    $resGraphReportPath,
    $freshnessAuditReportPath
)
$sceneCloseoutGateStatus = Get-ObservedReportStatus `
    -ReportPath $sceneCloseoutGateReportPath `
    -DependencyPaths $sceneCloseoutGateDependencies

$results.wrapper_reports = [ordered]@{
    scene_contract_compile = $sceneContractCompileStatus
    res_graph = $resGraphStatus
    freshness_audit = $freshnessAuditStatus
    scene_closeout_gate = $sceneCloseoutGateStatus
}

if ($sceneContractCompileStatus.report_present) {
    if ($sceneContractCompileStatus.stale) {
        Add-Detail $results "WRAPPER_REPORT" "WARNING" "scene_contract_compile_report.json esta stale em relacao ao spec/manifesto de cenas." "scene_contract_compile" $sceneContractCompileStatus.report_path @{
            report_kind = "scene_contract_compile"
            stale = $true
            generated_at = $sceneContractCompileStatus.generated_at
            latest_dependency_utc = $sceneContractCompileStatus.latest_dependency_utc
        }
    }
} else {
    Add-Detail $results "WRAPPER_REPORT" "INFO" "scene_contract_compile_report.json ausente; estado do compiler ainda nao foi observado neste projeto." "scene_contract_compile" $sceneContractCompileReportPath @{
        report_kind = "scene_contract_compile"
        report_present = $false
    }
}

if ($resGraphStatus.report_present) {
    if ($resGraphStatus.stale) {
        Add-Detail $results "WRAPPER_REPORT" "WARNING" "res_graph_report.json esta stale em relacao aos .res do projeto." "res_graph" $resGraphStatus.report_path @{
            report_kind = "res_graph"
            stale = $true
            generated_at = $resGraphStatus.generated_at
            latest_dependency_utc = $resGraphStatus.latest_dependency_utc
        }
    }
} else {
    Add-Detail $results "WRAPPER_REPORT" "INFO" "res_graph_report.json ausente; o grafo canonico de recursos ainda nao foi observado neste projeto." "res_graph" $resGraphReportPath @{
        report_kind = "res_graph"
        report_present = $false
    }
}

if ($freshnessAuditStatus.report_present) {
    if ($freshnessAuditStatus.stale) {
        Add-Detail $results "WRAPPER_REPORT" "WARNING" "freshness_audit_report.json esta stale em relacao aos artefatos canonicos observados." "freshness_audit" $freshnessAuditStatus.report_path @{
            report_kind = "freshness_audit"
            stale = $true
            generated_at = $freshnessAuditStatus.generated_at
            latest_dependency_utc = $freshnessAuditStatus.latest_dependency_utc
        }
    }
} else {
    Add-Detail $results "WRAPPER_REPORT" "INFO" "freshness_audit_report.json ausente; o drift entre evidencias ainda nao foi observado nesta sessao." "freshness_audit" $freshnessAuditReportPath @{
        report_kind = "freshness_audit"
        report_present = $false
    }
}

if ($sceneCloseoutGateStatus.report_present) {
    if ($sceneCloseoutGateStatus.stale) {
        Add-Detail $results "WRAPPER_REPORT" "WARNING" "scene_closeout_gate_report.json esta stale frente aos artefatos de fechamento da cena." "scene_closeout_gate" $sceneCloseoutGateStatus.report_path @{
            report_kind = "scene_closeout_gate"
            stale = $true
            generated_at = $sceneCloseoutGateStatus.generated_at
            latest_dependency_utc = $sceneCloseoutGateStatus.latest_dependency_utc
        }
    }
} else {
    Add-Detail $results "WRAPPER_REPORT" "INFO" "scene_closeout_gate_report.json ausente; nenhum fechamento canonico de cena foi observado ainda." "scene_closeout_gate" $sceneCloseoutGateReportPath @{
        report_kind = "scene_closeout_gate"
        report_present = $false
    }
}

$sourceArtifacts = @($REPORT_FILE)
if (Test-Path -LiteralPath $runtimeMetricsPath) { $sourceArtifacts += $runtimeMetricsPath }
if (Test-Path -LiteralPath $emulatorSessionPath) { $sourceArtifacts += $emulatorSessionPath }
if (Test-Path -LiteralPath $visualAestheticReportPath) { $sourceArtifacts += $visualAestheticReportPath }
if (Test-Path -LiteralPath $visualDeliveryGateReportPath) { $sourceArtifacts += $visualDeliveryGateReportPath }
if (Test-Path -LiteralPath $sceneRegressionReportPath) { $sourceArtifacts += $sceneRegressionReportPath }
if (Test-Path -LiteralPath $audioValidationReportPath) { $sourceArtifacts += $audioValidationReportPath }
if ($sceneContractCompileStatus.report_present) { $sourceArtifacts += $sceneContractCompileStatus.report_path }
if ($resGraphStatus.report_present) { $sourceArtifacts += $resGraphStatus.report_path }
if ($freshnessAuditStatus.report_present) { $sourceArtifacts += $freshnessAuditStatus.report_path }
if ($sceneCloseoutGateStatus.report_present) { $sourceArtifacts += $sceneCloseoutGateStatus.report_path }
if ($changelogStatus.present) { $sourceArtifacts += $changelogStatus.changelog_path }
if ($changelogStatus.latest_build_meta_path) { $sourceArtifacts += $changelogStatus.latest_build_meta_path }
$sourceArtifacts += $existingSessionEvidence
$results.status_panel.source_artifacts = @($sourceArtifacts | Select-Object -Unique)
$results.status_panel.visual_lab_aprovado =
    $results.status_panel.buildado -and
    $results.status_panel.changelog_ready -and
    $results.status_panel.scene_regression_ready -and
    $results.status_panel.visual_gate_ready -and
    $results.status_panel.blastem_gate -and
    (-not $results.status_panel.emulator_evidence_stale)

$hardwareRealGateReady = $results.qa_axes.hardware_real -notin @("nao_testado", "stale", "falha", "nao_medido", "invalido", "ausente")
$results.status_panel.gameplay_rom_aprovada =
    $results.status_panel.visual_lab_aprovado -and
    ($results.qa_axes.gameplay_basico -in @("funcional", "ok")) -and
    ($results.qa_axes.performance -eq "estavel") -and
    ($results.qa_axes.audio -eq "ok") -and
    $hardwareRealGateReady

if ($results.status_panel.visual_lab_aprovado -and -not $results.status_panel.gameplay_rom_aprovada) {
    $msg = "Gate final semantico incompleto: o laboratorio visual esta aprovado, mas a ROM jogavel ainda nao comprovou gameplay/performance/audio/hardware_real para ready_for_aaa."
    Write-Log $msg (Get-BlockingStatusLogLevel "gameplay_gate_incomplete")
    Add-BlockingStatus $results "gameplay_gate_incomplete" $msg "qa" $REPORT_FILE @{
        visual_lab_aprovado = $results.status_panel.visual_lab_aprovado
        gameplay_basico = $results.qa_axes.gameplay_basico
        performance = $results.qa_axes.performance
        audio = $results.qa_axes.audio
        hardware_real = $results.qa_axes.hardware_real
    }
}

$results.status_panel.closing_blockers = @($results.blocking_statuses)
$results.status_panel.ready_for_aaa =
    ($results.summary.errors -eq 0) -and
    $results.status_panel.gameplay_rom_aprovada -and
    $results.status_panel.validado_budget

$results.canonical_summary = New-CanonicalValidationSummary `
    -Results $results `
    -RuntimeMetrics $runtimeMetrics `
    -EmulatorSession $emulatorSession `
    -SceneRegressionStatus $sceneRegressionStatus `
    -AudioValidationStatus $audioValidationStatus `
    -ChangelogStatus $changelogStatus `
    -SceneContractCompileStatus $sceneContractCompileStatus `
    -ResGraphStatus $resGraphStatus `
    -FreshnessAuditStatus $freshnessAuditStatus `
    -SceneCloseoutGateStatus $sceneCloseoutGateStatus

[System.IO.File]::WriteAllText(
    $REPORT_FILE,
    ($results | ConvertTo-Json -Depth 16),
    [System.Text.Encoding]::UTF8
)
Write-Log "Validation finished. Errors: $($results.summary.errors), Warnings: $($results.summary.warnings), Checked: $($results.summary.checked), Recovered: $($results.summary.recovered)"

if ($results.summary.errors -gt 0) { exit 1 }
exit 0
