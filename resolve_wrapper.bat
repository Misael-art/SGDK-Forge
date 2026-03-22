@echo off
REM =========================================================================
REM resolve_wrapper.bat - Resolve a vendored or workspace SGDK wrapper
REM =========================================================================
setlocal

set "SGDK_WRAPPER_ROOT="

if exist "%~dp0tools\sgdk_wrapper\build.bat" if exist "%~dp0tools\sgdk_wrapper\prepare_assets.py" for %%I in ("%~dp0tools\sgdk_wrapper") do set "SGDK_WRAPPER_ROOT=%%~fI"
if not defined SGDK_WRAPPER_ROOT if exist "%~dp0..\build.bat" if exist "%~dp0..\prepare_assets.py" for %%I in ("%~dp0..") do set "SGDK_WRAPPER_ROOT=%%~fI"
if not defined SGDK_WRAPPER_ROOT if exist "%~dp0..\..\tools\sgdk_wrapper\build.bat" for %%I in ("%~dp0..\..\tools\sgdk_wrapper") do set "SGDK_WRAPPER_ROOT=%%~fI"
if not defined SGDK_WRAPPER_ROOT if exist "%~dp0..\..\..\tools\sgdk_wrapper\build.bat" for %%I in ("%~dp0..\..\..\tools\sgdk_wrapper") do set "SGDK_WRAPPER_ROOT=%%~fI"

if not defined SGDK_WRAPPER_ROOT (
    echo [ERROR] Could not locate tools\sgdk_wrapper from %~dp0
    echo [ERROR] Expected one of:
    echo [ERROR] - %~dp0tools\sgdk_wrapper
    echo [ERROR] - a parent workspace containing tools\sgdk_wrapper
    endlocal & exit /b 1
)

endlocal & set "SGDK_WRAPPER_ROOT=%SGDK_WRAPPER_ROOT%" & exit /b 0
