<# Validates post-seal tamper/ROM drift detection used by scene closeout. #>
[CmdletBinding()] param()
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$WrapperRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$Audit = Join-Path $WrapperRoot "audit_fresh_evidence_bundle.ps1"
$Fixture = Join-Path ([System.IO.Path]::GetTempPath()) ("sgdk_fresh_evidence_closeout_{0}" -f [guid]::NewGuid().ToString("N"))
$Evidence = Join-Path $Fixture "out\evidence\blastem"
$Logs = Join-Path $Fixture "out\logs"
New-Item -ItemType Directory -Force -Path $Evidence, $Logs | Out-Null
$Rom = Join-Path $Fixture "out\rom.bin"
[IO.File]::WriteAllBytes($Rom, [byte[]](1..64))
$RomHash = (Get-FileHash -LiteralPath $Rom -Algorithm SHA256).Hash.ToLowerInvariant()
$Session = "closeout-fixture-session"
$cards = @()
foreach ($name in @("rom", "screenshot", "sram", "vdp_dump", "runtime_metrics")) {
    $path = Join-Path $Evidence ("{0}.bin" -f $name)
    [IO.File]::WriteAllBytes($path, [Text.Encoding]::UTF8.GetBytes("$Session-$name"))
    $cards += [ordered]@{
        name = $name; path = [IO.Path]::GetFileName($path); session_id = $Session; rom_sha256 = $RomHash
        sha256 = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
        size_bytes = (Get-Item $path).Length; captured_at = (Get-Date).ToUniversalTime().ToString("o")
    }
}
$now = (Get-Date).ToUniversalTime().ToString("o")
[ordered]@{
    schema_version = "1.0.0"; generated_at = $now; tool_name = "seal_fresh_evidence_bundle"; tool_version = "1.0.0"
    status = "sealed"; session_id = $Session; session_started_at = $now; session_completed_at = $now
    rom_sha256 = $RomHash; expected_rom_sha256 = $RomHash; emulator = @{ ref = "fixture"; commit = ("a" * 64) }
    artifacts = $cards; semantic_capture_valid = $true; blockers = @(); claim_limit = "fixture"
} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $Evidence "evidence_manifest.json") -Encoding UTF8
[ordered]@{
    schema_version = "1.0.0"; generated_at = $now; tool_name = "fresh_evidence_bundle_audit"; tool_version = "1.0.0"
    status = "ok"; session_id = $Session; rom_sha256 = $RomHash; same_session = $true; artifact_count = 5
    required_artifact_count = 5; blockers = @(); manifest_path = "evidence_manifest.json"
} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $Evidence "freshness_report.json") -Encoding UTF8

& $Audit -ProjectRoot $Fixture
if ($LASTEXITCODE -ne 0) { throw "fresh bundle fixture should pass" }
[IO.File]::AppendAllText((Join-Path $Evidence "screenshot.bin"), "tamper")
& $Audit -ProjectRoot $Fixture
if ($LASTEXITCODE -eq 0) { throw "tampered artifact should block closeout audit" }
$report = Get-Content -LiteralPath (Join-Path $Logs "fresh_evidence_bundle_audit_report.json") -Raw | ConvertFrom-Json
if (@($report.blockers) -notcontains "fresh_evidence_artifact_hash_mismatch:screenshot") { throw "tamper blocker missing" }
[IO.File]::AppendAllText($Rom, "different-rom")
& $Audit -ProjectRoot $Fixture
if ($LASTEXITCODE -eq 0) { throw "different current ROM should block closeout audit" }
$report = Get-Content -LiteralPath (Join-Path $Logs "fresh_evidence_bundle_audit_report.json") -Raw | ConvertFrom-Json
if (@($report.blockers) -notcontains "fresh_evidence_current_rom_mismatch") { throw "current ROM mismatch blocker missing" }
Write-Host "[PASS] fresh evidence closeout audit accepts sealed fixture and blocks tamper or ROM drift"
