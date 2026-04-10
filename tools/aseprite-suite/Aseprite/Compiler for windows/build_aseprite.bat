@echo off
setlocal

REM Diretórios relativos (assumindo que o script está no mesmo local dos diretórios)
set ASEPRITE_SOURCE_DIR=%~dp0Aseprite-v1.3.11-beta2-Source
set SKIA_DIR=%~dp0Skia-Windows-Release-x64
set SKIA_LIBRARY_DIR=%SKIA_DIR%\out\Release-x64

REM Diretório de build
if not exist build (
    mkdir build
)
cd build

REM Executa o CMake para gerar a configuração com Ninja
REM Ajuste as flags conforme necessário. Caso necessite de ZLIB, ICU, etc., inclua os parâmetros.
cmake -G "Ninja" ^
  -DCMAKE_BUILD_TYPE=Release ^
  -DLAF_BACKEND=skia ^
  -DSKIA_DIR="%SKIA_DIR%" ^
  -DSKIA_LIBRARY_DIR="%SKIA_LIBRARY_DIR%" ^
  -DSKIA_LIBRARY="%SKIA_LIBRARY_DIR%\skia.lib" ^
  -DSKIA_ICU_LIBRARY="%SKIA_LIBRARY_DIR%\icuuc.lib" ^
  -DCMAKE_CXX_FLAGS=-DZLIB_CONST ^
  "%ASEPRITE_SOURCE_DIR%"

if errorlevel 1 (
    echo Erro ao configurar o projeto com CMake.
    pause
    exit /b 1
)

REM Compila o Aseprite usando o ninja
"%~dp0ninja.exe" aseprite

if errorlevel 1 (
    echo Erro na compilacao do Aseprite.
    pause
    exit /b 1
)

echo Compilacao concluida com sucesso!
pause
endlocal
