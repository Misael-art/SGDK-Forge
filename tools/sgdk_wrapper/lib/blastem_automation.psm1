<#
.SYNOPSIS
  Biblioteca canonica unica de automacao BlastEm para o wrapper SGDK.

.DESCRIPTION
  Fonte de verdade operacional para todos os fluxos que falam com o BlastEm:
    - `run_runtime_capture.ps1`
    - `run_visual_capture.ps1`
    - `run_scene_capture_matrix.ps1`

  Contrato canonico de readiness e debug (2026-04):

    1) GDB stub do BlastEm (release oficial):
       - Z0 (breakpoint simples)         : SUPORTADO
       - Z2/Z3/Z4 (watchpoints)          : NAO SUPORTADO pelo stub (pacote vazio)
       - `m addr,len` com CPU parada      : SUPORTADO
       - `c` (continue) + leitura         : degrada o canal interativo
       CONCLUSAO: nao existe rota viavel de heartbeat ao vivo via Z2.
       Qualquer tentativa futura de rota Z2-based exige reavaliacao do stub
       em release nova do BlastEm e aprovacao humana explicita.

    2) Readiness canonica:
       - ROM expoe heartbeat `READY` em SRAM `0x100`, re-assinado em rolling
         (READY + 3 bytes de frame-counter) a cada N frames pos-warmup.
       - Wrapper detecta via snapshot periodico da SRAM do sandbox:
         `Test-MDReadyHeartbeat` + `Find-FirstSramWithReady`.
       - Detecao em fast-path via `FileSystemWatcher` em $SaveRoots com
         polling como backstop.
       - Flush-trigger ativo: a cada K presses sem READY, ciclo breve de
         ESC pause/resume forca o BlastEm a flushar SRAM para o sandbox.
       - Key rotation opcional: em timeout do 1o laco, tentativa extra com
         tecla alternativa.
       - Toda evidencia gated por `Test-FreshSramCandidate` (sandbox-root +
         processStartedAt).

    3) Sandbox de execucao:
       - sempre `out/blastem_env_*` do projeto alvo
       - `HOME`/`USERPROFILE` apontando para AppData do sandbox
       - `save_path` e `screenshot_path` em `ui {}` do cfg gerado
       - proibido fallback para `%LOCALAPPDATA%\\blastem\\rom` global

    4) Close escalonado obrigatorio:
       ESC -> WM_CLOSE -> Alt+F4 -> Stop-Process.

    5) Auditoria: toda etapa emite JSONL em `out/logs/*_blastem.log` com
       campos canonicos (`navigation_mode`, `ready_probe_source`,
       `fresh_sram_confirmed`, `sandbox_root`, `close_exit_mode`, ...).

  Qualquer regressao desse contrato deve ser bloqueada por revisao humana.
#>

Set-StrictMode -Version Latest

$script:BlastEmAutomationLoaded = $false
$script:BlastEmInputSize = 0

function Ensure-BlastEmAutomationLoaded {
    if ($script:BlastEmAutomationLoaded) {
        return
    }

    Add-Type -AssemblyName System.Drawing
    Add-Type -AssemblyName System.Windows.Forms
    Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

public static class SGDKBlastEmWin32 {
    [StructLayout(LayoutKind.Sequential)]
    public struct RECT {
        public int Left;
        public int Top;
        public int Right;
        public int Bottom;
    }

    [StructLayout(LayoutKind.Sequential)]
    public struct KEYBDINPUT {
        public ushort wVk;
        public ushort wScan;
        public uint   dwFlags;
        public uint   time;
        public IntPtr dwExtraInfo;
    }

    [StructLayout(LayoutKind.Sequential)]
    public struct MOUSEINPUT {
        public int    dx;
        public int    dy;
        public uint   mouseData;
        public uint   dwFlags;
        public uint   time;
        public IntPtr dwExtraInfo;
    }

    [StructLayout(LayoutKind.Sequential)]
    public struct HARDWAREINPUT {
        public uint   uMsg;
        public ushort wParamL;
        public ushort wParamH;
    }

    [StructLayout(LayoutKind.Explicit)]
    public struct INPUTUNION {
        [FieldOffset(0)] public MOUSEINPUT    mi;
        [FieldOffset(0)] public KEYBDINPUT    ki;
        [FieldOffset(0)] public HARDWAREINPUT hi;
    }

    [StructLayout(LayoutKind.Sequential)]
    public struct INPUT {
        public uint       type;
        public INPUTUNION u;
    }

    public const uint INPUT_KEYBOARD       = 1;
    public const uint KEYEVENTF_KEYUP       = 0x0002;
    public const uint KEYEVENTF_SCANCODE    = 0x0008;
    public const uint KEYEVENTF_EXTENDEDKEY = 0x0001;

    [DllImport("user32.dll", SetLastError = true)]
    public static extern uint SendInput(uint nInputs, INPUT[] pInputs, int cbSize);

    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

    [DllImport("user32.dll")]
    public static extern bool BringWindowToTop(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern IntPtr GetForegroundWindow();

    [DllImport("user32.dll")]
    public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);

    [DllImport("kernel32.dll")]
    public static extern uint GetCurrentThreadId();

    [DllImport("user32.dll")]
    public static extern bool AttachThreadInput(uint idAttach, uint idAttachTo, bool fAttach);

    [DllImport("user32.dll")]
    public static extern uint MapVirtualKey(uint uCode, uint uMapType);

    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);

    [DllImport("user32.dll")]
    public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdcBlt, uint nFlags);
}
"@ | Out-Null

    $script:BlastEmAutomationLoaded = $true
    $script:BlastEmInputSize = [System.Runtime.InteropServices.Marshal]::SizeOf([type]"SGDKBlastEmWin32+INPUT")
}

