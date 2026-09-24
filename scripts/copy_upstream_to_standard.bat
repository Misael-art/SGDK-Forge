@echo off
REM Script para copiar PlatformerEngine upstream → standard

setlocal enabledelayedexpansion

set "TOOLKIT=SGDK_Engines\PlatformerEngine Toolkit [VER.1.0] [SGDK 211] [GEN] [COLLECTION] [PLATAFORMA]"
set "CONSOL=SGDK_Engines\PlatformerEngine_CONSOLIDATED [VER.1.0] [SGDK 211] [GEN] [COLLECTION] [PLATAFORMA]"

echo ========================================
echo Copiando PlatformerEngine upstream ^→ standard
echo ========================================

cd /d "f:\Projects\MegaDrive_DEV"

echo.
echo [1] Copiando SRC...
xcopy "%TOOLKIT%\upstream\PlatformerEngine\src\*" "%CONSOL%\standard\src\" /E /I /Y
if errorlevel 1 echo ERRO em SRC! & goto END

echo [OK] SRC copiado

echo.
echo [2] Copiando INC...
xcopy "%TOOLKIT%\upstream\PlatformerEngine\inc\*" "%CONSOL%\standard\inc\" /E /I /Y
if errorlevel 1 echo ERRO em INC! & goto END

echo [OK] INC copiado

echo.
echo [3] Copiando RES...
xcopy "%TOOLKIT%\upstream\PlatformerEngine\res\*" "%CONSOL%\standard\res\" /E /I /Y
if errorlevel 1 echo ERRO em RES! & goto END

echo [OK] RES copiado

echo.
echo [4] Copiando makefile...
copy "%TOOLKIT%\upstream\PlatformerEngine\makefile" "%CONSOL%\standard\" /Y
copy "%TOOLKIT%\upstream\PlatformerEngine\.mddev" "%CONSOL%\standard\" /Y
copy "%TOOLKIT%\upstream\PlatformerEngine\.gitignore" "%CONSOL%\standard\" /Y 2>nul

echo.
echo.
echo ========================================
echo SUCESSO! Código copiado para standard/
echo ========================================
goto END

:END
endlocal
