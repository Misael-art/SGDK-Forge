<#
.SYNOPSIS
    Validates active/legacy skill lifecycle integrity.
#>

[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Executor real do host; nunca "powershell" literal (ausente no Linux).
. (Join-Path $PSScriptRoot "../lib/host_executors_bootstrap.ps1")
$script:HostPwsh = Get-PowerShellExecutable

# Motor canonico de hash. Este teste mantinha a sua propria copia com
# `Sort-Object FullName` e separador `\` literal, o que no Linux produzia chave
# e ordem erradas e falhava com `restoration fixture hash mismatch`. Consumir o
# modulo garante que a verificacao de reversibilidade usa exatamente o mesmo
# motor que o auditor.
. (Join-Path $PSScriptRoot "../lib/skill_payload_hash_bootstrap.ps1")

$WrapperRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$WorkspaceRoot = Split-Path (Split-Path $WrapperRoot -Parent) -Parent
$AgentRoot = Join-Path $WrapperRoot ".agent"
$RegistryPath = Join-Path $AgentRoot "references\skill_lifecycle_registry.json"
$SchemaPath = Join-Path $WrapperRoot "schemas\skill_lifecycle_registry.schema.json"
$AuditScript = Join-Path $WrapperRoot "audit_skill_lifecycle.ps1"
$ReportPath = Join-Path ([System.IO.Path]::GetTempPath()) ("skill_lifecycle_{0}.json" -f ([guid]::NewGuid().ToString("N")))

function Assert-True {
    param(
        [Parameter(Mandatory = $true)][bool]$Condition,
        [Parameter(Mandatory = $true)][string]$Message
    )
    if (-not $Condition) { throw $Message }
}

Assert-True (Test-Path -LiteralPath $RegistryPath -PathType Leaf) "skill lifecycle registry missing"
Assert-True (Test-Path -LiteralPath $SchemaPath -PathType Leaf) "skill lifecycle schema missing"
Assert-True (Test-Path -LiteralPath $AuditScript -PathType Leaf) "skill lifecycle auditor missing"

try {
    & $script:HostPwsh -NoProfile -ExecutionPolicy Bypass -File $AuditScript `
        -WorkspaceRoot $WorkspaceRoot `
        -OutputPath $ReportPath | Out-Null
    Assert-True ($LASTEXITCODE -eq 0) "skill lifecycle audit failed"
    Assert-True (Test-Path -LiteralPath $ReportPath -PathType Leaf) "skill lifecycle report missing"

    $report = Get-Content -LiteralPath $ReportPath -Raw -Encoding UTF8 | ConvertFrom-Json
    Assert-True ($report.status -eq "ok") "expected lifecycle status ok, got '$($report.status)'"
    Assert-True ([int]$report.summary.errors -eq 0) "expected zero lifecycle errors"
    Assert-True ([int]$report.summary.active -gt 0) "expected active skills"
    Assert-True ([int]$report.summary.legacy -gt 0) "expected legacy skills"

    $registry = Get-Content -LiteralPath $RegistryPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $merged = @($registry.entries | Where-Object lifecycle -eq "merged")[0]
    $fixtureRoot = Join-Path ([IO.Path]::GetTempPath()) ("skill_restore_{0}" -f ([guid]::NewGuid().ToString("N")))
    $fixtureSkill = Join-Path $fixtureRoot ([string]$merged.skill_id)
    New-Item -ItemType Directory -Path (Split-Path $fixtureSkill -Parent) -Force | Out-Null
    Copy-Item -LiteralPath (Join-Path $WorkspaceRoot ([string]$merged.legacy_path)) -Destination $fixtureSkill -Recurse
    Assert-True ((Get-SkillPayloadHash -Path $fixtureSkill) -eq [string]$merged.content_sha256) "restoration fixture hash mismatch"
    Assert-True (Test-Path -LiteralPath (Join-Path $fixtureSkill "SKILL.md")) "restoration fixture payload missing"
    Remove-Item -LiteralPath $fixtureRoot -Recurse -Force

    Write-Host "[PASS] skill lifecycle registry is complete, hashed and reversible"
}
finally {
    Remove-Item -LiteralPath $ReportPath -Force -ErrorAction SilentlyContinue
}
