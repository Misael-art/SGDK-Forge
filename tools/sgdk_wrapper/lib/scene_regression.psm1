<#
.SYNOPSIS
    Scene regression runner module for the AAA agent ecosystem.
.DESCRIPTION
    Provides functions to load regression manifests, bootstrap scenes,
    capture evidence, compare with baselines, and produce regression results.

    This module does NOT modify any existing wrapper behavior.
    It is consumed only by run_scene_regression.ps1.
#>

Set-StrictMode -Version Latest

# Import dependencies
$script:LibDir = $PSScriptRoot
Import-Module (Join-Path $script:LibDir 'sgdk_artifact_contracts.psm1') -Force
Import-Module (Join-Path $script:LibDir 'evidence_compare.psm1') -Force

# ---------------------------------------------------------------------------
# Get-SceneRegressionManifest
# ---------------------------------------------------------------------------
function Get-SceneRegressionManifest {
    <#
    .SYNOPSIS
        Loads and validates a scene regression manifest JSON.
    .PARAMETER ManifestPath
        Absolute path to scene-regression.json.
    .OUTPUTS
        Parsed manifest object, or $null if invalid.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$ManifestPath
    )

    if (-not (Test-Path -LiteralPath $ManifestPath)) {
        Write-Warning "Regression manifest not found: $ManifestPath"
        return $null
    }

    try {
        $raw = Get-Content -LiteralPath $ManifestPath -Raw -Encoding UTF8
        $manifest = $raw | ConvertFrom-Json
    } catch {
        Write-Warning "Invalid JSON in regression manifest: $($_.Exception.Message)"
        return $null
    }

    if (-not $manifest.PSObject.Properties['schema_version']) {
        Write-Warning "Regression manifest missing schema_version"
    }

    if (-not $manifest.PSObject.Properties['scenes']) {
        Write-Warning "Regression manifest missing scenes array"
        return $null
    }

    return $manifest
}

# ---------------------------------------------------------------------------
# Invoke-SceneBootstrap
# ---------------------------------------------------------------------------
function Invoke-SceneBootstrap {
    <#
    .SYNOPSIS
        Prepares the environment for capturing a specific scene.
    .DESCRIPTION
        Based on boot_mode, sets up the conditions for deterministic scene access.
        Currently supports: direct_boot (no-op), debug_menu (navigation sequence).
        Other modes return a placeholder indicating the bootstrap is not yet automated.

        DECISION PENDING: The exact bootstrap protocol for sram_bootstrap and
        runtime_flag modes is not yet defined. This function returns a status
        indicating the limitation rather than inventing a protocol.
    .PARAMETER SceneConfig
        Scene entry from the regression manifest.
    .PARAMETER ProjectRoot
        Absolute path to the project root.
    .OUTPUTS
        Hashtable: Bootstrapped (bool), BootMode, NavigationSequence, Note
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]$SceneConfig,
        [Parameter(Mandatory)][string]$ProjectRoot
    )

    $bootMode = if ($SceneConfig.PSObject.Properties['boot_mode']) { $SceneConfig.boot_mode } else { 'unsupported' }

    $result = @{
        Bootstrapped       = $false
        BootMode           = $bootMode
        NavigationSequence = @()
        Note               = $null
    }

    switch ($bootMode) {
        'direct_boot' {
            $result.Bootstrapped = $true
            $result.Note = 'Scene accessible via direct ROM boot'
        }
        'debug_menu' {
            # Use navigation sequence if provided
            if ($SceneConfig.PSObject.Properties['navigation_sequence']) {
                $result.NavigationSequence = @($SceneConfig.navigation_sequence)
            }
            $result.Bootstrapped = $true
            $result.Note = 'Scene accessible via debug menu navigation'
        }
        'sram_bootstrap' {
            $result.Note = 'DECISION PENDING: SRAM bootstrap protocol not yet defined'
        }
        'runtime_flag' {
            $result.Note = 'DECISION PENDING: Runtime flag protocol not yet defined'
        }
        'unsupported' {
            $result.Note = 'Scene cannot be deterministically booted'
        }
        default {
            $result.Note = "Unknown boot_mode: $bootMode"
        }
    }

    return $result
}

