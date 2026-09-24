<#
.SYNOPSIS
    Garante que nenhum script canonico chame `powershell`/`powershell.exe`
    literalmente e que o helper central resolva os executores do host.

.DESCRIPTION
    Duas falhas distintas motivam este gate.

    1. Executor literal. `& powershell ...` nao existe no Linux; `powershell.exe`
       pode existir como stub Wine. Nos dois casos o processo filho falha e o
       gate chamador reporta "teste falhou", apontando o diagnostico para o
       projeto quando a causa era o host. Ao longo da suite isso produzia
       falso vermelho no Linux e mascarava o estado real do framework.

    2. Dependencia ausente tratada como skip. Um gate que nao rodou nao pode
       contar como gate que passou; o helper lanca erro explicito.

    O gate varre os .ps1 canonicos por invocacao literal e exercita o helper
    de ponta a ponta, incluindo propagacao de exit code -- se o exit code do
    filho fosse engolido, um teste vermelho seria lido como verde.

    Escopo da varredura: chamadas de EXECUCAO. Mencao em comentario, string de
    diagnostico ou `.bat` de entrada Windows nao e violacao; `.bat` so roda em
    Windows real, onde `powershell` existe por definicao.
#>

[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "../lib/host_executors_bootstrap.ps1")

$wrapperRoot = Split-Path -Parent $PSScriptRoot
$failures = New-Object System.Collections.Generic.List[string]
$checks = 0

function Assert-True {
    param([string]$Label, [bool]$Condition, [string]$Detail = "")
    $script:checks++
    if ($Condition) {
        Write-Host "PASS $Label"
        return
    }
    if ([string]::IsNullOrWhiteSpace($Detail)) {
        $script:failures.Add($Label)
    } else {
        $script:failures.Add("${Label}: $Detail")
    }
    Write-Host "FAIL $Label $Detail"
}

# ---------------------------------------------------------------------------
# 1. Resolucao de executores
# ---------------------------------------------------------------------------

$pwshExe = Get-PowerShellExecutable
Assert-True "pwsh resolvido" (-not [string]::IsNullOrWhiteSpace($pwshExe)) "valor='$pwshExe'"
Assert-True "pwsh existe no disco" (Test-Path -LiteralPath $pwshExe) "path='$pwshExe'"

# Um stub Wine satisfaria "existe" mas quebraria na execucao. Provar que o
# executor roda de verdade e emite o resultado esperado.
$echoed = & $pwshExe -NoProfile -Command 'Write-Output "executor_alive"'
Assert-True "pwsh executa" ("$echoed".Trim() -eq "executor_alive") "saida='$echoed'"

$pythonExe = Get-PythonExecutable
Assert-True "python resolvido" (Test-Path -LiteralPath $pythonExe) "path='$pythonExe'"

if (-not (Test-IsWindowsHost)) {
    Assert-True "pwsh nao e stub .exe no Linux" ($pwshExe -notmatch '\.exe$') "path='$pwshExe'"
}

# ---------------------------------------------------------------------------
# 2. Invoke-HostPowerShell: propagacao de exit code e blocker explicito
# ---------------------------------------------------------------------------

$tempDir = Join-Path ([System.IO.Path]::GetTempPath()) ("host_exec_gate_" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
try {
    $okScript = Join-Path $tempDir "ok.ps1"
    Set-Content -LiteralPath $okScript -Value 'Write-Output "child_ok"; exit 0' -Encoding UTF8
    $out = Invoke-HostPowerShell -ScriptPath $okScript
    Assert-True "filho bem-sucedido propaga 0" ($LASTEXITCODE -eq 0) "exit=$LASTEXITCODE"
    Assert-True "filho bem-sucedido devolve saida" ("$out".Trim() -eq "child_ok") "saida='$out'"

    # O caso critico: exit code nao-zero PRECISA chegar ao chamador. Se este
    # assert cair, todo gate que usa o helper reporta verde sobre teste vermelho.
    $failScript = Join-Path $tempDir "fail.ps1"
    Set-Content -LiteralPath $failScript -Value 'Write-Output "child_fail"; exit 3' -Encoding UTF8
    Invoke-HostPowerShell -ScriptPath $failScript | Out-Null
    Assert-True "filho falho propaga exit code" ($LASTEXITCODE -eq 3) "exit=$LASTEXITCODE"

    # Argumentos precisam chegar intactos, inclusive com espaco no valor.
    $argScript = Join-Path $tempDir "args.ps1"
    Set-Content -LiteralPath $argScript -Value 'param([string]$Label) Write-Output "got=$Label"' -Encoding UTF8
    $argOut = Invoke-HostPowerShell -ScriptPath $argScript -Arguments @('-Label', 'a b')
    Assert-True "argumentos com espaco preservados" ("$argOut".Trim() -eq "got=a b") "saida='$argOut'"

    # Script ausente e blocker, nunca skip silencioso.
    $threw = $false
    try {
        Invoke-HostPowerShell -ScriptPath (Join-Path $tempDir "absent.ps1") | Out-Null
    } catch {
        $threw = $_.Exception.Message -like "host_powershell_script_missing*"
    }
    Assert-True "script ausente bloqueia" $threw
}
finally {
    Remove-Item -LiteralPath $tempDir -Recurse -Force -ErrorAction SilentlyContinue
}

# ---------------------------------------------------------------------------
# 3. Varredura: nenhum .ps1 canonico invoca executor literal
# ---------------------------------------------------------------------------

# Casa apenas EXECUCAO:
#   & powershell ... / & powershell.exe ...
#   Start-Process powershell...
#   -Command "powershell..."  (executor embutido em string de comando)
# Nao casa comentario, texto de erro nem nome de variavel.
$literalPattern = '(&\s*powershell(\.exe)?[\s"'']|Start-Process\s+["'']?powershell(\.exe)?\b)'

# O proprio helper e este gate citam os nomes por contrato/diagnostico.
$allowList = @(
    'lib/host_executors.psm1',
    'ci/test_host_executor_resolution.ps1'
)

$scanned = 0
$violations = New-Object System.Collections.Generic.List[string]
foreach ($file in (Get-ChildItem -LiteralPath $wrapperRoot -Filter '*.ps1' -File -Recurse)) {
    $relative = $file.FullName.Substring($wrapperRoot.Length).TrimStart('/', '\').Replace('\', '/')
    if ($allowList -contains $relative) { continue }
    $scanned++

    $lineNumber = 0
    foreach ($line in (Get-Content -LiteralPath $file.FullName)) {
        $lineNumber++
        if ($line -match $literalPattern) {
            $violations.Add("${relative}:${lineNumber}: $($line.Trim())")
        }
    }
}

Assert-True "varredura encontrou scripts" ($scanned -gt 0) "scanned=$scanned"
Assert-True "nenhum executor literal em .ps1" ($violations.Count -eq 0) "violacoes=$($violations.Count)"
foreach ($violation in $violations) {
    Write-Host "     $violation"
}

Write-Host ""
if ($failures.Count -gt 0) {
    Write-Host "host executor resolution: $checks verificacoes, $($failures.Count) falha(s)"
    foreach ($failure in $failures) { Write-Host "- $failure" }
    exit 1
}

Write-Host "PASS host executor resolution ($checks verificacoes, $scanned scripts varridos)"
exit 0
