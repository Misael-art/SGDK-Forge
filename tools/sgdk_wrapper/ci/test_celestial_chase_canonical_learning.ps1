$ErrorActionPreference = "Stop"

$wrapperRoot = Split-Path -Parent $PSScriptRoot
$agentRoot = Join-Path $wrapperRoot ".agent"
$reviewPath = Join-Path $agentRoot "references/celestial_chase_canonical_learning_review_2026-06-19.json"
$protocolPath = Join-Path $agentRoot "references/production_truth_protocol.md"
$workflowPath = Join-Path $agentRoot "workflows/production-diagnostic-triage.md"
$schemaPath = Join-Path $wrapperRoot "schemas/canonical_learning_review.schema.json"

foreach ($path in @($reviewPath, $protocolPath, $workflowPath, $schemaPath)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "canonical_learning_dependency_missing:$path"
    }
}

$review = Get-Content -LiteralPath $reviewPath -Raw | ConvertFrom-Json
if ($review.schema_version -ne "1.0.0") {
    throw "canonical_learning_schema_version_invalid"
}
if ($review.artifact_kind -ne "canonical_learning_review") {
    throw "canonical_learning_artifact_kind_invalid"
}

$items = @($review.items)
$ids = @($items | ForEach-Object { $_.id })
if (($ids | Select-Object -Unique).Count -ne $ids.Count) {
    throw "canonical_learning_duplicate_ids"
}

$active = @($items | Where-Object { $_.decision -eq "active_policy" })
$pilots = @($items | Where-Object { $_.decision -eq "pilot_required" })
$rejected = @($items | Where-Object { $_.decision -eq "rejected_pattern" })

if ($active.Count -ne 6) {
    throw "canonical_learning_active_policy_count_invalid:$($active.Count)"
}
if ($pilots.Count -ne 7) {
    throw "canonical_learning_pilot_count_invalid:$($pilots.Count)"
}
if ($rejected.Count -ne 2) {
    throw "canonical_learning_rejected_count_invalid:$($rejected.Count)"
}

$requiredPilotContexts = @(
    "clean_host",
    "legacy_project",
    "new_project",
    "degraded_executor"
)
$broadPilotIds = @(
    "host_capability_preflight_v1",
    "staged_wrapper_result_contract_v1"
)
foreach ($pilotId in $broadPilotIds) {
    $pilot = $pilots | Where-Object { $_.id -eq $pilotId }
    if ($null -eq $pilot) {
        throw "canonical_learning_required_pilot_missing:$pilotId"
    }
    foreach ($context in $requiredPilotContexts) {
        if (@($pilot.required_validation) -notcontains $context) {
            throw "canonical_learning_pilot_context_missing:$($pilotId):$context"
        }
    }
}

$protocol = Get-Content -LiteralPath $protocolPath -Raw
$requiredProtocolTerms = @(
    "host_executor",
    "toolchain_wrapper",
    "rom_runtime",
    "creative_quality",
    "Metadados gerados pelo RESCOMP",
    "Input enviado nao equivale a input recebido",
    "technical_closeout: passed",
    "creative_promotion: blocked",
    "PostMessage",
    "SendInput"
)
foreach ($term in $requiredProtocolTerms) {
    if (-not $protocol.Contains($term)) {
        throw "production_truth_protocol_term_missing:$term"
    }
}

$workflow = Get-Content -LiteralPath $workflowPath -Raw
foreach ($heading in @(
    "## Entrada minima",
    "## Saida minima",
    "## Passa quando",
    "## Handoff para proxima etapa"
)) {
    if (-not $workflow.Contains($heading)) {
        throw "production_diagnostic_workflow_contract_missing:$heading"
    }
}

Write-Host "PASS Celestial Chase canonical learning curation"
exit 0
