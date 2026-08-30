$ErrorActionPreference = 'Stop'

function Assert-True {
    param(
        [bool]$Condition,
        [string]$Message
    )
    if (-not $Condition) {
        throw "ASSERT FAILED: $Message"
    }
}

function Assert-Equal {
    param(
        $Expected,
        $Actual,
        [string]$Message
    )
    if ($Expected -ne $Actual) {
        throw "ASSERT FAILED: $Message. Expected '$Expected', got '$Actual'"
    }
}

function Get-Json {
    param([string]$Path)
    return Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
}

function Remove-TestProjectSafely {
    param(
        [string]$Path,
        [string]$ExpectedLeaf
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        return
    }

    $Resolved = (Resolve-Path -LiteralPath $Path).Path
    $ResolvedProjects = (Resolve-Path -LiteralPath 'SGDK_projects').Path
    $Leaf = Split-Path -Leaf $Resolved
    if ((Split-Path -Parent $Resolved) -ne $ResolvedProjects) {
        throw "refusing cleanup outside SGDK_projects: $Resolved"
    }
    if ($Leaf -ne $ExpectedLeaf) {
        throw "refusing cleanup unexpected leaf: $Leaf"
    }

    for ($Attempt = 1; $Attempt -le 8; $Attempt++) {
        try {
            Remove-Item -LiteralPath $Resolved -Recurse -Force -ErrorAction Stop
            return
        }
        catch {
            if ($Attempt -eq 8) {
                throw
            }
            Start-Sleep -Seconds 2
        }
    }
}

function Stop-TestProjectProcesses {
    param([string]$ProjectName)

    $Pattern = [regex]::Escape($ProjectName)
    $CurrentPid = $PID
    $Processes = @(Get-CimInstance Win32_Process | Where-Object {
        $_.ProcessId -ne $CurrentPid -and
        $_.CommandLine -and
        $_.CommandLine -match $Pattern
    })

    foreach ($Process in $Processes) {
        Stop-Process -Id $Process.ProcessId -Force -ErrorAction SilentlyContinue
    }
}

function Assert-JsonMatchesSchema {
    param(
        [string]$InstancePath,
        [string]$SchemaPath
    )

    Assert-True (Test-Path -LiteralPath $InstancePath) "missing JSON instance: $InstancePath"
    Assert-True (Test-Path -LiteralPath $SchemaPath) "missing JSON schema: $SchemaPath"

    $ValidatorPath = Join-Path $OutDir 'validate_json_schema.py'
    $ValidatorScript = @'
import json
import sys
from pathlib import Path
from jsonschema import Draft7Validator

instance_path = Path(sys.argv[1])
schema_path = Path(sys.argv[2])

instance = json.loads(instance_path.read_text(encoding="utf-8-sig"))
schema = json.loads(schema_path.read_text(encoding="utf-8-sig"))
validator = Draft7Validator(schema)
errors = sorted(validator.iter_errors(instance), key=lambda error: list(error.path))
if errors:
    for error in errors:
        location = "$" + "".join(f"[{repr(part)}]" for part in error.path)
        print(f"{location}: {error.message}")
    sys.exit(1)
'@
    $ValidatorScript | Set-Content -Encoding UTF8 -Path $ValidatorPath

    $Output = & uv run --with jsonschema python $ValidatorPath $InstancePath $SchemaPath 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "schema validation failed for ${InstancePath} against ${SchemaPath}: $Output"
    }
}

function Assert-NoRuntimeEvidence {
    param([string]$Root)

    $Forbidden = @(Get-ChildItem -LiteralPath $Root -Recurse -File -ErrorAction SilentlyContinue | Where-Object {
        $_.FullName -match 'VIBE_PLAYABLE_LOOP_FIXTURE|runtime_comparison_panel|asset_approval_panel|visual_vdp_dump|save\.sram|rom\.bin|screenshot|blastem'
    })
    Assert-True ($Forbidden.Count -eq 0) "template contains E2E/runtime evidence asset: $($Forbidden.FullName -join ', ')"
}

