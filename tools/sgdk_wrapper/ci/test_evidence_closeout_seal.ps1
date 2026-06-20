<#
.SYNOPSIS
    Regression test for ROM-identity sealing after emulator capture.
#>

[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$WrapperRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$ScriptUnderTest = Join-Path $WrapperRoot "finalize_emulator_evidence.ps1"
$CaptureScript = Join-Path $WrapperRoot "capture_blastem_evidence.ps1"

function Assert-True {
    param(
        [Parameter(Mandatory = $true)][bool]$Condition,
        [Parameter(Mandatory = $true)][string]$Message
    )
    if (-not $Condition) { throw $Message }
}

$ProjectRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("sgdk_evidence_seal_{0}" -f ([guid]::NewGuid().ToString("N")))
$LogDir = Join-Path $ProjectRoot "out\logs"
$EvidenceDir = Join-Path $ProjectRoot "out\evidence\blastem"
New-Item -ItemType Directory -Force -Path $LogDir, $EvidenceDir | Out-Null

try {
    $captureSource = Get-Content -LiteralPath $CaptureScript -Raw
    Assert-True ($captureSource -match "finalize_emulator_evidence\.ps1") "Standalone BlastEm capture must invoke the evidence finalizer."

    $romPath = Join-Path $ProjectRoot "out\rom.bin"
    [System.IO.File]::WriteAllBytes($romPath, [byte[]](1, 2, 3, 4))
    [System.IO.File]::WriteAllBytes((Join-Path $EvidenceDir "screenshot.png"), [byte[]](1, 2, 3))
    [System.IO.File]::WriteAllBytes((Join-Path $EvidenceDir "save.sram"), [byte[]](4, 5, 6))
    $romHash = (Get-FileHash -LiteralPath $romPath -Algorithm SHA256).Hash.ToLowerInvariant()

    @{
        schema_version = "1.0.0"
        rom_path = $romPath
        rom_sha256 = $romHash
        screenshot_path = (Join-Path $EvidenceDir "screenshot.png")
        sram_path = (Join-Path $EvidenceDir "save.sram")
        evidence_stale = $false
    } | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $LogDir "emulator_session.json") -Encoding UTF8

    $reportPath = Join-Path $LogDir "evidence_closeout_report.json"
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ScriptUnderTest -ProjectRoot $ProjectRoot -OutputPath $reportPath | Out-Null
    Assert-True ($LASTEXITCODE -eq 0) "Matching ROM identity should seal evidence."
    $sealed = Get-Content -LiteralPath $reportPath -Raw | ConvertFrom-Json
    Assert-True ($sealed.seal_status -eq "sealed") "Expected seal_status=sealed."
    Assert-True ([bool]$sealed.rom_identity_stable) "Expected stable ROM identity."
    Assert-True (@($sealed.evidence_artifacts).Count -eq 2) "Expected every captured artifact in the seal manifest."
    Assert-True (@($sealed.evidence_artifacts | Where-Object { $_.sha256 -match '^[0-9a-f]{64}$' }).Count -eq 2) "Expected SHA-256 for every captured artifact."

    Remove-Item -LiteralPath (Join-Path $EvidenceDir "screenshot.png") -Force
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ScriptUnderTest -ProjectRoot $ProjectRoot -OutputPath $reportPath | Out-Null
    Assert-True ($LASTEXITCODE -ne 0) "A missing captured artifact must invalidate the evidence seal."
    $missingArtifact = Get-Content -LiteralPath $reportPath -Raw | ConvertFrom-Json
    Assert-True ($missingArtifact.blocker_code -eq "emulator_evidence_artifact_missing") "Expected missing evidence artifact blocker."
    [System.IO.File]::WriteAllBytes((Join-Path $EvidenceDir "screenshot.png"), [byte[]](1, 2, 3))

    [System.IO.File]::WriteAllBytes($romPath, [byte[]](9, 8, 7, 6))
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ScriptUnderTest -ProjectRoot $ProjectRoot -OutputPath $reportPath | Out-Null
    Assert-True ($LASTEXITCODE -ne 0) "A rebuilt ROM must invalidate the capture seal."
    $invalid = Get-Content -LiteralPath $reportPath -Raw | ConvertFrom-Json
    Assert-True ($invalid.blocker_code -eq "rom_identity_changed_after_capture") "Expected ROM identity blocker."

    Write-Host "[PASS] evidence closeout seals one ROM identity and rejects rebuild drift"
}
finally {
    Remove-Item -LiteralPath $ProjectRoot -Recurse -Force -ErrorAction SilentlyContinue
}
