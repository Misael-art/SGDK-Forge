<#
.SYNOPSIS
    Scene capture gate — single authority for capture validity decisions.
.DESCRIPTION
    Exports Test-SceneCaptureSuccess: recomputes capture truth from artifacts
    on disk, MDRT blocks, and readiness heartbeats. Does NOT trust bundle.json
    blindly — validates from raw evidence.

    Canonical statuses: ok, degraded, wrong_scene, failed.
.NOTES
    Consumed by scene_capture_gate.ps1 (standalone) and run_scene_regression.ps1.
#>

Set-StrictMode -Version Latest

$script:LibDir = $PSScriptRoot
Import-Module (Join-Path $script:LibDir 'blastem_automation.psm1') -Force
Import-Module (Join-Path $script:LibDir 'sgdk_artifact_contracts.psm1') -Force

# ---------------------------------------------------------------------------
# Test-SceneCaptureSuccess
# ---------------------------------------------------------------------------
function Test-SceneCaptureSuccess {
    <#
    .SYNOPSIS
        Recomputes capture validity from artifacts on disk.
    .PARAMETER SceneManifestEntry
        Scene entry from scene-regression.json (PSObject with scene_id,
        expected_app_scene_id, required_artifacts, etc.).
    .PARAMETER EvidencePath
        Absolute path to out/evidence/scenes/<scene_id>/.
    .PARAMETER RomSha256
        SHA256 of the ROM being tested (for provenance).
    .PARAMETER RequireHeartbeat
        If true, missing heartbeat downgrades to 'degraded' instead of 'ok'.
        Default: true.
    .OUTPUTS
        Ordered hashtable with capture_status, scene_match, readiness_ok, etc.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]$SceneManifestEntry,
        [Parameter(Mandatory)][string]$EvidencePath,
        [string]$RomSha256 = 'UNKNOWN',
        [bool]$RequireHeartbeat = $true
    )

    $sid = $SceneManifestEntry.scene_id
    $expectedAppSceneId = $null
    if ($SceneManifestEntry.PSObject.Properties['expected_app_scene_id'] -and
        $null -ne $SceneManifestEntry.expected_app_scene_id) {
        $expectedAppSceneId = [int]$SceneManifestEntry.expected_app_scene_id
    }
    $sceneVerificationRequired = ($null -ne $expectedAppSceneId)

    $result = [ordered]@{
        scene_id                    = $sid
        expected_app_scene_id       = $expectedAppSceneId
        captured_app_scene_id       = $null
        scene_verification_required = $sceneVerificationRequired
        scene_match                 = $null
        mdrt_present                = $false
        mdrt                        = $null
        ready_heartbeat_ok          = $false
        readiness_ok                = $false
        artifacts_captured          = @()
        required_artifacts_present  = $false
        capture_status              = 'failed'
        failure_reason              = $null
    }

    # -----------------------------------------------------------------------
    # Step 1: Validate artifacts exist on disk
    # -----------------------------------------------------------------------
    $artifactLabels = [System.Collections.ArrayList]::new()

    $screenshotPath = Join-Path $EvidencePath 'screenshot.png'
    $sramPath = Join-Path $EvidencePath 'save.sram'
    $vdpDumpPath = Join-Path $EvidencePath 'visual_vdp_dump.bin'

    if (Test-Path -LiteralPath $screenshotPath -PathType Leaf) {
        if ((Get-Item -LiteralPath $screenshotPath).Length -gt 0) {
            [void]$artifactLabels.Add('screenshot')
        }
    }
    if (Test-Path -LiteralPath $sramPath -PathType Leaf) {
        if ((Get-Item -LiteralPath $sramPath).Length -gt 0) {
            [void]$artifactLabels.Add('sram')
        }
    }
    if (Test-Path -LiteralPath $vdpDumpPath -PathType Leaf) {
        if ((Get-Item -LiteralPath $vdpDumpPath).Length -gt 0) {
            [void]$artifactLabels.Add('vdp_dump')
        }
    }

    $result.artifacts_captured = @($artifactLabels.ToArray())

    # Determine required artifacts
    $requiredArtifacts = @('screenshot')
    if ($SceneManifestEntry.PSObject.Properties['required_artifacts'] -and
        $SceneManifestEntry.required_artifacts) {
        $requiredArtifacts = @($SceneManifestEntry.required_artifacts)
    } elseif ($SceneManifestEntry.PSObject.Properties['capture_kind'] -and
              $SceneManifestEntry.capture_kind -eq 'evidence_bundle') {
        $requiredArtifacts = @('screenshot', 'sram')
    }

    $missingArtifacts = @($requiredArtifacts | Where-Object { $result.artifacts_captured -notcontains $_ })
    $result.required_artifacts_present = ($missingArtifacts.Count -eq 0)

    if (-not $result.required_artifacts_present) {
        $result.capture_status = 'failed'
        $result.failure_reason = "Required artifacts missing: $($missingArtifacts -join ', ')"
        return $result
    }

    # -----------------------------------------------------------------------
    # Step 2: Validate SRAM integrity and MDRT
    # -----------------------------------------------------------------------
    if ($result.artifacts_captured -contains 'sram') {
        # Parse MDRT block
        $mdrtInfo = Get-MdrtSceneRuntimeInfo -SramPath $sramPath -SramOffset 0x200
        $result.mdrt = $mdrtInfo
        $result.mdrt_present = ($null -ne $mdrtInfo -and $mdrtInfo.valid -eq $true)

        if ($result.mdrt_present) {
            $result.captured_app_scene_id = $mdrtInfo.scene_id
        }

        # Check readiness heartbeat
        $heartbeatOk = Test-MDReadyHeartbeat -SramPath $sramPath -Offset 0x100
        $result.ready_heartbeat_ok = $heartbeatOk
    }

    # -----------------------------------------------------------------------
    # Step 3: Decide scene_match
    # -----------------------------------------------------------------------
    if ($sceneVerificationRequired) {
        if (-not $result.mdrt_present) {
            $result.scene_match = $null
        } else {
            $result.scene_match = ($result.captured_app_scene_id -eq $expectedAppSceneId)
        }
    }

    # -----------------------------------------------------------------------
    # Step 4: Combine into readiness_ok
    # -----------------------------------------------------------------------
    $sceneVerified = (-not $sceneVerificationRequired) -or ($result.scene_match -eq $true)
    $result.readiness_ok = ($result.ready_heartbeat_ok -and $sceneVerified)

    # -----------------------------------------------------------------------
    # Step 5: Close capture_status
    # -----------------------------------------------------------------------
    if ($sceneVerificationRequired -and -not $result.mdrt_present) {
        $result.capture_status = 'failed'
        $errMsg = 'MDRT block absent in save.sram — scene not verifiable.'
        if ($result.mdrt -and $result.mdrt.error) {
            $errMsg = $result.mdrt.error
        }
        $result.failure_reason = $errMsg
    }
    elseif ($sceneVerificationRequired -and $result.scene_match -eq $false) {
        $result.capture_status = 'wrong_scene'
        $result.failure_reason = "Wrong scene captured: expected app_scene_id=$expectedAppSceneId, got MDRT.scene_id=$($result.captured_app_scene_id)"
    }
    elseif ($RequireHeartbeat -and -not $result.ready_heartbeat_ok) {
        $result.capture_status = 'degraded'
        $result.failure_reason = 'Readiness heartbeat not detected — capture is degraded (non-deterministic)'
    }
    else {
        $result.capture_status = 'ok'
        $result.failure_reason = $null
    }

    return $result
}

