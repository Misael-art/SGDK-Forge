@echo off
REM =========================================================================
REM build.bat - Delegacao canonica para tools\\sgdk_wrapper
REM NUNCA adicione logica aqui. Centralize no wrapper.
REM =========================================================================
setlocal EnableExtensions EnableDelayedExpansion
set "SGDK_LOCAL_ENV=%~dp0sgdk_wrapper_env.bat"
if exist "!SGDK_LOCAL_ENV!" call "!SGDK_LOCAL_ENV!"
set "SGDK_PROJECT_ROOT=%~dp0."
for %%I in ("!SGDK_PROJECT_ROOT!") do set "SGDK_PROJECT_ROOT=%%~fI"
set "SGDK_WRAPPER_BUILD=%~dp0..\..\..\tools\sgdk_wrapper\build.bat"
for %%I in ("!SGDK_WRAPPER_BUILD!") do set "SGDK_WRAPPER_BUILD=%%~fI"
if not exist "!SGDK_WRAPPER_BUILD!" (
    echo [ERROR] Nao foi possivel localizar tools\sgdk_wrapper\build.bat a partir de %~dp0
    exit /b 1
)
call "!SGDK_WRAPPER_BUILD!" "!SGDK_PROJECT_ROOT!"
set "SGDK_WRAPPER_RC=!ERRORLEVEL!"
exit /b !SGDK_WRAPPER_RC!
