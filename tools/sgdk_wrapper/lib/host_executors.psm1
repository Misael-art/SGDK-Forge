<#
.SYNOPSIS
    Resolucao centralizada de executores do host (PowerShell, Python, Java) e
    do ambiente Python offline do framework.

.DESCRIPTION
    Fonte unica de verdade para "qual binario chamar" em qualquer script do
    wrapper ou da CI.

    Contrato travado:
      * Nenhum script pode chamar `powershell` ou `powershell.exe` literalmente.
        No Linux esses nomes nao existem (ou sao stubs Wine) e a chamada falha
        como se o TESTE tivesse falhado, contaminando o diagnostico do projeto.
      * `Get-PowerShellExecutable` devolve o executor real: `pwsh` quando existe,
        `powershell.exe` apenas em Windows real.
      * Dependencia ausente e ERRO EXPLICITO, nunca skip. Um gate que nao rodou
        nao pode ser contado como gate que passou.
      * Nenhuma funcao aqui baixa nada da rede. O preparo de `jsonschema` e
        `Pillow` usa exclusivamente o lock local do workspace.

.NOTES
    Este modulo nunca deve conter workaround de uma maquina especifica.
    Diferencas de host pertencem a deteccao, nao a excecoes hardcoded.
#>

Set-StrictMode -Version Latest

$script:ResolvedCache = @{}

function Get-WorkspaceRootFromModule {
    <#
    .SYNOPSIS
        Deriva a raiz do workspace a partir da localizacao deste modulo.
    #>
    $libDir = Split-Path $PSScriptRoot -Parent          # tools/sgdk_wrapper
    $toolsDir = Split-Path $libDir -Parent              # tools
    return (Split-Path $toolsDir -Parent)               # workspace root
}

function Test-IsWindowsHost {
    <#
    .SYNOPSIS
        Windows real, nao Wine.
    #>
    if (Get-Variable -Name IsWindows -Scope Global -ErrorAction SilentlyContinue) {
        return [bool]$global:IsWindows
    }
    # PowerShell 5.1 (Windows) nao define $IsWindows.
    return ($env:OS -eq 'Windows_NT')
}

function Get-PowerShellExecutable {
    <#
    .SYNOPSIS
        Executor PowerShell real deste host.

    .DESCRIPTION
        Ordem: pwsh (cross-platform, preferido) -> powershell.exe (Windows real).
        Em Linux, `powershell.exe` pode existir como stub Wine: nunca e aceito.

    .PARAMETER Required
        Quando $true (default), ausencia lanca erro. Nunca retorna $null silencioso.
    #>
    param([bool]$Required = $true)

    if ($script:ResolvedCache.ContainsKey('pwsh')) {
        return $script:ResolvedCache['pwsh']
    }

    # Get-Command pode devolver varios matches quando o PATH tem entradas
    # duplicadas (comum em Linux com /usr/bin e /bin apontando ao mesmo lugar).
    # Sempre reduzir ao primeiro, nunca deixar array virar string.
    $candidate = @(Get-Command 'pwsh' -CommandType Application -ErrorAction SilentlyContinue) |
        Select-Object -First 1
    if ($null -ne $candidate) {
        $script:ResolvedCache['pwsh'] = $candidate.Source
        return $candidate.Source
    }

    if (Test-IsWindowsHost) {
        $winps = @(Get-Command 'powershell.exe' -CommandType Application -ErrorAction SilentlyContinue) |
            Select-Object -First 1
        if ($null -ne $winps) {
            $script:ResolvedCache['pwsh'] = $winps.Source
            return $winps.Source
        }
    }

    if ($Required) {
        throw "host_executor_missing: nenhum PowerShell real encontrado (procurado: pwsh; powershell.exe apenas em Windows real). Instale pwsh 7+ antes de rodar os gates."
    }
    return $null
}

