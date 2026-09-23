@echo off
REM Script para copiar arquivos de configure/support de upstream → standard

set "TOOLKIT=SGDK_Engines\PlatformerEngine Toolkit [VER.1.0] [SGDK 211] [GEN] [COLLECTION] [PLATAFORMA]"
set "CONSOL=SGDK_Engines\PlatformerEngine_CONSOLIDATED [VER.1.0] [SGDK 211] [GEN] [COLLECTION] [PLATAFORMA]"

echo ========================================
echo Copiando arquivos de suporte...
echo ========================================

cd /d "f:\Projects\MegaDrive_DEV"

echo [1] Copiando .agent/...
xcopy "%TOOLKIT%\upstream\PlatformerEngine\.agent\*" "%CONSOL%\standard\.agent\" /E /I /Y 2>nul

echo [2] Copiando .cursor/...
xcopy "%TOOLKIT%\upstream\PlatformerEngine\.cursor\*" "%CONSOL%\standard\.cursor\" /E /I /Y 2>nul

echo [3] Copiando .vscode/...
xcopy "%TOOLKIT%\upstream\PlatformerEngine\.vscode\*" "%CONSOL%\standard\.vscode\" /E /I /Y 2>nul

echo [4] Copiando .mddev/...
xcopy "%TOOLKIT%\upstream\PlatformerEngine\.mddev\*" "%CONSOL%\standard\.mddev\" /E /I /Y 2>nul

echo [5] Copiando README e config...
copy "%TOOLKIT%\upstream\PlatformerEngine\README.md" "%CONSOL%\standard\" /Y 2>nul
copy "%TOOLKIT%\upstream\PlatformerEngine\.sgdk_migration_state.json" "%CONSOL%\standard\" /Y 2>nul
copy "%TOOLKIT%\upstream\PlatformerEngine\.gitignore" "%CONSOL%\standard\" /Y 2>nul

echo ========================================
echo SUCESSO! Arquivos de suporte copiados
echo ========================================
