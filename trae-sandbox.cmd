@echo off
setlocal EnableExtensions

set "CMD=%~1"
if "%CMD%"=="" set "CMD=%*"

cmd.exe /d /s /c %CMD%
exit /b %ERRORLEVEL%
