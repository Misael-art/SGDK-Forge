param()

$ErrorActionPreference = "Stop"
$scriptPath = $MyInvocation.MyCommand.Path
$ciRoot = Split-Path -Parent $scriptPath
$wrapperRoot = Split-Path -Parent $ciRoot
$workspaceRoot = Split-Path -Parent (Split-Path -Parent $wrapperRoot)
$templateRoot = Join-Path $wrapperRoot "modelo"
$checker = Join-Path $wrapperRoot "check_prd_readiness.ps1"
$schemaPath = Join-Path $wrapperRoot "schemas\prd_readiness_report.schema.json"
$schemaValidator = Join-Path $wrapperRoot "validate_artifact_schema.ps1"

function Assert-True([string]$Name, [bool]$Condition, [string]$Detail = "") {
    if (-not $Condition) {
        if ($Detail) { throw "[FAIL] $Name - $Detail" }
        throw "[FAIL] $Name"
    }
    Write-Host "[OK] $Name"
}

if (-not (Test-Path -LiteralPath $templateRoot)) {
    throw "Template root not found: $templateRoot"
}

$protoReport = Join-Path $env:TEMP "prd_readiness_proto_test.json"
& powershell -NoProfile -ExecutionPolicy Bypass -File $checker -ProjectRoot $templateRoot -TargetProfile prototype -OutPath $protoReport
Assert-True "prototype check exits cleanly" ($LASTEXITCODE -eq 0)
$proto = Get-Content -LiteralPath $protoReport -Raw -Encoding UTF8 | ConvertFrom-Json
Assert-True "prototype status ok" ($proto.status -eq "ok") "status=$($proto.status)"
Assert-True "prototype has tier0 required" ([int]$proto.summary.required -ge 5) "required=$($proto.summary.required)"

$schemaOutput = & powershell -NoProfile -ExecutionPolicy Bypass -File $schemaValidator -SchemaPath $schemaPath -ArtifactPath $protoReport 2>&1
Assert-True "prototype report passes schema" ($LASTEXITCODE -eq 0) ($schemaOutput -join "; ")

$aaaReport = Join-Path $env:TEMP "prd_readiness_aaa_test.json"
& powershell -NoProfile -ExecutionPolicy Bypass -File $checker -ProjectRoot $templateRoot -TargetProfile AAA -OutPath $aaaReport -WarnOnly
Assert-True "AAA warn-only check exits cleanly" ($LASTEXITCODE -eq 0)
$aaa = Get-Content -LiteralPath $aaaReport -Raw -Encoding UTF8 | ConvertFrom-Json
Assert-True "AAA template is blocked while PRDs are seed/missing" ($aaa.status -eq "blocked") "status=$($aaa.status)"
Assert-True "AAA has blockers" ([int]$aaa.blockers.Count -gt 0) "blockers=$($aaa.blockers.Count)"

Write-Host "[OK] PRD readiness tests passed"
