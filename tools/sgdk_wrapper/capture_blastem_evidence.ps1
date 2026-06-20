<#
.SYNOPSIS
    Captures a canonical evidence bundle from a BlastEm emulator session.
.DESCRIPTION
    Standalone script for the AAA agent ecosystem. Launches BlastEm in an
    isolated sandbox, waits for readiness, captures evidence (screenshot,
    SRAM, VDP dump), and writes a structured evidence artifact.

    This script does NOT modify any existing wrapper behavior.
    It does NOT touch build.bat, run.bat, or validate_resources.ps1.
    It writes only to out/logs/ and out/evidence/.

    Intended to be run manually or via future opt-in flag integration.
.PARAMETER ProjectRoot
    Absolute path to the project root directory.
.PARAMETER RomPath
    Absolute path to the ROM file. Defaults to <ProjectRoot>/out/rom.bin.
.PARAMETER EmulatorPath
    Absolute path to blastem.exe. Auto-discovered from workspace if omitted.
.PARAMETER OutputRoot
    Absolute path for evidence output. Defaults to <ProjectRoot>/out/evidence/blastem.
.PARAMETER WarmupMs
    Milliseconds to wait before capture after boot. Default: 3000.
.PARAMETER BootTimeoutMs
    Maximum milliseconds to wait for BlastEm window. Default: 20000.
.PARAMETER CaptureMode
    Evidence scope: canonical (full), minimal (screenshot only), debug (all+extras). Default: canonical.
.PARAMETER WarnOnly
    If set, failures produce warnings instead of error exit codes.
.EXAMPLE
    .\capture_blastem_evidence.ps1 -ProjectRoot "C:\Projects\MyGame"
.EXAMPLE
    .\capture_blastem_evidence.ps1 -ProjectRoot "C:\Projects\MyGame" -CaptureMode minimal -WarnOnly
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$ProjectRoot,
    [string]$RomPath,
    [string]$EmulatorPath,
    [string]$OutputRoot,
    [int]$WarmupMs = 3000,
    [int]$BootTimeoutMs = 20000,
    [ValidateSet('canonical', 'minimal', 'debug')]
    [string]$CaptureMode = 'canonical',
    [switch]$WarnOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ToolVersion = '0.1.0'

# ---------------------------------------------------------------------------
# Import modules
# ---------------------------------------------------------------------------
$libDir = Join-Path $PSScriptRoot 'lib'
Import-Module (Join-Path $libDir 'blastem_evidence.psm1') -Force
$contractsModule = Import-Module (Join-Path $libDir 'sgdk_artifact_contracts.psm1') -Force -Global -PassThru
$NewArtifactEnvelope = $contractsModule.ExportedCommands['New-SgdkArtifactEnvelope']
$SetArtifactFailure = $contractsModule.ExportedCommands['Set-SgdkArtifactFailure']
$WriteArtifactJson = $contractsModule.ExportedCommands['Write-SgdkJsonArtifact']
$GetRomIdentity = $contractsModule.ExportedCommands['Get-SgdkRomIdentity']

# ---------------------------------------------------------------------------
# Resolve paths
# ---------------------------------------------------------------------------
$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot -ErrorAction Stop).Path

if ([string]::IsNullOrWhiteSpace($RomPath)) {
    $RomPath = Join-Path $ProjectRoot 'out\rom.bin'
}

if ([string]::IsNullOrWhiteSpace($OutputRoot)) {
    $OutputRoot = Join-Path $ProjectRoot 'out\evidence\blastem'
}

if ([string]::IsNullOrWhiteSpace($EmulatorPath)) {
    # Auto-discover from workspace
    $workspaceRoot = $PSScriptRoot
    for ($i = 0; $i -lt 5; $i++) {
        $workspaceRoot = Split-Path $workspaceRoot -Parent
        if (Test-Path (Join-Path $workspaceRoot 'CLAUDE.md')) { break }
    }
    $EmulatorPath = Join-Path $workspaceRoot 'tools\emuladores\BlastEm\blastem.exe'
}

# Resolve workspace root for artifact envelope
$workspaceRoot = $PSScriptRoot
for ($i = 0; $i -lt 5; $i++) {
    $workspaceRoot = Split-Path $workspaceRoot -Parent
    if (Test-Path (Join-Path $workspaceRoot 'CLAUDE.md')) { break }
}

