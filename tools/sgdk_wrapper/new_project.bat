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

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0validate_project_name.ps1" -Name "%NEW_PROJ_NAME%" >nul
if ERRORLEVEL 1 goto :invalid_standard_name

call "%~dp0env.bat"
if ERRORLEVEL 1 (
    echo [ERROR] Failed to initialize the SGDK wrapper environment.
    exit /b 1
)

goto :after_name_validation

:invalid_name
    echo [ERROR] Invalid project name "%NEW_PROJ_NAME%". Use only a single directory name.
    exit /b 1

:invalid_standard_name
    echo [ERROR] Invalid canonical project name "%NEW_PROJ_NAME%".
    echo [ERROR] Expected: NOME [VER.XXX] [SGDK YYY] [PLATAFORMA] [TIPO] [GENERO]
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

REM O template pode conter uma .agent legada; projetos novos devem receber
REM apenas a ponte canonica criada por ensure_project_agent.bat.
if exist "%TARGET_DIR%\.agent" (
    rmdir /S /Q "%TARGET_DIR%\.agent"
)

REM Personaliza placeholders do template para o nome real do projeto.
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ^
    "$targetDir = '%TARGET_DIR%'; $projName = '%NEW_PROJ_NAME%';" ^
    "$files = @(Get-ChildItem -LiteralPath $targetDir -Recurse -File -Include '*.md','*.json' -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName);" ^
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

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0adopt_project_methodology.ps1" -ProjectRoot "%TARGET_DIR%" -Lifecycle new
if ERRORLEVEL 1 (
    echo [ERROR] Failed to materialize project methodology manifests.
    if "%CREATED_TARGET%"=="1" if exist "%TARGET_DIR%" rmdir /S /Q "%TARGET_DIR%"
    exit /b 1
)

call "%~dp0ensure_project_agent.bat" "%TARGET_DIR%"
if ERRORLEVEL 1 (
    echo [ERROR] Project created, but failed to bootstrap the canonical .agent into "%TARGET_DIR%".
    if "%CREATED_TARGET%"=="1" if exist "%TARGET_DIR%" rmdir /S /Q "%TARGET_DIR%"
    exit /b 1
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scene_contract_compiler.ps1" -ProjectRoot "%TARGET_DIR%" -WarnOnly >nul
if ERRORLEVEL 1 (
    echo [WARN] Project created, but scene_contract_compiler.ps1 could not generate the initial doc\scene-contracts.json.
    echo [WARN] Review doc\13-spec-cenas.md and doc\scene-regression.json before the first validation pass.
)

echo [OK] Project created: %TARGET_DIR%
echo.
echo Next steps:
echo   1. cd SGDK_projects\%NEW_PROJ_NAME%
echo   2. code .
echo   3. Classifique doc\project_context_manifest.json antes de arte/runtime.
echo   4. Valide o contexto com tools\sgdk_wrapper\validate_project_context.ps1.
echo   5. Classifique doc\project_methodology_manifest.json e doc\technique_usage_manifest.json antes de arte/runtime.
echo   6. Valide com tools\sgdk_wrapper\validate_project_methodology.ps1; review_required bloqueia closeout.
echo   7. Atualize doc\00-project-brief.md, doc\10-memory-bank.md, doc\11-gdd.md, doc\15-tdd.md, doc\13-spec-cenas.md e doc\scene-regression.json conforme o contexto.
echo   8. Use audit_project_learning.ps1 em Audit/Capture; aprendizado e automatico apenas no projeto e propostas canonicas exigem aprovacao humana.
echo   9. Preencha doc\14-plano-de-provas-qa.md com a rota minima para visual, audio e hardware_real
echo   10. Registre mudancas operacionais em doc\changelog\changelog.md
echo   11. Revise o companion gerado em doc\scene-contracts.json
echo   12. Declare a identidade de front-end e o papel formal de menu/title antes do runtime.
echo   13. Put raw art in res\data\ when needed.
echo   14. Run build.bat to verify the canonical wrapper pipeline.
echo.
echo REGRA DE OURO: sempre atualize a documentacao quando a verdade do projeto mudar.

endlocal
