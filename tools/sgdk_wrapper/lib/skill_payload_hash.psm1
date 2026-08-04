<#
.SYNOPSIS
    Motor canonico de hash de payload de skill (lado PowerShell).

.DESCRIPTION
    `content_sha256` no skill_lifecycle_registry.json precisa ser identico em
    Windows e Linux, e identico entre PowerShell e Python. Antes deste modulo
    existiam TRES implementacoes independentes:

      - tools/sgdk_wrapper/audit_skill_lifecycle.ps1
      - tools/sgdk_wrapper/.agent/scripts/validate_skill_framework.py
      - tools/sgdk_wrapper/ci/test_skill_lifecycle_registry.ps1

    A terceira usava `Sort-Object FullName` e montava o caminho relativo com
    separador `\` literal, entao no Linux produzia chave errada e ordem errada.
    Sintoma observado: `restoration fixture hash mismatch`.

    CONTRATO CANONICO (o mesmo em ambos os motores):

      1. Chave de cada arquivo = caminho relativo a raiz do payload, com `/`
         como separador, preservando maiusculas/minusculas originais.
      2. Ordenacao explicita pela chave, ordinal (ordem de code point). Nunca
         ordenar objetos de caminho nem usar `Sort-Object`, que e cultural e
         case-insensitive.
      3. Chaves restritas a ASCII imprimivel e sem `\`. Isso NAO e cosmetico:
         `StringComparer.Ordinal` compara unidades UTF-16 e o `sorted()` do
         Python compara code points; as duas ordens divergem para caracteres
         fora do BMP. Restringindo a ASCII, a igualdade das ordens e provada,
         nao esperada. Um `\` no nome colidiria com o separador normalizado.
      4. Extensoes textuais declaradas (Get-SkillPayloadTextExtension) tem
         CRLF e CR solitario normalizados para LF antes do hash do arquivo.
         Assim o mesmo conteudo versionado com autocrlf ou sem produz o mesmo
         hash.
      5. Qualquer outra extensao e tratada como binaria e hasheada byte-exata.
         Um `.bin` que contenha 0x0D 0x0A NAO e alterado.
      6. Payload agregado = para cada entrada, em ordem:
         chave UTF-8 + 0x00 + sha256 hex minusculo + 0x0A.
      7. Hash final = sha256 do payload agregado, hex minusculo.

    O gate tools/sgdk_wrapper/ci/test_skill_hash_engine_parity.ps1 prova este
    contrato contra a funcao real do validador Python, inclusive provando que
    reintroduzir `Sort-Object FullName`, `sorted(Path)` ou remover a
    normalizacao CRLF faz o gate falhar.
#>

Set-StrictMode -Version Latest

# Ordem alfabetica por manutencao; a ordem nao afeta o hash. Deve permanecer
# identica a TEXT_EXTENSIONS em validate_skill_framework.py -- o gate de
# paridade compara os dois conjuntos e falha se divergirem.
$script:SkillPayloadTextExtensions = [string[]]@(
    '.bat',
    '.c',
    '.cfg',
    '.cmd',
    '.csv',
    '.h',
    '.ini',
    '.json',
    '.md',
    '.ps1',
    '.psd1',
    '.psm1',
    '.py',
    '.sh',
    '.svg',
    '.toml',
    '.txt',
    '.xml',
    '.yaml',
    '.yml'
)

$script:SkillPayloadTextExtensionSet = [System.Collections.Generic.HashSet[string]]::new(
    $script:SkillPayloadTextExtensions,
    [System.StringComparer]::Ordinal
)

function Get-SkillPayloadTextExtension {
    <#
    .SYNOPSIS
        Retorna as extensoes tratadas como texto pelo contrato canonico.
    #>
    [CmdletBinding()]
    param()

    return [string[]]@($script:SkillPayloadTextExtensions)
}

function Assert-SkillPayloadRelativeKey {
    <#
    .SYNOPSIS
        Falha se a chave relativa nao for portavel entre os dois motores.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][AllowEmptyString()][string]$Key
    )

    if ([string]::IsNullOrEmpty($Key)) {
        throw "skill_payload_key_empty"
    }
    if ($Key.Contains('\')) {
        throw "skill_payload_key_has_backslash:$Key"
    }
    foreach ($char in $Key.ToCharArray()) {
        $code = [int]$char
        if ($code -lt 0x20 -or $code -gt 0x7E) {
            throw ("skill_payload_key_not_ascii:{0}:U+{1:X4}" -f $Key, $code)
        }
    }
    return $Key
}

function Get-SkillPayloadRelativeKey {
    <#
    .SYNOPSIS
        Converte um caminho absoluto na chave canonica relativa a raiz.

    .DESCRIPTION
        Usa [IO.Path]::GetRelativePath, que no Windows compara o prefixo de
        forma case-insensitive e no Linux de forma case-sensitive -- ou seja, a
        semantica do proprio sistema de arquivos. O resultado preserva o case
        real do arquivo e e normalizado para `/`.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$Root,
        [Parameter(Mandatory = $true)][string]$FullPath
    )

    $rootFull = [System.IO.Path]::GetFullPath($Root)
    $fileFull = [System.IO.Path]::GetFullPath($FullPath)
    $relative = [System.IO.Path]::GetRelativePath($rootFull, $fileFull)

    if ([System.IO.Path]::IsPathRooted($relative)) {
        throw "skill_payload_file_outside_root:$fileFull"
    }
    $key = $relative.Replace('\', '/')
    if ($key -eq '..' -or $key.StartsWith('../')) {
        throw "skill_payload_file_outside_root:$fileFull"
    }

    return Assert-SkillPayloadRelativeKey -Key $key
}

function Get-SkillPayloadCanonicalBytes {
    <#
    .SYNOPSIS
        Le um arquivo aplicando a normalizacao de fim de linha do contrato.

    .DESCRIPTION
        Normaliza somente extensoes textuais declaradas, e opera sobre bytes --
        nao decodifica texto. Decodificar arriscaria reescrever BOM, substituir
        bytes invalidos por U+FFFD e mudar o hash de um arquivo que nao mudou.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$RelativeKey
    )

    $bytes = [System.IO.File]::ReadAllBytes($Path)
    $extension = [System.IO.Path]::GetExtension($RelativeKey)
    if ([string]::IsNullOrEmpty($extension)) {
        return $bytes
    }
    if (-not $script:SkillPayloadTextExtensionSet.Contains($extension.ToLowerInvariant())) {
        return $bytes
    }

    $output = [System.Collections.Generic.List[byte]]::new($bytes.Length)
    for ($index = 0; $index -lt $bytes.Length; $index++) {
        $byte = $bytes[$index]
        if ($byte -eq 0x0D) {
            # CRLF e CR solitario colapsam para LF.
            if (($index + 1) -lt $bytes.Length -and $bytes[$index + 1] -eq 0x0A) {
                $index++
            }
            $output.Add([byte]0x0A)
            continue
        }
        $output.Add($byte)
    }

    return $output.ToArray()
}

function Get-SkillPayloadFileHash {
    <#
    .SYNOPSIS
        sha256 hex minusculo dos bytes canonicos de um arquivo.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$RelativeKey
    )

    $bytes = Get-SkillPayloadCanonicalBytes -Path $Path -RelativeKey $RelativeKey
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        return [System.Convert]::ToHexString($sha.ComputeHash($bytes)).ToLowerInvariant()
    }
    finally {
        $sha.Dispose()
    }
}

function Get-SkillPayloadHash {
    <#
    .SYNOPSIS
        Hash canonico do diretorio de payload de uma skill.

    .DESCRIPTION
        Implementacao unica do contrato descrito no cabecalho deste modulo.
        Consumidores: audit_skill_lifecycle.ps1 e
        ci/test_skill_lifecycle_registry.ps1. Nao duplique este corpo.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Container)) {
        throw "skill_payload_root_missing:$Path"
    }

    $rootFull = [System.IO.Path]::GetFullPath($Path)
    $byKey = [System.Collections.Generic.Dictionary[string, string]]::new([System.StringComparer]::Ordinal)

    foreach ($file in Get-ChildItem -LiteralPath $rootFull -File -Recurse -Force) {
        $key = Get-SkillPayloadRelativeKey -Root $rootFull -FullPath $file.FullName
        if ($byKey.ContainsKey($key)) {
            throw "skill_payload_duplicate_key:$key"
        }
        $byKey[$key] = $file.FullName
    }

    $orderedKeys = [string[]]@($byKey.Keys)
    [System.Array]::Sort($orderedKeys, [System.StringComparer]::Ordinal)

    $payload = [System.Collections.Generic.List[byte]]::new()
    foreach ($key in $orderedKeys) {
        $fileHash = Get-SkillPayloadFileHash -Path $byKey[$key] -RelativeKey $key
        $payload.AddRange([System.Text.Encoding]::UTF8.GetBytes($key))
        $payload.Add([byte]0x00)
        $payload.AddRange([System.Text.Encoding]::ASCII.GetBytes($fileHash))
        $payload.Add([byte]0x0A)
    }

    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        return [System.Convert]::ToHexString($sha.ComputeHash($payload.ToArray())).ToLowerInvariant()
    }
    finally {
        $sha.Dispose()
    }
}

Export-ModuleMember -Function @(
    'Get-SkillPayloadTextExtension',
    'Assert-SkillPayloadRelativeKey',
    'Get-SkillPayloadRelativeKey',
    'Get-SkillPayloadCanonicalBytes',
    'Get-SkillPayloadFileHash',
    'Get-SkillPayloadHash'
)