function Invoke-HostPowerShell {
    <#
    .SYNOPSIS
        Executa um script .ps1 no PowerShell real deste host.

    .DESCRIPTION
        Substituto unico de `& powershell ...` e `& powershell.exe ...`. Todos os
        call sites do wrapper e da CI passam por aqui, entao a resolucao do
        executor existe em UM lugar e nao em 150.

        `-ExecutionPolicy Bypass` e sempre emitido: `pwsh` aceita a flag nas tres
        plataformas (no Linux ela e aceita e ignorada) e `powershell.exe` a exige
        para rodar script nao assinado. Verificado neste host com pwsh 7.6.3.

        O exit code do processo filho e propagado em $global:LASTEXITCODE, porque
        os gates decidem por exit code. Sem isso, um teste que falhou seria lido
        como teste que passou -- exatamente o falso verde que esta remediacao
        ataca.

    .PARAMETER ScriptPath
        Caminho do .ps1 a executar. Ausencia e erro explicito, nunca skip.

    .PARAMETER Arguments
        Argumentos repassados ao script, apos `-File`.
    #>
    param(
        [Parameter(Mandatory = $true)][string]$ScriptPath,
        [Parameter(Mandatory = $false)][object[]]$Arguments = @()
    )

    if (-not (Test-Path -LiteralPath $ScriptPath -PathType Leaf)) {
        throw "host_powershell_script_missing: '$ScriptPath' nao existe. Um gate que nao pode ser executado e blocker, nao skip."
    }

    $exe = Get-PowerShellExecutable
    $invocation = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $ScriptPath) + $Arguments

    & $exe @invocation
}

function Get-PythonExecutable {
    <#
    .SYNOPSIS
        Interpretador Python do framework.

    .DESCRIPTION
        Respeita SGDK_FORGE_PYTHON quando definido, para que processos filhos
        herdem exatamente o mesmo interpretador do runner pai. Sem isso, um teste
        pode rodar em um Python e o filho em outro, e o PYTHONPATH offline deixa
        de valer.
    #>
    param([bool]$Required = $true)

    if (-not [string]::IsNullOrWhiteSpace($env:SGDK_FORGE_PYTHON)) {
        if (Test-Path -LiteralPath $env:SGDK_FORGE_PYTHON) {
            return $env:SGDK_FORGE_PYTHON
        }
        throw "host_executor_invalid: SGDK_FORGE_PYTHON aponta para caminho inexistente: $($env:SGDK_FORGE_PYTHON)"
    }

    if ($script:ResolvedCache.ContainsKey('python')) {
        return $script:ResolvedCache['python']
    }

    foreach ($name in @('python3', 'python')) {
        $candidate = @(Get-Command $name -CommandType Application -ErrorAction SilentlyContinue) |
            Select-Object -First 1
        if ($null -ne $candidate) {
            $script:ResolvedCache['python'] = $candidate.Source
            return $candidate.Source
        }
    }

    if ($Required) {
        throw "host_executor_missing: Python nao encontrado (procurado: python3, python)."
    }
    return $null
}

function Get-JavaExecutable {
    <#
    .SYNOPSIS
        Java usado pelo RESCOMP do SGDK.
    #>
    param([bool]$Required = $true)

    if ($script:ResolvedCache.ContainsKey('java')) {
        return $script:ResolvedCache['java']
    }

    $candidate = @(Get-Command 'java' -CommandType Application -ErrorAction SilentlyContinue) |
        Select-Object -First 1
    if ($null -ne $candidate) {
        $script:ResolvedCache['java'] = $candidate.Source
        return $candidate.Source
    }

    if ($Required) {
        throw "host_executor_missing: Java nao encontrado. RESCOMP do SGDK 2.11 exige JRE/JDK."
    }
    return $null
}