function New-BlastEmKeyboardInputInternal {
    param(
        [Parameter(Mandatory = $true)][uint16]$VirtualKey,
        [Parameter(Mandatory = $false)][bool]$Extended = $false,
        [Parameter(Mandatory = $false)][bool]$KeyUp = $false
    )

    $scan = [SGDKBlastEmWin32]::MapVirtualKey([uint32]$VirtualKey, 0)
    $flags = [SGDKBlastEmWin32]::KEYEVENTF_SCANCODE
    if ($Extended) {
        $flags = $flags -bor [SGDKBlastEmWin32]::KEYEVENTF_EXTENDEDKEY
    }
    if ($KeyUp) {
        $flags = $flags -bor [SGDKBlastEmWin32]::KEYEVENTF_KEYUP
    }

    $input = New-Object "SGDKBlastEmWin32+INPUT"
    $input.type = [SGDKBlastEmWin32]::INPUT_KEYBOARD
    $input.u.ki.wVk = 0
    $input.u.ki.wScan = [uint16]$scan
    $input.u.ki.dwFlags = $flags
    $input.u.ki.time = 0
    $input.u.ki.dwExtraInfo = [IntPtr]::Zero
    return $input
}

function Get-BlastEmCandidateFilesInternal {
    param(
        [Parameter(Mandatory = $true)][string[]]$RootPaths
    )

    $candidates = @()
    foreach ($root in $RootPaths) {
        if ([string]::IsNullOrWhiteSpace($root) -or -not (Test-Path -LiteralPath $root)) {
            continue
        }

        $files = Get-ChildItem -LiteralPath $root -Recurse -File -ErrorAction SilentlyContinue | Where-Object {
            $_.Length -gt 0 -and (
                $_.Name -ieq "save.sram" -or
                $_.Extension -ieq ".sram" -or
                $_.Extension -ieq ".srm" -or
                $_.Extension -ieq ".sav"
            )
        }
        if ($files) {
            $candidates += $files
        }
    }

    return @($candidates | Sort-Object LastWriteTimeUtc -Descending | Select-Object -Property * -Unique)
}