function Assert-LegitimateSourceArtPresent {
    param(
        [string]$Root,
        [string[]]$RelativePaths
    )

    foreach ($RelativePath in $RelativePaths) {
        Assert-True ($RelativePath -match '^data/source_art/') "legitimate source art must live under data/source_art: $RelativePath"
        $FullPath = Join-Path $Root ($RelativePath -replace '/', [IO.Path]::DirectorySeparatorChar)
        Assert-True (Test-Path -LiteralPath $FullPath) "missing legitimate template source art: $RelativePath"
        $Item = Get-Item -LiteralPath $FullPath
        Assert-True ($Item.Length -gt 0) "legitimate template source art is empty: $RelativePath"
    }
}

function Assert-NewProjectBirth {
    param(
        [string]$ProjectRoot,
        [string]$ProjectName
    )

    Assert-True (Test-Path -LiteralPath $ProjectRoot) "new project was not created: $ProjectName"
    Assert-True (-not (Test-Path -LiteralPath (Join-Path $ProjectRoot 'out'))) 'new project preserved out directory'

    $PremiumPath = Join-Path $ProjectRoot 'data\source_art\premium_source_manifest.json'
    $ApprovalPath = Join-Path $ProjectRoot 'doc\human_approval_record.md'
    $RuntimeSeedPath = Join-Path $ProjectRoot 'doc\contracts\runtime_admission_report.json'

    Assert-True (Test-Path -LiteralPath $PremiumPath) 'new project missing premium source seed'
    Assert-True (Test-Path -LiteralPath $ApprovalPath) 'new project missing human approval record'
    Assert-True (Test-Path -LiteralPath $RuntimeSeedPath) 'new project missing runtime admission seed'
    Assert-LegitimateSourceArtPresent -Root $ProjectRoot -RelativePaths $LegitimateTemplateSourceArt

    $Premium = Get-Json -Path $PremiumPath
    $RuntimeSeed = Get-Json -Path $RuntimeSeedPath
    $ApprovalText = Get-Content -Raw -LiteralPath $ApprovalPath

    Assert-True ($Premium.production_source_ready -eq $false) 'new project premium source is prevalidated'
    Assert-Equal 0 @($Premium.assets).Count 'new project contains premium assets'
    Assert-True (-not ($ApprovalText -match 'decision:\s*approved')) 'new project has pre-signed approval'
    Assert-True (-not ($ApprovalText -match 'approved_by\s*:')) 'new project has approved_by'
    Assert-True (-not $RuntimeSeed.runtime_admitted) 'new project runtime seed admits production runtime'
}

function Invoke-ProcessWithTimeout {
    param(
        [string]$FilePath,
        [string]$ArgumentList,
        [string]$OutputPrefix,
        [int]$TimeoutSeconds = 240
    )

    $StdoutPath = Join-Path $OutDir "$OutputPrefix.stdout.txt"
    $StderrPath = Join-Path $OutDir "$OutputPrefix.stderr.txt"
    Remove-Item -LiteralPath $StdoutPath, $StderrPath -Force -ErrorAction SilentlyContinue

    $Process = Start-Process `
        -FilePath $FilePath `
        -ArgumentList $ArgumentList `
        -NoNewWindow `
        -PassThru `
        -RedirectStandardOutput $StdoutPath `
        -RedirectStandardError $StderrPath

    if (-not $Process.WaitForExit($TimeoutSeconds * 1000)) {
        Stop-Process -Id $Process.Id -Force -ErrorAction SilentlyContinue
        throw "process timeout after ${TimeoutSeconds}s: $FilePath $ArgumentList"
    }

    $Stdout = ''
    $Stderr = ''
    if (Test-Path -LiteralPath $StdoutPath) {
        $Stdout = (Get-Content -Raw -LiteralPath $StdoutPath)
    }
    if (Test-Path -LiteralPath $StderrPath) {
        $Stderr = (Get-Content -Raw -LiteralPath $StderrPath)
    }

    return [pscustomobject]@{
        ExitCode = $Process.ExitCode
        Output = "$Stdout`n$Stderr"
    }
}

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
Set-Location $RepoRoot

