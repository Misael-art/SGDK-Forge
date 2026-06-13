Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$workspaceRoot = Split-Path (Split-Path $wrapperRoot -Parent) -Parent
$modelRoot = Join-Path $wrapperRoot 'modelo'
$preflightScript = Join-Path $wrapperRoot 'preflight_host.ps1'
$newProjectScript = Join-Path $wrapperRoot 'new_project.bat'
$newProjectSh = Join-Path $wrapperRoot 'new_project.sh'
$nameValidator = Join-Path $wrapperRoot 'validate_project_name.ps1'
$commonLib = Join-Path $wrapperRoot '_lib\sgdk_common.ps1'
$envBat = Join-Path $wrapperRoot 'env.bat'

$passed = 0
$failed = 0
$total = 0

function Assert-True {
    param([string]$Name, [bool]$Condition, [string]$Detail = '')
    $script:total++
    if ($Condition) {
        $script:passed++
        Write-Host "  [PASS] $Name"
    } else {
        $script:failed++
        $msg = "  [FAIL] $Name"
        if ($Detail) { $msg += " -- $Detail" }
        Write-Host $msg
    }
}

function Read-Text {
    param([string]$Path)
    return [System.IO.File]::ReadAllText($Path, [System.Text.Encoding]::UTF8)
}

Write-Host ''
Write-Host '=== Project Bootstrap QA Proof Smoke Test ==='
Write-Host ''

$modelQaPlan = Join-Path $modelRoot 'doc\14-plano-de-provas-qa.md'
$modelMemory = Read-Text -Path (Join-Path $modelRoot 'doc\10-memory-bank.md')
$preflightText = Read-Text -Path $preflightScript
$newProjectText = Read-Text -Path $newProjectScript
$newProjectShText = Read-Text -Path $newProjectSh
$envBatText = Read-Text -Path $envBat
. $commonLib
$pythonPath = SGDK_GetPythonPath
$validNameAccepted = $false
$invalidNameRejected = $false
if (Test-Path -LiteralPath $nameValidator -PathType Leaf) {
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $nameValidator -Name 'CI Methodology Bootstrap [VER.999] [SGDK 211] [GEN] [LAB] [TECHDEMO]' | Out-Null
    $validNameAccepted = ($LASTEXITCODE -eq 0)
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $nameValidator -Name 'CI' | Out-Null
    $invalidNameRejected = ($LASTEXITCODE -ne 0)
}

Assert-True 'modelo inclui plano de provas QA' (Test-Path -LiteralPath $modelQaPlan -PathType Leaf)
Assert-True 'memory bank do modelo referencia plano QA' ($modelMemory.Contains('doc/14-plano-de-provas-qa.md'))
Assert-True 'preflight exige plano QA' ($preflightText.Contains('doc\\14-plano-de-provas-qa.md'))
Assert-True 'preflight exige scene-contracts compilado' ($preflightText.Contains('doc\\scene-contracts.json'))
Assert-True 'new_project orienta preencher plano QA' ($newProjectText.Contains('doc\14-plano-de-provas-qa.md'))
Assert-True 'modelo inclui manifesto metodologico' (Test-Path -LiteralPath (Join-Path $modelRoot 'doc\project_methodology_manifest.json') -PathType Leaf)
Assert-True 'modelo inclui manifesto de contexto' (Test-Path -LiteralPath (Join-Path $modelRoot 'doc\project_context_manifest.json') -PathType Leaf)
Assert-True 'modelo inclui project brief' (Test-Path -LiteralPath (Join-Path $modelRoot 'doc\00-project-brief.md') -PathType Leaf)
Assert-True 'modelo inclui TDD dedicado' (Test-Path -LiteralPath (Join-Path $modelRoot 'doc\15-tdd.md') -PathType Leaf)
Assert-True 'modelo inclui manifesto de higiene' (Test-Path -LiteralPath (Join-Path $modelRoot 'doc\project_hygiene_manifest.json') -PathType Leaf)
Assert-True 'modelo inclui manifesto de tecnicas' (Test-Path -LiteralPath (Join-Path $modelRoot 'doc\technique_usage_manifest.json') -PathType Leaf)
Assert-True 'modelo inclui ledger de aprendizado local seguro' (Test-Path -LiteralPath (Join-Path $modelRoot 'doc\agent_learning\learning_ledger.json') -PathType Leaf)
Assert-True 'modelo inclui rascunho organizado' (Test-Path -LiteralPath (Join-Path $modelRoot 'rascunho\README.md') -PathType Leaf)
Assert-True 'modelo canonico nao carrega artefatos em out' (@(Get-ChildItem -LiteralPath (Join-Path $modelRoot 'out') -Recurse -File -ErrorAction SilentlyContinue).Count -eq 0)
Assert-True 'new_project.bat orienta classificar metodologia' ($newProjectText.Contains('doc\project_methodology_manifest.json'))
Assert-True 'new_project.bat orienta classificar contexto' ($newProjectText.Contains('doc\project_context_manifest.json'))
Assert-True 'new_project.sh personaliza placeholders JSON' ($newProjectShText.Contains("-name '*.json'"))
Assert-True 'new_project.bat materializa metodologia ausente' ($newProjectText.Contains('adopt_project_methodology.ps1'))
Assert-True 'new_project.sh materializa metodologia ausente' ($newProjectShText.Contains('adopt_project_methodology.ps1'))
Assert-True 'validator canonico de nome existe' (Test-Path -LiteralPath $nameValidator -PathType Leaf)
Assert-True 'validator canonico aceita nome completo' $validNameAccepted
Assert-True 'validator canonico rejeita nome curto sem tags' $invalidNameRejected
Assert-True 'new_project.bat valida nome antes de criar' ($newProjectText.Contains('validate_project_name.ps1'))
Assert-True 'new_project.sh valida nome antes de criar' ($newProjectShText.Contains('validate_project_name.ps1'))
Assert-True 'python discovery funciona sob StrictMode e ErrorAction Stop' (-not [string]::IsNullOrWhiteSpace([string]$pythonPath))
Assert-True 'preflight prefere SGDK local antes de variavel GDK' (
    $preflightText.IndexOf('$candidates = @($localGdk)') -ge 0 -and
    $preflightText.IndexOf('$candidates = @($localGdk)') -lt $preflightText.IndexOf('if ($env:GDK')
)
Assert-True 'env.bat prefere SGDK local antes de variavel GDK' (
    $envBatText.IndexOf('if exist "%SGDK_LOCAL_GDK%\makefile.gen"') -ge 0 -and
    $envBatText.IndexOf('if exist "%SGDK_LOCAL_GDK%\makefile.gen"') -lt $envBatText.IndexOf('if not defined GDK_CANDIDATE if defined GDK ')
)

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
