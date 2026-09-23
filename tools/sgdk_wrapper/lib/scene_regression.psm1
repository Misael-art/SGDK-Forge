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
Import-Module (Join-Path $script:LibDir 'blastem_automation.psm1') -Force
Import-Module (Join-Path $script:LibDir 'scene_capture_gate.psm1') -Force

$script:SceneBootstrapSramOffset = 0x120
$script:SceneBootstrapSchemaVersion = 1
$script:SceneBootstrapTotalBytes = 12
$script:SceneBootstrapHoldSchemaVersion = 2
$script:SceneBootstrapHoldTotalBytes = 16
$script:SceneBootstrapHoldFlag = 1
$script:SceneBootstrapForceChaseFailureFlag = 2
$script:SceneBootstrapChecksumSeed = 0xA55A

function Get-SceneConfigIntValue {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]$SceneConfig,
        [Parameter(Mandatory)][string[]]$PropertyNames
    )

    foreach ($propertyName in $PropertyNames) {
        if (-not $SceneConfig.PSObject.Properties[$propertyName]) {
            continue
        }

        $rawValue = [string]$SceneConfig.$propertyName
        if ([string]::IsNullOrWhiteSpace($rawValue)) {
            continue
        }

        try {
            return [int]$rawValue
        }
        catch {
            throw "Campo '$propertyName' invalido em scene-regression.json para cena '$($SceneConfig.scene_id)': '$rawValue'"
        }
    }

    return $null
}

function Get-SceneConfigArtifactList {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]$SceneConfig,
        [Parameter(Mandatory)][string]$PropertyName,
        [Parameter(Mandatory)][string[]]$DefaultArtifacts
    )

    if ($SceneConfig.PSObject.Properties[$PropertyName] -and $SceneConfig.$PropertyName) {
        return @($SceneConfig.$PropertyName)
    }

    return @($DefaultArtifacts)
}

function Get-SceneBootstrapFlags {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]$SceneConfig
    )

    $flags = 0
    if ($SceneConfig.PSObject.Properties['bootstrap_flags_value']) {
        try {
            $flags = [int]([string]$SceneConfig.bootstrap_flags_value)
        }
        catch {
            throw "Campo 'bootstrap_flags_value' invalido em scene-regression.json para cena '$($SceneConfig.scene_id)': '$($SceneConfig.bootstrap_flags_value)'"
        }
    }

    if ($SceneConfig.PSObject.Properties['bootstrap_flags'] -and $SceneConfig.bootstrap_flags) {
        foreach ($flagName in @($SceneConfig.bootstrap_flags)) {
            switch ([string]$flagName) {
                'force_chase_failure_result' { $flags = $flags -bor $script:SceneBootstrapForceChaseFailureFlag }
                default {
                    throw "bootstrap_flags desconhecido em scene-regression.json para cena '$($SceneConfig.scene_id)': '$flagName'"
                }
            }
        }
    }

    return $flags
}

function Read-SceneRegressionU16BE {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][byte[]]$Bytes,
        [Parameter(Mandatory = $true)][int]$Offset
    )

    if ($Offset -lt 0 -or ($Offset + 1) -ge $Bytes.Length) {
        throw "Offset fora do range: $Offset (len=$($Bytes.Length))"
    }

    return ([int]$Bytes[$Offset] -shl 8) -bor [int]$Bytes[$Offset + 1]
}

function Write-SceneRegressionU16BE {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][byte[]]$Bytes,
        [Parameter(Mandatory = $true)][int]$Offset,
        [Parameter(Mandatory = $true)][int]$Value
    )

    if ($Offset -lt 0 -or ($Offset + 1) -ge $Bytes.Length) {
        throw "Offset fora do range para escrita: $Offset (len=$($Bytes.Length))"
    }

    $Bytes[$Offset] = [byte](($Value -shr 8) -band 0xFF)
    $Bytes[$Offset + 1] = [byte]($Value -band 0xFF)
}