# ---------------------------------------------------------------------------
# Invoke-SceneCapture
# ---------------------------------------------------------------------------
function Invoke-SceneCapture {
    <#
    .SYNOPSIS
        Captures evidence for a scene by delegating to the BlastEm evidence system.
    .PARAMETER SceneConfig
        Scene entry from the regression manifest.
    .PARAMETER ProjectRoot
        Absolute path to the project root.
    .PARAMETER OutputRoot
        Absolute path for scene evidence output directory.
        NOTE: This is the FINAL evidence dir — caller already appended scene_id.
        Do NOT append scene_id again inside this function.
    .PARAMETER EmulatorPath
        Path to blastem.exe.
    .PARAMETER RomPath
        Path to ROM file.
    .PARAMETER NavigationSequence
        Optional navigation commands from bootstrap (e.g. key presses to reach scene).
    .OUTPUTS
        Hashtable: Captured (bool), EvidencePath, Artifacts, ReadinessOk (bool), Error
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]$SceneConfig,
        [Parameter(Mandatory)][string]$ProjectRoot,
        [Parameter(Mandatory)][string]$OutputRoot,
        [Parameter(Mandatory)][string]$EmulatorPath,
        [Parameter(Mandatory)][string]$RomPath,
        [string[]]$NavigationSequence = @()
    )

    $sid = $SceneConfig.scene_id
    # OutputRoot IS the scene evidence dir — do not append $sid again
    $sceneEvidenceDir = $OutputRoot
    $captureKind = if ($SceneConfig.PSObject.Properties['capture_kind']) { $SceneConfig.capture_kind } else { 'screenshot' }
    $captureMode = if ($captureKind -eq 'evidence_bundle') { 'canonical' } else { 'minimal' }

    # Compute warmup from capture_frame first (more precise), then warmup_frames
    $warmupMs = 3000
    if ($SceneConfig.PSObject.Properties['capture_frame'] -and $SceneConfig.capture_frame -gt 0) {
        # capture_frame governs total wait: frame_number * 16.67ms (60fps)
        $warmupMs = [int]($SceneConfig.capture_frame * 16.67)
    } elseif ($SceneConfig.PSObject.Properties['warmup_frames'] -and $SceneConfig.warmup_frames -gt 0) {
        $warmupMs = [int]($SceneConfig.warmup_frames * 16.67)
    }
    if ($warmupMs -lt 1000) { $warmupMs = 1000 }

    $result = @{
        Captured     = $false
        EvidencePath = $sceneEvidenceDir
        Artifacts    = @()
        ReadinessOk  = $false
        CaptureStatus = 'failed'
        Error        = $null
    }

    try {
        # Import evidence module
        $evidenceModule = Join-Path $script:LibDir 'blastem_evidence.psm1'
        if (-not (Test-Path -LiteralPath $evidenceModule)) {
            $result.Error = "blastem_evidence.psm1 not found"
            return $result
        }
        Import-Module $evidenceModule -Force

        $session = Start-BlastemEvidenceSession `
            -EmulatorPath $EmulatorPath `
            -RomPath $RomPath `
            -OutputRoot $sceneEvidenceDir `
            -BootTimeoutMs 20000

        # Execute navigation sequence if provided (e.g. for debug_menu boot)
        if ($NavigationSequence.Count -gt 0) {
            Import-Module (Join-Path $script:LibDir 'blastem_automation.psm1') -Force
            Invoke-BlastEmNavigation `
                -Process $session.Process `
                -Sequence $NavigationSequence `
                -LogPath $session.LogPath `
                -SaveRoots @($session.SaveRoot, $session.SandboxRoot) `
                -HeartbeatOffset 0x100 `
                -ProcessStartedAtUtc $session.ProcessStartedAtUtc `
                -SandboxRoot $session.SandboxRoot
        }

        # Wait for readiness
        $readyResult = Wait-BlastemReady -Session $session -WarmupMs $warmupMs -TimeoutMs 15000
        $result.ReadinessOk = $readyResult.Ready

        # Gate: if readiness failed, record but still attempt capture (degraded)
        if (-not $readyResult.Ready) {
            $result.Error = 'Readiness heartbeat not detected — capture is degraded (non-deterministic)'
        }

        # Capture
        $captureResult = Invoke-BlastemEvidenceCapture `
            -Session $session `
            -CaptureMode $captureMode `
            -EvidenceRoot $sceneEvidenceDir

        # Stop
        Stop-BlastemEvidenceSession -Session $session | Out-Null

        $result.Captured = (@($captureResult.Captured).Count -gt 0)
        $result.Artifacts = @($captureResult.Captured)
        $result.CaptureStatus = if ($result.Captured) {
            if ($result.ReadinessOk) { 'ok' } else { 'degraded' }
        } else {
            'failed'
        }

        # Write bundle manifest
        $romId = Get-SgdkRomIdentity -RomPath $RomPath
        $bundle = [ordered]@{
            schema_version  = '1.0.0'
            scene_id        = $sid
            captured_at     = (Get-Date).ToUniversalTime().ToString('o')
            rom_sha256      = $romId.rom_sha256
            boot_mode       = $SceneConfig.boot_mode
            capture_frame   = if ($SceneConfig.PSObject.Properties['capture_frame']) { $SceneConfig.capture_frame } else { $null }
            warmup_frames   = if ($SceneConfig.PSObject.Properties['warmup_frames']) { $SceneConfig.warmup_frames } else { $null }
            readiness_ok    = $result.ReadinessOk
            artifacts       = [ordered]@{
                screenshot = if ($captureResult.ScreenshotPath) { 'screenshot.png' } else { $null }
                sram       = if ($captureResult.SramPath) { 'save.sram' } else { $null }
                vdp_dump   = if ($captureResult.VdpDumpPath) { 'visual_vdp_dump.bin' } else { $null }
            }
            capture_status  = $result.CaptureStatus
        }
        Write-SgdkJsonArtifact -Data $bundle -Path (Join-Path $sceneEvidenceDir 'bundle.json') | Out-Null
    }
    catch {
        $result.Error = $_.Exception.Message
    }

    return $result
}

