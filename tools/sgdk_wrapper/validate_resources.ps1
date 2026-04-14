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

function Write-Log($msg, $level = "INFO") {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $fullMsg = "[$timestamp] [$level] $msg"
    Write-Host $fullMsg
    if (-not (Test-Path -LiteralPath $LOG_DIR)) {
        New-Item -ItemType Directory -Force -Path $LOG_DIR | Out-Null
    }
    Add-Content -LiteralPath $DEBUG_LOG $fullMsg
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
    $candidates = @()
    $cmdMagick = Get-Command magick -ErrorAction SilentlyContinue
    if ($cmdMagick -and $cmdMagick.Source -and ($cmdMagick.Source -notmatch 'WindowsApps')) {
        $candidates += $cmdMagick.Source
    }
    $searchRoots = @((Join-Path $env:ProgramFiles 'ImageMagick*'))
    $pf86 = [Environment]::GetEnvironmentVariable('ProgramFiles(x86)')
    if (-not [string]::IsNullOrWhiteSpace($pf86)) {
        $searchRoots += (Join-Path $pf86 'ImageMagick*')
    }
    foreach ($root in $searchRoots) {
        $found = Get-ChildItem -Path $root -Filter 'magick.exe' -Recurse -ErrorAction SilentlyContinue |
            Select-Object -ExpandProperty FullName
        if ($found) { $candidates += $found }
    }
    foreach ($p in $candidates) {
        if ($p -and (Test-Path -LiteralPath $p)) {
            return [string]$p
        }
    }
    return $null
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
    $effectiveColors = if ($isIndexed -and $palEntries -gt 0) { $palEntries } elseif ($isIndexed) { [Math]::Pow(2, $bitDepth) } else { 0 }

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
        "budget_doc_mismatch",
        "changelog_missing",
        "emulator_evidence_stale",
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
    function Test-UsablePythonExe([string]$Path) {
        if (-not $Path -or -not (Test-Path -LiteralPath $Path)) { return $false }
        if ($Path -match 'WindowsApps') { return $false }
        return $true
    }

    foreach ($name in @('python', 'py')) {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if ($cmd -and (Test-UsablePythonExe $cmd.Source)) {
            return $cmd.Source
        }
    }

    $roots = @(
        (Join-Path $env:LOCALAPPDATA 'Programs\Python'),
        (Join-Path $env:ProgramFiles 'Python*')
    )
    $pf86 = [Environment]::GetEnvironmentVariable('ProgramFiles(x86)')
    if (-not [string]::IsNullOrWhiteSpace($pf86)) {
        $roots += (Join-Path $pf86 'Python*')
    }
    foreach ($root in $roots) {
        $exes = Get-ChildItem -Path $root -Filter 'python.exe' -Recurse -ErrorAction SilentlyContinue |
            Where-Object { $_.FullName -notmatch 'WindowsApps' } |
            Sort-Object FullName -Descending
        foreach ($ex in $exes) {
            if (Test-UsablePythonExe $ex.FullName) { return $ex.FullName }
        }
    }

    return $null
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
                        if (-not (Test-Path -LiteralPath $localTracked)) {
                            $result.bootstrap_degradado = $true
                            $result.reason = "missing_tracked_path"
                            break
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
        agent_bootstrapped = $false
        bootstrap_degradado = $false
        placeholder = $false
        parcial = $false
        futuro_arquitetural = $false
        runtime_capture_present = $false
        blastem_gate = $false
        emulator_evidence_stale = $false
        visual_gate_ready = $false
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
$runtimeThresholdsPath = Join-Path $PSScriptRoot "runtime_thresholds.json"
$aestheticAnalyzerPath = $null
$visualLabAnalyzerPath = $null
$visualLabManifestPath = Join-Path $pwd.Path "res\data\visual_lab_case.json"
$aestheticReferenceProfile = if ($env:SGDK_AESTHETIC_REFERENCE_PROFILE) { $env:SGDK_AESTHETIC_REFERENCE_PROFILE } else { "generic-megadrive-elite" }
$pythonPath = Get-PythonPath
$visualAnalyses = @()
$visualLabBenchmark = $null
$visualAnalyzerAvailable = $false
$runtimeMetrics = $null
$emulatorSession = $null
$runtimeThresholds = $null
$workspaceRoot = Resolve-WorkspaceRoot $pwd.Path

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
        if ($info.Colors -gt 16) { $invalidReasons += "$($info.Colors) cores" }

        if ($info.Indexed -and $info.PSObject.Properties.Name -contains 'PaletteEntries' -and $info.PaletteEntries -gt 16) {
            $msg = "Imagem $path tem $($info.PaletteEntries) entradas de paleta PLTE (max 16). Mesmo com poucas cores unicas, indices redundantes impedem deduplicacao de tiles no rescomp e causam corrupcao visual."
            Write-Log $msg "ERROR"
            $results.summary.errors++
            Add-Detail $results "PALETTE_INFLATED" "ERROR" $msg $name $path @{
                paletteEntries = $info.PaletteEntries
                bitDepth = $info.Depth
                uniqueColors = $info.Colors
            }
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
                    $logLevel = switch ($transparencySeverity.level) {
                        "ERROR" { "ERROR" }
                        "WARNING" { "WARN" }
                        default { "INFO" }
                    }
                    $auditMsg = "Imagem ${name}: $($transparencySeverity.message)"
                    Write-Log $auditMsg $logLevel
                    if ($transparencySeverity.level -eq "ERROR") {
                        $results.summary.errors++
                    } elseif ($transparencySeverity.level -eq "WARNING") {
                        $results.summary.warnings++
                    }
                    Add-Detail $results $transparencySeverity.code $transparencySeverity.level $auditMsg $name $path @{
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
            $visualOutputPath = Join-Path $LOG_DIR ("aesthetic_{0}.json" -f $name.ToLowerInvariant())
            try {
                $analysis = Invoke-AestheticAnalysis `
                    -PythonPath $pythonPath `
                    -AnalyzerPath $aestheticAnalyzerPath `
                    -AssetPath $absPath `
                    -Role $visualRole `
                    -ReferenceProfile $aestheticReferenceProfile `
                    -OutputPath $visualOutputPath `
                    -CriticalVisual $criticalVisual

                $analysis | Add-Member -NotePropertyName resource_name -NotePropertyValue $name -Force
                $analysis | Add-Member -NotePropertyName resource_kind -NotePropertyValue $kind -Force
                $analysis | Add-Member -NotePropertyName resource_path -NotePropertyValue $path -Force
                $visualAnalyses += $analysis
            } catch {
                $warnMsg = "Falha ao executar juiz estetico para ${name}: $($_.Exception.Message)"
                Write-Log $warnMsg "WARN"
                $results.summary.warnings++
                Add-Detail $results "VISUAL_ANALYSIS" "WARNING" $warnMsg $name $absPath
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
    Write-Log $msg "ERROR"
    Add-BlockingStatus $results "agent_context_degraded" $msg ".agent" $agentBootstrapStatus.local_agent_dir @{
        canonicalVersion = $agentBootstrapStatus.canonical_version
        localVersion = $agentBootstrapStatus.local_version
        reason = $agentBootstrapStatus.reason
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
    $reportPayload | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $visualAestheticReportPath

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
        $msg = "Juiz estetico sinalizou assets que pedem revisao antes de serem tratados como Elite."
        Write-Log $msg "WARN"
        $results.summary.warnings++
        Add-Detail $results "VISUAL_ELITE" "WARNING" $msg "visual" $visualAestheticReportPath @{
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
$budgetDocMismatch = Get-BudgetDocumentationMismatch -ProjectRoot $pwd.Path
$changelogStatus = Get-ChangelogStatus -ProjectRoot $pwd.Path -RomIdentity $romIdentity
$results.evidence.changelog_status = $changelogStatus

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

$results.status_panel.documentado =
    (Test-Path -LiteralPath (Join-Path $pwd.Path "README.md")) -or
    (Test-Path -LiteralPath (Join-Path $pwd.Path "doc")) -or
    (Test-Path -LiteralPath (Join-Path $pwd.Path "docs"))
$results.status_panel.implementado =
    (Test-Path -LiteralPath (Join-Path $pwd.Path "src")) -or
    (Test-Path -LiteralPath (Join-Path $pwd.Path "inc")) -or
    (Test-Path -LiteralPath (Join-Path $pwd.Path "res"))
$results.status_panel.buildado = Test-Path -LiteralPath $romPath
$results.status_panel.runtime_capture_present = (($runtimeSamplesRecorded -gt 0) -or ($existingSessionEvidence.Count -gt 0)) -and (-not $emulatorEvidenceStale)
$results.status_panel.emulator_evidence_stale = $emulatorEvidenceStale

if ($emulatorEvidenceStale -and $emulatorSession) {
    $msg = ("Evidencia de emulador obsoleta ou insuficiente: {0}." -f $emulatorEvidenceReason)
    Write-Log $msg (Get-BlockingStatusLogLevel "emulator_evidence_stale")
    Add-BlockingStatus $results "emulator_evidence_stale" $msg "emulator" $emulatorSessionPath @{
        reason = $emulatorEvidenceReason
        launchStatus = $sessionLaunchStatus
        evidenceFiles = $existingSessionEvidence.Count
    }
}

$blastEmGate = $false
if ($emulatorSession) {
    $emulatorName = Get-SafeString $emulatorSession.emulator (Get-SafeString $emulatorSession.reference_emulator "")
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
    $hardwareStatus = Get-SafeString $emulatorSession.hardware_real ""
    if ($hardwareStatus) {
        $results.qa_axes.hardware_real = $hardwareStatus
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

$sourceArtifacts = @($REPORT_FILE)
if (Test-Path -LiteralPath $runtimeMetricsPath) { $sourceArtifacts += $runtimeMetricsPath }
if (Test-Path -LiteralPath $emulatorSessionPath) { $sourceArtifacts += $emulatorSessionPath }
if (Test-Path -LiteralPath $visualAestheticReportPath) { $sourceArtifacts += $visualAestheticReportPath }
if ($changelogStatus.present) { $sourceArtifacts += $changelogStatus.changelog_path }
if ($changelogStatus.latest_build_meta_path) { $sourceArtifacts += $changelogStatus.latest_build_meta_path }
$sourceArtifacts += $existingSessionEvidence
$results.status_panel.source_artifacts = @($sourceArtifacts | Select-Object -Unique)
$results.status_panel.closing_blockers = @($results.blocking_statuses)
$results.status_panel.ready_for_aaa =
    ($results.summary.errors -eq 0) -and
    $results.status_panel.buildado -and
    $results.status_panel.changelog_ready -and
    $results.status_panel.visual_gate_ready -and
    $results.status_panel.blastem_gate -and
    (-not $results.status_panel.emulator_evidence_stale)

$results | ConvertTo-Json -Depth 16 | Set-Content -LiteralPath $REPORT_FILE
Write-Log "Validation finished. Errors: $($results.summary.errors), Warnings: $($results.summary.warnings), Checked: $($results.summary.checked), Recovered: $($results.summary.recovered)"

if ($results.summary.errors -gt 0) { exit 1 }
exit 0
