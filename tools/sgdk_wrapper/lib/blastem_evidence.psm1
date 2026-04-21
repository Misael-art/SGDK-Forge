<#
.SYNOPSIS
    BlastEm canonical evidence capture module for the AAA agent ecosystem.
.DESCRIPTION
    Provides functions to start an isolated BlastEm session, wait for readiness,
    capture evidence (screenshot, SRAM, VDP dump), and cleanly shut down.

    Reuses blastem_automation.psm1 for all Win32 interaction — does NOT
    duplicate keyboard injection, window management, or SRAM detection.

    This module does NOT modify any existing wrapper behavior.
    It is consumed only by capture_blastem_evidence.ps1.
.NOTES
    All evidence goes to an isolated directory under out/evidence/blastem/.
    No existing out/ artifacts are modified.
#>

Set-StrictMode -Version Latest

# Import the canonical automation library
$script:AutomationModule = Join-Path $PSScriptRoot 'blastem_automation.psm1'
if (Test-Path -LiteralPath $script:AutomationModule) {
    Import-Module $script:AutomationModule -Force
}

# Import artifact contracts
$script:ContractsModule = Join-Path $PSScriptRoot 'sgdk_artifact_contracts.psm1'
if (Test-Path -LiteralPath $script:ContractsModule) {
    Import-Module $script:ContractsModule -Force
}

# ---------------------------------------------------------------------------
# Start-BlastemEvidenceSession
# ---------------------------------------------------------------------------
function Start-BlastemEvidenceSession {
    <#
    .SYNOPSIS
        Starts an isolated BlastEm process with a sandboxed environment for evidence capture.
    .PARAMETER EmulatorPath
        Absolute path to blastem.exe.
    .PARAMETER RomPath
        Absolute path to the ROM file.
    .PARAMETER OutputRoot
        Absolute path to the evidence output directory (e.g. out/evidence/blastem).
    .PARAMETER BootTimeoutMs
        Maximum milliseconds to wait for BlastEm window to appear.
    .OUTPUTS
        Hashtable with: Process, SandboxRoot, SaveRoot, ScreenshotRoot, LogPath,
        ProcessStartedAtUtc, SessionId.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$EmulatorPath,
        [Parameter(Mandatory)][string]$RomPath,
        [Parameter(Mandatory)][string]$OutputRoot,
        [int]$BootTimeoutMs = 20000
    )

    Ensure-BlastEmAutomationLoaded

    $sessionId = (Get-Date).ToString('yyyyMMdd_HHmmss') + '_' + ([guid]::NewGuid().ToString('N').Substring(0,8))

    # Sandbox structure
    $sandboxRoot = Join-Path $OutputRoot "sandbox_$sessionId"
    $sandboxHome = Join-Path $sandboxRoot 'Home'
    $sandboxLocalAppData = Join-Path $sandboxHome 'AppData\Local'
    $sandboxAppData = Join-Path $sandboxHome 'AppData\Roaming'
    $sandboxUserDir = Join-Path $sandboxLocalAppData 'blastem'
    $sandboxUserCfg = Join-Path $sandboxUserDir 'blastem.cfg'
    $saveRoot = Join-Path $sandboxRoot 'saves'
    $screenshotRoot = Join-Path $sandboxRoot 'screenshots'
    $logPath = Join-Path $OutputRoot "evidence_session_$sessionId.log"

    foreach ($dir in @($sandboxLocalAppData, $sandboxAppData, $sandboxHome, $sandboxUserDir, $saveRoot, $screenshotRoot)) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
    }

    # Write sandboxed BlastEm config
    $blastEmRoot = Split-Path $EmulatorPath -Parent
    $defaultCfg = Join-Path $blastEmRoot 'default.cfg'
    if (-not (Test-Path -LiteralPath $defaultCfg)) {
        throw "default.cfg not found at $defaultCfg"
    }
    Write-BlastEmConfig -BaseConfigPath $defaultCfg -TargetConfigPath $sandboxUserCfg -SaveRoot $saveRoot -ScreenshotRoot $screenshotRoot

    Write-BlastEmCaptureLog -LogPath $logPath -Event 'evidence_session_start' -Data @{
        session_id = $sessionId
        rom = $RomPath
        sandbox_root = $sandboxRoot
        emulator = $EmulatorPath
    }

    # Start BlastEm with sandboxed environment
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $EmulatorPath
    $psi.Arguments = ('"' + $RomPath + '"')
    $psi.WorkingDirectory = $blastEmRoot
    $psi.UseShellExecute = $false
    $psi.Environment['LOCALAPPDATA'] = $sandboxLocalAppData
    $psi.Environment['APPDATA'] = $sandboxAppData
    $psi.Environment['USERPROFILE'] = $sandboxHome
    $psi.Environment['HOME'] = $sandboxHome

    $startedAtUtc = [datetime]::UtcNow
    $process = [System.Diagnostics.Process]::Start($psi)
    if (-not $process) {
        throw "Failed to start BlastEm process."
    }

    Write-BlastEmCaptureLog -LogPath $logPath -Event 'process_started' -Data @{ pid = $process.Id }

    # Wait for window
    $deadline = (Get-Date).AddMilliseconds($BootTimeoutMs)
    while ((Get-Date) -lt $deadline) {
        $process.Refresh()
        if ($process.HasExited) {
            throw "BlastEm exited before exposing main window (exit code: $($process.ExitCode))."
        }
        if ($process.MainWindowHandle -ne [IntPtr]::Zero) { break }
        Start-Sleep -Milliseconds 250
    }
    $process.Refresh()
    if ($process.MainWindowHandle -eq [IntPtr]::Zero) {
        throw "BlastEm main window did not appear within ${BootTimeoutMs}ms."
    }

    Write-BlastEmCaptureLog -LogPath $logPath -Event 'window_ready' -Data @{
        title = $process.MainWindowTitle
        hwnd = [int64]$process.MainWindowHandle
    }

    return @{
        Process              = $process
        SandboxRoot          = $sandboxRoot
        SaveRoot             = $saveRoot
        ScreenshotRoot       = $screenshotRoot
        LogPath              = $logPath
        ProcessStartedAtUtc  = $startedAtUtc
        SessionId            = $sessionId
    }
}

