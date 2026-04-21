[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$ProjectDir = "",
    [Parameter(Mandatory = $false)]
    [string]$RomPath = "",
    [Parameter(Mandatory = $false)]
    [string]$OutputPath = "",
    [Parameter(Mandatory = $false)]
    [int]$FrameWindow = 1800,
    [Parameter(Mandatory = $false)]
    [int]$TargetScene = 2,
    [Parameter(Mandatory = $false)]
    [int]$TimeoutSeconds = 0,
    [Parameter(Mandatory = $false)]
    [ValidateSet("auto", "bizhawk", "blastem")]
    [string]$Emulator = "auto",
    [Parameter(Mandatory = $false)]
    [string[]]$BlastEmNavigation = @(
        "wait:3500",
        "region_unlock",
        "press_until_ready:start,timeout_ms=9000,interval_ms=450,hold=80,max_presses=18",
        "wait:1200",
        "mash:a,count=3,interval=400"
    )
)

$ErrorActionPreference = "Stop"

$BlastEmAutomationModule = Join-Path $PSScriptRoot "lib\blastem_automation.psm1"
Import-Module -Name $BlastEmAutomationModule -Force


function Resolve-ProbeAddress {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SymbolPath
    )

    $symbolLine = Get-Content -LiteralPath $SymbolPath | Where-Object { $_ -match '\bg_mdRuntimeProbe\b' } | Select-Object -First 1
    if (-not $symbolLine) {
        throw "Simbolo g_mdRuntimeProbe nao encontrado em $SymbolPath"
    }

    $tokens = $symbolLine -split '\s+'
    foreach ($token in $tokens) {
        if ($token -match '^[0-9A-Fa-f]{8}$') {
            $address = ([Convert]::ToUInt32($token, 16) -band 0xFFFFFF)
            if ($address -ge 0xFF0000 -and $address -le 0xFFFFFF) {
                return ($address - 0xFF0000)
            }
            return $address
        }
    }

    throw "Endereco do simbolo g_mdRuntimeProbe nao pode ser resolvido."
}

function Resolve-RomForCapture {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RomPath,
        [Parameter(Mandatory = $true)]
        [string]$LogDir
    )

    $resolvedRomPath = (Resolve-Path -LiteralPath $RomPath).Path
    $captureRomPath = Join-Path $LogDir "runtime_capture_rom.bin"
    [System.IO.File]::Copy($resolvedRomPath, $captureRomPath, $true)
    return $captureRomPath
}

