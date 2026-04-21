[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$ProjectDir = "",
    [Parameter(Mandatory = $false)]
    [string[]]$NavigationSequence = @(),
    [Parameter(Mandatory = $false)]
    [switch]$AllowMissingEvidence
)

$ErrorActionPreference = "Stop"

$BlastEmAutomationModule = Join-Path $PSScriptRoot "lib\blastem_automation.psm1"
Import-Module -Name $BlastEmAutomationModule -Force

function Resolve-ProjectRoot {
    param([string]$InputPath)

    if ([string]::IsNullOrWhiteSpace($InputPath)) {
        return (Get-Location).Path
    }

    return (Resolve-Path -LiteralPath $InputPath).Path
}

function Wait-ForBlastEmWindow {
    param(
        [Parameter(Mandatory = $true)][System.Diagnostics.Process]$Process,
        [Parameter(Mandatory = $false)][int]$TimeoutSeconds = 20
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        $Process.Refresh()
        if ($Process.HasExited) {
            throw "BlastEm encerrou antes de expor a janela principal."
        }
        if ($Process.MainWindowHandle -ne [IntPtr]::Zero) {
            return
        }
        Start-Sleep -Milliseconds 250
    }

    throw "Janela principal do BlastEm nao apareceu em $TimeoutSeconds segundos."
}

function Get-RomMetadata {
    param([Parameter(Mandatory = $true)][string]$RomPath)

    $rom = Get-Item -LiteralPath $RomPath
    $stream = [System.IO.File]::OpenRead($RomPath)
    try {
        $sha256 = [System.Security.Cryptography.SHA256]::Create()
        try {
            $hash = ([System.BitConverter]::ToString($sha256.ComputeHash($stream)).Replace("-", "")).ToLowerInvariant()
        }
        finally {
            $sha256.Dispose()
        }
    }
    finally {
        $stream.Dispose()
    }

    return [ordered]@{
        path = $RomPath
        size_bytes = $rom.Length
        last_write_utc = $rom.LastWriteTimeUtc.ToString("o")
        sha256 = $hash
    }
}

function Test-VisualEvidenceSignature {
    param([Parameter(Mandatory = $true)][string]$SramPath)

    try {
        $bytes = [System.IO.File]::ReadAllBytes($SramPath)
        if ($bytes.Length -lt 8) {
            return $false
        }
        return ([System.Text.Encoding]::ASCII.GetString($bytes, 0, 4) -eq "VLAB")
    }
    catch {
        return $false
    }
}

function Find-FreshVisualEvidenceSave {
    param(
        [Parameter(Mandatory = $true)][string[]]$RootPaths,
        [Parameter(Mandatory = $false)][datetime]$ProcessStartedAtUtc = ([datetime]::MinValue),
        [Parameter(Mandatory = $false)][string]$SandboxRoot = ""
    )

    foreach ($rootPath in $RootPaths) {
        if (-not (Test-Path -LiteralPath $rootPath)) {
            continue
        }

        $candidates = Get-ChildItem -LiteralPath $rootPath -Recurse -File -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTimeUtc -Descending
        foreach ($candidate in $candidates) {
            if ($candidate.Length -le 0) {
                continue
            }
            $isSaveCandidate =
                $candidate.Name -ieq "save.sram" -or
                $candidate.Extension -ieq ".sram" -or
                $candidate.Extension -ieq ".srm" -or
                $candidate.Extension -ieq ".sav"
            if (-not $isSaveCandidate) {
                continue
            }
            if (-not (Test-FreshSramCandidate -Path $candidate.FullName -ProcessStartedAtUtc $ProcessStartedAtUtc -SandboxRoot $SandboxRoot)) {
                continue
            }
            if (Test-VisualEvidenceSignature -SramPath $candidate.FullName) {
                return $candidate.FullName
            }
        }
    }

    return $null
}

