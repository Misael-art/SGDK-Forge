@echo off
REM ============================================
REM  MegaDrive_DEV - Environment Setup (Host)
REM ============================================

REM 1. Set current session paths
call "%~dp0tools\sgdk_wrapper\env.bat"

REM 2. Execute Powershell logic to make variables permanent and install dependencies
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\sgdk_wrapper\install_host_deps.ps1" -GDKPath "%GDK%"

REM summary
if defined GDK (
    echo.
    echo ============================================
    echo  SGDK v2.11 Environment Ready
    echo  GDK = %GDK%
    echo  EMULATOR = %SGDK_EMULATOR_PATH%
    echo ============================================
    echo.
) else (
    echo [WARNING] GDK path not set - environment may not be configured correctly.
)

echo [INFO] Dependencies checked: Java, Python, ImageMagick, Visual C++ runtimes, VSCode.
echo You may need to restart your terminal or VSCode for environment changes to take effect.
echo Use: new-project.bat ^<nome^> para criar um novo projeto

echo.
