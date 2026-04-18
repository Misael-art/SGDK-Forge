function SGDK_GetMagickPath {
    $candidates = @()
    $cmdMagick = Get-Command magick -ErrorAction SilentlyContinue
    if ($cmdMagick -and $cmdMagick.Source -and ($cmdMagick.Source -notmatch 'WindowsApps')) {
        $candidates += $cmdMagick.Source
    }
    $searchRoots = @((Join-Path $env:ProgramFiles 'ImageMagick*'))
    $pf86 = [Environment]::GetEnvironmentVariable('ProgramFiles(x86)')
    if (-not [string]::IsNullOrWhiteSpace($pf86)) {
        $searchRoots += (Join-Path $pf86 'ImageMagick*')
    }
    foreach ($root in $searchRoots) {
        $found = Get-ChildItem -Path $root -Filter 'magick.exe' -Recurse -ErrorAction SilentlyContinue |
            Select-Object -ExpandProperty FullName
        if ($found) { $candidates += $found }
    }
    foreach ($p in $candidates) {
        if ($p -and (Test-Path -LiteralPath $p)) {
            return [string]$p
        }
    }
    return $null
}

function SGDK_GetPythonPath {
    function Test-UsablePythonExe([string]$Path) {
        if (-not $Path -or -not (Test-Path -LiteralPath $Path)) { return $false }
        if ($Path -match 'WindowsApps') { return $false }
        return $true
    }
    foreach ($name in @('python', 'py')) {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if ($cmd -and (Test-UsablePythonExe $cmd.Source)) {
            return $cmd.Source
        }
    }
    $roots = @(
        (Join-Path $env:LOCALAPPDATA 'Programs\Python'),
        (Join-Path $env:ProgramFiles 'Python*')
    )
    $pf86 = [Environment]::GetEnvironmentVariable('ProgramFiles(x86)')
    if (-not [string]::IsNullOrWhiteSpace($pf86)) {
        $roots += (Join-Path $pf86 'Python*')
    }
    foreach ($root in $roots) {
        $exes = Get-ChildItem -Path $root -Filter 'python.exe' -Recurse -ErrorAction SilentlyContinue |
            Where-Object { $_.FullName -notmatch 'WindowsApps' } |
            Sort-Object FullName -Descending
        foreach ($ex in $exes) {
            if (Test-UsablePythonExe $ex.FullName) { return $ex.FullName }
        }
    }
    return $null
}

function SGDK_EstimateVDPSprites([int]$wTiles, [int]$hTiles) {
    $count = 0
    $remW = $wTiles
    while ($remW -gt 0) {
        $stepW = if ($remW -ge 4) { 4 } else { $remW }
        $remH = $hTiles
        while ($remH -gt 0) {
            $stepH = if ($remH -ge 4) { 4 } else { $remH }
            $count++
            $remH -= $stepH
        }
        $remW -= $stepW
    }
    return $count
}

function SGDK_FindRecoveredPath([string]$relPath, [string]$baseDir) {
    $fileName = Split-Path $relPath -Leaf
    $searchDirs = @("sprite", "sprites", "gfx", "bg", "bgs", "sound", "sfx", "music")
    foreach ($parent in @("sprite", "sprites", "gfx", "bg", "bgs")) {
        $parentPath = Join-Path $baseDir $parent
        if (Test-Path -LiteralPath $parentPath) {
            Get-ChildItem -LiteralPath $parentPath -Directory -ErrorAction SilentlyContinue | ForEach-Object {
                $searchDirs += "$parent/$($_.Name)"
            }
        }
    }
    foreach ($dir in $searchDirs | Select-Object -Unique) {
        $tryPath = Join-Path $baseDir (Join-Path $dir $fileName)
        if (Test-Path -LiteralPath $tryPath) {
            return $tryPath
        }
    }
    return $null
}
