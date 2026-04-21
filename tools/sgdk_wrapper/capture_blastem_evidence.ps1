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
$closeResult = $null

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
    $artifact['readiness_ok'] = $readyResult.Ready

    if (-not $readyResult.Ready) {
        Write-Host "[WARN]  Readiness heartbeat not detected — capture will proceed in degraded mode"
    }

    # Capture evidence
    $captureResult = Invoke-BlastemEvidenceCapture `
        -Session $session `
        -CaptureMode $CaptureMode `
        -EvidenceRoot $OutputRoot

    # Stop session
    $closeResult = Stop-BlastemEvidenceSession -Session $session

    $artifact['session_completed'] = $true
    $artifact['screenshot_present'] = ($null -ne $captureResult.ScreenshotPath)
    $artifact['sram_present'] = ($null -ne $captureResult.SramPath)
    $artifact['vdp_dump_present'] = ($null -ne $captureResult.VdpDumpPath)

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
        artifacts          = [ordered]@{
            screenshot = if ($captureResult.ScreenshotPath) { 'screenshot.png' } else { $null }
            sram       = if ($captureResult.SramPath) { 'save.sram' } else { $null }
            vdp_dump   = if ($captureResult.VdpDumpPath) { 'visual_vdp_dump.bin' } else { $null }
        }
        process_id         = $session.Process.Id
        exit_code          = $closeResult.ExitCode
        close_mode         = $closeResult.ExitMode
        errors             = @()
    }

    $manifestPath = Join-Path $OutputRoot 'session_manifest.json'
    & $WriteArtifactJson -Data $manifestData -Path $manifestPath | Out-Null
    $artifact['session_manifest_path'] = $manifestPath

    # Evaluate evidence completeness
    $bundle = Test-BlastemEvidenceBundle -SessionRoot $OutputRoot
    $issues = @()

    if (-not $bundle.Complete) {
        $issues += "Incomplete evidence bundle. Missing: $($bundle.Missing -join ', ')"
    }
    if (-not $readyResult.Ready) {
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
    if ($session -and $session.Process -and -not $session.Process.HasExited) {
        try { Stop-BlastemEvidenceSession -Session $session | Out-Null } catch {}
    }
    Complete-WithFailure "Capture session error: $errMsg"
}

# ---------------------------------------------------------------------------
# Write final artifact
# ---------------------------------------------------------------------------
$artifact['duration_ms'] = [int]((Get-Date) - $startTime).TotalMilliseconds
& $WriteArtifactJson -Data $artifact -Path $artifactPath | Out-Null

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
