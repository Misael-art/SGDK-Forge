[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string[]]$Roots,

    [Parameter(Mandatory = $false)]
    [string]$RootsCsv,

    [int]$Limit = 0,

    [switch]$StopOnFirstFail,

    [int]$PerProjectTimeoutSec = 900
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Try-ReadJson {
    param([Parameter(Mandatory = $true)][string]$Path)
    try { return (Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json) } catch { return $null }
}

function Get-BuildPolicy {
    param($Json)
    if ($null -eq $Json) { return "enabled" }
    if ($Json.PSObject.Properties["build_policy"]) {
        $v = [string]$Json.build_policy
        if (-not [string]::IsNullOrWhiteSpace($v)) { return $v.ToLowerInvariant() }
    }
    if ($Json.PSObject.Properties["buildPolicy"]) {
        $v = [string]$Json.buildPolicy
        if (-not [string]::IsNullOrWhiteSpace($v)) { return $v.ToLowerInvariant() }
    }
    return "enabled"
}

function Read-FirstErrorLines {
    param([Parameter(Mandatory = $true)][string]$Path, [int]$Max = 20)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return @() }
    $matches = @(Select-String -LiteralPath $Path -Pattern 'error:|fatal error:|Error \d+|No rule to make target|undefined reference|multiple definition|permission denied|access is denied' -CaseSensitive:$false -ErrorAction SilentlyContinue)
    if (-not $matches) { return @() }
    return @($matches | Select-Object -First $Max | ForEach-Object { $_.Line.TrimEnd() })
}

function Resolve-WorkDir {
    param(
        [Parameter(Mandatory = $true)][string]$ProjectDir,
        [Parameter(Mandatory = $true)][string]$WrapperDir
    )

    $resolver = Join-Path $WrapperDir "resolve_project.ps1"
    if (-not (Test-Path -LiteralPath $resolver -PathType Leaf)) { return $ProjectDir }

    try {
        $json = & powershell -NoProfile -ExecutionPolicy Bypass -File $resolver -EntryDir $ProjectDir -OutputFormat Json 2>$null
        if (-not $json) { return $ProjectDir }
        $ctx = $json | ConvertFrom-Json -ErrorAction Stop
        if ($ctx -and $ctx.SgdkRoot -and (Test-Path -LiteralPath $ctx.SgdkRoot -PathType Container)) {
            return [string]$ctx.SgdkRoot
        }
        return $ProjectDir
    }
    catch {
        return $ProjectDir
    }
}

