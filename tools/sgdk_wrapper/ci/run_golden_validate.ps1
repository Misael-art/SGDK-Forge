<#
.SYNOPSIS
  Pre-flight do host + validate_resources no projeto dourado (referencia para CI local).
  Roda tambem o regression-guard generalista do novo validator de especializacoes.
  Para build e observacao BlastEm no Linux: python3 tools/sgdk_wrapper/ci/run_reference_e2e.py.
  Este script valida recursos; nao executa nem certifica E2E.

.NOTES
  Exit 1 se preflight bloqueante ou validacao falhar.
  Preflight exit 2 (avisos Python/Magick) e aceite como sucesso para nao bloquear CI minimo.
#>
[CmdletBinding()]
param(
    [string]$GoldenProjectRelative = "SGDK_projects/FORGE_REFERENCE [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]",
    [switch]$DeliveryCloseout
)

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
$goldenPath = Join-Path $repoRoot $GoldenProjectRelative

$goldenTargets = @()
if (Test-Path -LiteralPath $goldenPath -PathType Container) {
    $goldenTargets += [pscustomobject]@{
        Relative = $GoldenProjectRelative
        Path = $goldenPath
    }
}

if ($goldenTargets.Count -eq 0) {
    Write-Host "[ci] BLOCKED: alvo obrigatorio ausente: $GoldenProjectRelative; integracao nao executada."
    exit 1
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
    $validationArgs = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $validate, '-WorkDir', $target.Path)
    # A neutral technical fixture is not a game delivery. Preserve the full
    # delivery gate as an explicit scope, rather than forcing AAA on this lab.
    if ($DeliveryCloseout) { $validationArgs += '-CloseoutGate' }
    & $powerShellHost.Source @validationArgs
    if ($LASTEXITCODE -ne 0) {
        Write-Error "validate_resources.ps1 falhou para $($target.Path)."
        exit 1
    }
}

Write-Host "[ci] resource_validation OK (targets: $($goldenTargets.Count)); build/playtest nao executados por este script."
exit 0
