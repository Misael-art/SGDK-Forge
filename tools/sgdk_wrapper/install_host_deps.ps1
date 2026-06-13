param (
    [string]$GDKPath
)

$ErrorActionPreference = 'Stop'

function Write-Step {
    param([string]$Message)
    Write-Host "[Setup] $Message"
}

function Test-CommandAvailable {
    param([string]$Name)
    return $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

function Refresh-ProcessPath {
    $machinePath = [Environment]::GetEnvironmentVariable('Path', 'Machine')
    $userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
    if ([string]::IsNullOrWhiteSpace($machinePath)) {
        $env:Path = $userPath
    } elseif ([string]::IsNullOrWhiteSpace($userPath)) {
        $env:Path = $machinePath
    } else {
        $env:Path = $machinePath + ';' + $userPath
    }
}

function Invoke-WingetInstall {
    param(
        [Parameter(Mandatory = $true)][string]$Id,
        [Parameter(Mandatory = $true)][string]$Label
    )

    if (-not (Test-CommandAvailable -Name 'winget')) {
        Write-Host "[WARNING] Winget is not available. Cannot install $Label automatically."
        return $false
    }

    $args = @(
        'install',
        '--id', $Id,
        '-e',
        '--accept-package-agreements',
        '--accept-source-agreements',
        '--silent'
    )

    Write-Step "Running: winget $($args -join ' ')"
    $process = Start-Process winget -ArgumentList $args -Wait -NoNewWindow -PassThru
    if ($process.ExitCode -eq 0 -or $process.ExitCode -eq -1978335189) {
        Refresh-ProcessPath
        return $true
    }

    Write-Host "[WARNING] Winget failed to install $Label (ExitCode: $($process.ExitCode))."
    return $false
}

function Test-ValidSgdkPath {
    param([string]$Path)
    if ([string]::IsNullOrWhiteSpace($Path)) { return $false }
    return (Test-Path -LiteralPath (Join-Path $Path 'makefile.gen') -PathType Leaf)
}

function Get-SgdkDownloadCandidates {
    $urls = New-Object System.Collections.Generic.List[string]

    try {
        $release = Invoke-RestMethod -Headers @{ 'User-Agent' = 'SGDK-Forge' } -Uri 'https://api.github.com/repos/Stephane-D/SGDK/releases/tags/v2.11'
        foreach ($asset in $release.assets) {
            if ($asset.name -eq 'sgdk211.7z' -and $asset.browser_download_url) {
                $urls.Add([string]$asset.browser_download_url)
            }
        }
    } catch {
        Write-Host "[WARNING] Could not query the official SGDK release API. Falling back to known download URLs."
    }

    foreach ($fallback in @(
        'https://github.com/Stephane-D/SGDK/releases/download/v2.11/sgdk211.7z',
        'https://sourceforge.net/projects/sgdk/files/releases/v2.11/sgdk211.7z/download'
    )) {
        if (-not $urls.Contains($fallback)) {
            $urls.Add($fallback)
        }
    }

    return @($urls)
}

function Download-File {
    param(
        [Parameter(Mandatory = $true)][string[]]$Urls,
        [Parameter(Mandatory = $true)][string]$Destination
    )

    foreach ($url in $Urls) {
        Write-Step "Downloading SGDK from: $url"
        try {
            if (Test-CommandAvailable -Name 'curl.exe') {
                & curl.exe -L --fail --retry 3 --retry-delay 2 -sS -o $Destination $url
                if ($LASTEXITCODE -eq 0 -and (Test-Path -LiteralPath $Destination) -and ((Get-Item $Destination).Length -gt 0)) {
                    return $true
                }
            } else {
                Invoke-WebRequest -Headers @{ 'User-Agent' = 'SGDK-Forge' } -Uri $url -OutFile $Destination
                if (Test-Path -LiteralPath $Destination) {
                    return $true
                }
            }
        } catch {
            Write-Host "[WARNING] Download failed from $url"
        }

        Remove-Item -LiteralPath $Destination -Force -ErrorAction SilentlyContinue
    }

    return $false
}

function Get-7ZipExecutable {
    foreach ($commandName in @('7z', '7zr')) {
        $command = Get-Command $commandName -ErrorAction SilentlyContinue
        if ($command) {
            return $command.Source
        }
    }

    $commonPaths = @(
        (Join-Path $env:ProgramFiles '7-Zip\7z.exe'),
        (Join-Path ${env:ProgramFiles(x86)} '7-Zip\7z.exe')
    )
    foreach ($path in $commonPaths) {
        if ([string]::IsNullOrWhiteSpace($path)) { continue }
        if (Test-Path -LiteralPath $path -PathType Leaf) {
            return $path
        }
    }

    return $null
}

function Ensure-7ZipExecutable {
    $sevenZip = Get-7ZipExecutable
    if ($sevenZip) {
        return $sevenZip
    }

    Write-Step "7-Zip not found. Attempting installation..."
    if (Invoke-WingetInstall -Id '7zip.7zip' -Label '7-Zip') {
        $sevenZip = Get-7ZipExecutable
        if ($sevenZip) {
            return $sevenZip
        }
    }

    return $null
}

function Ensure-PythonExecutable {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) {
        return $python.Source
    }

    Write-Step "Python not found. Attempting installation..."
    if (Invoke-WingetInstall -Id 'Python.Python.3' -Label 'Python 3') {
        $python = Get-Command python -ErrorAction SilentlyContinue
        if ($python) {
            return $python.Source
        }
    }

    return $null
}