$OutDir = Join-Path $RepoRoot 'out\ci\vibe_template_birth'
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$RequiredSchemas = @(
    'tools/sgdk_wrapper/schemas/vibe_playable_route_report.schema.json',
    'tools/sgdk_wrapper/schemas/premium_source_manifest.schema.json',
    'tools/sgdk_wrapper/schemas/runtime_admission_report.schema.json',
    'tools/sgdk_wrapper/schemas/art_gameplay_direction_gate.schema.json',
    'tools/sgdk_wrapper/schemas/visual_delivery_gate_report.schema.json'
)
$MissingSchemas = @($RequiredSchemas | Where-Object { -not (Test-Path -LiteralPath $_) })
if ($MissingSchemas.Count -ne 0) {
    throw "blocked_missing_vibe_playable_schema: $($MissingSchemas -join ', ')"
}

Assert-True (-not (Test-Path -LiteralPath 'tools/sgdk_wrapper/schemas/vibe_playable_birth_contract.schema.json')) 'parallel template birth schema must not exist'
Assert-True (-not (Test-Path -LiteralPath 'tools/sgdk_wrapper/schemas/template_birth.schema.json')) 'parallel template schema must not exist'

$TemplateRoot = Join-Path $RepoRoot 'tools\sgdk_wrapper\modelo'
$RouteSeedPath = Join-Path $TemplateRoot 'doc\contracts\vibe_playable_route_report.json'
$ArtSeedPath = Join-Path $TemplateRoot 'doc\contracts\art_gameplay_direction_gate.json'
$VisualSeedPath = Join-Path $TemplateRoot 'doc\contracts\visual_delivery_gate_report.json'
$RuntimeSeedPath = Join-Path $TemplateRoot 'doc\contracts\runtime_admission_report.json'
$PremiumPath = Join-Path $TemplateRoot 'data\source_art\premium_source_manifest.json'
$ApprovalPath = Join-Path $TemplateRoot 'doc\human_approval_record.md'
$LegitimateTemplateSourceArt = @(
    'data/source_art/branding_intro/production/author_panel_source.png',
    'data/source_art/branding_intro/production/engine_mark_source.png',
    'data/source_art/branding_intro/production/project_crest_source.png'
)

Assert-True (Test-Path -LiteralPath $RouteSeedPath) 'missing route seed'
Assert-True (Test-Path -LiteralPath $ArtSeedPath) 'missing art gameplay seed'
Assert-True (Test-Path -LiteralPath $VisualSeedPath) 'missing visual delivery seed'
Assert-True (Test-Path -LiteralPath $RuntimeSeedPath) 'missing runtime admission seed'
Assert-True (Test-Path -LiteralPath $PremiumPath) 'missing premium_source_manifest'
Assert-True (Test-Path -LiteralPath $ApprovalPath) 'missing human approval record'
Assert-LegitimateSourceArtPresent -Root $TemplateRoot -RelativePaths $LegitimateTemplateSourceArt

Assert-JsonMatchesSchema $RouteSeedPath 'tools/sgdk_wrapper/schemas/vibe_playable_route_report.schema.json'
Assert-JsonMatchesSchema $PremiumPath 'tools/sgdk_wrapper/schemas/premium_source_manifest.schema.json'
Assert-JsonMatchesSchema $RuntimeSeedPath 'tools/sgdk_wrapper/schemas/runtime_admission_report.schema.json'
Assert-JsonMatchesSchema $ArtSeedPath 'tools/sgdk_wrapper/schemas/art_gameplay_direction_gate.schema.json'
Assert-JsonMatchesSchema $VisualSeedPath 'tools/sgdk_wrapper/schemas/visual_delivery_gate_report.schema.json'

