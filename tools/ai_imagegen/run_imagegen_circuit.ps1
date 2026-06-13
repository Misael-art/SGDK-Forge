#!/usr/bin/env pwsh
# run_imagegen_circuit.ps1
# Wrapper PowerShell do imagegen_circuit.py (Ring 1).
# Usado pelo agente (art-creation-sourcing::RotaA::passo3) ou pelo usuario.
#
# Aceita args estilo Unix (--asset-role concept_art) e repassa ao Python.
# O uso de `--%` no call interno do Python faz o PowerShell 5.1 repassar
# os args sem consumir `--` como end-of-options.
#
# Uso:
#   .\run_imagegen_circuit.ps1 preflight --project "<nome>" --asset-role concept_art [--style-manifest PATH] [--json]
#   .\run_imagegen_circuit.ps1 run       --project "<nome>" --asset-role concept_art --prompt "..." [--seed 42] [--dry-run] [--json]
#
# Exit codes (espelham imagegen_circuit.py):
#   0  ok
#   2  license_blocked
#   3  scope_blocked
#   4  blocked_host_capability
#   5  forbidden scope
#   6  backend refused
#   7  filesystem error
#
# Este wrapper NAO escreve em res/. Toda persistencia eh em
# <project>/data/raw_ai/, <project>/data/source_art/ ou <project>/out/logs/.

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$Python = & python -c "import sys; print(sys.executable)"

if ($args.Count -lt 1) {
    Write-Error "Usage: run_imagegen_circuit.ps1 {preflight|run} [args...]"
    exit 7
}

$Command = [string]$args[0]
if ($Command -ne "preflight" -and $Command -ne "run") {
    Write-Error "ERROR: first arg must be 'preflight' or 'run' (got: $Command)"
    exit 7
}

# Constroi uma unica string de args para passar via --% (stop-parsing).
# --% faz o PowerShell 5.1 repassar args sem consumir `--` como end-of-options.
$ForwardArgs = $Command
if ($args.Count -gt 1) {
    $Rest = $args[1..($args.Count - 1)]
    foreach ($a in $Rest) {
        # Escapa aspas duplas internas e envolve em aspas se ha espacos.
        $s = [string]$a
        if ($s -match '\s') {
            $s = '"' + ($s -replace '"', '`"') + '"'
        }
        $ForwardArgs += " " + $s
    }
}

# `--%` (stop-parsing) garante que PowerShell nao consuma `--` no meio dos args.
Invoke-Expression "& '$Python' '$ScriptDir\imagegen_circuit.py' --% $ForwardArgs"
exit $LASTEXITCODE
