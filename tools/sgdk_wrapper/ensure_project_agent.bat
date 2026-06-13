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
if not exist "%SOURCE_DIR%\framework_manifest.json" (
    echo [ERROR] Canonical .agent manifest not found in wrapper: %SOURCE_DIR%\framework_manifest.json
    exit /b 1
)

set "BOOTSTRAP_SCRIPT=%~dp0ensure_project_agent.ps1"
if not exist "%BOOTSTRAP_SCRIPT%" (
    echo [ERROR] Missing .agent bootstrap helper: %BOOTSTRAP_SCRIPT%
    exit /b 1
)

for /f %%I in ('powershell -NoProfile -ExecutionPolicy Bypass -Command "[guid]::NewGuid().ToString(\"N\")"') do set "BOOTSTRAP_TOKEN=%%I"
set "BOOTSTRAP_STATUS_FILE=%TEMP%\sgdk_agent_bootstrap_%BOOTSTRAP_TOKEN%.cmd"

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$out = & '%BOOTSTRAP_SCRIPT%' -SourceDir '%SOURCE_DIR%' -TargetDir '%TARGET_DIR%' -OutputFormat Batch; $rc = $LASTEXITCODE; $out | Set-Content -LiteralPath '%BOOTSTRAP_STATUS_FILE%' -Encoding ASCII; exit $rc"
set "BOOTSTRAP_RC=%ERRORLEVEL%"
if not "%BOOTSTRAP_RC%"=="0" (
    if exist "%BOOTSTRAP_STATUS_FILE%" del "%BOOTSTRAP_STATUS_FILE%" >nul 2>&1
    echo [ERROR] Failed to ensure .agent for project root: %TARGET_DIR%
    exit /b %BOOTSTRAP_RC%
)

call "%BOOTSTRAP_STATUS_FILE%"
set "BOOTSTRAP_IMPORT_RC=%ERRORLEVEL%"
if exist "%BOOTSTRAP_STATUS_FILE%" del "%BOOTSTRAP_STATUS_FILE%" >nul 2>&1
if not "%BOOTSTRAP_IMPORT_RC%"=="0" (
    echo [ERROR] Failed to import .agent bootstrap status for: %TARGET_DIR%
    exit /b 1
)

if "%SGDK_AGENT_BOOTSTRAP_DEGRADED%"=="1" (
    echo [WARN] .agent local em modo degradado: %SGDK_AGENT_BOOTSTRAP_REASON%
)

endlocal & (
    set "SGDK_AGENT_BOOTSTRAPPED=%SGDK_AGENT_BOOTSTRAPPED%"
    set "SGDK_AGENT_BOOTSTRAP_DEGRADED=%SGDK_AGENT_BOOTSTRAP_DEGRADED%"
    set "SGDK_AGENT_BOOTSTRAP_REASON=%SGDK_AGENT_BOOTSTRAP_REASON%"
    set "SGDK_AGENT_CANONICAL_VERSION=%SGDK_AGENT_CANONICAL_VERSION%"
    set "SGDK_AGENT_LOCAL_VERSION=%SGDK_AGENT_LOCAL_VERSION%"
    set "SGDK_AGENT_SOURCE_DIR=%SGDK_AGENT_SOURCE_DIR%"
    set "SGDK_AGENT_LOCAL_DIR=%SGDK_AGENT_LOCAL_DIR%"
)
exit /b 0
