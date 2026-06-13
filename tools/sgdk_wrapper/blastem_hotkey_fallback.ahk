#Requires AutoHotkey v2.0
#SingleInstance Force

if A_Args.Length < 2
    ExitApp 64

pid := A_Args[1]
action := A_Args[2]
target := "ahk_pid " pid " ahk_class SDL_app"
key := ""

if (action = "screenshot")
    key := "{F11}"
else if (action = "quicksave")
    key := "{F12}"
else if (action = "quit")
    key := "{Esc}"
else
    ExitApp 65

if !WinExist(target)
    ExitApp 2

WinActivate target
WinWaitActive target, , 2
Send key
Sleep 150
ExitApp 0
