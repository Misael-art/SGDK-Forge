@echo off
:: Photo2SGDK - Launcher Proativo
:: Este script inicia a interface do Photoshop do SGDK garantindo o contexto correto.

setlocal
set "APP_DIR=%~dp0interface.dist"
set "EXE_NAME=photo2sgdk.exe"

if not exist "%APP_DIR%\%EXE_NAME%" (
    echo [ERRO] Executavel nao encontrado em: %APP_DIR%\%EXE_NAME%
    pause
    exit /b 1
)

echo [Photo2SGDK] Iniciando a Suite de Imagem Elite...
cd /d "%APP_DIR%"
start "" "%EXE_NAME%"
exit
