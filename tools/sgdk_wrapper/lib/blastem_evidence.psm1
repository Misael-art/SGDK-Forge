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
# Internal SRAM evidence helpers
# ---------------------------------------------------------------------------
function Get-SramEvidenceMagicInternal {
    param(
        [Parameter(Mandatory)][string]$SramPath
    )

    try {
        $bytes = [System.IO.File]::ReadAllBytes($SramPath)
        if ($bytes.Length -lt 4) {
            return $null
        }
        $rootMagic = [System.Text.Encoding]::ASCII.GetString($bytes, 0, 4)
        if ($rootMagic -eq 'VLAB') {
            return $rootMagic
        }

        foreach ($offset in @(0x200, 0x400)) {
            if ($bytes.Length -ge ($offset + 4)) {
                $magic = [System.Text.Encoding]::ASCII.GetString($bytes, $offset, 4)
                if ($magic -eq 'VLAB') {
                    return $magic
                }
            }
        }

        return $rootMagic
    }
    catch {
        return $null
    }
}

function Extract-VisualEvidenceDumpInternal {
    param(
        [Parameter(Mandatory)][string]$SramPath,
        [Parameter(Mandatory)][string]$OutputPath
    )

    $bytes = [System.IO.File]::ReadAllBytes($SramPath)
    if ($bytes.Length -lt 8) {
        throw "save.sram muito pequeno para conter o bloco de evidencia."
    }

    $blockOffset = $null
    foreach ($offset in @(0, 0x200, 0x400)) {
        if ($bytes.Length -ge ($offset + 8)) {
            $magic = [System.Text.Encoding]::ASCII.GetString($bytes, $offset, 4)
            if ($magic -eq 'VLAB') {
                $blockOffset = $offset
                break
            }
        }
    }

    if ($null -eq $blockOffset) {
        throw "Bloco SRAM nao contem a assinatura VLAB."
    }

    $totalBytes = ([int]$bytes[$blockOffset + 6] -shl 8) -bor [int]$bytes[$blockOffset + 7]
    if ($totalBytes -le 0 -or ($blockOffset + $totalBytes) -gt $bytes.Length) {
        throw "Tamanho do bloco de evidencia invalido: $totalBytes bytes."
    }

    [System.IO.File]::WriteAllBytes($OutputPath, $bytes[$blockOffset..($blockOffset + $totalBytes - 1)])
}

