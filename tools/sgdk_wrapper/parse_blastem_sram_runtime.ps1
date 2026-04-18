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

if (-not (Test-Path -LiteralPath $SramPath)) {
    throw "SRAM nao encontrada: $SramPath"
}

$bytes = [System.IO.File]::ReadAllBytes((Resolve-Path -LiteralPath $SramPath).Path)
if ($bytes.Length -lt ($SramOffset + 12)) {
    throw "SRAM curta demais (len=$($bytes.Length)) para offset 0x$("{0:X}" -f $SramOffset)"
}

$sig = [System.Text.Encoding]::ASCII.GetString($bytes, $SramOffset, 4)
if ($sig -ne "MDRT") {
    throw "Assinatura MDRT nao encontrada em offset 0x$("{0:X}" -f $SramOffset) (encontrado='$sig')"
}

$schema = Read-U16BE -Bytes $bytes -Offset ($SramOffset + 4)
$totalBytes = Read-U16BE -Bytes $bytes -Offset ($SramOffset + 6)
$wordCount = Read-U16BE -Bytes $bytes -Offset ($SramOffset + 8)
$payloadStart = $SramOffset + 10
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

if ($wordCount -lt 64) {
    throw "Dump MDRT invalido: wordCount=$wordCount"
}

$samplesRecorded = [int]$words[9]
if ($samplesRecorded -lt 0) { $samplesRecorded = 0 }

$sampleOffset = 32
$maxSamples = [int]$wordCount - $sampleOffset
if ($samplesRecorded -gt $maxSamples) {
    $samplesRecorded = $maxSamples
}

$samples = @()
for ($i = 0; $i -lt $samplesRecorded; $i++) {
    $samples += [int]$words[$sampleOffset + $i]
}

$samplesSorted = @($samples | Sort-Object)
$avg = 0.0
if ($samplesRecorded -gt 0) {
    $sum = 0.0
    foreach ($v in $samples) { $sum += [double]$v }
    $avg = $sum / [double]$samplesRecorded
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
    scene_id = [int]$words[5]
    frames_seen = [int]$words[8]
    samples_recorded = [int]$samplesRecorded
    over_budget_frames = [int]$words[10]
    cpu_load_max = [int]$words[11]
    cpu_load_jitter_max = [int]$words[13]
    max_scanline_sprites = [int]$words[14]
    fx_peak_concurrency = [int]$words[15]
    sprite_engine_peak = [int]$words[16]
    active_fx = [int]$words[17]
    budget_threshold = [int]$words[23]
    frame_cpu_ratio_avg = [math]::Round($avg, 2)
    frame_cpu_ratio_p95 = [int](Get-Percentile -Sorted $samplesSorted -Ratio 0.95)
    perceptual_check = [ordered]@{
        fluidez = [int]$PerceptualFluidez
        leitura = [int]$PerceptualLeitura
        naturalidade = [int]$PerceptualNaturalidade
        impacto = [int]$PerceptualImpacto
    }
    sram_block = [ordered]@{
        offset = [int]$SramOffset
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
