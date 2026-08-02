<#
.SYNOPSIS
    Garante que os dois motores de hash de payload de skill produzem o mesmo valor.

.DESCRIPTION
    `content_sha256` no skill_lifecycle_registry.json e computado por DOIS
    consumidores independentes:

      - tools/sgdk_wrapper/audit_skill_lifecycle.ps1        (PowerShell)
      - tools/sgdk_wrapper/.agent/scripts/validate_skill_framework.py (Python)

    Eles usavam a mesma formula de payload mas ordens de arquivo diferentes:
    o Python ordena o caminho relativo POSIX em ordinal; o PowerShell usava
    `Sort-Object FullName`, que e case-insensitive e cultural. Em qualquer
    payload com subdiretorio (`agents/openai.yaml` + `SKILL.md`) a ordem
    invertia e os hashes divergiam.

    O sintoma era invisivel e permanente: satisfazer um motor quebrava o outro,
    entao o registry so podia estar certo para um dos lados por vez. Todas as
    13 skills legacy tem subdiretorio, o que produzia exatamente 13 erros de
    um lado ou do outro.

    Este gate compara os dois motores arquivo a arquivo e falha se divergirem,
    incluindo um payload sintetico construido para expor o caso de ordenacao.
#>

$ErrorActionPreference = "Stop"

$wrapperRoot = Split-Path -Parent $PSScriptRoot
$auditor = Join-Path $wrapperRoot "audit_skill_lifecycle.ps1"
$pythonValidator = Join-Path $wrapperRoot ".agent/scripts/validate_skill_framework.py"
$legacyRoot = Join-Path $wrapperRoot ".agent/legacy/skills"

foreach ($required in @($auditor, $pythonValidator)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "skill_hash_engine_parity_dependency_missing:$required"
    }
}

$python = Get-Command python -ErrorAction SilentlyContinue
$pythonArgs = @()
if ($null -eq $python) {
    $python = Get-Command python3 -ErrorAction SilentlyContinue
}
if ($null -eq $python) {
    $python = Get-Command py -ErrorAction SilentlyContinue
    $pythonArgs = @("-3")
}
if ($null -eq $python) {
    throw "python_runtime_missing"
}

# Importa Get-DirectoryContentHash do auditor sem executar o corpo dele.
$auditorText = Get-Content -LiteralPath $auditor -Raw
$match = [regex]::Match(
    $auditorText,
    '(?ms)^function Get-DirectoryContentHash \{.*?^\}'
)
if (-not $match.Success) {
    throw "skill_hash_engine_parity_function_not_found:Get-DirectoryContentHash"
}
. ([scriptblock]::Create($match.Value))

function Get-PythonDirectoryHash {
    param([Parameter(Mandatory = $true)][string]$Path)

    $script = @'
import hashlib, sys
from pathlib import Path

root = Path(sys.argv[1])
payload = bytearray()
for file_path in sorted(p for p in root.rglob("*") if p.is_file()):
    payload.extend(file_path.relative_to(root).as_posix().encode("utf-8"))
    payload.extend(b"\0")
    payload.extend(hashlib.sha256(file_path.read_bytes()).hexdigest().encode("ascii"))
    payload.extend(b"\n")
print(hashlib.sha256(payload).hexdigest())
'@
    $tempScript = Join-Path ([System.IO.Path]::GetTempPath()) ("skill_hash_parity_" + [guid]::NewGuid().ToString("N") + ".py")
    try {
        Set-Content -LiteralPath $tempScript -Value $script -Encoding UTF8 -NoNewline
        $result = & $python.Path @pythonArgs $tempScript $Path
        if ($LASTEXITCODE -ne 0) {
            throw "python_hash_engine_failed:$Path"
        }
        return ([string]$result).Trim().ToLowerInvariant()
    }
    finally {
        Remove-Item -LiteralPath $tempScript -Force -ErrorAction SilentlyContinue
    }
}

$failures = New-Object System.Collections.Generic.List[string]
$checked = 0

function Assert-Parity {
    param([string]$Label, [string]$Path)

    $psHash = (Get-DirectoryContentHash -Path $Path).ToLowerInvariant()
    $pyHash = Get-PythonDirectoryHash -Path $Path
    $script:checked++
    if ($psHash -ne $pyHash) {
        $script:failures.Add("hash_engine_divergence:${Label}:pwsh=$psHash:python=$pyHash")
        Write-Host "FAIL $Label"
        Write-Host "     pwsh   = $psHash"
        Write-Host "     python = $pyHash"
        return
    }
    Write-Host "PASS $Label ($psHash)"
}

# 1. Payload sintetico que expoe o caso de ordenacao: um arquivo no topo cujo
#    nome comeca com maiuscula e um subdiretorio cujo nome comeca com minuscula.
#    Em ordem ordinal `SKILL.md` (0x53) vem antes de `agents/` (0x61); em ordem
#    cultural/case-insensitive vem depois. Se os motores discordarem de ordenacao,
#    este caso falha mesmo que a arvore real esteja vazia.
$fixture = Join-Path ([System.IO.Path]::GetTempPath()) ("skill_hash_parity_fixture_" + [guid]::NewGuid().ToString("N"))
try {
    New-Item -ItemType Directory -Force -Path (Join-Path $fixture "agents") | Out-Null
    New-Item -ItemType Directory -Force -Path (Join-Path $fixture "Zresources") | Out-Null
    Set-Content -LiteralPath (Join-Path $fixture "SKILL.md") -Value "# fixture" -Encoding UTF8
    Set-Content -LiteralPath (Join-Path $fixture "agents/openai.yaml") -Value "name: fixture" -Encoding UTF8
    Set-Content -LiteralPath (Join-Path $fixture "Zresources/notes.md") -Value "notes" -Encoding UTF8
    Assert-Parity -Label "fixture/ordering-edge-case" -Path $fixture
}
finally {
    Remove-Item -LiteralPath $fixture -Recurse -Force -ErrorAction SilentlyContinue
}

# 2. Todos os payloads legacy reais.
if (-not (Test-Path -LiteralPath $legacyRoot -PathType Container)) {
    throw "skill_hash_engine_parity_legacy_root_missing:$legacyRoot"
}
foreach ($skillFile in (Get-ChildItem -LiteralPath $legacyRoot -Filter "SKILL.md" -File -Recurse | Sort-Object FullName)) {
    $skillDir = Split-Path -Parent $skillFile.FullName
    $label = "legacy/" + (Resolve-Path -LiteralPath $skillDir).Path.Substring((Resolve-Path -LiteralPath $legacyRoot).Path.Length + 1).Replace("\", "/")
    Assert-Parity -Label $label -Path $skillDir
}

Write-Host ""
if ($failures.Count -gt 0) {
    Write-Host "skill hash engine parity: $checked verificados, $($failures.Count) divergentes"
    foreach ($failure in $failures) { Write-Host "- $failure" }
    exit 1
}

Write-Host "PASS skill hash engine parity ($checked payloads, pwsh == python)"
exit 0