# ---------------------------------------------------------------------------
# Wait-BlastemReady
# ---------------------------------------------------------------------------
function Wait-BlastemReady {
    <#
    .SYNOPSIS
        Waits for BlastEm to signal readiness via SRAM heartbeat.
    .PARAMETER Session
        Session hashtable from Start-BlastemEvidenceSession.
    .PARAMETER WarmupMs
        Milliseconds to wait before checking readiness.
    .PARAMETER TimeoutMs
        Maximum milliseconds to wait for readiness signal.
    .OUTPUTS
        Hashtable with: Ready (bool), SramPath (string or null).
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][hashtable]$Session,
        [int]$WarmupMs = 3000,
        [int]$TimeoutMs = 15000
    )

    $process = $Session.Process
    $logPath = $Session.LogPath

    # Bring to foreground for input acceptance
    $fgOk = Ensure-BlastEmForeground -Process $process
    Write-BlastEmCaptureLog -LogPath $logPath -Event 'foreground_for_warmup' -Data @{ success = [bool]$fgOk }

    # Initial warmup wait
    if ($WarmupMs -gt 0) {
        Start-Sleep -Milliseconds $WarmupMs
    }

    # Check if process still alive
    $process.Refresh()
    if ($process.HasExited) {
        return @{ Ready = $false; SramPath = $null }
    }

    # Poll for SRAM heartbeat
    $deadline = (Get-Date).AddMilliseconds($TimeoutMs)
    $saveRoots = @($Session.SaveRoot, $Session.SandboxRoot)

    while ((Get-Date) -lt $deadline) {
        $process.Refresh()
        if ($process.HasExited) {
            Write-BlastEmCaptureLog -LogPath $logPath -Event 'process_exited_during_wait' -Data @{ exit_code = $process.ExitCode }
            break
        }

        $sram = Find-FirstSramWithReady -RootPaths $saveRoots -HeartbeatOffset 0x100 -ProcessStartedAtUtc $Session.ProcessStartedAtUtc -SandboxRoot $Session.SandboxRoot
        if ($sram) {
            Write-BlastEmCaptureLog -LogPath $logPath -Event 'ready_heartbeat_found' -Data @{ sram_path = $sram }
            return @{ Ready = $true; SramPath = $sram }
        }

        # Try flush cycle periodically
        if (((Get-Date) - $Session.ProcessStartedAtUtc).TotalSeconds -gt 8) {
            Invoke-BlastEmFlushCycle -Process $process -LogPath $logPath
        }

        Start-Sleep -Milliseconds 500
    }

    Write-BlastEmCaptureLog -LogPath $logPath -Event 'ready_timeout' -Data @{ timeout_ms = $TimeoutMs }
    return @{ Ready = $false; SramPath = $null }
}

