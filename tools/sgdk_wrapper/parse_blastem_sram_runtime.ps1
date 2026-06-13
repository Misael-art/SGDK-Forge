[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$SramPath,
    [Parameter(Mandatory = $false)]
    [string]$OutputPath = "",
    [Parameter(Mandatory = $false)]
    [int]$SramOffset = 0x200,
    [Parameter(Mandatory = $false)]
    [int]$FrameWindow = 1800,
    [Parameter(Mandatory = $false)]
    [int]$TimeoutFrame = 0,
    [Parameter(Mandatory = $false)]
    [int]$PerceptualFluidez = 0,
    [Parameter(Mandatory = $false)]
    [int]$PerceptualLeitura = 0,
    [Parameter(Mandatory = $false)]
    [int]$PerceptualNaturalidade = 0,
    [Parameter(Mandatory = $false)]
    [int]$PerceptualImpacto = 0
)

$ErrorActionPreference = "Stop"

function Read-U16BE {
    param(
        [Parameter(Mandatory = $true)][byte[]]$Bytes,
        [Parameter(Mandatory = $true)][int]$Offset
    )

    if ($Offset -lt 0 -or ($Offset + 1) -ge $Bytes.Length) {
        throw "Offset fora do range: $Offset (len=$($Bytes.Length))"
    }

    return ([int]$Bytes[$Offset] -shl 8) -bor [int]$Bytes[$Offset + 1]
}

function Get-Percentile {
    param(
        [Parameter(Mandatory = $true)][int[]]$Sorted,
        [Parameter(Mandatory = $true)][double]$Ratio
    )

    if (-not $Sorted -or $Sorted.Count -eq 0) {
        return 0
    }

    $count = $Sorted.Count
    $index = [int][math]::Floor((($count - 1) * $Ratio) + 1)
    if ($index -lt 1) { $index = 1 }
    if ($index -gt $count) { $index = $count }
    return $Sorted[$index - 1]
}

function Get-MdrtOffsetCandidates {
    param(
        [Parameter(Mandatory = $false)][int]$PreferredOffset = 0x200
    )

    $offsets = [System.Collections.Generic.List[int]]::new()
    [void]$offsets.Add($PreferredOffset)
    if ($PreferredOffset -eq 0x200) {
        [void]$offsets.Add(0)
    }

    return @($offsets | Select-Object -Unique)
}

if (-not (Test-Path -LiteralPath $SramPath)) {
    throw "SRAM nao encontrada: $SramPath"
}

$bytes = [System.IO.File]::ReadAllBytes((Resolve-Path -LiteralPath $SramPath).Path)
$candidateOffsetsText = ((Get-MdrtOffsetCandidates -PreferredOffset $SramOffset) -join ', ')
$resolvedOffset = $null
$lastSignature = $null
foreach ($candidateOffset in (Get-MdrtOffsetCandidates -PreferredOffset $SramOffset)) {
    if ($bytes.Length -lt ($candidateOffset + 12)) {
        continue
    }

    $candidateSig = [System.Text.Encoding]::ASCII.GetString($bytes, $candidateOffset, 4)
    $lastSignature = $candidateSig
    if ($candidateSig -eq "MDRT") {
        $resolvedOffset = $candidateOffset
        break
    }
}

if ($null -eq $resolvedOffset) {
    throw "Assinatura MDRT nao encontrada nos offsets candidatos $candidateOffsetsText (ultimo='$lastSignature')"
}

$schema = Read-U16BE -Bytes $bytes -Offset ($resolvedOffset + 4)
$totalBytes = Read-U16BE -Bytes $bytes -Offset ($resolvedOffset + 6)
$wordCount = Read-U16BE -Bytes $bytes -Offset ($resolvedOffset + 8)

# Sanity guard: impedir alocacao descontrolada em caso de SRAM corrompida.
# BENCHMARK_VISUAL_LAB/inc/system/runtime_probe.h define MAX_SAMPLES <= 2048
# => maximo real de wordCount esperado e ~2080 (32 header + 2048 samples).
# Tetamos em 8192 como margem de seguranca contra drift de schema.
$MDRT_WORDCOUNT_MIN = 64
$MDRT_WORDCOUNT_MAX = 8192
if ($wordCount -lt $MDRT_WORDCOUNT_MIN) {
    throw "Dump MDRT invalido (wordCount=$wordCount < $MDRT_WORDCOUNT_MIN). Provavel SRAM corrompida ou schema incompativel."
}
if ($wordCount -gt $MDRT_WORDCOUNT_MAX) {
    throw "Dump MDRT invalido (wordCount=$wordCount > $MDRT_WORDCOUNT_MAX). Provavel SRAM corrompida."
}

$payloadStart = $resolvedOffset + 10
$expectedSize = $payloadStart + ($wordCount * 2)
if ($bytes.Length -lt $expectedSize) {
    throw "SRAM nao contem payload completo: precisa=$expectedSize len=$($bytes.Length) wordCount=$wordCount"
}

$words = New-Object int[] $wordCount
$pos = $payloadStart
for ($i = 0; $i -lt $wordCount; $i++) {
    $words[$i] = Read-U16BE -Bytes $bytes -Offset $pos
    $pos += 2
}

$samplesRecorded = [int]$words[9]
if ($samplesRecorded -lt 0) { $samplesRecorded = 0 }

$sampleOffset = 32
$maxSamples = [int]$wordCount - $sampleOffset
if ($samplesRecorded -gt $maxSamples) {
    $samplesRecorded = $maxSamples
}

