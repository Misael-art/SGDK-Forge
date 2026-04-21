[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$ProjectDir = "",

    [Parameter(Mandatory = $false)]
    [string]$SceneKey = ""
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

function Get-SceneIdFromSram {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }

    $bytes = [System.IO.File]::ReadAllBytes($Path)
    if ($bytes.Length -lt 14) {
        return $null
    }

    return [int]$bytes[13]
}

function Copy-ArtifactOrNull {
    param(
        [string]$SourcePath,
        [string]$DestinationPath
    )

    if (-not (Test-Path -LiteralPath $SourcePath -PathType Leaf)) {
        return $null
    }

    Copy-Item -LiteralPath $SourcePath -Destination $DestinationPath -Force
    return $DestinationPath
}

function Normalize-Sequence {
    param([object[]]$Steps)

    $normalized = @()
    foreach ($step in @($Steps)) {
        $text = [string]$step
        if (-not [string]::IsNullOrWhiteSpace($text)) {
            $normalized += $text
        }
    }
    return ,$normalized
}

$projectRoot = Resolve-ProjectRoot -InputPath $ProjectDir
$manifestPath = Join-Path $projectRoot ".mddev\project.json"
$manifest = Get-JsonOrNull $manifestPath
if (-not $manifest -or -not $manifest.scene_regression -or -not $manifest.scene_regression.scenes) {
    throw "scene_regression nao configurado em $manifestPath"
}

$scenes = @($manifest.scene_regression.scenes)
if ($SceneKey) {
    $scenes = @($scenes | Where-Object { ([string]$_.scene_key) -eq $SceneKey })
    if ($scenes.Count -eq 0) {
        throw "SceneKey '$SceneKey' nao encontrado em scene_regression.scenes."
    }
}

$captureScript = Join-Path $PSScriptRoot "run_visual_capture.ps1"
$globalCaptureDir = Join-Path $projectRoot "out\captures"
$globalLogDir = Join-Path $projectRoot "out\logs"
$capturesRoot = Join-Path $globalCaptureDir "scene_matrix"
$reportPath = Join-Path $globalLogDir "scene_regression_report.json"
$sessionPath = Join-Path $globalLogDir "emulator_session.json"
$runtimeMetricsPath = Join-Path $globalLogDir "runtime_metrics.json"
$latestRomSha = ""
$sceneReports = @()
$previousSceneRegressionFlag = $env:SGDK_SCENE_REGRESSION_BUILDING

New-Item -ItemType Directory -Force -Path $capturesRoot | Out-Null

try {
    $env:SGDK_SCENE_REGRESSION_BUILDING = "1"

    foreach ($scene in $scenes) {
        $sceneKeyText = [string]$scene.scene_key
        $sceneId = [int]$scene.scene_id
        $baseSequence = Normalize-Sequence -Steps @($scene.navigation_sequence)
        $overlayKey = [string]$scene.overlay_toggle
        if ([string]::IsNullOrWhiteSpace($overlayKey)) {
            $overlayKey = "c"
        }

        $sceneDir = Join-Path $capturesRoot $sceneKeyText
        New-Item -ItemType Directory -Force -Path $sceneDir | Out-Null

        $modes = @(
            @{ name = "overlay_off"; sequence = $baseSequence }
            @{ name = "overlay_on"; sequence = (Normalize-Sequence -Steps ($baseSequence + @($overlayKey, "wait:800"))) }
        )

        $modeReports = @()
        foreach ($mode in $modes) {
            & $captureScript -ProjectDir $projectRoot -NavigationSequence $mode.sequence | Out-Null
            $session = Get-JsonOrNull $sessionPath
            if (-not $session) {
                throw "Falha ao carregar emulator_session.json apos captura de $sceneKeyText ($($mode.name))."
            }

            $latestRomSha = [string]$session.rom_sha256
            $prefix = "{0}_{1}" -f $sceneKeyText, $mode.name
            $pngDest = Copy-ArtifactOrNull -SourcePath (Join-Path $globalCaptureDir "benchmark_visual.png") -DestinationPath (Join-Path $sceneDir ($prefix + ".png"))
            $sramDest = Copy-ArtifactOrNull -SourcePath (Join-Path $globalCaptureDir "save.sram") -DestinationPath (Join-Path $sceneDir ($prefix + ".sram"))
            $dumpDest = Copy-ArtifactOrNull -SourcePath (Join-Path $globalCaptureDir "visual_vdp_dump.bin") -DestinationPath (Join-Path $sceneDir ($prefix + ".bin"))
            $metricsDest = Copy-ArtifactOrNull -SourcePath $runtimeMetricsPath -DestinationPath (Join-Path $sceneDir ($prefix + ".runtime_metrics.json"))
            $sessionDest = Copy-ArtifactOrNull -SourcePath $sessionPath -DestinationPath (Join-Path $sceneDir ($prefix + ".session.json"))

            $capturedSceneId = Get-SceneIdFromSram -Path $sramDest
            $modeOk = ($null -ne $capturedSceneId) -and ($capturedSceneId -eq $sceneId) -and $pngDest -and $sramDest -and $dumpDest

            $modeReports += [ordered]@{
                mode = $mode.name
                status = if ($modeOk) { "captured" } else { "failed" }
                expected_scene_id = $sceneId
                captured_scene_id = $capturedSceneId
                screenshot = $pngDest
                save_sram = $sramDest
                visual_vdp_dump = $dumpDest
                runtime_metrics = $metricsDest
                session_json = $sessionDest
            }
        }

        $sceneStatus = if (($modeReports | Where-Object { $_.status -ne "captured" }).Count -eq 0) { "captured" } else { "failed" }
        $sceneReports += [ordered]@{
            scene_key = $sceneKeyText
            scene_id = $sceneId
            overlay_mode = [string]$scene.overlay_mode
            required_planes = @($scene.required_planes)
            required_features = @($scene.required_features)
            status = $sceneStatus
            captures = $modeReports
        }
    }
}
finally {
    if ($null -eq $previousSceneRegressionFlag) {
        Remove-Item Env:SGDK_SCENE_REGRESSION_BUILDING -ErrorAction SilentlyContinue
    } else {
        $env:SGDK_SCENE_REGRESSION_BUILDING = $previousSceneRegressionFlag
    }
}

$failedScenes = @($sceneReports | Where-Object { $_.status -ne "captured" } | ForEach-Object { $_.scene_key })
$report = [ordered]@{
    schema_version = 1
    project = $manifest.display_name
    generated_at = (Get-Date -Format "o")
    rom_sha256 = $latestRomSha
    scenes = $sceneReports
    summary = [ordered]@{
        scene_count = $sceneReports.Count
        failed_scene_keys = @($failedScenes)
        all_captured = ($failedScenes.Count -eq 0)
    }
}

$report | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $reportPath
Get-Content -LiteralPath $reportPath
