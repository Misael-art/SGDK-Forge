[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$ProjectDir = "",

    [Parameter(Mandatory = $false)]
    [string[]]$NavigationSequence = @()
)

$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

public static class CodexWindowCapture
{
    [StructLayout(LayoutKind.Sequential)]
    public struct RECT
    {
        public int Left;
        public int Top;
        public int Right;
        public int Bottom;
    }

    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);

    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern bool BringWindowToTop(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

    [DllImport("user32.dll")]
    public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdcBlt, uint nFlags);

    [DllImport("user32.dll")]
    public static extern bool PostMessage(IntPtr hWnd, uint msg, IntPtr wParam, IntPtr lParam);

    [DllImport("user32.dll")]
    public static extern uint MapVirtualKey(uint uCode, uint uMapType);
}
"@

function Resolve-ProjectRoot {
    param([string]$InputPath)

    if ([string]::IsNullOrWhiteSpace($InputPath)) {
        return (Get-Location).Path
    }

    return (Resolve-Path -LiteralPath $InputPath).Path
}

function Get-RomMetadata {
    param([Parameter(Mandatory = $true)][string]$RomPath)

    $rom = Get-Item -LiteralPath $RomPath
    $stream = [System.IO.File]::OpenRead($RomPath)
    try {
        $sha256 = [System.Security.Cryptography.SHA256]::Create()
        try {
            $hash = ([System.BitConverter]::ToString($sha256.ComputeHash($stream)).Replace("-", "")).ToLowerInvariant()
        } finally {
            $sha256.Dispose()
        }
    } finally {
        $stream.Dispose()
    }

    return [ordered]@{
        path = $RomPath
        size_bytes = $rom.Length
        last_write_utc = $rom.LastWriteTimeUtc.ToString("o")
        sha256 = $hash
    }
}

function Wait-ForMainWindow {
    param(
        [Parameter(Mandatory = $true)]
        [System.Diagnostics.Process]$Process,
        [int]$TimeoutSeconds = 20
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        $Process.Refresh()
        if ($Process.HasExited) {
            throw "BlastEm encerrou antes de abrir a janela principal."
        }
        if ($Process.MainWindowHandle -ne 0) {
            return
        }
        Start-Sleep -Milliseconds 250
    }

    throw "BlastEm nao expôs MainWindowHandle dentro do timeout."
}

