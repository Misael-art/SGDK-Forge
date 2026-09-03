<#
.SYNOPSIS
  Pre-flight do host + validate_resources no projeto dourado (referencia para CI local).
  Roda tambem o regression-guard generalista do novo validator de especializacoes.

.NOTES
  Exit 1 se preflight bloqueante ou validacao falhar.
  Preflight exit 2 (avisos Python/Magick) e aceite como sucesso para nao bloquear CI minimo.
#>
[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ciRoot = $PSScriptRoot
$wrapperRoot = [System.IO.Path]::GetFullPath((Join-Path $ciRoot ".."))
$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $wrapperRoot "..\.."))
$powerShellHost = Get-Command pwsh -ErrorAction SilentlyContinue
if ($null -eq $powerShellHost) {
    $powerShellHost = Get-Command powershell -ErrorAction SilentlyContinue
}
if ($null -eq $powerShellHost) {
    throw "Nenhum host PowerShell encontrado (pwsh/powershell)."
}

# Generalista regression-guard: validator de especializacoes nao pode quebrar
# projetos gerais. Roda contra uma fixture sem doc/genre_specialization_manifest.json.
# Executa antes da checagem de golden targets para garantir cobertura mesmo
# quando o workspace nao tem projeto dourado.
$generalistaTest = Join-Path $ciRoot "test_genre_specialization_generalista_unchanged.ps1"
& $powerShellHost.Source -NoProfile -ExecutionPolicy Bypass -File $generalistaTest
if ($LASTEXITCODE -ne 0) {
    Write-Error "test_genre_specialization_generalista_unchanged.ps1 falhou."
    exit 1
}

# Projeto dourado: laboratorio visual estavel no monorepo
$GoldenProjectRelative = "SGDK_projects\BENCHMARK_VISUAL_LAB"
$goldenPath = Join-Path $repoRoot $GoldenProjectRelative

$goldenTargets = @()
if (Test-Path -LiteralPath $goldenPath -PathType Container) {
    $goldenTargets += [pscustomobject]@{
        Relative = $GoldenProjectRelative
        Path = $goldenPath
    }
} else {
    $projectsRoot = Join-Path $repoRoot "SGDK_projects"
    $effectLabTargets = @(Get-ChildItem -LiteralPath $projectsRoot -Directory -Filter "AAA EFFECT LAB - *" | Sort-Object Name)
    foreach ($target in $effectLabTargets) {
        $goldenTargets += [pscustomobject]@{
            Relative = "SGDK_projects\$($target.Name)"
            Path = $target.FullName
        }
    }
}

if ($goldenTargets.Count -eq 0) {
    Write-Host "[ci] run_golden_validate.ps1: nenhum projeto dourado encontrado; generalista guard passou, encerrando com sucesso."
    exit 0
}

$preflight = Join-Path $wrapperRoot "preflight_host.ps1"
& $preflight -RepoRoot $repoRoot
$pf = $LASTEXITCODE
if ($pf -eq 1) {
    Write-Error "preflight_host.ps1 falhou (checks obrigatorios)."
    exit 1
}
if ($pf -eq 2) {
    Write-Warning "preflight_host.ps1 concluiu com avisos opcionais (exit 2) - prosseguindo."
}

$validate = Join-Path $wrapperRoot "validate_resources.ps1"
foreach ($target in $goldenTargets) {
    & $powerShellHost.Source -NoProfile -ExecutionPolicy Bypass -File $validate -WorkDir $target.Path -CloseoutGate
    if ($LASTEXITCODE -ne 0) {
        Write-Error "validate_resources.ps1 falhou para $($target.Path)."
        exit 1
    }
}

Write-Host "[ci] run_golden_validate.ps1 OK (targets: $($goldenTargets.Count))"
exit 0
