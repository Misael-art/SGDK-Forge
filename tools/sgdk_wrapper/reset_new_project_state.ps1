<#
.SYNOPSIS
    Remove runtime/history claims inherited from the canonical model.

.DESCRIPTION
    This script is intentionally narrow and must run only during new-project
    bootstrap, before the project has an out/rom.bin. It preserves structural
    design seeds and source assets while resetting operational truth.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectRoot,

    [Parameter(Mandatory = $true)]
    [switch]$ConfirmNewProjectSeed
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$project = [System.IO.Path]::GetFullPath($ProjectRoot)
$manifest = Join-Path $project ".mddev/project.json"
$docRoot = Join-Path $project "doc"
$romPath = Join-Path $project "out/rom.bin"

if (-not $ConfirmNewProjectSeed) {
    throw "reset_new_project_state requires -ConfirmNewProjectSeed"
}
if (-not (Test-Path -LiteralPath $manifest -PathType Leaf)) {
    throw "Project manifest missing: $manifest"
}
if (-not (Test-Path -LiteralPath $docRoot -PathType Container)) {
    throw "Project doc directory missing: $docRoot"
}
if (Test-Path -LiteralPath $romPath -PathType Leaf) {
    throw "Refusing to reset a project that already contains out/rom.bin"
}

$projectName = Split-Path $project -Leaf
$timestamp = (Get-Date).ToUniversalTime().ToString("o")
$memoryPath = Join-Path $docRoot "10-memory-bank.md"
$changelogPath = Join-Path $docRoot "changelog/changelog.md"
$romHistoryPath = Join-Path $docRoot "changelog/roms"

$memory = @"
<!-- SGDK GENERATED STATUS START -->
## 0. Estado Derivado dos Artefatos

- Fonte: bootstrap de projeto novo
- Ultima sincronizacao: $timestamp
- Ultimo build versionado: nenhum
- ROM vigente: inexistente
- Evidencia de emulador: inexistente
- Gate visual: blocked_no_premium_source
- Gate gameplay: nao provado
- Gate AAA: ready_for_aaa=false
<!-- SGDK GENERATED STATUS END -->

# 10 - Memory Bank & Context Tracker - $projectName

**Ultima atualizacao:** $timestamp
**Fase atual:** fundacao documental
**Proxima fase:** classificar contexto e metodologia antes de arte/runtime

## 1. Estado operacional

- documentado: estrutura inicial materializada
- implementado: nao
- buildado: nao
- testado_em_emulador: nao
- validado_budget: nao
- audio: nao validado
- ready_for_aaa: false

## 2. Bloqueios iniciais

- contexto e metodologia ainda precisam de classificacao humana
- fonte visual premium ainda nao foi aprovada
- nenhuma ROM ou evidencia de BlastEm existe

## 3. Regra de continuidade

Atualize este arquivo, o changelog e os manifests sempre que a verdade
operacional mudar. Nunca copie hashes, builds, aprovacao ou evidencia do modelo.
"@

$changelog = @"
# Changelog Canonico - $projectName

## $timestamp - bootstrap

- projeto criado a partir da estrutura canonica
- historico de ROM, hashes e evidencia do modelo removido
- status inicial: documentado; nao buildado; nao testado em emulador
- proximo gate: classificar contexto e metodologia
"@

$memory | Set-Content -LiteralPath $memoryPath -Encoding UTF8
$changelogParent = Split-Path $changelogPath -Parent
if (-not (Test-Path -LiteralPath $changelogParent -PathType Container)) {
    New-Item -ItemType Directory -Force -Path $changelogParent | Out-Null
}
$changelog | Set-Content -LiteralPath $changelogPath -Encoding UTF8

if (Test-Path -LiteralPath $romHistoryPath -PathType Container) {
    Remove-Item -LiteralPath $romHistoryPath -Recurse -Force
}

$brandingPath = Join-Path $docRoot "branding_sequence_contract.json"
if (Test-Path -LiteralPath $brandingPath -PathType Leaf) {
    $branding = Get-Content -LiteralPath $brandingPath -Raw | ConvertFrom-Json
    if ($null -ne $branding.runtime_capture_current) {
        $branding.runtime_capture_current.rom_sha256 = $null
        $branding.runtime_capture_current.blastem_status = "not_run"
        $branding.runtime_capture_current.target_scene = $null
        $branding.runtime_capture_current.runtime_scene_id = $null
        $branding.runtime_capture_current.capture_status = "not_captured"
        $branding.runtime_capture_current.frames_seen = 0
        $branding.runtime_capture_current.samples_recorded = 0
        $branding.runtime_capture_current.over_budget_frames = 0
        $branding.runtime_capture_current.cpu_load_max = 0
        $branding.runtime_capture_current.frame_cpu_ratio_p95 = 0
        $branding.runtime_capture_current.sprite_engine_peak = 0
        $branding.runtime_capture_current.max_scanline_sprites = 0
        $branding.runtime_capture_current.screenshot_path = $null
        $branding.runtime_capture_current.sram_path = $null
        $branding.runtime_capture_current.runtime_metrics_path = $null
        $branding.runtime_capture_current.visual_vdp_dump_path = $null
        $branding.runtime_capture_current.visual_vdp_dump_status = "not_captured"
        $branding.runtime_capture_current.performance_gate = "not_measured"
    }
    if ($null -ne $branding.verification_current) {
        $branding.verification_current.direct_sgdk_make = "not_run"
        $branding.verification_current.wrapper_build = "not_built"
        $branding.verification_current.res_graph = "not_run"
        $branding.verification_current.validate_audio = "not_run"
        $branding.verification_current.blastem = "not_run"
        $branding.verification_current.freshness = "not_run"
        $branding.verification_current.scene_closeout_gate = "not_run"
        $branding.verification_current.known_blockers = @(
            "project_not_built",
            "emulator_evidence_missing"
        )
    }
    $branding | ConvertTo-Json -Depth 100 | Set-Content -LiteralPath $brandingPath -Encoding UTF8
}

Write-Host "[OK] New-project operational state reset: $project"