function Test-WaterboxHost {
    param(
        [Parameter(Mandatory = $true)]
        [string]$DllPath
    )

    $nativeMethods = Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
namespace SGDK.Runtime {
    public static class Win32 {
        [DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
        public static extern IntPtr LoadLibrary(string lpFileName);

        [DllImport("kernel32.dll", SetLastError = true)]
        public static extern bool FreeLibrary(IntPtr hModule);
    }
}
"@ -PassThru

    $handle = $nativeMethods::LoadLibrary($DllPath)
    if ($handle -eq [IntPtr]::Zero) {
        return [Runtime.InteropServices.Marshal]::GetLastWin32Error()
    }

    [void]$nativeMethods::FreeLibrary($handle)
    return 0
}

function Test-VCRuntime140Present {
    $candidates = @(
        (Join-Path $env:SystemRoot "System32\vcruntime140.dll"),
        (Join-Path $env:SystemRoot "System32\vcruntime140_1.dll")
    )

    foreach ($candidate in $candidates) {
        if (-not (Test-Path -LiteralPath $candidate)) {
            return $false
        }
    }

    return $true
}

function Invoke-BlastEmRuntimeCapture {
    param(
        [Parameter(Mandatory = $true)][string]$ProjectDir,
        [Parameter(Mandatory = $true)][string]$RomPath,
        [Parameter(Mandatory = $true)][string]$OutputPath,
        [Parameter(Mandatory = $false)][int]$FrameWindow = 1800,
        [Parameter(Mandatory = $false)][int]$TimeoutSeconds = 45,
        [Parameter(Mandatory = $false)][string[]]$NavigationSequence = @(),
        [Parameter(Mandatory = $false)][int]$SramOffset = 0x200
    )

    Ensure-BlastEmAutomationLoaded

    $workspaceRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
    $blastEmRoot = Join-Path $workspaceRoot "tools\emuladores\BlastEm"
    $blastEmExe = Join-Path $blastEmRoot "blastem.exe"
    $blastEmDefaultCfg = Join-Path $blastEmRoot "default.cfg"
    if (-not (Test-Path -LiteralPath $blastEmExe)) {
        throw "blastem.exe nao encontrado em $blastEmExe"
    }
    if (-not (Test-Path -LiteralPath $blastEmDefaultCfg)) {
        throw "default.cfg do BlastEm nao encontrado em $blastEmDefaultCfg"
    }

    $logDir = Join-Path $ProjectDir "out\logs"
    if (-not (Test-Path -LiteralPath $logDir)) {
        New-Item -ItemType Directory -Force -Path $logDir | Out-Null
    }

    $sandboxRoot = Join-Path $ProjectDir "out\blastem_env_runtime"
    $sandboxHome = Join-Path $sandboxRoot "Home"
    $sandboxLocalAppData = Join-Path $sandboxHome "AppData\Local"
    $sandboxAppData = Join-Path $sandboxHome "AppData\Roaming"
    $sandboxUserDir = Join-Path $sandboxLocalAppData "blastem"
    $sandboxUserCfg = Join-Path $sandboxUserDir "blastem.cfg"
    $saveRoot = Join-Path $sandboxRoot "saves"
    $screenshotRoot = Join-Path $sandboxRoot "screenshots"
    $blastemLogPath = Join-Path $logDir "runtime_capture_blastem.log"
    $timestampSafe = (Get-Date).ToString("yyyyMMdd_HHmmss")
    $failureScreenshotPath = Join-Path $logDir ("blastem_failure_" + $timestampSafe + ".png")
    $globalSaveRoot = Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'blastem'

    if (Test-Path -LiteralPath $sandboxRoot) {
        Remove-Item -LiteralPath $sandboxRoot -Recurse -Force
    }
    foreach ($path in @($sandboxLocalAppData, $sandboxAppData, $sandboxHome, $sandboxUserDir, $saveRoot, $screenshotRoot)) {
        New-Item -ItemType Directory -Force -Path $path | Out-Null
    }
    if (Test-Path -LiteralPath $blastemLogPath) {
        Remove-Item -LiteralPath $blastemLogPath -Force
    }

    Write-BlastEmCaptureLog -LogPath $blastemLogPath -Event "capture_begin" -Data @{
        rom = $RomPath
        frame_window = $FrameWindow
        timeout_seconds = $TimeoutSeconds
        nav_steps = $NavigationSequence.Count
        navigation_mode = "scan_code_sendinput"
        ready_probe_source = "sram_ready_heartbeat"
        sram_offset = ("0x{0:X}" -f $SramOffset)
        heartbeat_offset = "0x100"
        sandbox_root = $sandboxRoot
        save_root = $saveRoot
        screenshot_root = $screenshotRoot
        failure_artifact_path = $failureScreenshotPath
    }

    $process = $null
    $processStartedAtUtc = [datetime]::MinValue
    $capturedEarly = $false
    $screenshotSaved = $false
    $closeResult = $null
    $runtimeSram = $null
    $freshSramConfirmed = $false
    $postCloseWaitSeconds = 12

    try {
        Write-BlastEmConfig -BaseConfigPath $blastEmDefaultCfg -TargetConfigPath $sandboxUserCfg -SaveRoot $saveRoot -ScreenshotRoot $screenshotRoot

        $processStartInfo = New-Object System.Diagnostics.ProcessStartInfo
        $processStartInfo.FileName = $blastEmExe
        $processStartInfo.Arguments = ('"' + $RomPath + '"')
        $processStartInfo.WorkingDirectory = Split-Path -Parent $blastEmExe
        $processStartInfo.UseShellExecute = $false
        $processStartInfo.Environment['LOCALAPPDATA'] = $sandboxLocalAppData
        $processStartInfo.Environment['APPDATA'] = $sandboxAppData
        $processStartInfo.Environment['USERPROFILE'] = $sandboxHome
        $processStartInfo.Environment['HOME'] = $sandboxHome
        $processStartedAtUtc = [datetime]::UtcNow
        $process = [System.Diagnostics.Process]::Start($processStartInfo)
        if (-not $process) {
            throw "Falha ao iniciar o BlastEm."
        }
        Write-BlastEmCaptureLog -LogPath $blastemLogPath -Event "process_started" -Data @{ pid = $process.Id }

        $windowDeadline = (Get-Date).AddSeconds(20)
        while ((Get-Date) -lt $windowDeadline) {
            $process.Refresh()
            if ($process.HasExited) {
                throw "BlastEm encerrou antes de expor a janela principal."
            }
            if ($process.MainWindowHandle -ne [IntPtr]::Zero) {
                break
            }
            Start-Sleep -Milliseconds 250
        }
        $process.Refresh()
        if ($process.MainWindowHandle -eq [IntPtr]::Zero) {
            throw "Janela principal do BlastEm nao apareceu em 20s."
        }

        Write-BlastEmCaptureLog -LogPath $blastemLogPath -Event "window_ready" -Data @{
            title = $process.MainWindowTitle
            hwnd = [int64]$process.MainWindowHandle
        }

        $foregroundOk = Ensure-BlastEmForeground -Process $process
        Write-BlastEmCaptureLog -LogPath $blastemLogPath -Event "foreground_set" -Data @{ success = [bool]$foregroundOk }

        Invoke-BlastEmNavigation `
            -Process $process `
            -Sequence $NavigationSequence `
            -LogPath $blastemLogPath `
            -SaveRoots @($saveRoot, $sandboxRoot) `
            -HeartbeatOffset 0x100 `
            -ProcessStartedAtUtc $processStartedAtUtc `
            -SandboxRoot $sandboxRoot

        $pollDeadline = (Get-Date).AddSeconds($TimeoutSeconds)
        $lastPollLog = Get-Date
        while ((Get-Date) -lt $pollDeadline) {
            $process.Refresh()
            if ($process.HasExited) {
                Write-BlastEmCaptureLog -LogPath $blastemLogPath -Event "process_exited_during_poll" -Data @{ exit_code = $process.ExitCode }
                break
            }

            $runtimeSram = Find-FirstSramWithSignature `
                -RootPaths @($saveRoot, $sandboxRoot) `
                -SramOffset $SramOffset `
                -ProcessStartedAtUtc $processStartedAtUtc `
                -SandboxRoot $sandboxRoot
            if ($runtimeSram) {
                $freshSramConfirmed = $true
                $capturedEarly = $true
                Write-BlastEmCaptureLog -LogPath $blastemLogPath -Event "sram_mdrt_detected" -Data @{
                    sram_path = $runtimeSram
                    fresh_sram_confirmed = $true
                }
                break
            }

            if (((Get-Date) - $lastPollLog).TotalSeconds -ge 5) {
                Write-BlastEmCaptureLog -LogPath $blastemLogPath -Event "poll_heartbeat" -Data @{
                    title = $process.MainWindowTitle
                    sandbox_root = $sandboxRoot
                    save_root_files = @(Get-ChildItem -LiteralPath $saveRoot -File -Recurse -ErrorAction SilentlyContinue | ForEach-Object { $_.Name })
                }
                $lastPollLog = Get-Date
            }

            Start-Sleep -Milliseconds 500
        }
    }
    catch {
        Write-BlastEmCaptureLog -LogPath $blastemLogPath -Event "capture_exception" -Data @{
            message = $_.Exception.Message
            failure_artifact_path = $failureScreenshotPath
        }
        if ($process) {
            $screenshotSaved = Save-BlastEmWindowScreenshot -Process $process -OutputPath $failureScreenshotPath
            if ($screenshotSaved) {
                Write-BlastEmCaptureLog -LogPath $blastemLogPath -Event "failure_screenshot" -Data @{ path = $failureScreenshotPath }
            }
        }
        throw
    }
    finally {
        if ($process) {
            $closeResult = Close-BlastEmGracefully -Process $process -LogPath $blastemLogPath
            Write-BlastEmCaptureLog -LogPath $blastemLogPath -Event "close_result" -Data @{
                close_exit_mode = $closeResult.exit_mode
                forced = [bool]$closeResult.forced
            }
        }
    }

    if (-not $runtimeSram) {
        $postCloseDeadline = (Get-Date).AddSeconds($postCloseWaitSeconds)
        while ((Get-Date) -lt $postCloseDeadline) {
            $runtimeSram = Find-FirstSramWithSignature `
                -RootPaths @($saveRoot, $sandboxRoot) `
                -SramOffset $SramOffset `
                -ProcessStartedAtUtc $processStartedAtUtc `
                -SandboxRoot $sandboxRoot
            if ($runtimeSram) {
                $freshSramConfirmed = $true
                break
            }
            Start-Sleep -Milliseconds 500
        }
    }

    if (-not $runtimeSram) {
        $outsideSandboxCandidate = $null
        if (Test-Path -LiteralPath $globalSaveRoot) {
            $outsideSandboxCandidate = Find-FirstSramWithSignature `
                -RootPaths @($globalSaveRoot) `
                -SramOffset $SramOffset `
                -ProcessStartedAtUtc $processStartedAtUtc
        }

        $staleSandboxCandidate = Find-FirstSramWithSignature `
            -RootPaths @($saveRoot, $sandboxRoot) `
            -SramOffset $SramOffset `
            -SandboxRoot $sandboxRoot

        $reason = 'missing_fresh_sram'
        if ($outsideSandboxCandidate) {
            $reason = 'outside_sandbox'
        }
        elseif ($staleSandboxCandidate) {
            $reason = 'stale_sram'
        }

        if ($process -and -not $screenshotSaved) {
            $screenshotSaved = Save-BlastEmWindowScreenshot -Process $process -OutputPath $failureScreenshotPath
        }

        Write-BlastEmCaptureLog -LogPath $blastemLogPath -Event "sram_not_found" -Data @{
            reason = $reason
            outside_sandbox_candidate = $outsideSandboxCandidate
            stale_sandbox_candidate = $staleSandboxCandidate
            sandbox_root = $sandboxRoot
            fresh_sram_confirmed = $false
            screenshot_path = if ($screenshotSaved) { $failureScreenshotPath } else { $null }
        }

        $diag = "save.sram com assinatura MDRT nao foi encontrado no sandbox fresco ($sandboxRoot). Motivo: $reason. Log: $blastemLogPath"
        if ($outsideSandboxCandidate) {
            $diag += "; candidato fora do sandbox: $outsideSandboxCandidate"
        }
        elseif ($staleSandboxCandidate) {
            $diag += "; candidato stale: $staleSandboxCandidate"
        }
        if ($screenshotSaved) {
            $diag += "; screenshot: $failureScreenshotPath"
        }
        throw $diag
    }

    Write-BlastEmCaptureLog -LogPath $blastemLogPath -Event "sram_resolved" -Data @{
        path = $runtimeSram
        captured_early = $capturedEarly
        fresh_sram_confirmed = $freshSramConfirmed
    }

    $parseScript = Join-Path $PSScriptRoot "parse_blastem_sram_runtime.ps1"
    if (-not (Test-Path -LiteralPath $parseScript)) {
        throw "Parser nao encontrado: $parseScript"
    }

    & $parseScript `
        -SramPath $runtimeSram `
        -OutputPath $OutputPath `
        -SramOffset $SramOffset `
        -FrameWindow $FrameWindow `
        -TimeoutFrame 0 `
        -PerceptualFluidez ([int]$env:SGDK_RT_PERCEPTUAL_FLUIDEZ) `
        -PerceptualLeitura ([int]$env:SGDK_RT_PERCEPTUAL_LEITURA) `
        -PerceptualNaturalidade ([int]$env:SGDK_RT_PERCEPTUAL_NATURALIDADE) `
        -PerceptualImpacto ([int]$env:SGDK_RT_PERCEPTUAL_IMPACTO) | Out-Null

    Write-BlastEmCaptureLog -LogPath $blastemLogPath -Event "capture_done" -Data @{
        output_path = $OutputPath
        close_exit_mode = if ($closeResult) { $closeResult.exit_mode } else { $null }
        fresh_sram_confirmed = $freshSramConfirmed
    }
}

if ([string]::IsNullOrWhiteSpace($ProjectDir)) {
    $ProjectDir = (Get-Location).Path
}

$ProjectDir = (Resolve-Path -LiteralPath $ProjectDir).Path
$LogDir = Join-Path $ProjectDir "out\logs"
if (-not (Test-Path -LiteralPath $LogDir)) {
    New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
}

if ([string]::IsNullOrWhiteSpace($RomPath)) {
    $romCandidates = @(
        (Join-Path $ProjectDir "out\rom.bin"),
        (Join-Path $ProjectDir "out\rom.out")
    )
    $RomPath = $romCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
}

if (-not $RomPath) {
    throw "ROM nao encontrada em out\rom.bin ou out\rom.out."
}

$RomPath = Resolve-RomForCapture -RomPath $RomPath -LogDir $LogDir

if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $OutputPath = Join-Path $LogDir "runtime_metrics.json"
}