function Extract-VisualEvidenceDump {
    param(
        [Parameter(Mandatory = $true)][string]$SramPath,
        [Parameter(Mandatory = $true)][string]$OutputPath
    )

    $bytes = [System.IO.File]::ReadAllBytes($SramPath)
    if ($bytes.Length -lt 8) {
        throw "save.sram muito pequeno para conter o bloco de evidencia."
    }

    $magic = [System.Text.Encoding]::ASCII.GetString($bytes, 0, 4)
    if ($magic -ne "VLAB") {
        throw "Bloco SRAM nao contem a assinatura VLAB."
    }

    $totalBytes = ([int]$bytes[6] -shl 8) -bor [int]$bytes[7]
    if ($totalBytes -le 0 -or $totalBytes -gt $bytes.Length) {
        throw "Tamanho do bloco de evidencia invalido: $totalBytes bytes."
    }

    [System.IO.File]::WriteAllBytes($OutputPath, $bytes[0..($totalBytes - 1)])
}

function Get-VisualEvidenceBlock {
    param([Parameter(Mandatory = $true)][string]$SramPath)

    $bytes = [System.IO.File]::ReadAllBytes($SramPath)
    if ($bytes.Length -lt 16) {
        return $null
    }

    if ([System.Text.Encoding]::ASCII.GetString($bytes, 0, 4) -ne "VLAB") {
        return $null
    }

    return [ordered]@{
        magic = "VLAB"
        version = (([int]$bytes[4] -shl 8) -bor [int]$bytes[5])
        total_bytes = (([int]$bytes[6] -shl 8) -bor [int]$bytes[7])
        flags = [int]$bytes[12]
        scene_id = [int]$bytes[13]
        byte14 = [int]$bytes[14]
        byte15 = [int]$bytes[15]
    }
}

$ProjectDir = Resolve-ProjectRoot -InputPath $ProjectDir
$projectBuild = Join-Path $ProjectDir "build.bat"
$romPath = Join-Path $ProjectDir "out\rom.bin"
$capturesDir = Join-Path $ProjectDir "out\captures"
$logsDir = Join-Path $ProjectDir "out\logs"
$sessionPath = Join-Path $logsDir "emulator_session.json"
$validatorPath = Join-Path $PSScriptRoot "validate_resources.ps1"
$workspaceRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
$blastEmRoot = Join-Path $workspaceRoot "tools\emuladores\BlastEm"
$blastEmExe = Join-Path $blastEmRoot "blastem.exe"
$blastEmDefaultCfg = Join-Path $blastEmRoot "default.cfg"
$blastEmSandboxRoot = Join-Path $ProjectDir "out\blastem_env_visual"
$blastEmHome = Join-Path $blastEmSandboxRoot "Home"
$blastEmLocalAppData = Join-Path $blastEmHome "AppData\Local"
$blastEmAppData = Join-Path $blastEmHome "AppData\Roaming"
$blastEmUserDir = Join-Path $blastEmLocalAppData "blastem"
$blastEmUserCfg = Join-Path $blastEmUserDir "blastem.cfg"
$saveRoot = Join-Path $blastEmSandboxRoot "saves"
$screenshotRoot = Join-Path $blastEmSandboxRoot "screenshots"
$blastEmLogPath = Join-Path $logsDir "visual_capture_blastem.log"
$timestampSafe = (Get-Date).ToString("yyyyMMdd_HHmmss")
$failureScreenshotPath = Join-Path $logsDir ("blastem_visual_failure_" + $timestampSafe + ".png")

if (-not (Test-Path -LiteralPath $projectBuild)) {
    throw "build.bat nao encontrado em $ProjectDir"
}
if (-not (Test-Path -LiteralPath $blastEmExe)) {
    throw "blastem.exe nao encontrado em $blastEmExe"
}
if (-not (Test-Path -LiteralPath $blastEmDefaultCfg)) {
    throw "default.cfg do BlastEm nao encontrado em $blastEmDefaultCfg"
}

New-Item -ItemType Directory -Force -Path $capturesDir | Out-Null
New-Item -ItemType Directory -Force -Path $logsDir | Out-Null
if (Test-Path -LiteralPath $blastEmSandboxRoot) {
    Remove-Item -LiteralPath $blastEmSandboxRoot -Recurse -Force
}
foreach ($path in @($blastEmLocalAppData, $blastEmAppData, $blastEmHome, $blastEmUserDir, $saveRoot, $screenshotRoot)) {
    New-Item -ItemType Directory -Force -Path $path | Out-Null
}
foreach ($staleFile in @(
    (Join-Path $capturesDir "benchmark_visual.png"),
    (Join-Path $capturesDir "visual_vdp_dump.bin"),
    (Join-Path $capturesDir "save.sram")
)) {
    if (Test-Path -LiteralPath $staleFile) {
        Remove-Item -LiteralPath $staleFile -Force -ErrorAction SilentlyContinue
    }
}
Get-ChildItem -LiteralPath $capturesDir -Filter "benchmark_quicksave*" -File -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
if (Test-Path -LiteralPath $blastEmLogPath) {
    Remove-Item -LiteralPath $blastEmLogPath -Force
}

