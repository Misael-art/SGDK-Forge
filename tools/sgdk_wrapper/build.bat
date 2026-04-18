@echo off
REM =========================================================================
REM build.bat - Wrapper central de build com bootstrap automatico da .agent
REM =========================================================================
setlocal

call "%~dp0load_project_context.bat" "%~1"
if errorlevel 1 exit /b 1

if /I "%SGDK_BUILD_POLICY%"=="disabled" (
    echo [SGDK Wrapper] Pacote de referencia detectado: %SGDK_DISPLAY_NAME%
    echo [SGDK Wrapper] Build desativado por manifesto. Consulte README.md e doc\.
    endlocal & set "SGDK_BUILD_SKIPPED=1" & exit /b 0
)

cd /d "%SGDK_WORK_DIR_SHORT%" >nul 2>&1
if errorlevel 1 (
    cd /d "%SGDK_WORK_DIR%" >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Failed to change directory to work dir.
        echo [ERROR] SGDK_WORK_DIR_SHORT="%SGDK_WORK_DIR_SHORT%"
        echo [ERROR] SGDK_WORK_DIR="%SGDK_WORK_DIR%"
        exit /b 1
    )
)

set "ENV_STDERR=%TEMP%\sgdk_env_stderr_%RANDOM%.txt"
call "%~dp0env.bat" "%SGDK_PROJECT_ROOT%" 2> "%ENV_STDERR%"
set "ENV_RC=%ERRORLEVEL%"
if exist "%ENV_STDERR%" (
    for /f "usebackq delims=" %%L in ("%ENV_STDERR%") do (
        echo %%L | findstr /I /C:"O sistema" >nul 2>&1
        if errorlevel 1 echo [WARN] env.bat stderr: %%L
    )
    del "%ENV_STDERR%" >nul 2>&1
)
if not "%ENV_RC%"=="0" exit /b %ENV_RC%
if not defined GDK (
    echo [ERROR] GDK not defined; please run "setup-env.bat" to configure your environment.
    exit /b 1
)
if not exist "%GDK%\makefile.gen" (
    echo [ERROR] Could not locate a valid SGDK installation.
    echo [ERROR] Expected makefile at: %GDK%\makefile.gen
    echo [ERROR] Use one of these options:
    echo [ERROR] 1. Set the GDK environment variable to your SGDK 2.11 folder.
    echo [ERROR] 2. Extract SGDK 2.11 to: %MD_ROOT%\sdk\sgdk-2.11
    exit /b 1
)

echo [SGDK Wrapper] Building project in: %SGDK_WORK_DIR%
echo [SGDK Wrapper] Layout: %SGDK_LAYOUT% (%SGDK_RESOLUTION_REASON%)

call "%~dp0build_inner.bat"
endlocal & exit /b %ERRORLEVEL%