function Test-BlastEmPathUnderRootInternal {
    param(
        [Parameter(Mandatory = $true)][string]$CandidatePath,
        [Parameter(Mandatory = $true)][string]$RootPath
    )

    if ([string]::IsNullOrWhiteSpace($RootPath)) {
        return $true
    }

    try {
        $normalizedCandidate = [System.IO.Path]::GetFullPath($CandidatePath).TrimEnd('\', '/')
        $normalizedRoot = [System.IO.Path]::GetFullPath($RootPath).TrimEnd('\', '/')
        $rootPrefix = $normalizedRoot + [System.IO.Path]::DirectorySeparatorChar
        return $normalizedCandidate.Equals($normalizedRoot, [System.StringComparison]::OrdinalIgnoreCase) -or
            $normalizedCandidate.StartsWith($rootPrefix, [System.StringComparison]::OrdinalIgnoreCase)
    }
    catch {
        return $false
    }
}

function Send-BlastEmAltF4Internal {
    param(
        [Parameter(Mandatory = $true)][System.Diagnostics.Process]$Process
    )

    Ensure-BlastEmForeground -Process $Process -MaxAttempts 3 | Out-Null

    $inputs = [array]::CreateInstance([type]"SGDKBlastEmWin32+INPUT", 4)
    $inputs.SetValue((New-BlastEmKeyboardInputInternal -VirtualKey 0x12), 0)
    $inputs.SetValue((New-BlastEmKeyboardInputInternal -VirtualKey 0x73), 1)
    $inputs.SetValue((New-BlastEmKeyboardInputInternal -VirtualKey 0x73 -KeyUp $true), 2)
    $inputs.SetValue((New-BlastEmKeyboardInputInternal -VirtualKey 0x12 -KeyUp $true), 3)

    $sent = [SGDKBlastEmWin32]::SendInput(4, $inputs, $script:BlastEmInputSize)
    if ($sent -ne 4) {
        $err = [System.Runtime.InteropServices.Marshal]::GetLastWin32Error()
        throw "SendInput Alt+F4 falhou (Win32=$err)."
    }
}

function Get-BlastEmKeyMap {
    return @{
        "up"    = @{ vk = 0x26; ext = $true  }
        "down"  = @{ vk = 0x28; ext = $true  }
        "left"  = @{ vk = 0x25; ext = $true  }
        "right" = @{ vk = 0x27; ext = $true  }
        "a"     = @{ vk = 0x41; ext = $false }
        "b"     = @{ vk = 0x53; ext = $false }
        "c"     = @{ vk = 0x44; ext = $false }
        "x"     = @{ vk = 0x51; ext = $false }
        "y"     = @{ vk = 0x57; ext = $false }
        "z"     = @{ vk = 0x45; ext = $false }
        "mode"  = @{ vk = 0x46; ext = $false }
        "start" = @{ vk = 0x0D; ext = $false }
        "esc"   = @{ vk = 0x1B; ext = $false }
    }
}

function Write-BlastEmCaptureLog {
    param(
        [Parameter(Mandatory = $false)][string]$LogPath,
        [Parameter(Mandatory = $true)][string]$Event,
        [Parameter(Mandatory = $false)][hashtable]$Data
    )

    if ([string]::IsNullOrWhiteSpace($LogPath)) {
        return
    }

    $parent = Split-Path -Parent $LogPath
    if ($parent -and -not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Force -Path $parent | Out-Null
    }

    $entry = [ordered]@{
        ts    = (Get-Date).ToString("o")
        event = $Event
    }
    if ($Data) {
        foreach ($key in $Data.Keys) {
            $entry[$key] = $Data[$key]
        }
    }

    try {
        $line = ($entry | ConvertTo-Json -Compress -Depth 8)
        Add-Content -LiteralPath $LogPath -Value $line -Encoding UTF8
    }
    catch {
        # logging never breaks capture
    }
}

function Ensure-BlastEmForeground {
    param(
        [Parameter(Mandatory = $true)][System.Diagnostics.Process]$Process,
        [Parameter(Mandatory = $false)][int]$MaxAttempts = 6
    )

    Ensure-BlastEmAutomationLoaded

    $Process.Refresh()
    if ($Process.MainWindowHandle -eq [IntPtr]::Zero) {
        throw "BlastEm nao expos janela para navegacao automatica."
    }

    $hwnd = $Process.MainWindowHandle
    for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
        [SGDKBlastEmWin32]::ShowWindow($hwnd, 9) | Out-Null
        [SGDKBlastEmWin32]::BringWindowToTop($hwnd) | Out-Null

        $currentThread = [SGDKBlastEmWin32]::GetCurrentThreadId()
        $fgHandle = [SGDKBlastEmWin32]::GetForegroundWindow()
        $fgProc = [uint32]0
        $fgThread = [uint32]0
        if ($fgHandle -ne [IntPtr]::Zero) {
            $fgThread = [SGDKBlastEmWin32]::GetWindowThreadProcessId($fgHandle, [ref]$fgProc)
        }

        $attached = $false
        if ($fgThread -ne 0 -and $fgThread -ne $currentThread) {
            $attached = [SGDKBlastEmWin32]::AttachThreadInput($currentThread, $fgThread, $true)
        }
        try {
            [SGDKBlastEmWin32]::SetForegroundWindow($hwnd) | Out-Null
        }
        finally {
            if ($attached) {
                [SGDKBlastEmWin32]::AttachThreadInput($currentThread, $fgThread, $false) | Out-Null
            }
        }

        Start-Sleep -Milliseconds 140
        if ([SGDKBlastEmWin32]::GetForegroundWindow() -eq $hwnd) {
            return $true
        }
    }

    return $false
}

function Send-BlastEmKey {
    param(
        [Parameter(Mandatory = $true)][System.Diagnostics.Process]$Process,
        [Parameter(Mandatory = $true)][uint16]$VirtualKey,
        [Parameter(Mandatory = $false)][bool]$Extended = $false,
        [Parameter(Mandatory = $false)][int]$HoldMilliseconds = 70
    )

    Ensure-BlastEmAutomationLoaded

    $Process.Refresh()
    if ($Process.HasExited) {
        throw "BlastEm encerrou antes do envio de tecla."
    }

    Ensure-BlastEmForeground -Process $Process | Out-Null

    $inputDown = New-BlastEmKeyboardInputInternal -VirtualKey $VirtualKey -Extended $Extended
    $inputUp = New-BlastEmKeyboardInputInternal -VirtualKey $VirtualKey -Extended $Extended -KeyUp $true

    $arrDown = [array]::CreateInstance([type]"SGDKBlastEmWin32+INPUT", 1)
    $arrDown.SetValue($inputDown, 0)
    $arrUp = [array]::CreateInstance([type]"SGDKBlastEmWin32+INPUT", 1)
    $arrUp.SetValue($inputUp, 0)

    $sent = [SGDKBlastEmWin32]::SendInput(1, $arrDown, $script:BlastEmInputSize)
    if ($sent -ne 1) {
        $err = [System.Runtime.InteropServices.Marshal]::GetLastWin32Error()
        throw "SendInput KEYDOWN falhou (Win32=$err, vk=$VirtualKey)."
    }

    Start-Sleep -Milliseconds $HoldMilliseconds

    $sent = [SGDKBlastEmWin32]::SendInput(1, $arrUp, $script:BlastEmInputSize)
    if ($sent -ne 1) {
        $err = [System.Runtime.InteropServices.Marshal]::GetLastWin32Error()
        throw "SendInput KEYUP falhou (Win32=$err, vk=$VirtualKey)."
    }
}

function Save-BlastEmWindowScreenshot {
    param(
        [Parameter(Mandatory = $true)][System.Diagnostics.Process]$Process,
        [Parameter(Mandatory = $true)][string]$OutputPath
    )

    Ensure-BlastEmAutomationLoaded

    try {
        $Process.Refresh()
        if ($Process.HasExited) { return $false }
        if ($Process.MainWindowHandle -eq [IntPtr]::Zero) { return $false }

        $rect = New-Object "SGDKBlastEmWin32+RECT"
        if (-not [SGDKBlastEmWin32]::GetWindowRect($Process.MainWindowHandle, [ref]$rect)) {
            return $false
        }

        $width = $rect.Right - $rect.Left
        $height = $rect.Bottom - $rect.Top
        if ($width -le 0 -or $height -le 0) {
            return $false
        }

        $parent = Split-Path -Parent $OutputPath
        if ($parent -and -not (Test-Path -LiteralPath $parent)) {
            New-Item -ItemType Directory -Force -Path $parent | Out-Null
        }

        $bitmap = New-Object System.Drawing.Bitmap $width, $height
        try {
            $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
            try {
                $hdc = $graphics.GetHdc()
                $printed = $false
                try {
                    $printed = [SGDKBlastEmWin32]::PrintWindow($Process.MainWindowHandle, $hdc, 0)
                }
                finally {
                    $graphics.ReleaseHdc($hdc)
                }

                if (-not $printed) {
                    $graphics.CopyFromScreen($rect.Left, $rect.Top, 0, 0, $bitmap.Size)
                }
            }
            finally {
                $graphics.Dispose()
            }

            $bitmap.Save($OutputPath, [System.Drawing.Imaging.ImageFormat]::Png)
            return $true
        }
        finally {
            $bitmap.Dispose()
        }
    }
    catch {
        return $false
    }
}

function Write-BlastEmConfig {
    param(
        [Parameter(Mandatory = $true)][string]$BaseConfigPath,
        [Parameter(Mandatory = $true)][string]$TargetConfigPath,
        [Parameter(Mandatory = $true)][string]$SaveRoot,
        [Parameter(Mandatory = $false)][string]$ScreenshotRoot = ""
    )

    if (-not (Test-Path -LiteralPath $BaseConfigPath)) {
        throw "default.cfg base nao existe: $BaseConfigPath"
    }

    $content = Get-Content -LiteralPath $BaseConfigPath -Raw
    if ([string]::IsNullOrWhiteSpace($content)) {
        throw "default.cfg base ausente ou vazio: $BaseConfigPath"
    }

    $normalizedSave = $SaveRoot.Replace("\", "/").TrimEnd("/")
    $uiLines = @("`tsave_path $normalizedSave/`$ROMNAME")

    $rewritten = [System.Text.RegularExpressions.Regex]::Replace(
        $content,
        '(?m)^[ \t]*save_path[ \t]+[^\r\n]*\r?\n?',
        ''
    )

    if (-not [string]::IsNullOrWhiteSpace($ScreenshotRoot)) {
        $normalizedScreenshot = $ScreenshotRoot.Replace("\", "/").TrimEnd("/")
        $uiLines = @("`tscreenshot_path $normalizedScreenshot") + $uiLines
        $rewritten = [System.Text.RegularExpressions.Regex]::Replace(
            $rewritten,
            '(?m)^[ \t]*screenshot_path[ \t]+[^\r\n]*\r?\n?',
            ''
        )
    }

    $uiInsertion = ($uiLines -join "`r`n") + "`r`n"
    $uiBlockPattern = '(?m)^ui\s*\{\r?\n'
    if (-not [System.Text.RegularExpressions.Regex]::IsMatch($rewritten, $uiBlockPattern)) {
        throw "Write-BlastEmConfig: bloco 'ui {' nao encontrado no default.cfg"
    }

    $finalContent = [System.Text.RegularExpressions.Regex]::Replace(
        $rewritten,
        $uiBlockPattern,
        {
            param($match)
            return $match.Value + $uiInsertion
        },
        1
    )

    $savePathMatches = [System.Text.RegularExpressions.Regex]::Matches(
        $finalContent,
        '(?m)^[ \t]*save_path[ \t]+'
    )
    if ($savePathMatches.Count -ne 1) {
        throw ("Write-BlastEmConfig: esperado 1 save_path, encontrei " + $savePathMatches.Count + " apos reescrita.")
    }

    if (-not [string]::IsNullOrWhiteSpace($ScreenshotRoot)) {
        $screenshotPathMatches = [System.Text.RegularExpressions.Regex]::Matches(
            $finalContent,
            '(?m)^[ \t]*screenshot_path[ \t]+'
        )
        if ($screenshotPathMatches.Count -ne 1) {
            throw ("Write-BlastEmConfig: esperado 1 screenshot_path, encontrei " + $screenshotPathMatches.Count + " apos reescrita.")
        }
    }

    $configDir = Split-Path -Parent $TargetConfigPath
    New-Item -ItemType Directory -Force -Path $configDir | Out-Null
    Set-Content -LiteralPath $TargetConfigPath -Value $finalContent -Encoding UTF8
}

function Close-BlastEmGracefully {
    param(
        [Parameter(Mandatory = $true)][System.Diagnostics.Process]$Process,
        [Parameter(Mandatory = $true)][string]$LogPath,
        [Parameter(Mandatory = $false)][int]$EscWaitMs = 4000,
        [Parameter(Mandatory = $false)][int]$CloseWaitMs = 5000,
        [Parameter(Mandatory = $false)][int]$AltF4WaitMs = 3000,
        [Parameter(Mandatory = $false)][int]$InputIdleMs = 2000
    )

    if ($Process.HasExited) {
        Write-BlastEmCaptureLog -LogPath $LogPath -Event "close_skip_already_exited" -Data @{
            exit_code = $Process.ExitCode
        }
        return @{ exit_mode = "already_exited"; forced = $false }
    }

    try {
        $idle = $Process.WaitForInputIdle($InputIdleMs)
        Write-BlastEmCaptureLog -LogPath $LogPath -Event "close_input_idle" -Data @{ reached_idle = [bool]$idle }
    }
    catch {
        Write-BlastEmCaptureLog -LogPath $LogPath -Event "close_input_idle_error" -Data @{
            message = $_.Exception.Message
        }
    }

    $fg = Ensure-BlastEmForeground -Process $Process -MaxAttempts 4
    Write-BlastEmCaptureLog -LogPath $LogPath -Event "close_foreground" -Data @{ success = [bool]$fg }

    try {
        Send-BlastEmKey -Process $Process -VirtualKey 0x1B -Extended $false -HoldMilliseconds 90
        Write-BlastEmCaptureLog -LogPath $LogPath -Event "close_esc_sent"
    }
    catch {
        Write-BlastEmCaptureLog -LogPath $LogPath -Event "close_esc_error" -Data @{
            message = $_.Exception.Message
        }
    }

    if ($Process.WaitForExit($EscWaitMs)) {
        Write-BlastEmCaptureLog -LogPath $LogPath -Event "close_exit_via_esc" -Data @{
            exit_code = $Process.ExitCode
        }
        return @{ exit_mode = "esc"; forced = $false }
    }

    try {
        $closeOk = $Process.CloseMainWindow()
        Write-BlastEmCaptureLog -LogPath $LogPath -Event "close_main_window_sent" -Data @{ posted = [bool]$closeOk }
    }
    catch {
        Write-BlastEmCaptureLog -LogPath $LogPath -Event "close_main_window_error" -Data @{
            message = $_.Exception.Message
        }
    }

    if ($Process.WaitForExit($CloseWaitMs)) {
        Write-BlastEmCaptureLog -LogPath $LogPath -Event "close_exit_via_wm_close" -Data @{
            exit_code = $Process.ExitCode
        }
        return @{ exit_mode = "wm_close"; forced = $false }
    }

    try {
        Send-BlastEmAltF4Internal -Process $Process
        Write-BlastEmCaptureLog -LogPath $LogPath -Event "close_alt_f4_sent"
    }
    catch {
        Write-BlastEmCaptureLog -LogPath $LogPath -Event "close_alt_f4_error" -Data @{
            message = $_.Exception.Message
        }
    }

    if ($Process.WaitForExit($AltF4WaitMs)) {
        Write-BlastEmCaptureLog -LogPath $LogPath -Event "close_exit_via_alt_f4" -Data @{
            exit_code = $Process.ExitCode
        }
        return @{ exit_mode = "alt_f4"; forced = $false }
    }

    try {
        Stop-Process -Id $Process.Id -Force -ErrorAction Stop
    }
    catch {
        Write-BlastEmCaptureLog -LogPath $LogPath -Event "close_kill_error" -Data @{
            message = $_.Exception.Message
        }
    }

    $Process.WaitForExit()
    Write-BlastEmCaptureLog -LogPath $LogPath -Event "close_force_killed" -Data @{
        exit_code = $Process.ExitCode
    }
    return @{ exit_mode = "force_kill"; forced = $true }
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

function Test-MDReadyHeartbeat {
    param(
        [Parameter(Mandatory = $true)][string]$SramPath,
        [Parameter(Mandatory = $false)][int]$Offset = 0x100
    )

    try {
        $bytes = [System.IO.File]::ReadAllBytes($SramPath)
        if ($bytes.Length -lt ($Offset + 5)) {
            return $false
        }
        return ([System.Text.Encoding]::ASCII.GetString($bytes, $Offset, 5) -eq "READY")
    }
    catch {
        return $false
    }
}

function Test-FreshSramCandidate {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $false)][datetime]$ProcessStartedAtUtc = ([datetime]::MinValue),
        [Parameter(Mandatory = $false)][string]$SandboxRoot = ""
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $false
    }

    try {
        $item = Get-Item -LiteralPath $Path
        if ($item.Length -le 0) {
            return $false
        }

        if (-not [string]::IsNullOrWhiteSpace($SandboxRoot)) {
            if (-not (Test-BlastEmPathUnderRootInternal -CandidatePath $item.FullName -RootPath $SandboxRoot)) {
                return $false
            }
        }

        if ($ProcessStartedAtUtc -gt [datetime]::MinValue) {
            if ($item.LastWriteTimeUtc -lt $ProcessStartedAtUtc) {
                return $false
            }
        }

        return $true
    }
    catch {
        return $false
    }
}

function Find-FirstSramWithReady {
    param(
        [Parameter(Mandatory = $true)][string[]]$RootPaths,
        [Parameter(Mandatory = $false)][int]$HeartbeatOffset = 0x100,
        [Parameter(Mandatory = $false)][datetime]$ProcessStartedAtUtc = ([datetime]::MinValue),
        [Parameter(Mandatory = $false)][string]$SandboxRoot = ""
    )

    foreach ($candidate in (Get-BlastEmCandidateFilesInternal -RootPaths $RootPaths)) {
        if (-not (Test-FreshSramCandidate -Path $candidate.FullName -ProcessStartedAtUtc $ProcessStartedAtUtc -SandboxRoot $SandboxRoot)) {
            continue
        }
        if (Test-MDReadyHeartbeat -SramPath $candidate.FullName -Offset $HeartbeatOffset) {
            return $candidate.FullName
        }
    }

    return $null
}

function Find-FirstSramWithSignature {
    param(
        [Parameter(Mandatory = $true)][string[]]$RootPaths,
        [Parameter(Mandatory = $false)][int]$SramOffset = 0x200,
        [Parameter(Mandatory = $false)][datetime]$ProcessStartedAtUtc = ([datetime]::MinValue),
        [Parameter(Mandatory = $false)][string]$SandboxRoot = ""
    )

    foreach ($candidate in (Get-BlastEmCandidateFilesInternal -RootPaths $RootPaths)) {
        if (-not (Test-FreshSramCandidate -Path $candidate.FullName -ProcessStartedAtUtc $ProcessStartedAtUtc -SandboxRoot $SandboxRoot)) {
            continue
        }
        if (Test-MDRTRuntimeSignature -SramPath $candidate.FullName -Offset $SramOffset) {
            return $candidate.FullName
        }
    }

    return $null
}

function Start-BlastEmSaveWatchers {
    param(
        [Parameter(Mandatory = $true)][string[]]$RootPaths
    )

    $watchers = @()
    foreach ($root in $RootPaths) {
        if ([string]::IsNullOrWhiteSpace($root)) { continue }
        if (-not (Test-Path -LiteralPath $root -PathType Container)) { continue }

        $fsw = New-Object System.IO.FileSystemWatcher
        $fsw.Path = (Resolve-Path -LiteralPath $root).Path
        $fsw.IncludeSubdirectories = $true
        $fsw.Filter = "*.*"
        $fsw.NotifyFilter = ([System.IO.NotifyFilters]::LastWrite -bor [System.IO.NotifyFilters]::FileName -bor [System.IO.NotifyFilters]::Size)
        $fsw.EnableRaisingEvents = $true
        $watchers += $fsw
    }
    return @($watchers)
}

function Stop-BlastEmSaveWatchers {
    param(
        [Parameter(Mandatory = $false)][object[]]$Watchers
    )

    if (-not $Watchers) { return }
    foreach ($w in $Watchers) {
        if (-not $w) { continue }
        try {
            $w.EnableRaisingEvents = $false
            $w.Dispose()
        } catch {
            # silencia: teardown de watcher nunca pode quebrar o caminho feliz
        }
    }
}

function Wait-ForSramChangeOrDeadline {
    param(
        [Parameter(Mandatory = $false)][AllowNull()][object[]]$Watchers = @(),
        [Parameter(Mandatory = $true)][datetime]$DeadlineUtc,
        [Parameter(Mandatory = $false)][int]$PollIntervalMs = 400
    )

    $remainingMs = ($DeadlineUtc - [datetime]::UtcNow).TotalMilliseconds
    if ($remainingMs -le 0) {
        return "deadline"
    }

    $cappedInterval = [Math]::Max(1, $PollIntervalMs)
    $waitMs = [int]([Math]::Min($remainingMs, $cappedInterval))
    if ($waitMs -lt 1) { $waitMs = 1 }

    $watcherCount = 0
    if ($Watchers) { $watcherCount = @($Watchers).Count }

    if ($watcherCount -eq 0) {
        # Backstop de polling: sem FSW ativo ainda respeitamos o intervalo
        # para nao degenerar em hot-loop no caller.
        Start-Sleep -Milliseconds $waitMs
        return "poll_tick"
    }

    foreach ($w in $Watchers) {
        if (-not $w) { continue }
        try {
            $result = $w.WaitForChanged([System.IO.WatcherChangeTypes]::All, $waitMs)
            if (-not $result.TimedOut) {
                return "fsw_event"
            }
        } catch {
            # cai no polling backstop
        }
    }
    return "poll_tick"
}

function Invoke-BlastEmFlushCycle {
    param(
        [Parameter(Mandatory = $true)][System.Diagnostics.Process]$Process,
        [Parameter(Mandatory = $false)][string]$LogPath
    )

    <#
    BlastEm tends to flush SRAM to disk on pause/unpause and on certain UI
    transitions. This helper sends ESC -> wait -> ESC again, asking the emu
    to pause and resume without user interaction. The effect: any pending
    SRAM buffered in-memory lands on the sandbox save_path so the wrapper
    detection layer can observe it within the current `press_until_ready`
    iteration instead of waiting for the next natural flush.
    #>
    try {
        Send-BlastEmKey -Process $Process -VirtualKey 0x1B -Extended $false -HoldMilliseconds 60
        Start-Sleep -Milliseconds 220
        Send-BlastEmKey -Process $Process -VirtualKey 0x1B -Extended $false -HoldMilliseconds 60
        Write-BlastEmCaptureLog -LogPath $LogPath -Event "nav_flush_cycle"
    }
    catch {
        Write-BlastEmCaptureLog -LogPath $LogPath -Event "nav_flush_cycle_error" -Data @{
            message = $_.Exception.Message
        }
    }
}

function Invoke-BlastEmNavigation {
    param(
        [Parameter(Mandatory = $true)][System.Diagnostics.Process]$Process,
        [Parameter(Mandatory = $true)][string[]]$Sequence,
        [Parameter(Mandatory = $false)][string]$LogPath,
        [Parameter(Mandatory = $false)][string[]]$SaveRoots = @(),
        [Parameter(Mandatory = $false)][int]$HeartbeatOffset = 0x100,
        [Parameter(Mandatory = $false)][datetime]$ProcessStartedAtUtc = ([datetime]::MinValue),
        [Parameter(Mandatory = $false)][string]$SandboxRoot = ""
    )

    if (-not $Sequence -or $Sequence.Count -eq 0) {
        Write-BlastEmCaptureLog -LogPath $LogPath -Event "nav_skip_empty"
        return
    }

    $keyMap = Get-BlastEmKeyMap
    $parseKv = {
        param([string[]]$parts)
        $kv = @{}
        for ($i = 1; $i -lt $parts.Length; $i++) {
            $segment = $parts[$i]
            if ($segment -match "^([a-z_]+)=(\d+)(ms)?$") {
                $kv[$matches[1]] = [int]$matches[2]
            }
        }
        return $kv
    }

    Write-BlastEmCaptureLog -LogPath $LogPath -Event "nav_begin" -Data @{
        steps = $Sequence.Count
        navigation_mode = "scan_code_sendinput"
        heartbeat_offset = ("0x{0:X}" -f $HeartbeatOffset)
        sandbox_root = $SandboxRoot
        save_roots = $SaveRoots
        window_title = $Process.MainWindowTitle
    }

    foreach ($rawStep in $Sequence) {
        if ($Process.HasExited) {
            Write-BlastEmCaptureLog -LogPath $LogPath -Event "nav_abort_process_exited"
            return
        }

        $step = $rawStep.Trim().ToLowerInvariant()
        if ([string]::IsNullOrWhiteSpace($step)) {
            continue
        }

        if ($step.StartsWith("wait:")) {
            $milliseconds = 0
            if (-not [int]::TryParse($step.Substring(5), [ref]$milliseconds) -or $milliseconds -lt 0) {
                throw "Passo de navegacao invalido: $rawStep"
            }
            Write-BlastEmCaptureLog -LogPath $LogPath -Event "nav_wait" -Data @{ ms = $milliseconds }
            Start-Sleep -Milliseconds $milliseconds
            continue
        }

        if ($step.StartsWith("mash:")) {
            $parts = $step.Substring(5).Split(",")
            $keyName = $parts[0]
            if (-not $keyMap.ContainsKey($keyName)) {
                throw "Tecla nao suportada em mash: $keyName"
            }
            $kv = & $parseKv $parts
            $count = if ($kv.ContainsKey("count")) { [int]$kv.count } else { 10 }
            $interval = if ($kv.ContainsKey("interval")) { [int]$kv.interval } else { 160 }
            $hold = if ($kv.ContainsKey("hold")) { [int]$kv.hold } else { 70 }
            $key = $keyMap[$keyName]
            Write-BlastEmCaptureLog -LogPath $LogPath -Event "nav_mash" -Data @{
                key = $keyName
                count = $count
                interval_ms = $interval
                hold_ms = $hold
            }
            for ($i = 0; $i -lt $count; $i++) {
                if ($Process.HasExited) { break }
                Send-BlastEmKey -Process $Process -VirtualKey $key.vk -Extended $key.ext -HoldMilliseconds $hold
                Start-Sleep -Milliseconds $interval
            }
            continue
        }

        if ($step.StartsWith("hold:")) {
            $parts = $step.Substring(5).Split(",")
            $keyName = $parts[0]
            if (-not $keyMap.ContainsKey($keyName)) {
                throw "Tecla nao suportada em hold: $keyName"
            }
            $kv = & $parseKv $parts
            $duration = if ($kv.ContainsKey("duration")) { [int]$kv.duration } else { 1000 }
            $key = $keyMap[$keyName]
            Write-BlastEmCaptureLog -LogPath $LogPath -Event "nav_hold" -Data @{
                key = $keyName
                duration_ms = $duration
            }
            Send-BlastEmKey -Process $Process -VirtualKey $key.vk -Extended $key.ext -HoldMilliseconds $duration
            Start-Sleep -Milliseconds 120
            continue
        }

        if ($step -eq "region_unlock") {
            $key = $keyMap["start"]
            Write-BlastEmCaptureLog -LogPath $LogPath -Event "nav_region_unlock"
            for ($i = 0; $i -lt 3; $i++) {
                if ($Process.HasExited) { break }
                Send-BlastEmKey -Process $Process -VirtualKey $key.vk -Extended $key.ext -HoldMilliseconds 80
                Start-Sleep -Milliseconds 850
            }
            continue
        }

        if ($step.StartsWith("press_until_ready:")) {
            $parts = $step.Substring(18).Split(",")
            $keyName = $parts[0]
            if (-not $keyMap.ContainsKey($keyName)) {
                throw "Tecla nao suportada em press_until_ready: $keyName"
            }

            $kv = & $parseKv $parts
            $timeout = if ($kv.ContainsKey("timeout_ms")) { [int]$kv.timeout_ms } else { 8000 }
            $interval = if ($kv.ContainsKey("interval_ms")) { [int]$kv.interval_ms } else { 400 }
            $hold = if ($kv.ContainsKey("hold")) { [int]$kv.hold } else { 80 }
            $maxPresses = if ($kv.ContainsKey("max_presses")) { [int]$kv.max_presses } else { 40 }
            $flushEvery = if ($kv.ContainsKey("flush_every")) { [int]$kv.flush_every } else { 8 }

            $rotateKey = $null
            foreach ($seg in $parts) {
                if ($seg -match "^rotate_key=([a-z_]+)$") {
                    $rotateKey = $matches[1]
                    break
                }
            }
            if ($rotateKey -and -not $keyMap.ContainsKey($rotateKey)) {
                throw "Tecla nao suportada em press_until_ready rotate_key: $rotateKey"
            }

            if (-not $SaveRoots -or $SaveRoots.Count -eq 0) {
                Write-BlastEmCaptureLog -LogPath $LogPath -Event "nav_press_until_ready_skip" -Data @{
                    key = $keyName
                    reason = "save_roots_ausente"
                }
                $degradeCount = [Math]::Max(1, [int]($timeout / [Math]::Max(100, $interval)))
                $key = $keyMap[$keyName]
                for ($i = 0; $i -lt $degradeCount; $i++) {
                    if ($Process.HasExited) { break }
                    Send-BlastEmKey -Process $Process -VirtualKey $key.vk -Extended $key.ext -HoldMilliseconds $hold
                    Start-Sleep -Milliseconds $interval
                }
                continue
            }

            $watchers = @(Start-BlastEmSaveWatchers -RootPaths $SaveRoots)
            $watcherCount = $watchers.Count
            Write-BlastEmCaptureLog -LogPath $LogPath -Event "nav_press_until_ready_begin" -Data @{
                key = $keyName
                timeout_ms = $timeout
                interval_ms = $interval
                hold_ms = $hold
                max_presses = $maxPresses
                flush_every = $flushEvery
                rotate_key = $rotateKey
                heartbeat_offset = ("0x{0:X}" -f $HeartbeatOffset)
                ready_probe_source = "sram_ready_heartbeat"
                fsw_watchers = $watcherCount
                detection_mode = if ($watcherCount -gt 0) { "fsw_fastpath_with_polling_backstop" } else { "polling_only" }
            }

            $readyPath = $null
            $totalPresses = 0
            $rotations = @()
            $attempts = @($keyName)
            if ($rotateKey) { $attempts += $rotateKey }

            try {
                foreach ($attemptKeyName in $attempts) {
                    if ($readyPath) { break }
                    if ($Process.HasExited) { break }

                    $attemptKey = $keyMap[$attemptKeyName]
                    $attemptDeadlineUtc = [datetime]::UtcNow.AddMilliseconds($timeout)
                    $attemptPresses = 0
                    $isRotation = ($attemptKeyName -ne $keyName)
                    if ($isRotation) {
                        Write-BlastEmCaptureLog -LogPath $LogPath -Event "nav_press_until_ready_rotation" -Data @{
                            from_key = $keyName
                            to_key = $attemptKeyName
                        }
                        $rotations += $attemptKeyName
                    }

                    while ([datetime]::UtcNow -lt $attemptDeadlineUtc -and $attemptPresses -lt $maxPresses) {
                        if ($Process.HasExited) {
                            Write-BlastEmCaptureLog -LogPath $LogPath -Event "nav_press_until_ready_abort" -Data @{
                                reason = "process_exited"
                                presses = $totalPresses
                            }
                            break
                        }

                        Send-BlastEmKey -Process $Process -VirtualKey $attemptKey.vk -Extended $attemptKey.ext -HoldMilliseconds $hold
                        $attemptPresses++
                        $totalPresses++

                        if ($flushEvery -gt 0 -and ($attemptPresses % $flushEvery) -eq 0) {
                            Invoke-BlastEmFlushCycle -Process $Process -LogPath $LogPath
                        }

                        $signal = Wait-ForSramChangeOrDeadline -Watchers $watchers -DeadlineUtc $attemptDeadlineUtc -PollIntervalMs $interval

                        $readyPath = Find-FirstSramWithReady `
                            -RootPaths $SaveRoots `
                            -HeartbeatOffset $HeartbeatOffset `
                            -ProcessStartedAtUtc $ProcessStartedAtUtc `
                            -SandboxRoot $SandboxRoot
                        if ($readyPath) {
                            Write-BlastEmCaptureLog -LogPath $LogPath -Event "nav_press_until_ready_signal" -Data @{
                                key = $attemptKeyName
                                attempt_presses = $attemptPresses
                                total_presses = $totalPresses
                                signal = $signal
                                sram_path = $readyPath
                            }
                            break
                        }
                    }

                    if (-not $readyPath) {
                        Write-BlastEmCaptureLog -LogPath $LogPath -Event "nav_press_until_ready_attempt_timeout" -Data @{
                            key = $attemptKeyName
                            attempt_presses = $attemptPresses
                            total_presses = $totalPresses
                            elapsed_ms = $timeout
                        }
                    }
                }
            }
            finally {
                Stop-BlastEmSaveWatchers -Watchers $watchers
            }

            if ($readyPath) {
                Write-BlastEmCaptureLog -LogPath $LogPath -Event "nav_press_until_ready_ok" -Data @{
                    key = $keyName
                    presses = $totalPresses
                    rotations = $rotations
                    sram_path = $readyPath
                    ready_probe_source = "sram_ready_heartbeat"
                }
            }
            else {
                Write-BlastEmCaptureLog -LogPath $LogPath -Event "nav_press_until_ready_timeout" -Data @{
                    key = $keyName
                    presses = $totalPresses
                    rotations = $rotations
                    elapsed_ms = $timeout
                    ready_probe_source = "sram_ready_heartbeat"
                }
            }
            continue
        }

        if (-not $keyMap.ContainsKey($step)) {
            throw "Tecla de navegacao nao suportada: $rawStep"
        }

        $key = $keyMap[$step]
        Write-BlastEmCaptureLog -LogPath $LogPath -Event "nav_press" -Data @{ key = $step }
        Send-BlastEmKey -Process $Process -VirtualKey $key.vk -Extended $key.ext -HoldMilliseconds 80
        Start-Sleep -Milliseconds 200
    }

    Write-BlastEmCaptureLog -LogPath $LogPath -Event "nav_end"
}

Export-ModuleMember -Function @(
    'Ensure-BlastEmAutomationLoaded',
    'Ensure-BlastEmForeground',
    'Send-BlastEmKey',
    'Get-BlastEmKeyMap',
    'Write-BlastEmCaptureLog',
    'Save-BlastEmWindowScreenshot',
    'Write-BlastEmConfig',
    'Close-BlastEmGracefully',
    'Test-MDRTRuntimeSignature',
    'Test-MDReadyHeartbeat',
    'Find-FirstSramWithSignature',
    'Find-FirstSramWithReady',
    'Test-FreshSramCandidate',
    'Invoke-BlastEmNavigation'
)
