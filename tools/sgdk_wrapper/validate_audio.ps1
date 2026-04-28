[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$WorkDir = "",
    [Parameter(Mandatory = $false)]
    [switch]$Fix,
    [Parameter(Mandatory = $false)]
    [int]$MaxAudioPercent = 40,
    [Parameter(Mandatory = $false)]
    [int]$RomSizeKB = 4096
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

try {
    if (-not [string]::IsNullOrWhiteSpace($WorkDir)) {
        Set-Location -LiteralPath $WorkDir
    }
} catch {
    Write-Error ("[ERROR] validate_audio.ps1: failed to Set-Location to '{0}'. Details: {1}" -f $WorkDir, $_.Exception.Message)
    exit 1
}

$ProjectRoot = (Get-Location).Path
$LOG_DIR = Join-Path $ProjectRoot "out\logs"
$REPORT_FILE = Join-Path $LOG_DIR "audio_validation_report.json"
$DEBUG_LOG = Join-Path $LOG_DIR "validate_audio_debug.log"

function Ensure-Directory {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Container)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }
}

function Write-Log {
    param(
        [Parameter(Mandatory = $true)][string]$Message,
        [string]$Level = "INFO"
    )

    Ensure-Directory -Path $LOG_DIR
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $fullMessage = "[$timestamp] [$Level] $Message"
    Write-Host $fullMessage
    Add-Content -LiteralPath $DEBUG_LOG -Value $fullMessage
}

