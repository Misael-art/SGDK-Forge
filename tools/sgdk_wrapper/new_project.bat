@echo off
REM =========================================================================
REM new_project.bat - Create a new SGDK project from the canonical model
REM =========================================================================
setlocal
set "NEW_PROJ_NAME=%~1"
if "%NEW_PROJ_NAME%"=="" (
    echo Usage: new_project.bat ^<project-name^>
    exit /b 1
)

call "%~dp0env.bat"

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
    exit /b 1
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
    echo [WARNING] Failed to personalize some template placeholders.
)

call "%~dp0ensure_project_agent.bat" "%TARGET_DIR%"
if ERRORLEVEL 1 (
    echo [ERROR] Project created, but failed to bootstrap the canonical .agent into "%TARGET_DIR%".
    exit /b 1
)

echo [OK] Project created: %TARGET_DIR%
echo.
echo Next steps:
echo   1. cd SGDK_projects\%NEW_PROJ_NAME%
echo   2. code .
echo   3. Atualize .mddev\project.json e doc\01-visao-geral.md
echo   4. Put raw art in res\data\ when needed.
echo   5. Run build.bat to verify the canonical wrapper pipeline.
echo.
echo REGRA DE OURO: sempre atualize a documentacao quando a verdade do projeto mudar.

endlocal
