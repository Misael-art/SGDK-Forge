<#
.SYNOPSIS
    Tests that canonical bat wrappers correctly parse project-root arguments.
.DESCRIPTION
    The current conservative contract is that unexpected extra arguments are
    ignored by load_project_context.bat, while the first argument remains the
    project root. The test executes cmd.exe /c so quoting behavior is real.
#>

[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$WrapperRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$WorkspaceRoot = [System.IO.Path]::GetFullPath((Join-Path $WrapperRoot '..\..'))
$LabRoot = Join-Path $WorkspaceRoot 'SGDK_projects\_agent_laboratory'
$script:passed = 0
$script:failed = 0
$CreatedRoots = New-Object System.Collections.ArrayList

function Assert-True {
    param([string]$Name, [bool]$Condition, [string]$Detail = '')
    if ($Condition) { $script:passed++; Write-Host "  [PASS] $Name" }
    else { $script:failed++; Write-Host "  [FAIL] $Name -- $Detail" }
}

function Quote-CmdArg {
    param([string]$Value)
    return ('"{0}"' -f ($Value -replace '"', '""'))
}

function New-WrapperFixtureProject {
    param([string]$LeafName)

    $root = Join-Path $LabRoot $LeafName
    [void]$CreatedRoots.Add($root)
    New-Item -ItemType Directory -Force -Path `
        (Join-Path $root 'src'),
        (Join-Path $root 'res'),
        (Join-Path $root 'doc'),
        (Join-Path $root 'out\logs'),
        (Join-Path $root '.mddev') | Out-Null

    $manifest = [ordered]@{
        schema_version = 1
        version = '1.0'
        display_name = $LeafName
        layout = 'flat'
        project_root = '.'
        sgdk_root = '.'
        build_policy = 'disabled'
        kind = 'ci_fixture'
        category = 'wrapper'
        notes = 'Fixture temporaria para teste de parsing de wrapper bat.'
    } | ConvertTo-Json -Depth 4
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText((Join-Path $root '.mddev\project.json'), ($manifest + "`r`n"), $utf8NoBom)
    [System.IO.File]::WriteAllText((Join-Path $root 'doc\13-spec-cenas.md'), "# fixture`n", $utf8NoBom)
    return $root
}

function Invoke-LoadProjectContext {
    param(
        [string]$ProjectRoot,
        [string]$ExpectedRoot = '',
        [string[]]$ExtraArgs = @()
    )

    $loadBat = Join-Path $WrapperRoot 'load_project_context.bat'
    if ([string]::IsNullOrWhiteSpace($ExpectedRoot)) {
        $ExpectedRoot = $ProjectRoot.TrimEnd('\')
    }
    $allArgs = @($ProjectRoot) + @($ExtraArgs)
    $quotedArgs = @($allArgs | ForEach-Object { Quote-CmdArg $_ })
    $command = 'set "__EXPECTED_ROOT={0}" & call {1} {2} & set "__RC=!ERRORLEVEL!" & if "!__RC!"=="0" if /I "!SGDK_PROJECT_ROOT!"=="!__EXPECTED_ROOT!" echo __ROOT_MATCH__=1 & if "!__RC!"=="0" if exist "!SGDK_PROJECT_ROOT!\.mddev\project.json" echo __ROOT_EXISTS__=1 & if "!__RC!"=="0" echo __ROOT__=!SGDK_PROJECT_ROOT! & exit /b !__RC!' -f $ExpectedRoot, (Quote-CmdArg $loadBat), ($quotedArgs -join ' ')
    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $output = & cmd.exe /v:on /d /s /c $command 2>&1
    } finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
    return [pscustomobject]@{
        ExitCode = [int]$LASTEXITCODE
        Output = @($output | ForEach-Object { [string]$_ })
    }
}

function Get-OutputValue {
    param([string[]]$Output, [string]$Name)
    $prefix = "__$Name`__="
    $line = @($Output | Where-Object { $_.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase) } | Select-Object -Last 1)
    if ($line.Count -eq 0) { return '' }
    return $line[0].Substring($prefix.Length).Trim()
}