function Expand-SevenZipArchive {
    param(
        [Parameter(Mandatory = $true)][string]$ArchivePath,
        [Parameter(Mandatory = $true)][string]$Destination
    )

    $sevenZip = Ensure-7ZipExecutable
    if ($sevenZip) {
        & $sevenZip x "-o$Destination" '-y' $ArchivePath | Out-Host
        return ($LASTEXITCODE -eq 0)
    }

    $python = Ensure-PythonExecutable
    if (-not $python) {
        Write-Host "[WARNING] No extractor is available for .7z archives."
        return $false
    }

    & $python -c "import py7zr" *> $null
    if ($LASTEXITCODE -ne 0) {
        Write-Step "Installing py7zr as a Python fallback extractor..."
        & $python -m pip install --user py7zr
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[WARNING] Failed to install py7zr."
            return $false
        }
    }

    $extractScript = Join-Path $env:TEMP ("sgdk_extract_{0}.py" -f ([guid]::NewGuid().ToString('N')))
    @'
import os
import sys
import py7zr

archive = sys.argv[1]
destination = sys.argv[2]
os.makedirs(destination, exist_ok=True)
with py7zr.SevenZipFile(archive, mode="r") as handle:
    handle.extractall(path=destination)
'@ | Set-Content -LiteralPath $extractScript -Encoding UTF8

    try {
        & $python $extractScript $ArchivePath $Destination
        return ($LASTEXITCODE -eq 0)
    } finally {
        Remove-Item -LiteralPath $extractScript -Force -ErrorAction SilentlyContinue
    }
}