function Get-SceneBootstrapChecksum {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][int]$SceneId,
        [int]$SchemaVersion = $script:SceneBootstrapSchemaVersion,
        [int]$TotalBytes = $script:SceneBootstrapTotalBytes,
        [int]$HoldFrame = 0,
        [int]$Flags = 0
    )

    return (($script:SceneBootstrapChecksumSeed -bxor
        $SchemaVersion -bxor
        $TotalBytes -bxor
        $SceneId -bxor
        $HoldFrame -bxor
        $Flags) -band 0xFFFF)
}

function New-SceneBootstrapPayload {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][int]$SceneId,
        [int]$HoldFrame = -1,
        [int]$Flags = 0
    )

    if ($SceneId -lt 0 -or $SceneId -gt 0xFFFF) {
        throw "scene_id fora do range u16 para bootstrap SRAM: $SceneId"
    }

    if ($HoldFrame -gt 0xFFFF) {
        throw "capture_hold_frame fora do range u16 para bootstrap SRAM: $HoldFrame"
    }

    $useHold = $HoldFrame -ge 0 -or $Flags -ne 0
    $schemaVersion = if ($useHold) { $script:SceneBootstrapHoldSchemaVersion } else { $script:SceneBootstrapSchemaVersion }
    $totalBytes = if ($useHold) { $script:SceneBootstrapHoldTotalBytes } else { $script:SceneBootstrapTotalBytes }
    $flags = if ($useHold) { $script:SceneBootstrapHoldFlag -bor $Flags } else { 0 }
    $effectiveHoldFrame = if ($HoldFrame -ge 0) { $HoldFrame } else { 0 }

    $payload = New-Object byte[] ($script:SceneBootstrapSramOffset + $totalBytes)
    $offset = $script:SceneBootstrapSramOffset
    [System.Text.Encoding]::ASCII.GetBytes('SBIS').CopyTo($payload, $offset)
    Write-SceneRegressionU16BE -Bytes $payload -Offset ($offset + 4) -Value $schemaVersion
    Write-SceneRegressionU16BE -Bytes $payload -Offset ($offset + 6) -Value $totalBytes
    Write-SceneRegressionU16BE -Bytes $payload -Offset ($offset + 8) -Value $SceneId
    if ($useHold) {
        Write-SceneRegressionU16BE -Bytes $payload -Offset ($offset + 10) -Value $effectiveHoldFrame
        Write-SceneRegressionU16BE -Bytes $payload -Offset ($offset + 12) -Value $flags
        Write-SceneRegressionU16BE -Bytes $payload -Offset ($offset + 14) -Value (
            Get-SceneBootstrapChecksum -SceneId $SceneId -SchemaVersion $schemaVersion -TotalBytes $totalBytes -HoldFrame $effectiveHoldFrame -Flags $flags
        )
    } else {
        Write-SceneRegressionU16BE -Bytes $payload -Offset ($offset + 10) -Value (
            Get-SceneBootstrapChecksum -SceneId $SceneId -SchemaVersion $schemaVersion -TotalBytes $totalBytes
        )
    }
    return $payload
}

function Get-MdrtOffsetCandidates {
    [CmdletBinding()]
    param(
        [int]$PreferredOffset = 0x200
    )

    $offsets = [System.Collections.Generic.List[int]]::new()
    [void]$offsets.Add($PreferredOffset)
    if ($PreferredOffset -eq 0x200) {
        # BENCHMARK_VISUAL_LAB currently persists MDRT at SRAM base.
        [void]$offsets.Add(0)
    }

    return @($offsets | Select-Object -Unique)
}

