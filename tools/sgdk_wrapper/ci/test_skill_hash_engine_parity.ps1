<#
.SYNOPSIS
    Prova que os motores PowerShell e Python de hash de payload sao um contrato
    unico, identico em Windows e Linux.

.DESCRIPTION
    `content_sha256` no skill_lifecycle_registry.json e computado por DOIS
    motores independentes:

      - tools/sgdk_wrapper/lib/skill_payload_hash.psm1              (PowerShell)
      - tools/sgdk_wrapper/.agent/scripts/validate_skill_framework.py (Python)

    Historico do defeito: existiam TRES implementacoes. `audit_skill_lifecycle.ps1`
    e `ci/test_skill_lifecycle_registry.ps1` mantinham copias proprias, a segunda
    ainda com `Sort-Object FullName` (cultural, case-insensitive) e separador `\`
    literal. Em qualquer payload com subdiretorio a ordem invertia e o hash
    divergia; no Linux a chave relativa saia errada por completo. O sintoma era
    `restoration fixture hash mismatch`, e satisfazer um motor quebrava o outro.

    Este gate nao reimplementa nada. Importa a funcao REAL de cada lado -- o
    modulo PowerShell e a funcao `directory_hash` do validador Python -- e prova
    o contrato. Uma copia embutida no teste provaria apenas que a copia concorda
    consigo mesma.

    Cobertura:

      1. paridade dos dois motores em fixtures dirigidas e nos payloads legacy;
      2. LF e CRLF do mesmo texto produzem o MESMO hash;
      3. binario com bytes CRLF permanece byte-exato (hash DIFERENTE);
      4. arquivo na raiz e em subdiretorio, e diferenca de caixa nos nomes;
      5. caminho Windows e POSIX convergem para a mesma chave relativa;
      6. os conjuntos de extensoes textuais dos dois lados sao identicos;
      7. mutantes: reintroduzir `Sort-Object FullName`, `sorted(Path)` ou
         remover a normalizacao CRLF faz este gate falhar.
#>

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$wrapperRoot = Split-Path -Parent $PSScriptRoot
$pythonValidator = Join-Path $wrapperRoot ".agent/scripts/validate_skill_framework.py"
$auditor = Join-Path $wrapperRoot "audit_skill_lifecycle.ps1"
$hashModule = Join-Path $wrapperRoot "lib/skill_payload_hash.psm1"
$legacyRoot = Join-Path $wrapperRoot ".agent/legacy/skills"

foreach ($required in @($pythonValidator, $auditor, $hashModule)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "skill_hash_engine_parity_dependency_missing:$required"
    }
}

. (Join-Path $PSScriptRoot "../lib/host_executors_bootstrap.ps1")
. (Join-Path $PSScriptRoot "../lib/skill_payload_hash_bootstrap.ps1")
$python = Get-PythonExecutable

$failures = New-Object System.Collections.Generic.List[string]
$checked = 0

function Add-Failure {
    param([Parameter(Mandatory = $true)][string]$Detail)
    $script:failures.Add($Detail)
    Write-Host "FAIL $Detail"
}

function Assert-Check {
    param(
        [Parameter(Mandatory = $true)][string]$Label,
        [Parameter(Mandatory = $true)][bool]$Condition,
        [Parameter(Mandatory = $false)][string]$Detail = ""
    )
    $script:checked++
    if ($Condition) {
        Write-Host "PASS $Label"
        return
    }
    Add-Failure ("{0}{1}" -f $Label, $(if ($Detail) { ":$Detail" } else { "" }))
}

# ---------------------------------------------------------------------------
# Ponte para o motor Python real.
# ---------------------------------------------------------------------------

function Invoke-PythonHarness {
    <#
    .SYNOPSIS
        Executa um snippet Python que ja tem o validador real importado.
    #>
    param(
        [Parameter(Mandatory = $true)][string]$Body,
        [Parameter(Mandatory = $false)][string[]]$Arguments = @()
    )

    $preamble = @'
import importlib.util, sys
spec = importlib.util.spec_from_file_location("validate_skill_framework", sys.argv[1])
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)
'@
    $script = $preamble + "`n" + $Body
    $tempScript = Join-Path ([System.IO.Path]::GetTempPath()) ("skill_hash_parity_" + [guid]::NewGuid().ToString("N") + ".py")
    try {
        Set-Content -LiteralPath $tempScript -Value $script -Encoding UTF8
        $output = & $python $tempScript $pythonValidator @Arguments 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw ("python_harness_failed:{0}" -f (($output | Out-String).Trim()))
        }
        return ([string]($output | Out-String)).Trim()
    }
    finally {
        Remove-Item -LiteralPath $tempScript -Force -ErrorAction SilentlyContinue
    }
}

