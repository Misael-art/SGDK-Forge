<#
.SYNOPSIS
    Writes the canonical ROM mastering report for an SGDK/Mega Drive project.
.DESCRIPTION
    Observes the built ROM, header, SGDK checksum, validation, closeout,
    budget and BlastEm evidence, then writes out/logs/rom_mastering_report.json.
    This script does not patch the ROM.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectRoot,

    [Parameter(Mandatory = $false)]
    [string]$RomPath = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot -ErrorAction Stop).Path
if ([string]::IsNullOrWhiteSpace($RomPath)) {
    $RomPath = Join-Path $ProjectRoot "out\rom.bin"
}
$RomPath = (Resolve-Path -LiteralPath $RomPath -ErrorAction Stop).Path

$LogDir = Join-Path $ProjectRoot "out\logs"
if (-not (Test-Path -LiteralPath $LogDir -PathType Container)) {
    New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
}
$ReportPath = Join-Path $LogDir "rom_mastering_report.json"

function Get-FileSha256Hex {
    param([Parameter(Mandatory = $true)][string]$Path)

    $sha = [System.Security.Cryptography.SHA256]::Create()
    $stream = $null
    try {
        $stream = [System.IO.File]::OpenRead($Path)
        return ([System.BitConverter]::ToString($sha.ComputeHash($stream))).Replace("-", "").ToLowerInvariant()
    } finally {
        if ($stream) { $stream.Dispose() }
        if ($sha) { $sha.Dispose() }
    }
}

function Read-AsciiField {
    param(
        [Parameter(Mandatory = $true)][byte[]]$Bytes,
        [Parameter(Mandatory = $true)][int]$Offset,
        [Parameter(Mandatory = $true)][int]$Length
    )

    if ($Bytes.Length -lt ($Offset + $Length)) {
        return ""
    }
    return ([System.Text.Encoding]::ASCII.GetString($Bytes, $Offset, $Length)).Trim()
}

function Read-U16BE {
    param(
        [Parameter(Mandatory = $true)][byte[]]$Bytes,
        [Parameter(Mandatory = $true)][int]$Offset
    )

    if ($Bytes.Length -lt ($Offset + 2)) {
        return $null
    }
    return (([int]$Bytes[$Offset] -shl 8) -bor [int]$Bytes[$Offset + 1])
}

function Read-U32BE {
    param(
        [Parameter(Mandatory = $true)][byte[]]$Bytes,
        [Parameter(Mandatory = $true)][int]$Offset
    )

    if ($Bytes.Length -lt ($Offset + 4)) {
        return $null
    }
    return ([uint32](
        ([uint32]$Bytes[$Offset] -shl 24) -bor
        ([uint32]$Bytes[$Offset + 1] -shl 16) -bor
        ([uint32]$Bytes[$Offset + 2] -shl 8) -bor
        [uint32]$Bytes[$Offset + 3]
    ))
}

function Get-SgdkHeaderChecksum {
    param([Parameter(Mandatory = $true)][byte[]]$SourceBytes)

    $bytes = [byte[]]$SourceBytes.Clone()
    if ($bytes.Length -gt 0x18F) {
        $bytes[0x18E] = 0
        $bytes[0x18F] = 0
    }

    [uint32]$checksum = 0
    for ($i = 0; $i -lt $bytes.Length; $i += 4) {
        [uint32]$word = 0
        for ($j = 0; $j -lt 4; $j++) {
            $index = $i + $j
            [uint32]$value = 0
            if ($index -lt $bytes.Length) {
                $value = [uint32]$bytes[$index]
            }
            $word = $word -bor ($value -shl (24 - ($j * 8)))
        }
        $checksum = $checksum -bxor $word
    }

    return [int](($checksum -bxor ($checksum -shr 16)) -band 0xFFFF)
}

function Get-JsonOrNull {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }
    try {
        return Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json
    } catch {
        return $null
    }
}

function Get-BlockingStatuses {
    param($Report)

    if ($null -eq $Report -or -not ($Report.PSObject.Properties.Name -contains "blocking_statuses")) {
        return @()
    }
    return @($Report.blocking_statuses | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) })
}

$romItem = Get-Item -LiteralPath $RomPath
$romBytes = [System.IO.File]::ReadAllBytes($RomPath)
$romSha256 = Get-FileSha256Hex -Path $RomPath
$headerChecksum = Read-U16BE -Bytes $romBytes -Offset 0x18E
$sgdkChecksum = Get-SgdkHeaderChecksum -SourceBytes $romBytes

$validationPath = Join-Path $LogDir "validation_report.json"
$emulatorSessionPath = Join-Path $LogDir "emulator_session.json"
$closeoutPath = Join-Path $LogDir "scene_closeout_gate_report.json"
$budgetPath = Join-Path $LogDir "scene_budget_report.json"

$validation = Get-JsonOrNull -Path $validationPath
$emulatorSession = Get-JsonOrNull -Path $emulatorSessionPath
$closeout = Get-JsonOrNull -Path $closeoutPath
$budget = Get-JsonOrNull -Path $budgetPath

