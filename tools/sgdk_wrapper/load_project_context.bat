@echo off
REM =========================================================================
REM load_project_context.bat - Resolve projeto/manifesto e prepara contexto
REM =========================================================================
setlocal

set "ENTRY_DIR=%~1"
if "%ENTRY_DIR%"=="" set "ENTRY_DIR=%CD%"
REM Avoid trailing backslash inside quotes (breaks PowerShell argv parsing)
if not "%ENTRY_DIR%"=="" (
    if "%ENTRY_DIR:~-1%"=="\" (
        REM Keep root like C:\ intact
        if not "%ENTRY_DIR:~1,2%"==":\" (
            set "ENTRY_DIR=%ENTRY_DIR:~0,-1%"
        ) else (
            REM If longer than 3 chars, safe to trim
            if not "%ENTRY_DIR:~3%"=="" set "ENTRY_DIR=%ENTRY_DIR:~0,-1%"
        )
    )
)

set "RESOLVE_SCRIPT=%~dp0resolve_project.ps1"
if not exist "%RESOLVE_SCRIPT%" (
    echo [ERROR] Missing project resolver: %RESOLVE_SCRIPT%
    exit /b 1
)

for /f %%I in ('powershell -NoProfile -ExecutionPolicy Bypass -Command "[guid]::NewGuid().ToString(\"N\")"') do set "CTX_TOKEN=%%I"
set "CTX_FILE=%TEMP%\sgdk_context_%CTX_TOKEN%.cmd"

powershell -NoProfile -ExecutionPolicy Bypass -File "%RESOLVE_SCRIPT%" -EntryDir "%ENTRY_DIR%" -OutputFormat Batch > "%CTX_FILE%"
if errorlevel 1 (
    if exist "%CTX_FILE%" del "%CTX_FILE%" >nul 2>&1
    echo [ERROR] Failed to resolve project context for: %ENTRY_DIR%
    exit /b 1
)

call "%CTX_FILE%"
set "CTX_RC=%ERRORLEVEL%"
if exist "%CTX_FILE%" del "%CTX_FILE%" >nul 2>&1
if not "%CTX_RC%"=="0" (
    echo [ERROR] Failed to import resolved project context.
    exit /b 1
)

for %%I in ("%SGDK_ENTRY_DIR%") do set "SGDK_ENTRY_DIR_SHORT=%%~sI"
for %%I in ("%SGDK_PROJECT_ROOT%") do set "SGDK_PROJECT_ROOT_SHORT=%%~sI"
for %%I in ("%SGDK_WORK_DIR%") do set "SGDK_WORK_DIR_SHORT=%%~sI"

REM Validate & align project worktree to canonical standard (fix-in-place)
set "ALIGN_SCRIPT=%~dp0validate_and_align_worktree.ps1"
if exist "%ALIGN_SCRIPT%" (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%ALIGN_SCRIPT%" -ProjectRoot "%SGDK_PROJECT_ROOT%" -WorkspaceRoot "%~dp0..\.." -Fix
    if errorlevel 1 (
        echo [ERROR] Failed to validate/align worktree for: %SGDK_PROJECT_ROOT%
        exit /b 1
    )
) else (
    echo [ERROR] Missing worktree validator: %ALIGN_SCRIPT%
    exit /b 1
)

call "%~dp0ensure_project_agent.bat" "%SGDK_PROJECT_ROOT%"
if errorlevel 1 (
    echo [ERROR] Failed to bootstrap .agent into project root: %SGDK_PROJECT_ROOT%
    exit /b 1
)

endlocal & (
    set "SGDK_ENTRY_DIR=%SGDK_ENTRY_DIR%"
    set "SGDK_PROJECT_ROOT=%SGDK_PROJECT_ROOT%"
    set "SGDK_WORK_DIR=%SGDK_WORK_DIR%"
    set "SGDK_LAYOUT=%SGDK_LAYOUT%"
    set "SGDK_MANIFEST_PATH=%SGDK_MANIFEST_PATH%"
    set "SGDK_DISPLAY_NAME=%SGDK_DISPLAY_NAME%"
    set "SGDK_KIND=%SGDK_KIND%"
    set "SGDK_CATEGORY=%SGDK_CATEGORY%"
    set "SGDK_BUILD_POLICY=%SGDK_BUILD_POLICY%"
    set "SGDK_NOTES=%SGDK_NOTES%"
    set "SGDK_RESOLUTION_REASON=%SGDK_RESOLUTION_REASON%"
    set "SGDK_ENTRY_DIR_SHORT=%SGDK_ENTRY_DIR_SHORT%"
    set "SGDK_PROJECT_ROOT_SHORT=%SGDK_PROJECT_ROOT_SHORT%"
    set "SGDK_WORK_DIR_SHORT=%SGDK_WORK_DIR_SHORT%"
)

exit /b 0
