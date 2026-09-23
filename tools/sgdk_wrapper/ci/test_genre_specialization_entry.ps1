param(
    [Parameter(Mandatory = $true)]
    [string]$ExpectedId
)

$ErrorActionPreference = "Stop"

$wrapperRoot = Split-Path -Parent $PSScriptRoot
$workspaceRoot = Split-Path -Parent (Split-Path -Parent $wrapperRoot)
$registryPath = Join-Path $workspaceRoot "doc/07_game_design/genre_specialization_registry.json"
$globalGate = Join-Path $PSScriptRoot "test_genre_specialization_registry.ps1"

if (-not (Test-Path -LiteralPath $registryPath -PathType Leaf)) {
    throw "genre_registry_missing:$registryPath"
}
if (-not (Test-Path -LiteralPath $globalGate -PathType Leaf)) {
    throw "genre_registry_gate_missing:$globalGate"
}

$global:LASTEXITCODE = 0
& $globalGate
$globalGateExit = if ($null -eq $LASTEXITCODE) { 0 } else { [int]$LASTEXITCODE }
if ($globalGateExit -ne 0) {
    throw "genre_registry_global_gate_failed:$globalGateExit"
}

$registry = Get-Content -LiteralPath $registryPath -Raw | ConvertFrom-Json
$matches = [System.Collections.Generic.List[object]]::new()

function Find-ActiveRegistryEntry {
    param(
        [Parameter(Mandatory = $true)]
        [object]$Node
    )

    if ($null -eq $Node) {
        return
    }

    if ($Node -is [System.Collections.IEnumerable] -and
        $Node -isnot [string] -and
        $Node -isnot [System.Management.Automation.PSCustomObject]) {
        foreach ($item in $Node) {
            if ($null -ne $item) {
                Find-ActiveRegistryEntry -Node $item
            }
        }
        return
    }

    if ($Node -is [System.Management.Automation.PSCustomObject]) {
        $properties = @($Node.PSObject.Properties)
        $containsExpectedId = $false
        foreach ($property in $properties) {
            if ($property.Value -is [string] -and $property.Value -eq $ExpectedId) {
                $containsExpectedId = $true
                break
            }
        }

        $statusProperty = $Node.PSObject.Properties["status"]
        if ($containsExpectedId -and $null -ne $statusProperty -and $statusProperty.Value -eq "active") {
            $matches.Add($Node)
        }

        foreach ($property in $properties) {
            if ($null -ne $property.Value -and $property.Value -isnot [string]) {
                Find-ActiveRegistryEntry -Node $property.Value
            }
        }
    }
}

Find-ActiveRegistryEntry -Node $registry

if ($matches.Count -ne 1) {
    throw "genre_registry_active_entry_count_invalid:$($ExpectedId):$($matches.Count)"
}

Write-Host "PASS genre specialization active entry: $ExpectedId"
exit 0