function Write-BlastEmConfig {
    param(
        [Parameter(Mandatory = $true)][string]$BaseConfigPath,
        [Parameter(Mandatory = $true)][string]$TargetConfigPath,
        [Parameter(Mandatory = $true)][string]$ScreenshotRoot,
        [Parameter(Mandatory = $true)][string]$SaveRoot
    )

    $content = Get-Content -LiteralPath $BaseConfigPath -Raw
    $normalizedShot = $ScreenshotRoot.Replace("\", "/")
    $normalizedSave = $SaveRoot.Replace("\", "/")

    $content = [System.Text.RegularExpressions.Regex]::Replace($content, '(?m)^\s*screenshot_path\s+.*$', "`tscreenshot_path $normalizedShot")
    $content = [System.Text.RegularExpressions.Regex]::Replace($content, '(?m)^\s*save_path\s+.*$', "`tsave_path $normalizedSave/`$ROMNAME")
    $content = [System.Text.RegularExpressions.Regex]::Replace($content, '(?m)^\s*f11\s+.*$', "")
    $content = [System.Text.RegularExpressions.Regex]::Replace($content, '(?m)^\s*f12\s+.*$', "")
    $content = [System.Text.RegularExpressions.Regex]::Replace(
        $content,
        '(?m)^(\s*keys\s*\{\s*)$',
        "`$1`r`n`t`t f11 ui.screenshot`r`n`t`t f12 ui.save_state"
    )
    $configDir = Split-Path -Parent $TargetConfigPath
    New-Item -ItemType Directory -Force -Path $configDir | Out-Null
    Set-Content -LiteralPath $TargetConfigPath -Value $content -Encoding UTF8
}

function Get-AutoHotkeyExecutableOrNull {
    foreach ($candidate in @(
        "C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe",
        "C:\Program Files\AutoHotkey\v2\AutoHotkey.exe",
        "C:\Program Files\AutoHotkey\AutoHotkey.exe",
        "C:\Program Files (x86)\AutoHotkey\AutoHotkey.exe"
    )) {
        if (Test-Path -LiteralPath $candidate) {
            return $candidate
        }
    }

    $command = Get-Command AutoHotkey, AutoHotkey64 -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($command) {
        return $command.Source
    }

    return $null
}

function Get-AutoItExecutableOrNull {
    foreach ($candidate in @(
        "C:\Program Files\AutoIt3\AutoIt3.exe",
        "C:\Program Files (x86)\AutoIt3\AutoIt3.exe"
    )) {
        if (Test-Path -LiteralPath $candidate) {
            return $candidate
        }
    }

    $command = Get-Command AutoIt3 -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($command) {
        return $command.Source
    }

    return $null
}

function Invoke-BlastEmHotkey {
    param(
        [Parameter(Mandatory = $true)][System.Diagnostics.Process]$Process,
        [Parameter(Mandatory = $true)][ValidateSet("screenshot", "quicksave", "quit")][string]$Action
    )

    $helperScript = Join-Path $PSScriptRoot "invoke_blastem_hotkey.ps1"
    $ahkScript = Join-Path $PSScriptRoot "blastem_hotkey_fallback.ahk"
    $autoItScript = Join-Path $PSScriptRoot "blastem_hotkey_fallback.au3"

    if (Test-Path -LiteralPath $helperScript) {
        try {
            & $helperScript -ProcessId $Process.Id -Action $Action | Out-Null
            return "native-postmessage"
        }
        catch {
        }
    }

    $autoHotkey = Get-AutoHotkeyExecutableOrNull
    if ($autoHotkey -and (Test-Path -LiteralPath $ahkScript)) {
        try {
            $ahkProcess = Start-Process -FilePath $autoHotkey -ArgumentList @($ahkScript, [string]$Process.Id, $Action) -PassThru -Wait -NoNewWindow
            if ($ahkProcess.ExitCode -eq 0) {
                return "autohotkey"
            }
        }
        catch {
        }
    }

    $autoIt = Get-AutoItExecutableOrNull
    if ($autoIt -and (Test-Path -LiteralPath $autoItScript)) {
        try {
            $autoItProcess = Start-Process -FilePath $autoIt -ArgumentList @($autoItScript, [string]$Process.Id, $Action) -PassThru -Wait -NoNewWindow
            if ($autoItProcess.ExitCode -eq 0) {
                return "autoit"
            }
        }
        catch {
        }
    }

    return $null
}

function Capture-WindowScreenshot {
    param(
        [Parameter(Mandatory = $true)][System.Diagnostics.Process]$Process,
        [Parameter(Mandatory = $true)][string]$OutputPath
    )

    $Process.Refresh()
    if ($Process.MainWindowHandle -eq 0) {
        throw "BlastEm nao expôs uma janela capturavel para screenshot dedicado."
    }

    $rect = New-Object CodexWindowCapture+RECT
    if (-not [CodexWindowCapture]::GetWindowRect($Process.MainWindowHandle, [ref]$rect)) {
        throw "Falha ao obter o retangulo da janela do BlastEm."
    }

    $width = $rect.Right - $rect.Left
    $height = $rect.Bottom - $rect.Top
    if ($width -le 0 -or $height -le 0) {
        throw "Janela do BlastEm retornou dimensoes invalidas para captura."
    }

    $bitmap = New-Object System.Drawing.Bitmap $width, $height
    try {
        $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
        try {
            $hdc = $graphics.GetHdc()
            try {
                $printed = [CodexWindowCapture]::PrintWindow($Process.MainWindowHandle, $hdc, 0)
            }
            finally {
                $graphics.ReleaseHdc($hdc)
            }

            if (-not $printed) {
                $graphics.CopyFromScreen($rect.Left, $rect.Top, 0, 0, $bitmap.Size)
            }
        } finally {
            $graphics.Dispose()
        }

        $parent = Split-Path -Parent $OutputPath
        New-Item -ItemType Directory -Force -Path $parent | Out-Null
        $bitmap.Save($OutputPath, [System.Drawing.Imaging.ImageFormat]::Png)
    } finally {
        $bitmap.Dispose()
    }
}

function Focus-ProcessWindow {
    param(
        [Parameter(Mandatory = $true)][System.Diagnostics.Process]$Process
    )

    $Process.Refresh()
    if ($Process.MainWindowHandle -eq 0) {
        throw "BlastEm nao expôs uma janela focavel."
    }

    [CodexWindowCapture]::ShowWindow($Process.MainWindowHandle, 9) | Out-Null
    [CodexWindowCapture]::BringWindowToTop($Process.MainWindowHandle) | Out-Null
    [CodexWindowCapture]::SetForegroundWindow($Process.MainWindowHandle) | Out-Null
    Start-Sleep -Milliseconds 800
}

function Invoke-BlastEmVirtualKey {
    param(
        [Parameter(Mandatory = $true)][System.Diagnostics.Process]$Process,
        [Parameter(Mandatory = $true)][UInt32]$VirtualKey,
        [Parameter(Mandatory = $false)][int]$HoldMilliseconds = 180
    )

    $Process.Refresh()
    if ($Process.MainWindowHandle -eq 0) {
        throw "BlastEm nao expôs uma janela para navegacao automatica."
    }

    $scanCode = [CodexWindowCapture]::MapVirtualKey($VirtualKey, 0)
    $wmKeyDown = 0x100
    $wmKeyUp = 0x101
    $downLParam = 1 -bor ($scanCode -shl 16)
    $upLParam = 1 -bor ($scanCode -shl 16) -bor 0xC0000000

    [CodexWindowCapture]::PostMessage($Process.MainWindowHandle, $wmKeyDown, [intptr]$VirtualKey, [intptr]$downLParam) | Out-Null
    Start-Sleep -Milliseconds $HoldMilliseconds
    [CodexWindowCapture]::PostMessage($Process.MainWindowHandle, $wmKeyUp, [intptr]$VirtualKey, [intptr]$upLParam) | Out-Null
}

function Invoke-BlastEmNavigation {
    param(
        [Parameter(Mandatory = $true)][System.Diagnostics.Process]$Process,
        [Parameter(Mandatory = $true)][string[]]$Sequence
    )

    if (-not $Sequence -or $Sequence.Count -eq 0) {
        Start-Sleep -Seconds 5
        return
    }

    $virtualKeys = @{
        "up" = 0x26
        "down" = 0x28
        "left" = 0x25
        "right" = 0x27
        "a" = 0x41
        "b" = 0x53
        "c" = 0x44
        "start" = 0x0D
    }
    $sendKeys = @{
        "up" = "{UP}"
        "down" = "{DOWN}"
        "left" = "{LEFT}"
        "right" = "{RIGHT}"
        "a" = "a"
        "b" = "s"
        "c" = "d"
        "start" = "{ENTER}"
    }

    foreach ($rawStep in $Sequence) {
        $step = $rawStep.Trim().ToLowerInvariant()
        if ([string]::IsNullOrWhiteSpace($step)) {
            continue
        }

        if ($step.StartsWith("wait:")) {
            $milliseconds = 0
            if (-not [int]::TryParse($step.Substring(5), [ref]$milliseconds) -or $milliseconds -lt 0) {
                throw "Passo de navegacao invalido: $rawStep"
            }
            Start-Sleep -Milliseconds $milliseconds
            continue
        }

        if (-not $virtualKeys.ContainsKey($step)) {
            throw "Tecla de navegacao nao suportada: $rawStep"
        }

        Invoke-BlastEmVirtualKey -Process $Process -VirtualKey $virtualKeys[$step]
        Focus-ProcessWindow -Process $Process
        [System.Windows.Forms.SendKeys]::SendWait($sendKeys[$step])
        Start-Sleep -Milliseconds 220
    }
}

function Get-NewestFileOrNull {
    param(
        [Parameter(Mandatory = $true)][string]$RootPath,
        [Parameter(Mandatory = $true)][scriptblock]$Filter
    )

    if (-not (Test-Path -LiteralPath $RootPath)) {
        return $null
    }

    $files = Get-ChildItem -LiteralPath $RootPath -Recurse -File -ErrorAction SilentlyContinue | Where-Object $Filter
    if (-not $files) {
        return $null
    }

    return $files | Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
}

function Get-SaveEvidenceFileOrNull {
    param(
        [Parameter(Mandatory = $true)][string]$RootPath
    )

    return Get-NewestFileOrNull -RootPath $RootPath -Filter {
        $_.Length -gt 0 -and (
            $_.Name -ieq "save.sram" -or
            $_.Extension -ieq ".sram" -or
            $_.Extension -ieq ".srm" -or
            $_.Extension -ieq ".sav"
        )
    }
}

function Test-VisualEvidenceSignature {
    param(
        [Parameter(Mandatory = $true)][string]$SramPath
    )

    if (-not (Test-Path -LiteralPath $SramPath)) {
        return $false
    }

    $bytes = [System.IO.File]::ReadAllBytes($SramPath)
    if ($bytes.Length -lt 8) {
        return $false
    }

    return ([System.Text.Encoding]::ASCII.GetString($bytes, 0, 4) -eq "VLAB")
}

function Wait-ForVisualEvidenceSave {
    param(
        [Parameter(Mandatory = $true)][string[]]$RootPaths,
        [int]$TimeoutSeconds = 12
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        foreach ($rootPath in $RootPaths) {
            $candidate = Get-SaveEvidenceFileOrNull -RootPath $rootPath
            if ($candidate -and (Test-VisualEvidenceSignature -SramPath $candidate.FullName)) {
                return $candidate
            }
        }

        Start-Sleep -Milliseconds 300
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


$ProjectDir = Resolve-ProjectRoot -InputPath $ProjectDir
$projectBuild = Join-Path $ProjectDir "build.bat"
$romPath = Join-Path $ProjectDir "out\rom.bin"
$capturesDir = Join-Path $ProjectDir "out\captures"
$logsDir = Join-Path $ProjectDir "out\logs"
$sessionPath = Join-Path $logsDir "emulator_session.json"
$validatorPath = Join-Path $PSScriptRoot "validate_resources.ps1"
$workspaceRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")
$blastEmExe = Join-Path $workspaceRoot "tools\emuladores\Blastem\blastem.exe"
$blastEmDefaultCfg = Join-Path $workspaceRoot "tools\emuladores\Blastem\default.cfg"
$blastEmSandboxRoot = Join-Path $ProjectDir "out\blastem_env"
$blastEmLocalAppData = Join-Path $blastEmSandboxRoot "LocalAppData"
$blastEmAppData = Join-Path $blastEmSandboxRoot "AppData"
$blastEmHome = Join-Path $blastEmSandboxRoot "Home"
$blastEmRuntimeConfigRoot = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::LocalApplicationData)
$blastEmRuntimeUserDir = Join-Path $blastEmRuntimeConfigRoot "blastem"
$blastEmUserDir = Join-Path $blastEmLocalAppData "blastem"
$blastEmUserCfg = Join-Path $blastEmUserDir "blastem.cfg"
$blastEmGlobalSaveRoot = Join-Path $blastEmRuntimeUserDir "rom"
$configBackup = $null
$tempCaptureRoot = Join-Path $capturesDir "_blastem_staging"

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
New-Item -ItemType Directory -Force -Path $blastEmLocalAppData | Out-Null
New-Item -ItemType Directory -Force -Path $blastEmAppData | Out-Null
New-Item -ItemType Directory -Force -Path $blastEmHome | Out-Null
if (Test-Path -LiteralPath $tempCaptureRoot) {
    Remove-Item -LiteralPath $tempCaptureRoot -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $tempCaptureRoot | Out-Null
foreach ($staleFile in @(
    (Join-Path $capturesDir "benchmark_visual.png"),
    (Join-Path $capturesDir "visual_vdp_dump.bin"),
    (Join-Path $capturesDir "save.sram"),
    (Join-Path $blastEmSandboxRoot "Home\AppData\Local\blastem\rom\save.sram"),
    (Join-Path $tempCaptureRoot "save.sram")
)) {
    if (Test-Path -LiteralPath $staleFile) {
        Remove-Item -LiteralPath $staleFile -Force -ErrorAction SilentlyContinue
    }
}

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
        launch_status = "attempted"
    } | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $sessionPath

    if (Test-Path -LiteralPath $blastEmUserCfg) {
        $configBackup = Get-Content -LiteralPath $blastEmUserCfg -Raw
    }

    Write-BlastEmConfig `
        -BaseConfigPath $blastEmDefaultCfg `
        -TargetConfigPath $blastEmUserCfg `
        -ScreenshotRoot $tempCaptureRoot `
        -SaveRoot $tempCaptureRoot

    $quotedRomPath = '"' + $romPath + '"'
    $processStartInfo = New-Object System.Diagnostics.ProcessStartInfo
    $processStartInfo.FileName = $blastEmExe
    $processStartInfo.Arguments = $quotedRomPath
    $processStartInfo.WorkingDirectory = Split-Path -Parent $blastEmExe
    $processStartInfo.UseShellExecute = $false
    $processStartInfo.Environment["LOCALAPPDATA"] = $blastEmLocalAppData
    $processStartInfo.Environment["APPDATA"] = $blastEmAppData
    $processStartInfo.Environment["USERPROFILE"] = $blastEmHome
    $processStartInfo.Environment["HOME"] = $blastEmHome
    $process = [System.Diagnostics.Process]::Start($processStartInfo)
    if (-not $process) {
        throw "Falha ao iniciar o BlastEm com sandbox de captura dedicado."
    }
    Wait-ForMainWindow -Process $process -TimeoutSeconds 20

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
        launch_status = "started"
    } | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $sessionPath

    $screenshotDest = Join-Path $capturesDir "benchmark_visual.png"
    Focus-ProcessWindow -Process $process
    Invoke-BlastEmNavigation -Process $process -Sequence $NavigationSequence
    Start-Sleep -Milliseconds 1200
    Capture-WindowScreenshot -Process $process -OutputPath $screenshotDest
    $screenshotMethod = "window-focused"
    $nativeScreenshotMethod = $null
    $quickSaveMethod = $null

    $gracefulExit = $false
    $quitMethod = $null
    if ($process.CloseMainWindow()) {
        if ($process.WaitForExit(10000)) {
            $gracefulExit = $true
        } else {
            Start-Sleep -Seconds 2
            if ($process.CloseMainWindow() -and $process.WaitForExit(8000)) {
                $gracefulExit = $true
            }
        }
    }

    if (-not $gracefulExit) {
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        $process.WaitForExit()
    }

    Start-Sleep -Seconds 2

    $saveSram = Wait-ForVisualEvidenceSave -RootPaths @($tempCaptureRoot, $blastEmSandboxRoot) -TimeoutSeconds 8

    $quickSave = Get-NewestFileOrNull -RootPath $tempCaptureRoot -Filter {
        $_.Name -ne "save.sram" -and
        $_.Extension -ine ".png" -and
        $_.Extension -ine ".cfg" -and
        $_.Extension -ine ".sram" -and
        $_.Extension -ine ".sav"
    }
    if (-not $quickSave) {
        $quickSave = Get-NewestFileOrNull -RootPath $blastEmSandboxRoot -Filter {
            $_.Name -ne "save.sram" -and
            $_.Extension -ine ".png" -and
            $_.Extension -ine ".cfg" -and
            $_.Extension -ine ".sram" -and
            $_.Extension -ine ".sav"
        }
    }

    if (-not $saveSram) {
        throw "save.sram nao foi encontrado; o dump visual nao pode ser extraido."
    }

    $quickSaveDest = $null
    $saveSramDest = Join-Path $capturesDir "save.sram"
    $dumpDest = Join-Path $capturesDir "visual_vdp_dump.bin"

    if ($quickSave) {
        $quickSaveDest = Join-Path $capturesDir ("benchmark_quicksave" + $quickSave.Extension)
        Copy-Item -LiteralPath $quickSave.FullName -Destination $quickSaveDest -Force
    }
    Copy-Item -LiteralPath $saveSram.FullName -Destination $saveSramDest -Force
    Extract-VisualEvidenceDump -SramPath $saveSramDest -OutputPath $dumpDest

    $captureList = @(
        $screenshotDest,
        $dumpDest,
        $saveSramDest
    )
    if ($quickSaveDest) {
        $captureList += $quickSaveDest
    }

    @{
        timestamp = (Get-Date -Format "o")
        emulator = $blastEmExe
        rom_path = $romMeta.path
        rom_size_bytes = $romMeta.size_bytes
        rom_last_write_utc = $romMeta.last_write_utc
        rom_sha256 = $romMeta.sha256
        boot_emulador = "ok"
        gameplay_basico = "funcional"
        performance = "nao_testado"
        audio = "nao_testado"
        hardware_real = "nao_testado"
        launch_status = "captured"
        graceful_exit = $gracefulExit
        screenshot_method = $screenshotMethod
        quicksave_captured = [bool]$quickSaveDest
        quicksave_path = $quickSaveDest
        quicksave_method = $quickSaveMethod
        captures = $captureList
        evidence_files = @(
            $screenshotDest,
            $dumpDest,
            $saveSramDest
        )
    } | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $sessionPath

    Set-Location -LiteralPath $ProjectDir
    & $validatorPath
    if ($LASTEXITCODE -ne 0) {
        throw "validate_resources.ps1 retornou erro apos a captura visual."
    }
}
finally {
    if ($configBackup -ne $null) {
        Set-Content -LiteralPath $blastEmUserCfg -Value $configBackup -Encoding UTF8
    }
    elseif (Test-Path -LiteralPath $blastEmUserCfg) {
        Remove-Item -LiteralPath $blastEmUserCfg -Force
    }

    if (Test-Path -LiteralPath $tempCaptureRoot) {
        Remove-Item -LiteralPath $tempCaptureRoot -Recurse -Force
    }

    Pop-Location
}

Get-Content -LiteralPath $sessionPath
