<#
.SYNOPSIS
    Audits active and legacy SGDK skill lifecycle state without mutation.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)][string]$WorkspaceRoot = "",
    [Parameter(Mandatory = $false)][string]$OutputPath = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($WorkspaceRoot)) {
    $WorkspaceRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
}
$WorkspaceRoot = [System.IO.Path]::GetFullPath($WorkspaceRoot)
$AgentRoot = Join-Path $WorkspaceRoot "tools\sgdk_wrapper\.agent"
$ActiveRoot = Join-Path $AgentRoot "skills"
$LegacyRoot = Join-Path $AgentRoot "legacy\skills"
$RegistryPath = Join-Path $AgentRoot "references\skill_lifecycle_registry.json"

if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $OutputPath = Join-Path $WorkspaceRoot "out\logs\skill_lifecycle_report.json"
}

function Get-DirectoryContentHash {
    param([Parameter(Mandatory = $true)][string]$Path)

    $baseFull = [System.IO.Path]::GetFullPath($Path).TrimEnd("\", "/") + [System.IO.Path]::DirectorySeparatorChar
    $files = @(Get-ChildItem -LiteralPath $Path -File -Recurse | ForEach-Object {
        $fileFull = [System.IO.Path]::GetFullPath($_.FullName)
        if (-not $fileFull.StartsWith($baseFull, [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "skill_file_outside_payload:$fileFull"
        }
        [pscustomobject]@{
            File = $_
            Relative = $fileFull.Substring($baseFull.Length).Replace("\", "/")
        }
    } | Sort-Object -Property @{ Expression = {
        [System.Convert]::ToHexString([System.Text.Encoding]::UTF8.GetBytes([string]$_.Relative))
    } })
    $items = foreach ($item in $files) {
        $fileBytes = [System.IO.File]::ReadAllBytes($item.File.FullName)
        if ([System.IO.Path]::GetExtension($item.File.Name).ToLowerInvariant() -in @(".md", ".json", ".yaml", ".yml", ".txt")) {
            $text = [System.Text.Encoding]::UTF8.GetString($fileBytes).Replace("`r`n", "`n").Replace("`r", "`n")
            $fileBytes = [System.Text.Encoding]::UTF8.GetBytes($text)
        }
        $fileSha = [System.Security.Cryptography.SHA256]::Create()
        try {
            $fileHash = ([System.BitConverter]::ToString($fileSha.ComputeHash($fileBytes))).Replace("-", "").ToLowerInvariant()
        }
        finally {
            $fileSha.Dispose()
        }
        "$($item.Relative)`0$fileHash`n"
    }
    $bytes = [System.Text.Encoding]::UTF8.GetBytes([string]::Concat($items))
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        return ([System.BitConverter]::ToString($sha.ComputeHash($bytes))).Replace("-", "").ToLowerInvariant()
    }
    finally {
        $sha.Dispose()
    }
}

function Get-WordCount {
    param([Parameter(Mandatory = $true)][string]$SkillRoot)
    $skillFile = Join-Path $SkillRoot "SKILL.md"
    if (-not (Test-Path -LiteralPath $skillFile -PathType Leaf)) { return 0 }
    return [regex]::Matches(
        (Get-Content -LiteralPath $skillFile -Raw -Encoding UTF8),
        "\S+"
    ).Count
}

$errors = New-Object System.Collections.Generic.List[string]
$details = New-Object System.Collections.Generic.List[object]
$activeCount = 0
$legacyCount = 0

if (-not (Test-Path -LiteralPath $RegistryPath -PathType Leaf)) {
    $errors.Add("skill_lifecycle_registry_missing")
    $registry = $null
}
else {
    try {
        $registry = Get-Content -LiteralPath $RegistryPath -Raw -Encoding UTF8 | ConvertFrom-Json
    }
    catch {
        $errors.Add("skill_lifecycle_registry_unreadable")
        $registry = $null
    }
}

if ($registry) {
    $entries = @($registry.entries)
    $ids = @{}
    foreach ($entry in $entries) {
        $skillId = [string]$entry.skill_id
        $lifecycle = [string]$entry.lifecycle
        if ([string]::IsNullOrWhiteSpace($skillId)) {
            $errors.Add("entry_skill_id_missing")
            continue
        }
        if ($ids.ContainsKey($skillId)) {
            $errors.Add("duplicate_skill_id:$skillId")
            continue
        }
        $ids[$skillId] = $entry

        $isActive = $lifecycle -eq "active"
        $payload = if ($isActive) {
            Join-Path $ActiveRoot $skillId
        }
        else {
            Join-Path $LegacyRoot $skillId
        }
        $opposite = if ($isActive) {
            Join-Path $LegacyRoot $skillId
        }
        else {
            Join-Path $ActiveRoot $skillId
        }

        if (-not (Test-Path -LiteralPath (Join-Path $payload "SKILL.md") -PathType Leaf)) {
            $errors.Add("skill_payload_missing:$skillId")
            continue
        }
        if (Test-Path -LiteralPath $opposite) {
            $errors.Add("skill_present_in_both_roots:$skillId")
        }

        $actualHash = Get-DirectoryContentHash -Path $payload
        $words = Get-WordCount -SkillRoot $payload
        if ($isActive) {
            $activeCount++
            if ($words -gt [int]$entry.context_budget_words) {
                $errors.Add("skill_context_budget_exceeded:$skillId")
            }
        }
        else {
            $legacyCount++
            if ($actualHash -ne ([string]$entry.content_sha256).ToLowerInvariant()) {
                $errors.Add("skill_hash_mismatch:$skillId")
            }
        }

        foreach ($replacement in @($entry.replacement_skills)) {
            $replacementPath = Join-Path $ActiveRoot ([string]$replacement)
            if (-not (Test-Path -LiteralPath (Join-Path $replacementPath "SKILL.md") -PathType Leaf)) {
                $errors.Add("replacement_skill_missing:$($entry.skill_id):$replacement")
            }
        }

        $details.Add([ordered]@{
            skill_id = $skillId
            lifecycle = $lifecycle
            path = $payload
            content_sha256 = $actualHash
            word_count = $words
            context_budget_words = [int]$entry.context_budget_words
        })
    }

    if (Test-Path -LiteralPath $LegacyRoot -PathType Container) {
        $legacyBaseFull = [System.IO.Path]::GetFullPath($LegacyRoot).TrimEnd("\", "/") + [System.IO.Path]::DirectorySeparatorChar
        foreach ($skillFile in Get-ChildItem -LiteralPath $LegacyRoot -Filter "SKILL.md" -File -Recurse) {
            $legacyDir = Split-Path $skillFile.FullName -Parent
            $legacyDirFull = [System.IO.Path]::GetFullPath($legacyDir)
            if (-not $legacyDirFull.StartsWith($legacyBaseFull, [System.StringComparison]::OrdinalIgnoreCase)) {
                $errors.Add("legacy_skill_outside_root:$legacyDirFull")
                continue
            }
            $legacyId = $legacyDirFull.Substring($legacyBaseFull.Length).Replace("\", "/")
            if (-not $ids.ContainsKey($legacyId)) {
                $errors.Add("legacy_skill_unregistered:$legacyId")
            }
        }
    }
}

$report = [ordered]@{
    schema_version = "1.0.0"
    generated_at = (Get-Date).ToUniversalTime().ToString("o")
    tool_name = "audit_skill_lifecycle"
    status = if ($errors.Count -eq 0) { "ok" } else { "error" }
    workspace_root = $WorkspaceRoot
    registry_path = $RegistryPath
    summary = [ordered]@{
        active = $activeCount
        legacy = $legacyCount
        errors = $errors.Count
        warnings = 0
    }
    errors = @($errors | ForEach-Object { $_ })
    warnings = @()
    skills = @($details | ForEach-Object { $_ })
}

$outputDir = Split-Path -Parent $OutputPath
if ($outputDir) { New-Item -ItemType Directory -Force -Path $outputDir | Out-Null }
$report | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $OutputPath -Encoding UTF8
$report | ConvertTo-Json -Depth 10 | Write-Output

if ($errors.Count -gt 0) { exit 1 }
exit 0
