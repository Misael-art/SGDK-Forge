<# 
.SYNOPSIS
    Regression test for tools/sgdk_wrapper/art_diagnostic.py ASCII-safe output on Windows terminals.
#>

[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$WrapperRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$ScriptUnderTest = Join-Path $WrapperRoot "art_diagnostic.py"
if (-not (Test-Path -LiteralPath $ScriptUnderTest -PathType Leaf)) {
    throw "Script under test not found: $ScriptUnderTest"
}

function Assert-True {
    param(
        [Parameter(Mandatory = $true)][bool]$Condition,
        [Parameter(Mandatory = $true)][string]$Message
    )
    if (-not $Condition) { throw $Message }
}

$ProjectRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("SGDK_ART_DIAG_TEST_[{0}]" -f ([guid]::NewGuid().ToString("N")))
$ResDir = Join-Path $ProjectRoot "res"
$DataDir = Join-Path $ProjectRoot "data"
foreach ($p in @($ResDir, $DataDir)) { [System.IO.Directory]::CreateDirectory($p) | Out-Null }

$pngPath = Join-Path $ResDir "sprite_ok.png"
& py -c @"
from PIL import Image
img = Image.new('P', (8,8))
palette = [255,0,255, 0,0,0] + [0,0,0]*14
img.putpalette(palette)
img.save(r'$pngPath')
"@ | Out-Null

$output = & py $ScriptUnderTest --project $ProjectRoot
Assert-True ($LASTEXITCODE -eq 0 -or $LASTEXITCODE -eq 1) "Unexpected exit code from art_diagnostic.py: $LASTEXITCODE"

$nonAscii = @($output.ToCharArray() | Where-Object { [int]$_ -gt 127 })
Assert-True ($nonAscii.Count -eq 0) ("Expected ASCII-only output, got non-ASCII char count: {0}" -f $nonAscii.Count)

Write-Host "[PASS] art_diagnostic output is ASCII-safe by default"

$TempRoot = [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath()).TrimEnd('\', '/')
$ResolvedFixture = [System.IO.Path]::GetFullPath($ProjectRoot)
if ($ResolvedFixture.StartsWith($TempRoot + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) {
    Remove-Item -LiteralPath $ResolvedFixture -Recurse -Force
}
