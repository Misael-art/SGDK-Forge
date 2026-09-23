<#
.SYNOPSIS
    Validates project-local storage, organized scratch space, and copied external inputs.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectRoot,

    [Parameter(Mandatory = $false)]
    [string]$WorkspaceRoot = "",

    [Parameter(Mandatory = $false)]
    [string]$OutputPath = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Import-Module (Join-Path $PSScriptRoot 'lib\sgdk_artifact_contracts.psm1') -Force

function Get-Prop {
    param($Object, [string]$Name, $Default = $null)
    if ($null -eq $Object) { return $Default }
    $property = $Object.PSObject.Properties[$Name]
    if ($null -eq $property) { return $Default }
    return $property.Value
}

function Test-UnderRoot {
    param([string]$Candidate, [string]$Root)
    if ([string]::IsNullOrWhiteSpace($Candidate) -or [string]::IsNullOrWhiteSpace($Root)) { return $false }
    $full = [System.IO.Path]::GetFullPath($Candidate)
    $base = [System.IO.Path]::GetFullPath($Root).TrimEnd('\', '/')
    return $full.Equals($base, [System.StringComparison]::OrdinalIgnoreCase) -or
        $full.StartsWith($base + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)
}

function Resolve-ProjectPath {
    param([string]$Value)
    if ([string]::IsNullOrWhiteSpace($Value)) { return $null }
    if ([System.IO.Path]::IsPathRooted($Value)) { return [System.IO.Path]::GetFullPath($Value) }
    return [System.IO.Path]::GetFullPath((Join-Path $script:ResolvedProjectRoot $Value))
}

function Add-Blocker {
    param([string]$Status, [string]$Message, [string]$Path = '', $Details = $null)
    if ($script:Report.blocking_statuses -notcontains $Status) {
        $script:Report.blocking_statuses += $Status
    }
    $script:Report.details += [ordered]@{
        status = $Status
        message = $Message
        path = $Path
        details = $Details
    }
}

$script:ResolvedProjectRoot = [System.IO.Path]::GetFullPath($ProjectRoot)
if (-not (Test-Path -LiteralPath $script:ResolvedProjectRoot -PathType Container)) {
    throw "ProjectRoot not found: $script:ResolvedProjectRoot"
}
if ([string]::IsNullOrWhiteSpace($WorkspaceRoot)) {
    $WorkspaceRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
}
$WorkspaceRoot = [System.IO.Path]::GetFullPath($WorkspaceRoot)

$manifestPath = Join-Path $script:ResolvedProjectRoot 'doc\project_hygiene_manifest.json'
if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $OutputPath = Join-Path $script:ResolvedProjectRoot 'out\logs\project_hygiene_report.json'
}

$script:Report = [ordered]@{
    schema_version = '1.0.0'
    generated_at = (Get-Date).ToUniversalTime().ToString('o')
    project_root = $script:ResolvedProjectRoot
    manifest_path = $manifestPath
    status = 'blocked'
    ready = $false
    blocking_statuses = @()
    details = @()
    observed = [ordered]@{
        suspicious_project_artifacts = @()
        unexpected_root_entries = @()
        noncanonical_project_entries = @()
        external_inputs_checked = 0
        external_path_references = @()
        workspace_root_orphans = @()
    }
}

$manifest = $null
if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
    Add-Blocker 'project_hygiene_manifest_missing' 'Projeto sem doc/project_hygiene_manifest.json.' $manifestPath
} else {
    try {
        $manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
    } catch {
        Add-Blocker 'project_hygiene_manifest_invalid' 'project_hygiene_manifest.json possui JSON invalido.' $manifestPath
    }
}

