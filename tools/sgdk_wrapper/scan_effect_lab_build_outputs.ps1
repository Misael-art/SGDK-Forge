<#
.SYNOPSIS
    Scans current AAA Effect Lab ROM outputs without rebuilding.
#>

[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$WorkspaceRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
$ProjectsRoot = Join-Path $WorkspaceRoot "SGDK_projects"
$CampaignRoot = Join-Path $ProjectsRoot "ProjectLab_effect_campaign [VER.001] [SGDK 211] [GEN] [HOMEBREW] [DEMO]"
$SummaryRoot = Join-Path $CampaignRoot "out\logs"
if (-not (Test-Path -LiteralPath $SummaryRoot -PathType Container)) {
    New-Item -ItemType Directory -Force -Path $SummaryRoot | Out-Null
}
$SummaryPath = Join-Path $SummaryRoot "aaa_effect_lab_build_scan_final.json"

$rows = @()
foreach ($project in @(Get-ChildItem -LiteralPath $ProjectsRoot -Directory -Filter "AAA EFFECT LAB - *" | Sort-Object Name)) {
    $romPath = Join-Path $project.FullName "out\rom.bin"
    $romExists = Test-Path -LiteralPath $romPath -PathType Leaf
    $romSha256 = $null
    $romSizeBytes = $null
    $romLastWriteUtc = $null
    if ($romExists) {
        $item = Get-Item -LiteralPath $romPath
        $romSizeBytes = [int64]$item.Length
        $romLastWriteUtc = $item.LastWriteTimeUtc.ToString("o")
        $romSha256 = (Get-FileHash -LiteralPath $romPath -Algorithm SHA256).Hash.ToLowerInvariant()
    }
    $rows += [ordered]@{
        project = $project.Name
        project_root = $project.FullName
        status = if ($romExists) { "ok" } else { "missing_rom" }
        rom_exists = [bool]$romExists
        rom_size_bytes = $romSizeBytes
        rom_last_write_utc = $romLastWriteUtc
        rom_sha256 = $romSha256
    }
}

$failedCount = @($rows | Where-Object { $_.status -ne "ok" }).Count
$summary = [ordered]@{
    schema_version = "1.0.0"
    generated_at = (Get-Date).ToUniversalTime().ToString("o")
    tool_name = "scan_effect_lab_build_outputs"
    project_count = $rows.Count
    built_count = @($rows | Where-Object { $_.status -eq "ok" }).Count
    failed_count = $failedCount
    status = if ($rows.Count -eq 17 -and $failedCount -eq 0) { "ok" } else { "failed" }
    rows = $rows
}

$summary | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $SummaryPath -Encoding UTF8
Write-Host ("[build-scan] status={0} built={1}/{2} report={3}" -f $summary.status, $summary.built_count, $summary.project_count, $SummaryPath)
if ($summary.status -ne "ok") { exit 1 }
exit 0

