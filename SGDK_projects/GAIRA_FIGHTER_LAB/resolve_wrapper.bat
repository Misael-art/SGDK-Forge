@echo off
set "SGDK_WRAPPER_ROOT="

if exist "%~dp0..\build.bat" if exist "%~dp0..\prepare_assets.py" set "SGDK_WRAPPER_ROOT=%~dp0.."
if not defined SGDK_WRAPPER_ROOT if exist "%~dp0..\..\tools\sgdk_wrapper\build.bat" set "SGDK_WRAPPER_ROOT=%~dp0..\..\tools\sgdk_wrapper"
if not defined SGDK_WRAPPER_ROOT if exist "%~dp0..\..\..\tools\sgdk_wrapper\build.bat" set "SGDK_WRAPPER_ROOT=%~dp0..\..\..\tools\sgdk_wrapper"

if not defined SGDK_WRAPPER_ROOT (
    echo [ERROR] Nao foi possivel localizar tools\sgdk_wrapper a partir de %~dp0
    exit /b 1
)

exit /b 0
