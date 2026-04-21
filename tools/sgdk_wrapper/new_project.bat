@echo off
REM =========================================================================
REM new_project.bat - Create a new SGDK project from the canonical model
REM =========================================================================
setlocal
set "CREATED_TARGET=0"
set "NEW_PROJ_NAME=%~1"
if "%NEW_PROJ_NAME%"=="" (
    echo Usage: new_project.bat ^<project-name^>
    exit /b 1
)

if not "%NEW_PROJ_NAME:\=%"=="%NEW_PROJ_NAME%" goto :invalid_name
if not "%NEW_PROJ_NAME:/=%"=="%NEW_PROJ_NAME%" goto :invalid_name
if not "%NEW_PROJ_NAME:..=%"=="%NEW_PROJ_NAME%" goto :invalid_name

call "%~dp0env.bat"
if ERRORLEVEL 1 (
    echo [ERROR] Failed to initialize the SGDK wrapper environment.
    exit /b 1
)

goto :after_name_validation

:invalid_name
    echo [ERROR] Invalid project name "%NEW_PROJ_NAME%". Use only a single directory name.
    exit /b 1

:after_name_validation

set "TARGET_DIR=%MD_ROOT%\SGDK_projects\%NEW_PROJ_NAME%"

if exist "%TARGET_DIR%" (
    echo [ERROR] Project "%NEW_PROJ_NAME%" already exists.
    exit /b 1
)

set "TEMPLATE_DIR=%~dp0modelo"
if not exist "%TEMPLATE_DIR%" set "TEMPLATE_DIR=%MD_ROOT%\SGDK_templates\base-elite"
if not exist "%TEMPLATE_DIR%" (
    echo [ERROR] Canonical template not found at "%TEMPLATE_DIR%".
    exit /b 1
)

echo [INFO] Creating project "%NEW_PROJ_NAME%" from canonical SGDK model...
xcopy /E /I /Y /Q "%TEMPLATE_DIR%\*" "%TARGET_DIR%\" >nul
if ERRORLEVEL 1 (
    echo [ERROR] Failed to copy project template.
    if exist "%TARGET_DIR%" rmdir /S /Q "%TARGET_DIR%"
    exit /b 1
)
set "CREATED_TARGET=1"

REM Projetos novos devem sempre receber a .agent mais recente do wrapper.
if exist "%TARGET_DIR%\.agent" (
    rmdir /S /Q "%TARGET_DIR%\.agent"
)

REM Personaliza placeholders do template para o nome real do projeto.
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$targetDir = '%TARGET_DIR%'; $projName = '%NEW_PROJ_NAME%';" ^
    "$files = @($targetDir + '\README.md', $targetDir + '\.mddev\project.json');" ^
    "$docFiles = Get-ChildItem -LiteralPath ($targetDir + '\doc') -Filter '*.md' -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName;" ^
    "if ($docFiles) { $files = $files + @($docFiles) };" ^
    "foreach ($file in $files) {" ^
    "  if (Test-Path -LiteralPath $file) {" ^
    "    $content = Get-Content -LiteralPath $file -Raw -Encoding UTF8;" ^
    "    $content = $content.Replace('__PROJECT_NAME__', $projName);" ^
    "    Set-Content -LiteralPath $file -Value $content -Encoding UTF8;" ^
    "  }" ^
    "}"
if ERRORLEVEL 1 (
    echo [ERROR] Failed to personalize template placeholders.
    if "%CREATED_TARGET%"=="1" if exist "%TARGET_DIR%" rmdir /S /Q "%TARGET_DIR%"
    exit /b 1
)

call "%~dp0ensure_project_agent.bat" "%TARGET_DIR%"
if ERRORLEVEL 1 (
    echo [ERROR] Project created, but failed to bootstrap the canonical .agent into "%TARGET_DIR%".
    if "%CREATED_TARGET%"=="1" if exist "%TARGET_DIR%" rmdir /S /Q "%TARGET_DIR%"
    exit /b 1
)

echo [OK] Project created: %TARGET_DIR%
echo.
echo Next steps:
echo   1. cd SGDK_projects\%NEW_PROJ_NAME%
echo   2. code .
echo   3. Atualize .mddev\project.json, doc\11-gdd.md e doc\13-spec-cenas.md
echo   4. Declare a identidade de front-end e o papel formal de menu/title antes do runtime.
echo   5. Put raw art in res\data\ when needed.
echo   6. Run build.bat to verify the canonical wrapper pipeline.
echo.
echo REGRA DE OURO: sempre atualize a documentacao quando a verdade do projeto mudar.

endlocal
