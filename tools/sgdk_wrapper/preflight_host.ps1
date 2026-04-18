<#
.SYNOPSIS
  Verifica pre-requisitos do host Windows antes de build SGDK (Java, make, GDK, ferramentas opcionais).

.DESCRIPTION
  Exit codes:
    0 - Todos os checks obrigatorios OK (avisos opcionais podem ter sido impressos).
    1 - Falha obrigatoria (GDK/make/java ou MD_ROOT invalido).
    2 - Apenas avisos fortes (ex.: Python/Magick ausentes para validador estetico).

  Alinhado a env.bat (RESOLVE_GDK) e validate_resources.ps1 (Python/Magick nao-WindowsApps).

.PARAMETER RepoRoot
  Raiz do monorepo MegaDrive_DEV. Por omissao: avo de tools/sgdk_wrapper (este script).
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$RepoRoot = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "_lib\sgdk_common.ps1")

function Write-PreflightLog {
    param([string]$Level, [string]$Message)
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host ("[{0}] [{1}] {2}" -f $ts, $Level, $Message)
}

function Test-CommandExists {
    param([string]$Name)
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

function Resolve-MegaDriveRoot {
    param([string]$ExplicitRoot)
    if (-not [string]::IsNullOrWhiteSpace($ExplicitRoot)) {
        return [System.IO.Path]::GetFullPath($ExplicitRoot)
    }
    $wrapperDirInfo = [System.IO.DirectoryInfo]$PSScriptRoot
    $toolsDirInfo = $wrapperDirInfo.Parent
    $rootDirInfo = $toolsDirInfo.Parent
    return [System.IO.Path]::GetFullPath($rootDirInfo.FullName)
}

function Resolve-GdkPath {
    param([string]$MdRoot)
    $localGdk = Join-Path $MdRoot "sdk\sgdk-2.11"
    $candidates = @()
    if ($env:GDK -and (Test-Path -LiteralPath $env:GDK)) { $candidates += $env:GDK }
    if ($env:GDK_WIN -and (Test-Path -LiteralPath $env:GDK_WIN)) { $candidates += $env:GDK_WIN }
    $candidates += $localGdk
    $candidates += (Join-Path $env:USERPROFILE "sgdk\sgdk-2.11")
    $candidates += "C:\SGDK\sgdk-2.11"
    $candidates += "C:\sgdk\sgdk-2.11"
    foreach ($c in $candidates) {
        if (-not $c) { continue }
        $gen = Join-Path $c "makefile.gen"
        if (Test-Path -LiteralPath $gen -PathType Leaf) {
            return $c
        }
    }
    return $localGdk
}

function Get-UsablePythonPath {
    return SGDK_GetPythonPath
}

function Get-MagickPathResolved {
    return SGDK_GetMagickPath
}

$blockingFailures = 0
$softWarnings = 0

try {
    $mdRoot = Resolve-MegaDriveRoot -ExplicitRoot $RepoRoot
    if (-not (Test-Path -LiteralPath $mdRoot -PathType Container)) {
        Write-PreflightLog "ERROR" "MD_ROOT invalido ou inexistente: $mdRoot"
        exit 1
    }
    Write-PreflightLog "INFO" "MD_ROOT=$mdRoot"

    $gdk = Resolve-GdkPath -MdRoot $mdRoot
    $makefileGen = Join-Path $gdk "makefile.gen"
    if (-not (Test-Path -LiteralPath $makefileGen -PathType Leaf)) {
        Write-PreflightLog "ERROR" "GDK sem makefile.gen. GDK candidato=$gdk. Defina GDK ou instale SGDK em sdk\sgdk-2.11."
        $script:blockingFailures++
    } else {
        Write-PreflightLog "OK" "GDK=$gdk"
    }

    if (-not (Test-CommandExists 'make')) {
        Write-PreflightLog "ERROR" "Comando 'make' nao encontrado no PATH (msys2 / toolchain SGDK)."
        $script:blockingFailures++
    } else {
        Write-PreflightLog "OK" "make encontrado."
    }

    if (-not (Test-CommandExists 'java')) {
        Write-PreflightLog "ERROR" "Comando 'java' nao encontrado no PATH. ResComp precisa de Java; build_inner.bat tenta corrigir PATH em alguns setups."
        $script:blockingFailures++
    } else {
        Write-PreflightLog "OK" "java encontrado."
    }

    $py = Get-UsablePythonPath
    if (-not $py) {
        Write-PreflightLog "WARN" "Python utilizavel nao encontrado (stub WindowsApps ignorado). validate_resources / analyze_aesthetic podem falhar."
        $script:softWarnings++
    } else {
        Write-PreflightLog "OK" "Python=$py"
    }

    $magick = Get-MagickPathResolved
    if (-not $magick) {
        Write-PreflightLog "WARN" "ImageMagick magick.exe nao encontrado. Validador pode degradar para header PNG."
        $script:softWarnings++
    } else {
        Write-PreflightLog "OK" "ImageMagick=$magick"
    }

    if ($script:blockingFailures -gt 0) {
        Write-PreflightLog "ERROR" ("Preflight FALHOU: {0} check(s) obrigatorio(s)." -f $script:blockingFailures)
        exit 1
    }
    if ($script:softWarnings -gt 0) {
        Write-PreflightLog "WARN" ("Preflight OK com {0} aviso(s) (ferramentas opcionais)." -f $script:softWarnings)
        exit 2
    }
    Write-PreflightLog "INFO" "Preflight OK sem avisos."
    exit 0
}
catch {
    Write-PreflightLog "ERROR" "Excecao: $($_.Exception.Message)"
    exit 1
}