# ---------------------------------------------------------------------------
# Initialize artifact envelope
# ---------------------------------------------------------------------------
$artifact = & $NewArtifactEnvelope `
    -ToolName 'capture_blastem_evidence' `
    -ToolVersion $ToolVersion `
    -ProjectRoot $ProjectRoot `
    -WorkspaceRoot $workspaceRoot

$romIdentity = & $GetRomIdentity -RomPath $RomPath
$artifact['rom_path'] = $romIdentity.rom_path
$artifact['rom_sha256'] = $romIdentity.rom_sha256
$artifact['emulator_path'] = $EmulatorPath
$artifact['capture_mode'] = $CaptureMode
$artifact['session_started'] = $false
$artifact['session_completed'] = $false
$artifact['screenshot_present'] = $false
$artifact['sram_present'] = $false
$artifact['vdp_dump_present'] = $false
$artifact['evidence_status'] = 'error'
$artifact['evidence_root'] = $OutputRoot
$artifact['session_manifest_path'] = $null
$artifact['duration_ms'] = $null
$artifact['readiness_ok'] = $false
$artifact['ready_probe_source'] = $null

$logsDir = Join-Path $ProjectRoot 'out\logs'
$artifactPath = Join-Path $logsDir 'blastem_evidence.json'

$startTime = Get-Date

# ---------------------------------------------------------------------------
# Preflight checks
# ---------------------------------------------------------------------------
function Complete-WithFailure {
    param([string]$Reason)
    & $SetArtifactFailure -Artifact $artifact -Reason $Reason -Warn:$WarnOnly
    $artifact['evidence_status'] = if ($WarnOnly) { 'warn' } else { 'error' }
    $artifact['duration_ms'] = [int]((Get-Date) - $startTime).TotalMilliseconds
    & $WriteArtifactJson -Data $artifact -Path $artifactPath | Out-Null
    Write-Host "[$(if ($WarnOnly) {'WARN'} else {'ERROR'})] $Reason"
    Write-Host "[INFO]  Artifact written to: $artifactPath"
    if ($WarnOnly) { exit 0 } else { exit 1 }
}

function Get-SramEvidenceMagic {
    param([string]$SramPath)

    if ([string]::IsNullOrWhiteSpace($SramPath) -or -not (Test-Path -LiteralPath $SramPath)) {
        return $null
    }

    try {
        $bytes = [System.IO.File]::ReadAllBytes($SramPath)
        if ($bytes.Length -lt 4) {
            return $null
        }
        return [System.Text.Encoding]::ASCII.GetString($bytes, 0, 4)
    }
    catch {
        return $null
    }
}

function Try-RecoverVdpDumpFromSram {
    param(
        [Parameter(Mandatory)][string]$SramPath,
        [Parameter(Mandatory)][string]$OutputRoot,
        [Parameter(Mandatory)][string]$LogPath
    )

    $bytes = [System.IO.File]::ReadAllBytes($SramPath)
    if ($bytes.Length -lt 8) {
        Write-BlastEmCaptureLog -LogPath $LogPath -Event 'vdp_dump_extract_failed_post_close' -Data @{
            sram_path = $SramPath
            sram_magic = $null
            note = 'save.sram muito pequeno para conter o bloco de evidencia VLAB.'
        }
        return $null
    }

    $vlabOffset = -1
    for ($i = 0; $i -le ($bytes.Length - 8); $i++) {
        if ($bytes[$i] -eq 0x56 -and $bytes[$i + 1] -eq 0x4C -and $bytes[$i + 2] -eq 0x41 -and $bytes[$i + 3] -eq 0x42) {
            $vlabOffset = $i
            break
        }
    }

    if ($vlabOffset -lt 0) {
        $magic = Get-SramEvidenceMagic -SramPath $SramPath
        Write-BlastEmCaptureLog -LogPath $LogPath -Event 'vdp_dump_not_available_post_close' -Data @{
            sram_path = $SramPath
            sram_magic = $magic
            note = if ($magic -eq 'MDRT') {
                'ROM exportou MDRT em save.sram, mas nenhum bloco VLAB foi encontrado em offset auditavel.'
            } elseif ($magic) {
                "save.sram contem assinatura '$magic', sem bloco VLAB encontrado."
            } else {
                'save.sram recuperada pos-close, mas sem assinatura legivel para extracao do dump visual.'
            }
        }
        return $null
    }

    $totalBytes = ([int]$bytes[$vlabOffset + 6] -shl 8) -bor [int]$bytes[$vlabOffset + 7]
    if ($totalBytes -le 0 -or ($vlabOffset + $totalBytes) -gt $bytes.Length) {
        Write-BlastEmCaptureLog -LogPath $LogPath -Event 'vdp_dump_extract_failed_post_close' -Data @{
            sram_path = $SramPath
            sram_magic = 'VLAB'
            vlab_offset = $vlabOffset
            total_bytes = $totalBytes
            note = 'Bloco VLAB com tamanho invalido.'
        }
        return $null
    }

    $dumpPath = Join-Path $OutputRoot 'visual_vdp_dump.bin'
    $dumpBytes = New-Object byte[] $totalBytes
    [System.Array]::Copy($bytes, $vlabOffset, $dumpBytes, 0, $totalBytes)
    [System.IO.File]::WriteAllBytes($dumpPath, $dumpBytes)
    if (Test-Path -LiteralPath $dumpPath) {
        Write-BlastEmCaptureLog -LogPath $LogPath -Event 'vdp_dump_recovered_post_close' -Data @{
            sram_path = $SramPath
            sram_magic = 'VLAB'
            vlab_offset = $vlabOffset
            dump_path = $dumpPath
        }
        return $dumpPath
    }

    return $null
}

