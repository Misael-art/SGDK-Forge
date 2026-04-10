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
    [int]$TimeoutSeconds = 45
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
    if ([System.IO.Path]::GetExtension($resolvedRomPath).Equals(".bin", [System.StringComparison]::OrdinalIgnoreCase)) {
        return $resolvedRomPath
    }

    $binSibling = [System.IO.Path]::ChangeExtension($resolvedRomPath, ".bin")
    if (Test-Path -LiteralPath $binSibling) {
        return (Resolve-Path -LiteralPath $binSibling).Path
    }

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
$SymbolPath = Join-Path $ProjectDir "out\symbol.txt"
if (-not (Test-Path -LiteralPath $SymbolPath)) {
    throw "Arquivo de simbolos nao encontrado: $SymbolPath"
}

if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $OutputPath = Join-Path $LogDir "runtime_metrics.json"
}

$HeartbeatPath = Join-Path $LogDir "runtime_capture_heartbeat.txt"
$ErrorPath = Join-Path $LogDir "runtime_capture_error.txt"
$LauncherPath = Join-Path $LogDir "runtime_capture_launcher.lua"

$bizHawkRoot = Join-Path $PSScriptRoot "..\emuladores\BizHawk"
$bizHawkRoot = (Resolve-Path -LiteralPath $bizHawkRoot).Path
$emuHawkPath = Join-Path $bizHawkRoot "EmuHawk.exe"
$luaScriptPath = Join-Path $PSScriptRoot "bizhawk_runtime_capture.lua"
$ContextPath = "$luaScriptPath.context"
$configPath = Join-Path $bizHawkRoot "config.ini"
$waterboxHostPath = Join-Path $bizHawkRoot "dll\waterboxhost.dll"

if (-not (Test-Path -LiteralPath $emuHawkPath)) {
    throw "EmuHawk.exe nao encontrado em $emuHawkPath"
}

if (-not (Test-Path -LiteralPath $luaScriptPath)) {
    throw "Script Lua nao encontrado em $luaScriptPath"
}

$probeAddress = Resolve-ProbeAddress -SymbolPath $SymbolPath
$originalConfigContent = $null
$originalPathEnv = $env:PATH
$waterboxLoadError = 0

if (Test-Path -LiteralPath $waterboxHostPath) {
    $waterboxLoadError = Test-WaterboxHost -DllPath $waterboxHostPath
    if ($waterboxLoadError -ne 0) {
        throw "BizHawk nao conseguiu carregar waterboxhost.dll (Win32=$waterboxLoadError). Rode tools\emuladores\BizHawk\bizhawk_prereqs.exe para instalar os prerequisitos nativos."
    }
}

if (Test-Path -LiteralPath $configPath) {
    $originalConfigContent = Get-Content -LiteralPath $configPath -Raw
    $configJson = $originalConfigContent | ConvertFrom-Json
    $luaScriptConfigPath = $luaScriptPath -replace '\\', '/'
    $configJson.LuaEngine = 0
    if ($null -eq $configJson.PreferredPlatformsForExtensions.PSObject.Properties[".out"]) {
        $configJson.PreferredPlatformsForExtensions | Add-Member -NotePropertyName ".out" -NotePropertyValue "GEN"
    }
    else {
        $configJson.PreferredPlatformsForExtensions.".out" = "GEN"
    }
    $configJson.RecentLua.recentlist = @()
    $configJson.RecentLua.AutoLoad = $false
    $configJson.RecentLuaSession.recentlist = @()
    $configJson.RecentLuaSession.AutoLoad = $false
    $configJson.DisableLuaScriptsOnLoad = $false
    [System.IO.File]::WriteAllText($configPath, ($configJson | ConvertTo-Json -Depth 100))
}

$env:SGDK_RT_OUTPUT = $OutputPath
$env:SGDK_RT_PROBE_ADDR = [string]$probeAddress
$env:SGDK_RT_FRAME_WINDOW = [string]$FrameWindow
$env:SGDK_RT_TARGET_SCENE = [string]$TargetScene
$env:SGDK_RT_PERCEPTUAL_FLUIDEZ = if ($env:SGDK_PERCEPTUAL_FLUIDEZ) { $env:SGDK_PERCEPTUAL_FLUIDEZ } else { "0" }
$env:SGDK_RT_PERCEPTUAL_LEITURA = if ($env:SGDK_PERCEPTUAL_LEITURA) { $env:SGDK_PERCEPTUAL_LEITURA } else { "0" }
$env:SGDK_RT_PERCEPTUAL_NATURALIDADE = if ($env:SGDK_PERCEPTUAL_NATURALIDADE) { $env:SGDK_PERCEPTUAL_NATURALIDADE } else { "0" }
$env:SGDK_RT_PERCEPTUAL_IMPACTO = if ($env:SGDK_PERCEPTUAL_IMPACTO) { $env:SGDK_PERCEPTUAL_IMPACTO } else { "0" }
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
)
[System.IO.File]::WriteAllLines($ContextPath, $contextLines)

foreach ($path in @($OutputPath, $HeartbeatPath, $ErrorPath)) {
    if (Test-Path -LiteralPath $path) {
        Remove-Item -LiteralPath $path -Force
    }
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

    if (-not $process.HasExited -and $outputReady) {
        Stop-Process -Id $process.Id -Force
        $process.WaitForExit()
    } elseif (-not $process.HasExited) {
        Stop-Process -Id $process.Id -Force
        $process.WaitForExit()
        throw "Captura de runtime excedeu o timeout de $TimeoutSeconds segundos"
    }

    if ((-not $outputReady) -and $process.ExitCode -ne 0) {
        throw "EmuHawk encerrou com codigo $($process.ExitCode)"
    }
}
finally {
    if ($null -ne $originalConfigContent) {
        [System.IO.File]::WriteAllText($configPath, $originalConfigContent)
    }
    if (Test-Path -LiteralPath $LauncherPath) {
        Remove-Item -LiteralPath $LauncherPath -Force
    }
    if (Test-Path -LiteralPath $ContextPath) {
        Remove-Item -LiteralPath $ContextPath -Force
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
