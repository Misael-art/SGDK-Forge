[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [int]$ProcessId,

    [Parameter(Mandatory = $true)]
    [ValidateSet("screenshot", "quicksave", "quit")]
    [string]$Action,

    [int]$DelayAfterMs = 120
)

$ErrorActionPreference = "Stop"

Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

public static class BlastEmHotkeyNative
{
    [DllImport("user32.dll")]
    public static extern bool PostMessage(IntPtr hWnd, uint msg, IntPtr wParam, IntPtr lParam);

    [DllImport("user32.dll")]
    public static extern uint MapVirtualKey(uint code, uint mapType);
}
"@

function Get-VirtualKeyForAction {
    param([Parameter(Mandatory = $true)][string]$RequestedAction)

    switch ($RequestedAction) {
        "screenshot" { return 0x7A } # F11
        "quicksave"  { return 0x7B } # F12
        "quit"       { return 0x1B } # ESC
        default      { throw "Acao nao suportada: $RequestedAction" }
    }
}

function Send-WindowKey {
    param(
        [Parameter(Mandatory = $true)][IntPtr]$WindowHandle,
        [Parameter(Mandatory = $true)][uint32]$VirtualKey
    )

    $WM_KEYDOWN = 0x100
    $WM_KEYUP = 0x101
    $scanCode = [BlastEmHotkeyNative]::MapVirtualKey($VirtualKey, 0)
    $downLParam = [intptr](1 -bor ($scanCode -shl 16))
    $upLParam = [intptr](1 -bor ($scanCode -shl 16) -bor (1 -shl 30) -bor (1 -shl 31))

    if (-not [BlastEmHotkeyNative]::PostMessage($WindowHandle, $WM_KEYDOWN, [intptr]$VirtualKey, $downLParam)) {
        throw "Falha ao postar WM_KEYDOWN para a janela do BlastEm."
    }

    Start-Sleep -Milliseconds 80

    if (-not [BlastEmHotkeyNative]::PostMessage($WindowHandle, $WM_KEYUP, [intptr]$VirtualKey, $upLParam)) {
        throw "Falha ao postar WM_KEYUP para a janela do BlastEm."
    }
}

$process = Get-Process -Id $ProcessId -ErrorAction Stop
$process.Refresh()
if ($process.HasExited) {
    throw "Processo $ProcessId ja encerrou."
}
if ($process.MainWindowHandle -eq 0) {
    throw "Processo $ProcessId nao expôs MainWindowHandle."
}

$virtualKey = Get-VirtualKeyForAction -RequestedAction $Action
Send-WindowKey -WindowHandle ([intptr]$process.MainWindowHandle) -VirtualKey $virtualKey
Start-Sleep -Milliseconds $DelayAfterMs

[pscustomobject]@{
    process_id = $ProcessId
    action = $Action
    method = "native-postmessage"
    main_window_title = $process.MainWindowTitle
} | ConvertTo-Json -Depth 4