function Get-PythonPayloadHash {
    param([Parameter(Mandatory = $true)][string]$Path)

    return (Invoke-PythonHarness -Body @'
from pathlib import Path
print(validator.directory_hash(Path(sys.argv[2])))
'@ -Arguments @($Path)).ToLowerInvariant()
}

function New-Fixture {
    param([Parameter(Mandatory = $true)][string]$Name)
    $path = Join-Path ([System.IO.Path]::GetTempPath()) ("skill_hash_fx_${Name}_" + [guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Force -Path $path | Out-Null
    return $path
}

function Set-FixtureBytes {
    <#
    .SYNOPSIS
        Escreve bytes exatos, sem traducao de fim de linha do PowerShell.
    #>
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][byte[]]$Bytes
    )
    $parent = Split-Path -Parent $Path
    if ($parent -and -not (Test-Path -LiteralPath $parent -PathType Container)) {
        New-Item -ItemType Directory -Force -Path $parent | Out-Null
    }
    [System.IO.File]::WriteAllBytes($Path, $Bytes)
}

function Get-Ascii {
    param([Parameter(Mandatory = $true)][AllowEmptyString()][string]$Text)
    return [System.Text.Encoding]::ASCII.GetBytes($Text)
}

function Assert-Parity {
    <#
    .SYNOPSIS
        Os dois motores devem concordar; retorna o hash comum ou $null.
    #>
    param(
        [Parameter(Mandatory = $true)][string]$Label,
        [Parameter(Mandatory = $true)][string]$Path
    )

    $psHash = (Get-SkillPayloadHash -Path $Path).ToLowerInvariant()
    $pyHash = Get-PythonPayloadHash -Path $Path
    $script:checked++
    if ($psHash -ne $pyHash) {
        Add-Failure "hash_engine_divergence:${Label}:pwsh=$psHash:python=$pyHash"
        return $null
    }
    Write-Host "PASS parity $Label ($psHash)"
    return $psHash
}

$tempRoots = New-Object System.Collections.Generic.List[string]
try {
    # -----------------------------------------------------------------------
    # 1. Ordenacao: arquivo na raiz + subdiretorios com caixas diferentes.
    #    Em ordem ordinal `SKILL.md` (0x53) precede `agents/` (0x61); em ordem
    #    cultural/case-insensitive a relacao inverte. Cobre raiz e subdiretorio.
    # -----------------------------------------------------------------------
    $ordering = New-Fixture -Name "ordering"
    $tempRoots.Add($ordering)
    Set-FixtureBytes -Path (Join-Path $ordering "SKILL.md") -Bytes (Get-Ascii "# fixture`n")
    Set-FixtureBytes -Path (Join-Path $ordering "agents/openai.yaml") -Bytes (Get-Ascii "name: fixture`n")
    Set-FixtureBytes -Path (Join-Path $ordering "Zresources/notes.md") -Bytes (Get-Ascii "notes`n")
    Set-FixtureBytes -Path (Join-Path $ordering "aresources/notes.md") -Bytes (Get-Ascii "notes`n")
    Assert-Parity -Label "ordering/root-and-subdirs" -Path $ordering | Out-Null

    # -----------------------------------------------------------------------
    # 2. Caixa nos nomes: `Alpha.md` e `alpha.md` coexistem no Linux. Ordem
    #    ordinal poe maiuscula antes; ordem cultural poe minuscula antes.
    #    No Windows os dois arquivos colidem, entao a fixture se adapta -- o que
    #    importa e que os dois motores concordem no que o host suporta.
    # -----------------------------------------------------------------------
    $caseFixture = New-Fixture -Name "case"
    $tempRoots.Add($caseFixture)
    Set-FixtureBytes -Path (Join-Path $caseFixture "Alpha.md") -Bytes (Get-Ascii "A`n")
    Set-FixtureBytes -Path (Join-Path $caseFixture "beta.md") -Bytes (Get-Ascii "b`n")
    $lowerAlpha = Join-Path $caseFixture "alpha.md"
    if (-not (Test-Path -LiteralPath $lowerAlpha -PathType Leaf)) {
        Set-FixtureBytes -Path $lowerAlpha -Bytes (Get-Ascii "a`n")
    }
    Assert-Parity -Label "ordering/case-sensitivity" -Path $caseFixture | Out-Null

    # -----------------------------------------------------------------------
    # 3. CRLF vs LF em extensao textual: MESMO hash.
    # -----------------------------------------------------------------------
    $lfFixture = New-Fixture -Name "lf"
    $crlfFixture = New-Fixture -Name "crlf"
    $tempRoots.Add($lfFixture)
    $tempRoots.Add($crlfFixture)
    Set-FixtureBytes -Path (Join-Path $lfFixture "SKILL.md") -Bytes (Get-Ascii "# title`nline one`nline two`n")
    Set-FixtureBytes -Path (Join-Path $lfFixture "agents/openai.yaml") -Bytes (Get-Ascii "name: x`nvalue: y`n")
    Set-FixtureBytes -Path (Join-Path $crlfFixture "SKILL.md") -Bytes (Get-Ascii "# title`r`nline one`r`nline two`r`n")
    Set-FixtureBytes -Path (Join-Path $crlfFixture "agents/openai.yaml") -Bytes (Get-Ascii "name: x`r`nvalue: y`r`n")

    $lfHash = Assert-Parity -Label "eol/lf" -Path $lfFixture
    $crlfHash = Assert-Parity -Label "eol/crlf" -Path $crlfFixture
    Assert-Check -Label "eol/crlf-equals-lf" `
        -Condition ($null -ne $lfHash -and $lfHash -eq $crlfHash) `
        -Detail "lf=$lfHash crlf=$crlfHash"

    # CR solitario (Mac classico) tambem colapsa para LF.
    $crFixture = New-Fixture -Name "cr"
    $tempRoots.Add($crFixture)
    Set-FixtureBytes -Path (Join-Path $crFixture "SKILL.md") -Bytes (Get-Ascii "# title`rline one`rline two`r")
    Set-FixtureBytes -Path (Join-Path $crFixture "agents/openai.yaml") -Bytes (Get-Ascii "name: x`rvalue: y`r")
    $crHash = Assert-Parity -Label "eol/cr" -Path $crFixture
    Assert-Check -Label "eol/cr-equals-lf" `
        -Condition ($null -ne $lfHash -and $lfHash -eq $crHash) `
        -Detail "lf=$lfHash cr=$crHash"

    # -----------------------------------------------------------------------
    # 4. Binario com bytes CRLF: NAO normaliza, hash DIFERENTE do gemeo LF.
    # -----------------------------------------------------------------------
    $binCrlf = New-Fixture -Name "bincrlf"
    $binLf = New-Fixture -Name "binlf"
    $tempRoots.Add($binCrlf)
    $tempRoots.Add($binLf)
    Set-FixtureBytes -Path (Join-Path $binCrlf "payload.bin") -Bytes ([byte[]]@(0x01, 0x0D, 0x0A, 0x02, 0x0D, 0x03))
    Set-FixtureBytes -Path (Join-Path $binLf "payload.bin") -Bytes ([byte[]]@(0x01, 0x0A, 0x02, 0x0A, 0x03))
    $binCrlfHash = Assert-Parity -Label "binary/crlf-bytes" -Path $binCrlf
    $binLfHash = Assert-Parity -Label "binary/lf-bytes" -Path $binLf
    Assert-Check -Label "binary/stays-byte-exact" `
        -Condition ($null -ne $binCrlfHash -and $null -ne $binLfHash -and $binCrlfHash -ne $binLfHash) `
        -Detail "crlf=$binCrlfHash lf=$binLfHash"

    # -----------------------------------------------------------------------
    # 5. Caminho Windows e POSIX convergem para a mesma chave relativa.
    #    Um caminho com separador nativo, um com `/` e um com componente `.`
    #    devem produzir a mesma chave nos dois motores.
    # -----------------------------------------------------------------------
    $keyRoot = New-Fixture -Name "keys"
    $tempRoots.Add($keyRoot)
    Set-FixtureBytes -Path (Join-Path $keyRoot "agents/openai.yaml") -Bytes (Get-Ascii "name: k`n")
    $nativeVariant = Join-Path (Join-Path $keyRoot "agents") "openai.yaml"
    $slashVariant = $keyRoot.Replace('\', '/') + "/agents/openai.yaml"
    $dottedVariant = Join-Path $keyRoot "./agents/openai.yaml"
    $expectedKey = "agents/openai.yaml"
    foreach ($variant in @(
            @{ Label = "native"; Value = $nativeVariant },
            @{ Label = "posix-slash"; Value = $slashVariant },
            @{ Label = "dot-component"; Value = $dottedVariant }
        )) {
        $psKey = Get-SkillPayloadRelativeKey -Root $keyRoot -FullPath $variant.Value
        Assert-Check -Label "relkey/pwsh/$($variant.Label)" `
            -Condition ($psKey -eq $expectedKey) -Detail "got=$psKey"
    }
    $pyKey = Invoke-PythonHarness -Body @'
from pathlib import Path
root = Path(sys.argv[2])
print(validator.relative_key(root, Path(sys.argv[3]).resolve()))
'@ -Arguments @($keyRoot, $dottedVariant)
    Assert-Check -Label "relkey/python/matches-pwsh" `
        -Condition ($pyKey -eq $expectedKey) -Detail "got=$pyKey"

    # Chave nao-portavel deve ser rejeitada nos dois lados, nao silenciosamente
    # hasheada em uma ordem que os motores nao garantem.
    $psRejected = $false
    try { Assert-SkillPayloadRelativeKey -Key "a`u{1F600}b.md" | Out-Null }
    catch { $psRejected = $true }
    Assert-Check -Label "relkey/pwsh/rejects-non-ascii" -Condition $psRejected
    $pyRejected = Invoke-PythonHarness -Body @'
try:
    validator.assert_relative_key("a\U0001F600b.md")
    print("accepted")
except ValueError:
    print("rejected")
'@
    Assert-Check -Label "relkey/python/rejects-non-ascii" `
        -Condition ($pyRejected -eq "rejected") -Detail "got=$pyRejected"

    # -----------------------------------------------------------------------
    # 6. Os conjuntos de extensoes textuais devem ser identicos. Se um lado
    #    ganhar `.cfg` e o outro nao, os hashes divergem apenas em repos com
    #    aquele arquivo -- falha rara e dificil de rastrear.
    # -----------------------------------------------------------------------
    $psExtensions = (Get-SkillPayloadTextExtension | Sort-Object) -join ","
    $pyExtensions = Invoke-PythonHarness -Body @'
print(",".join(sorted(validator.TEXT_EXTENSIONS)))
'@
    Assert-Check -Label "contract/text-extensions-match" `
        -Condition ($psExtensions -eq $pyExtensions) `
        -Detail "pwsh=[$psExtensions] python=[$pyExtensions]"

    # -----------------------------------------------------------------------
    # 7. Mutantes. Cada um reintroduz um defeito real ja observado; se o gate
    #    continuar verde com o mutante, o gate nao esta provando nada.
    # -----------------------------------------------------------------------

    # 7a. `Sort-Object FullName` no lado PowerShell.
    function Get-MutantSortObjectHash {
        param([string]$Path)
        $payload = ""
        foreach ($file in Get-ChildItem -LiteralPath $Path -File -Recurse | Sort-Object FullName) {
            $baseFull = [IO.Path]::GetFullPath($Path).TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
            $relative = [IO.Path]::GetFullPath($file.FullName).Substring($baseFull.Length).Replace("\", "/")
            $bytes = [IO.File]::ReadAllBytes($file.FullName)
            $fileHash = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($bytes)).ToLowerInvariant()
            $payload += "$relative`0$fileHash`n"
        }
        return [Convert]::ToHexString(
            [Security.Cryptography.SHA256]::HashData([Text.Encoding]::UTF8.GetBytes($payload))
        ).ToLowerInvariant()
    }
    $mutantSort = Get-MutantSortObjectHash -Path $ordering
    $canonicalOrdering = (Get-SkillPayloadHash -Path $ordering).ToLowerInvariant()
    Assert-Check -Label "mutant/sort-object-fullname-detected" `
        -Condition ($mutantSort -ne $canonicalOrdering) `
        -Detail "mutante concorda com o canonico; a fixture de ordenacao deixou de expor o defeito"

    # 7b. `sorted(Path)` no lado Python. Em PosixPath a ordem coincide com a
    #     ordinal, entao o mutante e provado pela chave que ele produziria em
    #     WindowsPath: comparacao case-insensitive por componentes.
    $mutantPathOrder = Invoke-PythonHarness -Body @'
from pathlib import PurePosixPath, PureWindowsPath
names = ["SKILL.md", "agents/openai.yaml", "Zresources/notes.md", "aresources/notes.md"]
canonical = sorted(names)
posix_order = [str(p) for p in sorted(PurePosixPath(n) for n in names)]
windows_order = [str(PureWindowsPath(p)).replace("\\", "/") for p in sorted(PureWindowsPath(n) for n in names)]
print("canonical_eq_posix" if canonical == posix_order else "canonical_ne_posix")
print("windows_diverges" if windows_order != canonical else "windows_agrees")
'@
    $mutantLines = @($mutantPathOrder -split "`r?`n" | Where-Object { $_ })
    Assert-Check -Label "mutant/sorted-path-diverges-on-windows" `
        -Condition ($mutantLines -contains "windows_diverges") `
        -Detail ("sorted(Path) nao divergiu; saida=" + ($mutantLines -join "|"))

    # 7c. Remover a normalizacao CRLF.
    $mutantNoNormalize = Invoke-PythonHarness -Body @'
import hashlib
from pathlib import Path

def raw_hash(root: Path) -> str:
    payload = bytearray()
    for key in sorted(
        p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()
    ):
        payload.extend(key.encode("utf-8"))
        payload.extend(b"\0")
        payload.extend(hashlib.sha256((root / key).read_bytes()).hexdigest().encode("ascii"))
        payload.extend(b"\n")
    return hashlib.sha256(payload).hexdigest()

lf, crlf = Path(sys.argv[2]), Path(sys.argv[3])
print("mutant_diverges" if raw_hash(lf) != raw_hash(crlf) else "mutant_agrees")
print("canonical_agrees" if validator.directory_hash(lf) == validator.directory_hash(crlf) else "canonical_diverges")
'@ -Arguments @($lfFixture, $crlfFixture)
    $normalizeLines = @($mutantNoNormalize -split "`r?`n" | Where-Object { $_ })
    Assert-Check -Label "mutant/no-crlf-normalization-detected" `
        -Condition ($normalizeLines -contains "mutant_diverges" -and $normalizeLines -contains "canonical_agrees") `
        -Detail ("saida=" + ($normalizeLines -join "|"))

    # -----------------------------------------------------------------------
    # 8. Todos os payloads legacy reais.
    # -----------------------------------------------------------------------
    if (-not (Test-Path -LiteralPath $legacyRoot -PathType Container)) {
        throw "skill_hash_engine_parity_legacy_root_missing:$legacyRoot"
    }
    $legacyFull = [System.IO.Path]::GetFullPath($legacyRoot)
    $legacyDirs = @{}
    foreach ($skillFile in (Get-ChildItem -LiteralPath $legacyFull -Filter "SKILL.md" -File -Recurse)) {
        $skillDir = Split-Path -Parent $skillFile.FullName
        $legacyDirs[(Get-SkillPayloadRelativeKey -Root $legacyFull -FullPath $skillDir)] = $skillDir
    }
    $legacyKeys = [string[]]@($legacyDirs.Keys)
    [System.Array]::Sort($legacyKeys, [System.StringComparer]::Ordinal)
    if ($legacyKeys.Count -eq 0) {
        throw "skill_hash_engine_parity_legacy_payloads_missing:$legacyFull"
    }
    foreach ($key in $legacyKeys) {
        Assert-Parity -Label "legacy/$key" -Path $legacyDirs[$key] | Out-Null
    }

    # -----------------------------------------------------------------------
    # 9. Nenhuma implementacao paralela de hash deve ressurgir.
    # -----------------------------------------------------------------------
    $canonicalOwners = @(
        (Join-Path $wrapperRoot "lib/skill_payload_hash.psm1"),
        $pythonValidator,
        $PSCommandPath
    ) | ForEach-Object { [System.IO.Path]::GetFullPath($_) }

    $duplicates = New-Object System.Collections.Generic.List[string]
    foreach ($candidate in (Get-ChildItem -LiteralPath $wrapperRoot -Recurse -File -Include "*.ps1", "*.psm1" -Force)) {
        $candidateFull = [System.IO.Path]::GetFullPath($candidate.FullName)
        if ($canonicalOwners -contains $candidateFull) { continue }
        $text = Get-Content -LiteralPath $candidateFull -Raw -ErrorAction SilentlyContinue
        if ([string]::IsNullOrEmpty($text)) { continue }
        if ($text -match 'function\s+Get-DirectoryContentHash') {
            $duplicates.Add((Get-SkillPayloadRelativeKey -Root $wrapperRoot -FullPath $candidateFull))
        }
    }
    Assert-Check -Label "contract/no-duplicate-hash-implementation" `
        -Condition ($duplicates.Count -eq 0) `
        -Detail ("implementacoes paralelas: " + ($duplicates -join ", "))
}
finally {
    foreach ($root in $tempRoots) {
        Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Write-Host ""
if ($failures.Count -gt 0) {
    Write-Host "skill hash engine parity: $checked verificacoes, $($failures.Count) falhas"
    foreach ($failure in $failures) { Write-Host "- $failure" }
    exit 1
}

Write-Host "PASS skill hash engine parity ($checked verificacoes, pwsh == python, LF/CRLF/binario/ordenacao cobertos)"
exit 0