# ---------------------------------------------------------------------------
# Compare-SceneEvidence
# ---------------------------------------------------------------------------
function Compare-SceneEvidence {
    <#
    .SYNOPSIS
        Compares captured scene evidence against a baseline.
    .PARAMETER SceneConfig
        Scene entry from the regression manifest.
    .PARAMETER EvidencePath
        Path to the captured evidence directory.
    .PARAMETER BaselinePath
        Path to the baseline evidence directory.
    .OUTPUTS
        Hashtable: Status (passed/failed/missing/stale), DiffSummary, FailureReason
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]$SceneConfig,
        [Parameter(Mandatory)][string]$EvidencePath,
        [Parameter(Mandatory)][string]$BaselinePath
    )

    $result = @{
        Status        = 'error'
        DiffSummary   = @{
            screenshot_match    = $null
            sram_match          = $null
            vdp_dump_match      = $null
            pixel_diff_fraction = $null
        }
        FailureReason = $null
    }

    # Check baseline exists
    if (-not (Test-Path -LiteralPath $BaselinePath)) {
        $result.Status = 'missing'
        $result.FailureReason = "Baseline directory not found: $BaselinePath"
        return $result
    }

    $compMode = if ($SceneConfig.PSObject.Properties['comparison_mode']) { $SceneConfig.comparison_mode } else { 'exact' }
    $threshold = if ($SceneConfig.PSObject.Properties['tolerance_threshold']) { $SceneConfig.tolerance_threshold } else { 0.0 }

    $requiredArtifacts = @('screenshot')
    if ($SceneConfig.PSObject.Properties['required_artifacts']) {
        $requiredArtifacts = @($SceneConfig.required_artifacts)
    }

    $allMatch = $true

    # Compare screenshot
    if ('screenshot' -in $requiredArtifacts) {
        $baseScreenshot = Join-Path $BaselinePath 'screenshot.png'
        $currScreenshot = Join-Path $EvidencePath 'screenshot.png'

        if ($compMode -eq 'tolerant') {
            $imgResult = Compare-ImageTolerance -BaselinePath $baseScreenshot -CurrentPath $currScreenshot -Threshold $threshold
            $result.DiffSummary.screenshot_match = $imgResult.Match
            $result.DiffSummary.pixel_diff_fraction = $imgResult.DiffFraction
            if ($imgResult.Error) { $result.FailureReason = $imgResult.Error; $allMatch = $false }
            elseif (-not $imgResult.Match) { $allMatch = $false }
        } else {
            $hashResult = Compare-ExactHash -BaselinePath $baseScreenshot -CurrentPath $currScreenshot
            $result.DiffSummary.screenshot_match = $hashResult.Match
            if ($hashResult.Error) { $result.FailureReason = $hashResult.Error; $allMatch = $false }
            elseif (-not $hashResult.Match) { $allMatch = $false }
        }
    }

    # Compare SRAM
    if ('sram' -in $requiredArtifacts) {
        $baseSram = Join-Path $BaselinePath 'save.sram'
        $currSram = Join-Path $EvidencePath 'save.sram'
        $sramResult = Compare-BinaryExact -BaselinePath $baseSram -CurrentPath $currSram
        $result.DiffSummary.sram_match = $sramResult.Match
        if ($sramResult.Error) { $result.FailureReason = $sramResult.Error; $allMatch = $false }
        elseif (-not $sramResult.Match) { $allMatch = $false }
    }

    # Compare VDP dump
    if ('vdp_dump' -in $requiredArtifacts) {
        $baseVdp = Join-Path $BaselinePath 'visual_vdp_dump.bin'
        $currVdp = Join-Path $EvidencePath 'visual_vdp_dump.bin'
        $vdpResult = Compare-BinaryExact -BaselinePath $baseVdp -CurrentPath $currVdp
        $result.DiffSummary.vdp_dump_match = $vdpResult.Match
        if ($vdpResult.Error) { $result.FailureReason = $vdpResult.Error; $allMatch = $false }
        elseif (-not $vdpResult.Match) { $allMatch = $false }
    }

    $result.Status = if ($allMatch) { 'passed' } else { 'failed' }
    return $result
}

