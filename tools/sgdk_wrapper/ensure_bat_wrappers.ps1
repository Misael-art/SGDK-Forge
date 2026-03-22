<#
.SYNOPSIS
    Escaneia todos os projetos SGDK (.c) e garante que os .bat deleguem corretamente ao wrapper.

.DESCRIPTION
    Rotina de manutencao que:
    1. Descobre todos os projetos SGDK (src/*.c ou .mddev/project.json) em SGDK_projects, SGDK_Engines, SGDK_templates, templates
    2. Para cada projeto, calcula a profundidade correta (2 ou 4+ niveis ate a raiz do workspace)
    3. Garante que build.bat, clean.bat, run.bat, rebuild.bat existam e deleguem com o caminho correto

.PARAMETER WorkspaceRoot
    Raiz do workspace MegaDrive_DEV. Se omitido, usa dois niveis acima do script.

.PARAMETER Roots
    Pastas raiz para escanear (ex: SGDK_projects, SGDK_Engines). Se omitido, usa as padrao.

.PARAMETER Fix
    Aplica correcoes. Sem -Fix, apenas reporta problemas (modo auditoria).

.PARAMETER Verbose
    Exibe detalhes por projeto.

.EXAMPLE
    .\ensure_bat_wrappers.ps1 -Fix
    Corrige todos os .bat desalinhados.

.EXAMPLE
    .\ensure_bat_wrappers.ps1
    Apenas audita e reporta sem alterar arquivos.
#>

[CmdletBinding()]
param(
    [string]$WorkspaceRoot = "",
    [string[]]$Roots = @(),
    [switch]$Fix,
    [switch]$ShowDetails
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$script:WrapperDir = $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($WorkspaceRoot)) {
    $script:WorkspaceRoot = [System.IO.Path]::GetFullPath((Join-Path $script:WrapperDir "..\.."))
} else {
    $script:WorkspaceRoot = [System.IO.Path]::GetFullPath($WorkspaceRoot)
}

if (-not $Roots -or ($Roots | Measure-Object).Count -eq 0) {
    $script:ScanRoots = @(
        (Join-Path $script:WorkspaceRoot "SGDK_projects"),
        (Join-Path $script:WorkspaceRoot "SGDK_Engines"),
        (Join-Path $script:WorkspaceRoot "SGDK_templates"),
        (Join-Path $script:WorkspaceRoot "templates")
    )
} else {
    $script:ScanRoots = @($Roots | ForEach-Object { [System.IO.Path]::GetFullPath($_) })
}

function Get-RelativeDepth {
    param(
        [Parameter(Mandatory = $true)][string]$ProjectRoot,
        [Parameter(Mandatory = $true)][string]$WsRoot
    )
    $proj = [System.IO.Path]::GetFullPath($ProjectRoot).TrimEnd('\')
    $ws = [System.IO.Path]::GetFullPath($WsRoot).TrimEnd('\')
    if (-not $proj.StartsWith($ws, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "ProjectRoot '$ProjectRoot' nao esta dentro do workspace '$WsRoot'."
    }
    $relative = $proj.Substring($ws.Length).TrimStart('\', '/')
    if ([string]::IsNullOrWhiteSpace($relative)) { return 0 }
    $segments = $relative.Split(@('\', '/'), [StringSplitOptions]::RemoveEmptyEntries)
    return ($segments | Measure-Object).Count
}

function Get-WrapperRelativePath {
    param([int]$Depth)
    if ($Depth -le 0) { return "tools\sgdk_wrapper\" }
    $prefix = ("..\" * $Depth)
    return $prefix + "tools\sgdk_wrapper\"
}

function Get-WrapperBatContent {
    param(
        [Parameter(Mandatory = $true)][string]$Verb,
        [Parameter(Mandatory = $true)][string]$RelPathToWrapper
    )
    return @(
        '@echo off'
        'REM ========================================================================='
        "REM $Verb.bat - Delegacao canonica para tools\\sgdk_wrapper"
        'REM NUNCA adicione logica aqui. Centralize no wrapper.'
        'REM ========================================================================='
        'setlocal'
        'set "SGDK_LOCAL_ENV=%~dp0sgdk_wrapper_env.bat"'
        'if exist "%SGDK_LOCAL_ENV%" call "%SGDK_LOCAL_ENV%"'
        'set "SGDK_PROJECT_ROOT=%~dp0."'
        'for %%I in ("%SGDK_PROJECT_ROOT%") do set "SGDK_PROJECT_ROOT=%%~fI"'
        'set "SGDK_WRAPPER_ROOT="'
        "if exist ""%~dp0tools\sgdk_wrapper\$Verb.bat"" if exist ""%~dp0tools\sgdk_wrapper\prepare_assets.py"" for %%I in (""%~dp0tools\sgdk_wrapper"") do set ""SGDK_WRAPPER_ROOT=%%~fI"""
        'if not defined SGDK_WRAPPER_ROOT if exist "%~dp0..\build.bat" if exist "%~dp0..\prepare_assets.py" for %%I in ("%~dp0..") do set "SGDK_WRAPPER_ROOT=%%~fI"'
        "if not defined SGDK_WRAPPER_ROOT if exist ""%~dp0..\..\tools\sgdk_wrapper\$Verb.bat"" for %%I in (""%~dp0..\..\tools\sgdk_wrapper"") do set ""SGDK_WRAPPER_ROOT=%%~fI"""
        "if not defined SGDK_WRAPPER_ROOT if exist ""%~dp0..\..\..\tools\sgdk_wrapper\$Verb.bat"" for %%I in (""%~dp0..\..\..\tools\sgdk_wrapper"") do set ""SGDK_WRAPPER_ROOT=%%~fI"""
        'if not defined SGDK_WRAPPER_ROOT ('
        '    echo [ERROR] Nao foi possivel localizar tools\sgdk_wrapper a partir de %~dp0'
        '    endlocal & exit /b 1'
        ')'
        "call ""%SGDK_WRAPPER_ROOT%\\$Verb.bat"" ""%SGDK_PROJECT_ROOT%"""
        'endlocal & exit /b %errorlevel%'
        ''
    ) -join "`r`n"
}

function Test-IsSgdkProject {
    param([Parameter(Mandatory = $true)][string]$Path)
    if ($Path -match "\\build\\|\\out\\|\\rds\\|\\upstream\\|\\companions\\") { return $false }
    $srcDir = Join-Path $Path "src"
    if (-not (Test-Path -LiteralPath $srcDir -PathType Container)) { return $false }
    $cFiles = Get-ChildItem -LiteralPath $srcDir -Filter "*.c" -File -ErrorAction SilentlyContinue
    $cCount = ($cFiles | Measure-Object).Count
    if ($cCount -gt 0) { return $true }
    $mddev = Join-Path $Path ".mddev\project.json"
    if (Test-Path -LiteralPath $mddev -PathType Leaf) { return $true }
    return $false
}

function Get-ProjectRoots {
    $found = New-Object System.Collections.Generic.HashSet[string]([StringComparer]::OrdinalIgnoreCase)
    foreach ($root in $script:ScanRoots) {
        if (-not (Test-Path -LiteralPath $root -PathType Container)) { continue }
        Get-ChildItem -LiteralPath $root -Recurse -Force -File -Filter "*.c" -ErrorAction SilentlyContinue |
            Where-Object { $_.FullName -like "*\src\*" } |
            ForEach-Object {
                $srcDir = $_.Directory.FullName
                $projRoot = (Split-Path -Parent $srcDir)
                if (Test-IsSgdkProject -Path $projRoot) {
                    [void]$found.Add($projRoot)
                }
            }
        Get-ChildItem -LiteralPath $root -Recurse -Force -File -Filter "project.json" -ErrorAction SilentlyContinue |
            Where-Object { $_.FullName -like "*\.mddev\project.json" } |
            ForEach-Object {
                $projRoot = (Split-Path -Parent (Split-Path -Parent $_.FullName))
                if (Test-IsSgdkProject -Path $projRoot) {
                    [void]$found.Add($projRoot)
                }
            }
    }
    return @($found | Sort-Object)
}

function Ensure-BatFile {
    param(
        [Parameter(Mandatory = $true)][string]$ProjectRoot,
        [Parameter(Mandatory = $true)][string]$Verb,
        [Parameter(Mandatory = $true)][string]$RelPathToWrapper,
        [Parameter(Mandatory = $true)][bool]$DoFix
    )
    $batPath = Join-Path $ProjectRoot "$Verb.bat"
    $expected = Get-WrapperBatContent -Verb $Verb -RelPathToWrapper $RelPathToWrapper
    $exists = Test-Path -LiteralPath $batPath -PathType Leaf
    if ($exists) {
        try {
            $current = [System.IO.File]::ReadAllText($batPath)
            $currentNorm = $current -replace "`r`n", "`n" -replace "`r", "`n"
            $expectedNorm = $expected -replace "`r`n", "`n" -replace "`r", "`n"
            if ($currentNorm.TrimEnd() -eq $expectedNorm.TrimEnd()) {
                return New-Object PSObject -Property @{ Status = "OK"; Path = $batPath; Message = $null }
            }
            if (-not $DoFix) {
                return New-Object PSObject -Property @{ Status = "Desalinhado"; Path = $batPath; Message = $null }
            }
            $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
            [System.IO.File]::WriteAllText($batPath, $expected, $utf8NoBom)
            return New-Object PSObject -Property @{ Status = "Fixed"; Path = $batPath; Message = $null }
        } catch {
            return New-Object PSObject -Property @{ Status = "Error"; Path = $batPath; Message = $_.Exception.Message }
        }
    }
    if (-not $DoFix) {
        return New-Object PSObject -Property @{ Status = "Missing"; Path = $batPath; Message = $null }
    }
    try {
        $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::WriteAllText($batPath, $expected, $utf8NoBom)
        return New-Object PSObject -Property @{ Status = "Fixed"; Path = $batPath; Message = $null }
    } catch {
        return New-Object PSObject -Property @{ Status = "Error"; Path = $batPath; Message = $_.Exception.Message }
    }
}

try {
    Write-Host "[ensure_bat_wrappers] Workspace: $script:WorkspaceRoot"
    Write-Host "[ensure_bat_wrappers] Scan roots: $($script:ScanRoots -join ', ')"
    Write-Host "[ensure_bat_wrappers] Modo: $(if ($Fix) { 'Fix' } else { 'Auditoria (use -Fix para corrigir)' })"
    Write-Host ""

    $projects = @(Get-ProjectRoots)
    $projectCount = ($projects | Measure-Object).Count
    Write-Host "[ensure_bat_wrappers] Projetos encontrados: $projectCount"
    if ($projectCount -eq 0) {
        Write-Host "[ensure_bat_wrappers] Nenhum projeto SGDK encontrado."
        exit 0
    }

    $verbs = @("build", "clean", "run", "rebuild")
    $totalOk = 0
    $totalFixed = 0
    $totalMissing = 0
    $totalError = 0
    $report = @()

    foreach ($proj in $projects) {
        $depth = Get-RelativeDepth -ProjectRoot $proj -WsRoot $script:WorkspaceRoot
        $relPath = Get-WrapperRelativePath -Depth $depth

        if ($ShowDetails) {
            Write-Host "  [PROJ] $proj (depth=$depth)"
        }

        foreach ($verb in $verbs) {
            $r = Ensure-BatFile -ProjectRoot $proj -Verb $verb -RelPathToWrapper $relPath -DoFix $Fix
            switch ($r.Status) {
                "OK"          { $totalOk++ }
                "Fixed"       { $totalFixed++; $report += $r }
                "Desalinhado" { $totalMissing++; $report += $r }
                "Missing"     { $totalMissing++; $report += $r }
                "Error"       { $totalError++; $report += $r }
            }
            if ($ShowDetails -and $r.Status -ne "OK") {
                Write-Host "    [$verb] $($r.Status): $($r.Path)"
            }
        }
    }

    Write-Host ""
    Write-Host "[SUMMARY] OK=$totalOk Fixed=$totalFixed Missing=$totalMissing Error=$totalError"
    if ($report -and $report.Length -gt 0) {
        Write-Host ""
        foreach ($r in $report) {
            Write-Host "  $($r.Status): $($r.Path)"
            if ($r.Message) { Write-Host "    $($r.Message)" }
        }
    }

    if ($totalError -gt 0) { exit 1 }
    if (-not $Fix -and ($totalMissing -gt 0 -or $totalFixed -gt 0)) {
        Write-Host ""
        Write-Host "[INFO] Execute com -Fix para aplicar correcoes."
        exit 0
    }
    exit 0
}
catch {
    Write-Error $_
    exit 1
}
