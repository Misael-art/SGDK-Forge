<#
.SYNOPSIS
    Audita ou canoniza materializacoes locais de .agent.

.DESCRIPTION
    A fonte canonica permanece em tools/sgdk_wrapper/.agent. Este script
    preserva snapshots auditaveis antes de substituir .agent fisicas por
    junctions para a canonica.
#>

[CmdletBinding()]
param(
    [ValidateSet("Audit", "Apply")]
    [string]$Mode = "Audit",

    [string[]]$ScopeRoots = @(),

    [string]$OutputRoot = "",

    [string]$CanonicalAgentDir = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$wrapperRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$workspaceRoot = Split-Path -Parent (Split-Path -Parent $wrapperRoot)
if (-not $CanonicalAgentDir) { $CanonicalAgentDir = Join-Path $wrapperRoot ".agent" }
$canonicalAgentDirFull = [System.IO.Path]::GetFullPath($CanonicalAgentDir)
if (-not (Test-Path -LiteralPath $canonicalAgentDirFull -PathType Container)) {
    throw "Canonical .agent not found: $canonicalAgentDirFull"
}

if (-not $OutputRoot) {
    $OutputRoot = Join-Path $workspaceRoot "out\agent_context_cleanup"
}
$runId = Get-Date -Format "yyyyMMdd_HHmmss"
$runRoot = Join-Path ([System.IO.Path]::GetFullPath($OutputRoot)) $runId
$snapshotRoot = Join-Path $runRoot "snapshots"
New-Item -ItemType Directory -Force -Path $snapshotRoot | Out-Null

$usingDefaultScope = ($ScopeRoots.Count -eq 0)
if ($usingDefaultScope) {
    $ScopeRoots = @(
        (Join-Path $workspaceRoot "SGDK_projects"),
        (Join-Path $workspaceRoot "SGDK_Engines")
    )
}
$scopeRootsFull = @($ScopeRoots | ForEach-Object { [System.IO.Path]::GetFullPath($_) } | Where-Object { Test-Path -LiteralPath $_ -PathType Container })

function Convert-ToLongPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    $full = [System.IO.Path]::GetFullPath($Path)
    if ($full.StartsWith("\\?\", [System.StringComparison]::Ordinal)) { return $full }
    if ($full.StartsWith("\\", [System.StringComparison]::Ordinal)) {
        return "\\?\UNC\" + $full.Substring(2)
    }
    return "\\?\" + $full
}

function Get-FileHashPortable {
    param([Parameter(Mandatory = $true)][string]$Path)

    $effectivePath = Convert-ToLongPath -Path $Path
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $stream = [System.IO.File]::OpenRead($effectivePath)
        try {
            return ([BitConverter]::ToString($sha.ComputeHash($stream)).Replace("-", "")).ToLowerInvariant()
        } finally {
            $stream.Dispose()
        }
    } finally {
        $sha.Dispose()
    }
}

function Get-NormalizedHash {
    param([Parameter(Mandatory = $true)][string]$Path)

    $effectivePath = Convert-ToLongPath -Path $Path
    if (-not [System.IO.File]::Exists($effectivePath)) { return "" }
    $extension = [System.IO.Path]::GetExtension($Path).ToLowerInvariant()
    if ($extension -in @(".md", ".json", ".yaml", ".yml", ".ps1", ".py", ".bat")) {
        $content = [System.IO.File]::ReadAllText($effectivePath, [System.Text.Encoding]::UTF8)
        $normalized = $content.Replace("`r`n", "`n")
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($normalized)
        $sha = [System.Security.Cryptography.SHA256]::Create()
        try { return ([BitConverter]::ToString($sha.ComputeHash($bytes)).Replace("-", "")).ToLowerInvariant() }
        finally { $sha.Dispose() }
    }
    return Get-FileHashPortable -Path $Path
}

function Get-FileManifest {
    param([Parameter(Mandatory = $true)][string]$Root)

    if (-not (Test-Path -LiteralPath $Root -PathType Container)) { return @() }
    $rootFull = [System.IO.Path]::GetFullPath($Root).TrimEnd('\')
    return @(
        Get-ChildItem -LiteralPath $Root -Recurse -File -Force -ErrorAction SilentlyContinue |
            Sort-Object FullName |
            ForEach-Object {
                $full = [System.IO.Path]::GetFullPath($_.FullName)
                [pscustomobject]@{
                    relative_path = ($full.Substring($rootFull.Length).TrimStart('\') -replace '\\', '/')
                    bytes = $_.Length
                    sha256 = Get-NormalizedHash -Path $full
                }
            }
    )
}

function Get-DirectoryDigest {
    param([Parameter(Mandatory = $true)][string]$Root)

    $manifest = @(Get-FileManifest -Root $Root)
    $payload = [string]::Join("`n", @($manifest | ForEach-Object { "{0}={1}" -f $_.relative_path, $_.sha256 }))
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($payload)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($sha.ComputeHash($bytes)).Replace("-", "")).ToLowerInvariant() }
    finally { $sha.Dispose() }
}

function Get-NodeInfo {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        return [ordered]@{ kind = "missing"; link_type = ""; target = ""; digest = "" }
    }
    $item = Get-Item -LiteralPath $Path -Force
    $isReparse = ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0
    $target = ""
    if ($item.Target) {
        $targets = @($item.Target)
        if ($targets.Count -gt 0) { $target = [string]$targets[0] }
    }
    $kind = if ($isReparse) { "link" } elseif ($item.PSIsContainer) { "physical_dir" } else { "file" }
    $digest = if ($item.PSIsContainer -and -not $isReparse) { Get-DirectoryDigest -Root $Path } elseif (-not $item.PSIsContainer) { Get-NormalizedHash -Path $Path } else { "" }
    return [ordered]@{ kind = $kind; link_type = ("" + $item.LinkType); target = $target; digest = $digest }
}

function Convert-ToSafeSnapshotName {
    param([Parameter(Mandatory = $true)][string]$Path)
    $relative = $Path
    if ($Path.StartsWith($workspaceRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        $relative = $Path.Substring($workspaceRoot.Length).TrimStart('\')
    }
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $hash = ([BitConverter]::ToString($sha.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($relative))).Replace("-", "")).ToLowerInvariant().Substring(0, 12)
    } finally {
        $sha.Dispose()
    }
    return ("agent_{0}.agent" -f $hash)
}

function Test-UnderAnyScope {
    param([Parameter(Mandatory = $true)][string]$Path)
    $full = [System.IO.Path]::GetFullPath($Path)
    foreach ($scope in $scopeRootsFull) {
        $scopeFull = $scope.TrimEnd('\') + '\'
        if (($full + '\').StartsWith($scopeFull, [System.StringComparison]::OrdinalIgnoreCase)) { return $true }
    }
    return $false
}

function Test-NestedGitRepo {
    param([Parameter(Mandatory = $true)][string]$Path)
    $current = Get-Item -LiteralPath (Split-Path -Parent $Path) -Force
    while ($current -and $current.FullName -ne $workspaceRoot) {
        if (Test-Path -LiteralPath (Join-Path $current.FullName ".git")) { return $true }
        $current = $current.Parent
    }
    return $false
}

function Get-AgentCandidates {
    $candidates = New-Object System.Collections.Generic.List[string]
    foreach ($scope in $scopeRootsFull) {
        foreach ($agentDir in @(Get-ChildItem -LiteralPath $scope -Directory -Force -Filter ".agent" -Recurse -ErrorAction SilentlyContinue)) {
            $full = [System.IO.Path]::GetFullPath($agentDir.FullName)
            if ($usingDefaultScope -and $full -match '\\(archives|\.tmp|\.claude|out|sdk)\\') { continue }
            if (Test-NestedGitRepo -Path $full) { continue }
            $candidates.Add($full)
        }
    }
    return @($candidates | Sort-Object -Unique)
}

function Get-DriftSummary {
    param([Parameter(Mandatory = $true)][string]$AgentDir)

    $localManifest = Get-FileManifest -Root $AgentDir
    $canonicalManifest = Get-FileManifest -Root $canonicalAgentDirFull
    $canonicalByPath = @{}
    foreach ($entry in $canonicalManifest) { $canonicalByPath[$entry.relative_path] = $entry.sha256 }
    $localByPath = @{}
    foreach ($entry in $localManifest) { $localByPath[$entry.relative_path] = $entry.sha256 }

    $missing = @($canonicalByPath.Keys | Where-Object { -not $localByPath.ContainsKey($_) } | Sort-Object)
    $extra = @($localByPath.Keys | Where-Object { -not $canonicalByPath.ContainsKey($_) } | Sort-Object)
    $changed = @($localByPath.Keys | Where-Object { $canonicalByPath.ContainsKey($_) -and $canonicalByPath[$_] -ne $localByPath[$_] } | Sort-Object)
    return [ordered]@{
        missing_count = $missing.Count
        extra_count = $extra.Count
        changed_count = $changed.Count
        missing_examples = @($missing | Select-Object -First 20)
        extra_examples = @($extra | Select-Object -First 20)
        changed_examples = @($changed | Select-Object -First 20)
    }
}

function Backup-AgentOrThrow {
    param([Parameter(Mandatory = $true)][string]$AgentDir)

    $safeName = Convert-ToSafeSnapshotName -Path $AgentDir
    $snapshotPath = Join-Path $snapshotRoot $safeName
    if (Test-Path -LiteralPath $snapshotPath) {
        Remove-Item -LiteralPath $snapshotPath -Recurse -Force
    }
    & robocopy $AgentDir $snapshotPath /MIR /R:1 /W:1 /NFL /NDL /NJH /NJS /NP | Out-Null
    if ($LASTEXITCODE -gt 7) {
        throw "Backup copy failed for $AgentDir (robocopy exit $LASTEXITCODE)"
    }
    $sourceDigest = Get-DirectoryDigest -Root $AgentDir
    $snapshotDigest = Get-DirectoryDigest -Root $snapshotPath
    if ($sourceDigest -ne $snapshotDigest) {
        throw "Backup verification failed for $AgentDir"
    }
    return [ordered]@{
        source_path = $AgentDir
        snapshot_path = $snapshotPath
        source_digest = $sourceDigest
        snapshot_digest = $snapshotDigest
        file_count = @(Get-FileManifest -Root $AgentDir).Count
    }
}

function Set-AgentJunction {
    param([Parameter(Mandatory = $true)][string]$AgentDir)

    if (-not (Test-UnderAnyScope -Path $AgentDir)) {
        throw "Unsafe path outside cleanup scope: $AgentDir"
    }

    $item = Get-Item -LiteralPath $AgentDir -Force
    $isReparse = ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0
    if ($isReparse) {
        Remove-Item -LiteralPath $AgentDir -Force
    } else {
        $emptyDeleteSource = Join-Path $runRoot "_empty_delete_source"
        New-Item -ItemType Directory -Force -Path $emptyDeleteSource | Out-Null
        & robocopy $emptyDeleteSource $AgentDir /MIR /R:1 /W:1 /NFL /NDL /NJH /NJS /NP | Out-Null
        if ($LASTEXITCODE -gt 7) {
            throw "Unable to clear physical .agent before junction replacement: $AgentDir (robocopy exit $LASTEXITCODE)"
        }
        Remove-Item -LiteralPath $AgentDir -Recurse -Force
    }
    New-Item -ItemType Junction -Path $AgentDir -Target $canonicalAgentDirFull -Force | Out-Null
}

$inventory = New-Object System.Collections.Generic.List[object]
$backups = New-Object System.Collections.Generic.List[object]

foreach ($agentDir in Get-AgentCandidates) {
    $node = Get-NodeInfo -Path $agentDir
    $drift = if ($node.kind -eq "physical_dir") { Get-DriftSummary -AgentDir $agentDir } else { [ordered]@{} }
    $expected = [System.IO.Path]::GetFullPath($canonicalAgentDirFull)
    $actual = if ($node.target) { [System.IO.Path]::GetFullPath($node.target) } else { "" }
    $isCanonicalLink = ($node.kind -eq "link" -and $actual -eq $expected)
    $action = if ($isCanonicalLink) { "keep" } elseif ($node.kind -eq "physical_dir") { "replace_physical_with_junction" } elseif ($node.kind -eq "link") { "retarget_link" } else { "skip" }

    $entry = [ordered]@{
        path = $agentDir
        kind = $node.kind
        link_type = $node.link_type
        target = $node.target
        canonical_target = $canonicalAgentDirFull
        is_canonical_link = $isCanonicalLink
        action = $action
        digest = $node.digest
        drift = $drift
        apply_status = "not_run"
        backup = $null
        error = ""
    }

    if ($Mode -eq "Apply" -and $action -ne "keep" -and $action -ne "skip") {
        try {
            if ($node.kind -eq "physical_dir") {
                $backup = Backup-AgentOrThrow -AgentDir $agentDir
                $backups.Add([pscustomobject]$backup)
                $entry.backup = $backup
            }
            Set-AgentJunction -AgentDir $agentDir
            $entry.apply_status = "replaced_with_junction"
        } catch {
            $entry.apply_status = "failed"
            $entry.error = $_.Exception.Message
        }
    }

    $inventory.Add([pscustomobject]$entry)
}

$inventoryPath = Join-Path $runRoot "agent_context_inventory.json"
$backupManifestPath = Join-Path $runRoot "agent_context_backup_manifest.json"
$driftReportPath = Join-Path $runRoot "agent_context_drift_report.md"

[System.IO.File]::WriteAllText($inventoryPath, ($inventory | ConvertTo-Json -Depth 12), [System.Text.Encoding]::UTF8)
[System.IO.File]::WriteAllText($backupManifestPath, ($backups | ConvertTo-Json -Depth 8), [System.Text.Encoding]::UTF8)

$lines = New-Object System.Collections.Generic.List[string]
$lines.Add("# Agent Context Cleanup Report")
$lines.Add("")
$lines.Add("- mode: $Mode")
$lines.Add("- canonical_agent_dir: $canonicalAgentDirFull")
$lines.Add("- candidates: $($inventory.Count)")
$lines.Add("- backups: $($backups.Count)")
$lines.Add("")
foreach ($entry in $inventory) {
    $lines.Add(("## {0}" -f $entry.path))
    $lines.Add(("- kind: {0}" -f $entry.kind))
    $lines.Add(("- action: {0}" -f $entry.action))
    $lines.Add(("- apply_status: {0}" -f $entry.apply_status))
    if ($entry.error) { $lines.Add(("- error: {0}" -f $entry.error)) }
    if ($entry.drift -and $entry.drift.Count -gt 0) {
        $lines.Add(("- drift: missing={0}, extra={1}, changed={2}" -f $entry.drift.missing_count, $entry.drift.extra_count, $entry.drift.changed_count))
    }
    $lines.Add("")
}
[System.IO.File]::WriteAllText($driftReportPath, [string]::Join("`r`n", $lines), [System.Text.Encoding]::UTF8)

[pscustomobject]@{
    mode = $Mode
    run_root = $runRoot
    inventory_path = $inventoryPath
    backup_manifest_path = $backupManifestPath
    drift_report_path = $driftReportPath
    candidates = $inventory.Count
    backups = $backups.Count
    replaced = @($inventory | Where-Object { $_.apply_status -eq "replaced_with_junction" }).Count
    failed = @($inventory | Where-Object { $_.apply_status -eq "failed" }).Count
} | ConvertTo-Json -Depth 6