# ---------------------------------------------------------------------------
# New-SceneRegressionResult
# ---------------------------------------------------------------------------
function New-SceneRegressionResult {
    <#
    .SYNOPSIS
        Creates a structured result entry for one scene in the regression report.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$SceneId,
        [Parameter(Mandatory)][string]$Status,
        [string]$ComparisonMode = $null,
        [string]$BaselineRomSha256 = $null,
        [string]$CurrentRomSha256 = $null,
        [hashtable]$DiffSummary = $null,
        [string]$EvidencePath = $null,
        [string]$BaselinePath = $null,
        [string]$FailureReason = $null,
        [Nullable[bool]]$ReadinessOk = $null,
        [string]$CaptureStatus = $null,
        [bool]$CaptureDegraded = $false
    )

    return [ordered]@{
        scene_id            = $SceneId
        status              = $Status
        comparison_mode     = $ComparisonMode
        baseline_rom_sha256 = $BaselineRomSha256
        current_rom_sha256  = $CurrentRomSha256
        diff_summary        = $DiffSummary
        evidence_path       = $EvidencePath
        baseline_path       = $BaselinePath
        failure_reason      = $FailureReason
        readiness_ok        = $ReadinessOk
        capture_status      = $CaptureStatus
        capture_degraded    = $CaptureDegraded
    }
}

# ---------------------------------------------------------------------------
# Exports
# ---------------------------------------------------------------------------
Export-ModuleMember -Function @(
    'Get-SceneRegressionManifest',
    'Invoke-SceneBootstrap',
    'Invoke-SceneCapture',
    'Compare-SceneEvidence',
    'New-SceneRegressionResult'
)
