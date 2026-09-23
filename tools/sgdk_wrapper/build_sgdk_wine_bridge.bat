@echo off
setlocal EnableExtensions

if "%~1"=="" (
    echo wine_bridge_status=blocked reason=gdk_path_required
    exit /b 2
)
if "%~2"=="" (
    echo wine_bridge_status=blocked reason=project_path_required
    exit /b 2
)

set "GDK=%~1"
set "PROJECT_ROOT=%~2"
if not exist "%GDK%\makefile.gen" (
    echo wine_bridge_status=blocked reason=makefile_missing path=%GDK%\makefile.gen
    exit /b 2
)
if not exist "%PROJECT_ROOT%\res\resources.res" (
    echo wine_bridge_status=blocked reason=resources_missing path=%PROJECT_ROOT%\res\resources.res
    exit /b 2
)

set "PATH=%GDK%\bin;%PATH%"
cd /d "%PROJECT_ROOT%"
if errorlevel 1 (
    echo wine_bridge_status=blocked reason=project_cd_failed path=%PROJECT_ROOT%
    exit /b 2
)

make -f "%GDK%\makefile.gen"
set "BUILD_RC=%ERRORLEVEL%"
if not "%BUILD_RC%"=="0" (
    echo wine_bridge_status=blocked reason=sgdk_make_failed exit_code=%BUILD_RC%
    exit /b %BUILD_RC%
)
if not exist "%PROJECT_ROOT%\out\rom.bin" (
    echo wine_bridge_status=blocked reason=rom_missing_after_make
    exit /b 2
)

echo wine_bridge_status=buildado project=%PROJECT_ROOT%
exit /b 0
