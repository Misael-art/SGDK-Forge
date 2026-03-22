[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectRoot,

    [Parameter(Mandatory = $true)]
    [string]$WorkspaceRoot,

    [ValidateSet("WarnOnly", "Fix")]
    [string]$Mode = "Fix",

    [switch]$Fix,

    [switch]$WarnOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-FullPath {
    param([Parameter(Mandatory = $true)][string]$Path)
    return [System.IO.Path]::GetFullPath($Path)
}

function Ensure-Directory {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (Test-Path -LiteralPath $Path -PathType Container) { return }
    if ($Mode -ne "Fix") { Write-Warning ("[SGDK Wrapper] Diretorio obrigatorio ausente: '{0}'." -f $Path); return }
    New-Item -ItemType Directory -Path $Path -Force | Out-Null
}

function Ensure-FileIfMissing {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$ContentUtf8NoBom
    )
    if (Test-Path -LiteralPath $Path -PathType Leaf) { return }
    if ($Mode -ne "Fix") { Write-Warning ("[SGDK Wrapper] Arquivo obrigatorio ausente: '{0}'." -f $Path); return }
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, $ContentUtf8NoBom, $utf8NoBom)
}

function Get-WrapperRelativePathFromProject {
    param(
        [Parameter(Mandatory = $true)][string]$ProjectRootPath,
        [Parameter(Mandatory = $true)][string]$WorkspaceRootPath
    )
    $proj = [System.IO.Path]::GetFullPath($ProjectRootPath).TrimEnd('\')
    $ws = [System.IO.Path]::GetFullPath($WorkspaceRootPath).TrimEnd('\')
    if (-not $proj.StartsWith($ws, [System.StringComparison]::OrdinalIgnoreCase)) {
        return "..\..\tools\sgdk_wrapper\"
    }
    $relative = $proj.Substring($ws.Length).TrimStart('\', '/')
    if ([string]::IsNullOrWhiteSpace($relative)) { return "tools\sgdk_wrapper\" }
    $segments = $relative.Split(@('\', '/'), [StringSplitOptions]::RemoveEmptyEntries)
    $depth = $segments.Count
    $prefix = ("..\" * $depth)
    return $prefix + "tools\sgdk_wrapper\"
}

function Write-WrapperBat {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][ValidateSet("build","clean","rebuild","run")][string]$Verb,
        [Parameter(Mandatory = $true)][string]$ProjectRootPath,
        [Parameter(Mandatory = $true)][string]$WorkspaceRootPath
    )

    $content = @(
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

    if (Test-Path -LiteralPath $Path -PathType Leaf) {
        $existing = Get-Content -LiteralPath $Path -Raw -ErrorAction Stop
        if ($existing -eq $content) { return }
        if ($Mode -ne "Fix") { Write-Warning ("[SGDK Wrapper] Wrapper BAT desalinhado: '{0}'." -f $Path); return }
    } else {
        if ($Mode -ne "Fix") { Write-Warning ("[SGDK Wrapper] Wrapper BAT ausente: '{0}'." -f $Path); return }
    }

    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, $content, $utf8NoBom)
}

function Ensure-ManifestIfMissing {
    param(
        [Parameter(Mandatory = $true)][string]$ProjectRootPath,
        [Parameter(Mandatory = $true)][string]$DisplayName
    )
    $mddevDir = Join-Path $ProjectRootPath ".mddev"
    Ensure-Directory -Path $mddevDir

    $manifestPath = Join-Path $mddevDir "project.json"
    if (Test-Path -LiteralPath $manifestPath -PathType Leaf) { return }
    if ($Mode -ne "Fix") { Write-Warning ("[SGDK Wrapper] Manifesto ausente: '{0}'." -f $manifestPath); return }

    $manifest = [ordered]@{
        display_name = $DisplayName
        layout       = "flat"
        project_root = "."
        sgdk_root    = "."
        build_policy = "enabled"
        kind         = ""
        category     = ""
        notes        = "Gerado automaticamente pelo SGDK Wrapper para alinhar o worktree ao padrao."
    } | ConvertTo-Json -Depth 4

    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($manifestPath, ($manifest + "`r`n"), $utf8NoBom)
}

function Read-JsonLoose {
    param([Parameter(Mandatory = $true)][string]$Path)
    try {
        $raw = Get-Content -LiteralPath $Path -Raw -ErrorAction Stop
        # tolerate BOM and "old" manifests: ConvertFrom-Json already handles UTF-8 BOM in most cases,
        # but keep the logic centralized here.
        return $raw | ConvertFrom-Json -ErrorAction Stop
    }
    catch {
        if ($Mode -eq "WarnOnly") {
            Write-Warning ("[SGDK Wrapper] Manifesto invalido (JSON): '{0}'. Detalhes: {1}" -f $Path, $_.Exception.Message)
            return $null
        }
        throw "Manifesto invalido (JSON): '$Path'. Detalhes: $($_.Exception.Message)"
    }
}

function Write-JsonUtf8NoBom {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)]$Object
    )
    $json = $Object | ConvertTo-Json -Depth 16
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, ($json + "`r`n"), $utf8NoBom)
}

function Validate-ManifestMinimum {
    param([Parameter(Mandatory = $true)][string]$ManifestPath)

    if (-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)) {
        if ($Mode -eq "Fix") { return } # will be created by Ensure-ManifestIfMissing
        Write-Warning ("[SGDK Wrapper] Manifesto ausente: '{0}'." -f $ManifestPath)
        return
    }

    $manifest = Read-JsonLoose -Path $ManifestPath
    if ($null -eq $manifest) { return }
    $script:ManifestChanged = $false
    $warnings = New-Object System.Collections.Generic.List[string]

    function Get-Prop {
        param($Obj, [string[]]$Names)
        foreach ($n in $Names) {
            $p = $Obj.PSObject.Properties[$n]
            if ($null -ne $p) { return $p.Value }
        }
        return $null
    }
    function Set-PropIfMissing {
        param($Obj, [string]$Name, $Value)
        $p = $Obj.PSObject.Properties[$Name]
        if ($null -eq $p) {
            $Obj | Add-Member -NotePropertyName $Name -NotePropertyValue $Value -Force
            $script:ManifestChanged = $true
        }
    }

    # schema_version: accept missing on old manifests; fix adds it.
    $schema = Get-Prop -Obj $manifest -Names @("schema_version", "schemaVersion")
    if ($null -eq $schema) {
        $warnings.Add("manifest missing schema_version") | Out-Null
        if ($Mode -eq "Fix") { Set-PropIfMissing -Obj $manifest -Name "schema_version" -Value 1 }
    } elseif (-not ($schema -is [int] -or $schema -is [long])) {
        $warnings.Add("manifest schema_version is not numeric") | Out-Null
    }

    # version: accept name/version pattern on old manifests
    $version = Get-Prop -Obj $manifest -Names @("version")
    if ($null -eq $version) {
        $warnings.Add("manifest missing version") | Out-Null
        if ($Mode -eq "Fix") { Set-PropIfMissing -Obj $manifest -Name "version" -Value "1.0" }
    }

    # layout: required; old manifests may already have it.
    $layout = Get-Prop -Obj $manifest -Names @("layout")
    if ($null -eq $layout) {
        $warnings.Add("manifest missing layout") | Out-Null
        if ($Mode -eq "Fix") { Set-PropIfMissing -Obj $manifest -Name "layout" -Value "flat" }
    } else {
        $validLayouts = @("flat","nested","manifest")
        if ($validLayouts -notcontains ([string]$layout).ToLowerInvariant()) {
            $warnings.Add("manifest layout invalid: $layout") | Out-Null
        }
    }

    # build_policy: required for governance (enabled/disabled); fix adds default enabled.
    $policy = Get-Prop -Obj $manifest -Names @("build_policy","buildPolicy")
    if ($null -eq $policy) {
        $warnings.Add("manifest missing build_policy") | Out-Null
        if ($Mode -eq "Fix") { Set-PropIfMissing -Obj $manifest -Name "build_policy" -Value "enabled" }
    } else {
        $validPolicies = @("enabled","disabled")
        if ($validPolicies -notcontains ([string]$policy).ToLowerInvariant()) {
            $warnings.Add("manifest build_policy invalid: $policy") | Out-Null
        }
    }

    if ($warnings.Count -gt 0) {
        foreach ($w in $warnings) { Write-Warning ("[SGDK Wrapper] {0} ({1})" -f $w, $ManifestPath) }
    }

    if ($Mode -eq "Fix" -and $script:ManifestChanged) {
        Write-JsonUtf8NoBom -Path $ManifestPath -Object $manifest
    }
}