function Get-PythonLockPath {
    <#
    .SYNOPSIS
        Lock canonico e unico das dependencias Python do framework.

    .DESCRIPTION
        Fonte: tools/sgdk_wrapper/linux_python_requirements.lock.
        Este modulo NUNCA cria um segundo lock. Se as versoes precisarem mudar,
        o lock existente e editado com hash, fora da janela dos gates.
    #>
    param([string]$WorkspaceRoot = '')

    if ([string]::IsNullOrWhiteSpace($WorkspaceRoot)) {
        $WorkspaceRoot = Get-WorkspaceRootFromModule
    }
    return (Join-Path (Join-Path (Join-Path $WorkspaceRoot 'tools') 'sgdk_wrapper') 'linux_python_requirements.lock')
}

function Get-OfflinePythonPath {
    <#
    .SYNOPSIS
        Destino canonico do cache local de dependencias Python.

    .DESCRIPTION
        `out/host_tools/python/site-packages`, exatamente o alvo que
        `ensure_linux_python_deps.sh` popula a partir de
        `out/host_tools/python/wheels`. Nao inventa diretorio novo.

        Nunca baixa nada. Se o alvo nao estiver pronto, o chamador deve tratar
        como blocker de dependencia, nao como skip.
    #>
    param([string]$WorkspaceRoot = '')

    if ([string]::IsNullOrWhiteSpace($WorkspaceRoot)) {
        $WorkspaceRoot = Get-WorkspaceRootFromModule
    }
    $toolRoot = Join-Path (Join-Path $WorkspaceRoot 'out') 'host_tools'
    return (Join-Path (Join-Path $toolRoot 'python') 'site-packages')
}

function Get-PythonWheelCachePath {
    <#
    .SYNOPSIS
        Diretorio de wheels baixados previamente, usado em modo --no-index.
    #>
    param([string]$WorkspaceRoot = '')

    if ([string]::IsNullOrWhiteSpace($WorkspaceRoot)) {
        $WorkspaceRoot = Get-WorkspaceRootFromModule
    }
    $toolRoot = Join-Path (Join-Path $WorkspaceRoot 'out') 'host_tools'
    return (Join-Path (Join-Path $toolRoot 'python') 'wheels')
}

function Get-LockedPythonVersions {
    <#
    .SYNOPSIS
        Le o lock e devolve mapa pacote -> versao fixada.

    .DESCRIPTION
        As versoes exigidas vem SEMPRE do lock, nunca hardcoded neste modulo.
        Assim, editar o lock e suficiente; nenhum codigo precisa acompanhar.
    #>
    param([string]$WorkspaceRoot = '')

    $lockPath = Get-PythonLockPath -WorkspaceRoot $WorkspaceRoot
    if (-not (Test-Path -LiteralPath $lockPath)) {
        throw "python_lock_missing: lock canonico ausente em '$lockPath'. Os gates nao podem inferir versoes sem ele."
    }

    $versions = @{}
    foreach ($line in (Get-Content -LiteralPath $lockPath)) {
        $match = [regex]::Match($line.Trim(), '^([A-Za-z0-9_.\-]+)==([^\s\\]+)')
        if ($match.Success) {
            # Normaliza para a chave usada por importlib.metadata.
            $versions[$match.Groups[1].Value.ToLowerInvariant()] = $match.Groups[2].Value
        }
    }
    if ($versions.Count -eq 0) {
        throw "python_lock_unparsable: nenhuma versao fixada encontrada em '$lockPath'."
    }
    return $versions
}