try {
    New-Item -ItemType Directory -Force -Path $LabRoot | Out-Null

    Write-Host '--- load_project_context.bat canonical existence ---'
    $loadBat = Join-Path $WrapperRoot 'load_project_context.bat'
    Assert-True 'load_project_context.bat exists' (Test-Path -LiteralPath $loadBat -PathType Leaf) $loadBat

    Write-Host '--- load_project_context.bat with missing argument ---'
    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $missingOutput = & cmd.exe /d /s /c ('call {0}' -f (Quote-CmdArg $loadBat)) 2>&1
    } finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
    $missingExit = [int]$LASTEXITCODE
    Assert-True 'load_project_context without arg exits with error' ($missingExit -ne 0) ("exit=$missingExit output=$($missingOutput -join ' | ')")

    Write-Host '--- load_project_context.bat path with spaces ---'
    $spaceRoot = New-WrapperFixtureProject -LeafName ('ci bat caminho com espacos {0}' -f ([guid]::NewGuid().ToString('N').Substring(0, 8)))
    $spaceResult = Invoke-LoadProjectContext -ProjectRoot $spaceRoot
    $spaceMatch = Get-OutputValue -Output $spaceResult.Output -Name 'ROOT_MATCH'
    $spaceExists = Get-OutputValue -Output $spaceResult.Output -Name 'ROOT_EXISTS'
    Assert-True 'path with spaces exits 0' ($spaceResult.ExitCode -eq 0) ("exit=$($spaceResult.ExitCode) output=$($spaceResult.Output -join ' | ')")
    Assert-True 'path with spaces resolves project root' ($spaceMatch -eq '1') ($spaceResult.Output -join ' | ')
    Assert-True 'path with spaces exposes existing project root' ($spaceExists -eq '1') ($spaceResult.Output -join ' | ')

    Write-Host '--- load_project_context.bat path with acento ---'
    $accentRoot = New-WrapperFixtureProject -LeafName ('ci_bat_caminho_com_ação_{0}' -f ([guid]::NewGuid().ToString('N').Substring(0, 8)))
    $accentResult = Invoke-LoadProjectContext -ProjectRoot $accentRoot
    $accentMatch = Get-OutputValue -Output $accentResult.Output -Name 'ROOT_MATCH'
    $accentExists = Get-OutputValue -Output $accentResult.Output -Name 'ROOT_EXISTS'
    Assert-True 'path with acento exits 0' ($accentResult.ExitCode -eq 0) ("exit=$($accentResult.ExitCode) output=$($accentResult.Output -join ' | ')")
    Assert-True 'path with acento resolves project root' ($accentMatch -eq '1') ($accentResult.Output -join ' | ')
    Assert-True 'path with acento exposes existing project root' ($accentExists -eq '1') ($accentResult.Output -join ' | ')

    Write-Host '--- load_project_context.bat path with trailing backslash ---'
    $slashRoot = New-WrapperFixtureProject -LeafName ('ci_bat_trailing_slash_{0}' -f ([guid]::NewGuid().ToString('N').Substring(0, 8)))
    $slashResult = Invoke-LoadProjectContext -ProjectRoot ($slashRoot.TrimEnd('\') + '\') -ExpectedRoot ([System.IO.Path]::GetFullPath($slashRoot))
    $slashMatch = Get-OutputValue -Output $slashResult.Output -Name 'ROOT_MATCH'
    $slashExists = Get-OutputValue -Output $slashResult.Output -Name 'ROOT_EXISTS'
    Assert-True 'path with trailing backslash exits 0' ($slashResult.ExitCode -eq 0) ("exit=$($slashResult.ExitCode) output=$($slashResult.Output -join ' | ')")
    Assert-True 'path with trailing backslash resolves project root' ($slashMatch -eq '1') ($slashResult.Output -join ' | ')
    Assert-True 'path with trailing backslash exposes existing project root' ($slashExists -eq '1') ($slashResult.Output -join ' | ')

    Write-Host '--- load_project_context.bat unexpected extra argument ---'
    $extraRoot = New-WrapperFixtureProject -LeafName ('ci_bat_extra_arg_{0}' -f ([guid]::NewGuid().ToString('N').Substring(0, 8)))
    $extraResult = Invoke-LoadProjectContext -ProjectRoot $extraRoot -ExtraArgs @('--unexpected-extra-arg')
    $extraMatch = Get-OutputValue -Output $extraResult.Output -Name 'ROOT_MATCH'
    $extraExists = Get-OutputValue -Output $extraResult.Output -Name 'ROOT_EXISTS'
    Assert-True 'unexpected extra argument is ignored conservatively' ($extraResult.ExitCode -eq 0) ("exit=$($extraResult.ExitCode) output=$($extraResult.Output -join ' | ')")
    Assert-True 'unexpected extra argument preserves first project root' ($extraMatch -eq '1') ($extraResult.Output -join ' | ')
    Assert-True 'unexpected extra argument exposes existing project root' ($extraExists -eq '1') ($extraResult.Output -join ' | ')

    Write-Host '--- canonical wrapper files ---'
    foreach ($name in @('build.bat', 'clean.bat', 'rebuild.bat', 'run.bat', 'env.bat')) {
        $path = Join-Path $WrapperRoot $name
        Assert-True "$name exists" (Test-Path -LiteralPath $path -PathType Leaf) $path
    }
    $batFiles = Get-ChildItem -LiteralPath $WrapperRoot -Filter '*.bat' | Select-Object -ExpandProperty Name
    Assert-True 'setup-env.bat is not required by current canonical wrappers' (-not ($batFiles -contains 'setup-env.bat')) ($batFiles -join ', ')
    Assert-True 'at least 5 bat wrappers exist' ($batFiles.Count -ge 5) "found $($batFiles.Count): $($batFiles -join ', ')"
}
finally {
    foreach ($root in @($CreatedRoots)) {
        if (Test-Path -LiteralPath $root) {
            Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
}

Write-Host ''
Write-Host "=== Results: $script:passed passed, $script:failed failed ==="
if ($script:failed -gt 0) { exit 1 }
exit 0
