<#
.SYNOPSIS
    Ponto de entrada dot-sourceavel para skill_payload_hash.psm1.

.DESCRIPTION
    Segue o mesmo padrao de host_executors_bootstrap.ps1: um consumidor precisa
    de UMA linha e nao recalcula a localizacao do modulo.

        . (Join-Path $PSScriptRoot "../lib/skill_payload_hash_bootstrap.ps1")

    Importado com -Global para que as funcoes fiquem visiveis dentro de
    scriptblocks e funcoes do chamador. Idempotente.
#>

Set-StrictMode -Version Latest

if (-not (Get-Module -Name 'skill_payload_hash')) {
    $script:skillPayloadHashModule = Join-Path $PSScriptRoot 'skill_payload_hash.psm1'
    if (-not (Test-Path -LiteralPath $script:skillPayloadHashModule -PathType Leaf)) {
        throw "skill_payload_hash_module_missing: '$($script:skillPayloadHashModule)' ausente. Sem o motor canonico, cada consumidor voltaria a implementar o hash por conta propria e o registry divergiria entre Windows e Linux."
    }
    Import-Module -Name $script:skillPayloadHashModule -Global -Force -ErrorAction Stop
}
