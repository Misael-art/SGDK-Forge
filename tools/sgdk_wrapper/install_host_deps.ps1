param (
    [string]$GDKPath
)

$ErrorActionPreference = 'Stop'

Write-Host "============================================"
Write-Host " MegaDrive_DEV - Host Environment Setup"
Write-Host "============================================"

if ([string]::IsNullOrWhiteSpace($GDKPath)) {
    throw "GDKPath was not provided to install_host_deps.ps1."
}

if (-not (Test-Path -LiteralPath $GDKPath)) {
    Write-Host "[Setup] SGDK root not found at: $GDKPath"
    Write-Host "[Setup] Creating the expected local SDK folder so the path is stable on this host..."
    New-Item -ItemType Directory -Path $GDKPath -Force | Out-Null
    Write-Host "[Setup] NOTE: This step does not download SGDK itself."
    Write-Host "[Setup] Extract SGDK 2.11 into that folder or define GDK to an existing installation."
}

# 1. Update GDK variables
Write-Host "[Setup] Registering GDK environment variables for User..."
[Environment]::SetEnvironmentVariable('GDK', $GDKPath, 'User')
[Environment]::SetEnvironmentVariable('GDK_WIN', $GDKPath, 'User')

# 2. Update User PATH
$GDKBin = Join-Path -Path $GDKPath -ChildPath "bin"
$userPath = [Environment]::GetEnvironmentVariable('Path', 'User')

# Robust check for GDKBin in PATH
$escapedGDKBin = [regex]::Escape($GDKBin)
if ($userPath -notmatch "($escapedGDKBin\\?)(;|$)") {
    Write-Host "[Setup] Adding $GDKBin to User PATH..."
    if ([string]::IsNullOrWhiteSpace($userPath)) {
        $newPath = $GDKBin
    } elseif ($userPath.EndsWith(';')) {
        $newPath = $userPath + $GDKBin
    } else {
        $newPath = $userPath + ';' + $GDKBin
    }
    [Environment]::SetEnvironmentVariable('Path', $newPath, 'User')
} else {
    Write-Host "[Setup] $GDKBin is already in User PATH."
}

# 3. Check for external dependencies (Java is required for rescomp)
Write-Host "[Setup] Checking for Java runtime..."
try {
    $javaPath = Get-Command java -ErrorAction SilentlyContinue
    if ($javaPath) {
        Write-Host "[Setup] Java is installed at: $($javaPath.Source)"
    } else {
        Write-Host "[Setup] Java not found! Attempting to install Eclipse Temurin JRE 17 via Winget..."
        # We use winget and accept all agreements to make it unattended
        $wingetArgs = @("install", "--id", "EclipseAdoptium.Temurin.17.JRE", "-e", "--accept-package-agreements", "--accept-source-agreements", "--silent")
        Write-Host "[Setup] Running: winget $wingetArgs"
        
        $process = Start-Process winget -ArgumentList $wingetArgs -Wait -NoNewWindow -PassThru
        if ($process.ExitCode -eq 0) {
            Write-Host "[Setup] Java installed successfully."
        } else {
            Write-Host "[WARNING] Winget failed to install Java (ExitCode: $($process.ExitCode))."
            Write-Host "Please install Java manually to use the SGDK resource compiler (rescomp)."
        }
    }
} catch {
    Write-Host "[ERROR] An error occurred while checking/installing Java: $_"
}

# 3b. Python runtime needed for some tooling/scripts
Write-Host "[Setup] Checking for Python installation..."
try {
    $pyPath = Get-Command python -ErrorAction SilentlyContinue
    if ($pyPath) {
        Write-Host "[Setup] Python is installed at: $($pyPath.Source)"
    } else {
        Write-Host "[Setup] Python not found! Attempting to install Python 3 via Winget..."
        $wingetArgs = @("install", "--id", "Python.Python.3", "-e", "--accept-package-agreements", "--accept-source-agreements", "--silent")
        Write-Host "[Setup] Running: winget $wingetArgs"
        $process = Start-Process winget -ArgumentList $wingetArgs -Wait -NoNewWindow -PassThru
        if ($process.ExitCode -eq 0) {
            Write-Host "[Setup] Python installed successfully."
        } else {
            Write-Host "[WARNING] Winget failed to install Python (ExitCode: $($process.ExitCode))."
            Write-Host "Please install Python manually if you plan to use any Python scripts."        
        }
    }
} catch {
    Write-Host "[ERROR] An error occurred while checking/installing Python: $_"
}