$requestedEmulator = $Emulator
if ([string]::IsNullOrWhiteSpace($requestedEmulator) -or $requestedEmulator -eq "auto") {
    if ($env:SGDK_RUNTIME_EMULATOR) {
        $requestedEmulator = $env:SGDK_RUNTIME_EMULATOR
    }
}
$requestedEmulator = $requestedEmulator.Trim().ToLowerInvariant()
if ($requestedEmulator -notin @("auto", "bizhawk", "blastem")) {
    throw "Emulator invalido: $requestedEmulator"
}

$HeartbeatPath = Join-Path $LogDir "runtime_capture_heartbeat.txt"
$ErrorPath = Join-Path $LogDir "runtime_capture_error.txt"
$LauncherPath = Join-Path $LogDir "runtime_capture_launcher.lua"
$LegacyTempRomPath = Join-Path $LogDir "runtime_capture_rom.md"

$maxWaitFrames = [Math]::Max($FrameWindow + 600, 900)
if ($TimeoutSeconds -le 0) {
    $TimeoutSeconds = [int][Math]::Ceiling($maxWaitFrames / 60.0) + 20
}

$env:SGDK_RT_PERCEPTUAL_FLUIDEZ = if ($env:SGDK_PERCEPTUAL_FLUIDEZ) { $env:SGDK_PERCEPTUAL_FLUIDEZ } else { "0" }
$env:SGDK_RT_PERCEPTUAL_LEITURA = if ($env:SGDK_PERCEPTUAL_LEITURA) { $env:SGDK_PERCEPTUAL_LEITURA } else { "0" }
$env:SGDK_RT_PERCEPTUAL_NATURALIDADE = if ($env:SGDK_PERCEPTUAL_NATURALIDADE) { $env:SGDK_PERCEPTUAL_NATURALIDADE } else { "0" }
$env:SGDK_RT_PERCEPTUAL_IMPACTO = if ($env:SGDK_PERCEPTUAL_IMPACTO) { $env:SGDK_PERCEPTUAL_IMPACTO } else { "0" }

