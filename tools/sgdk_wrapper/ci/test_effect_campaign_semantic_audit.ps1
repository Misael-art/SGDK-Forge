<#
.SYNOPSIS
    Verifica que audit_effect_campaign_semantics.ps1 reprova falso verde procedural.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$workspaceRoot = Split-Path (Split-Path $wrapperRoot -Parent) -Parent
$fixtureRoot = Join-Path $workspaceRoot "out\ci\effect_campaign_semantic_audit_fixture"
$campaignRoot = Join-Path $fixtureRoot "campaign"
$projectsRoot = Join-Path $fixtureRoot "projects"
$auditScript = Join-Path $wrapperRoot "audit_effect_campaign_semantics.ps1"
$reportPath = Join-Path $campaignRoot "semantic_audit_report.json"

$passed = 0
$failed = 0
$total = 0

function Assert-True {
    param([string]$Name, [bool]$Condition, [string]$Detail = "")
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

Write-Host ""
Write-Host "=== Effect Campaign Semantic Audit Test ==="
Write-Host ""

if (Test-Path -LiteralPath $fixtureRoot) {
    Remove-Item -LiteralPath $fixtureRoot -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $campaignRoot | Out-Null
New-Item -ItemType Directory -Force -Path $projectsRoot | Out-Null

$techniques = @()
for ($i = 1; $i -le 180; $i++) {
    $techniques += [ordered]@{
        local_id = ("fx_{0:000}" -f $i)
        axis_number = 1
        axis = "Profundidade & Movimento"
        axis_slug = "profundidade-movimento"
        canonical_or_honest_name = ("Fake effect {0}" -f $i)
        registry_id = if ($i -le 40) { "registry_effect" } else { "proposal_only" }
        registry_link = if ($i -le 40) { "registry_backed" } else { "proposal_only" }
        fallback = "Fallback procedural jogavel com BG_A/B, texto curto, colisao simples e variacao temporal segura."
        lib_cases_consulted = @()
    }
}
$coverage = [ordered]@{
    schema_version = "1.0.0"
    total_techniques = 180
    axes_count = 17
    canonical_180_catalog_verified = $false
    techniques = $techniques
}
[System.IO.File]::WriteAllText((Join-Path $campaignRoot "master_coverage_180.json"), ($coverage | ConvertTo-Json -Depth 8), [System.Text.Encoding]::UTF8)

$projectName = "AAA EFFECT LAB - profundidade-movimento [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]"
$projectRoot = Join-Path $projectsRoot $projectName
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot "src") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot "res\data") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot "out\logs") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot "out\agent_learning") | Out-Null

Set-Content -LiteralPath (Join-Path $projectRoot "src\main.c") -Encoding UTF8 -Value @'
#include <genesis.h>
#define USE_LINE_SCROLL 0
static const char *EFFECT_NAMES[] = {"fake"};
static void drawBackground(void) {
    VDP_drawText("safe rhythm lane", 1, 1);
    VDP_drawText("efeito empurra", 1, 2);
    VDP_drawText("microfase de laboratorio", 1, 3);
    VDP_drawText("line 01", 1, 4);
    VDP_drawText("line 02", 1, 5);
    VDP_drawText("line 03", 1, 6);
    VDP_drawText("line 04", 1, 7);
    VDP_drawText("line 05", 1, 8);
    VDP_drawText("line 06", 1, 9);
    VDP_drawText("line 07", 1, 10);
    VDP_drawText("line 08", 1, 11);
    VDP_drawText("line 09", 1, 12);
}
static void drawEffectPanel(void) { VDP_drawText("fallback procedural", 1, 13); }
int main(void) { drawBackground(); drawEffectPanel(); while(1){ SYS_doVBlankProcess(); } }
'@
Set-Content -LiteralPath (Join-Path $projectRoot "res\resources.res") -Encoding UTF8 -Value 'IMAGE lab_bg_b "data/lab_bg_b.png"'
[System.IO.File]::WriteAllBytes((Join-Path $projectRoot "res\data\lab_bg_b.png"), [byte[]](1..16))

$validation = [ordered]@{
    status_panel = [ordered]@{ ready_for_aaa = $true }
    blocking_statuses = @()
    observed_reports = [ordered]@{
        visual_delivery_gate = [ordered]@{ report_present = $false; stale = $false }
        freshness_audit = [ordered]@{ report_present = $false; stale = $false }
        scene_closeout_gate = [ordered]@{ report_present = $false; stale = $false }
        res_graph = [ordered]@{ report_present = $false; stale = $false }
    }
}
[System.IO.File]::WriteAllText((Join-Path $projectRoot "out\logs\validation_report.json"), ($validation | ConvertTo-Json -Depth 8), [System.Text.Encoding]::UTF8)

$effectNotes = [ordered]@{
    effects = @(
        [ordered]@{ implementation_note = "same fallback note"; fallback = "same fallback note" },
        [ordered]@{ implementation_note = "same fallback note"; fallback = "same fallback note" },
        [ordered]@{ implementation_note = "same fallback note"; fallback = "same fallback note" },
        [ordered]@{ implementation_note = "same fallback note"; fallback = "same fallback note" }
    )
}
[System.IO.File]::WriteAllText((Join-Path $projectRoot "out\agent_learning\effect_implementation_notes.json"), ($effectNotes | ConvertTo-Json -Depth 8), [System.Text.Encoding]::UTF8)

& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $auditScript -WorkspaceRoot $workspaceRoot -CampaignRoot $campaignRoot -ProjectsRoot $projectsRoot -ReportPath $reportPath -FailOnBlocker | Out-Host
$auditExit = $LASTEXITCODE
Assert-True "semantic audit exits non-zero" ($auditExit -ne 0) "exit=$auditExit"
Assert-True "semantic audit report generated" (Test-Path -LiteralPath $reportPath)

$report = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json
$codes = @($report.findings | ForEach-Object { $_.code })
Assert-True "blocks unverified proposal_only catalog" ($codes -contains "canonical_180_identity_unverified") ($codes -join ",")
Assert-True "blocks mass procedural fallback" ($codes -contains "mass_generic_procedural_fallback") ($codes -join ",")
Assert-True "blocks missing lib case consultation" ($codes -contains "registry_backed_without_lib_cases") ($codes -join ",")
Assert-True "blocks generic debug panel" ($codes -contains "generic_debug_text_panel") ($codes -join ",")
Assert-True "blocks generic lab resources" ($codes -contains "generic_lab_resource_set") ($codes -join ",")
Assert-True "blocks ready_for_aaa with unproven reports" ($codes -contains "ready_for_aaa_with_unproven_report") ($codes -join ",")
$repeatedLearningNotes = @($report.findings | Where-Object { $_.code -eq "repeated_effect_learning_notes" })
Assert-True "repeated effect learning notes are blockers" (
    @($repeatedLearningNotes | Where-Object { $_.severity -eq "blocker" }).Count -gt 0
) ($repeatedLearningNotes | ConvertTo-Json -Depth 5)

Write-Host ""
Write-Host "Total: $total | Passed: $passed | Failed: $failed"
if ($failed -gt 0) { exit 1 }
exit 0