# 3c. ImageMagick for image conversions
Write-Host "[Setup] Checking for ImageMagick (magick.exe)..."
try {
    function Test-Magick {
        # Source for the reload logic: https://stackoverflow.com/a/32428135
        # This allows the current session to see PATH changes made by installers
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        $magickPath = Get-Command magick -ErrorAction SilentlyContinue
        if ($magickPath) {
            return $magickPath
        }

        # If Get-Command still fails, search well-known installation directories
        $programFiles = ${env:ProgramFiles}
        $programFilesX86 = ${env:ProgramFiles(x86)}
        $possiblePaths = @(
            (Join-Path $programFiles "ImageMagick*\magick.exe"),
            (Join-Path $programFilesX86 "ImageMagick*\magick.exe")
        )
        foreach ($path in $possiblePaths) {
            $found = Get-ChildItem $path -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($found) {
                # Return the object so the caller can see the path
                return $found
            }
        }
        return $null
    }

    $magick = Test-Magick

    if ($magick) {
        Write-Host "[Setup] ImageMagick is already installed."
    } else {
        Write-Host "[Setup] ImageMagick not found. Attempting installation..."
        
        # Attempt 1: Winget
        Write-Host "[Setup] Trying to install via Winget..."
        # ID from `winget search ImageMagick`
        $wingetArgs = @("install", "--id", "ImageMagick.ImageMagick", "-e", "--accept-package-agreements", "--accept-source-agreements", "--silent")
        $process = Start-Process winget -ArgumentList $wingetArgs -Wait -NoNewWindow -PassThru
        
        if ($process.ExitCode -ne 0) {
            Write-Host "[WARNING] Winget exited with code $($process.ExitCode). Verifying installation anyway..."
        }

        $magick = Test-Magick
        if ($magick) {
            Write-Host "[Setup] ImageMagick installed successfully via Winget (verified)."
        } else {
            Write-Host "[WARNING] Winget installation failed or was not detected."
            
            # Attempt 2: Local Installer Fallback
            $ScriptPath = $PSScriptRoot
            # The installer should be in tools\ImageMagick, relative to this script's location in tools\sgdk_wrapper
            $localInstallerPath = Join-Path (Resolve-Path (Join-Path $ScriptPath "..")) "ImageMagick"
            $localInstaller = Get-ChildItem (Join-Path $localInstallerPath "ImageMagick*.exe") -ErrorAction SilentlyContinue | Select-Object -First 1

            if ($localInstaller) {
                Write-Host "[Setup] Found local installer. Executing silently: $($localInstaller.FullName)"
                $instArgs = "/VERYSILENT", "/NORESTART", "/SP-"
                $instProc = Start-Process -FilePath $localInstaller.FullName -ArgumentList $instArgs -Wait -NoNewWindow -PassThru
                
                if ($instProc.ExitCode -ne 0) {
                    Write-Host "[WARNING] Local installer exited with non-zero code $($instProc.ExitCode). This is often okay. Verifying installation..."
                }

                $magick = Test-Magick
                if ($magick) {
                    Write-Host "[Setup] ImageMagick installed successfully via local installer (verified)."
                } else {
                    Write-Host "[WARNING] FATAL: Could not verify ImageMagick installation after running local installer."
                    Write-Host "Please install ImageMagick manually from https://imagemagick.org and ensure 'magick.exe' is in your PATH."
                }
            } else {
                Write-Host "[WARNING] FATAL: No local ImageMagick installer (ImageMagick*.exe) found in $localInstallerPath."
                Write-Host "Please install ImageMagick manually and ensure 'magick.exe' is in your PATH."
            }
        }
    }
} catch {
    Write-Host "[ERROR] An unexpected error occurred while checking/installing ImageMagick: $_"
}

# 4. Check for Microsoft Visual C++ 2010 Redistributable (Required for EmuHawk/BizHawk)
Write-Host "[Setup] Ensuring Microsoft Visual C++ 2010 Redistributable is installed..."

$vcPackages = @("Microsoft.VCRedist.2010.x64", "Microsoft.VCRedist.2010.x86")

foreach ($vcPack in $vcPackages) {
    Write-Host "[Setup] Checking Winget for $vcPack..."
    $vcArgs = @("install", "--id", $vcPack, "-e", "--accept-package-agreements", "--accept-source-agreements", "--silent")
    $vcProcess = Start-Process winget -ArgumentList $vcArgs -Wait -NoNewWindow -PassThru
    # ExitCode 0 is success, -1978335189 means already installed
    if ($vcProcess.ExitCode -eq 0) {
        Write-Host "[Setup] $vcPack installed successfully."
    } elseif ($vcProcess.ExitCode -eq -1978335189) {
        Write-Host "[Setup] $vcPack is already installed."
    } else {
        Write-Host "[WARNING] Failed to install $vcPack (ExitCode: $($vcProcess.ExitCode))."
        Write-Host "BizHawk might crash or fail to open without this dependency."
    }
}

