<#
.SYNOPSIS
  Pre-flight do host + validate_resources no projeto dourado (referencia para CI local).

.NOTES
  Exit 1 se preflight bloqueante ou validacao falhar.
  Preflight exit 2 (avisos Python/Magick) e aceite como sucesso para nao bloquear CI minimo.
#>
[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ciRoot = $PSScriptRoot
$wrapperRoot = Split-Path -LiteralPath $ciRoot -Parent
$repoRoot = Split-Path -LiteralPath $wrapperRoot -Parent
# Projeto dourado: laboratorio visual estavel no monorepo
$GoldenProjectRelative = "SGDK_projects\BENCHMARK_VISUAL_LAB"
$goldenPath = Join-Path $repoRoot $GoldenProjectRelative

if (-not (Test-Path -LiteralPath $goldenPath -PathType Container)) {
    Write-Error "Projeto dourado nao encontrado: $goldenPath. Ajuste GoldenProjectRelative em run_golden_validate.ps1."
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
    Write-Warning "preflight_host.ps1 concluiu com avisos opcionais (exit 2) — prosseguindo."
}

$validate = Join-Path $wrapperRoot "validate_resources.ps1"
& powershell -NoProfile -ExecutionPolicy Bypass -File $validate -WorkDir $goldenPath -CloseoutGate
if ($LASTEXITCODE -ne 0) {
    Write-Error "validate_resources.ps1 falhou para $goldenPath."
    exit 1
}

Write-Host "[ci] run_golden_validate.ps1 OK (golden: $GoldenProjectRelative)"
exit 0