Assert-True (-not (Test-Path -LiteralPath (Join-Path $TemplateRoot 'out'))) 'template contains out directory'
Assert-NoRuntimeEvidence -Root $TemplateRoot

$RouteSeed = Get-Json -Path $RouteSeedPath
$Premium = Get-Json -Path $PremiumPath
$RuntimeSeed = Get-Json -Path $RuntimeSeedPath
$ArtSeed = Get-Json -Path $ArtSeedPath
$VisualSeed = Get-Json -Path $VisualSeedPath
$ApprovalText = Get-Content -Raw -LiteralPath $ApprovalPath

Assert-True ($RouteSeed.template_prevalidated -eq $false) 'route seed claims prevalidation'
Assert-True (-not $RouteSeed.runtime_open_allowed) 'route seed permits runtime open'
Assert-True (-not $RouteSeed.runtime_admission.runtime_admitted) 'route seed admits production runtime'
Assert-True ($Premium.production_source_ready -eq $false) 'template prevalidated premium source'
Assert-Equal 0 @($Premium.assets).Count 'template contains premium assets'
Assert-True (-not $RuntimeSeed.runtime_admitted) 'runtime seed admits production runtime'
Assert-True (-not $RuntimeSeed.technical_runtime_admitted) 'runtime seed admits technical runtime'
Assert-True (-not $RuntimeSeed.runtime_lab_admitted) 'runtime seed admits lab runtime'
Assert-True (-not $RuntimeSeed.visual_status_promotion_allowed) 'runtime seed promotes visual status'
Assert-Equal 'documented_visual_route_only' $RuntimeSeed.claim_ceiling 'runtime seed has unsafe claim ceiling'
Assert-True ($VisualSeed.ready_for_aaa -eq $false) 'visual seed claims ready_for_aaa'
Assert-True ($ArtSeed.decision.production_allowed -eq $false) 'art seed permits production'
Assert-True (-not ($ApprovalText -match 'decision:\s*approved')) 'template has pre-signed approval'
Assert-True (-not ($ApprovalText -match 'approved_by\s*:')) 'template has approved_by'
Assert-True (-not ($ApprovalText -match 'rom_sha256|screenshot|save\.sram|visual_vdp_dump|runtime_comparison_panel')) 'approval record contains runtime evidence'

$AssetRegisterPath = Join-Path $TemplateRoot 'doc\18-asset-register.json'
$AssetRegister = Get-Json -Path $AssetRegisterPath
Assert-True ($AssetRegister.assets[0].promotion_allowed -eq $false) 'asset register seed promotes'
Assert-True ($AssetRegister.assets[0].status -eq 'blocked_no_premium_source') 'asset register default visual status not blocking'

$TemplateRegistryPath = Join-Path $RepoRoot 'doc\template_registry.json'
$TemplateRegistry = Get-Json -Path $TemplateRegistryPath
$Template = @($TemplateRegistry.templates | Where-Object { $_.id -eq 'sgdk_modelo' })[0]
Assert-True ($Template.vibe_playable_birth_seed -eq $true) 'registry missing vibe birth marker'
Assert-True ($Template.template_prevalidated -eq $false) 'registry says template prevalidated'
Assert-True ($Template.contains_runtime_evidence -eq $false) 'registry permits runtime evidence'
Assert-True ($Template.contains_human_approval -eq $false) 'registry permits human approval'
Assert-True ($Template.contains_e2e_fixture_assets -eq $false) 'registry permits e2e fixture assets'
Assert-True ($Template.default_visual_status -eq 'blocked_no_premium_source') 'registry visual default not blocking'