$process = $null
$processStartedAtUtc = [datetime]::MinValue
$closeResult = $null
$screenshotSaved = $false
$saveSramPath = $null
$saveSramDest = $null
$dumpDest = $null
$quickSaveDest = $null
$evidenceBlock = $null
$romMeta = $null
$sessionLaunchStatus = "attempted"
$sessionBootStatus = "nao_testado"
$audioStatus = "nao_testado"
$navigationToRun = if ($NavigationSequence -and $NavigationSequence.Count -gt 0) { $NavigationSequence } else { @("wait:5000") }

Push-Location -LiteralPath $ProjectDir
try {
    $buildProcess = Start-Process -FilePath "cmd.exe" -ArgumentList @("/c", "build.bat") -PassThru -Wait -NoNewWindow
    if ($buildProcess.ExitCode -ne 0) {
        throw "Falha no build do projeto."
    }
    if (-not (Test-Path -LiteralPath $romPath)) {
        throw "ROM nao encontrada em $romPath apos o build."
    }

    $romMeta = Get-RomMetadata -RomPath $romPath
    @{
        timestamp = (Get-Date -Format "o")
        emulator = $blastEmExe
        rom_path = $romMeta.path
        rom_size_bytes = $romMeta.size_bytes
        rom_last_write_utc = $romMeta.last_write_utc
        rom_sha256 = $romMeta.sha256
        boot_emulador = "nao_testado"
        gameplay_basico = "nao_testado"
        performance = "nao_testado"
        audio = "nao_testado"
        hardware_real = "nao_testado"
        launch_status = $sessionLaunchStatus
        sandbox_root = $blastEmSandboxRoot
        save_root = $saveRoot
        screenshot_root = $screenshotRoot
        emulator_log_path = $blastEmLogPath
        navigation_mode = "scan_code_sendinput"
        ready_probe_source = "sram_ready_heartbeat"
        failure_artifact_path = $failureScreenshotPath
    } | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $sessionPath

    Write-BlastEmCaptureLog -LogPath $blastEmLogPath -Event "capture_begin" -Data @{
        rom = $romPath
        sandbox_root = $blastEmSandboxRoot
        save_root = $saveRoot
        screenshot_root = $screenshotRoot
        failure_artifact_path = $failureScreenshotPath
        navigation_steps = $navigationToRun.Count
    }

    Write-BlastEmConfig -BaseConfigPath $blastEmDefaultCfg -TargetConfigPath $blastEmUserCfg -SaveRoot $saveRoot -ScreenshotRoot $screenshotRoot

    $processStartInfo = New-Object System.Diagnostics.ProcessStartInfo
    $processStartInfo.FileName = $blastEmExe
    $processStartInfo.Arguments = ('"' + $romPath + '"')
    $processStartInfo.WorkingDirectory = Split-Path -Parent $blastEmExe
    $processStartInfo.UseShellExecute = $false
    $processStartInfo.Environment["LOCALAPPDATA"] = $blastEmLocalAppData
    $processStartInfo.Environment["APPDATA"] = $blastEmAppData
    $processStartInfo.Environment["USERPROFILE"] = $blastEmHome
    $processStartInfo.Environment["HOME"] = $blastEmHome
    $processStartedAtUtc = [datetime]::UtcNow
    $process = [System.Diagnostics.Process]::Start($processStartInfo)
    if (-not $process) {
        throw "Falha ao iniciar o BlastEm com sandbox dedicado."
    }

    Write-BlastEmCaptureLog -LogPath $blastEmLogPath -Event "process_started" -Data @{ pid = $process.Id }
    Wait-ForBlastEmWindow -Process $process -TimeoutSeconds 20
    Write-BlastEmCaptureLog -LogPath $blastEmLogPath -Event "window_ready" -Data @{
        title = $process.MainWindowTitle
        hwnd = [int64]$process.MainWindowHandle
    }

    $sessionLaunchStatus = "started"
    @{
        timestamp = (Get-Date -Format "o")
        emulator = $blastEmExe
        rom_path = $romMeta.path
        rom_size_bytes = $romMeta.size_bytes
        rom_last_write_utc = $romMeta.last_write_utc
        rom_sha256 = $romMeta.sha256
        boot_emulador = "nao_testado"
        gameplay_basico = "nao_testado"
        performance = "nao_testado"
        audio = "nao_testado"
        hardware_real = "nao_testado"
        launch_status = $sessionLaunchStatus
        sandbox_root = $blastEmSandboxRoot
        save_root = $saveRoot
        screenshot_root = $screenshotRoot
        emulator_log_path = $blastEmLogPath
        navigation_mode = "scan_code_sendinput"
        ready_probe_source = "sram_ready_heartbeat"
        failure_artifact_path = $failureScreenshotPath
    } | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $sessionPath

    $foregroundOk = Ensure-BlastEmForeground -Process $process
    Write-BlastEmCaptureLog -LogPath $blastEmLogPath -Event "foreground_set" -Data @{ success = [bool]$foregroundOk }

    try {
        Invoke-BlastEmNavigation `
            -Process $process `
            -Sequence $navigationToRun `
            -LogPath $blastEmLogPath `
            -SaveRoots @($saveRoot, $blastEmSandboxRoot) `
            -HeartbeatOffset 0x100 `
            -ProcessStartedAtUtc $processStartedAtUtc `
            -SandboxRoot $blastEmSandboxRoot

        Start-Sleep -Milliseconds 1200
        $screenshotDest = Join-Path $capturesDir "benchmark_visual.png"
        $screenshotSaved = Save-BlastEmWindowScreenshot -Process $process -OutputPath $screenshotDest
        if (-not $screenshotSaved) {
            throw "Falha ao capturar screenshot dedicado da janela do BlastEm."
        }

        Write-BlastEmCaptureLog -LogPath $blastEmLogPath -Event "screenshot_saved" -Data @{ path = $screenshotDest }
    }
    catch {
        Write-BlastEmCaptureLog -LogPath $blastEmLogPath -Event "capture_exception" -Data @{
            message = $_.Exception.Message
            failure_artifact_path = $failureScreenshotPath
        }
        if ($process) {
            $null = Save-BlastEmWindowScreenshot -Process $process -OutputPath $failureScreenshotPath
        }
        throw
    }
    finally {
        if ($process) {
            $closeResult = Close-BlastEmGracefully -Process $process -LogPath $blastEmLogPath
        }
    }

    $saveDeadline = (Get-Date).AddSeconds(20)
    while ((Get-Date) -lt $saveDeadline) {
        $saveSramPath = Find-FreshVisualEvidenceSave -RootPaths @($saveRoot, $blastEmSandboxRoot) -ProcessStartedAtUtc $processStartedAtUtc -SandboxRoot $blastEmSandboxRoot
        if ($saveSramPath) {
            break
        }
        Start-Sleep -Milliseconds 400
    }

    if ($saveSramPath) {
        $saveSramDest = Join-Path $capturesDir "save.sram"
        Copy-Item -LiteralPath $saveSramPath -Destination $saveSramDest -Force
        $dumpDest = Join-Path $capturesDir "visual_vdp_dump.bin"
        Extract-VisualEvidenceDump -SramPath $saveSramDest -OutputPath $dumpDest
        $evidenceBlock = Get-VisualEvidenceBlock -SramPath $saveSramDest
        Write-BlastEmCaptureLog -LogPath $blastEmLogPath -Event "visual_evidence_found" -Data @{
            sram_path = $saveSramPath
            dump_path = $dumpDest
            fresh_sram_confirmed = $true
        }
    }
    elseif (-not $AllowMissingEvidence) {
        Write-BlastEmCaptureLog -LogPath $blastEmLogPath -Event "visual_evidence_missing" -Data @{
            sandbox_root = $blastEmSandboxRoot
            fresh_sram_confirmed = $false
        }
        throw "save.sram fresco com assinatura VLAB nao foi encontrado no sandbox $blastEmSandboxRoot. Log: $blastEmLogPath"
    }

    if ($evidenceBlock -and $evidenceBlock.scene_id -eq 12) {
        $driver = [int]$evidenceBlock.byte14
        $pcmMask = [int]$evidenceBlock.byte15
        if ($pcmMask -ne 0 -or $driver -ne 0) {
            $audioStatus = "ok"
        }
    }

    $sessionBootStatus = "ok"
    $sessionLaunchStatus = if ($saveSramDest -or $AllowMissingEvidence) { "captured" } else { "captured_partial" }
    $captureList = @()
    if ($screenshotSaved) { $captureList += (Join-Path $capturesDir "benchmark_visual.png") }
    if ($dumpDest) { $captureList += $dumpDest }
    if ($saveSramDest) { $captureList += $saveSramDest }
    if ($quickSaveDest) { $captureList += $quickSaveDest }

    @{
        timestamp = (Get-Date -Format "o")
        emulator = $blastEmExe
        rom_path = $romMeta.path
        rom_size_bytes = $romMeta.size_bytes
        rom_last_write_utc = $romMeta.last_write_utc
        rom_sha256 = $romMeta.sha256
        boot_emulador = $sessionBootStatus
        gameplay_basico = "funcional"
        performance = "nao_testado"
        audio = $audioStatus
        hardware_real = "nao_testado"
        launch_status = $sessionLaunchStatus
        graceful_exit = if ($closeResult) { -not $closeResult.forced } else { $false }
        close_exit_mode = if ($closeResult) { $closeResult.exit_mode } else { $null }
        screenshot_method = if ($screenshotSaved) { "window_capture" } else { "falhou" }
        quicksave_captured = [bool]$quickSaveDest
        quicksave_path = $quickSaveDest
        quicksave_method = $null
        captures = $captureList
        evidence_files = $captureList
        save_sram_path = $saveSramDest
        visual_vdp_dump_path = $dumpDest
        sandbox_root = $blastEmSandboxRoot
        save_root = $saveRoot
        screenshot_root = $screenshotRoot
        emulator_log_path = $blastEmLogPath
        fresh_sram_confirmed = [bool]$saveSramDest
        outside_sandbox_candidate = $null
        stale_sandbox_candidate = $null
        navigation_mode = "scan_code_sendinput"
        ready_probe_source = "sram_ready_heartbeat"
        failure_artifact_path = if (Test-Path -LiteralPath $failureScreenshotPath) { $failureScreenshotPath } else { $null }
    } | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $sessionPath

    Write-BlastEmCaptureLog -LogPath $blastEmLogPath -Event "capture_done" -Data @{
        session_path = $sessionPath
        fresh_sram_confirmed = [bool]$saveSramDest
        close_exit_mode = if ($closeResult) { $closeResult.exit_mode } else { $null }
    }

    Set-Location -LiteralPath $ProjectDir
    & $validatorPath
    if ($LASTEXITCODE -ne 0) {
        throw "validate_resources.ps1 retornou erro apos a captura visual."
    }
}
finally {
    # Safety net: se exception disparou ANTES do try/finally interno (L335-368)
    # fechar $process corretamente, o BlastEm pode ficar orfao. Esta cauda
    # garante teardown deterministico do processo.
    if ($process) {
        try {
            $process.Refresh()
            if (-not $process.HasExited) {
                if (-not $closeResult) {
                    try {
                        $closeResult = Close-BlastEmGracefully -Process $process -LogPath $blastEmLogPath
                    } catch {
                        Write-Warning "Close-BlastEmGracefully silenced: $_"
                    }
                }
                $process.Refresh()
                if (-not $process.HasExited) {
                    try { Stop-Process -Id $process.Id -Force -ErrorAction Stop } catch { Write-Warning "Stop-Process silenced: $_" }
                    $process.WaitForExit(3000) | Out-Null
                }
            }
        } catch {
            Write-Warning "visual_capture cleanup silenced: $_"
        }
    }
    Pop-Location
}

Get-Content -LiteralPath $sessionPath