function Install-SgdkIfMissing {
    param([Parameter(Mandatory = $true)][string]$TargetPath)

    if (Test-ValidSgdkPath -Path $TargetPath) {
        Write-Step "SGDK 2.11 already available at: $TargetPath"
        return $true
    }

    Write-Step "SGDK 2.11 not found. Bootstrapping local SDK..."
    $targetParent = Split-Path -Parent $TargetPath
    if (-not (Test-Path -LiteralPath $targetParent)) {
        New-Item -ItemType Directory -Path $targetParent -Force | Out-Null
    }

    $cacheRoot = Join-Path $env:TEMP 'sgdk-wrapper-cache'
    $archivePath = Join-Path $cacheRoot 'sgdk211.7z'
    $extractRoot = Join-Path $cacheRoot ("extract_{0}" -f ([guid]::NewGuid().ToString('N')))

    New-Item -ItemType Directory -Path $cacheRoot -Force | Out-Null
    New-Item -ItemType Directory -Path $extractRoot -Force | Out-Null

    if (-not (Test-Path -LiteralPath $archivePath) -or ((Get-Item $archivePath).Length -eq 0)) {
        if (-not (Download-File -Urls (Get-SgdkDownloadCandidates) -Destination $archivePath)) {
            Write-Host "[WARNING] Failed to download SGDK 2.11 automatically."
            return $false
        }
    } else {
        Write-Step "Reusing cached SGDK archive: $archivePath"
    }

    if (-not (Expand-SevenZipArchive -ArchivePath $archivePath -Destination $extractRoot)) {
        Write-Host "[WARNING] Failed to extract the SGDK archive."
        return $false
    }

    $makefile = Get-ChildItem -Path $extractRoot -Filter 'makefile.gen' -File -Recurse -ErrorAction SilentlyContinue |
        Sort-Object { $_.FullName.Length } |
        Select-Object -First 1

    if (-not $makefile) {
        Write-Host "[WARNING] Extracted archive did not contain makefile.gen."
        return $false
    }

    $sourceRoot = $makefile.Directory.FullName
    if (Test-Path -LiteralPath $TargetPath) {
        if (Test-ValidSgdkPath -Path $TargetPath) {
            return $true
        }

        $backupPath = "{0}_backup_{1}" -f $TargetPath, (Get-Date -Format 'yyyyMMdd_HHmmss')
        Write-Step "Backing up incomplete SDK folder to: $backupPath"
        Move-Item -LiteralPath $TargetPath -Destination $backupPath -Force
    }

    New-Item -ItemType Directory -Path $TargetPath -Force | Out-Null
    Copy-Item -Path (Join-Path $sourceRoot '*') -Destination $TargetPath -Recurse -Force

    if (Test-ValidSgdkPath -Path $TargetPath) {
        Write-Step "SGDK 2.11 installed successfully at: $TargetPath"
        return $true
    }

    Write-Host "[WARNING] SGDK bootstrap finished without a valid makefile.gen at $TargetPath."
    return $false
}

Write-Host "============================================"
Write-Host " MegaDrive_DEV - Host Environment Setup"
Write-Host "============================================"

if ([string]::IsNullOrWhiteSpace($GDKPath)) {
    throw "GDKPath was not provided to install_host_deps.ps1."
}

$sgdkReady = Install-SgdkIfMissing -TargetPath $GDKPath

# 1. Update GDK variables
Write-Step "Registering GDK environment variables for User..."
[Environment]::SetEnvironmentVariable('GDK', $GDKPath, 'User')
[Environment]::SetEnvironmentVariable('GDK_WIN', $GDKPath, 'User')

# 2. Update User PATH
$GDKBin = Join-Path -Path $GDKPath -ChildPath 'bin'
$userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
$escapedGDKBin = [regex]::Escape($GDKBin)
if ($userPath -notmatch "($escapedGDKBin\\?)(;|$)") {
    Write-Step "Adding $GDKBin to User PATH..."
    if ([string]::IsNullOrWhiteSpace($userPath)) {
        $newPath = $GDKBin
    } elseif ($userPath.EndsWith(';')) {
        $newPath = $userPath + $GDKBin
    } else {
        $newPath = $userPath + ';' + $GDKBin
    }
    [Environment]::SetEnvironmentVariable('Path', $newPath, 'User')
} else {
    Write-Step "$GDKBin is already in User PATH."
}

# 3. Check for Java runtime (required for rescomp)
Write-Step "Checking for Java runtime..."
try {
    $javaPath = Get-Command java -ErrorAction SilentlyContinue
    if ($javaPath) {
        Write-Step "Java is installed at: $($javaPath.Source)"
    } else {
        Write-Step "Java not found. Attempting installation..."
        if (Invoke-WingetInstall -Id 'EclipseAdoptium.Temurin.17.JRE' -Label 'Eclipse Temurin JRE 17') {
            $javaPath = Get-Command java -ErrorAction SilentlyContinue
            if ($javaPath) {
                Write-Step "Java installed successfully."
            }
        } else {
            Write-Host "[WARNING] Please install Java manually to use the SGDK resource compiler (rescomp)."
        }
    }
} catch {
    Write-Host "[ERROR] An error occurred while checking/installing Java: $_"
}

