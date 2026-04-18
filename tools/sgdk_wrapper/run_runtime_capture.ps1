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
    [string[]]$BlastEmNavigation = @("wait:5000", "start")
)

$ErrorActionPreference = "Stop"

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

function Ensure-BlastEmAutomationLoaded {
    if ($script:BlastEmAutomationLoaded) {
        return
    }

    Add-Type -AssemblyName System.Windows.Forms
    Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public static class SGDKBlastEmWin32 {
    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

    [DllImport("user32.dll")]
    public static extern bool BringWindowToTop(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern uint MapVirtualKey(uint uCode, uint uMapType);

    [DllImport("user32.dll")]
    public static extern bool PostMessage(IntPtr hWnd, uint msg, IntPtr wParam, IntPtr lParam);
}
"@ | Out-Null

    $script:BlastEmAutomationLoaded = $true
}

function Wait-ForBlastEmMainWindow {
    param(
        [Parameter(Mandatory = $true)][System.Diagnostics.Process]$Process,
        [Parameter(Mandatory = $false)][int]$TimeoutSeconds = 20
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

function Focus-BlastEmWindow {
    param(
        [Parameter(Mandatory = $true)][System.Diagnostics.Process]$Process
    )

    $Process.Refresh()
    if ($Process.MainWindowHandle -eq 0) {
        throw "BlastEm nao expôs uma janela focavel."
    }

    [SGDKBlastEmWin32]::ShowWindow($Process.MainWindowHandle, 9) | Out-Null
    [SGDKBlastEmWin32]::BringWindowToTop($Process.MainWindowHandle) | Out-Null
    [SGDKBlastEmWin32]::SetForegroundWindow($Process.MainWindowHandle) | Out-Null
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

    $scanCode = [SGDKBlastEmWin32]::MapVirtualKey($VirtualKey, 0)
    $wmKeyDown = 0x100
    $wmKeyUp = 0x101
    $downLParam = 1 -bor ($scanCode -shl 16)
    $upLParam = 1 -bor ($scanCode -shl 16) -bor 0xC0000000

    [SGDKBlastEmWin32]::PostMessage($Process.MainWindowHandle, $wmKeyDown, [intptr]$VirtualKey, [intptr]$downLParam) | Out-Null
    Start-Sleep -Milliseconds $HoldMilliseconds
    [SGDKBlastEmWin32]::PostMessage($Process.MainWindowHandle, $wmKeyUp, [intptr]$VirtualKey, [intptr]$upLParam) | Out-Null
}

function Invoke-BlastEmNavigation {
    param(
        [Parameter(Mandatory = $true)][System.Diagnostics.Process]$Process,
        [Parameter(Mandatory = $true)][string[]]$Sequence
    )

    if (-not $Sequence -or $Sequence.Count -eq 0) {
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
        Focus-BlastEmWindow -Process $Process
        [System.Windows.Forms.SendKeys]::SendWait($sendKeys[$step])
        Start-Sleep -Milliseconds 220
    }
}

function Write-BlastEmConfig {
    param(
        [Parameter(Mandatory = $true)][string]$BaseConfigPath,
        [Parameter(Mandatory = $true)][string]$TargetConfigPath,
        [Parameter(Mandatory = $true)][string]$SaveRoot
    )

    $content = Get-Content -LiteralPath $BaseConfigPath -Raw
    $normalizedSave = $SaveRoot.Replace("\", "/")
    $content = [System.Text.RegularExpressions.Regex]::Replace($content, '(?m)^\s*save_path\s+.*$', "`tsave_path $normalizedSave/`$ROMNAME")
    $configDir = Split-Path -Parent $TargetConfigPath
    New-Item -ItemType Directory -Force -Path $configDir | Out-Null
    Set-Content -LiteralPath $TargetConfigPath -Value $content -Encoding UTF8
}

function Test-MDRTRuntimeSignature {
    param(
        [Parameter(Mandatory = $true)][string]$SramPath,
        [Parameter(Mandatory = $false)][int]$Offset = 0x200
    )

    try {
        $bytes = [System.IO.File]::ReadAllBytes($SramPath)
        if ($bytes.Length -lt ($Offset + 4)) {
            return $false
        }
        return ([System.Text.Encoding]::ASCII.GetString($bytes, $Offset, 4) -eq "MDRT")
    }
    catch {
        return $false
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

function Wait-ForRuntimeSram {
    param(
        [Parameter(Mandatory = $true)][string[]]$RootPaths,
        [Parameter(Mandatory = $false)][int]$TimeoutSeconds = 20
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        foreach ($root in $RootPaths) {
            $candidate = Get-NewestFileOrNull -RootPath $root -Filter {
                $_.Length -gt 0 -and (
                    $_.Name -ieq "save.sram" -or
                    $_.Extension -ieq ".sram" -or
                    $_.Extension -ieq ".srm" -or
                    $_.Extension -ieq ".sav"
                )
            }
            if ($candidate -and (Test-MDRTRuntimeSignature -SramPath $candidate.FullName)) {
                return $candidate.FullName
            }
        }

        Start-Sleep -Milliseconds 400
    }

    return $null
}

function Invoke-BlastEmRuntimeCapture {
    param(
        [Parameter(Mandatory = $true)][string]$ProjectDir,
        [Parameter(Mandatory = $true)][string]$RomPath,
        [Parameter(Mandatory = $true)][string]$OutputPath,
        [Parameter(Mandatory = $true)][int]$FrameWindow,
        [Parameter(Mandatory = $true)][int]$TimeoutSeconds,
        [Parameter(Mandatory = $true)][string[]]$NavigationSequence,
        [Parameter(Mandatory = $false)][int]$SramOffset = 0x200
    )

    Ensure-BlastEmAutomationLoaded

    $workspaceRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")
    $blastEmExe = Join-Path $workspaceRoot "tools\emuladores\Blastem\blastem.exe"
    $blastEmDefaultCfg = Join-Path $workspaceRoot "tools\emuladores\Blastem\default.cfg"
    if (-not (Test-Path -LiteralPath $blastEmExe)) {
        throw "blastem.exe nao encontrado em $blastEmExe"
    }
    if (-not (Test-Path -LiteralPath $blastEmDefaultCfg)) {
        throw "default.cfg do BlastEm nao encontrado em $blastEmDefaultCfg"
    }

    $sandboxRoot = Join-Path $ProjectDir "out\blastem_env_runtime"
    $sandboxLocalAppData = Join-Path $sandboxRoot "LocalAppData"
    $sandboxAppData = Join-Path $sandboxRoot "AppData"
    $sandboxHome = Join-Path $sandboxRoot "Home"
    $sandboxUserDir = Join-Path $sandboxLocalAppData "blastem"
    $sandboxUserCfg = Join-Path $sandboxUserDir "blastem.cfg"
    $saveRoot = Join-Path $ProjectDir "out\logs\_blastem_runtime_staging"

    New-Item -ItemType Directory -Force -Path $sandboxLocalAppData | Out-Null
    New-Item -ItemType Directory -Force -Path $sandboxAppData | Out-Null
    New-Item -ItemType Directory -Force -Path $sandboxHome | Out-Null
    if (Test-Path -LiteralPath $saveRoot) {
        Remove-Item -LiteralPath $saveRoot -Recurse -Force
    }
    New-Item -ItemType Directory -Force -Path $saveRoot | Out-Null

    $configBackup = $null
    if (Test-Path -LiteralPath $sandboxUserCfg) {
        $configBackup = Get-Content -LiteralPath $sandboxUserCfg -Raw
    }

    try {
        Write-BlastEmConfig -BaseConfigPath $blastEmDefaultCfg -TargetConfigPath $sandboxUserCfg -SaveRoot $saveRoot

        $processStartInfo = New-Object System.Diagnostics.ProcessStartInfo
        $processStartInfo.FileName = $blastEmExe
        $processStartInfo.Arguments = ('"' + $RomPath + '"')
        $processStartInfo.WorkingDirectory = Split-Path -Parent $blastEmExe
        $processStartInfo.UseShellExecute = $false
        $processStartInfo.Environment["LOCALAPPDATA"] = $sandboxLocalAppData
        $processStartInfo.Environment["APPDATA"] = $sandboxAppData
        $processStartInfo.Environment["USERPROFILE"] = $sandboxHome
        $processStartInfo.Environment["HOME"] = $sandboxHome
        $process = [System.Diagnostics.Process]::Start($processStartInfo)
        if (-not $process) {
            throw "Falha ao iniciar o BlastEm."
        }

        Wait-ForBlastEmMainWindow -Process $process -TimeoutSeconds 20
        Focus-BlastEmWindow -Process $process
        Invoke-BlastEmNavigation -Process $process -Sequence $NavigationSequence

        Start-Sleep -Seconds $TimeoutSeconds

        $gracefulExit = $false
        if ($process.CloseMainWindow()) {
            if ($process.WaitForExit(8000)) {
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
    }
    finally {
        if ($null -ne $configBackup) {
            Set-Content -LiteralPath $sandboxUserCfg -Value $configBackup -Encoding UTF8
        }
    }

    Start-Sleep -Seconds 2

    $runtimeSram = Wait-ForRuntimeSram -RootPaths @($saveRoot, $sandboxRoot) -TimeoutSeconds 20
    if (-not $runtimeSram) {
        throw "save.sram com assinatura MDRT nao foi encontrado (roots: $saveRoot ; $sandboxRoot)."
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
