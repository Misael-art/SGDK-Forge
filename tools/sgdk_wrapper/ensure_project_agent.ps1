[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$SourceDir,

    [Parameter(Mandatory = $true)]
    [string]$TargetDir,

    [ValidateSet("Host", "Batch", "Json")]
    [string]$OutputFormat = "Host"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
if ($OutputFormat -ne "Host") {
    $WarningPreference = "SilentlyContinue"
}

function Resolve-FullPath {
    param([Parameter(Mandatory = $true)][string]$Path)
    return [System.IO.Path]::GetFullPath($Path)
}

function Get-AgentManifest {
    param([Parameter(Mandatory = $true)][string]$AgentDir)

    $manifestPath = Join-Path $AgentDir "framework_manifest.json"
    if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
        return $null
    }

    try {
        return Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    } catch {
        Write-Warning ("[SGDK Wrapper] framework_manifest.json invalido em '{0}': {1}" -f $manifestPath, $_.Exception.Message)
        return $null
    }
}

function Get-FileSha256OrEmpty {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return ""
    }

    $extension = [System.IO.Path]::GetExtension($Path).ToLowerInvariant()
    if ($extension -in @(".md", ".json")) {
        $content = Get-Content -LiteralPath $Path -Raw
        $normalized = $content.Replace("`r`n", "`n")
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($normalized)
        $sha256 = [System.Security.Cryptography.SHA256]::Create()
        try {
            $hashBytes = $sha256.ComputeHash($bytes)
            return ([System.BitConverter]::ToString($hashBytes).Replace("-", "")).ToLowerInvariant()
        } finally {
            $sha256.Dispose()
        }
    }

    $stream = [System.IO.File]::OpenRead($Path)
    try {
        $sha256 = [System.Security.Cryptography.SHA256]::Create()
        try {
            $hashBytes = $sha256.ComputeHash($stream)
            return ([System.BitConverter]::ToString($hashBytes).Replace("-", "")).ToLowerInvariant()
        } finally {
            $sha256.Dispose()
        }
    } finally {
        $stream.Dispose()
    }
}

function Convert-ToBatchLine {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Value
    )

    $safe = $Value.Replace('"', '""')
    return ('set "{0}={1}"' -f $Name, $safe)
}

function New-BootstrapStatus {
    return [ordered]@{
        SGDK_AGENT_BOOTSTRAPPED = "0"
        SGDK_AGENT_BOOTSTRAP_DEGRADED = "0"
        SGDK_AGENT_BOOTSTRAP_REASON = "unknown"
        SGDK_AGENT_CANONICAL_VERSION = "desconhecida"
        SGDK_AGENT_LOCAL_VERSION = ""
        SGDK_AGENT_SOURCE_DIR = ""
        SGDK_AGENT_LOCAL_DIR = ""
    }
}

function Write-StatusResult {
    param([Parameter(Mandatory = $true)][hashtable]$Status)

    if ($OutputFormat -eq "Batch") {
        foreach ($pair in $Status.GetEnumerator()) {
            Write-Output (Convert-ToBatchLine -Name $pair.Key -Value ([string]$pair.Value))
        }
        return
    }

    if ($OutputFormat -eq "Json") {
        [PSCustomObject]$Status | ConvertTo-Json -Depth 5
        return
    }
}

