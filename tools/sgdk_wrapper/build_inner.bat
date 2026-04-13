@echo off
REM =============================================
REM SGDK build_inner - Logica de build Elite V16
REM =============================================
setlocal enabledelayedexpansion

REM Setup Env + bootstrap opportunistico da .agent local
if not defined GDK (
    call "%~dp0env.bat" "%CD%"
)
if not defined GDK (
    echo [ERROR] GDK not defined.
    exit /b 1
)
if not exist "%GDK%\makefile.gen" (
    echo [ERROR] Could not locate a valid SGDK installation.
    echo [ERROR] Expected makefile at: %GDK%\makefile.gen
    echo [ERROR] Set GDK to your SGDK 2.11 folder or extract it to sdk\sgdk-2.11.
    exit /b 1
)

set "LOG_DIR=out\logs"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%" >nul 2>&1
set "LOG_FILE=%LOG_DIR%\build_output.log"
set "MAX_RETRIES=3"
set "RETRY_COUNT=0"
set "PREPARE_SCRIPT=%~dp0prepare_assets.py"
set "NORMALIZE_LOG_SCRIPT=%~dp0normalize_build_log.ps1"
set "VALIDATE_SCRIPT=%~dp0validate_resources.ps1"
set "STALE_SCRIPT=%~dp0test_project_stale.ps1"
set "FIX_TRANSPARENCY_SCRIPT=%~dp0fix_transparency.ps1"
set "RUNTIME_CAPTURE_SCRIPT=%~dp0run_runtime_capture.ps1"
set "RUNTIME_MERGE_SCRIPT=%~dp0merge_runtime_metrics.ps1"
if not defined SGDK_RUNTIME_FRAME_WINDOW set "SGDK_RUNTIME_FRAME_WINDOW=1800"

echo [SGDK Wrapper] Pre-processing (migration + resource validation)...
powershell -NoProfile -ExecutionPolicy Bypass -Command "& '%~dp0fix_migration_issues.ps1' '%CD%'"
if errorlevel 1 (
    echo [ERROR] Pre-processing migration step failed. Check out\logs\build_debug.log
    exit /b 1
)

if not exist "%VALIDATE_SCRIPT%" (
    echo [ERROR] Missing resource validation helper: %VALIDATE_SCRIPT%
    exit /b 1
)

if "%SGDK_AUTO_PREPARE_ASSETS%"=="1" (
    if not exist "%PREPARE_SCRIPT%" (
        echo [ERROR] Missing asset preparation helper: %PREPARE_SCRIPT%
        exit /b 1
    )
    echo [SGDK Wrapper] Automatic asset preparation enabled ^(SGDK_AUTO_PREPARE_ASSETS=1^)
    echo [SGDK Wrapper] Raw assets will be scanned from res\data and mirrored into res\
    echo [SGDK Wrapper] Existing incompatible images in res\ will be backed up into res\data\backup\
    python "%PREPARE_SCRIPT%" --project "%CD%"
    if errorlevel 1 (
        echo [ERROR] Asset preparation failed. Check out\logs\asset_preparation_report.json, out\logs\asset_preparation.log and out\logs\asset_preparation_preview.png
        exit /b 1
    )
)

