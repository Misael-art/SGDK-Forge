$ErrorActionPreference = 'Stop'

function Assert-True {
    param(
        [bool]$Condition,
        [string]$Message
    )
    if (-not $Condition) {
        throw "ASSERT FAILED: $Message"
    }
}

function Assert-Equal {
    param(
        $Expected,
        $Actual,
        [string]$Message
    )
    if ($Expected -ne $Actual) {
        throw "ASSERT FAILED: $Message. Expected '$Expected', got '$Actual'"
    }
}

function Invoke-Admission {
    param(
        [string[]]$Arguments,
        [string]$OutputPath
    )

    & powershell -NoProfile -ExecutionPolicy Bypass -File $AdmissionScript @Arguments -OutputPath $OutputPath | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "runtime admission command failed"
    }

    return Get-Content -Raw -Path $OutputPath | ConvertFrom-Json
}

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$AdmissionSchema = Join-Path $RepoRoot 'tools\sgdk_wrapper\schemas\runtime_admission_report.schema.json'
$TechnicalScopeSchema = Join-Path $RepoRoot 'tools\sgdk_wrapper\schemas\technical_change_scope_report.schema.json'
$AdmissionScript = Join-Path $RepoRoot 'tools\sgdk_wrapper\evaluate_runtime_admission.ps1'
$RouterScript = Join-Path $RepoRoot 'tools\sgdk_wrapper\route_vibe_playable_request.ps1'
$OutDir = Join-Path $RepoRoot 'out\ci\runtime_admission'
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

Assert-True (Test-Path -LiteralPath $AdmissionSchema) 'runtime_admission_report schema must exist'
Assert-True (Test-Path -LiteralPath $TechnicalScopeSchema) 'technical_change_scope_report schema must exist'
Assert-True (Test-Path -LiteralPath $AdmissionScript) 'runtime admission evaluator must exist'

$RoutePath = Join-Path $OutDir 'visual_route.json'
& powershell -NoProfile -ExecutionPolicy Bypass -File $RouterScript `
    -RequestText 'create a level with a hero fighting a boss' `
    -ProjectRoot $RepoRoot `
    -OutputPath $RoutePath `
    -SkipGraphify | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw 'router command failed while preparing runtime admission fixture'
}

$VisualAdmission = Invoke-Admission `
    -Arguments @('-AdmissionType', 'production_visual', '-RouteReportPath', $RoutePath) `
    -OutputPath (Join-Path $OutDir 'visual_admission.json')
Assert-Equal 'runtime_admission_report' $VisualAdmission.report_kind 'visual admission must produce canonical report'
Assert-Equal 'production_visual' $VisualAdmission.admission_type 'visual admission type must be explicit'
Assert-True (-not $VisualAdmission.runtime_admitted) 'production visual runtime must stay blocked without source approval and BlastEm evidence'
Assert-True (-not $VisualAdmission.technical_runtime_admitted) 'visual route must not masquerade as technical runtime'
Assert-Equal 'documented_visual_route_only' $VisualAdmission.claim_ceiling 'blocked visual route must cap claims'
Assert-True (@($VisualAdmission.blocking_statuses) -contains 'blocked_no_premium_source') 'missing premium source must block production visual runtime'

$TechnicalScopePath = Join-Path $OutDir 'technical_scope.json'
$TechnicalScope = [pscustomobject][ordered]@{
    schema_version = '1.0.0'
    report_kind = 'technical_change_scope_report'
    change_id = 'fixture_technical_only'
    changes_player_facing_visuals = $false
    changes_assets = $false
    changes_composition = $false
    changes_presentation = $false
    evidence = @('fixture explicitly says no visual assets, composition or presentation changed')
}
$TechnicalScope | ConvertTo-Json -Depth 20 | Set-Content -Encoding UTF8 -Path $TechnicalScopePath

$TechnicalAdmission = Invoke-Admission `
    -Arguments @('-AdmissionType', 'technical', '-TechnicalChangeScopePath', $TechnicalScopePath) `
    -OutputPath (Join-Path $OutDir 'technical_admission.json')
Assert-True (-not $TechnicalAdmission.runtime_admitted) 'technical runtime must not count as production visual runtime'
Assert-True $TechnicalAdmission.technical_runtime_admitted 'technical-only change may enter technical runtime'
Assert-True (-not $TechnicalAdmission.visual_status_promotion_allowed) 'technical runtime cannot promote visual status'
Assert-Equal 'technical_runtime_only' $TechnicalAdmission.claim_ceiling 'technical route must cap claims'

$LabAdmission = Invoke-Admission `
    -Arguments @('-AdmissionType', 'lab', '-LabReason', 'smoke test with lab_not_delivery placeholder') `
    -OutputPath (Join-Path $OutDir 'lab_admission.json')
Assert-True (-not $LabAdmission.runtime_admitted) 'lab runtime must not count as production visual runtime'
Assert-True $LabAdmission.runtime_lab_admitted 'lab admission must be explicit'
Assert-Equal 'lab_not_delivery' $LabAdmission.claim_ceiling 'lab route must cap claims as lab_not_delivery'
Assert-True (-not $LabAdmission.visual_status_promotion_allowed) 'lab runtime cannot promote visual status'

Write-Output 'test_runtime_admission: PASS'