# 3b. Python runtime needed for tooling and archive fallback
Write-Step "Checking for Python installation..."
try {
    $pythonPath = Ensure-PythonExecutable
    if ($pythonPath) {
        Write-Step "Python is installed at: $pythonPath"
    } else {
        Write-Host "[WARNING] Please install Python manually if you plan to use Python-based tools."
    }
} catch {
    Write-Host "[ERROR] An error occurred while checking/installing Python: $_"
}

# 3c. ImageMagick for image conversions
Write-Step "Checking for ImageMagick (magick.exe)..."
try {
    function Test-Magick {
        Refresh-ProcessPath
        $magickPath = Get-Command magick -ErrorAction SilentlyContinue
        if ($magickPath) {
            return $magickPath
        }

        $programFiles = ${env:ProgramFiles}
        $programFilesX86 = ${env:ProgramFiles(x86)}
        $possiblePaths = @(
            (Join-Path $programFiles 'ImageMagick*\magick.exe'),
            (Join-Path $programFilesX86 'ImageMagick*\magick.exe')
        )
        foreach ($path in $possiblePaths) {
            $found = Get-ChildItem $path -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($found) {
                return $found
            }
        }
        return $null
    }

    $magick = Test-Magick
    if ($magick) {
        Write-Step "ImageMagick is already installed."
    } else {
        Write-Step "ImageMagick not found. Attempting installation..."
        if (Invoke-WingetInstall -Id 'ImageMagick.ImageMagick' -Label 'ImageMagick') {
            $magick = Test-Magick
            if ($magick) {
                Write-Step "ImageMagick installed successfully via Winget."
            }
        }

        if (-not $magick) {
            $localInstallerPath = Join-Path (Resolve-Path (Join-Path $PSScriptRoot '..')) 'ImageMagick'
            $localInstaller = Get-ChildItem (Join-Path $localInstallerPath 'ImageMagick*.exe') -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($localInstaller) {
                Write-Step "Found local ImageMagick installer. Executing silently..."
                $instArgs = '/VERYSILENT', '/NORESTART', '/SP-'
                $instProc = Start-Process -FilePath $localInstaller.FullName -ArgumentList $instArgs -Wait -NoNewWindow -PassThru
                if ($instProc.ExitCode -ne 0) {
                    Write-Host "[WARNING] Local ImageMagick installer exited with code $($instProc.ExitCode). Verifying installation anyway..."
                }

                $magick = Test-Magick
                if ($magick) {
                    Write-Step "ImageMagick installed successfully via local installer."
                }
            }
        }

        if (-not $magick) {
            Write-Host "[WARNING] Please install ImageMagick manually from https://imagemagick.org and ensure 'magick.exe' is in your PATH."
        }
    }
} catch {
    Write-Host "[ERROR] An unexpected error occurred while checking/installing ImageMagick: $_"
}

# 4. Check for Microsoft Visual C++ 2010 Redistributable (Required for EmuHawk/BizHawk)
Write-Step "Ensuring Microsoft Visual C++ 2010 Redistributable is installed..."
foreach ($vcPack in @('Microsoft.VCRedist.2010.x64', 'Microsoft.VCRedist.2010.x86')) {
    try {
        if (Invoke-WingetInstall -Id $vcPack -Label $vcPack) {
            Write-Step "$vcPack is installed."
        } else {
            Write-Host "[WARNING] BizHawk may fail to open without $vcPack."
        }
    } catch {
        Write-Host "[WARNING] Failed while checking/installing $vcPack."
    }
}

