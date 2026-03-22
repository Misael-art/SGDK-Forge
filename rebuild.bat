@echo off
REM =========================================================================
REM rebuild.bat - Delegacao canonica para tools\\sgdk_wrapper
REM NUNCA adicione logica aqui. Centralize no wrapper.
REM =========================================================================
setlocal
set "SGDK_LOCAL_ENV=%~dp0sgdk_wrapper_env.bat"
if exist "%SGDK_LOCAL_ENV%" call "%SGDK_LOCAL_ENV%"
set "SGDK_PROJECT_ROOT=%~dp0."
for %%I in ("%SGDK_PROJECT_ROOT%") do set "SGDK_PROJECT_ROOT=%%~fI"
set "SGDK_WRAPPER_ROOT="
if exist "%~dp0tools\sgdk_wrapper\rebuild.bat" if exist "%~dp0tools\sgdk_wrapper\prepare_assets.py" for %%I in ("%~dp0tools\sgdk_wrapper") do set "SGDK_WRAPPER_ROOT=%%~fI"
if not defined SGDK_WRAPPER_ROOT if exist "%~dp0..\build.bat" if exist "%~dp0..\prepare_assets.py" for %%I in ("%~dp0..") do set "SGDK_WRAPPER_ROOT=%%~fI"
if not defined SGDK_WRAPPER_ROOT if exist "%~dp0..\..\tools\sgdk_wrapper\rebuild.bat" for %%I in ("%~dp0..\..\tools\sgdk_wrapper") do set "SGDK_WRAPPER_ROOT=%%~fI"
if not defined SGDK_WRAPPER_ROOT if exist "%~dp0..\..\..\tools\sgdk_wrapper\rebuild.bat" for %%I in ("%~dp0..\..\..\tools\sgdk_wrapper") do set "SGDK_WRAPPER_ROOT=%%~fI"
if not defined SGDK_WRAPPER_ROOT (
    echo [ERROR] Nao foi possivel localizar tools\sgdk_wrapper a partir de %~dp0
    endlocal & exit /b 1
)
call "%SGDK_WRAPPER_ROOT%\\rebuild.bat" "%SGDK_PROJECT_ROOT%"
endlocal & exit /b %errorlevel%
