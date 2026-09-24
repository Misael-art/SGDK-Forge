Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$repoRoot = Split-Path (Split-Path $wrapperRoot -Parent) -Parent
$graphifyWrapper = Join-Path $wrapperRoot "graphify_forge.ps1"
$fixtureRoot = Join-Path $repoRoot "out\graphify_update_failure_fixture"
$fakeBin = Join-Path $fixtureRoot "fake-bin"
$graphOut = Join-Path $fixtureRoot "graphify-out"

function Write-Utf8Text {
    param([string]$Path, [string]$Text)
    $parent = Split-Path $Path -Parent
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
    [IO.File]::WriteAllText($Path, $Text, [Text.UTF8Encoding]::new($false))
}

try {
    Remove-Item -LiteralPath $fixtureRoot -Recurse -Force -ErrorAction SilentlyContinue
    New-Item -ItemType Directory -Path $fakeBin, $graphOut -Force | Out-Null
    Copy-Item -LiteralPath (Join-Path $repoRoot ".graphifyignore") -Destination $fixtureRoot

    Write-Utf8Text -Path (Join-Path $fixtureRoot "tools\sgdk_wrapper\.agent\rules\SGDK_GLOBAL.md") -Text "# fixture"
    Write-Utf8Text -Path (Join-Path $fixtureRoot "doc\05_technical\sample.md") -Text "# fixture"
    Write-Utf8Text -Path (Join-Path $fixtureRoot "doc\07_game_design\sample.md") -Text "# fixture"
    Write-Utf8Text -Path (Join-Path $fixtureRoot "doc\06_AI_MEMORY_BANK.md") -Text "# fixture"

    $graph = @{
        nodes = @(
            @{ source_file = "tools/sgdk_wrapper/.agent/rules/SGDK_GLOBAL.md" }
        )
        edges = @()
    } | ConvertTo-Json -Depth 10
    Write-Utf8Text -Path (Join-Path $graphOut "graph.json") -Text $graph

    $fakeGraphify = if ($IsWindows) {
        Join-Path $fakeBin "graphify.cmd"
    } else {
        Join-Path $fakeBin "graphify"
    }
    if ($IsWindows) {
        Write-Utf8Text -Path $fakeGraphify -Text "@echo off`r`necho simulated graphify refusal 1>&2`r`nexit /b 9`r`n"
    } else {
        Write-Utf8Text -Path $fakeGraphify -Text "#!/bin/sh`necho simulated graphify refusal 1>&2`nexit 9`n"
        & chmod +x $fakeGraphify
    }

    $oldPath = $env:PATH
    $env:PATH = "$fakeBin$([System.IO.Path]::PathSeparator)$oldPath"
    $output = (& pwsh -NoProfile -ExecutionPolicy Bypass -File $graphifyWrapper `
        -Action update -RepoRoot $fixtureRoot 2>&1 | Out-String)
    $exitCode = $LASTEXITCODE

    if ($exitCode -eq 0) {
        throw "graphify update failure was incorrectly accepted:`n$output"
    }
    if (Test-Path -LiteralPath (Join-Path $graphOut "FORGE_FRESHNESS.json")) {
        throw "failed graphify update wrote a fresh snapshot"
    }

    if ($IsWindows) {
        Write-Utf8Text -Path $fakeGraphify -Text "@echo off`r`nping -n 6 127.0.0.1 >nul`r`nexit /b 0`r`n"
    } else {
        Write-Utf8Text -Path $fakeGraphify -Text "#!/bin/sh`nsleep 5`nexit 0`n"
        & chmod +x $fakeGraphify
    }
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $timeoutOutput = (& pwsh -NoProfile -ExecutionPolicy Bypass -File $graphifyWrapper `
        -Action update -RepoRoot $fixtureRoot -GraphifyTimeoutSeconds 1 2>&1 | Out-String)
    $timeoutExitCode = $LASTEXITCODE
    $sw.Stop()

    if ($timeoutExitCode -eq 0) {
        throw "graphify timeout was incorrectly accepted:`n$timeoutOutput"
    }
    if ($timeoutOutput -notmatch 'graphify_timeout') {
        throw "graphify timeout did not report graphify_timeout:`n$timeoutOutput"
    }
    if ($sw.Elapsed.TotalSeconds -gt 10) {
        throw "graphify timeout did not return promptly: $($sw.Elapsed.TotalSeconds)s"
    }

    Write-Host "[PASS] graphify update failure remains stale"
}
finally {
    if ($null -ne $oldPath) {
        $env:PATH = $oldPath
    }
    Remove-Item -LiteralPath $fixtureRoot -Recurse -Force -ErrorAction SilentlyContinue
}