# ---------------------------------------------------------------------------
# Get-MdrtSceneRuntimeInfo (delegated from scene_regression module)
# ---------------------------------------------------------------------------
function Get-MdrtSceneRuntimeInfo {
    <#
    .SYNOPSIS
        Parses MDRT runtime block from SRAM.
    .PARAMETER SramPath
        Path to save.sram file.
    .PARAMETER SramOffset
        Byte offset where MDRT block starts (default 0x200).
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$SramPath,
        [int]$SramOffset = 0x200
    )

    $result = [ordered]@{
        present     = $false
        valid       = $false
        magic       = $null
        schema      = $null
        total_bytes = $null
        word_count  = $null
        schema_version = $null
        scene_id    = $null
        error       = $null
    }

    if (-not (Test-Path -LiteralPath $SramPath -PathType Leaf)) {
        $result.error = 'SRAM file not found'
        return $result
    }

    try {
        $bytes = [System.IO.File]::ReadAllBytes($SramPath)
    } catch {
        $result.error = "Failed to read SRAM: $($_.Exception.Message)"
        return $result
    }

    # Try candidate offsets: 0x200 (standard), then 0x0 (legacy)
    $candidates = @($SramOffset, 0x0)
    foreach ($offset in $candidates) {
        if (($offset + 10) -gt $bytes.Length) { continue }

        $magic = [System.Text.Encoding]::ASCII.GetString($bytes, $offset, 4)
        if ($magic -ne 'MDRT') { continue }

        $result.present = $true
        $result.magic = $magic

        $schema = ([int]$bytes[$offset + 4] -shl 8) -bor [int]$bytes[$offset + 5]
        $totalBytes = ([int]$bytes[$offset + 6] -shl 8) -bor [int]$bytes[$offset + 7]
        $wordCount = ([int]$bytes[$offset + 8] -shl 8) -bor [int]$bytes[$offset + 9]

        $result.schema = $schema
        $result.total_bytes = $totalBytes
        $result.word_count = $wordCount

        if ($wordCount -lt 1 -or $wordCount -gt 8192) {
            $result.error = "MDRT word_count out of range: $wordCount"
            return $result
        }

        $payloadStart = $offset + 10
        $payloadEnd = $payloadStart + ($wordCount * 2)
        if ($payloadEnd -gt $bytes.Length) {
            $result.error = "MDRT payload extends beyond SRAM (need $payloadEnd, have $($bytes.Length))"
            return $result
        }

        $words = New-Object int[] $wordCount
        $pos = $payloadStart
        for ($i = 0; $i -lt $wordCount; $i++) {
            $words[$i] = (([int]$bytes[$pos] -shl 8) -bor [int]$bytes[$pos + 1])
            $pos += 2
        }

        # Match the canonical parser used by scene_regression/parse_blastem_sram_runtime.
        if ($wordCount -ge 3) {
            $result.schema_version = [int]$words[2]
        }
        if ($wordCount -ge 6) {
            $result.scene_id = [int]$words[5]
        }

        $result.valid = $true
        return $result
    }

    $result.error = 'MDRT signature not found at any candidate offset'
    return $result
}

# ---------------------------------------------------------------------------
# Exports
# ---------------------------------------------------------------------------
Export-ModuleMember -Function @(
    'Test-SceneCaptureSuccess',
    'Get-MdrtSceneRuntimeInfo'
)