# ---------------------------------------------------------------------------
# Invoke-BlastemEvidenceCapture
# ---------------------------------------------------------------------------
function Invoke-BlastemEvidenceCapture {
    <#
    .SYNOPSIS
        Captures evidence artifacts from a running BlastEm session.
    .PARAMETER Session
        Session hashtable from Start-BlastemEvidenceSession.
    .PARAMETER CaptureMode
        "canonical" (screenshot+sram+vdp), "minimal" (screenshot only), "debug" (all+extras).
    .PARAMETER EvidenceRoot
        Absolute path to write evidence files.
    .OUTPUTS
        Hashtable with: ScreenshotPath, SramPath, VdpDumpPath, Captured (list of artifact names).
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][hashtable]$Session,
        [string]$CaptureMode = 'canonical',
        [Parameter(Mandatory)][string]$EvidenceRoot
    )

    $process = $Session.Process
    $logPath = $Session.LogPath
    $captured = @()
    $result = @{
        ScreenshotPath = $null
        SramPath       = $null
        VdpDumpPath    = $null
        Captured       = @()
    }

    if (-not (Test-Path -LiteralPath $EvidenceRoot)) {
        New-Item -ItemType Directory -Force -Path $EvidenceRoot | Out-Null
    }

    $process.Refresh()
    if ($process.HasExited) {
        Write-BlastEmCaptureLog -LogPath $logPath -Event 'capture_skip_process_exited'
        return $result
    }

    # Ensure foreground for screenshot
    Ensure-BlastEmForeground -Process $process | Out-Null

    # Screenshot (all modes)
    $screenshotPath = Join-Path $EvidenceRoot 'screenshot.png'
    $ssOk = Save-BlastEmWindowScreenshot -Process $process -OutputPath $screenshotPath
    if ($ssOk -and (Test-Path -LiteralPath $screenshotPath)) {
        $result.ScreenshotPath = $screenshotPath
        $captured += 'screenshot'
        Write-BlastEmCaptureLog -LogPath $logPath -Event 'screenshot_captured' -Data @{ path = $screenshotPath }
    } else {
        Write-BlastEmCaptureLog -LogPath $logPath -Event 'screenshot_failed'
    }

    # SRAM capture (canonical and debug modes)
    if ($CaptureMode -in @('canonical', 'debug')) {
        # Trigger SRAM flush
        Invoke-BlastEmFlushCycle -Process $process -LogPath $logPath
        Start-Sleep -Milliseconds 1000

        # Find and copy SRAM
        $sramFiles = Get-ChildItem -Path @($Session.SaveRoot, $Session.SandboxRoot) -Include '*.sram','*.srm','*.sav' -Recurse -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTimeUtc -Descending
        if ($sramFiles.Count -gt 0) {
            $sramDest = Join-Path $EvidenceRoot 'save.sram'
            Copy-Item -LiteralPath $sramFiles[0].FullName -Destination $sramDest -Force
            if (Test-Path -LiteralPath $sramDest) {
                $result.SramPath = $sramDest
                $captured += 'sram'
                Write-BlastEmCaptureLog -LogPath $logPath -Event 'sram_captured' -Data @{
                    source = $sramFiles[0].FullName
                    dest = $sramDest
                }
            }
        } else {
            Write-BlastEmCaptureLog -LogPath $logPath -Event 'sram_not_found'
        }
    }

    # VDP dump (canonical and debug modes)
    # NOTE: VDP dump capability depends on BlastEm version and configuration.
    # This is a best-effort capture — if no dump is available, we record the gap
    # rather than faking data. This is a documented "decision pending" per roadmap.
    if ($CaptureMode -in @('canonical', 'debug')) {
        $vdpDumpPath = Join-Path $EvidenceRoot 'visual_vdp_dump.bin'
        # Look for any VDP dump files in sandbox
        $vdpFiles = Get-ChildItem -Path $Session.SandboxRoot -Include '*.vdp','*vram*','*vdp*dump*' -Recurse -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTimeUtc -Descending
        if ($vdpFiles.Count -gt 0) {
            Copy-Item -LiteralPath $vdpFiles[0].FullName -Destination $vdpDumpPath -Force
            if (Test-Path -LiteralPath $vdpDumpPath) {
                $result.VdpDumpPath = $vdpDumpPath
                $captured += 'vdp_dump'
                Write-BlastEmCaptureLog -LogPath $logPath -Event 'vdp_dump_captured' -Data @{
                    source = $vdpFiles[0].FullName
                    dest = $vdpDumpPath
                }
            }
        } else {
            Write-BlastEmCaptureLog -LogPath $logPath -Event 'vdp_dump_not_available' -Data @{
                note = 'VDP dump format from BlastEm not yet documented. Registered as decision pending.'
            }
        }
    }

    $result.Captured = $captured
    return $result
}

