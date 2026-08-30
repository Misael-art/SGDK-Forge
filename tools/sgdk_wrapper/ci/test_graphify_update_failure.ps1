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

    Write-Utf8Text -Path (Join-Path $fakeBin "graphify.cmd") -Text "@echo off`r`necho simulated graphify refusal 1>&2`r`nexit /b 9`r`n"

    $oldPath = $env:PATH
    $env:PATH = "$fakeBin;$oldPath"
    $output = (& pwsh -NoProfile -ExecutionPolicy Bypass -File $graphifyWrapper `
        -Action update -RepoRoot $fixtureRoot 2>&1 | Out-String)
    $exitCode = $LASTEXITCODE

    if ($exitCode -eq 0) {
        throw "graphify update failure was incorrectly accepted:`n$output"
    }
    if (Test-Path -LiteralPath (Join-Path $graphOut "FORGE_FRESHNESS.json")) {
        throw "failed graphify update wrote a fresh snapshot"
    }

    Write-Host "[PASS] graphify update failure remains stale"
}
finally {
    if ($null -ne $oldPath) {
        $env:PATH = $oldPath
    }
    Remove-Item -LiteralPath $fixtureRoot -Recurse -Force -ErrorAction SilentlyContinue
}
