@echo off
REM =============================================================================
REM Standardization Script: SGDK_* -> sgdk_* (lowercase)
REM =============================================================================
REM IMPORTANTE: Execute APÓS fechar VS Code e todos os exploradores!
REM =============================================================================

cd /d f:\Projects\MegaDrive_DEV

echo.
echo [INFO] Iniciando padronização de nomenclatura...
echo [INFO] Convertendo SGDK_* para sgdk_* (lowercase)
echo.

REM Check if directories exist
if not exist "SGDK_Engines" (
    echo [WARN] SGDK_Engines nao encontrado
) else (
    echo [ACTION] Renomeando: SGDK_Engines ^-^> sgdk_engines
    ren SGDK_Engines sgdk_engines
    if %ERRORLEVEL% EQU 0 (
        echo [OK] SGDK_Engines renomeado com sucesso
    ) else (
        echo [ERROR] Falha ao renomear SGDK_Engines
        echo [HINT] Feche VS Code, exploradores, e tente novamente com admin
        pause
        exit /b 1
    )
)

if not exist "SGDK_projects" (
    echo [WARN] SGDK_projects nao encontrado
) else (
    echo [ACTION] Renomeando: SGDK_projects ^-^> sgdk_projects
    ren SGDK_projects sgdk_projects
    if %ERRORLEVEL% EQU 0 (
        echo [OK] SGDK_projects renomeado com sucesso
    ) else (
        echo [ERROR] Falha ao renomear SGDK_projects
        pause
        exit /b 1
    )
)

if not exist "SGDK_templates" (
    echo [WARN] SGDK_templates nao encontrado
) else (
    echo [ACTION] Renomeando: SGDK_templates ^-^> sgdk_templates
    ren SGDK_templates sgdk_templates
    if %ERRORLEVEL% EQU 0 (
        echo [OK] SGDK_templates renomeado com sucesso
    ) else (
        echo [ERROR] Falha ao renomear SGDK_templates
        pause
        exit /b 1
    )
)

echo.
echo [VALIDACAO] Verificando estrutura padronizada...
dir /b | findstr /i ^sgdk_

echo.
echo [OK] Padronizacao concluida com sucesso!
echo [ACTION NEXT] Abra VS Code e execute: locate "SGDK_" em workspace
echo [ACTION NEXT] Atualize qualquer referencia em scripts/docs se necessario
echo.
pause
