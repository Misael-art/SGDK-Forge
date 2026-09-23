[CmdletBinding()]
param(
    [string]$ProjectDir = "",
    [int]$DurationMs = 46000
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($ProjectDir)) {
    $ProjectDir = (Get-Location).Path
}
$ProjectDir = (Resolve-Path -LiteralPath $ProjectDir).Path
$workspaceRoot = (Resolve-Path -LiteralPath (Join-Path $ProjectDir "..\..")).Path
$wrapperRoot = Join-Path $workspaceRoot "tools\sgdk_wrapper"
$automationModule = Join-Path $wrapperRoot "lib\blastem_automation.psm1"
$blastEmRoot = Join-Path $workspaceRoot "tools\emuladores\BlastEm"
$blastEmExe = Join-Path $blastEmRoot "blastem.exe"
$blastEmDefaultCfg = Join-Path $blastEmRoot "default.cfg"
$sourceRom = Join-Path $ProjectDir "out\rom.bin"
$routeRoot = Join-Path $ProjectDir "out\evidence\blastem\routes\success"
$sandboxRoot = Join-Path $ProjectDir "out\blastem_env_sector01_success"
$saveRoot = Join-Path $sandboxRoot "saves"
$screenshotRoot = Join-Path $sandboxRoot "screenshots"
$homeRoot = Join-Path $sandboxRoot "Home"
$localAppData = Join-Path $homeRoot "AppData\Local"
$appData = Join-Path $homeRoot "AppData\Roaming"
$userConfigDir = Join-Path $localAppData "blastem"
$userConfig = Join-Path $userConfigDir "blastem.cfg"
$captureRom = Join-Path $ProjectDir "out\logs\sector01_success_route_rom.bin"
$routeLog = Join-Path $routeRoot "route_log.jsonl"

foreach ($required in @($automationModule, $blastEmExe, $blastEmDefaultCfg, $sourceRom)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "Arquivo obrigatorio ausente: $required"
    }
}

Import-Module -Name $automationModule -Force