function Ensure-ReadmeIfMissing {
    param([Parameter(Mandatory = $true)][string]$ProjectRootPath)
    $readmePath = Join-Path $ProjectRootPath "README.md"
    if (Test-Path -LiteralPath $readmePath -PathType Leaf) { return }
    if ($Mode -ne "Fix") { Write-Warning ("[SGDK Wrapper] README.md ausente: '{0}'." -f $readmePath); return }

    $name = Split-Path -Leaf $ProjectRootPath
    $content = @"
## $name

Este projeto faz parte do ecossistema **MegaDrive_DEV** (SGDK 2.11).

### Build / Run (obrigatorio via wrapper canonico)
- `build.bat`: compila o ROM usando `tools\sgdk_wrapper\`
- `run.bat`: executa em emulador (auto-build se necessario)
- `clean.bat`: limpa artefatos
- `rebuild.bat`: clean + build

### Regras para Agentes de IA (obrigatorio)
- **Nao duplicar** logica de build nesses `.bat`. Toda logica fica em `F:\Projects\MegaDrive_DEV\tools\sgdk_wrapper\`.
- **Hierarquia de verdade / governanca**: siga `AGENTS.md`, `CLAUDE.md` e a documentacao do projeto (ex.: `doc/` e `doc/10-memory-bank.md` quando aplicavel).
- **SGDK / Mega Drive**: sem `float/double`, sem `malloc/free` em gameplay loop, sem inventar APIs, respeitar budgets de VRAM/DMA/sprites.
- **Ciclo de producao**: planejar → implementar → build pelo wrapper → validar (emulador) → atualizar docs (handoff).

### Estrutura esperada do worktree
`\inc`, `\res`, `\src`, `\doc`, `\.mddev`, `\out` (artefatos), além dos wrappers `.bat`.

"@
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($readmePath, $content, $utf8NoBom)
}

try {
    if ($Fix) { $Mode = "Fix" }
    if ($WarnOnly) { $Mode = "WarnOnly" }

    $projectRootPath = Resolve-FullPath -Path $ProjectRoot
    $workspaceRootPath = Resolve-FullPath -Path $WorkspaceRoot

    if (-not (Test-Path -LiteralPath $projectRootPath -PathType Container)) {
        throw "ProjectRoot inexistente: '$projectRootPath'."
    }
    if (-not (Test-Path -LiteralPath $workspaceRootPath -PathType Container)) {
        throw "WorkspaceRoot inexistente: '$workspaceRootPath'."
    }

    $requiredDirs = @(
        "inc","res","src","doc","out","rds",
        ".mddev",".agent",".cursor",".vscode"
    )
    foreach ($d in $requiredDirs) {
        Ensure-Directory -Path (Join-Path $projectRootPath $d)
    }

    Ensure-ManifestIfMissing -ProjectRootPath $projectRootPath -DisplayName (Split-Path -Leaf $projectRootPath)
    Validate-ManifestMinimum -ManifestPath (Join-Path $projectRootPath ".mddev\project.json")
    Ensure-ReadmeIfMissing -ProjectRootPath $projectRootPath

    Write-WrapperBat -Path (Join-Path $projectRootPath "build.bat") -Verb "build" -ProjectRootPath $projectRootPath -WorkspaceRootPath $workspaceRootPath
    Write-WrapperBat -Path (Join-Path $projectRootPath "clean.bat") -Verb "clean" -ProjectRootPath $projectRootPath -WorkspaceRootPath $workspaceRootPath
    Write-WrapperBat -Path (Join-Path $projectRootPath "rebuild.bat") -Verb "rebuild" -ProjectRootPath $projectRootPath -WorkspaceRootPath $workspaceRootPath
    Write-WrapperBat -Path (Join-Path $projectRootPath "run.bat") -Verb "run" -ProjectRootPath $projectRootPath -WorkspaceRootPath $workspaceRootPath

    exit 0
}
catch {
    if ($Mode -eq "WarnOnly") {
        Write-Warning ("[SGDK Wrapper] {0}" -f $_.Exception.Message)
        exit 0
    }
    Write-Error $_
    exit 1
}