if ($manifest) {
    if ([string](Get-Prop $manifest 'project_root_policy' '') -ne 'all_project_material_inside_project') {
        Add-Blocker 'project_hygiene_manifest_invalid' 'project_root_policy precisa ser all_project_material_inside_project.' $manifestPath
    }
    if ([string](Get-Prop $manifest 'naming_policy' '') -ne 'portable_descriptive_v1') {
        Add-Blocker 'project_naming_policy_invalid' 'naming_policy precisa ser portable_descriptive_v1.' $manifestPath
    }

    $scratch = Get-Prop $manifest 'scratch_policy' $null
    $scratchRootValue = [string](Get-Prop $scratch 'root' '')
    $scratchRoot = Resolve-ProjectPath $scratchRootValue
    if (-not $scratchRoot -or -not (Test-UnderRoot $scratchRoot $script:ResolvedProjectRoot) -or
        -not (Test-Path -LiteralPath $scratchRoot -PathType Container)) {
        Add-Blocker 'project_scratch_structure_missing' 'A pasta organizada rascunho/ precisa existir dentro do projeto.' $scratchRootValue
    }
    foreach ($field in @('raw_inputs', 'processed_inputs', 'temporary')) {
        $value = [string](Get-Prop $scratch $field '')
        $resolved = Resolve-ProjectPath $value
        if (-not $resolved -or -not $scratchRoot -or -not (Test-UnderRoot $resolved $scratchRoot)) {
            Add-Blocker 'project_hygiene_manifest_invalid' "scratch_policy.$field precisa permanecer dentro de scratch_policy.root." $manifestPath @{
                field = $field
                value = $value
            }
        }
    }

    $allowedRootEntries = @((Get-Prop $manifest 'allowed_root_entries' @()) | ForEach-Object { [string]$_ })
    foreach ($item in Get-ChildItem -LiteralPath $script:ResolvedProjectRoot -Force -ErrorAction SilentlyContinue) {
        if ($item.Name -eq '.pytest_cache') { continue }
        if ($allowedRootEntries -notcontains $item.Name) {
            $script:Report.observed.unexpected_root_entries += $item.FullName
        }
    }
    if ($script:Report.observed.unexpected_root_entries.Count -gt 0) {
        Add-Blocker 'orphan_project_root_entry' 'A raiz do projeto possui entradas nao classificadas no manifesto de higiene.' $manifestPath @{
            entries = @($script:Report.observed.unexpected_root_entries)
        }
    }

    $namingScanExcludedRoots = @('.agent', 'out', 'rascunho', '.pytest_cache') |
        ForEach-Object { Join-Path $script:ResolvedProjectRoot $_ }
    $portableNamePattern = '^(?:\.[a-z0-9][a-z0-9._-]*|[a-z0-9][a-z0-9._-]*|README\.md|LICENSE(?:\.md)?|COPYING|Makefile)$'
    foreach ($item in Get-ChildItem -LiteralPath $script:ResolvedProjectRoot -Recurse -Force -ErrorAction SilentlyContinue) {
        if ($item.PSIsContainer -and $item.Name -eq '__pycache__') { continue }
        $excluded = $false
        foreach ($excludedRoot in $namingScanExcludedRoots) {
            if (Test-UnderRoot $item.FullName $excludedRoot) {
                $excluded = $true
                break
            }
        }
        if ($excluded) { continue }
        if ($item.Name -cnotmatch $portableNamePattern) {
            $script:Report.observed.noncanonical_project_entries += $item.FullName
        }
    }
    if ($script:Report.observed.noncanonical_project_entries.Count -gt 0) {
        Add-Blocker 'noncanonical_project_entry_name' 'Material ativo possui nome nao portatil ou ambiguo; use minusculas, ASCII, snake_case/kebab-case e sem espacos.' $script:ResolvedProjectRoot @{
            entries = @($script:Report.observed.noncanonical_project_entries)
            policy = 'portable_descriptive_v1'
        }
    }

    $excludedRoots = @('.agent', '.cursor', '.mddev', '.vscode', 'out', 'rascunho') |
        ForEach-Object { Join-Path $script:ResolvedProjectRoot $_ }
    $suspiciousFilePattern = '(?i)(\.tmp|\.temp|\.bak|\.old|\.orig|\.rej|~)$'
    $suspiciousDirNames = @('tmp', 'temp', 'temporary', 'scratch', 'draft', 'rascunhos')
    foreach ($item in Get-ChildItem -LiteralPath $script:ResolvedProjectRoot -Recurse -Force -ErrorAction SilentlyContinue) {
        $excluded = $false
        foreach ($excludedRoot in $excludedRoots) {
            if (Test-UnderRoot $item.FullName $excludedRoot) {
                $excluded = $true
                break
            }
        }
        if ($excluded) { continue }
        if ((-not $item.PSIsContainer -and $item.Name -match $suspiciousFilePattern) -or
            ($item.PSIsContainer -and $suspiciousDirNames -contains $item.Name.ToLowerInvariant())) {
            $script:Report.observed.suspicious_project_artifacts += $item.FullName
        }
    }
    if ($script:Report.observed.suspicious_project_artifacts.Count -gt 0) {
        Add-Blocker 'orphan_project_artifact' 'Arquivos temporarios ou pastas de rascunho foram encontrados fora de rascunho/ e out/.' $manifestPath @{
            artifacts = @($script:Report.observed.suspicious_project_artifacts)
        }
    }

    foreach ($input in @((Get-Prop $manifest 'external_inputs' @()))) {
        $script:Report.observed.external_inputs_checked++
        $declaredSource = [string](Get-Prop $input 'source' '')
        $copiedTo = [string](Get-Prop $input 'copied_to' '')
        $copyPath = Resolve-ProjectPath $copiedTo
        $expectedHash = ([string](Get-Prop $input 'sha256' '')).ToLowerInvariant()
        if (-not $copyPath -or -not (Test-UnderRoot $copyPath $script:ResolvedProjectRoot) -or
            -not (Test-Path -LiteralPath $copyPath -PathType Leaf)) {
            Add-Blocker 'external_input_not_copied' 'Entrada externa precisa possuir copia local rastreavel dentro do projeto.' $copiedTo @{
                source = $declaredSource
            }
            continue
        }
        $actualHash = Get-SgdkBinarySha256 -FilePath $copyPath
        if (-not $expectedHash -or $actualHash -ne $expectedHash) {
            Add-Blocker 'external_input_copy_hash_mismatch' 'A copia local da entrada externa nao corresponde ao hash declarado.' $copiedTo @{
                expected_sha256 = $expectedHash
                actual_sha256 = $actualHash
            }
        }

        $copiedRootValue = [string](Get-Prop $input 'copied_root' '')
        if (-not [string]::IsNullOrWhiteSpace($copiedRootValue)) {
            $copiedRoot = Resolve-ProjectPath $copiedRootValue
            $inventoryIssues = @()
            if (-not $copiedRoot -or -not (Test-UnderRoot $copiedRoot $script:ResolvedProjectRoot) -or
                -not (Test-Path -LiteralPath $copiedRoot -PathType Container)) {
                $inventoryIssues += "copied_root ausente ou fora do projeto: $copiedRootValue"
            } elseif (-not (Test-UnderRoot $copyPath $copiedRoot)) {
                $inventoryIssues += "copied_to precisa estar dentro de copied_root"
            }

            $inventory = $null
            try {
                $inventory = Get-Content -LiteralPath $copyPath -Raw -Encoding UTF8 | ConvertFrom-Json
            } catch {
                $inventoryIssues += "copied_to nao e inventario JSON valido: $($_.Exception.Message)"
            }

            if ($inventory) {
                $normalizedDeclaredSource = $declaredSource.Replace('\', '/').TrimEnd('/')
                $normalizedInventorySource = ([string](Get-Prop $inventory 'source' '')).Replace('\', '/').TrimEnd('/')
                if ($normalizedDeclaredSource -ne $normalizedInventorySource) {
                    $inventoryIssues += "source do inventario diverge do manifesto"
                }

                $inventoryFiles = @((Get-Prop $inventory 'files' @()))
                if ($inventoryFiles.Count -eq 0) {
                    $inventoryIssues += "inventario nao declara arquivos"
                }
                if ([int](Get-Prop $inventory 'file_count' -1) -ne $inventoryFiles.Count) {
                    $inventoryIssues += "file_count diverge da lista files"
                }

                $seenInventoryPaths = @{}
                $observedBytes = [int64]0
                foreach ($inventoryFile in $inventoryFiles) {
                    $relativePath = [string](Get-Prop $inventoryFile 'path' '')
                    $inventoryHash = ([string](Get-Prop $inventoryFile 'sha256' '')).ToLowerInvariant()
                    $inventoryPath = Resolve-ProjectPath $relativePath
                    if ([string]::IsNullOrWhiteSpace($relativePath) -or $seenInventoryPaths.ContainsKey($relativePath)) {
                        $inventoryIssues += "path ausente ou duplicado no inventario: $relativePath"
                        continue
                    }
                    $seenInventoryPaths[$relativePath] = $true
                    if (-not $inventoryPath -or -not $copiedRoot -or -not (Test-UnderRoot $inventoryPath $copiedRoot) -or
                        -not (Test-Path -LiteralPath $inventoryPath -PathType Leaf)) {
                        $inventoryIssues += "arquivo inventariado ausente ou fora de copied_root: $relativePath"
                        continue
                    }
                    $inventoryItem = Get-Item -LiteralPath $inventoryPath
                    $observedBytes += $inventoryItem.Length
                    $actualInventoryHash = Get-SgdkBinarySha256 -FilePath $inventoryPath
                    if (-not $inventoryHash -or $inventoryHash -ne $actualInventoryHash) {
                        $inventoryIssues += "hash divergente para arquivo inventariado: $relativePath"
                    }
                }
                if ([int64](Get-Prop $inventory 'total_bytes' -1) -ne $observedBytes) {
                    $inventoryIssues += "total_bytes diverge dos arquivos inventariados"
                }
            }

            if ($inventoryIssues.Count -gt 0) {
                Add-Blocker 'external_input_inventory_invalid' 'Inventario de entrada externa nao prova uma copia local integra.' $copyPath @{
                    source = $declaredSource
                    copied_root = $copiedRootValue
                    issues = @($inventoryIssues)
                }
            }
        }
    }

    $allowedReferenceRoots = @($script:ResolvedProjectRoot)
    foreach ($dependency in @((Get-Prop $manifest 'canonical_shared_dependencies' @()))) {
        $dependencyRoot = [System.IO.Path]::GetFullPath((Join-Path $WorkspaceRoot ([string]$dependency)))
        $allowedReferenceRoots += $dependencyRoot
    }
    $normalizedAllowedReferenceRoots = @($allowedReferenceRoots | ForEach-Object {
        ([System.IO.Path]::GetFullPath($_).TrimEnd('\', '/')).Replace('/', '\')
    })
    $referenceScanExcludedRoots = @('.agent', 'out', 'rascunho') |
        ForEach-Object { Join-Path $script:ResolvedProjectRoot $_ }
    $referenceScanExtensions = @('.asm', '.bat', '.c', '.h', '.json', '.md', '.ps1', '.py', '.res', '.s', '.sh', '.txt')
    $absoluteWindowsPathPattern = [regex]'(?i)\b[A-Z]:[\\/][^`"''<>\r\n]*'
    foreach ($file in Get-ChildItem -LiteralPath $script:ResolvedProjectRoot -Recurse -Force -File -ErrorAction SilentlyContinue) {
        if ($referenceScanExtensions -notcontains $file.Extension.ToLowerInvariant()) { continue }
        if ($file.FullName.Equals($manifestPath, [System.StringComparison]::OrdinalIgnoreCase)) { continue }
        $excluded = $false
        foreach ($excludedRoot in $referenceScanExcludedRoots) {
            if (Test-UnderRoot $file.FullName $excludedRoot) {
                $excluded = $true
                break
            }
        }
        if ($excluded) { continue }

        try {
            $lineNumber = 0
            foreach ($line in Get-Content -LiteralPath $file.FullName -Encoding UTF8 -ErrorAction Stop) {
                $lineNumber++
                foreach ($match in $absoluteWindowsPathPattern.Matches([string]$line)) {
                    $reference = $match.Value.Trim().TrimEnd('.', ',', ';', ':', ')', ']', '}')
                    $normalizedReference = [regex]::Replace($reference.Replace('/', '\'), '\\+', '\')
                    $allowed = $false
                    foreach ($allowedRoot in $normalizedAllowedReferenceRoots) {
                        if ($normalizedReference.Equals($allowedRoot, [System.StringComparison]::OrdinalIgnoreCase) -or
                            $normalizedReference.StartsWith($allowedRoot + '\', [System.StringComparison]::OrdinalIgnoreCase)) {
                            $allowed = $true
                            break
                        }
                    }
                    if (-not $allowed) {
                        $script:Report.observed.external_path_references += [ordered]@{
                            file = $file.FullName
                            line = $lineNumber
                            reference = $reference
                        }
                    }
                }
            }
        } catch {
            Add-Blocker 'project_hygiene_scan_failed' 'Nao foi possivel auditar referencias de caminho em arquivo ativo.' $file.FullName @{
                error = $_.Exception.Message
            }
        }
    }
    if ($script:Report.observed.external_path_references.Count -gt 0) {
        Add-Blocker 'external_path_reference_outside_project' 'Codigo, scripts, manifestos ou documentacao ativa referenciam caminho absoluto fora do projeto.' $script:ResolvedProjectRoot @{
            references = @($script:Report.observed.external_path_references)
        }
    }

    $workspaceRootAllowedFiles = @('.gitignore', 'AGENTS.md', 'CLAUDE.md', 'README.md')
    $workspaceOrphanExtensions = @('.c', '.h', '.s', '.asm', '.py', '.ps1', '.sh', '.tmp', '.temp', '.bak', '.json')
    foreach ($item in Get-ChildItem -LiteralPath $WorkspaceRoot -Force -File -ErrorAction SilentlyContinue) {
        if ($workspaceRootAllowedFiles -contains $item.Name) { continue }
        if ($workspaceOrphanExtensions -contains $item.Extension.ToLowerInvariant()) {
            $script:Report.observed.workspace_root_orphans += $item.FullName
        }
    }
    if ($script:Report.observed.workspace_root_orphans.Count -gt 0) {
        Add-Blocker 'workspace_root_orphan_artifact' 'A raiz do workspace possui arquivo tecnico ou temporario nao autorizado.' $WorkspaceRoot @{
            artifacts = @($script:Report.observed.workspace_root_orphans)
        }
    }
}

$script:Report.ready = ($script:Report.blocking_statuses.Count -eq 0)
$script:Report.status = if ($script:Report.ready) { 'passed' } else { 'blocked' }
$outputParent = Split-Path $OutputPath -Parent
if (-not (Test-Path -LiteralPath $outputParent -PathType Container)) {
    New-Item -ItemType Directory -Force -Path $outputParent | Out-Null
}
[System.IO.File]::WriteAllText($OutputPath, ($script:Report | ConvertTo-Json -Depth 20), [System.Text.Encoding]::UTF8)
Write-Host ("[validate_project_hygiene] status={0} blockers={1} report={2}" -f $script:Report.status, $script:Report.blocking_statuses.Count, $OutputPath)
if ($script:Report.ready) { exit 0 }
exit 1
