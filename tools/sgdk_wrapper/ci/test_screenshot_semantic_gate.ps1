<#
.SYNOPSIS
    Integration regression for screenshot semantic audit and evidence sealing.
#>

[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$wrapperRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$auditScript = Join-Path $wrapperRoot "audit_screenshot_semantics.ps1"
$finalizerScript = Join-Path $wrapperRoot "finalize_emulator_evidence.ps1"
$powerShellHost = (Get-Process -Id $PID).Path

function Assert-True {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) { throw $Message }
}

function New-SyntheticPpm {
    param(
        [string]$Path,
        [bool]$LowInformation
    )
    $width = 64
    $height = 48
    $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::Create)
    try {
        $header = [System.Text.Encoding]::ASCII.GetBytes("P6`n$width $height`n255`n")
        $stream.Write($header, 0, $header.Length)
        for ($y = 0; $y -lt $height; $y++) {
            for ($x = 0; $x -lt $width; $x++) {
                if ($LowInformation) {
                    $pixel = [byte[]](250, 250, 250)
                } elseif (([math]::Floor($x / 4) + [math]::Floor($y / 4)) % 2 -eq 0) {
                    $pixel = [byte[]](8, 24, 52)
                } else {
                    $pixel = [byte[]](54, 146, 206)
                }
                $stream.Write($pixel, 0, 3)
            }
        }
    } finally {
        $stream.Dispose()
    }
}

$fixtureRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("sgdk_semantic_images_{0}" -f ([guid]::NewGuid().ToString("N")))
New-Item -ItemType Directory -Force -Path $fixtureRoot | Out-Null
$badFixture = Join-Path $fixtureRoot "low_information.png"
$goodFixture = Join-Path $fixtureRoot "rich_scene.png"
New-SyntheticPpm -Path $badFixture -LowInformation $true
New-SyntheticPpm -Path $goodFixture -LowInformation $false

function New-EvidenceFixture {
    param([string]$ScreenshotSource)

    $root = Join-Path ([System.IO.Path]::GetTempPath()) ("sgdk_semantic_gate_{0}" -f ([guid]::NewGuid().ToString("N")))
    $evidenceDir = Join-Path $root "out\evidence\blastem"
    $logDir = Join-Path $root "out\logs"
    New-Item -ItemType Directory -Force -Path $evidenceDir, $logDir | Out-Null
    $romPath = Join-Path $root "out\rom.bin"
    $screenshotPath = Join-Path $evidenceDir "screenshot.png"
    [System.IO.File]::WriteAllBytes($romPath, [byte[]](0x53, 0x47, 0x44, 0x4B))
    Copy-Item -LiteralPath $ScreenshotSource -Destination $screenshotPath -Force
    $romHash = (Get-FileHash -LiteralPath $romPath -Algorithm SHA256).Hash.ToLowerInvariant()
    $session = [ordered]@{
        schema_version = "1.0.0"
        timestamp = (Get-Date).ToUniversalTime().ToString("o")
        emulator = "blastem"
        session_id = "semantic-gate-fixture-session"
        launch_status = "captured_closed"
        rom_path = $romPath
        rom_sha256 = $romHash
        evidence_stale = $false
        screenshot_path = $screenshotPath
        evidence_files = @($screenshotPath)
    }
    $session | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $logDir "emulator_session.json") -Encoding UTF8
    return [pscustomobject]@{ Root = $root; Screenshot = $screenshotPath; Logs = $logDir }
}

$bad = New-EvidenceFixture -ScreenshotSource $badFixture
$good = New-EvidenceFixture -ScreenshotSource $goodFixture

& $powerShellHost -NoProfile -File $auditScript -ProjectRoot $bad.Root -ScreenshotPath $bad.Screenshot
$badAuditExit = $LASTEXITCODE
Assert-True ($badAuditExit -ne 0) "Low-information capture must make semantic audit exit non-zero"
$badSemantic = Get-Content -LiteralPath (Join-Path $bad.Logs "screenshot_semantic_gate_report.json") -Raw | ConvertFrom-Json
Assert-True (-not [bool]$badSemantic.semantic_capture_valid) "Low-information fixture was incorrectly accepted"
Assert-True ($badSemantic.blocker_code -eq "blank_or_low_information_capture") "Unexpected semantic blocker: $($badSemantic.blocker_code)"
Assert-True ($badSemantic.claim_impacts.gameplay -eq "unproven") "Invalid screenshot must force gameplay unproven"
Assert-True ($badSemantic.claim_impacts.performance -eq "unproven") "Invalid screenshot must force performance unproven"

& $powerShellHost -NoProfile -File $auditScript -ProjectRoot $good.Root -ScreenshotPath $good.Screenshot
Assert-True ($LASTEXITCODE -eq 0) "Semantically rich control screenshot should pass"
$goodSemantic = Get-Content -LiteralPath (Join-Path $good.Logs "screenshot_semantic_gate_report.json") -Raw | ConvertFrom-Json
Assert-True ([bool]$goodSemantic.semantic_capture_valid) "Control screenshot was incorrectly rejected"
Assert-True ($goodSemantic.claim_impacts.gameplay -eq "not_proven_by_screenshot_alone") "Valid screenshot must not prove gameplay"

& $powerShellHost -NoProfile -File $finalizerScript -ProjectRoot $bad.Root
$badSealExit = $LASTEXITCODE
Assert-True ($badSealExit -ne 0) "Evidence finalizer must reject a low-information screenshot"
$badSeal = Get-Content -LiteralPath (Join-Path $bad.Logs "evidence_closeout_report.json") -Raw | ConvertFrom-Json
Assert-True ($badSeal.seal_status -eq "rejected") "Low-information evidence was incorrectly sealed"
Assert-True ($badSeal.blocker_code -eq "blank_or_low_information_capture") "Finalizer did not propagate semantic blocker"

& $powerShellHost -NoProfile -File $finalizerScript -ProjectRoot $good.Root
Assert-True ($LASTEXITCODE -eq 0) "Evidence finalizer should seal the valid control fixture"
$goodSeal = Get-Content -LiteralPath (Join-Path $good.Logs "evidence_closeout_report.json") -Raw | ConvertFrom-Json
Assert-True ($goodSeal.seal_status -eq "sealed") "Valid control evidence was not sealed"
Assert-True ([bool]$goodSeal.semantic_capture_valid) "Finalizer lost the positive semantic decision"

Write-Host "[PASS] screenshot semantic gate rejects synthetic low-information capture"
Write-Host "[PASS] valid dark/gameplay capture remains accepted without proving gameplay or performance"
Write-Host "[PASS] evidence finalizer propagates the semantic decision"
Remove-Item -LiteralPath $fixtureRoot, $bad.Root, $good.Root -Recurse -Force -ErrorAction SilentlyContinue
