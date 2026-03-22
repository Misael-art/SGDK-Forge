@echo off
REM =========================================================================
REM ensure_bats.bat - Garante que todos os .bat dos projetos SGDK deleguem ao wrapper
REM =========================================================================
REM
REM Escaneia SGDK_projects, SGDK_Engines, SGDK_templates, templates em busca de
REM projetos com .c e garante que build.bat, clean.bat, run.bat, rebuild.bat
REM existam e usem o caminho correto (2 ou 4+ niveis conforme profundidade).
REM
REM Uso:
REM   ensure_bats.bat           - Auditoria (reporta sem alterar)
REM   ensure_bats.bat -Fix      - Aplica correcoes
REM   ensure_bats.bat -Fix -ShowDetails
REM
REM =========================================================================
setlocal

set "SCRIPT_DIR=%~dp0"
set "PS_SCRIPT=%SCRIPT_DIR%ensure_bat_wrappers.ps1"

if not exist "%PS_SCRIPT%" (
    echo [ERROR] Script nao encontrado: %PS_SCRIPT%
    exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%PS_SCRIPT%" %*
exit /b %ERRORLEVEL%
