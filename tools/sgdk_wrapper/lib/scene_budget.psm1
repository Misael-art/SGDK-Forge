<#
.SYNOPSIS
    Scene budget analysis module for the AAA agent ecosystem.
.DESCRIPTION
    Provides functions to import runtime metrics, measure per-scene budget,
    evaluate against thresholds, and generate budget summaries.

    This module does NOT modify any existing wrapper behavior.
    DECISION PENDING: Canonical budget thresholds per scene type are not yet
    defined. Current thresholds are conservative defaults for observation mode.
#>

Set-StrictMode -Version Latest

# Mega Drive hardware limits (conservative reference values)
$script:HW_MAX_SPRITES = 80
$script:HW_MAX_SPRITES_PER_SCANLINE = 20
$script:HW_VRAM_TOTAL = 65536  # 64KB
$script:HW_DMA_BUDGET_VBLANK = 7500  # approximate bytes per VBlank DMA window

# Default thresholds (observation mode — these are NOT canonical gates)
$script:DefaultThresholds = @{
    sprite_count_warn         = 64
    sprite_count_error        = 80
    sprites_per_scanline_warn = 16
    sprites_per_scanline_error = 20
    vram_usage_warn           = 52000  # ~80% of 64KB
    vram_usage_error          = 62000  # ~95% of 64KB
    dma_bytes_warn            = 6000
    dma_bytes_error           = 7500
}

# ---------------------------------------------------------------------------
# Import-SceneBudgetMetrics
# ---------------------------------------------------------------------------
function Import-SceneBudgetMetrics {
    <#
    .SYNOPSIS
        Loads runtime metrics from a JSON file.
    .PARAMETER MetricsPath
        Absolute path to a runtime_metrics.json or similar metrics file.
    .OUTPUTS
        Parsed metrics object, or $null if invalid/missing.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$MetricsPath
    )

    if (-not (Test-Path -LiteralPath $MetricsPath)) {
        Write-Warning "Metrics file not found: $MetricsPath"
        return $null
    }

    try {
        $raw = Get-Content -LiteralPath $MetricsPath -Raw -Encoding UTF8
        return ($raw | ConvertFrom-Json)
    } catch {
        Write-Warning "Invalid metrics JSON: $($_.Exception.Message)"
        return $null
    }
}

# ---------------------------------------------------------------------------
# Measure-SceneBudget
# ---------------------------------------------------------------------------
function Measure-SceneBudget {
    <#
    .SYNOPSIS
        Analyzes frame metrics for a scene and computes peak values.
    .PARAMETER SceneId
        Scene identifier.
    .PARAMETER FrameMetrics
        Array of per-frame metric objects (matching scene_budget_frame schema).
    .PARAMETER MeasurementOrigin
        Overall measurement origin classification.
    .OUTPUTS
        Hashtable matching scene_budget_entry schema.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$SceneId,
        [Parameter(Mandatory)][array]$FrameMetrics,
        [string]$MeasurementOrigin = 'estimated'
    )

    $peaks = @{
        dma_bytes_peak            = 0
        dma_ops_peak              = 0
        sprite_count_peak         = 0
        sprites_per_scanline_peak = 0
        pal_changes_peak          = 0
        vram_usage_estimate_peak  = 0
        cpu_overrun_count         = 0
    }

    foreach ($frame in $FrameMetrics) {
        if ($frame.PSObject.Properties['dma_bytes_requested'] -and $frame.dma_bytes_requested -gt $peaks.dma_bytes_peak) {
            $peaks.dma_bytes_peak = $frame.dma_bytes_requested
        }
        if ($frame.PSObject.Properties['dma_ops'] -and $frame.dma_ops -gt $peaks.dma_ops_peak) {
            $peaks.dma_ops_peak = $frame.dma_ops
        }
        if ($frame.PSObject.Properties['sprite_count'] -and $frame.sprite_count -gt $peaks.sprite_count_peak) {
            $peaks.sprite_count_peak = $frame.sprite_count
        }
        if ($frame.PSObject.Properties['max_sprites_per_scanline'] -and $frame.max_sprites_per_scanline -gt $peaks.sprites_per_scanline_peak) {
            $peaks.sprites_per_scanline_peak = $frame.max_sprites_per_scanline
        }
        if ($frame.PSObject.Properties['pal_changes'] -and $frame.pal_changes -gt $peaks.pal_changes_peak) {
            $peaks.pal_changes_peak = $frame.pal_changes
        }
        if ($frame.PSObject.Properties['vram_usage_estimate'] -and $frame.vram_usage_estimate -gt $peaks.vram_usage_estimate_peak) {
            $peaks.vram_usage_estimate_peak = $frame.vram_usage_estimate
        }
        if ($frame.PSObject.Properties['cpu_frame_overrun_flag'] -and $frame.cpu_frame_overrun_flag -eq $true) {
            $peaks.cpu_overrun_count++
        }
    }

    # Evaluate budget status
    $thresholds = Get-SceneBudgetThresholds
    $status = 'ok'
    $notes = @()

    if ($peaks.sprite_count_peak -ge $thresholds.sprite_count_error) {
        $status = 'error'; $notes += "Sprite count peak ($($peaks.sprite_count_peak)) at/over HW limit"
    } elseif ($peaks.sprite_count_peak -ge $thresholds.sprite_count_warn) {
        if ($status -ne 'error') { $status = 'warn' }; $notes += "Sprite count peak ($($peaks.sprite_count_peak)) approaching limit"
    }

    if ($peaks.sprites_per_scanline_peak -ge $thresholds.sprites_per_scanline_error) {
        $status = 'error'; $notes += "Sprites/scanline peak ($($peaks.sprites_per_scanline_peak)) at/over HW limit"
    } elseif ($peaks.sprites_per_scanline_peak -ge $thresholds.sprites_per_scanline_warn) {
        if ($status -ne 'error') { $status = 'warn' }; $notes += "Sprites/scanline peak ($($peaks.sprites_per_scanline_peak)) approaching limit"
    }

    if ($peaks.vram_usage_estimate_peak -ge $thresholds.vram_usage_error) {
        $status = 'error'; $notes += "VRAM usage peak ($($peaks.vram_usage_estimate_peak) bytes) near capacity"
    } elseif ($peaks.vram_usage_estimate_peak -ge $thresholds.vram_usage_warn) {
        if ($status -ne 'error') { $status = 'warn' }; $notes += "VRAM usage peak ($($peaks.vram_usage_estimate_peak) bytes) approaching limit"
    }

    if ($peaks.cpu_overrun_count -gt 0) {
        $status = 'error'; $notes += "CPU frame overruns detected: $($peaks.cpu_overrun_count)"
    }

    return [ordered]@{
        scene_id                  = $SceneId
        measurement_origin        = $MeasurementOrigin
        frames_analyzed           = $FrameMetrics.Count
        dma_bytes_peak            = $peaks.dma_bytes_peak
        dma_ops_peak              = $peaks.dma_ops_peak
        sprite_count_peak         = $peaks.sprite_count_peak
        sprites_per_scanline_peak = $peaks.sprites_per_scanline_peak
        pal_changes_peak          = $peaks.pal_changes_peak
        vram_usage_estimate_peak  = $peaks.vram_usage_estimate_peak
        cpu_overrun_count         = $peaks.cpu_overrun_count
        budget_status             = $status
        budget_notes              = if ($notes.Count -gt 0) { $notes -join '; ' } else { $null }
    }
}

