<#
.SYNOPSIS
    Builds all AAA Effect Lab projects with a conservative parallel throttle.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [int]$Throttle = 3
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$WorkspaceRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
$ProjectsRoot = Join-Path $WorkspaceRoot "SGDK_projects"
$CampaignRoot = Join-Path $ProjectsRoot "ProjectLab_effect_campaign [VER.001] [SGDK 211] [GEN] [HOMEBREW] [DEMO]"
$SummaryRoot = Join-Path $CampaignRoot "out\logs"
if (-not (Test-Path -LiteralPath $SummaryRoot -PathType Container)) {
    New-Item -ItemType Directory -Force -Path $SummaryRoot | Out-Null
}
$SummaryPath = Join-Path $SummaryRoot "aaa_effect_lab_build_matrix.json"

$projects = @(Get-ChildItem -LiteralPath $ProjectsRoot -Directory -Filter "AAA EFFECT LAB - *" | Sort-Object Name)
$jobs = New-Object System.Collections.ArrayList
$rows = New-Object System.Collections.ArrayList

function Receive-FinishedJob {
    param([Parameter(Mandatory = $true)]$Job)

    $row = Receive-Job -Job $Job -ErrorAction Stop
    Remove-Job -Job $Job -Force
    return $row
}

foreach ($project in $projects) {
    while ($jobs.Count -ge $Throttle) {
        Start-Sleep -Seconds 2
        foreach ($finished in @($jobs | Where-Object { $_.State -in @("Completed", "Failed", "Stopped") })) {
            [void]$rows.Add((Receive-FinishedJob -Job $finished))
            [void]$jobs.Remove($finished)
        }
    }

    $projectRoot = $project.FullName
    $projectName = $project.Name
    Write-Host ("[build-matrix] start {0}" -f $projectName)
    $job = Start-Job -ArgumentList $projectRoot, $projectName -ScriptBlock {
        param($ProjectRoot, $ProjectName)

        $started = (Get-Date).ToUniversalTime()
        $logDir = Join-Path $ProjectRoot "out\logs"
        if (-not (Test-Path -LiteralPath $logDir -PathType Container)) {
            New-Item -ItemType Directory -Force -Path $logDir | Out-Null
        }
        $logPath = Join-Path $logDir "build_matrix_build.log"
        $buildBat = Join-Path $ProjectRoot "build.bat"
        $output = & cmd.exe /c $buildBat 2>&1
        $exitCode = if ($LASTEXITCODE -is [int]) { [int]$LASTEXITCODE } else { 0 }
        [System.IO.File]::WriteAllLines($logPath, [string[]]($output | ForEach-Object { [string]$_ }), [System.Text.Encoding]::UTF8)
        $finished = (Get-Date).ToUniversalTime()
        $romPath = Join-Path $ProjectRoot "out\rom.bin"
        $romExists = Test-Path -LiteralPath $romPath -PathType Leaf
        $romSha256 = $null
        $romSize = $null
        if ($romExists) {
            $item = Get-Item -LiteralPath $romPath
            $romSize = [int64]$item.Length
            $stream = [System.IO.File]::OpenRead($romPath)
            try {
                $sha = [System.Security.Cryptography.SHA256]::Create()
                try {
                    $romSha256 = ([System.BitConverter]::ToString($sha.ComputeHash($stream))).Replace("-", "").ToLowerInvariant()
                } finally {
                    $sha.Dispose()
                }
            } finally {
                $stream.Dispose()
            }
        }
        [ordered]@{
            project = $ProjectName
            project_root = $ProjectRoot
            status = if ($exitCode -eq 0 -and $romExists) { "ok" } else { "failed" }
            exit_code = $exitCode
            rom_exists = [bool]$romExists
            rom_sha256 = $romSha256
            rom_size_bytes = $romSize
            log_path = $logPath
            started_at = $started.ToString("o")
            finished_at = $finished.ToString("o")
            duration_ms = [int](($finished - $started).TotalMilliseconds)
        }
    }
    [void]$jobs.Add($job)
}

while ($jobs.Count -gt 0) {
    Start-Sleep -Seconds 2
    foreach ($finished in @($jobs | Where-Object { $_.State -in @("Completed", "Failed", "Stopped") })) {
        $row = Receive-FinishedJob -Job $finished
        Write-Host ("[build-matrix] {0}: {1}" -f $row.project, $row.status)
        [void]$rows.Add($row)
        [void]$jobs.Remove($finished)
    }
}

$summary = [ordered]@{
    schema_version = "1.0.0"
    generated_at = (Get-Date).ToUniversalTime().ToString("o")
    tool_name = "run_effect_lab_build_matrix"
    project_count = $projects.Count
    built_count = @($rows | Where-Object { $_.status -eq "ok" }).Count
    failed_count = @($rows | Where-Object { $_.status -ne "ok" }).Count
    status = if (@($rows | Where-Object { $_.status -ne "ok" }).Count -eq 0 -and $projects.Count -eq 17) { "ok" } else { "failed" }
    rows = @($rows | Sort-Object project)
}

$summary | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $SummaryPath -Encoding UTF8
Write-Host ("[build-matrix] status={0} report={1}" -f $summary.status, $SummaryPath)
if ($summary.status -ne "ok") { exit 1 }
exit 0
