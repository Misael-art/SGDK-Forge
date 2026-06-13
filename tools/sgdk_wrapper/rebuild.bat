@echo off
REM =============================================
REM SGDK wrapper rebuild script
REM Centralized rebuild logic for all projects.
REM It cleans and then builds the project.
REM =============================================
setlocal

call "%~dp0load_project_context.bat" "%~1"
if errorlevel 1 exit /b 1

if /I "%SGDK_BUILD_POLICY%"=="disabled" (
    echo [SGDK Wrapper] Pacote de referencia detectado: %SGDK_DISPLAY_NAME%
    echo [SGDK Wrapper] Rebuild desativado por manifesto. Consulte README.md e doc\.
    exit /b 0
)

echo [SGDK Wrapper] Rebuilding project in: %SGDK_WORK_DIR%

call "%~dp0env.bat" "%SGDK_PROJECT_ROOT%"

echo [SGDK Wrapper] Cleaning...
call "%~dp0clean.bat" "%SGDK_PROJECT_ROOT%"

echo [SGDK Wrapper] Building...
call "%~dp0build.bat" "%SGDK_PROJECT_ROOT%"

endlocal
