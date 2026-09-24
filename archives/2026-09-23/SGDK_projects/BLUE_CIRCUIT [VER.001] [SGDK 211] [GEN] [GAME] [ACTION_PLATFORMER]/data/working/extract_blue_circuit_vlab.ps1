param(
    [string]$ProjectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
)

$ErrorActionPreference = "Stop"

$sramPath = Join-Path $ProjectRoot "out\evidence\blastem\save.sram"
$dumpPath = Join-Path $ProjectRoot "out\evidence\blastem\visual_vdp_dump.bin"
$reportPath = Join-Path $ProjectRoot "out\logs\blue_circuit_vlab_extract_report.json"

if (-not (Test-Path -LiteralPath $sramPath -PathType Leaf)) {
    throw "save.sram nao encontrado: $sramPath"
}

$bytes = [System.IO.File]::ReadAllBytes($sramPath)

function Set-JsonProperty {
    param(
        [Parameter(Mandatory = $true)]$Object,
        [Parameter(Mandatory = $true)][string]$Name,
        $Value
    )

    if ($Object.PSObject.Properties.Name -contains $Name) {
        $Object.$Name = $Value
    } else {
        $Object | Add-Member -NotePropertyName $Name -NotePropertyValue $Value
    }
}

$vlabOffset = -1
for ($i = 0; $i -le ($bytes.Length - 8); $i++) {
    if ($bytes[$i] -eq 0x56 -and $bytes[$i + 1] -eq 0x4C -and $bytes[$i + 2] -eq 0x41 -and $bytes[$i + 3] -eq 0x42) {
        $vlabOffset = $i
        break
    }
}

if ($vlabOffset -lt 0) {
    throw "Bloco VLAB nao encontrado em save.sram."
}

$totalBytes = ([int]$bytes[$vlabOffset + 6] -shl 8) -bor [int]$bytes[$vlabOffset + 7]
if ($totalBytes -le 0 -or ($vlabOffset + $totalBytes) -gt $bytes.Length) {
    throw "Tamanho VLAB invalido: $totalBytes"
}

$dumpBytes = New-Object byte[] $totalBytes
[System.Array]::Copy($bytes, $vlabOffset, $dumpBytes, 0, $totalBytes)
[System.IO.File]::WriteAllBytes($dumpPath, $dumpBytes)

$sha = [System.Security.Cryptography.SHA256]::Create()
try {
    $dumpHash = ([System.BitConverter]::ToString($sha.ComputeHash($dumpBytes))).Replace("-", "").ToLowerInvariant()
    $sramHash = ([System.BitConverter]::ToString($sha.ComputeHash($bytes))).Replace("-", "").ToLowerInvariant()
}
finally {
    $sha.Dispose()
}

$report = [ordered]@{
    schema_version = "1.0.0"
    status = "ok"
    generated_at = (Get-Date).ToUniversalTime().ToString("o")
    tool_name = "extract_blue_circuit_vlab.ps1"
    sram_path = "out/evidence/blastem/save.sram"
    visual_vdp_dump_path = "out/evidence/blastem/visual_vdp_dump.bin"
    vlab_offset = $vlabOffset
    total_bytes = $totalBytes
    scene_id = [int]$bytes[$vlabOffset + 13]
    active_sprites = [int]$bytes[$vlabOffset + 14]
    max_scanline_sprites = [int]$bytes[$vlabOffset + 15]
    sram_sha256 = $sramHash
    visual_vdp_dump_sha256 = $dumpHash
}

foreach ($manifestName in @("emulator_session.json", "blastem_evidence.json")) {
    $manifestPath = Join-Path $ProjectRoot ("out\logs\" + $manifestName)
    if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
        continue
    }

    $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    if ($manifestName -eq "emulator_session.json") {
        Set-JsonProperty -Object $manifest -Name "vdp_dump_path" -Value $dumpPath
        Set-JsonProperty -Object $manifest -Name "visual_vdp_dump_path" -Value $dumpPath
        Set-JsonProperty -Object $manifest -Name "vdp_dump_status" -Value "captured"
        Set-JsonProperty -Object $manifest -Name "visual_vdp_dump_required" -Value $true
        $files = @()
        if ($manifest.evidence_files) { $files += @($manifest.evidence_files) }
        if ($dumpPath -notin $files) { $files += $dumpPath }
        Set-JsonProperty -Object $manifest -Name "evidence_files" -Value @($files)
        $captures = @()
        if ($manifest.captures) { $captures += @($manifest.captures) }
        if ($dumpPath -notin $captures) { $captures += $dumpPath }
        Set-JsonProperty -Object $manifest -Name "captures" -Value @($captures)
        Set-JsonProperty -Object $manifest -Name "qa_basis" -Value "BlastEm window screenshot plus persisted MDRT save.sram and VLAB visual evidence block"
    } else {
        Set-JsonProperty -Object $manifest -Name "vdp_dump_present" -Value $true
        Set-JsonProperty -Object $manifest -Name "vdp_dump_path" -Value $dumpPath
        Set-JsonProperty -Object $manifest -Name "visual_vdp_dump_path" -Value $dumpPath
        if ($manifest.PSObject.Properties.Name -contains "captured_artifacts") {
            $captured = @($manifest.captured_artifacts)
            if ("vdp_dump" -notin $captured) { $captured += "vdp_dump" }
            Set-JsonProperty -Object $manifest -Name "captured_artifacts" -Value @($captured)
        }
    }

    [System.IO.File]::WriteAllText($manifestPath, ($manifest | ConvertTo-Json -Depth 12), [System.Text.Encoding]::UTF8)
}

$json = $report | ConvertTo-Json -Depth 8
[System.IO.File]::WriteAllText($reportPath, $json, [System.Text.Encoding]::UTF8)
$json