$NewProjectBatText = Get-Content -Raw -LiteralPath (Join-Path $RepoRoot 'tools\sgdk_wrapper\new_project.bat')
$NewProjectShText = Get-Content -Raw -LiteralPath (Join-Path $RepoRoot 'tools\sgdk_wrapper\new_project.sh')
Assert-True ($NewProjectBatText -match 'TARGET_DIR%\\out' -and $NewProjectBatText -match 'rmdir\s+/S\s+/Q\s+"%TARGET_DIR%\\out"') 'new_project.bat does not explicitly prune TARGET_DIR out'
Assert-True ($NewProjectShText -match '\$TARGET_DIR/out' -and $NewProjectShText -match 'rm\s+-rf\s+"\$TARGET_DIR/out"') 'new_project.sh does not explicitly prune TARGET_DIR out'

$ProjectsRoot = Join-Path $RepoRoot 'SGDK_projects'
$BatProjectName = 'VIBE_TEMPLATE_BIRTH_BAT [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]'
$ShProjectName = 'VIBE_TEMPLATE_BIRTH_SH [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]'
$BatProjectRoot = Join-Path $ProjectsRoot $BatProjectName
$ShProjectRoot = Join-Path $ProjectsRoot $ShProjectName

$BatOutput = ''
$ShOutput = ''
try {
    Remove-TestProjectSafely -Path $BatProjectRoot -ExpectedLeaf $BatProjectName
    $BatRun = Invoke-ProcessWithTimeout `
        -FilePath (Join-Path $RepoRoot 'tools\sgdk_wrapper\new_project.bat') `
        -ArgumentList """$BatProjectName""" `
        -OutputPrefix 'new_project_bat'
    $BatOutput = $BatRun.Output
    if ($BatRun.ExitCode -ne 0 -and $BatOutput -notmatch '\[OK\] Project created') {
        throw "new_project.bat failed: $BatOutput"
    }
    Assert-NewProjectBirth -ProjectRoot $BatProjectRoot -ProjectName $BatProjectName
    Assert-True ($BatOutput -match 'blocked_no_premium_source') 'new_project.bat output does not explain blocker'

    $BashUsable = $false
    if ((Get-Command bash -ErrorAction SilentlyContinue) -and (Get-Command pwsh -ErrorAction SilentlyContinue)) {
        $BashProbe = Invoke-ProcessWithTimeout `
            -FilePath 'bash' `
            -ArgumentList '--version' `
            -OutputPrefix 'bash_probe' `
            -TimeoutSeconds 30
        $BashUsable = ($BashProbe.ExitCode -eq 0)
    }

    if ($BashUsable) {
        Remove-TestProjectSafely -Path $ShProjectRoot -ExpectedLeaf $ShProjectName
        $ShRun = Invoke-ProcessWithTimeout `
            -FilePath 'bash' `
            -ArgumentList "tools/sgdk_wrapper/new_project.sh ""$ShProjectName""" `
            -OutputPrefix 'new_project_sh'
        $ShOutput = $ShRun.Output
        if ($ShRun.ExitCode -ne 0 -and $ShOutput -notmatch '\[OK\] Project created') {
            throw "new_project.sh failed: $ShOutput"
        }
        Assert-NewProjectBirth -ProjectRoot $ShProjectRoot -ProjectName $ShProjectName
        Assert-True ($ShOutput -match 'blocked_no_premium_source') 'new_project.sh output does not explain blocker'
    }
    else {
        Write-Output 'new_project_sh_dynamic=skipped_bash_or_pwsh_unavailable'
    }
}
finally {
    Stop-TestProjectProcesses -ProjectName $BatProjectName
    Stop-TestProjectProcesses -ProjectName $ShProjectName
    Remove-TestProjectSafely -Path $BatProjectRoot -ExpectedLeaf $BatProjectName
    Remove-TestProjectSafely -Path $ShProjectRoot -ExpectedLeaf $ShProjectName
}

Write-Output 'test_vibe_playable_template_birth: PASS'
