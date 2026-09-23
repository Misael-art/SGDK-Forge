<#
.SYNOPSIS
    Protege o build SGDK quando o caminho canonico do workspace contem espacos.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$envScript = Join-Path $wrapperRoot 'env.bat'
$buildScript = Join-Path $wrapperRoot 'build_inner.bat'
$cleanScript = Join-Path $wrapperRoot 'clean.bat'

$envText = Get-Content -LiteralPath $envScript -Raw
$buildText = Get-Content -LiteralPath $buildScript -Raw
$cleanText = Get-Content -LiteralPath $cleanScript -Raw

$passed = 0
$failed = 0
$total = 0

function Assert-Match {
    param([string]$Name, [string]$Text, [string]$Pattern)
    $script:total++
    if ($Text -match $Pattern) {
        $script:passed++
        Write-Host "  [PASS] $Name"
    } else {
        $script:failed++
        Write-Host "  [FAIL] $Name"
    }
}

function Assert-NoMatch {
    param([string]$Name, [string]$Text, [string]$Pattern)
    $script:total++
    if ($Text -notmatch $Pattern) {
        $script:passed++
        Write-Host "  [PASS] $Name"
    } else {
        $script:failed++
        Write-Host "  [FAIL] $Name"
    }
}

Write-Host ''
Write-Host '=== GDK Short Path Build Contract ==='
Write-Host ''

Assert-Match 'env calcula GDK_SHORT pelo caminho 8.3' $envText 'for\s+%%I\s+in\s+\("%GDK%"\)\s+do\s+set\s+"GDK_SHORT=%%~sI"'
Assert-Match 'env exporta GDK_SHORT ao chamador' $envText 'set\s+"GDK_SHORT=%GDK_SHORT%"'
Assert-Match 'env reconhece a junction canonica sem espacos' $envText 'SGDKForge\\sdk\\sgdk-2\.11'
Assert-Match 'env exporta GDK_BUILD_ROOT ao chamador' $envText 'set\s+"GDK_BUILD_ROOT=%GDK_BUILD_ROOT%"'
Assert-Match 'build prefere GDK_BUILD_ROOT sem espacos e sem tilde' $buildText 'if\s+defined\s+GDK_BUILD_ROOT\s+if\s+exist\s+"%GDK_BUILD_ROOT%\\makefile\.gen"\s+set\s+"GDK_MAKEFILE_ROOT=%GDK_BUILD_ROOT%"'
Assert-Match 'clean prefere GDK_BUILD_ROOT sem espacos e sem tilde' $cleanText 'if\s+defined\s+GDK_BUILD_ROOT\s+if\s+exist\s+"%GDK_BUILD_ROOT%\\makefile\.gen"\s+set\s+"GDK_MAKEFILE_ROOT=%GDK_BUILD_ROOT%"'
Assert-Match 'build prefere GDK_SHORT para makefile.gen' $buildText 'if\s+defined\s+GDK_SHORT\s+if\s+exist\s+"%GDK_SHORT%\\makefile\.gen"\s+set\s+"GDK_MAKEFILE_ROOT=%GDK_SHORT%"'
Assert-Match 'clean prefere GDK_SHORT para makefile.gen' $cleanText 'if\s+defined\s+GDK_SHORT\s+if\s+exist\s+"%GDK_SHORT%\\makefile\.gen"\s+set\s+"GDK_MAKEFILE_ROOT=%GDK_SHORT%"'
Assert-Match 'build invoca make pelo root sem espacos' $buildText 'make\s+-f\s+"%GDK_MAKEFILE_ROOT%\\makefile\.gen"'
Assert-Match 'clean invoca make pelo root sem espacos' $cleanText 'make\s+-f\s+"%GDK_MAKEFILE_ROOT%\\makefile\.gen"\s+clean'
Assert-NoMatch 'build nao passa GDK longo diretamente ao make' $buildText 'make\s+-f\s+"%GDK%\\\\makefile\.gen"'
Assert-NoMatch 'clean nao passa GDK longo diretamente ao make' $cleanText 'make\s+-f\s+"%GDK%\\\\makefile\.gen"'

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
