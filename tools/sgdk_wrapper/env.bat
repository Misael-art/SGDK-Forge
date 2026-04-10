@echo off
REM =========================================================================
REM env.bat - Descobre ambiente SGDK, emulador e bootstrap opcional da .agent
REM =========================================================================
setlocal EnableDelayedExpansion

REM Optional diagnostics (disabled by default):
REM set SGDK_ENV_TRACE=1 to write a trace log and print its path.
set "SGDK_ENV_TRACE_LOG="
if defined SGDK_ENV_TRACE (
    set "SGDK_ENV_TRACE_LOG=%TEMP%\sgdk_env_trace_%RANDOM%_%RANDOM%.log"
    echo [SGDK Wrapper] env trace: !SGDK_ENV_TRACE_LOG!
    >"!SGDK_ENV_TRACE_LOG!" (
        echo [TRACE] env.bat start
        echo [TRACE] CD=!CD!
    )
)

if defined SGDK_ENV_TRACE_LOG (
    echo [TRACE] ENTRY_ARG=%~1>> "!SGDK_ENV_TRACE_LOG!"
)

for %%I in ("%~dp0..\..") do set "MD_ROOT=%%~fI"
call :RESOLVE_GDK
if not defined JAVA_OPTS set "JAVA_OPTS=-Xmx2g"
if defined SGDK_ENV_TRACE_LOG (
    echo [TRACE] MD_ROOT=!MD_ROOT!>> "!SGDK_ENV_TRACE_LOG!"
    echo [TRACE] GDK=!GDK!>> "!SGDK_ENV_TRACE_LOG!"
)

set "SGDK_EMULATOR_PATH="
if exist "%MD_ROOT%\tools\emuladores\Blastem\Blastem.exe" (
    set "SGDK_EMULATOR_PATH=%MD_ROOT%\tools\emuladores\Blastem\Blastem.exe"
) else if exist "%MD_ROOT%\tools\emuladores\BizHawk\EmuHawk.exe" (
    set "SGDK_EMULATOR_PATH=%MD_ROOT%\tools\emuladores\BizHawk\EmuHawk.exe"
) else if exist "%MD_ROOT%\tools\emuladores\Exodus_2.1\Exodus.exe" (
    set "SGDK_EMULATOR_PATH=%MD_ROOT%\tools\emuladores\Exodus_2.1\Exodus.exe"
) else if exist "%MD_ROOT%\tools\emuladores\GensKMod\gens.exe" (
    set "SGDK_EMULATOR_PATH=%MD_ROOT%\tools\emuladores\GensKMod\gens.exe"
)

set "UPDATED_PATH=%PATH%"
if exist "%GDK%\bin" set "UPDATED_PATH=%GDK%\bin;%UPDATED_PATH%"

set "ENV_ENTRY=%~1"
if "%ENV_ENTRY%"=="" set "ENV_ENTRY=%CD%"
if defined SGDK_ENV_TRACE_LOG echo [TRACE] ENV_ENTRY=!ENV_ENTRY!>> "!SGDK_ENV_TRACE_LOG!"

REM -------------------------------------------------------------------------
REM Host bootstrap (controlled): if critical deps are missing, attempt setup once
REM -------------------------------------------------------------------------
set "NEEDS_HOST_SETUP=0"
if not exist "%GDK%\makefile.gen" set "NEEDS_HOST_SETUP=1"

if defined SGDK_ENV_TRACE_LOG echo [TRACE] powershell availability check >> "!SGDK_ENV_TRACE_LOG!"
powershell -NoProfile -ExecutionPolicy Bypass -Command "exit 0" >nul 2>&1
if not "%ERRORLEVEL%"=="0" (
    echo [ERROR] PowerShell not available. Cannot bootstrap host dependencies.
    echo [ERROR] Please ensure PowerShell is installed and callable as 'powershell'.
    goto :AFTER_HOST_SETUP
)

if defined SGDK_ENV_TRACE_LOG echo [TRACE] probe java/make/magick >> "!SGDK_ENV_TRACE_LOG!"
powershell -NoProfile -ExecutionPolicy Bypass -Command "if (Get-Command java -ErrorAction SilentlyContinue) { exit 0 } exit 1" >nul 2>&1
if not "%ERRORLEVEL%"=="0" set "NEEDS_HOST_SETUP=1"

powershell -NoProfile -ExecutionPolicy Bypass -Command "if (Get-Command make -ErrorAction SilentlyContinue) { exit 0 } exit 1" >nul 2>&1
if not "%ERRORLEVEL%"=="0" set "NEEDS_HOST_SETUP=1"

powershell -NoProfile -ExecutionPolicy Bypass -Command "if (Get-Command magick -ErrorAction SilentlyContinue) { exit 0 } exit 1" >nul 2>&1
if not "%ERRORLEVEL%"=="0" set "NEEDS_HOST_SETUP=1"