# List<int> evita O(n^2) do operador "+=" em arrays PowerShell (ate 1800 iteracoes).
$samples = [System.Collections.Generic.List[int]]::new($samplesRecorded)
for ($i = 0; $i -lt $samplesRecorded; $i++) {
    [void]$samples.Add([int]$words[$sampleOffset + $i])
}

$samplesSorted = @($samples | Sort-Object)
$avg = 0.0
if ($samplesRecorded -gt 0) {
    $sum = 0.0
    foreach ($v in $samples) { $sum += [double]$v }
    $avg = $sum / [double]$samplesRecorded
}

$sceneId = [int]$words[5]
$framesSeen = [int]$words[8]
$overBudgetFrames = [int]$words[10]
$cpuLoadMax = [int]$words[11]
$cpuLoadJitterMax = [int]$words[13]
$maxScanlineSprites = [int]$words[14]
$fxPeakConcurrency = [int]$words[15]
$spriteEnginePeak = [int]$words[16]
$activeFx = [int]$words[17]
$budgetThreshold = [int]$words[23]
if ($budgetThreshold -le 0) {
    $budgetThreshold = 100
}
if ($cpuLoadMax -le 0 -and $samplesRecorded -gt 0) {
    $cpuLoadMax = ($samples | Measure-Object -Maximum).Maximum
}

$frameMetrics = [System.Collections.Generic.List[object]]::new()
if ($samplesRecorded -gt 0) {
    $sampleStep = if ($samplesRecorded -gt 0) {
        [Math]::Max(1, [int][Math]::Floor($framesSeen / $samplesRecorded))
    } else {
        1
    }

    $peakSpriteIndex = $samplesRecorded - 1
    $peakCpuIndex = if ($samplesRecorded -gt 0) {
        [Array]::IndexOf([int[]]$samples.ToArray(), $cpuLoadMax)
    } else {
        -1
    }
    if ($peakCpuIndex -lt 0) {
        $peakCpuIndex = $peakSpriteIndex
    }

    for ($i = 0; $i -lt $samplesRecorded; $i++) {
        $sampleValue = [int]$samples[$i]
        $frameMetrics.Add([ordered]@{
            scene_id                  = $sceneId
            frame_index               = [int](($i + 1) * $sampleStep)
            cpu_load_ratio            = $sampleValue
            cpu_frame_overrun_flag    = ($sampleValue -gt $budgetThreshold)
            sprite_count              = if ($i -eq $peakSpriteIndex) { $spriteEnginePeak } else { 0 }
            max_sprites_per_scanline  = if ($i -eq $peakSpriteIndex) { $maxScanlineSprites } else { 0 }
            fx_concurrency            = if ($i -eq $peakSpriteIndex) { $fxPeakConcurrency } else { $activeFx }
            measurement_source        = 'mdrt_sample_series'
            capture_status            = if ($samplesRecorded -ge $FrameWindow) { 'ok' } else { 'partial' }
        }) | Out-Null
    }

    if ($peakCpuIndex -ge 0 -and $peakCpuIndex -lt $frameMetrics.Count) {
        $frameMetrics[$peakCpuIndex].cpu_load_ratio = $cpuLoadMax
    }
}

$report = [ordered]@{
    schema_version = [int]$words[2]
    source = "blastem_sram"
    capture_status = if ($samplesRecorded -ge $FrameWindow) { "ok" } else { "partial" }
    frame_window = [int]$FrameWindow
    timeout_frame = [int]$TimeoutFrame
    probe_magic_hi = [int]$words[0]
    probe_magic_lo = [int]$words[1]
    target_fps = [int]$words[4]
    scene_id = $sceneId
    frames_seen = $framesSeen
    samples_recorded = [int]$samplesRecorded
    over_budget_frames = $overBudgetFrames
    cpu_load_max = $cpuLoadMax
    cpu_load_jitter_max = $cpuLoadJitterMax
    max_scanline_sprites = $maxScanlineSprites
    fx_peak_concurrency = $fxPeakConcurrency
    sprite_engine_peak = $spriteEnginePeak
    active_fx = $activeFx
    budget_threshold = $budgetThreshold
    frame_cpu_ratio_avg = [math]::Round($avg, 2)
    frame_cpu_ratio_p95 = if ($samplesSorted.Count -gt 0) {
        [int](Get-Percentile -Sorted $samplesSorted -Ratio 0.95)
    } else {
        0
    }
    frame_metrics_kind = 'mdrt_sample_series'
    frame_metrics = @($frameMetrics)
    perceptual_check = [ordered]@{
        fluidez = [int]$PerceptualFluidez
        leitura = [int]$PerceptualLeitura
        naturalidade = [int]$PerceptualNaturalidade
        impacto = [int]$PerceptualImpacto
    }
    sram_block = [ordered]@{
        offset = [int]$resolvedOffset
        schema = [int]$schema
        total_bytes = [int]$totalBytes
        word_count = [int]$wordCount
    }
}

if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $OutputPath = Join-Path (Split-Path -Parent (Resolve-Path -LiteralPath $SramPath).Path) "runtime_metrics.json"
}

$outDir = Split-Path -Parent $OutputPath
if (-not (Test-Path -LiteralPath $outDir)) {
    New-Item -ItemType Directory -Force -Path $outDir | Out-Null
}

$report | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $OutputPath -Encoding UTF8
Get-Content -LiteralPath $OutputPath
