param(
    [ValidateSet("Show", "Set", "Reset")]
    [string]$Action = "Show",

    [ValidateSet("idle", "create_new_project", "analyze_existing_project", "train_agent", "laboratory", "curation")]
    [string]$Mode,

    [ValidateSet("none", "director", "architect", "artist", "hardware", "coder", "audio", "qa", "learner", "curator", "lab_operator")]
    [string]$Perspective,

    [string]$ActiveProject,
    [string]$Reason,
    [switch]$UserConfirmed,
    [string]$StatePath
)

$ErrorActionPreference = "Stop"

$workspaceRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")
if (-not $StatePath) {
    $StatePath = Join-Path $workspaceRoot "doc\agent_session_state.json"
}

if ($env:SGDK_SKIP_AGENT_ENVIRONMENT_GUARD -ne "1") {
    $agentEnvGuard = Join-Path $workspaceRoot "tools\sgdk_wrapper\assert_agent_environment.ps1"
    if (Test-Path -LiteralPath $agentEnvGuard -PathType Leaf) {
        & powershell -NoProfile -ExecutionPolicy Bypass -File $agentEnvGuard -RepoRoot $workspaceRoot
        if ($LASTEXITCODE -ne 0) {
            throw "Agent environment guard failed. See graphify-out/AGENT_ENVIRONMENT_REPORT.json."
        }
    }
}

$defaultPerspectiveByMode = @{
    "idle" = "none"
    "create_new_project" = "director"
    "analyze_existing_project" = "qa"
    "train_agent" = "learner"
    "laboratory" = "lab_operator"
    "curation" = "curator"
}

function New-DefaultState {
    [pscustomobject]@{
        schema_version = "1.0.0"
        state_id = "workspace_session_state"
        last_updated = "2026-06-05T00:00:00Z"
        current_mode = "idle"
        current_perspective = "none"
        active_project = $null
        mode_history = @()
        pending_transition = $null
        pending_insights = @()
        consent_policy = [pscustomobject]@{
            mode_switch_requires_user_confirmation = $true
            perspective_switch_requires_user_confirmation = $true
            canonical_patch_requires_explicit_human_approval = $true
            direct_task_bypasses_menu_when_unambiguous = $true
        }
    }
}

function Read-State {
    if (Test-Path -LiteralPath $StatePath) {
        return Get-Content -LiteralPath $StatePath -Raw | ConvertFrom-Json
    }

    return New-DefaultState
}

function Write-State {
    param([object]$State)

    $parent = Split-Path -Parent $StatePath
    if (-not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent | Out-Null
    }

    $State | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $StatePath -Encoding UTF8
}

function Write-AgentMenu {
    param([object]$State)

    @"
+--------------------------------------------------+
|                 SGDK FORGE                       |
|        .----.      FORGE-16      .----.          |
|       / o  o \   16-BIT READY   / o  o \         |
|       \  --  /------------------\  --  /         |
|        '----'                    '----'          |
+--------------------------------------------------+

[1] CRIAR NOVO PROJETO DE JOGO DE MEGA DRIVE
[2] ANALISAR PROJETO EXISTENTE
[3] TREINAR AGENTE
[4] LABORATORIO
[5] CURADORIA

Estado atual:
  modo:        $($State.current_mode)
  perspectiva: $($State.current_perspective)
  projeto:     $(if ($State.active_project) { $State.active_project } else { "<nenhum>" })

Uso:
  tools/sgdk_wrapper/show_agent_menu.ps1
  tools/sgdk_wrapper/show_agent_menu.ps1 -Action Set -Mode analyze_existing_project -Perspective qa -ActiveProject "SGDK_projects/foo" -Reason "Usuario escolheu analisar projeto" -UserConfirmed
"@
}

$state = Read-State

if ($Action -eq "Show") {
    Write-AgentMenu -State $state
    exit 0
}

if (-not $UserConfirmed) {
    throw "Mode or perspective transition requires -UserConfirmed."
}

$previousMode = $state.current_mode
$previousPerspective = $state.current_perspective

if ($Action -eq "Reset") {
    $Mode = "idle"
    $Perspective = "none"
    $ActiveProject = $null
    if (-not $Reason) {
        $Reason = "Session state reset with human confirmation."
    }
}

if ($Action -eq "Set") {
    if (-not $Mode) {
        throw "-Mode is required for -Action Set."
    }
    if (-not $Perspective) {
        $Perspective = $defaultPerspectiveByMode[$Mode]
    }
    if (-not $Reason) {
        throw "-Reason is required for -Action Set."
    }
}

if ($Mode -eq "idle") {
    $Perspective = "none"
    $ActiveProject = $null
}

if ($Mode -ne "idle" -and $Perspective -eq "none") {
    throw "Non-idle mode requires a concrete perspective."
}

$timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")

$history = @()
if ($null -ne $state.mode_history) {
    $history = @($state.mode_history)
}

$history += [pscustomobject]@{
    timestamp = $timestamp
    from_mode = $previousMode
    to_mode = $Mode
    from_perspective = $previousPerspective
    to_perspective = $Perspective
    reason = $Reason
    user_confirmed = $true
}

$state.current_mode = $Mode
$state.current_perspective = $Perspective
$state.active_project = if ($ActiveProject) { $ActiveProject } else { $null }
$state.mode_history = $history
$state.pending_transition = $null
$state.last_updated = $timestamp

Write-State -State $state
Write-AgentMenu -State $state