function Get-MdrtSceneRuntimeInfo {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$SramPath,
        [int]$SramOffset = 0x200
    )

    $info = [ordered]@{
        source_path = $SramPath
        sram_offset = $SramOffset
        present = $false
        valid = $false
        magic = $null
        schema = $null
        total_bytes = $null
        word_count = $null
        schema_version = $null
        scene_id = $null
        error = $null
    }

    if ([string]::IsNullOrWhiteSpace($SramPath) -or -not (Test-Path -LiteralPath $SramPath -PathType Leaf)) {
        $info.error = "SRAM nao encontrada: $SramPath"
        return $info
    }

    try {
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
            if ($candidateSig -eq 'MDRT') {
                $resolvedOffset = $candidateOffset
                $info.magic = $candidateSig
                $info.sram_offset = $candidateOffset
                break
            }
        }

        if ($null -eq $resolvedOffset) {
            if ($bytes.Length -lt ($SramOffset + 12)) {
                throw "SRAM curta demais (len=$($bytes.Length)) para offsets candidatos $candidateOffsetsText"
            }

            $info.magic = $lastSignature
            throw "Assinatura MDRT nao encontrada nos offsets candidatos $candidateOffsetsText (ultimo='$lastSignature')"
        }

        $schema = Read-SceneRegressionU16BE -Bytes $bytes -Offset ($resolvedOffset + 4)
        $totalBytes = Read-SceneRegressionU16BE -Bytes $bytes -Offset ($resolvedOffset + 6)
        $wordCount = Read-SceneRegressionU16BE -Bytes $bytes -Offset ($resolvedOffset + 8)
        $info.present = $true
        $info.schema = [int]$schema
        $info.total_bytes = [int]$totalBytes
        $info.word_count = [int]$wordCount

        $mdrtWordCountMin = 64
        $mdrtWordCountMax = 8192
        if ($wordCount -lt $mdrtWordCountMin) {
            throw "Dump MDRT invalido (wordCount=$wordCount < $mdrtWordCountMin)."
        }
        if ($wordCount -gt $mdrtWordCountMax) {
            throw "Dump MDRT invalido (wordCount=$wordCount > $mdrtWordCountMax)."
        }

        $payloadStart = $resolvedOffset + 10
        $expectedSize = $payloadStart + ($wordCount * 2)
        if ($bytes.Length -lt $expectedSize) {
            throw "SRAM nao contem payload MDRT completo: precisa=$expectedSize len=$($bytes.Length) wordCount=$wordCount"
        }

        $words = New-Object int[] $wordCount
        $pos = $payloadStart
        for ($i = 0; $i -lt $wordCount; $i++) {
            $words[$i] = Read-SceneRegressionU16BE -Bytes $bytes -Offset $pos
            $pos += 2
        }

        $info.schema_version = [int]$words[2]
        $info.scene_id = [int]$words[5]
        $info.valid = $true
    }
    catch {
        $info.error = $_.Exception.Message
    }

    return $info
}

function Try-RecoverSceneSramPostClose {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][hashtable]$Session,
        [Parameter(Mandatory)][string]$SceneEvidenceDir
    )

    $rootPaths = @()
    if ($Session.ContainsKey('SaveRoot') -and -not [string]::IsNullOrWhiteSpace([string]$Session.SaveRoot)) {
        $rootPaths += [string]$Session.SaveRoot
    }
    if ($Session.ContainsKey('SandboxRoot') -and -not [string]::IsNullOrWhiteSpace([string]$Session.SandboxRoot)) {
        $rootPaths += [string]$Session.SandboxRoot
    }
    $rootPaths = @($rootPaths | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Select-Object -Unique)
    if ($rootPaths.Count -eq 0) {
        return $null
    }

    $processStartedAtUtc = [datetime]::MinValue
    if ($Session.ContainsKey('ProcessStartedAtUtc') -and $null -ne $Session.ProcessStartedAtUtc) {
        try {
            $processStartedAtUtc = [datetime]$Session.ProcessStartedAtUtc
        }
        catch {
            $processStartedAtUtc = [datetime]::MinValue
        }
    }

    $sandboxRoot = ''
    if ($Session.ContainsKey('SandboxRoot') -and -not [string]::IsNullOrWhiteSpace([string]$Session.SandboxRoot)) {
        $sandboxRoot = [string]$Session.SandboxRoot
    }

    $sourceSram = Find-FirstSramWithSignature `
        -RootPaths $rootPaths `
        -SramOffset 0x200 `
        -ProcessStartedAtUtc $processStartedAtUtc `
        -SandboxRoot $sandboxRoot
    if ([string]::IsNullOrWhiteSpace($sourceSram)) {
        return $null
    }

    $recoveredPath = Join-Path $SceneEvidenceDir 'save.sram'
    [System.IO.File]::Copy($sourceSram, $recoveredPath, $true)
    if (Test-Path -LiteralPath $recoveredPath -PathType Leaf) {
        return $recoveredPath
    }

    return $null
}

