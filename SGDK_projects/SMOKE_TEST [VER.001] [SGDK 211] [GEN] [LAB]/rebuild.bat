@echo off
REM =========================================================================
REM rebuild.bat - Delegacao canonica para tools\\sgdk_wrapper
REM NUNCA adicione logica aqui. Centralize no wrapper.
REM =========================================================================
setlocal EnableExtensions EnableDelayedExpansion
set "SGDK_LOCAL_ENV=%~dp0sgdk_wrapper_env.bat"
if exist "!SGDK_LOCAL_ENV!" call "!SGDK_LOCAL_ENV!"
set "SGDK_PROJECT_ROOT=%~dp0."
for %%I in ("!SGDK_PROJECT_ROOT!") do set "SGDK_PROJECT_ROOT=%%~fI"
set "SGDK_WRAPPER_REBUILD=%~dp0..\..\tools\sgdk_wrapper\rebuild.bat"
for %%I in ("!SGDK_WRAPPER_REBUILD!") do set "SGDK_WRAPPER_REBUILD=%%~fI"
if not exist "!SGDK_WRAPPER_REBUILD!" (
    echo [ERROR] Nao foi possivel localizar tools\sgdk_wrapper\rebuild.bat a partir de %~dp0
    exit /b 1
)
powershell -NoProfile -ExecutionPolicy Bypass -Command "& $env:SGDK_WRAPPER_REBUILD $env:SGDK_PROJECT_ROOT; exit $LASTEXITCODE"
set "SGDK_WRAPPER_RC=!ERRORLEVEL!"
exit /b !SGDK_WRAPPER_RC!