function Assert-PythonDependencies {
    <#
    .SYNOPSIS
        Confirma que jsonschema e Pillow carregam DO CACHE LOCAL, na versao do
        lock, sem qualquer acesso a rede.

    .DESCRIPTION
        Nao basta importar: um `import jsonschema` que resolve para o
        site-packages global do sistema passaria aqui e quebraria a
        reprodutibilidade que P0-003 conquistou. Este assert valida tres coisas:

          1. o modulo importa;
          2. a versao e exatamente a do lock canonico;
          3. a procedencia esta DENTRO de out/host_tools/python/site-packages.

        Qualquer uma das tres falhando e BLOCKER. Reportar "skip" nesse caso e
        exatamente o falso verde que esta remediacao ataca.

        Nunca baixa nada: quando o cache nao esta pronto, a mensagem aponta para
        `ensure_linux_python_deps.sh`, que deve rodar FORA da janela dos gates.

    .PARAMETER Modules
        Mapa modulo-de-import -> nome-de-distribuicao. Default cobre o que os
        gates realmente usam: jsonschema (schemas) e PIL/pillow (imagens).
    #>
    param(
        [string]$WorkspaceRoot = '',
        [hashtable]$Modules = @{ 'jsonschema' = 'jsonschema'; 'PIL' = 'pillow' }
    )

    if ([string]::IsNullOrWhiteSpace($WorkspaceRoot)) {
        $WorkspaceRoot = Get-WorkspaceRootFromModule
    }

    $python = Get-PythonExecutable
    $offlinePath = Get-OfflinePythonPath -WorkspaceRoot $WorkspaceRoot
    $locked = Get-LockedPythonVersions -WorkspaceRoot $WorkspaceRoot

    if (-not (Test-Path -LiteralPath $offlinePath -PathType Container)) {
        throw "python_cache_missing: cache local ausente em '$offlinePath'. Rode tools/sgdk_wrapper/ensure_linux_python_deps.sh ANTES dos gates; downloads durante os gates sao proibidos. Isto e um BLOCKER, nao um skip."
    }

    # Prepend do cache local: a dependencia do workspace tem prioridade sobre a
    # global, para que o gate nao passe por acidente com a versao do sistema.
    $sep = [System.IO.Path]::PathSeparator
    if ([string]::IsNullOrWhiteSpace($env:PYTHONPATH)) {
        $env:PYTHONPATH = $offlinePath
    } elseif ($env:PYTHONPATH -notlike "*$offlinePath*") {
        $env:PYTHONPATH = "$offlinePath$sep$($env:PYTHONPATH)"
    }

    $probe = @'
import json, sys
from pathlib import Path
from importlib.metadata import distribution, version

root = Path(sys.argv[1]).resolve()
spec = json.loads(sys.argv[2])          # {import_name: distribution_name}
expected = json.loads(sys.argv[3])      # {distribution_name_lower: version}

result = {"python": sys.executable, "cache_root": str(root),
          "modules": {}, "missing": [], "version_mismatch": [], "outside_cache": []}

for import_name, dist_name in spec.items():
    try:
        mod = __import__(import_name)
    except Exception as exc:
        result["missing"].append({"module": import_name, "error": str(exc)})
        continue
    try:
        installed = version(dist_name)
        origin = Path(distribution(dist_name).locate_file("")).resolve()
    except Exception as exc:
        result["missing"].append({"module": import_name, "error": "metadata: %s" % exc})
        continue

    entry = {"distribution": dist_name, "version": installed, "origin": str(origin),
             "module_file": getattr(mod, "__file__", "unknown")}
    result["modules"][import_name] = entry

    want = expected.get(dist_name.lower())
    if want is not None and installed != want:
        result["version_mismatch"].append(
            {"module": import_name, "expected": want, "found": installed})

    if not origin.is_relative_to(root):
        result["outside_cache"].append(
            {"module": import_name, "origin": str(origin), "expected_under": str(root)})

print(json.dumps(result))
'@

    $probeFile = Join-Path ([System.IO.Path]::GetTempPath()) "sgdk_forge_depprobe_$PID.py"
    Set-Content -LiteralPath $probeFile -Value $probe -Encoding UTF8
    $raw = ''
    $parsed = $null
    try {
        $specJson = ($Modules | ConvertTo-Json -Compress)
        $lockJson = ($locked | ConvertTo-Json -Compress)
        $raw = (& $python $probeFile $offlinePath $specJson $lockJson 2>&1 | Out-String)
        $parsed = $raw | ConvertFrom-Json
    } catch {
        throw "python_dependency_probe_failed: nao foi possivel executar o probe de dependencias. Saida: $raw"
    } finally {
        Remove-Item -LiteralPath $probeFile -Force -ErrorAction SilentlyContinue
    }

    if (@($parsed.missing).Count -gt 0) {
        $names = (@($parsed.missing) | ForEach-Object { $_.module }) -join ', '
        throw "python_dependency_missing: [$names] nao pode(m) ser importado(s) do cache local '$offlinePath'. Rode ensure_linux_python_deps.sh antes dos gates. BLOCKER, nao skip."
    }
    if (@($parsed.version_mismatch).Count -gt 0) {
        $detail = (@($parsed.version_mismatch) | ForEach-Object { "$($_.module): esperado $($_.expected), encontrado $($_.found)" }) -join '; '
        throw "python_dependency_version_mismatch: $detail. O lock canonico e a autoridade. BLOCKER, nao skip."
    }
    if (@($parsed.outside_cache).Count -gt 0) {
        $detail = (@($parsed.outside_cache) | ForEach-Object { "$($_.module) veio de $($_.origin)" }) -join '; '
        throw "python_dependency_outside_cache: $detail. Esperado sob '$offlinePath'. Um gate que usa a dependencia global do sistema nao e reproduzivel. BLOCKER, nao skip."
    }

    return $parsed
}