try {
    $wrapperDir = $PSScriptRoot
    $repoRoot = (Resolve-Path -LiteralPath (Join-Path $wrapperDir "..\\..")).Path
    $wrapperBuild = Join-Path $wrapperDir "build.bat"
    if (-not (Test-Path -LiteralPath $wrapperBuild -PathType Leaf)) {
        throw "Wrapper build.bat ausente: '$wrapperBuild'."
    }

    $effectiveRoots = @()
    if ($Roots -and $Roots.Count -gt 0) { $effectiveRoots += $Roots }
    if (-not [string]::IsNullOrWhiteSpace($RootsCsv)) {
        $effectiveRoots += @($RootsCsv -split ';' | ForEach-Object { $_.Trim() } | Where-Object { $_ })
    }
    if (-not $effectiveRoots -or $effectiveRoots.Count -eq 0) {
        throw "Nenhuma raiz fornecida. Use -Roots ou -RootsCsv."
    }

    $candidates = New-Object System.Collections.Generic.List[object]
    foreach ($root in $effectiveRoots) {
        if (-not (Test-Path -LiteralPath $root -PathType Container)) { continue }

        # Enumerate projects by presence of build.bat (much smaller set than scanning all json).
        Get-ChildItem -LiteralPath $root -Recurse -Force -File -Filter "build.bat" -ErrorAction SilentlyContinue |
            ForEach-Object {
                $proj = $_.Directory.FullName
                $manifestPath = Join-Path $proj ".mddev\\project.json"
                $json = $null
                if (Test-Path -LiteralPath $manifestPath -PathType Leaf) {
                    $json = Try-ReadJson -Path $manifestPath
                }
                $policy = Get-BuildPolicy -Json $json
                if ($policy -eq "disabled") { return }
                if (-not (Test-Path -LiteralPath (Join-Path $proj "src"))) { return }

                $candidates.Add([pscustomobject]@{
                    Project = $proj
                    Manifest = $manifestPath
                    BuildPolicy = $policy
                }) | Out-Null
            }
    }

    $unique = @($candidates | Sort-Object Project -Unique)
    if ($Limit -gt 0) { $unique = @($unique | Select-Object -First $Limit) }

    $runId = (Get-Date -Format "yyyyMMdd_HHmmss")
    $reportDir = Join-Path $env:TEMP ("sgdk_build_reports_{0}" -f $runId)
    New-Item -ItemType Directory -Force -Path $reportDir | Out-Null
    $reportPath = Join-Path $reportDir ("build_all_enabled_{0}.json" -f $runId)

    $progressLog = Join-Path $reportDir "progress.log"
    "START run_id=$runId" | Add-Content -LiteralPath $progressLog

    $results = New-Object System.Collections.Generic.List[object]
    $i = 0
    foreach ($c in $unique) {
        $i++
        $line = ("[BUILD] ({0}/{1}) {2}" -f $i, $unique.Count, $c.Project)
        Write-Host $line
        $line | Add-Content -LiteralPath $progressLog

        $workDir = Resolve-WorkDir -ProjectDir $c.Project -WrapperDir $wrapperDir

        $sw = [System.Diagnostics.Stopwatch]::StartNew()
        $outFile = Join-Path $reportDir ("console_{0:D4}.out.log" -f $i)
        $errFile = Join-Path $reportDir ("console_{0:D4}.err.log" -f $i)
        $p = Start-Process -FilePath "cmd.exe" -ArgumentList @("/c","call `"$wrapperBuild`" `"$($c.Project)`"") -NoNewWindow -PassThru -RedirectStandardOutput $outFile -RedirectStandardError $errFile
        $exited = $p.WaitForExit($PerProjectTimeoutSec * 1000)
        if (-not $exited) {
            try { $p.Kill($true) } catch { try { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue } catch {} }
            $rc = 124
        } else {
            try { $p.Refresh() } catch {}
            $rc = [int]$p.ExitCode
        }
        $sw.Stop()

        $romPath = Join-Path $workDir "out\\rom.bin"
        $romExists = Test-Path -LiteralPath $romPath -PathType Leaf
        $logBuild = Join-Path $workDir "out\\logs\\build_output.log"
        $logDebug = Join-Path $workDir "out\\logs\\build_debug.log"

        $errors = @()
        if ($rc -ne 0 -or -not $romExists) {
            $errors += Read-FirstErrorLines -Path $logBuild -Max 20
            $errors += Read-FirstErrorLines -Path $logDebug -Max 20
            if (-not $errors -and (Test-Path -LiteralPath $errFile)) {
                $errors += @(Get-Content -LiteralPath $errFile -ErrorAction SilentlyContinue | Select-Object -First 60)
            }
            if (-not $errors -and (Test-Path -LiteralPath $outFile)) {
                $errors += @(Get-Content -LiteralPath $outFile -ErrorAction SilentlyContinue | Select-Object -First 60)
            }
            if ($rc -eq 124) {
                $errors = @("[TIMEOUT] Projeto excedeu o timeout de $PerProjectTimeoutSec s e foi interrompido.") + $errors
            }
        }

        $results.Add([pscustomobject]@{
            project = $c.Project
            work_dir = $workDir
            manifest = $c.Manifest
            build_policy = $c.BuildPolicy
            exit_code = $rc
            duration_ms = $sw.ElapsedMilliseconds
            rom_exists = $romExists
            rom_path = $romPath
            build_log = $logBuild
            debug_log = $logDebug
            console_out_log = $outFile
            console_err_log = $errFile
            error_snippets = $errors
        }) | Out-Null

        ("[DONE] rc={0} rom={1} ms={2} {3}" -f $rc, $romExists, $sw.ElapsedMilliseconds, $c.Project) | Add-Content -LiteralPath $progressLog

        if ($StopOnFirstFail -and ($rc -ne 0 -or -not $romExists)) { break }
    }

    $summary = [pscustomobject]@{
        run_id = $runId
        total = $results.Count
        ok = @($results | Where-Object { $_.exit_code -eq 0 -and $_.rom_exists }).Count
        failed = @($results | Where-Object { $_.exit_code -ne 0 -or -not $_.rom_exists }).Count
        report_path = $reportPath
    }

    $payload = [pscustomobject]@{
        summary = $summary
        results = $results
    }

    $payload | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $reportPath -Encoding UTF8

    Write-Host ("[SUMMARY] total={0} ok={1} failed={2}" -f $summary.total, $summary.ok, $summary.failed)
    Write-Host ("[REPORT] {0}" -f $reportPath)
    ("END total={0} ok={1} failed={2}" -f $summary.total, $summary.ok, $summary.failed) | Add-Content -LiteralPath $progressLog
    if ($summary.failed -gt 0) { exit 1 }
    exit 0
}
catch {
    Write-Error $_
    exit 1
}

