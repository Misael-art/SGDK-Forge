<#
.SYNOPSIS
    Garante que o runtime capture em BlastEm nao volte a depender de foreground/input.
.DESCRIPTION
    O caminho de runtime deve operar via SRAM bootstrap e fechamento nao interativo.
    Este teste inspeciona o script para impedir regressao acidental para SendInput,
    navegacao injetada ou helper de close interativo.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$scriptPath = Join-Path $wrapperRoot 'run_runtime_capture.ps1'
$content = Get-Content -LiteralPath $scriptPath -Raw

$passed = 0
$failed = 0
$total = 0

function Assert-True {
    param([string]$Name, [bool]$Condition, [string]$Detail = '')
    $script:total++
    if ($Condition) {
        $script:passed++
        Write-Host "  [PASS] $Name"
    } else {
        $script:failed++
        $msg = "  [FAIL] $Name"
        if ($Detail) { $msg += " -- $Detail" }
        Write-Host $msg
    }
}

function Get-FunctionBlock {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$FunctionName
    )

    $pattern = "(?s)function\s+$([regex]::Escape($FunctionName))\s*\{.*?^\}"
    $match = [regex]::Match($Source, $pattern, [System.Text.RegularExpressions.RegexOptions]::Multiline)
    if (-not $match.Success) {
        throw "Funcao nao encontrada: $FunctionName"
    }
    return $match.Value
}

Write-Host ''
Write-Host '=== Runtime Capture BlastEm Noninteractive Test ==='
Write-Host ''

$invokeBlock = Get-FunctionBlock -Source $content -FunctionName 'Invoke-BlastEmRuntimeCapture'
$closeBlock = Get-FunctionBlock -Source $content -FunctionName 'Close-BlastEmForRuntimeCapture'

Write-Host '--- Assertions ---'
Assert-True 'capture_begin usa modo sram_bootstrap_only' ($invokeBlock -match 'navigation_mode\s*=\s*"sram_bootstrap_only"')
Assert-True 'navegacao extra eh ignorada explicitamente' ($invokeBlock -match 'navigation_ignored')
Assert-True 'Invoke-BlastEmNavigation nao e chamado no runtime capture' (-not ($invokeBlock -match 'Invoke-BlastEmNavigation'))
Assert-True 'Ensure-BlastEmForeground nao e chamado no runtime capture' (-not ($invokeBlock -match 'Ensure-BlastEmForeground'))
Assert-True 'Close-BlastEmGracefully nao e usado no runtime capture' (-not ($invokeBlock -match 'Close-BlastEmGracefully'))
Assert-True 'runtime usa close nao interativo dedicado' ($invokeBlock -match 'Close-BlastEmForRuntimeCapture')
Assert-True 'helper de close usa CloseMainWindow' ($closeBlock -match 'CloseMainWindow\(')
Assert-True 'helper de close pode matar processo sem teclado' ($closeBlock -match 'Stop-Process\s+-Id')
Assert-True 'helper de close se declara nao interativo' ($closeBlock -match 'interactive\s*=\s*\$false')

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