# ---------------------------------------------------------------------------
# Get-SceneBudgetThresholds
# ---------------------------------------------------------------------------
function Get-SceneBudgetThresholds {
    <#
    .SYNOPSIS
        Returns the current budget thresholds for evaluation.
    .DESCRIPTION
        DECISION PENDING: These are conservative observation-mode defaults.
        Canonical thresholds per scene type are not yet defined.
    .OUTPUTS
        Hashtable of threshold values.
    #>
    [CmdletBinding()]
    param()

    return $script:DefaultThresholds.Clone()
}

# ---------------------------------------------------------------------------
# Write-SceneBudgetSummary
# ---------------------------------------------------------------------------
function Write-SceneBudgetSummary {
    <#
    .SYNOPSIS
        Writes a human-readable markdown summary of budget analysis.
    .PARAMETER SceneResults
        Array of scene budget entries.
    .PARAMETER OutputPath
        Absolute path for the markdown file.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][array]$SceneResults,
        [Parameter(Mandatory)][string]$OutputPath
    )

    $lines = @()
    $lines += '# Scene Budget Summary'
    $lines += ''
    $lines += "Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss UTC' -AsUTC)"
    $lines += ''
    $lines += '| Scene | Status | Sprites | Spr/Line | VRAM | DMA | Origin |'
    $lines += '|-------|--------|---------|----------|------|-----|--------|'

    foreach ($s in $SceneResults) {
        $statusIcon = switch ($s.budget_status) {
            'ok'    { 'OK' }
            'warn'  { 'WARN' }
            'error' { 'ERR' }
            default { '?' }
        }
        $lines += "| $($s.scene_id) | $statusIcon | $($s.sprite_count_peak) | $($s.sprites_per_scanline_peak) | $($s.vram_usage_estimate_peak) | $($s.dma_bytes_peak) | $($s.measurement_origin) |"
    }

    $lines += ''
    foreach ($s in $SceneResults) {
        if ($s.budget_notes) {
            $lines += "**$($s.scene_id):** $($s.budget_notes)"
        }
    }

    $parentDir = Split-Path $OutputPath -Parent
    if (-not (Test-Path -LiteralPath $parentDir)) {
        New-Item -ItemType Directory -Force -Path $parentDir | Out-Null
    }
    $lines -join "`n" | Set-Content -LiteralPath $OutputPath -Encoding UTF8
}

# ---------------------------------------------------------------------------
# Exports
# ---------------------------------------------------------------------------
Export-ModuleMember -Function @(
    'Import-SceneBudgetMetrics',
    'Measure-SceneBudget',
    'Get-SceneBudgetThresholds',
    'Write-SceneBudgetSummary'
)