try {
    $resolvedSource = Resolve-FullPath -Path $SourceDir
    $resolvedTarget = Resolve-FullPath -Path $TargetDir
    $status = New-BootstrapStatus
    $status["SGDK_AGENT_SOURCE_DIR"] = $resolvedSource
    $status["SGDK_AGENT_LOCAL_DIR"] = (Join-Path $resolvedTarget ".agent")

    if (-not (Test-Path -LiteralPath $resolvedSource -PathType Container)) {
        throw "Diretorio fonte da .agent nao encontrado: '$resolvedSource'."
    }

    $sourceArchitecture = Join-Path $resolvedSource "ARCHITECTURE.md"
    if (-not (Test-Path -LiteralPath $sourceArchitecture -PathType Leaf)) {
        throw "A .agent canonica esta incompleta. Arquivo obrigatorio ausente: '$sourceArchitecture'."
    }

    $sourceManifest = Get-AgentManifest -AgentDir $resolvedSource
    $sourceVersion = if ($sourceManifest -and $sourceManifest.framework_version) { [string]$sourceManifest.framework_version } else { "desconhecida" }
    $status["SGDK_AGENT_CANONICAL_VERSION"] = $sourceVersion
    $sourceArchitectureHash = Get-FileSha256OrEmpty -Path $sourceArchitecture
    $sourceManifestHash = Get-FileSha256OrEmpty -Path (Join-Path $resolvedSource "framework_manifest.json")

    if (-not (Test-Path -LiteralPath $resolvedTarget -PathType Container)) {
        throw "Diretorio do projeto nao encontrado: '$resolvedTarget'."
    }

    $destinationAgentDir = Join-Path $resolvedTarget ".agent"
    if (Test-Path -LiteralPath $destinationAgentDir -PathType Container) {
        if ($OutputFormat -eq "Host") {
            Write-Host "[SGDK Wrapper] .agent local ja existe em: $destinationAgentDir"
        }
        $status["SGDK_AGENT_BOOTSTRAPPED"] = "1"
        $status["SGDK_AGENT_BOOTSTRAP_REASON"] = "existing"
        $localManifest = Get-AgentManifest -AgentDir $destinationAgentDir
        if (-not $localManifest) {
            $sourceManifestPath = Join-Path $resolvedSource "framework_manifest.json"
            if (Test-Path -LiteralPath $sourceManifestPath -PathType Leaf) {
                $destManifestPath = Join-Path $destinationAgentDir "framework_manifest.json"
                try {
                    Copy-Item -LiteralPath $sourceManifestPath -Destination $destManifestPath -Force
                    $localManifest = Get-AgentManifest -AgentDir $destinationAgentDir
                    if ($localManifest) {
                        $status["SGDK_AGENT_BOOTSTRAP_REASON"] = "manifest_healed"
                        if ($OutputFormat -eq "Host") {
                            Write-Host "[SGDK Wrapper] framework_manifest.json copiado da canonica (heal) — nenhuma outra pasta da .agent local foi sobrescrita."
                        }
                    }
                } catch {
                    Write-Warning ("[SGDK Wrapper] Falha ao copiar framework_manifest.json da canonica: {0}" -f $_.Exception.Message)
                }
            }
        }
        if (-not $localManifest) {
            $status["SGDK_AGENT_BOOTSTRAP_DEGRADED"] = "1"
            $status["SGDK_AGENT_BOOTSTRAP_REASON"] = "missing_manifest"
            Write-Warning ("[SGDK Wrapper] .agent local sem framework_manifest.json apos heal. Canonica atual: {0}. Auditar drift." -f $sourceVersion)
        } else {
            $localVersion = if ($localManifest.framework_version) { [string]$localManifest.framework_version } else { "desconhecida" }
            $status["SGDK_AGENT_LOCAL_VERSION"] = $localVersion
            if ($localVersion -ne $sourceVersion) {
                $status["SGDK_AGENT_BOOTSTRAP_DEGRADED"] = "1"
                $status["SGDK_AGENT_BOOTSTRAP_REASON"] = "version_mismatch"
                Write-Warning ("[SGDK Wrapper] Divergencia de versao da .agent local. Local={0} / Canonica={1}. Nenhuma sobrescrita automatica sera feita." -f $localVersion, $sourceVersion)
            }

            $localArchitecturePath = Join-Path $destinationAgentDir "ARCHITECTURE.md"
            $localManifestPath = Join-Path $destinationAgentDir "framework_manifest.json"
            if (-not (Test-Path -LiteralPath $localArchitecturePath -PathType Leaf)) {
                $status["SGDK_AGENT_BOOTSTRAP_DEGRADED"] = "1"
                $status["SGDK_AGENT_BOOTSTRAP_REASON"] = "missing_architecture"
                Write-Warning ("[SGDK Wrapper] .agent local incompleta: arquivo obrigatorio ausente '{0}'." -f $localArchitecturePath)
            } else {
                $localArchitectureHash = Get-FileSha256OrEmpty -Path $localArchitecturePath
                if ($localArchitectureHash -and $sourceArchitectureHash -and $localArchitectureHash -ne $sourceArchitectureHash) {
                    $status["SGDK_AGENT_BOOTSTRAP_DEGRADED"] = "1"
                    $status["SGDK_AGENT_BOOTSTRAP_REASON"] = "architecture_drift"
                    Write-Warning "[SGDK Wrapper] .agent local com drift em ARCHITECTURE.md em relacao a canonica."
                }
            }

            $localManifestHash = Get-FileSha256OrEmpty -Path $localManifestPath
            if ($localManifestHash -and $sourceManifestHash -and $localManifestHash -ne $sourceManifestHash) {
                $status["SGDK_AGENT_BOOTSTRAP_DEGRADED"] = "1"
                if ($status["SGDK_AGENT_BOOTSTRAP_REASON"] -eq "existing") {
                    $status["SGDK_AGENT_BOOTSTRAP_REASON"] = "manifest_drift"
                }
                Write-Warning "[SGDK Wrapper] .agent local com drift em framework_manifest.json em relacao a canonica."
            }

            if ($sourceManifest -and $sourceManifest.tracked_paths) {
                foreach ($trackedPath in $sourceManifest.tracked_paths) {
                    $localTrackedPath = Join-Path $destinationAgentDir ([string]$trackedPath)
                    if (-not (Test-Path -LiteralPath $localTrackedPath)) {
                        $status["SGDK_AGENT_BOOTSTRAP_DEGRADED"] = "1"
                        $status["SGDK_AGENT_BOOTSTRAP_REASON"] = "missing_tracked_path"
                        Write-Warning ("[SGDK Wrapper] .agent local sem caminho rastreado obrigatorio: {0}" -f $localTrackedPath)
                        break
                    }
                }
            }
        }
        if (-not $status["SGDK_AGENT_LOCAL_VERSION"]) {
            $status["SGDK_AGENT_LOCAL_VERSION"] = $sourceVersion
        }
        Write-StatusResult -Status $status
        exit 0
    }

    New-Item -ItemType Directory -Path $destinationAgentDir -Force | Out-Null

    foreach ($child in Get-ChildItem -LiteralPath $resolvedSource -Force) {
        Copy-Item -LiteralPath $child.FullName -Destination $destinationAgentDir -Recurse -Force
    }

    $copiedArchitecture = Join-Path $destinationAgentDir "ARCHITECTURE.md"
    $copiedManifest = Join-Path $destinationAgentDir "framework_manifest.json"
    if (-not (Test-Path -LiteralPath $copiedArchitecture -PathType Leaf)) {
        throw "Falha ao copiar a .agent canonica para '$resolvedTarget'. O arquivo '$copiedArchitecture' nao foi materializado."
    }
    if (-not (Test-Path -LiteralPath $copiedManifest -PathType Leaf)) {
        throw "Falha ao copiar a .agent canonica para '$resolvedTarget'. O arquivo '$copiedManifest' nao foi materializado."
    }

    $status["SGDK_AGENT_BOOTSTRAPPED"] = "1"
    $status["SGDK_AGENT_BOOTSTRAP_REASON"] = "bootstrapped"
    $status["SGDK_AGENT_LOCAL_VERSION"] = $sourceVersion
    if ($OutputFormat -eq "Host") {
        Write-Host "[SGDK Wrapper] .agent bootstrap copiada para: $resolvedTarget (versao $sourceVersion)"
    }
    Write-StatusResult -Status $status
    exit 0
}
catch {
    Write-Error $_
    exit 1
}