if ($requestedEmulator -eq "blastem") {
    Invoke-BlastEmRuntimeCapture `
        -ProjectDir $ProjectDir `
        -RomPath $RomPath `
        -OutputPath $OutputPath `
        -FrameWindow $FrameWindow `
        -TimeoutSeconds $TimeoutSeconds `
        -NavigationSequence $BlastEmNavigation
    if (Test-Path -LiteralPath $RomPath) {
        Remove-Item -LiteralPath $RomPath -Force
    }
    Get-Content -LiteralPath $OutputPath
    exit 0
}

$SymbolPath = Join-Path $ProjectDir "out\symbol.txt"
if (-not (Test-Path -LiteralPath $SymbolPath)) {
    throw "Arquivo de simbolos nao encontrado: $SymbolPath"
}

$bizHawkRoot = Join-Path $PSScriptRoot "..\emuladores\BizHawk"
$bizHawkRoot = (Resolve-Path -LiteralPath $bizHawkRoot).Path
$emuHawkPath = Join-Path $bizHawkRoot "EmuHawk.exe"
$luaScriptPath = Join-Path $PSScriptRoot "bizhawk_runtime_capture.lua"
$ContextPath = "$luaScriptPath.context"
$configPath = Join-Path $bizHawkRoot "config.ini"
$waterboxHostPath = Join-Path $bizHawkRoot "dll\waterboxhost.dll"
$configBackupPath = Join-Path $bizHawkRoot "config.ini.runtime_capture.bak"

