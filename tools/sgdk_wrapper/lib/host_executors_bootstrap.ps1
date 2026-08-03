<#
.SYNOPSIS
    Ponto de entrada dot-sourceavel para host_executors.psm1.

.DESCRIPTION
    Existe para que um script consumidor precise de UMA linha, sem recalcular a
    localizacao do modulo em cada arquivo:

        . (Join-Path $PSScriptRoot "../lib/host_executors_bootstrap.ps1")

    Sem isto, cada um dos ~66 consumidores carregaria o modulo com o seu proprio
    numero de `..`, e mover um arquivo de pasta quebraria o carregamento de forma
    silenciosa.

    O modulo e importado com -Global para que as funcoes fiquem visiveis dentro
    de scriptblocks e funcoes do chamador. Import-Module com escopo default
    ficaria preso ao escopo do dot-source e `Invoke-HostPowerShell` apareceria
    como comando inexistente no meio de um gate.

    Idempotente: dois dot-sources no mesmo processo nao reimportam nem falham.
#>

Set-StrictMode -Version Latest

if (-not (Get-Module -Name 'host_executors')) {
    $script:hostExecutorsModule = Join-Path $PSScriptRoot 'host_executors.psm1'
    if (-not (Test-Path -LiteralPath $script:hostExecutorsModule -PathType Leaf)) {
        throw "host_executors_module_missing: '$($script:hostExecutorsModule)' ausente. Sem o helper central, os gates voltariam a chamar 'powershell' literal e falhariam no Linux."
    }
    Import-Module -Name $script:hostExecutorsModule -Global -Force -ErrorAction Stop
}