function Invoke-PythonProvisioning {
    <#
    .SYNOPSIS
        Garante o cache local de dependencias Python ANTES da janela dos gates.

    .DESCRIPTION
        Delega ao script canonico ja existente
        `tools/sgdk_wrapper/ensure_linux_python_deps.sh`, que:
          * usa o lock unico com --require-hashes;
          * instala com --no-index --no-deps --target no cache local;
          * sai como `source=cache` sem tocar a rede quando ja esta pronto.

        Este modulo NUNCA cria um segundo lock e NUNCA baixa nada por conta
        propria. O provisionamento pertence ao preparo; a partir do momento em
        que os gates comecam, `Assert-PythonDependencies` apenas verifica.

    .PARAMETER AllowNetwork
        Default $false. Com $false, o cache precisa estar pronto: se nao
        estiver, isto e um blocker explicito, porque baixar durante os gates e
        proibido. Passe $true somente em preparo consciente de ambiente novo.
    #>
    param(
        [string]$WorkspaceRoot = '',
        [bool]$AllowNetwork = $false
    )

    if ([string]::IsNullOrWhiteSpace($WorkspaceRoot)) {
        $WorkspaceRoot = Get-WorkspaceRootFromModule
    }

    $offlinePath = Get-OfflinePythonPath -WorkspaceRoot $WorkspaceRoot

    # Caminho rapido: cache ja valido, nada a fazer, nenhuma rede.
    try {
        $already = Assert-PythonDependencies -WorkspaceRoot $WorkspaceRoot
        return [pscustomobject]@{
            status = 'ready'; source = 'cache'; path = $offlinePath
            network_used = $false; modules = $already.modules
        }
    } catch {
        $firstFailure = $_.Exception.Message
    }

    if (-not $AllowNetwork) {
        throw "python_provisioning_required: $firstFailure`nProvisionamento com rede nao foi autorizado nesta chamada. Rode 'tools/sgdk_wrapper/ensure_linux_python_deps.sh' fora da janela dos gates e repita."
    }

    if (Test-IsWindowsHost) {
        throw "python_provisioning_unsupported_host: ensure_linux_python_deps.sh cobre Linux. Em Windows real, prepare o cache pelo caminho equivalente do host antes dos gates."
    }

    $ensureScript = Join-Path (Join-Path (Join-Path $WorkspaceRoot 'tools') 'sgdk_wrapper') 'ensure_linux_python_deps.sh'
    if (-not (Test-Path -LiteralPath $ensureScript)) {
        throw "python_provisioning_script_missing: '$ensureScript' ausente."
    }

    $output = (& bash $ensureScript 2>&1 | Out-String)
    if ($LASTEXITCODE -ne 0) {
        throw "python_provisioning_failed: ensure_linux_python_deps.sh saiu com $LASTEXITCODE.`n$output"
    }

    # Reverifica: provisionar sem validar seria o mesmo falso verde.
    $verified = Assert-PythonDependencies -WorkspaceRoot $WorkspaceRoot
    return [pscustomobject]@{
        status = 'ready'; source = 'provisioned'; path = $offlinePath
        network_used = $true; modules = $verified.modules
        provisioning_output_tail = (($output -split "`n" | Select-Object -Last 3) -join "`n")
    }
}