try {
    if (-not (Test-Path -LiteralPath $emuHawkPath)) {
        throw "EmuHawk.exe nao encontrado em $emuHawkPath"
    }

    if (-not (Test-Path -LiteralPath $luaScriptPath)) {
        throw "Script Lua nao encontrado em $luaScriptPath"
    }

    $probeAddress = Resolve-ProbeAddress -SymbolPath $SymbolPath
    $originalPathEnv = $env:PATH
    $waterboxLoadError = 0
    $createdTempConfig = $false

    if (Test-Path -LiteralPath $waterboxHostPath) {
        $waterboxLoadError = Test-WaterboxHost -DllPath $waterboxHostPath
        if ($waterboxLoadError -ne 0) {
            throw "BizHawk nao conseguiu carregar waterboxhost.dll (Win32=$waterboxLoadError). Rode tools\emuladores\BizHawk\bizhawk_prereqs.exe para instalar os prerequisitos nativos."
        }
    }

    if (-not (Test-VCRuntime140Present)) {
        throw "VC++ runtime nao encontrado (vcruntime140.dll / vcruntime140_1.dll). Rode tools\emuladores\BizHawk\bizhawk_prereqs.exe."
    }

    if (Test-Path -LiteralPath $configPath) {
        Copy-Item -LiteralPath $configPath -Destination $configBackupPath -Force
        try {
            $configJson = Get-Content -LiteralPath $configPath -Raw | ConvertFrom-Json
        }
        catch {
            throw "Falha ao ler config.ini do BizHawk: $($_.Exception.Message)"
        }
    }
    else {
        $emuhawkVersion = [System.Diagnostics.FileVersionInfo]::GetVersionInfo($emuHawkPath).ProductVersion
        $mainVersion = "2.8"
        if ($emuhawkVersion -match '^(\d+\.\d+)') {
            $mainVersion = $matches[1]
        }
        $configJson = [ordered]@{
            LastWrittenFrom = $mainVersion
            PreferredCores = [ordered]@{
                GEN = "Genplus-gx"
            }
            PreferredPlatformsForExtensions = [ordered]@{
                ".bin" = "GEN"
                ".out" = "GEN"
            }
            RecentLua = [ordered]@{
                recentlist = @()
                AutoLoad = $false
            }
            RecentLuaSession = [ordered]@{
                recentlist = @()
                AutoLoad = $false
            }
            DisableLuaScriptsOnLoad = $false
            LuaEngine = 0
        }
        $createdTempConfig = $true
    }

if ($null -eq $configJson.PreferredPlatformsForExtensions) {
    $configJson | Add-Member -NotePropertyName PreferredPlatformsForExtensions -NotePropertyValue ([ordered]@{})
}
$configJson.LuaEngine = 0
foreach ($ext in @(".bin", ".out")) {
    if ($null -eq $configJson.PreferredPlatformsForExtensions.PSObject.Properties[$ext]) {
        $configJson.PreferredPlatformsForExtensions | Add-Member -NotePropertyName $ext -NotePropertyValue "GEN"
    }
    else {
        $configJson.PreferredPlatformsForExtensions.$ext = "GEN"
    }
}
if ($null -eq $configJson.RecentLua) {
    $configJson | Add-Member -NotePropertyName RecentLua -NotePropertyValue ([ordered]@{})
}
if ($null -eq $configJson.RecentLuaSession) {
    $configJson | Add-Member -NotePropertyName RecentLuaSession -NotePropertyValue ([ordered]@{})
}
$configJson.RecentLua.recentlist = @()
$configJson.RecentLua.AutoLoad = $false
$configJson.RecentLuaSession.recentlist = @()
$configJson.RecentLuaSession.AutoLoad = $false
$configJson.DisableLuaScriptsOnLoad = $false
[System.IO.File]::WriteAllText($configPath, ($configJson | ConvertTo-Json -Depth 100))

$env:SGDK_RT_OUTPUT = $OutputPath
$env:SGDK_RT_PROBE_ADDR = [string]$probeAddress
$env:SGDK_RT_FRAME_WINDOW = [string]$FrameWindow
$env:SGDK_RT_TARGET_SCENE = [string]$TargetScene
$env:SGDK_RT_HEARTBEAT = $HeartbeatPath
$env:SGDK_RT_ERROR = $ErrorPath
$env:PATH = (Join-Path $bizHawkRoot "dll") + ";" + $env:PATH

$launcherLines = @(
    ('SGDK_RT_OUTPUT = [[{0}]]' -f ($OutputPath -replace '\\', '/'))
    ('SGDK_RT_PROBE_ADDR = [[{0}]]' -f $probeAddress)
    ('SGDK_RT_FRAME_WINDOW = [[{0}]]' -f $FrameWindow)
    ('SGDK_RT_TARGET_SCENE = [[{0}]]' -f $TargetScene)
    ('SGDK_RT_PERCEPTUAL_FLUIDEZ = [[{0}]]' -f $env:SGDK_RT_PERCEPTUAL_FLUIDEZ)
    ('SGDK_RT_PERCEPTUAL_LEITURA = [[{0}]]' -f $env:SGDK_RT_PERCEPTUAL_LEITURA)
    ('SGDK_RT_PERCEPTUAL_NATURALIDADE = [[{0}]]' -f $env:SGDK_RT_PERCEPTUAL_NATURALIDADE)
    ('SGDK_RT_PERCEPTUAL_IMPACTO = [[{0}]]' -f $env:SGDK_RT_PERCEPTUAL_IMPACTO)
    ('SGDK_RT_HEARTBEAT = [[{0}]]' -f ($HeartbeatPath -replace '\\', '/'))
    ('SGDK_RT_ERROR = [[{0}]]' -f ($ErrorPath -replace '\\', '/'))
    ('SGDK_RT_CONTEXT = [[{0}]]' -f ($ContextPath -replace '\\', '/'))
    ('dofile([[{0}]])' -f ($luaScriptPath -replace '\\', '/'))
)
[System.IO.File]::WriteAllLines($LauncherPath, $launcherLines)

$contextLines = @(
    "SGDK_RT_OUTPUT=$($OutputPath -replace '\\', '/')"
    "SGDK_RT_PROBE_ADDR=$probeAddress"
    "SGDK_RT_FRAME_WINDOW=$FrameWindow"
    "SGDK_RT_TARGET_SCENE=$TargetScene"
    "SGDK_RT_PERCEPTUAL_FLUIDEZ=$($env:SGDK_RT_PERCEPTUAL_FLUIDEZ)"
    "SGDK_RT_PERCEPTUAL_LEITURA=$($env:SGDK_RT_PERCEPTUAL_LEITURA)"
    "SGDK_RT_PERCEPTUAL_NATURALIDADE=$($env:SGDK_RT_PERCEPTUAL_NATURALIDADE)"
    "SGDK_RT_PERCEPTUAL_IMPACTO=$($env:SGDK_RT_PERCEPTUAL_IMPACTO)"
    "SGDK_RT_HEARTBEAT=$($HeartbeatPath -replace '\\', '/')"
    "SGDK_RT_ERROR=$($ErrorPath -replace '\\', '/')"
    "SGDK_RT_MAX_WAIT_FRAMES=$maxWaitFrames"
)
[System.IO.File]::WriteAllLines($ContextPath, $contextLines)

foreach ($path in @($OutputPath, $HeartbeatPath, $ErrorPath)) {
    if (Test-Path -LiteralPath $path) {
        Remove-Item -LiteralPath $path -Force
    }
}
if (Test-Path -LiteralPath $LegacyTempRomPath) {
    Remove-Item -LiteralPath $LegacyTempRomPath -Force
}

Push-Location $bizHawkRoot
$process = $null
try {
    $luaCliPath = $LauncherPath -replace '\\', '/'
    $process = Start-Process -FilePath $emuHawkPath -ArgumentList @($RomPath, "--luaconsole", "--lua=$luaCliPath") -WorkingDirectory $bizHawkRoot -PassThru
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    $outputReady = $false

    while ((Get-Date) -lt $deadline) {
        if (Test-Path -LiteralPath $OutputPath) {
            $outputReady = $true
            break
        }

        if ($process.HasExited) {
            break
        }

        Start-Sleep -Milliseconds 250
        $process.Refresh()
    }

    $process.Refresh()
    if (-not $process.HasExited -and $outputReady) {
        if (-not $process.WaitForExit(5000)) {
            Stop-Process -Id $process.Id -Force
            $process.WaitForExit()
        }
    }
    elseif (-not $process.HasExited) {
        Stop-Process -Id $process.Id -Force
        $process.WaitForExit()
        throw "Captura de runtime excedeu o timeout de $TimeoutSeconds segundos"
    }

    if ((-not $outputReady) -and $process.ExitCode -ne 0) {
        throw "EmuHawk encerrou com codigo $($process.ExitCode)"
    }
}
finally {
    # Defensive process cleanup: se exception disparou dentro do while/checks acima,
    # o processo EmuHawk pode ficar orfao. Tenta encerramento gracioso + kill forcado.
    if ($process) {
        try {
            $process.Refresh()
            if (-not $process.HasExited) {
                try { $process.CloseMainWindow() | Out-Null } catch { Write-Warning "CloseMainWindow silenced: $_" }
                if (-not $process.WaitForExit(2000)) {
                    try { Stop-Process -Id $process.Id -Force -ErrorAction Stop } catch { Write-Warning "Stop-Process silenced: $_" }
                    $process.WaitForExit(3000) | Out-Null
                }
            }
        } catch {
            Write-Warning "BizHawk cleanup silenced: $_"
        }
    }

    if (Test-Path -LiteralPath $configBackupPath) {
        Copy-Item -LiteralPath $configBackupPath -Destination $configPath -Force
        Remove-Item -LiteralPath $configBackupPath -Force
    }
    elseif ($createdTempConfig -and (Test-Path -LiteralPath $configPath)) {
        Remove-Item -LiteralPath $configPath -Force
    }
    foreach ($cleanupPath in @($LauncherPath, $ContextPath, $HeartbeatPath, $ErrorPath, $RomPath, $LegacyTempRomPath)) {
        if (Test-Path -LiteralPath $cleanupPath) {
            Remove-Item -LiteralPath $cleanupPath -Force
        }
    }
    $env:PATH = $originalPathEnv
    Pop-Location
}

if (-not (Test-Path -LiteralPath $OutputPath)) {
    if (Test-Path -LiteralPath $ErrorPath) {
        throw ("Captura de runtime falhou no Lua: " + (Get-Content -LiteralPath $ErrorPath -Raw))
    }
    if (Test-Path -LiteralPath $HeartbeatPath) {
        throw ("Captura de runtime nao gerou $OutputPath. Ultimo heartbeat: " + (Get-Content -LiteralPath $HeartbeatPath -Raw))
    }
    throw "Captura de runtime nao gerou $OutputPath"
}

    Get-Content -LiteralPath $OutputPath
}
catch {
    if ($requestedEmulator -eq "auto") {
        Invoke-BlastEmRuntimeCapture `
            -ProjectDir $ProjectDir `
            -RomPath $RomPath `
            -OutputPath $OutputPath `
            -FrameWindow $FrameWindow `
            -TimeoutSeconds $TimeoutSeconds `
            -NavigationSequence $BlastEmNavigation
        if (Test-Path -LiteralPath $RomPath) {
            Remove-Item -LiteralPath $RomPath -Force
        }
        Get-Content -LiteralPath $OutputPath
        exit 0
    }
    throw
}