# 5. Configure default emulator path for portable execution
Write-Step "Configuring default emulator..."
try {
    $rootItem = Get-Item -LiteralPath $GDKPath -ErrorAction SilentlyContinue
    if ($rootItem -and $rootItem.Parent -and $rootItem.Parent.Parent) {
        $rootPath = $rootItem.Parent.Parent.FullName
        $emuDir = Join-Path -Path $rootPath -ChildPath 'tools\emuladores'

        $emulatorPath = $null
        if (Test-Path -Path (Join-Path $emuDir 'Blastem\Blastem.exe')) {
            $emulatorPath = Join-Path $emuDir 'Blastem\Blastem.exe'
        } elseif (Test-Path -Path (Join-Path $emuDir 'BizHawk\EmuHawk.exe')) {
            $emulatorPath = Join-Path $emuDir 'BizHawk\EmuHawk.exe'
        } elseif (Test-Path -Path (Join-Path $emuDir 'Exodus_2.1\Exodus.exe')) {
            $emulatorPath = Join-Path $emuDir 'Exodus_2.1\Exodus.exe'
        } elseif (Test-Path -Path (Join-Path $emuDir 'GensKMod\gens.exe')) {
            $emulatorPath = Join-Path $emuDir 'GensKMod\gens.exe'
        }

        if ($emulatorPath) {
            Write-Step "Found emulator at: $emulatorPath"
            [Environment]::SetEnvironmentVariable('SGDK_EMULATOR_PATH', $emulatorPath, 'User')
        } else {
            Write-Host "[WARNING] No emulator found in $emuDir"
        }
    }
} catch {
    Write-Host "[WARNING] Failed to resolve a default emulator path."
}

# 6. Check for VSCode and configure extensions
Write-Step "Checking for Visual Studio Code..."
$vscodeExe = $null
$defaultUserPath = Join-Path $env:LocalAppData 'Programs\Microsoft VS Code\bin\code.cmd'
$defaultSystemPath = Join-Path $env:ProgramFiles 'Microsoft VS Code\bin\code.cmd'

if (Get-Command code -ErrorAction SilentlyContinue) {
    $vscodeExe = 'code'
} elseif (Get-Command code-insiders -ErrorAction SilentlyContinue) {
    $vscodeExe = 'code-insiders'
} elseif (Test-Path $defaultUserPath) {
    $vscodeExe = $defaultUserPath
} elseif (Test-Path $defaultSystemPath) {
    $vscodeExe = $defaultSystemPath
} else {
    Write-Step "VSCode not found. Attempting installation..."
    if (Invoke-WingetInstall -Id 'Microsoft.VisualStudioCode' -Label 'Visual Studio Code') {
        if (Test-Path $defaultUserPath) {
            $vscodeExe = $defaultUserPath
        } elseif (Test-Path $defaultSystemPath) {
            $vscodeExe = $defaultSystemPath
        } else {
            $vscodeExe = 'code'
        }
    }
}

if ($vscodeExe) {
    Write-Step "Found VSCode CLI: $vscodeExe"
    foreach ($ext in @(
        'ms-vscode.cpptools',
        'zerasul.genesis-code',
        'zerasul.mega-drive-mega-pack'
    )) {
        try {
            Write-Step "Installing VSCode extension: $ext"
            $extProcess = Start-Process $vscodeExe -ArgumentList @('--install-extension', $ext, '--force') -Wait -NoNewWindow -PassThru
            if ($extProcess.ExitCode -ne 0) {
                Write-Host "[WARNING] Failed to install VSCode extension $ext."
            }
        } catch {
            Write-Host "[WARNING] Could not execute VSCode extension installation for $ext."
        }
    }
}

if (-not $sgdkReady) {
    Write-Host "[WARNING] SGDK bootstrap did not complete successfully."
    Write-Host "[WARNING] Expected a valid SGDK 2.11 installation at: $GDKPath"
    Write-Host "[WARNING] You can still fix this manually by extracting SGDK 2.11 there or by setting the GDK environment variable."
}

Write-Step "Finished host environment configuration."
Write-Host "============================================"
