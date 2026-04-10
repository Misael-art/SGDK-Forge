If $CmdLine[0] < 2 Then Exit 64

Local $pid = $CmdLine[1]
Local $action = $CmdLine[2]
Local $title = "[CLASS:SDL_app; PID:" & $pid & "]"
Local $key = ""

If $action = "screenshot" Then
    $key = "{F11}"
ElseIf $action = "quicksave" Then
    $key = "{F12}"
ElseIf $action = "quit" Then
    $key = "{ESC}"
Else
    Exit 65
EndIf

If Not WinExists($title) Then Exit 2

WinActivate($title)
If Not WinWaitActive($title, "", 2) Then Exit 3

Send($key)
Sleep(150)
Exit 0