if "%NEEDS_HOST_SETUP%"=="1" (
    if not defined SGDK_HOST_BOOTSTRAPPED (
        set "BOOTSTRAP_SCRIPT=%~dp0install_host_deps.ps1"
        if exist "!BOOTSTRAP_SCRIPT!" (
            echo [SGDK Wrapper] Host dependencies or SGDK SDK are missing. Attempting zero-touch bootstrap...
            powershell -NoProfile -ExecutionPolicy Bypass -File "!BOOTSTRAP_SCRIPT!" -GDKPath "%GDK%"
            set "BOOTSTRAP_RC=!ERRORLEVEL!"
            if "!BOOTSTRAP_RC!"=="0" (
                set "SGDK_HOST_BOOTSTRAPPED=1"
                call :RESOLVE_GDK
                set "UPDATED_PATH=%PATH%"
                if exist "%GDK%\bin" set "UPDATED_PATH=%GDK%\bin;%UPDATED_PATH%"
            ) else (
                echo [WARN] Host bootstrap exited with code !BOOTSTRAP_RC!.
            )
        ) else (
            echo [ERROR] Missing host bootstrap script: !BOOTSTRAP_SCRIPT!
        )
    )
)

:AFTER_HOST_SETUP

set "BOOTSTRAP_TARGET="
set "RESOLVE_SCRIPT=%~dp0resolve_project.ps1"
if exist "%RESOLVE_SCRIPT%" (
    if defined SGDK_ENV_TRACE_LOG echo [TRACE] resolve_project start >> "!SGDK_ENV_TRACE_LOG!"
    for /f %%I in ('powershell -NoProfile -ExecutionPolicy Bypass -Command "[guid]::NewGuid().ToString(\"N\")" 2^>nul') do set "ENV_TOKEN=%%I"
    set "ENV_FILE=%TEMP%\sgdk_env_!ENV_TOKEN!.cmd"
    if defined SGDK_ENV_TRACE_LOG echo [TRACE] ENV_FILE=!ENV_FILE!>> "!SGDK_ENV_TRACE_LOG!"

    powershell -NoProfile -ExecutionPolicy Bypass -File "%RESOLVE_SCRIPT%" -EntryDir "%ENV_ENTRY%" -OutputFormat Batch > "!ENV_FILE!" 2>nul
    if not errorlevel 1 (
        call "!ENV_FILE!" >nul 2>&1
        if defined SGDK_PROJECT_ROOT set "BOOTSTRAP_TARGET=!SGDK_PROJECT_ROOT!"
    )

    if exist "!ENV_FILE!" del "!ENV_FILE!" >nul 2>&1
)

if defined BOOTSTRAP_TARGET (
    if defined SGDK_ENV_TRACE_LOG echo [TRACE] ensure_project_agent >> "!SGDK_ENV_TRACE_LOG!"
    call "%~dp0ensure_project_agent.bat" "%BOOTSTRAP_TARGET%" >nul 2>&1
)

if defined SGDK_ENV_TRACE_LOG (
    echo [TRACE] BOOTSTRAP_TARGET=!BOOTSTRAP_TARGET!>> "!SGDK_ENV_TRACE_LOG!"
    echo [TRACE] SGDK_EMULATOR_PATH=!SGDK_EMULATOR_PATH!>> "!SGDK_ENV_TRACE_LOG!"
    echo [TRACE] env.bat end>> "!SGDK_ENV_TRACE_LOG!"
)

endlocal & (
    set "MD_ROOT=%MD_ROOT%"
    set "GDK=%GDK%"
    set "GDK_WIN=%GDK_WIN%"
    set "JAVA_OPTS=%JAVA_OPTS%"
    set "SGDK_EMULATOR_PATH=%SGDK_EMULATOR_PATH%"
    set "PATH=%UPDATED_PATH%"
    set "SGDK_HOST_BOOTSTRAPPED=%SGDK_HOST_BOOTSTRAPPED%"
)

exit /b 0

:RESOLVE_GDK
set "SGDK_LOCAL_GDK=%MD_ROOT%\sdk\sgdk-2.11"
set "GDK_CANDIDATE="
if defined GDK if exist "%GDK%\makefile.gen" set "GDK_CANDIDATE=%GDK%"
if not defined GDK_CANDIDATE if defined GDK_WIN if exist "%GDK_WIN%\makefile.gen" set "GDK_CANDIDATE=%GDK_WIN%"
if not defined GDK_CANDIDATE if exist "%SGDK_LOCAL_GDK%\makefile.gen" set "GDK_CANDIDATE=%SGDK_LOCAL_GDK%"
if not defined GDK_CANDIDATE if exist "%USERPROFILE%\sgdk\sgdk-2.11\makefile.gen" set "GDK_CANDIDATE=%USERPROFILE%\sgdk\sgdk-2.11"
if not defined GDK_CANDIDATE if exist "C:\SGDK\sgdk-2.11\makefile.gen" set "GDK_CANDIDATE=C:\SGDK\sgdk-2.11"
if not defined GDK_CANDIDATE if exist "C:\sgdk\sgdk-2.11\makefile.gen" set "GDK_CANDIDATE=C:\sgdk\sgdk-2.11"
if not defined GDK_CANDIDATE set "GDK_CANDIDATE=%SGDK_LOCAL_GDK%"
set "GDK=%GDK_CANDIDATE%"
set "GDK_WIN=%GDK%"
goto :eof
