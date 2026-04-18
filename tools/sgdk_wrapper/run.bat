@echo off
REM =============================================
REM SGDK wrapper run script (Canonical & Resilient)
REM Launches the compiled ROM or builds it if missing.
REM =============================================
setlocal

call "%~dp0load_project_context.bat" "%~1"
if errorlevel 1 exit /b 1

if /I "%SGDK_BUILD_POLICY%"=="disabled" (
    echo [SGDK Wrapper] Pacote de referencia detectado: %SGDK_DISPLAY_NAME%
    echo [SGDK Wrapper] Execucao desativada por manifesto. Este item serve como material pedagogico.
    exit /b 0
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

REM load environment
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
    echo [ERROR] Set GDK to your SGDK 2.11 folder or extract it to sdk\sgdk-2.11.
    exit /b 1
)

set "ROM_PATH=%CD%\out\rom.bin"
set "LOG_DIR=%CD%\out\logs"
set "EMULATOR_SESSION_FILE=%LOG_DIR%\emulator_session.json"
set "STALE_SCRIPT=%~dp0test_project_stale.ps1"
for /f %%I in ('powershell -NoProfile -ExecutionPolicy Bypass -Command "[guid]::NewGuid().ToString(\"N\")"') do set "STALE_TOKEN=%%I"
set "STALE_FILE=%TEMP%\sgdk_stale_%STALE_TOKEN%.cmd"

if not exist "%STALE_SCRIPT%" (
    echo [ERROR] Missing stale-check helper: %STALE_SCRIPT%
    exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%STALE_SCRIPT%" -WorkDir "%SGDK_WORK_DIR%" -RomPath "%ROM_PATH%" -OutputFormat Batch > "%STALE_FILE%"
if errorlevel 1 (
    if exist "%STALE_FILE%" del "%STALE_FILE%" >nul 2>&1
    echo [ERROR] Failed to evaluate ROM freshness.
    exit /b 1
)

call "%STALE_FILE%"
set "STALE_RC=%ERRORLEVEL%"
if exist "%STALE_FILE%" del "%STALE_FILE%" >nul 2>&1
if not "%STALE_RC%"=="0" (
    echo [ERROR] Could not load ROM freshness context.
    exit /b 1
)

REM Rebuild if the ROM is missing or stale relative to src/res/inc.
if "%SGDK_ROM_NEEDS_BUILD%"=="1" (
    if "%SGDK_ROM_REASON%"=="missing" (
        echo [SGDK Wrapper] ROM not found at: %ROM_PATH%
    ) else (
        echo [SGDK Wrapper] ROM is stale relative to: %SGDK_ROM_NEWEST_INPUT%
    )
    echo [SGDK Wrapper] Triggering resilient build process...

    call "%~dp0build.bat" "%SGDK_ENTRY_DIR%"

    if errorlevel 1 (
        echo [ERROR] Build failed; refusing to run a missing or outdated ROM.
        exit /b 1
    )

    if not exist "%ROM_PATH%" (
        echo [ERROR] Build finished without generating ROM. Check out\logs\build_output.log for details.
        exit /b 1
    )
    echo [OK] Resilient build completed successfully.
)

for /f %%I in ('powershell -NoProfile -ExecutionPolicy Bypass -Command "[guid]::NewGuid().ToString(\"N\")"') do set "EVIDENCE_TOKEN=%%I"
set "EVIDENCE_FILE=%TEMP%\sgdk_evidence_%EVIDENCE_TOKEN%.cmd"
powershell -NoProfile -ExecutionPolicy Bypass -File "%STALE_SCRIPT%" -WorkDir "%SGDK_WORK_DIR%" -RomPath "%ROM_PATH%" -InvalidateEvidence -OutputFormat Batch > "%EVIDENCE_FILE%"
if errorlevel 1 (
    if exist "%EVIDENCE_FILE%" del "%EVIDENCE_FILE%" >nul 2>&1
    echo [ERROR] Failed to refresh emulator evidence state before launch.
    exit /b 1
)

call "%EVIDENCE_FILE%"
set "EVIDENCE_RC=%ERRORLEVEL%"
if exist "%EVIDENCE_FILE%" del "%EVIDENCE_FILE%" >nul 2>&1
if not "%EVIDENCE_RC%"=="0" (
    echo [ERROR] Could not load emulator evidence state before launch.
    exit /b 1
)
if "%SGDK_EVIDENCE_STALE%"=="1" (
    echo [WARN] Existing emulator evidence marked stale at origin: %SGDK_EVIDENCE_REASON%
)

if "%SGDK_EMULATOR_PATH%"=="" (
    echo [ERROR] No emulator configured or found.
    exit /b 1
)

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%" >nul 2>&1

echo [SGDK Wrapper] Running ROM: %ROM_PATH%
echo [SGDK Wrapper] Emulator: %SGDK_EMULATOR_PATH%
echo [SGDK Wrapper] Layout: %SGDK_LAYOUT% (%SGDK_RESOLUTION_REASON%)

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$rom = Get-Item -LiteralPath '%ROM_PATH%'; $stream = [System.IO.File]::OpenRead('%ROM_PATH%'); try { $sha256 = [System.Security.Cryptography.SHA256]::Create(); try { $hash = ([System.BitConverter]::ToString($sha256.ComputeHash($stream)).Replace('-', '')).ToLowerInvariant() } finally { $sha256.Dispose() } } finally { $stream.Dispose() }; $payload = [ordered]@{ timestamp = (Get-Date -Format o); emulator = '%SGDK_EMULATOR_PATH%'; rom_path = '%ROM_PATH%'; rom_size_bytes = $rom.Length; rom_last_write_utc = $rom.LastWriteTimeUtc.ToString('o'); rom_sha256 = $hash; boot_emulador = 'nao_testado'; gameplay_basico = 'nao_testado'; performance = 'nao_testado'; audio = 'nao_testado'; hardware_real = 'nao_testado'; launch_status = 'attempted' }; $payload | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath '%EMULATOR_SESSION_FILE%'"

start "" "%SGDK_EMULATOR_PATH%" "%ROM_PATH%"

if ERRORLEVEL 1 (
    echo [ERROR] The emulator failed to start or crashed immediately.
    exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$rom = Get-Item -LiteralPath '%ROM_PATH%'; $stream = [System.IO.File]::OpenRead('%ROM_PATH%'); try { $sha256 = [System.Security.Cryptography.SHA256]::Create(); try { $hash = ([System.BitConverter]::ToString($sha256.ComputeHash($stream)).Replace('-', '')).ToLowerInvariant() } finally { $sha256.Dispose() } } finally { $stream.Dispose() }; $payload = [ordered]@{ timestamp = (Get-Date -Format o); emulator = '%SGDK_EMULATOR_PATH%'; rom_path = '%ROM_PATH%'; rom_size_bytes = $rom.Length; rom_last_write_utc = $rom.LastWriteTimeUtc.ToString('o'); rom_sha256 = $hash; boot_emulador = 'nao_testado'; gameplay_basico = 'nao_testado'; performance = 'nao_testado'; audio = 'nao_testado'; hardware_real = 'nao_testado'; launch_status = 'started' }; $payload | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath '%EMULATOR_SESSION_FILE%'"

endlocal
exit /b 0