function Get-ProjectRelativePath {
    param([Parameter(Mandatory = $true)][string]$Path)
    $root = [System.IO.Path]::GetFullPath($ProjectRoot).TrimEnd('\')
    $full = [System.IO.Path]::GetFullPath($Path)
    $relative = [System.IO.Path]::GetRelativePath($root, $full)
    return $relative -replace '\\', '/'
}

function Resolve-DeclaredAssetPath {
    param(
        [Parameter(Mandatory = $true)][string]$BaseDir,
        [Parameter(Mandatory = $true)][string]$DeclaredPath
    )

    if ([System.IO.Path]::IsPathRooted($DeclaredPath)) {
        return [System.IO.Path]::GetFullPath($DeclaredPath)
    }

    return [System.IO.Path]::GetFullPath((Join-Path $BaseDir $DeclaredPath))
}

function Get-NullableIso8601Utc {
    param([Nullable[datetime]]$Value)
    if ($null -eq $Value) {
        return $null
    }
    return $Value.ToUniversalTime().ToString("o")
}

function Update-LatestTimestamp {
    param(
        [Nullable[datetime]]$Current,
        [string]$CandidatePath
    )

    if (-not (Test-Path -LiteralPath $CandidatePath -PathType Leaf)) {
        return $Current
    }

    $candidate = (Get-Item -LiteralPath $CandidatePath).LastWriteTimeUtc
    if (($null -eq $Current) -or ($candidate -gt $Current)) {
        return $candidate
    }

    return $Current
}

function Get-PlaybackEstimate {
    param(
        [Parameter(Mandatory = $true)][pscustomobject]$Declaration,
        [pscustomobject]$WaveInfo
    )

    $sourceSize = [int64]$Declaration.source_size_bytes

    if ($Declaration.resource_kind -in @("XGM", "XGM2")) {
        return [pscustomobject]@{
            estimated_rom_bytes = $sourceSize
            estimate_basis = "declared_music_source"
            target_driver = $Declaration.driver
            target_rate = $null
        }
    }

    if ($Declaration.resource_kind -eq "BIN_AUDIO") {
        return [pscustomobject]@{
            estimated_rom_bytes = $sourceSize
            estimate_basis = "declared_raw_asset"
            target_driver = "BIN_AUDIO"
            target_rate = $null
        }
    }

    if ($Declaration.resource_kind -ne "WAV" -or $null -eq $WaveInfo) {
        return [pscustomobject]@{
            estimated_rom_bytes = $sourceSize
            estimate_basis = "source_size_fallback"
            target_driver = $Declaration.driver
            target_rate = $null
        }
    }

    $durationSeconds = 0.0
    if ($WaveInfo.byte_rate -gt 0 -and $WaveInfo.data_size -gt 0) {
        $durationSeconds = [double]$WaveInfo.data_size / [double]$WaveInfo.byte_rate
    }

    if ($durationSeconds -le 0) {
        return [pscustomobject]@{
            estimated_rom_bytes = $sourceSize
            estimate_basis = "source_size_fallback"
            target_driver = $Declaration.driver
            target_rate = $null
        }
    }

    $driver = ($Declaration.driver | ForEach-Object { $_ }).ToString().ToUpperInvariant()
    $targetRate = $null
    $bytesPerOutputSample = 1.0
    $estimateBasis = "source_size_fallback"

    switch ($driver) {
        "PCM" {
            $targetRate = $(if ($Declaration.declared_rate) { [int]$Declaration.declared_rate } elseif ($WaveInfo.sample_rate -gt 0) { [int]$WaveInfo.sample_rate } else { 16000 })
            $estimateBasis = "pcm_runtime_estimate"
        }
        "PCM4" {
            $targetRate = 16000
            $estimateBasis = "pcm4_runtime_estimate"
        }
        "DPCM2" {
            $targetRate = 22050
            $bytesPerOutputSample = 0.5
            $estimateBasis = "dpcm2_runtime_estimate"
        }
        "XGM" {
            $targetRate = $(if ($Declaration.declared_rate) { [int]$Declaration.declared_rate } else { 14000 })
            $estimateBasis = "xgm_pcm_estimate"
        }
        "XGM2" {
            $targetRate = $(if ($Declaration.declared_rate) { [int]$Declaration.declared_rate } else { 13300 })
            $estimateBasis = "xgm2_pcm_estimate"
        }
        default {
            return [pscustomobject]@{
                estimated_rom_bytes = $sourceSize
                estimate_basis = "source_size_fallback"
                target_driver = $driver
                target_rate = $null
            }
        }
    }

    $estimatedBytes = [int64][Math]::Ceiling($durationSeconds * [double]$targetRate * $bytesPerOutputSample)
    return [pscustomobject]@{
        estimated_rom_bytes = $estimatedBytes
        estimate_basis = $estimateBasis
        target_driver = $driver
        target_rate = $targetRate
    }
}

function Get-WaveInfo {
    param([Parameter(Mandatory = $true)][string]$FilePath)

    $stream = $null
    $reader = $null

    try {
        $stream = [System.IO.File]::Open($FilePath, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::Read)
        $reader = New-Object System.IO.BinaryReader($stream)

        $riff = [System.Text.Encoding]::ASCII.GetString($reader.ReadBytes(4))
        if ($riff -ne "RIFF") {
            throw "RIFF header ausente."
        }

        [void]$reader.ReadUInt32()
        $wave = [System.Text.Encoding]::ASCII.GetString($reader.ReadBytes(4))
        if ($wave -ne "WAVE") {
            throw "WAVE header ausente."
        }

        $fmt = $null
        $dataSize = $null

        while ($reader.BaseStream.Position -le ($reader.BaseStream.Length - 8)) {
            $chunkId = [System.Text.Encoding]::ASCII.GetString($reader.ReadBytes(4))
            $chunkSize = [int64]$reader.ReadUInt32()
            $chunkStart = $reader.BaseStream.Position

            switch ($chunkId) {
                "fmt " {
                    $formatTag = $reader.ReadUInt16()
                    $channels = $reader.ReadUInt16()
                    $sampleRate = [int64]$reader.ReadUInt32()
                    $byteRate = [int64]$reader.ReadUInt32()
                    $blockAlign = $reader.ReadUInt16()
                    $bitsPerSample = $reader.ReadUInt16()

                    $fmt = [pscustomobject]@{
                        format_tag = [int]$formatTag
                        channels = [int]$channels
                        sample_rate = [int]$sampleRate
                        byte_rate = [int]$byteRate
                        block_align = [int]$blockAlign
                        bits_per_sample = [int]$bitsPerSample
                    }
                }
                "data" {
                    $dataSize = $chunkSize
                }
            }

            $reader.BaseStream.Position = $chunkStart + $chunkSize
            if (($chunkSize % 2) -ne 0 -and $reader.BaseStream.Position -lt $reader.BaseStream.Length) {
                $reader.BaseStream.Position++
            }

            if ($fmt -and $null -ne $dataSize) {
                break
            }
        }

        if (-not $fmt) {
            throw "Chunk 'fmt ' ausente."
        }

        return [pscustomobject]@{
            format_tag = $fmt.format_tag
            channels = $fmt.channels
            sample_rate = $fmt.sample_rate
            byte_rate = $fmt.byte_rate
            block_align = $fmt.block_align
            bits_per_sample = $fmt.bits_per_sample
            data_size = $(if ($null -ne $dataSize) { [int64]$dataSize } else { 0 })
            duration_seconds = $(if ($fmt.byte_rate -gt 0 -and $null -ne $dataSize) { [Math]::Round(([double]$dataSize / [double]$fmt.byte_rate), 3) } else { 0.0 })
        }
    } finally {
        if ($reader) { $reader.Close() }
        if ($stream) { $stream.Dispose() }
    }
}

function Get-SignedPcm8Analysis {
    param([Parameter(Mandatory = $true)][string]$FilePath)

    $bytes = [System.IO.File]::ReadAllBytes($FilePath)
    if ($bytes.Length -lt 16) {
        return $null
    }

    $readSize = [Math]::Min($bytes.Length, 4096)
    $sampleValues = New-Object System.Collections.Generic.List[int]
    for ($i = 0; $i -lt $readSize; $i++) {
        $value = [int]$bytes[$i]
        if ($value -gt 127) { $value -= 256 }
        [void]$sampleValues.Add($value)
    }

    $avg = ($sampleValues | Measure-Object -Average).Average
    $clipCount = ($sampleValues | Where-Object { $_ -eq 127 -or $_ -eq -128 }).Count
    $clipPct = $(if ($readSize -gt 0) { [Math]::Round(($clipCount / $readSize) * 100, 2) } else { 0.0 })
    $minVal = ($sampleValues | Measure-Object -Minimum).Minimum
    $maxVal = ($sampleValues | Measure-Object -Maximum).Maximum
    $dynamicRange = $maxVal - $minVal

    $tailSamples = New-Object System.Collections.Generic.List[int]
    for ($i = ($bytes.Length - 8); $i -lt $bytes.Length; $i++) {
        $value = [int]$bytes[$i]
        if ($value -gt 127) { $value -= 256 }
        [void]$tailSamples.Add([Math]::Abs($value))
    }
    $tailAvg = ($tailSamples | Measure-Object -Average).Average

    return [pscustomobject]@{
        dc_offset = [Math]::Round([double]$avg, 2)
        clip_percent = $clipPct
        dynamic_range = [int]$dynamicRange
        tail_amplitude_avg = [Math]::Round([double]$tailAvg, 2)
    }
}

function Test-SupportedAudioBinDeclaration {
    param(
        [Parameter(Mandatory = $true)][string]$DeclaredPath
    )

    $ext = [System.IO.Path]::GetExtension($DeclaredPath).ToLowerInvariant()
    return $ext -in @(".raw", ".pcm", ".dpcm")
}

function Get-AudioDeclarations {
    $resRoot = Join-Path $ProjectRoot "res"
    if (-not (Test-Path -LiteralPath $resRoot -PathType Container)) {
        return @()
    }

    $resFiles = Get-ChildItem -LiteralPath $resRoot -Filter "*.res" -Recurse -ErrorAction SilentlyContinue
    $declarations = @()
    $linePattern = '^\s*(?<kind>WAV|XGM2|XGM|BIN)\s+(?<name>\w+)\s+(?:"(?<quoted>[^"]+)"|(?<bare>\S+))(?:\s+(?<arg1>[A-Za-z0-9_]+))?(?:\s+(?<arg2>\d+))?'

    foreach ($resFile in $resFiles) {
        $report.inputs.res_files += (Get-ProjectRelativePath $resFile.FullName)
        $script:LatestResWriteUtc = Update-LatestTimestamp -Current $script:LatestResWriteUtc -CandidatePath $resFile.FullName

        $lineNumber = 0
        foreach ($line in (Get-Content -LiteralPath $resFile.FullName -ErrorAction SilentlyContinue)) {
            $lineNumber++
            $trimmed = $line.Trim()
            if ([string]::IsNullOrWhiteSpace($trimmed) -or $trimmed.StartsWith("//")) {
                continue
            }

            if ($trimmed -notmatch $linePattern) {
                continue
            }

            $kind = $matches["kind"].ToUpperInvariant()
            $resourceName = $matches["name"]
            $declaredPath = $(if ($matches["quoted"]) { $matches["quoted"] } else { $matches["bare"] })
            $arg1 = $matches["arg1"]
            $arg2 = $matches["arg2"]

            if ($kind -eq "BIN" -and -not (Test-SupportedAudioBinDeclaration -DeclaredPath $declaredPath)) {
                continue
            }

            $resolvedPath = Resolve-DeclaredAssetPath -BaseDir $resFile.Directory.FullName -DeclaredPath $declaredPath
            $exists = Test-Path -LiteralPath $resolvedPath -PathType Leaf
            if ($exists) {
                $script:LatestSourceWriteUtc = Update-LatestTimestamp -Current $script:LatestSourceWriteUtc -CandidatePath $resolvedPath
            }

            $declarations += [pscustomobject]@{
                resource_kind = $(if ($kind -eq "BIN") { "BIN_AUDIO" } else { $kind })
                resource_name = $resourceName
                source_res_file = $resFile.FullName
                source_res_path = Get-ProjectRelativePath $resFile.FullName
                source_res_line = $lineNumber
                declared_path = $declaredPath
                resolved_path = $resolvedPath
                resolved_relative_path = $(if ($exists) { Get-ProjectRelativePath $resolvedPath } else { [System.IO.Path]::GetRelativePath($ProjectRoot, $resolvedPath) -replace '\\', '/' })
                driver = $(if ($kind -eq "WAV") { $(if ($arg1) { $arg1 } else { "UNKNOWN" }) } elseif ($kind -eq "BIN") { "BIN_AUDIO" } else { $kind })
                declared_rate = $(if ($kind -eq "WAV" -and $arg2) { [int]$arg2 } else { $null })
                source_exists = [bool]$exists
                source_extension = [System.IO.Path]::GetExtension($resolvedPath).ToLowerInvariant()
                source_size_bytes = $(if ($exists) { [int64](Get-Item -LiteralPath $resolvedPath).Length } else { 0 })
            }
        }
    }

    return $declarations
}

function Add-Issue {
    param(
        [Parameter(Mandatory = $true)][string]$File,
        [Parameter(Mandatory = $true)][string]$Severity,
        [Parameter(Mandatory = $true)][string]$Message,
        [bool]$Autofix = $false
    )

    $report.issues += @{
        file = $File
        severity = $Severity
        message = $Message
        autofix = $Autofix
    }
    $report.summary.issues_count++
    if ($Severity -eq "CRITICAL") {
        $report.summary.pass = $false
    }

    $level = $(if ($Severity -eq "CRITICAL") { "ERROR" } elseif ($Severity -eq "INFO") { "INFO" } else { "WARN" })
    Write-Log -Message ("{0}: {1}: {2}" -f $Severity, $File, $Message) -Level $level
}

Ensure-Directory -Path $LOG_DIR
if (Test-Path -LiteralPath $DEBUG_LOG) {
    Remove-Item -LiteralPath $DEBUG_LOG -Force
}

$script:LatestSourceWriteUtc = $null
$script:LatestResWriteUtc = $null
$report = @{
    timestamp = (Get-Date).ToUniversalTime().ToString("o")
    project_dir = $ProjectRoot
    inputs = @{
        res_files = @()
        declared_audio_resources = 0
        latest_source_write_utc = $null
        latest_res_write_utc = $null
        measurement_basis = "declared_resources_estimate"
    }
    declared_resources = @()
    xgm_files = @()
    samples = @()
    issues = @()
    summary = @{
        total_declarations = 0
        total_samples = 0
        total_xgm = 0
        total_source_audio_bytes = 0
        total_audio_bytes = 0
        rom_budget_kb = $RomSizeKB
        audio_percent = 0.0
        budget_status = "UNKNOWN"
        issues_count = 0
        fixed_count = 0
        pass = $true
    }
}

Write-Log -Message "=== Audio Validation Start ==="
Write-Log -Message ("WorkDir: {0}" -f $ProjectRoot)
Write-Log -Message ("ROM Budget: {0}KB, Max Audio: {1}%" -f $RomSizeKB, $MaxAudioPercent)

$audioDeclarations = @(Get-AudioDeclarations)
$report.inputs.declared_audio_resources = $audioDeclarations.Count
$report.inputs.latest_source_write_utc = Get-NullableIso8601Utc $script:LatestSourceWriteUtc
$report.inputs.latest_res_write_utc = Get-NullableIso8601Utc $script:LatestResWriteUtc
$report.summary.total_declarations = $audioDeclarations.Count

Write-Log -Message ("Found {0} declared audio resource(s)." -f $audioDeclarations.Count)

$totalEstimatedRomBytes = 0L
$totalSourceBytes = 0L

foreach ($declaration in $audioDeclarations) {
    $resourceKey = "{0}:{1}" -f $declaration.resource_kind, $declaration.resource_name
    $totalSourceBytes += [int64]$declaration.source_size_bytes

    $entry = [ordered]@{
        resource_kind = $declaration.resource_kind
        resource_name = $declaration.resource_name
        driver = $declaration.driver
        declared_rate = $declaration.declared_rate
        source_res_file = $declaration.source_res_path
        source_res_line = $declaration.source_res_line
        declared_path = $declaration.declared_path
        resolved_path = $declaration.resolved_relative_path
        source_exists = [bool]$declaration.source_exists
        source_extension = $declaration.source_extension
        source_size_bytes = [int64]$declaration.source_size_bytes
    }

    if (-not $declaration.source_exists) {
        Add-Issue -File $resourceKey -Severity "CRITICAL" -Message ("Arquivo declarado nao encontrado: {0}" -f $declaration.resolved_relative_path)
        $entry["estimated_rom_bytes"] = 0
        $entry["estimate_basis"] = "missing_source"
        $report.declared_resources += [pscustomobject]$entry
        continue
    }

    switch ($declaration.resource_kind) {
        "WAV" {
            $waveInfo = $null
            try {
                $waveInfo = Get-WaveInfo -FilePath $declaration.resolved_path
                $entry["wave"] = $waveInfo
                if ($waveInfo.channels -ne 1) {
                    Add-Issue -File $resourceKey -Severity "WARN" -Message ("WAV declarado com {0} canais. AAA pede fonte mono para controle de conversao e budget." -f $waveInfo.channels)
                }
                if ($waveInfo.format_tag -ne 1) {
                    Add-Issue -File $resourceKey -Severity "WARN" -Message ("WAV usa format_tag={0}. Prefira PCM linear (format_tag=1) antes da integracao." -f $waveInfo.format_tag)
                }
                if ($waveInfo.bits_per_sample -lt 8) {
                    Add-Issue -File $resourceKey -Severity "WARN" -Message ("WAV com {0} bits por sample. Qualidade de fonte baixa para conversao AAA." -f $waveInfo.bits_per_sample)
                }
            } catch {
                Add-Issue -File $resourceKey -Severity "CRITICAL" -Message ("Falha ao ler WAV: {0}" -f $_.Exception.Message)
            }

            $estimate = Get-PlaybackEstimate -Declaration $declaration -WaveInfo $waveInfo
            $entry["estimated_rom_bytes"] = [int64]$estimate.estimated_rom_bytes
            $entry["estimate_basis"] = $estimate.estimate_basis
            $entry["target_driver"] = $estimate.target_driver
            $entry["target_rate"] = $estimate.target_rate
            $totalEstimatedRomBytes += [int64]$estimate.estimated_rom_bytes
            $report.samples += [pscustomobject]$entry
            $report.summary.total_samples++
        }
        "BIN_AUDIO" {
            $ext = $declaration.source_extension
            $entry["estimated_rom_bytes"] = [int64]$declaration.source_size_bytes
            $entry["estimate_basis"] = "declared_raw_asset"
            $totalEstimatedRomBytes += [int64]$declaration.source_size_bytes

            if ($ext -in @(".raw", ".pcm")) {
                if (($declaration.source_size_bytes % 256) -ne 0) {
                    $padding = 256 - ($declaration.source_size_bytes % 256)
                    if ($Fix) {
                        try {
                            $paddingBytes = [byte[]]::new($padding)
                            for ($i = 0; $i -lt $padding; $i++) {
                                $paddingBytes[$i] = 0x80
                            }
                            [System.IO.File]::AppendAllBytes($declaration.resolved_path, $paddingBytes)
                            $declaration.source_size_bytes += $padding
                            $entry["source_size_bytes"] = [int64]$declaration.source_size_bytes
                            $entry["estimated_rom_bytes"] = [int64]$declaration.source_size_bytes
                            $totalEstimatedRomBytes += $padding
                            $totalSourceBytes += $padding
                            $report.summary.fixed_count++
                            Add-Issue -File $resourceKey -Severity "INFO" -Message ("FIXED: adicionados {0} bytes de padding para alinhamento de 256 bytes." -f $padding) -Autofix $true
                        } catch {
                            Add-Issue -File $resourceKey -Severity "CRITICAL" -Message ("Falha ao corrigir alinhamento de 256 bytes: {0}" -f $_.Exception.Message)
                        }
                    } else {
                        Add-Issue -File $resourceKey -Severity "CRITICAL" -Message ("Asset bruto nao alinhado a 256 bytes; faltam {0} bytes de padding." -f $padding)
                    }
                }

                $analysis = Get-SignedPcm8Analysis -FilePath $declaration.resolved_path
                if ($analysis) {
                    $entry["analysis"] = $analysis
                    if ([Math]::Abs($analysis.dc_offset) -gt 10) {
                        Add-Issue -File $resourceKey -Severity "WARN" -Message ("DC offset detectado (avg={0})." -f $analysis.dc_offset)
                    }
                    if ($analysis.clip_percent -gt 2) {
                        Add-Issue -File $resourceKey -Severity "WARN" -Message ("Clipping detectado ({0}% das amostras no limite)." -f $analysis.clip_percent)
                    }
                    if ($analysis.dynamic_range -lt 80) {
                        Add-Issue -File $resourceKey -Severity "WARN" -Message ("Dynamic range baixo ({0})." -f $analysis.dynamic_range)
                    }
                    if ($analysis.tail_amplitude_avg -gt 20) {
                        Add-Issue -File $resourceKey -Severity "WARN" -Message ("Risco de click no fim do sample (tail amplitude avg={0})." -f $analysis.tail_amplitude_avg)
                    }
                }
            } elseif ($ext -eq ".dpcm") {
                if (($declaration.source_size_bytes % 128) -ne 0) {
                    $padding = 128 - ($declaration.source_size_bytes % 128)
                    if ($Fix) {
                        try {
                            $paddingBytes = [byte[]]::new($padding)
                            [System.IO.File]::AppendAllBytes($declaration.resolved_path, $paddingBytes)
                            $declaration.source_size_bytes += $padding
                            $entry["source_size_bytes"] = [int64]$declaration.source_size_bytes
                            $entry["estimated_rom_bytes"] = [int64]$declaration.source_size_bytes
                            $totalEstimatedRomBytes += $padding
                            $totalSourceBytes += $padding
                            $report.summary.fixed_count++
                            Add-Issue -File $resourceKey -Severity "INFO" -Message ("FIXED: adicionados {0} bytes de padding para alinhamento DPCM de 128 bytes." -f $padding) -Autofix $true
                        } catch {
                            Add-Issue -File $resourceKey -Severity "CRITICAL" -Message ("Falha ao corrigir alinhamento DPCM: {0}" -f $_.Exception.Message)
                        }
                    } else {
                        Add-Issue -File $resourceKey -Severity "CRITICAL" -Message ("Asset DPCM nao alinhado a 128 bytes; faltam {0} bytes de padding." -f $padding)
                    }
                }
            }

            $report.samples += [pscustomobject]$entry
            $report.summary.total_samples++
        }
        default {
            $estimate = Get-PlaybackEstimate -Declaration $declaration -WaveInfo $null
            $entry["estimated_rom_bytes"] = [int64]$estimate.estimated_rom_bytes
            $entry["estimate_basis"] = $estimate.estimate_basis
            $totalEstimatedRomBytes += [int64]$estimate.estimated_rom_bytes
            $report.xgm_files += [pscustomobject]$entry
            $report.summary.total_xgm++
        }
    }

    $report.declared_resources += [pscustomobject]$entry
}

$report.summary.total_source_audio_bytes = [int64]$totalSourceBytes
$report.summary.total_audio_bytes = [int64]$totalEstimatedRomBytes

$romTotalBytes = [int64]$RomSizeKB * 1024
$audioPercent = $(if ($romTotalBytes -gt 0) {
    [Math]::Round(([double]$totalEstimatedRomBytes / [double]$romTotalBytes) * 100, 2)
} else {
    0.0
})
$report.summary.audio_percent = $audioPercent

if ($audioPercent -gt $MaxAudioPercent) {
    $report.summary.budget_status = "OVER_BUDGET"
    $report.summary.pass = $false
    Add-Issue -File "ROM_BUDGET" -Severity "CRITICAL" -Message ("Audio estimado em {0}% da ROM (limite {1}%)." -f $audioPercent, $MaxAudioPercent)
} elseif ($audioPercent -gt ($MaxAudioPercent * 0.75)) {
    $report.summary.budget_status = "WARNING"
    Add-Issue -File "ROM_BUDGET" -Severity "WARN" -Message ("Audio em {0}% da ROM; zona de alerta." -f $audioPercent)
} else {
    $report.summary.budget_status = "OK"
}

Write-Log -Message "=== Validation Summary ==="
Write-Log -Message ("Declarations: {0}" -f $report.summary.total_declarations)
Write-Log -Message ("Samples: {0}" -f $report.summary.total_samples)
Write-Log -Message ("Music assets: {0}" -f $report.summary.total_xgm)
Write-Log -Message ("Estimated ROM audio: {0} KB ({1}% of {2}KB)" -f ([Math]::Round($totalEstimatedRomBytes / 1024, 2)), $audioPercent, $RomSizeKB)
Write-Log -Message ("Issues: {0}" -f $report.summary.issues_count)
Write-Log -Message ("Fixed: {0}" -f $report.summary.fixed_count)
Write-Log -Message ("Pass: {0}" -f $report.summary.pass)

$report | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $REPORT_FILE -Encoding UTF8
Write-Log -Message ("Report written to {0}" -f $REPORT_FILE)

if ($report.summary.pass) {
    Write-Host "`n[PASS] Audio validation passed." -ForegroundColor Green
    exit 0
}

Write-Host ("`n[FAIL] Audio validation failed with {0} issues." -f $report.summary.issues_count) -ForegroundColor Red
foreach ($issue in ($report.issues | Where-Object { $_.severity -eq "CRITICAL" })) {
    Write-Host ("  CRITICAL: {0} - {1}" -f $issue.file, $issue.message) -ForegroundColor Red
}
exit 1
