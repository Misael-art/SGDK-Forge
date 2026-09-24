[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$python = Get-Command python3 -ErrorAction SilentlyContinue
if ($null -eq $python) { $python = Get-Command python -ErrorAction Stop }

& $python.Source (Join-Path $root 'tools/sgdk_wrapper/ci/test_canonical_fixture_contracts.py')
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $python.Source (Join-Path $root 'tools/sgdk_wrapper/ci/test_project_learning_loop.py')
exit $LASTEXITCODE
