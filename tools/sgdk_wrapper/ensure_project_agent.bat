@echo off
REM =========================================================================
REM ensure_project_agent.bat - Materializa .agent canonica no projeto
REM =========================================================================
setlocal

set "TARGET_DIR=%~1"
if "%TARGET_DIR%"=="" if defined SGDK_PROJECT_ROOT set "TARGET_DIR=%SGDK_PROJECT_ROOT%"
if "%TARGET_DIR%"=="" (
    echo [ERROR] No project root provided to ensure_project_agent.bat.
    exit /b 1
)

set "SOURCE_DIR=%~dp0.agent"
if not exist "%SOURCE_DIR%\ARCHITECTURE.md" (
    echo [ERROR] Canonical .agent not found in wrapper: %SOURCE_DIR%
    exit /b 1
)

set "BOOTSTRAP_SCRIPT=%~dp0ensure_project_agent.ps1"
if not exist "%BOOTSTRAP_SCRIPT%" (
    echo [ERROR] Missing .agent bootstrap helper: %BOOTSTRAP_SCRIPT%
    exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%BOOTSTRAP_SCRIPT%" -SourceDir "%SOURCE_DIR%" -TargetDir "%TARGET_DIR%"
set "BOOTSTRAP_RC=%ERRORLEVEL%"
if not "%BOOTSTRAP_RC%"=="0" (
    echo [ERROR] Failed to ensure .agent for project root: %TARGET_DIR%
    exit /b %BOOTSTRAP_RC%
)

endlocal
exit /b 0