set "VALIDATE_FLAGS=-WorkDir "%CD%""
if "%SGDK_AUTO_FIX_RESOURCES%"=="1" (
    echo [SGDK Wrapper] Proactive resource fixing enabled ^(SGDK_AUTO_FIX_RESOURCES=1^)
    set "VALIDATE_FLAGS=!VALIDATE_FLAGS! -Fix"
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%VALIDATE_SCRIPT%" !VALIDATE_FLAGS!
if errorlevel 1 (
    echo [ERROR] Resource validation failed. Check out\logs\validation_report.json and out\logs\build_debug.log
    exit /b 1
)

REM Build loop with resilient retries (up to MAX_RETRIES)
:BUILD_LOOP
set /a RETRY_COUNT+=1
echo [SGDK Wrapper] Running Build (Elite Standard) - attempt !RETRY_COUNT!/%MAX_RETRIES%

REM MSYS sh invocado pelo make pode nao herdar o PATH completo da sessao (ex.: Java instalado via winget).
REM Garantir que java.exe esteja no PATH antes de rescomp.
if defined JAVA_HOME if exist "!JAVA_HOME!\bin\java.exe" (
    set "PATH=!JAVA_HOME!\bin;!PATH!"
)
for /f "usebackq delims=" %%J in (`powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$cmd = Get-Command java -ErrorAction SilentlyContinue; if ($cmd) { Split-Path $cmd.Source; exit }; $r1 = Join-Path $env:ProgramFiles 'Eclipse Adoptium'; $r2 = Join-Path ${env:ProgramFiles(x86)} 'Eclipse Adoptium'; foreach ($r in @($r1, $r2)) { if (Test-Path $r) { $all = @(Get-ChildItem $r -Recurse -Filter java.exe -ErrorAction SilentlyContinue); if ($all.Length -gt 0) { $all[0].DirectoryName; exit } } }"`) do (
    if exist "%%J\java.exe" set "PATH=%%J;!PATH!"
)

REM Use SGDK canonical makefile for maximum compatibility
make -f "%GDK%\\makefile.gen" > "%LOG_FILE%" 2>&1
set "MAKE_RC=%ERRORLEVEL%"

if %MAKE_RC% EQU 0 (
    if exist "%NORMALIZE_LOG_SCRIPT%" (
        powershell -NoProfile -ExecutionPolicy Bypass -File "%NORMALIZE_LOG_SCRIPT%" -LogFile "%CD%\%LOG_FILE%"
    )
    if not exist "%STALE_SCRIPT%" (
        echo [ERROR] Missing stale-check helper: %STALE_SCRIPT%
        exit /b 1
    )
    for /f %%I in ('powershell -NoProfile -ExecutionPolicy Bypass -Command "[guid]::NewGuid().ToString(\"N\")"') do set "EVIDENCE_TOKEN=%%I"
    set "EVIDENCE_FILE=%TEMP%\sgdk_evidence_!EVIDENCE_TOKEN!.cmd"
    powershell -NoProfile -ExecutionPolicy Bypass -File "%STALE_SCRIPT%" -WorkDir "%CD%" -RomPath "%CD%\out\rom.bin" -InvalidateEvidence -OutputFormat Batch > "!EVIDENCE_FILE!"
    if errorlevel 1 (
        if exist "!EVIDENCE_FILE!" del "!EVIDENCE_FILE!" >nul 2>&1
        echo [ERROR] Failed to mark stale emulator evidence after build.
        exit /b 1
    )
    call "!EVIDENCE_FILE!"
    set "EVIDENCE_RC=!ERRORLEVEL!"
    if exist "!EVIDENCE_FILE!" del "!EVIDENCE_FILE!" >nul 2>&1
    if not "!EVIDENCE_RC!"=="0" (
        echo [ERROR] Could not load stale evidence context after build.
        exit /b 1
    )
    if "!SGDK_EVIDENCE_STALE!"=="1" (
        echo [WARN] Existing emulator evidence marked stale at origin: !SGDK_EVIDENCE_REASON!
    )
    powershell -NoProfile -ExecutionPolicy Bypass -File "%VALIDATE_SCRIPT%" -WorkDir "%CD%"
    if errorlevel 1 (
        echo [ERROR] Post-build validation failed. Check out\logs\validation_report.json and out\logs\build_debug.log
        exit /b 1
    )
    if "%SGDK_RUNTIME_CAPTURE%"=="1" (
        echo [SGDK Wrapper] Runtime capture enabled ^(SGDK_RUNTIME_CAPTURE=1^)
        powershell -NoProfile -ExecutionPolicy Bypass -File "%RUNTIME_CAPTURE_SCRIPT%" -ProjectDir "%CD%" -FrameWindow %SGDK_RUNTIME_FRAME_WINDOW%
        if errorlevel 1 (
            echo [ERROR] Runtime capture failed. Check out\logs\runtime_metrics.json and emulator output.
            exit /b 1
        )
        powershell -NoProfile -ExecutionPolicy Bypass -File "%RUNTIME_MERGE_SCRIPT%" -ProjectDir "%CD%"
        if errorlevel 1 (
            echo [ERROR] Runtime merge failed. Check out\logs\validation_report.json
            exit /b 1
        )
    )
    echo [OK] Build successful.
    exit /b 0
)

echo [FAIL] Build error. Check %LOG_FILE%
findstr /C:"error:" "%LOG_FILE%" 2>nul

REM Retryable fixers based on log patterns
set "DID_FIX=0"

REM Transparency / palette issues -> try transparency fixer
findstr /I /C:"transparent pixel" /C:"not an indexed image" /C:"RGB image width should be >=" "%LOG_FILE%" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    if exist "%FIX_TRANSPARENCY_SCRIPT%" (
        echo [SGDK Wrapper] Detected transparency/palette issues. Running fix_transparency.ps1...
        powershell -NoProfile -ExecutionPolicy Bypass -File "%FIX_TRANSPARENCY_SCRIPT%"
        if %ERRORLEVEL% EQU 0 (
            set "DID_FIX=1"
        )
    ) else (
        echo [ERROR] Missing transparency fixer: %FIX_TRANSPARENCY_SCRIPT%
        exit /b !MAKE_RC!
    )
)

REM Deprecated API / signature mismatch -> force migration rules re-apply
findstr /I /C:"deprecated" /C:"too many arguments" /C:"implicit declaration of function" "%LOG_FILE%" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [SGDK Wrapper] Detected migration-related compile errors. Re-running fix_migration_issues.ps1 -Force...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "& '%~dp0fix_migration_issues.ps1' '%CD%' -Force"
    if %ERRORLEVEL% EQU 0 (
        set "DID_FIX=1"
    )
)

if "!DID_FIX!"=="1" (
    if !RETRY_COUNT! LSS !MAX_RETRIES! (
        echo [SGDK Wrapper] Fixers applied. Retrying build...
        goto :BUILD_LOOP
    )
)

echo [ERROR] Build failed after !RETRY_COUNT! attempt(s). No more retryable fixes available.
exit /b !MAKE_RC!