# ---------------------------------------------------------------------------
# Stop-BlastemEvidenceSession
# ---------------------------------------------------------------------------
function Stop-BlastemEvidenceSession {
    <#
    .SYNOPSIS
        Gracefully stops a BlastEm evidence session using the canonical close escalation.
    .PARAMETER Session
        Session hashtable from Start-BlastemEvidenceSession.
    .OUTPUTS
        Hashtable with: ExitMode, ExitCode, Forced.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][hashtable]$Session
    )

    $process = $Session.Process
    $logPath = $Session.LogPath

    $process.Refresh()
    if ($process.HasExited) {
        return @{
            ExitMode = 'already_exited'
            ExitCode = $process.ExitCode
            Forced   = $false
        }
    }

    $closeResult = Close-BlastEmGracefully -Process $process -LogPath $logPath
    $exitMode = if ($closeResult) { $closeResult.exit_mode } else { 'unknown' }
    $forced = if ($closeResult) { [bool]$closeResult.forced } else { $false }

    # Wait for exit after close
    $exited = $process.WaitForExit(5000)
    $exitCode = if ($exited) { $process.ExitCode } else { $null }

    # Force kill if still running
    if (-not $exited) {
        try {
            $process.Kill()
            $process.WaitForExit(3000)
            $exitMode = 'force_kill'
            $forced = $true
            $exitCode = $process.ExitCode
        } catch {
            Write-BlastEmCaptureLog -LogPath $logPath -Event 'force_kill_error' -Data @{ message = $_.Exception.Message }
        }
    }

    Write-BlastEmCaptureLog -LogPath $logPath -Event 'session_stopped' -Data @{
        exit_mode = $exitMode
        exit_code = $exitCode
        forced = $forced
    }

    return @{
        ExitMode = $exitMode
        ExitCode = $exitCode
        Forced   = $forced
    }
}

# ---------------------------------------------------------------------------
# Test-BlastemEvidenceBundle
# ---------------------------------------------------------------------------
function Test-BlastemEvidenceBundle {
    <#
    .SYNOPSIS
        Validates that the expected evidence artifacts exist in the output directory.
    .PARAMETER SessionRoot
        Absolute path to the evidence output directory.
    .PARAMETER RequireVdpDump
        If set, VDP dump is required for the bundle to be considered complete.
    .OUTPUTS
        Hashtable with: Complete (bool), ScreenshotPresent, SramPresent, VdpDumpPresent, Missing (list).
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$SessionRoot,
        [switch]$RequireVdpDump
    )

    $screenshot = Test-Path -LiteralPath (Join-Path $SessionRoot 'screenshot.png')
    $sram = Test-Path -LiteralPath (Join-Path $SessionRoot 'save.sram')
    $vdp = Test-Path -LiteralPath (Join-Path $SessionRoot 'visual_vdp_dump.bin')

    $missing = @()
    if (-not $screenshot) { $missing += 'screenshot' }
    if (-not $sram) { $missing += 'sram' }
    if ($RequireVdpDump -and -not $vdp) { $missing += 'vdp_dump' }

    $complete = ($missing.Count -eq 0)

    return @{
        Complete           = $complete
        ScreenshotPresent  = $screenshot
        SramPresent        = $sram
        VdpDumpPresent     = $vdp
        Missing            = $missing
    }
}

# ---------------------------------------------------------------------------
# Exports
# ---------------------------------------------------------------------------
Export-ModuleMember -Function @(
    'Start-BlastemEvidenceSession',
    'Wait-BlastemReady',
    'Invoke-BlastemEvidenceCapture',
    'Stop-BlastemEvidenceSession',
    'Test-BlastemEvidenceBundle'
)