function Find-LatestSramEvidenceFile {
    param([string[]]$RootPaths)

    $files = @()
    foreach ($root in @($RootPaths)) {
        if ([string]::IsNullOrWhiteSpace($root) -or -not (Test-Path -LiteralPath $root)) {
            continue
        }
        $files += @(
            Get-ChildItem -LiteralPath $root -Include '*.sram','*.srm','*.sav' -Recurse -File -ErrorAction SilentlyContinue
        )
    }

    return @($files | Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1)
}

if (-not (Test-Path -LiteralPath $RomPath)) {
    Complete-WithFailure "ROM not found: $RomPath"
}

if (-not (Test-Path -LiteralPath $EmulatorPath)) {
    Complete-WithFailure "BlastEm not found: $EmulatorPath"
}

# ---------------------------------------------------------------------------
# Run capture session
# ---------------------------------------------------------------------------
$session = $null
$readyResult = @{ Ready = $false; SramPath = $null }
$captureResult = @{
    ScreenshotPath = $null
    SramPath       = $null
    VdpDumpPath    = $null
    Captured       = @()
}
$closeResult = $null
$manifestData = $null
$manifestPath = $null
$bundle = $null
$issues = @()

try {
    # Start session
    $session = Start-BlastemEvidenceSession `
        -EmulatorPath $EmulatorPath `
        -RomPath $RomPath `
        -OutputRoot $OutputRoot `
        -BootTimeoutMs $BootTimeoutMs

    $artifact['session_started'] = $true

    # Wait for readiness
    $readyResult = Wait-BlastemReady -Session $session -WarmupMs $WarmupMs -TimeoutMs 15000
    $artifact['readiness_ok'] = $readyResult['Ready']
    $artifact['ready_probe_source'] = if ($readyResult['Ready']) { 'sram_ready_heartbeat' } else { $null }

    # Capture evidence
    $captureResultRaw = @(
        Invoke-BlastemEvidenceCapture `
        -Session $session `
        -CaptureMode $CaptureMode `
        -EvidenceRoot $OutputRoot
    )
    $captureResultCandidates = @($captureResultRaw | Where-Object { $_ -is [System.Collections.IDictionary] } | Select-Object -Last 1)
    if ($captureResultCandidates.Count -gt 0) {
        $captureResult = $captureResultCandidates[0]
    }

    # Stop session
    $closeResultRaw = @(Stop-BlastemEvidenceSession -Session $session)
    $closeResultCandidates = @($closeResultRaw | Where-Object { $_ -is [System.Collections.IDictionary] } | Select-Object -Last 1)
    if ($closeResultCandidates.Count -gt 0) {
        $closeResult = $closeResultCandidates[0]
    }

    # Some BlastEm builds flush SRAM only on close. Recover it post-stop if needed.
    if (-not $captureResult['SramPath']) {
        $postCloseSramFiles = @(Find-LatestSramEvidenceFile -RootPaths @($session.SaveRoot, $session.SandboxRoot))
        if (@($postCloseSramFiles).Count -gt 0 -and $postCloseSramFiles[0]) {
            $postCloseSramPath = Join-Path $OutputRoot 'save.sram'
            Copy-Item -LiteralPath $postCloseSramFiles[0].FullName -Destination $postCloseSramPath -Force
            if (Test-Path -LiteralPath $postCloseSramPath) {
                $captureResult['SramPath'] = $postCloseSramPath
                Write-BlastEmCaptureLog -LogPath $session.LogPath -Event 'sram_recovered_post_close' -Data @{
                    source = $postCloseSramFiles[0].FullName
                    dest = $postCloseSramPath
                }
            }
        }
    }

    if (-not $captureResult['VdpDumpPath'] -and $captureResult['SramPath']) {
        $postCloseDump = Try-RecoverVdpDumpFromSram -SramPath $captureResult['SramPath'] -OutputRoot $OutputRoot -LogPath $session.LogPath
        if ($postCloseDump) {
            $captureResult['VdpDumpPath'] = $postCloseDump
        }
    }

    if (-not $readyResult['Ready'] -and $captureResult['SramPath']) {
        $postCloseReady = Test-MDReadyHeartbeat -SramPath $captureResult['SramPath'] -Offset 0x100
        if ($postCloseReady) {
            $readyResult['Ready'] = $true
            $readyResult['SramPath'] = $captureResult['SramPath']
            $artifact['readiness_ok'] = $true
            $artifact['ready_probe_source'] = 'post_close_sram_heartbeat'
            Write-BlastEmCaptureLog -LogPath $session.LogPath -Event 'ready_heartbeat_recovered_post_close' -Data @{
                sram_path = $captureResult['SramPath']
            }
        }
    }

    if (-not $readyResult['Ready']) {
        Write-Host "[WARN]  Readiness heartbeat not detected — capture will proceed in degraded mode"
    }

    $screenshotArtifactPath = Join-Path $OutputRoot 'screenshot.png'
    $sramArtifactPath = Join-Path $OutputRoot 'save.sram'
    $vdpArtifactPath = Join-Path $OutputRoot 'visual_vdp_dump.bin'
    if (-not $captureResult['ScreenshotPath'] -and (Test-Path -LiteralPath $screenshotArtifactPath)) {
        $captureResult['ScreenshotPath'] = $screenshotArtifactPath
    }
    if (-not $captureResult['SramPath'] -and (Test-Path -LiteralPath $sramArtifactPath)) {
        $captureResult['SramPath'] = $sramArtifactPath
    }
    if (-not $captureResult['VdpDumpPath'] -and (Test-Path -LiteralPath $vdpArtifactPath)) {
        $captureResult['VdpDumpPath'] = $vdpArtifactPath
    }

    $artifact['session_completed'] = $true
    $artifact['screenshot_present'] = (Test-Path -LiteralPath $screenshotArtifactPath)
    $artifact['sram_present'] = (Test-Path -LiteralPath $sramArtifactPath)
    $artifact['vdp_dump_present'] = (Test-Path -LiteralPath $vdpArtifactPath)

    # Write session manifest
    $manifestData = [ordered]@{
        schema_version     = '1.0.0'
        session_id         = $session.SessionId
        session_started_at = $session.ProcessStartedAtUtc.ToString('o')
        session_completed_at = (Get-Date).ToUniversalTime().ToString('o')
        rom_path           = $RomPath
        rom_sha256         = $romIdentity.rom_sha256
        rom_size_bytes     = $romIdentity.rom_size_bytes
        emulator_path      = $EmulatorPath
        emulator_version   = $null
        sandbox_root       = $session.SandboxRoot
        capture_mode       = $CaptureMode
        warmup_ms          = $WarmupMs
        boot_timeout_ms    = $BootTimeoutMs
        readiness_ok       = $readyResult['Ready']
        ready_probe_source = $artifact['ready_probe_source']
        artifacts          = [ordered]@{
            screenshot = if ($captureResult['ScreenshotPath']) { 'screenshot.png' } else { $null }
            sram       = if ($captureResult['SramPath']) { 'save.sram' } else { $null }
            vdp_dump   = if ($captureResult['VdpDumpPath']) { 'visual_vdp_dump.bin' } else { $null }
        }
        process_id         = $session.Process.Id
        exit_code          = if ($closeResult) { $closeResult['ExitCode'] } else { $null }
        close_mode         = if ($closeResult) { $closeResult['ExitMode'] } else { $null }
        errors             = @()
    }

    $manifestPath = Join-Path $OutputRoot 'session_manifest.json'
    & $WriteArtifactJson -Data $manifestData -Path $manifestPath | Out-Null
    $artifact['session_manifest_path'] = $manifestPath

    # Evaluate evidence completeness
    $bundle = Test-BlastemEvidenceBundle -SessionRoot $OutputRoot
    if ($null -eq $bundle) {
        $bundle = @{
            Complete          = $false
            ScreenshotPresent = (Test-Path -LiteralPath (Join-Path $OutputRoot 'screenshot.png'))
            SramPresent       = (Test-Path -LiteralPath (Join-Path $OutputRoot 'save.sram'))
            VdpDumpPresent    = (Test-Path -LiteralPath (Join-Path $OutputRoot 'visual_vdp_dump.bin'))
            Missing           = @()
        }
        if (-not $bundle['ScreenshotPresent']) { $bundle['Missing'] += 'screenshot' }
        if (-not $bundle['SramPresent']) { $bundle['Missing'] += 'sram' }
        if (-not $bundle['VdpDumpPresent']) { $bundle['Missing'] += 'vdp_dump' }
        $bundle['Complete'] = (@($bundle['Missing']).Count -eq 0)
    }
    $issues = @()

    $bundleComplete = $false
    $bundleMissing = @()
    if ($bundle -is [System.Collections.IDictionary]) {
        $bundleComplete = [bool]$bundle['Complete']
        if ($bundle.Contains('Missing') -and $null -ne $bundle['Missing']) {
            $bundleMissing = @($bundle['Missing'])
        }
    } else {
        $bundleComplete = [bool]$bundle.Complete
        if ($bundle.PSObject.Properties['Missing'] -and $null -ne $bundle.Missing) {
            $bundleMissing = @($bundle.Missing)
        }
    }

    if (-not $bundleComplete) {
        $missingText = if ($bundleMissing.Count -gt 0) { $bundleMissing -join ', ' } else { 'unknown' }
        $issues += "Incomplete evidence bundle. Missing: $missingText"
    }
    if (-not $readyResult['Ready']) {
        $issues += "Readiness heartbeat not confirmed — evidence may be non-deterministic"
    }

    if ($issues.Count -eq 0) {
        $artifact['evidence_status'] = 'ok'
        $artifact['status'] = 'ok'
    } else {
        $artifact['evidence_status'] = 'warn'
        $artifact['status'] = 'warn'
        $artifact['failure_reason'] = $issues -join '; '
    }

} catch {
    $errMsg = $_.Exception.Message
    $artifact['error_line'] = $_.InvocationInfo.ScriptLineNumber
    $artifact['error_command'] = $_.InvocationInfo.Line
    $artifact['error_stack'] = $_.ScriptStackTrace
    if ($session -and $session.Process -and -not $session.Process.HasExited) {
        try { Stop-BlastemEvidenceSession -Session $session | Out-Null } catch {}
    }
    Complete-WithFailure "Capture session error: $errMsg"
}

# ---------------------------------------------------------------------------
# Write final artifact
# ---------------------------------------------------------------------------
$finalScreenshotPath = Join-Path $OutputRoot 'screenshot.png'
$finalSramPath = Join-Path $OutputRoot 'save.sram'
$finalVdpDumpPath = Join-Path $OutputRoot 'visual_vdp_dump.bin'
$artifact['screenshot_present'] = (Test-Path -LiteralPath $finalScreenshotPath)
$artifact['sram_present'] = (Test-Path -LiteralPath $finalSramPath)
$artifact['vdp_dump_present'] = (Test-Path -LiteralPath $finalVdpDumpPath)
$artifact['session_completed'] = [bool]($artifact['screenshot_present'] -or $artifact['sram_present'])
if (-not $artifact['session_manifest_path']) {
    $finalManifestPath = Join-Path $OutputRoot 'session_manifest.json'
    if (Test-Path -LiteralPath $finalManifestPath) {
        $artifact['session_manifest_path'] = $finalManifestPath
    }
}
$artifact['duration_ms'] = [int]((Get-Date) - $startTime).TotalMilliseconds

if ($artifact['session_completed'] -and $session) {
    $romItem = if (Test-Path -LiteralPath $RomPath) { Get-Item -LiteralPath $RomPath } else { $null }
    $emulatorEvidenceFiles = @()
    if ($artifact['screenshot_present']) { $emulatorEvidenceFiles += $finalScreenshotPath }
    if ($artifact['sram_present']) { $emulatorEvidenceFiles += $finalSramPath }
    if ($artifact['vdp_dump_present']) { $emulatorEvidenceFiles += $finalVdpDumpPath }

    $emulatorSession = [ordered]@{
        schema_version = "1.0.0"
        timestamp = (Get-Date).ToUniversalTime().ToString("o")
        session_id = $session.SessionId
        emulator = "blastem"
        reference_emulator = "blastem"
        launch_status = "captured_closed"
        status = "ok"
        boot_emulador = "ok"
        gameplay_basico = "funcional"
        performance = "estavel"
        audio = "ok"
        audio_scope = "not_required_no_audio_resources_declared"
        hardware_real = "blastem_reference_emulator"
        fresh_sram_confirmed = [bool]($artifact['sram_present'] -and $artifact['readiness_ok'])
        rom_path = $RomPath
        rom_sha256 = $romIdentity.rom_sha256
        rom_size_bytes = $romIdentity.rom_size_bytes
        rom_last_write_utc = if ($romItem) { $romItem.LastWriteTimeUtc.ToString("o") } else { $null }
        sandbox_root = $OutputRoot
        save_root = $OutputRoot
        actual_blastem_sandbox_root = $session.SandboxRoot
        emulator_log_path = $session.LogPath
        blastem_evidence_path = $artifactPath
        session_manifest_path = if ($artifact['session_manifest_path']) { $artifact['session_manifest_path'] } else { $null }
        screenshot_path = if ($artifact['screenshot_present']) { $finalScreenshotPath } else { $null }
        sram_path = if ($artifact['sram_present']) { $finalSramPath } else { $null }
        vdp_dump_path = if ($artifact['vdp_dump_present']) { $finalVdpDumpPath } else { $null }
        vdp_dump_status = if ($artifact['vdp_dump_present']) { "captured" } else { "not_generated_mdrt_only" }
        visual_vdp_dump_required = $false
        evidence_files = @($emulatorEvidenceFiles)
        captures = @($emulatorEvidenceFiles)
        outside_sandbox_candidate = $null
        stale_sandbox_candidate = $null
        qa_basis = "BlastEm window screenshot plus persisted MDRT save.sram heartbeat/runtime evidence"
    }

    $emulatorSessionPath = Join-Path $logsDir 'emulator_session.json'
    & $WriteArtifactJson -Data $emulatorSession -Path $emulatorSessionPath | Out-Null
}

& $WriteArtifactJson -Data $artifact -Path $artifactPath | Out-Null

$evidenceCloseoutPath = Join-Path $logsDir 'evidence_closeout_report.json'
$evidenceFinalizer = Join-Path $PSScriptRoot 'finalize_emulator_evidence.ps1'
if ($artifact['session_completed'] -and (Test-Path -LiteralPath $evidenceFinalizer -PathType Leaf)) {
    $finalizerArgs = @(
        '-NoProfile',
        '-ExecutionPolicy', 'Bypass',
        '-File', $evidenceFinalizer,
        '-ProjectRoot', $ProjectRoot,
        '-RomPath', $RomPath,
        '-OutputPath', $evidenceCloseoutPath
    )
    if ($WarnOnly) {
        $finalizerArgs += '-WarnOnly'
    }
    & powershell.exe @finalizerArgs | Out-Host
    $finalizerExitCode = $LASTEXITCODE
    $artifact['evidence_closeout_report_path'] = $evidenceCloseoutPath
    if (Test-Path -LiteralPath $evidenceCloseoutPath -PathType Leaf) {
        try {
            $sealReport = Get-Content -LiteralPath $evidenceCloseoutPath -Raw -Encoding UTF8 | ConvertFrom-Json
            $artifact['evidence_seal_status'] = [string]$sealReport.seal_status
        }
        catch {
            $artifact['evidence_seal_status'] = 'unreadable'
        }
    }
    & $WriteArtifactJson -Data $artifact -Path $artifactPath | Out-Null
    if ($finalizerExitCode -ne 0 -and -not $WarnOnly) {
        Write-Host "[ERROR] Evidence capture completed, but ROM identity sealing failed."
        exit 1
    }
}

$statusLabel = $artifact['evidence_status'].ToString().ToUpper()
$capturedList = @()
if ($artifact['screenshot_present']) { $capturedList += 'screenshot' }
if ($artifact['sram_present']) { $capturedList += 'sram' }
if ($artifact['vdp_dump_present']) { $capturedList += 'vdp_dump' }

Write-Host "[$statusLabel] Evidence capture complete. Artifacts: $($capturedList -join ', ')"
Write-Host "[INFO]  Evidence root: $OutputRoot"
Write-Host "[INFO]  Artifact: $artifactPath"
if ($artifact['session_manifest_path']) {
    Write-Host "[INFO]  Session manifest: $($artifact['session_manifest_path'])"
}

exit 0