function Get-BlastEmInitialSramPathInternal {
    param(
        [Parameter(Mandatory)][string]$SaveRoot,
        [Parameter(Mandatory)][string]$RomPath
    )

    $romName = [System.IO.Path]::GetFileNameWithoutExtension($RomPath)
    if ([string]::IsNullOrWhiteSpace($romName)) {
        throw "Nao foi possivel resolver o nome base da ROM para o bootstrap SRAM."
    }

    $targetDir = Join-Path $SaveRoot $romName
    New-Item -ItemType Directory -Force -Path $targetDir | Out-Null
    return (Join-Path $targetDir 'save.sram')
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
        [int]$BootTimeoutMs = 20000,
        $InitialSramBytes = @()
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

    $seedBytes = [byte[]]@()
    if ($null -ne $InitialSramBytes) {
        if ($InitialSramBytes -is [byte[]]) {
            $seedBytes = $InitialSramBytes
        } elseif ($InitialSramBytes -is [System.Array] -or $InitialSramBytes -is [System.Collections.IEnumerable]) {
            $seedBytes = [byte[]]@($InitialSramBytes)
        } else {
            $seedBytes = [byte[]]@($InitialSramBytes)
        }
    }

    $initialSramPath = $null
    if ($seedBytes.Length -gt 0) {
        $initialSramPath = Get-BlastEmInitialSramPathInternal -SaveRoot $saveRoot -RomPath $RomPath
        [System.IO.File]::WriteAllBytes($initialSramPath, $seedBytes)
    }

    Write-BlastEmCaptureLog -LogPath $logPath -Event 'evidence_session_start' -Data @{
        session_id = $sessionId
        rom = $RomPath
        sandbox_root = $sandboxRoot
        emulator = $EmulatorPath
        seeded_sram_path = $initialSramPath
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
        InitialSramPath      = $initialSramPath
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

    # Poll for SRAM heartbeat with watcher-assisted waiting and periodic flushes.
    $deadline = [datetime]::UtcNow.AddMilliseconds($TimeoutMs)
    $saveRoots = @($Session.SaveRoot, $Session.SandboxRoot)
    $watchers = @(Start-BlastEmSaveWatchers -RootPaths $saveRoots)
    $nextFlushUtc = [datetime]::UtcNow.AddMilliseconds([Math]::Max(3500, $WarmupMs))

    Write-BlastEmCaptureLog -LogPath $logPath -Event 'ready_wait_begin' -Data @{
        timeout_ms = $TimeoutMs
        warmup_ms = $WarmupMs
        save_roots = $saveRoots
        fsw_watchers = @($watchers).Count
        ready_probe_source = 'sram_ready_heartbeat'
    }

    try {
        while ([datetime]::UtcNow -lt $deadline) {
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

            if ([datetime]::UtcNow -ge $nextFlushUtc) {
                Invoke-BlastEmFlushCycle -Process $process -LogPath $logPath
                Start-Sleep -Milliseconds 900

                $sramAfterFlush = Find-FirstSramWithReady -RootPaths $saveRoots -HeartbeatOffset 0x100 -ProcessStartedAtUtc $Session.ProcessStartedAtUtc -SandboxRoot $Session.SandboxRoot
                if ($sramAfterFlush) {
                    Write-BlastEmCaptureLog -LogPath $logPath -Event 'ready_heartbeat_found_after_flush' -Data @{ sram_path = $sramAfterFlush }
                    return @{ Ready = $true; SramPath = $sramAfterFlush }
                }

                $nextFlushUtc = [datetime]::UtcNow.AddMilliseconds(3500)
            }

            $signal = Wait-ForSramChangeOrDeadline -Watchers $watchers -DeadlineUtc $deadline -PollIntervalMs 450
            if ($signal -eq 'deadline') {
                break
            }
        }
    }
    finally {
        Stop-BlastEmSaveWatchers -Watchers $watchers
    }

    if (-not $process.HasExited) {
        Invoke-BlastEmFlushCycle -Process $process -LogPath $logPath
        Start-Sleep -Milliseconds 1200
        $sramFinal = Find-FirstSramWithReady -RootPaths $saveRoots -HeartbeatOffset 0x100 -ProcessStartedAtUtc $Session.ProcessStartedAtUtc -SandboxRoot $Session.SandboxRoot
        if ($sramFinal) {
            Write-BlastEmCaptureLog -LogPath $logPath -Event 'ready_heartbeat_found_final_flush' -Data @{ sram_path = $sramFinal }
            return @{ Ready = $true; SramPath = $sramFinal }
        }
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
        "canonical" (project canonical evidence bundle; for V2, screenshot+sram with MDRT), "minimal" (screenshot only), "debug" (all+extras, including legacy artifacts when available).
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
        $sramFiles = @(
            Get-ChildItem -Path @($Session.SaveRoot, $Session.SandboxRoot) -Include '*.sram','*.srm','*.sav' -Recurse -ErrorAction SilentlyContinue |
                Sort-Object LastWriteTimeUtc -Descending
        )
        if ($sramFiles.Count -gt 0) {
            $sramDest = Join-Path $EvidenceRoot 'save.sram'
            [System.IO.File]::Copy($sramFiles[0].FullName, $sramDest, $true)
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
    # Prefer the ROM-authored SRAM evidence block when available. This keeps the
    # artifact format deterministic even when BlastEm itself does not expose a
    # raw VDP dump export.
    if ($CaptureMode -in @('canonical', 'debug')) {
        $vdpDumpPath = Join-Path $EvidenceRoot 'visual_vdp_dump.bin'
        $sramMagic = $null

        if ($result.SramPath) {
            $sramMagic = Get-SramEvidenceMagicInternal -SramPath $result.SramPath
            if ($sramMagic -eq 'VLAB') {
                try {
                    Extract-VisualEvidenceDumpInternal -SramPath $result.SramPath -OutputPath $vdpDumpPath
                    if (Test-Path -LiteralPath $vdpDumpPath) {
                        $result.VdpDumpPath = $vdpDumpPath
                        $captured += 'vdp_dump'
                        Write-BlastEmCaptureLog -LogPath $logPath -Event 'vdp_dump_captured' -Data @{
                            source = $result.SramPath
                            dest = $vdpDumpPath
                            source_kind = 'sram_vlab_block'
                        }
                    }
                }
                catch {
                    Write-BlastEmCaptureLog -LogPath $logPath -Event 'vdp_dump_extract_failed' -Data @{
                        sram_path = $result.SramPath
                        sram_magic = $sramMagic
                        message = $_.Exception.Message
                    }
                }
            }
        }

        if (-not $result.VdpDumpPath) {
            Write-BlastEmCaptureLog -LogPath $logPath -Event 'vdp_dump_not_available' -Data @{
                note = if ($sramMagic -eq 'MDRT') {
                    'ROM exportou bloco MDRT em save.sram; visual_vdp_dump.bin exige bloco VLAB ou outro exportador dedicado.'
                } elseif ($sramMagic) {
                    "save.sram contem assinatura '$sramMagic', sem exportador conhecido para visual_vdp_dump.bin."
                } elseif ($result.SramPath) {
                    'save.sram presente, mas sem assinatura legivel para extracao do dump visual.'
                } else {
                    'save.sram nao foi capturada; nao ha fonte para extrair visual_vdp_dump.bin.'
                }
                sram_path = $result.SramPath
                sram_magic = $sramMagic
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
    'Test-BlastemEvidenceBundle',
    'Test-MDReadyHeartbeat',
    'Write-BlastEmCaptureLog'
)