# 5. Configure default Emulator path for portable execution
Write-Host "[Setup] Configuring default emulator..."
# GDKPath is like F:\Projects\MegaDrive_DEV\sdk\sgdk-2.11
# We want F:\Projects\MegaDrive_DEV
$RootPath = (Get-Item $GDKPath).Parent.Parent.FullName
$EmuDir = Join-Path -Path $RootPath -ChildPath "tools\emuladores"

$EmulatorPath = $null
if (Test-Path -Path (Join-Path $EmuDir "BizHawk\EmuHawk.exe")) {
    $EmulatorPath = Join-Path $EmuDir "BizHawk\EmuHawk.exe"
} elseif (Test-Path -Path (Join-Path $EmuDir "Blastem\Blastem.exe")) {
    $EmulatorPath = Join-Path $EmuDir "Blastem\Blastem.exe"
} elseif (Test-Path -Path (Join-Path $EmuDir "Exodus_2.1\Exodus.exe")) {
    $EmulatorPath = Join-Path $EmuDir "Exodus_2.1\Exodus.exe"
} elseif (Test-Path -Path (Join-Path $EmuDir "GensKMod\gens.exe")) {
    $EmulatorPath = Join-Path $EmuDir "GensKMod\gens.exe"
}

if ($EmulatorPath) {
    Write-Host "[Setup] Found Emulator at: $EmulatorPath"
    Write-Host "[Setup] Setting SGDK_EMULATOR_PATH for User..."
    [Environment]::SetEnvironmentVariable('SGDK_EMULATOR_PATH', $EmulatorPath, 'User')
} else {
    Write-Host "[WARNING] No emulator found in $EmuDir"
    Write-Host "[WARNING] SGDK_EMULATOR_PATH will not be set."
}

# 5. Check for VSCode and configure extensions
Write-Host "[Setup] Checking for Visual Studio Code..."
$vscodeExe = $null

$defaultUserPath = Join-Path $env:LocalAppData "Programs\Microsoft VS Code\bin\code.cmd"
$defaultSystemPath = Join-Path $env:ProgramFiles "Microsoft VS Code\bin\code.cmd"

if (Get-Command code -ErrorAction SilentlyContinue) {
    $vscodeExe = "code"
} elseif (Get-Command code-insiders -ErrorAction SilentlyContinue) {
    $vscodeExe = "code-insiders"
} elseif (Test-Path $defaultUserPath) {
    $vscodeExe = $defaultUserPath
} elseif (Test-Path $defaultSystemPath) {
    $vscodeExe = $defaultSystemPath
} else {
    Write-Host "[Setup] VSCode not found! Attempting to install Microsoft Visual Studio Code via Winget..."
    $wingetVSCodeArgs = @("install", "--id", "Microsoft.VisualStudioCode", "-e", "--accept-package-agreements", "--accept-source-agreements", "--silent")
    Write-Host "[Setup] Running: winget $wingetVSCodeArgs"
    $processVSCode = Start-Process winget -ArgumentList $wingetVSCodeArgs -Wait -NoNewWindow -PassThru
    
    if ($processVSCode.ExitCode -eq 0 -or $processVSCode.ExitCode -eq -1978335189) {
        Write-Host "[Setup] VSCode is installed."
        if (Test-Path $defaultUserPath) {
            $vscodeExe = $defaultUserPath
        } elseif (Test-Path $defaultSystemPath) {
            $vscodeExe = $defaultSystemPath
        } else {
            $vscodeExe = "code"
        }
    } else {
        Write-Host "[WARNING] Winget failed to install VSCode (ExitCode: $($processVSCode.ExitCode))."
    }
}

if ($vscodeExe) {
    Write-Host "[Setup] Found VSCode CLI: $vscodeExe"
    Write-Host "[Setup] Ensuring required extensions are installed..."
    
    $requiredExtensions = @(
        "ms-vscode.cpptools",
        "zerasul.genesis-code",
        "zerasul.mega-drive-mega-pack"
    )

    foreach ($ext in $requiredExtensions) {
        Write-Host "[Setup] Installing extension: $ext"
        $extArgs = @("--install-extension", $ext, "--force")
        try {
            $extProcess = Start-Process $vscodeExe -ArgumentList $extArgs -Wait -NoNewWindow -PassThru
            if ($extProcess.ExitCode -eq 0) {
                Write-Host "[Setup] $ext configured successfully."
            } else {
                Write-Host "[WARNING] Failed to install $ext."
            }
        } catch {
            Write-Host "[WARNING] Could not execute $vscodeExe extension installation command for $ext."
        }
    }
}

Write-Host "[Setup] Finished host environment configuration."
Write-Host "============================================"
