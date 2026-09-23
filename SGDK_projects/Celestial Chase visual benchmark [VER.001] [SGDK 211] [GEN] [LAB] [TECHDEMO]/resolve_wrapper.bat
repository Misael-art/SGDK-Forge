@echo off
set "SGDK_WRAPPER_ROOT=%~dp0..\..\tools\sgdk_wrapper"
for %%I in ("%SGDK_WRAPPER_ROOT%") do set "SGDK_WRAPPER_ROOT=%%~fI"
if not exist "%SGDK_WRAPPER_ROOT%\build.bat" (
    echo [ERROR] Nao foi possivel localizar tools\sgdk_wrapper a partir de %~dp0
    exit /b 1
)

exit /b 0