$validationBlockers = @(Get-BlockingStatuses -Report $validation)
$validationClean = ($validation -and $validationBlockers.Count -eq 0)
$emulatorHashMatches = ($emulatorSession -and ([string]$emulatorSession.rom_sha256).ToLowerInvariant() -eq $romSha256)
$emulatorOk = ($emulatorSession -and [string]$emulatorSession.emulator -eq "blastem" -and [string]$emulatorSession.boot_emulador -eq "ok" -and [bool]$emulatorHashMatches)
$closeoutOk = ($closeout -and [string]$closeout.status -eq "ok")
$budgetOk = ($budget -and ([string]$budget.status).ToLowerInvariant() -in @("ok", "pass", "passed"))
$checksumOk = ($null -ne $headerChecksum -and $headerChecksum -eq $sgdkChecksum)
$sizeAligned = (($romItem.Length % 512) -eq 0)
$region = Read-AsciiField -Bytes $romBytes -Offset 0x1F0 -Length 16
$regionOk = ($region -match "J" -and $region -match "U" -and $region -match "E")
$romStart = Read-U32BE -Bytes $romBytes -Offset 0x1A0
$romEnd = Read-U32BE -Bytes $romBytes -Offset 0x1A4
$romRangeOk = ($null -ne $romStart -and $null -ne $romEnd -and $romStart -eq 0 -and $romEnd -ge ($romItem.Length - 1))

$requiredChecks = @(
    $validationClean,
    $emulatorOk,
    $closeoutOk,
    $budgetOk,
    $checksumOk,
    $sizeAligned,
    $regionOk,
    $romRangeOk
)
$masteringOk = -not ($requiredChecks -contains $false)

$report = [ordered]@{
    schema_version = "1.0.0"
    generated_at = (Get-Date).ToUniversalTime().ToString("o")
    tool_name = "write_rom_mastering_report"
    tool_version = "0.1.0"
    project_root = $ProjectRoot
    rom_path = $RomPath
    rom_sha256 = $romSha256
    sha256 = $romSha256
    size_bytes = [int64]$romItem.Length
    size_aligned_512 = [bool]$sizeAligned
    decision = if ($masteringOk) { "mastering_ok" } else { "mastering_needs_fix" }
    header = [ordered]@{
        console = Read-AsciiField -Bytes $romBytes -Offset 0x100 -Length 16
        domestic_name = Read-AsciiField -Bytes $romBytes -Offset 0x120 -Length 48
        overseas_name = Read-AsciiField -Bytes $romBytes -Offset 0x150 -Length 48
        product_id = Read-AsciiField -Bytes $romBytes -Offset 0x180 -Length 14
        checksum = ("0x{0:X4}" -f $headerChecksum)
        sgdk_computed_checksum = ("0x{0:X4}" -f $sgdkChecksum)
        checksum_matches_sgdk = [bool]$checksumOk
        rom_start = if ($null -ne $romStart) { ("0x{0:X8}" -f $romStart) } else { $null }
        rom_end = if ($null -ne $romEnd) { ("0x{0:X8}" -f $romEnd) } else { $null }
        rom_range_covers_file = [bool]$romRangeOk
        sram_start = $null
        sram_end = $null
        region = $region
        region_contract = "JUE"
        region_contract_ok = [bool]$regionOk
    }
    evidence = [ordered]@{
        validation_report = $validationPath
        emulator_session = $emulatorSessionPath
        scene_closeout_gate_report = $closeoutPath
        scene_budget_report = $budgetPath
        screenshot = if ($emulatorSession -and $emulatorSession.PSObject.Properties.Name -contains "screenshot_path") { $emulatorSession.screenshot_path } else { $null }
        save_sram = if ($emulatorSession -and $emulatorSession.PSObject.Properties.Name -contains "sram_path") { $emulatorSession.sram_path } else { $null }
        visual_vdp_dump = if ($emulatorSession -and $emulatorSession.PSObject.Properties.Name -contains "vdp_dump_path") { $emulatorSession.vdp_dump_path } else { $null }
    }
    checks = [ordered]@{
        validation_clean = [bool]$validationClean
        validation_blocking_statuses = @($validationBlockers)
        blastem_hash_matches_rom = [bool]$emulatorHashMatches
        blastem_boot_ok = [bool]$emulatorOk
        closeout_ok = [bool]$closeoutOk
        budget_ok = [bool]$budgetOk
        checksum_ok = [bool]$checksumOk
        size_aligned_512 = [bool]$sizeAligned
        region_ok = [bool]$regionOk
        rom_range_ok = [bool]$romRangeOk
    }
    sram_policy = "runtime_probe_evidence_only"
    qa_link = [ordered]@{
        emulator = "BlastEm"
        rom_hash_source = "out/rom.bin"
        emulator_hash_source = "out/logs/emulator_session.json"
    }
}

$report | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $ReportPath -Encoding UTF8
Write-Host ("[MASTERING] decision={0} sha256={1} report={2}" -f $report.decision, $romSha256, $ReportPath)

if (-not $masteringOk) {
    exit 1
}
exit 0
