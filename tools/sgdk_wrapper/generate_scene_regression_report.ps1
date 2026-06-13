[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$ProjectDir = ""
)

$ErrorActionPreference = "Stop"

function Resolve-ProjectRoot {
    param([string]$InputPath)

    if ([string]::IsNullOrWhiteSpace($InputPath)) {
        return (Get-Location).Path
    }

    return (Resolve-Path -LiteralPath $InputPath).Path
}

function Get-JsonOrNull {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }

    try {
        return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
    } catch {
        return $null
    }
}

function Get-SramSceneIdOrNull {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }

    $bytes = [System.IO.File]::ReadAllBytes($Path)
    if ($bytes.Length -lt 14) {
        return $null
    }

    $magic = [System.Text.Encoding]::ASCII.GetString($bytes, 0, 4)
    if ($magic -ne "VLAB") {
        return $null
    }

    return [int]$bytes[13]
}

$projectRoot = Resolve-ProjectRoot -InputPath $ProjectDir
$manifestPath = Join-Path $projectRoot ".mddev\project.json"
$manifest = Get-JsonOrNull $manifestPath
if (-not $manifest -or -not $manifest.scene_regression -or -not $manifest.scene_regression.scenes) {
    throw "scene_regression nao configurado em $manifestPath"
}

$logDir = Join-Path $projectRoot "out\logs"
$captureRoot = Join-Path $projectRoot "out\captures\scene_matrix"
$reportPath = Join-Path $logDir "scene_regression_report.json"
$mismatchLogPath = Join-Path $logDir "scene_regression_mismatch.log"
$sessionPath = Join-Path $logDir "emulator_session.json"
$session = Get-JsonOrNull $sessionPath
$romSha = if ($session) { [string]$session.rom_sha256 } else { $null }
$captureModes = @($manifest.scene_regression.capture_modes)
if ($captureModes.Count -eq 0) {
    $captureModes = @("overlay_off", "overlay_on")
}

New-Item -ItemType Directory -Force -Path $logDir | Out-Null

$sceneReports = @()
$mismatchLines = @()

foreach ($scene in @($manifest.scene_regression.scenes)) {
    $sceneKey = [string]$scene.scene_key
    $sceneId = [int]$scene.scene_id
    $sceneDir = Join-Path $captureRoot $sceneKey
    $modeReports = @()

    foreach ($mode in $captureModes) {
        $prefix = "{0}_{1}" -f $sceneKey, $mode
        $pngPath = Join-Path $sceneDir ($prefix + ".png")
        $sramPath = Join-Path $sceneDir ($prefix + ".sram")
        $dumpPath = Join-Path $sceneDir ($prefix + ".bin")
        $metricsPath = Join-Path $sceneDir ($prefix + ".runtime_metrics.json")
        $sessionJsonPath = Join-Path $sceneDir ($prefix + ".session.json")
        $capturedSceneId = Get-SramSceneIdOrNull -Path $sramPath

        $hasEvidence = (
            (Test-Path -LiteralPath $pngPath -PathType Leaf) -and
            (Test-Path -LiteralPath $sramPath -PathType Leaf) -and
            (Test-Path -LiteralPath $dumpPath -PathType Leaf)
        )
        $sceneMatch = ($null -ne $capturedSceneId) -and ($capturedSceneId -eq $sceneId)
        $status = if ($hasEvidence -and $sceneMatch) { "captured" } else { "failed" }

        if (-not $sceneMatch) {
            $mismatchLines += ("{0}`texpected={1}`tcaptured={2}`tmode={3}`tsram={4}" -f `
                (Get-Date -Format "o"),
                $sceneId,
                $(if ($null -ne $capturedSceneId) { $capturedSceneId } else { "null" }),
                $mode,
                $sramPath)
        }

        $modeReports += [ordered]@{
            mode = $mode
            status = $status
            expected_scene_id = $sceneId
            captured_scene_id = $capturedSceneId
            screenshot = if (Test-Path -LiteralPath $pngPath -PathType Leaf) { $pngPath } else { $null }
            save_sram = if (Test-Path -LiteralPath $sramPath -PathType Leaf) { $sramPath } else { $null }
            visual_vdp_dump = if (Test-Path -LiteralPath $dumpPath -PathType Leaf) { $dumpPath } else { $null }
            runtime_metrics = if (Test-Path -LiteralPath $metricsPath -PathType Leaf) { $metricsPath } else { $null }
            session_json = if (Test-Path -LiteralPath $sessionJsonPath -PathType Leaf) { $sessionJsonPath } else { $null }
        }
    }

    $sceneStatus = if (($modeReports | Where-Object { $_.status -ne "captured" }).Count -eq 0) { "captured" } else { "failed" }
    $sceneReports += [ordered]@{
        scene_key = $sceneKey
        scene_id = $sceneId
        overlay_mode = [string]$scene.overlay_mode
        required_planes = @($scene.required_planes)
        required_features = @($scene.required_features)
        status = $sceneStatus
        captures = $modeReports
    }
}

$failedSceneKeys = @($sceneReports | Where-Object { $_.status -ne "captured" } | ForEach-Object { $_.scene_key })
$report = [ordered]@{
    schema_version = 1
    project = $manifest.display_name
    generated_at = (Get-Date -Format "o")
    rom_sha256 = $romSha
    scenes = $sceneReports
    summary = [ordered]@{
        scene_count = $sceneReports.Count
        failed_scene_keys = @($failedSceneKeys)
        all_captured = ($failedSceneKeys.Count -eq 0)
        mismatch_count = $mismatchLines.Count
        mismatch_log_path = $mismatchLogPath
    }
}

$report | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $reportPath
if ($mismatchLines.Count -gt 0) {
    $mismatchLines | Set-Content -LiteralPath $mismatchLogPath
} elseif (Test-Path -LiteralPath $mismatchLogPath) {
    Remove-Item -LiteralPath $mismatchLogPath -Force
}

Get-Content -LiteralPath $reportPath