function Initialize-ConformanceEnvironment {
    <#
    .SYNOPSIS
        Prepara o ambiente herdado por TODOS os processos filhos dos gates.

    .DESCRIPTION
        Exporta SGDK_FORGE_PWSH, SGDK_FORGE_PYTHON e PYTHONPATH para que cada
        filho use exatamente o mesmo interpretador e o mesmo cache local do pai.

        Executor herdado e RESPEITADO: se SGDK_FORGE_PYTHON/SGDK_FORGE_PWSH ja
        vem do processo pai (caso do runner chamando um teste que chama outro),
        o valor existente prevalece em vez de ser redetectado. Isso evita que um
        neto rode em interpretador diferente do avo.

        Verifica dependencias sem rede. Falha de dependencia bloqueia.
    #>
    param(
        [string]$WorkspaceRoot = '',
        [bool]$AllowNetwork = $false
    )

    if ([string]::IsNullOrWhiteSpace($WorkspaceRoot)) {
        $WorkspaceRoot = Get-WorkspaceRootFromModule
    }

    # Respeita executores herdados; so detecta quando nao houver heranca.
    $inheritedPwsh = -not [string]::IsNullOrWhiteSpace($env:SGDK_FORGE_PWSH)
    $inheritedPython = -not [string]::IsNullOrWhiteSpace($env:SGDK_FORGE_PYTHON)

    $pwshExe = if ($inheritedPwsh -and (Test-Path -LiteralPath $env:SGDK_FORGE_PWSH)) {
        $env:SGDK_FORGE_PWSH
    } else {
        Get-PowerShellExecutable
    }
    $python = Get-PythonExecutable   # ja honra SGDK_FORGE_PYTHON internamente

    $env:SGDK_FORGE_PWSH = $pwshExe
    $env:SGDK_FORGE_PYTHON = $python
    $env:SGDK_FORGE_OFFLINE = '1'
    $env:PIP_NO_INDEX = '1'
    $env:PIP_DISABLE_PIP_VERSION_CHECK = '1'

    $provision = Invoke-PythonProvisioning -WorkspaceRoot $WorkspaceRoot -AllowNetwork $AllowNetwork

    return [pscustomobject]@{
        workspace_root      = $WorkspaceRoot
        powershell          = $pwshExe
        python              = $python
        pythonpath          = $env:PYTHONPATH
        python_cache        = (Get-OfflinePythonPath -WorkspaceRoot $WorkspaceRoot)
        python_lock         = (Get-PythonLockPath -WorkspaceRoot $WorkspaceRoot)
        locked_versions     = (Get-LockedPythonVersions -WorkspaceRoot $WorkspaceRoot)
        dependency_source   = $provision.source
        network_used        = $provision.network_used
        dependencies        = $provision.modules
        inherited_powershell = $inheritedPwsh
        inherited_python    = $inheritedPython
        offline             = $true
        is_windows          = (Test-IsWindowsHost)
    }
}

Export-ModuleMember -Function @(
    'Get-WorkspaceRootFromModule',
    'Test-IsWindowsHost',
    'Get-PowerShellExecutable',
    'Invoke-HostPowerShell',
    'Get-PythonExecutable',
    'Get-JavaExecutable',
    'Get-PythonLockPath',
    'Get-OfflinePythonPath',
    'Get-PythonWheelCachePath',
    'Get-LockedPythonVersions',
    'Assert-PythonDependencies',
    'Invoke-PythonProvisioning',
    'Initialize-ConformanceEnvironment'
)