function Try-RecoverSceneVdpDumpFromSram {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$SramPath,
        [Parameter(Mandatory)][string]$SceneEvidenceDir
    )

    if ([string]::IsNullOrWhiteSpace($SramPath) -or -not (Test-Path -LiteralPath $SramPath -PathType Leaf)) {
        return $null
    }

    try {
        $bytes = [System.IO.File]::ReadAllBytes($SramPath)
        if ($bytes.Length -lt 8) {
            return $null
        }

        $magic = [System.Text.Encoding]::ASCII.GetString($bytes, 0, 4)
        if ($magic -ne 'VLAB') {
            return $null
        }

        $totalBytes = ([int]$bytes[6] -shl 8) -bor [int]$bytes[7]
        if ($totalBytes -le 0 -or $totalBytes -gt $bytes.Length) {
            return $null
        }

        $dumpPath = Join-Path $SceneEvidenceDir 'visual_vdp_dump.bin'
        [System.IO.File]::WriteAllBytes($dumpPath, $bytes[0..($totalBytes - 1)])
        if (Test-Path -LiteralPath $dumpPath -PathType Leaf) {
            return $dumpPath
        }
    }
    catch {
        return $null
    }

    return $null
}

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
        Currently supports: direct_boot (no-op), debug_menu (navigation sequence),
        and sram_bootstrap (seed save.sram before ROM boot).
    .PARAMETER SceneConfig
        Scene entry from the regression manifest.
    .PARAMETER ProjectRoot
        Absolute path to the project root.
    .OUTPUTS
        Hashtable: Bootstrapped (bool), BootMode, NavigationSequence,
        InitialSramBytes, Note
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
        InitialSramBytes   = [byte[]]@()
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
            $bootstrapSceneId = Get-SceneConfigIntValue -SceneConfig $SceneConfig -PropertyNames @('bootstrap_scene_id', 'expected_app_scene_id', 'app_scene_id')
            if ($null -eq $bootstrapSceneId) {
                $result.Note = 'sram_bootstrap requer bootstrap_scene_id ou expected_app_scene_id'
                break
            }

            $captureHoldFrame = Get-SceneConfigIntValue -SceneConfig $SceneConfig -PropertyNames @('capture_hold_frame')
            $bootstrapFlags = Get-SceneBootstrapFlags -SceneConfig $SceneConfig
            $result.InitialSramBytes = if ($null -ne $captureHoldFrame) {
                New-SceneBootstrapPayload -SceneId $bootstrapSceneId -HoldFrame $captureHoldFrame -Flags $bootstrapFlags
            } else {
                New-SceneBootstrapPayload -SceneId $bootstrapSceneId -Flags $bootstrapFlags
            }
            $result.Bootstrapped = $true
            $result.Note = if ($null -ne $captureHoldFrame) {
                "Cena acessivel via SRAM bootstrap (scene_id=$bootstrapSceneId, capture_hold_frame=$captureHoldFrame, flags=$bootstrapFlags)"
            } else {
                "Cena acessivel via SRAM bootstrap (scene_id=$bootstrapSceneId, flags=$bootstrapFlags)"
            }
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
        [string[]]$NavigationSequence = @(),
        [byte[]]$InitialSramBytes = @()
    )

    $sid = $SceneConfig.scene_id
    # OutputRoot IS the scene evidence dir — do not append $sid again
    $sceneEvidenceDir = $OutputRoot
    $captureKind = if ($SceneConfig.PSObject.Properties['capture_kind']) { $SceneConfig.capture_kind } else { 'screenshot' }
    $captureMode = if ($captureKind -eq 'evidence_bundle') { 'canonical' } else { 'minimal' }
    $expectedAppSceneId = Get-SceneConfigIntValue -SceneConfig $SceneConfig -PropertyNames @('expected_app_scene_id', 'app_scene_id')
    $sceneVerificationRequired = ($null -ne $expectedAppSceneId)

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
        Captured                  = $false
        EvidencePath              = $sceneEvidenceDir
        Artifacts                 = @()
        ArtifactPaths             = [ordered]@{
            screenshot = $null
            sram = $null
            vdp_dump = $null
        }
        BundlePath                = $null
        ReadinessOk               = $false
        ReadyHeartbeatOk          = $false
        CaptureStatus             = 'failed'
        ExpectedAppSceneId        = $expectedAppSceneId
        CapturedAppSceneId        = $null
        SceneVerificationRequired = $sceneVerificationRequired
        SceneMatch                = $null
        MdrtPresent               = $false
        Mdrt                      = $null
        Error                     = $null
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
            -BootTimeoutMs 20000 `
            -InitialSramBytes $InitialSramBytes

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
        $result.ReadyHeartbeatOk = $readyResult.Ready

        # Capture
        $captureResult = Invoke-BlastemEvidenceCapture `
            -Session $session `
            -CaptureMode $captureMode `
            -EvidenceRoot $sceneEvidenceDir

        # Stop
        Stop-BlastemEvidenceSession -Session $session | Out-Null

        # Some BlastEm builds flush SRAM only on close. Always prefer the
        # post-close recovery candidate so a seeded bootstrap file does not
        # remain promoted as final evidence when the ROM flushes a newer SRAM.
        $postCloseSramPath = Try-RecoverSceneSramPostClose -Session $session -SceneEvidenceDir $sceneEvidenceDir
        if ($postCloseSramPath) {
            $captureResult.SramPath = $postCloseSramPath
        }

        if (-not $captureResult.VdpDumpPath -and $captureResult.SramPath) {
            $captureResult.VdpDumpPath = Try-RecoverSceneVdpDumpFromSram -SramPath $captureResult.SramPath -SceneEvidenceDir $sceneEvidenceDir
        }

        if (-not $readyResult.Ready -and $captureResult.SramPath) {
            $postCloseReady = Test-MDReadyHeartbeat -SramPath $captureResult.SramPath -Offset 0x100
            if ($postCloseReady) {
                $readyResult.Ready = $true
                $readyResult.SramPath = $captureResult.SramPath
            }
        }

        $mdrtInfo = $null
        if ($captureResult.SramPath) {
            $mdrtInfo = Get-MdrtSceneRuntimeInfo -SramPath $captureResult.SramPath -SramOffset 0x200
        }

        $artifactLabels = [System.Collections.ArrayList]::new()
        if ($captureResult.ScreenshotPath) {
            [void]$artifactLabels.Add('screenshot')
            $result.ArtifactPaths['screenshot'] = 'screenshot.png'
        }
        if ($captureResult.SramPath) {
            [void]$artifactLabels.Add('sram')
            $result.ArtifactPaths['sram'] = 'save.sram'
        }
        if ($captureResult.VdpDumpPath) {
            [void]$artifactLabels.Add('vdp_dump')
            $result.ArtifactPaths['vdp_dump'] = 'visual_vdp_dump.bin'
        }
        $result.Artifacts = @($artifactLabels.ToArray())

        $result.Captured = ($result.Artifacts.Count -gt 0)

        $romId = Get-SgdkRomIdentity -RomPath $RomPath
        $gateResult = Test-SceneCaptureSuccess `
            -SceneManifestEntry $SceneConfig `
            -EvidencePath $sceneEvidenceDir `
            -RomSha256 $romId.rom_sha256

        $result.ReadinessOk = [bool]$gateResult.readiness_ok
        $result.ReadyHeartbeatOk = [bool]$gateResult.ready_heartbeat_ok
        $result.CaptureStatus = [string]$gateResult.capture_status
        $result.ExpectedAppSceneId = $gateResult.expected_app_scene_id
        $result.CapturedAppSceneId = $gateResult.captured_app_scene_id
        $result.SceneVerificationRequired = [bool]$gateResult.scene_verification_required
        $result.SceneMatch = $gateResult.scene_match
        $result.MdrtPresent = [bool]$gateResult.mdrt_present
        $result.Mdrt = $gateResult.mdrt
        $result.Artifacts = @($gateResult.artifacts_captured)
        $result.Error = $gateResult.failure_reason

        # Write bundle manifest
        $bundle = [ordered]@{
            schema_version  = '1.0.0'
            scene_id        = $sid
            captured_at     = (Get-Date).ToUniversalTime().ToString('o')
            rom_sha256      = $romId.rom_sha256
            boot_mode       = $SceneConfig.boot_mode
            capture_frame   = if ($SceneConfig.PSObject.Properties['capture_frame']) { $SceneConfig.capture_frame } else { $null }
            warmup_frames   = if ($SceneConfig.PSObject.Properties['warmup_frames']) { $SceneConfig.warmup_frames } else { $null }
            expected_app_scene_id = $expectedAppSceneId
            captured_app_scene_id = $result.CapturedAppSceneId
            scene_verification_required = $sceneVerificationRequired
            scene_match     = $result.SceneMatch
            readiness_ok    = $result.ReadinessOk
            ready_heartbeat_ok = $result.ReadyHeartbeatOk
            mdrt_present    = $result.MdrtPresent
            mdrt            = $mdrtInfo
            artifacts_captured = @($result.Artifacts)
            artifacts       = [ordered]@{
                screenshot = $result.ArtifactPaths['screenshot']
                sram       = $result.ArtifactPaths['sram']
                vdp_dump   = $result.ArtifactPaths['vdp_dump']
            }
            required_artifacts_present = [bool]$gateResult.required_artifacts_present
            capture_status  = $result.CaptureStatus
            failure_reason  = $result.Error
        }
        $result.BundlePath = Join-Path $sceneEvidenceDir 'bundle.json'
        Write-SgdkJsonArtifact -Data $bundle -Path $result.BundlePath | Out-Null
    }
    catch {
        $position = $null
        if ($_.InvocationInfo -and $_.InvocationInfo.PositionMessage) {
            $position = ($_.InvocationInfo.PositionMessage -replace '\s+', ' ').Trim()
        }
        $result.Error = if ([string]::IsNullOrWhiteSpace($position)) {
            $_.Exception.Message
        } else {
            "$($_.Exception.Message) [$position]"
        }
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

    # Presence requirements and baseline diff inputs are intentionally split.
    # required_artifacts gates capture completeness; comparison_artifacts
    # controls what is actually compared against the baseline.
    $comparisonArtifacts = Get-SceneConfigArtifactList `
        -SceneConfig $SceneConfig `
        -PropertyName 'comparison_artifacts' `
        -DefaultArtifacts @('screenshot')

    $allMatch = $true

    # Compare screenshot
    if ('screenshot' -in $comparisonArtifacts) {
        $baseScreenshot = Join-Path $BaselinePath 'screenshot.png'
        $currScreenshot = Join-Path $EvidencePath 'screenshot.png'
        $screenshotCrop = if ($SceneConfig.PSObject.Properties['screenshot_viewport_crop']) { $SceneConfig.screenshot_viewport_crop } else { $null }

        if ($compMode -eq 'tolerant' -or $null -ne $screenshotCrop) {
            $effectiveThreshold = if ($compMode -eq 'tolerant') { $threshold } else { 0.0 }
            $imgResult = Compare-ImageTolerance -BaselinePath $baseScreenshot -CurrentPath $currScreenshot -Threshold $effectiveThreshold -CropRect $screenshotCrop
            $result.DiffSummary.screenshot_match = $imgResult.Match
            $result.DiffSummary.pixel_diff_fraction = $imgResult.DiffFraction
            if ($null -ne $imgResult.CropRect) {
                $result.DiffSummary.screenshot_crop = $imgResult.CropRect
            }
            if ($imgResult.Error) { $result.FailureReason = $imgResult.Error; $allMatch = $false }
            elseif (-not $imgResult.Match) {
                $result.FailureReason = "Screenshot diff fraction $($imgResult.DiffFraction) exceeds threshold $effectiveThreshold"
                $allMatch = $false
            }
        } else {
            $hashResult = Compare-ExactHash -BaselinePath $baseScreenshot -CurrentPath $currScreenshot
            $result.DiffSummary.screenshot_match = $hashResult.Match
            if ($hashResult.Error) { $result.FailureReason = $hashResult.Error; $allMatch = $false }
            elseif (-not $hashResult.Match) {
                $result.FailureReason = 'Screenshot hash mismatch'
                $allMatch = $false
            }
        }
    }

    # Compare SRAM
    if ('sram' -in $comparisonArtifacts) {
        $baseSram = Join-Path $BaselinePath 'save.sram'
        $currSram = Join-Path $EvidencePath 'save.sram'
        $sramResult = Compare-BinaryExact -BaselinePath $baseSram -CurrentPath $currSram
        $result.DiffSummary.sram_match = $sramResult.Match
        if ($sramResult.Error) { $result.FailureReason = $sramResult.Error; $allMatch = $false }
        elseif (-not $sramResult.Match) {
            $result.FailureReason = 'SRAM mismatch'
            $allMatch = $false
        }
    }

    # Compare VDP dump
    if ('vdp_dump' -in $comparisonArtifacts) {
        $baseVdp = Join-Path $BaselinePath 'visual_vdp_dump.bin'
        $currVdp = Join-Path $EvidencePath 'visual_vdp_dump.bin'
        $vdpResult = Compare-BinaryExact -BaselinePath $baseVdp -CurrentPath $currVdp
        $result.DiffSummary.vdp_dump_match = $vdpResult.Match
        if ($vdpResult.Error) { $result.FailureReason = $vdpResult.Error; $allMatch = $false }
        elseif (-not $vdpResult.Match) {
            $result.FailureReason = 'VDP dump mismatch'
            $allMatch = $false
        }
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
        [Nullable[bool]]$ReadyHeartbeatOk = $null,
        [string]$CaptureStatus = $null,
        [bool]$CaptureDegraded = $false,
        [Nullable[int]]$ExpectedAppSceneId = $null,
        [Nullable[int]]$CapturedAppSceneId = $null,
        [Nullable[bool]]$SceneMatch = $null,
        [bool]$MdrtPresent = $false,
        [string[]]$Artifacts = @(),
        [hashtable]$ArtifactPaths = $null,
        [string]$BundlePath = $null
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
        ready_heartbeat_ok  = $ReadyHeartbeatOk
        capture_status      = $CaptureStatus
        capture_degraded    = $CaptureDegraded
        expected_app_scene_id = $ExpectedAppSceneId
        captured_app_scene_id = $CapturedAppSceneId
        scene_match         = $SceneMatch
        mdrt_present        = $MdrtPresent
        artifacts           = @($Artifacts)
        artifact_paths      = $ArtifactPaths
        bundle_path         = $BundlePath
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