$projectPrefix = $ProjectDir.TrimEnd("\", "/") + [System.IO.Path]::DirectorySeparatorChar
$sandboxFull = [System.IO.Path]::GetFullPath($sandboxRoot)
if (-not $sandboxFull.StartsWith($projectPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Sandbox de rota escapou do projeto: $sandboxFull"
}
if (Test-Path -LiteralPath $sandboxRoot) {
    Remove-Item -LiteralPath $sandboxRoot -Recurse -Force
}

New-Item -ItemType Directory -Force -Path $routeRoot, $saveRoot, $screenshotRoot, $userConfigDir | Out-Null
Copy-Item -LiteralPath $sourceRom -Destination $captureRom -Force
Write-BlastEmConfig `
    -BaseConfigPath $blastEmDefaultCfg `
    -TargetConfigPath $userConfig `
    -SaveRoot $saveRoot `
    -ScreenshotRoot $screenshotRoot

$romBase = [System.IO.Path]::GetFileNameWithoutExtension($captureRom)
$saveDir = Join-Path $saveRoot $romBase
$savePath = Join-Path $saveDir "save.sram"
New-Item -ItemType Directory -Force -Path $saveDir | Out-Null

# SBIS v1: direct boot into APP_SCENE_RACE (3), checksum A55A xor fields.
$initialSram = New-Object byte[] 32768
[System.Text.Encoding]::ASCII.GetBytes("SBIS").CopyTo($initialSram, 0x120)
$bootstrapWords = @(1, 12, 3, (0xA55A -bxor 1 -bxor 12 -bxor 3))
for ($i = 0; $i -lt $bootstrapWords.Count; $i++) {
    $offset = 0x124 + ($i * 2)
    $initialSram[$offset] = [byte](($bootstrapWords[$i] -shr 8) -band 0xFF)
    $initialSram[$offset + 1] = [byte]($bootstrapWords[$i] -band 0xFF)
}
[System.IO.File]::WriteAllBytes($savePath, $initialSram)

if (-not ("Sector01TargetInput" -as [type])) {
    Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

public static class Sector01TargetInput
{
    public const uint WM_KEYDOWN = 0x0100;
    public const uint WM_KEYUP = 0x0101;
    public const uint WM_CLOSE = 0x0010;

    [DllImport("user32.dll", SetLastError = true)]
    public static extern bool PostMessage(IntPtr hWnd, uint msg, IntPtr wParam, IntPtr lParam);

    [DllImport("user32.dll")]
    public static extern uint MapVirtualKey(uint code, uint mapType);
}
"@
}

function Write-RouteEvent {
    param(
        [Parameter(Mandatory)][string]$Event,
        [hashtable]$Data = @{}
    )

    $entry = [ordered]@{
        timestamp_utc = [datetime]::UtcNow.ToString("o")
        elapsed_ms = if ($script:routeClock) { [int]$script:routeClock.ElapsedMilliseconds } else { 0 }
        event = $Event
    }
    foreach ($key in $Data.Keys) {
        $entry[$key] = $Data[$key]
    }
    [System.IO.File]::AppendAllText(
        $routeLog,
        (($entry | ConvertTo-Json -Compress -Depth 8) + [Environment]::NewLine),
        (New-Object System.Text.UTF8Encoding($false))
    )
}

function Wait-RouteTime {
    param([Parameter(Mandatory)][int]$TargetMs)

    while ($script:routeClock.ElapsedMilliseconds -lt $TargetMs) {
        $remaining = $TargetMs - [int]$script:routeClock.ElapsedMilliseconds
        Start-Sleep -Milliseconds ([Math]::Min(25, [Math]::Max(1, $remaining)))
    }
}

function Send-TargetedSdlKey {
    param(
        [Parameter(Mandatory)][System.Diagnostics.Process]$Process,
        [Parameter(Mandatory)][uint32]$VirtualKey,
        [bool]$Extended = $false,
        [int]$HoldMs = 90,
        [string]$Label = ""
    )

    $Process.Refresh()
    if ($Process.HasExited -or $Process.MainWindowHandle -eq [IntPtr]::Zero) {
        throw "BlastEm indisponivel ao enviar tecla $Label."
    }

    $scan = [Sector01TargetInput]::MapVirtualKey($VirtualKey, 0)
    [int64]$downBits = 1L -bor ([int64]$scan -shl 16)
    if ($Extended) {
        $downBits = $downBits -bor 0x01000000L
    }
    [int64]$upBits = $downBits -bor 0xC0000000L

    $downOk = [Sector01TargetInput]::PostMessage(
        $Process.MainWindowHandle,
        [Sector01TargetInput]::WM_KEYDOWN,
        [IntPtr]([int64]$VirtualKey),
        [IntPtr]$downBits
    )
    Start-Sleep -Milliseconds $HoldMs
    $upOk = [Sector01TargetInput]::PostMessage(
        $Process.MainWindowHandle,
        [Sector01TargetInput]::WM_KEYUP,
        [IntPtr]([int64]$VirtualKey),
        [IntPtr]$upBits
    )

    Write-RouteEvent -Event "targeted_key" -Data @{
        label = $Label
        virtual_key = ("0x{0:X2}" -f $VirtualKey)
        scan_code = ("0x{0:X2}" -f $scan)
        keydown_posted = [bool]$downOk
        keyup_posted = [bool]$upOk
    }
    if (-not $downOk -or -not $upOk) {
        throw "PostMessage falhou para $Label."
    }
}

function Save-RouteFrame {
    param(
        [Parameter(Mandatory)][System.Diagnostics.Process]$Process,
        [Parameter(Mandatory)][string]$Name
    )

    $path = Join-Path $routeRoot $Name
    $saved = Save-BlastEmWindowScreenshot -Process $Process -OutputPath $path
    Write-RouteEvent -Event "screenshot" -Data @{ name = $Name; saved = [bool]$saved; path = $path }
    if (-not $saved) {
        throw "Falha ao capturar $Name."
    }
}

function Read-U16BE {
    param([byte[]]$Bytes, [int]$Offset)
    return (([int]$Bytes[$Offset] -shl 8) -bor [int]$Bytes[$Offset + 1])
}

$process = $null
$script:routeClock = $null
try {
    if (Test-Path -LiteralPath $routeLog) {
        Remove-Item -LiteralPath $routeLog -Force
    }

    $startInfo = New-Object System.Diagnostics.ProcessStartInfo
    $startInfo.FileName = $blastEmExe
    $startInfo.Arguments = '"' + $captureRom + '"'
    $startInfo.WorkingDirectory = $blastEmRoot
    $startInfo.UseShellExecute = $false
    $startInfo.Environment["LOCALAPPDATA"] = $localAppData
    $startInfo.Environment["APPDATA"] = $appData
    $startInfo.Environment["USERPROFILE"] = $homeRoot
    $startInfo.Environment["HOME"] = $homeRoot

    $process = [System.Diagnostics.Process]::Start($startInfo)
    if (-not $process) {
        throw "Falha ao iniciar BlastEm."
    }

    $windowDeadline = (Get-Date).AddSeconds(20)
    while ((Get-Date) -lt $windowDeadline) {
        $process.Refresh()
        if ($process.HasExited) {
            throw "BlastEm encerrou antes da rota."
        }
        if ($process.MainWindowHandle -ne [IntPtr]::Zero) {
            break
        }
        Start-Sleep -Milliseconds 100
    }
    $process.Refresh()
    if ($process.MainWindowHandle -eq [IntPtr]::Zero) {
        throw "Janela SDL do BlastEm nao apareceu."
    }

    $script:routeClock = [System.Diagnostics.Stopwatch]::StartNew()
    Write-RouteEvent -Event "route_started" -Data @{
        pid = $process.Id
        hwnd = ("0x{0:X}" -f $process.MainWindowHandle.ToInt64())
        rom_sha256 = (Get-FileHash -LiteralPath $sourceRom -Algorithm SHA256).Hash
    }

    Wait-RouteTime 700
    Save-RouteFrame -Process $process -Name "race_start.png"

    # The initial PAL_fadeInAll is blocking; send movement only after it ends.
    Wait-RouteTime 2500
    Send-TargetedSdlKey -Process $process -VirtualKey 0x28 -Extended $true -Label "lane_down_early"

    # Jump through the right-lane Low Stone window at step 36.
    Wait-RouteTime 11900
    Send-TargetedSdlKey -Process $process -VirtualKey 0x53 -Label "jump_b"
    Wait-RouteTime 12550
    Send-TargetedSdlKey -Process $process -VirtualKey 0x53 -Label "jump_b_refresh"
    Wait-RouteTime 12100
    Save-RouteFrame -Process $process -Name "jump_active.png"

    # Mid-run frame includes the pursuer, HUD/WINDOW and first pressure gate arc.
    Wait-RouteTime 14000
    Save-RouteFrame -Process $process -Name "race_mid.png"

    # Center is the safe lane for the dual Astral Mark at step 56.
    Wait-RouteTime 17500
    Send-TargetedSdlKey -Process $process -VirtualKey 0x26 -Extended $true -Label "lane_up_center"

    # Pulse clears the tutorial hazard after right/right/all Lumen reaches 20.
    Wait-RouteTime 19000
    Send-TargetedSdlKey -Process $process -VirtualKey 0x41 -Label "pulse_a"
    Wait-RouteTime 19200
    Save-RouteFrame -Process $process -Name "pulse_active.png"

    # Move right for the step-70 left/center stones, then return for the Beacon.
    Wait-RouteTime 19600
    Send-TargetedSdlKey -Process $process -VirtualKey 0x28 -Extended $true -Label "lane_down"
    Wait-RouteTime 24000
    Send-TargetedSdlKey -Process $process -VirtualKey 0x26 -Extended $true -Label "lane_up"

    Wait-RouteTime 24500
    Save-RouteFrame -Process $process -Name "beacon_approach.png"

    Wait-RouteTime 29500
    Save-RouteFrame -Process $process -Name "result_complete.png"

    # Result grace period has expired; return naturally to Title.
    Wait-RouteTime 31200
    Send-TargetedSdlKey -Process $process -VirtualKey 0x0D -Label "result_start"
    Wait-RouteTime 33500
    Save-RouteFrame -Process $process -Name "title_return.png"

    Wait-RouteTime $DurationMs
    $process.Refresh()
    $closePosted = [Sector01TargetInput]::PostMessage(
        $process.MainWindowHandle,
        [Sector01TargetInput]::WM_CLOSE,
        [IntPtr]::Zero,
        [IntPtr]::Zero
    )
    Write-RouteEvent -Event "close_posted" -Data @{ posted = [bool]$closePosted }
    if (-not $process.WaitForExit(8000)) {
        Stop-Process -Id $process.Id -Force
        [void]$process.WaitForExit(2000)
        throw "BlastEm nao fechou graciosamente; SRAM nao e confiavel."
    }

    if (-not (Test-Path -LiteralPath $savePath -PathType Leaf)) {
        throw "save.sram da rota nao foi persistida."
    }

    $persisted = [System.IO.File]::ReadAllBytes($savePath)
    if ($persisted.Length -lt 0x20A) {
        throw "save.sram da rota esta truncada."
    }
    $mtrMagic = [System.Text.Encoding]::ASCII.GetString($persisted, 0x120, 3)
    $mdrtMagic = [System.Text.Encoding]::ASCII.GetString($persisted, 0x200, 4)
    $vlabMagic = [System.Text.Encoding]::ASCII.GetString($persisted, 0, 4)
    $success = ($mtrMagic -eq "MTR" -and $persisted[0x123] -eq 1)

    Copy-Item -LiteralPath $savePath -Destination (Join-Path $routeRoot "save.sram") -Force
    Copy-Item -LiteralPath $sourceRom -Destination (Join-Path $routeRoot "rom.bin") -Force

    if ($vlabMagic -eq "VLAB") {
        $vlabBytes = Read-U16BE -Bytes $persisted -Offset 6
        if ($vlabBytes -le 0 -or $vlabBytes -gt $persisted.Length) {
            throw "Bloco VLAB invalido: $vlabBytes bytes."
        }
        $visualDump = New-Object byte[] $vlabBytes
        [System.Array]::Copy($persisted, 0, $visualDump, 0, $vlabBytes)
        [System.IO.File]::WriteAllBytes((Join-Path $routeRoot "visual_vdp_dump.bin"), $visualDump)
    }

    if ($mdrtMagic -eq "MDRT") {
        & (Join-Path $wrapperRoot "parse_blastem_sram_runtime.ps1") `
            -SramPath $savePath `
            -OutputPath (Join-Path $routeRoot "runtime_metrics.json") `
            -SramOffset 0x200 `
            -FrameWindow 1800 `
            -TimeoutFrame 0 | Out-Null
    }

    $artifactRows = @()
    foreach ($file in Get-ChildItem -LiteralPath $routeRoot -File) {
        $artifactRows += [ordered]@{
            name = $file.Name
            size_bytes = $file.Length
            sha256 = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
        }
    }

    $manifest = [ordered]@{
        schema_version = 1
        route = "sector01_success"
        emulator = "BlastEm"
        input_transport = "targeted_wm_key_to_sdl_window"
        rom_sha256 = (Get-FileHash -LiteralPath $sourceRom -Algorithm SHA256).Hash.ToLowerInvariant()
        result_magic = $mtrMagic
        sector_cleared = $success
        current_scene_id = [int]$persisted[0x10B]
        observed_input = ("0x{0:X4}" -f (Read-U16BE -Bytes $persisted -Offset 0x115))
        vlab_magic = $vlabMagic
        mdrt_magic = $mdrtMagic
        artifacts = $artifactRows
    }
    [System.IO.File]::WriteAllText(
        (Join-Path $routeRoot "route_manifest.json"),
        ($manifest | ConvertTo-Json -Depth 8),
        (New-Object System.Text.UTF8Encoding($false))
    )

    if (-not $success) {
        throw "A rota terminou sem MTR de sucesso. Evidencia preservada em $routeRoot"
    }
    if ($mdrtMagic -ne "MDRT" -or $vlabMagic -ne "VLAB") {
        throw "A rota venceu, mas o bundle MDRT/VLAB esta incompleto."
    }

    $manifest | ConvertTo-Json -Depth 8
}
finally {
    if ($process -and -not $process.HasExited) {
        try {
            [void][Sector01TargetInput]::PostMessage(
                $process.MainWindowHandle,
                [Sector01TargetInput]::WM_CLOSE,
                [IntPtr]::Zero,
                [IntPtr]::Zero
            )
            if (-not $process.WaitForExit(3000)) {
                Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
            }
        }
        catch {
            Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        }
    }
}
