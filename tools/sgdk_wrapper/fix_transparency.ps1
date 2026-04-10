# ==============================================================================
# fix_transparency.ps1
# Script to automatically fix common resource errors in SGDK build process.
# ==============================================================================

# Global configuration
$MAX_RETRIES = 3
$RETRY_DELAY_MS = 500
$CIRCUIT_BREAKER_THRESHOLD = 20
$LOG_DIR = if ($env:SGDK_LOG_DIR) { $env:SGDK_LOG_DIR } else { Join-Path $pwd.Path "out\logs" }
$DEBUG_LOG = if ($env:SGDK_DEBUG_LOG) { $env:SGDK_DEBUG_LOG } else { Join-Path $LOG_DIR "build_debug.log" }
$BUILD_LOG = if ($env:SGDK_LOG_DIR) { Join-Path $env:SGDK_LOG_DIR "build_output.log" } else { Join-Path $LOG_DIR "build_output.log" }

function Write-Log($msg) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $fullMsg = "[$timestamp] $msg"
    Write-Host $fullMsg
    if (-not (Test-Path -LiteralPath $LOG_DIR)) {
        New-Item -ItemType Directory -Force -Path $LOG_DIR | Out-Null
    }
    Add-Content -LiteralPath $DEBUG_LOG $fullMsg
}

Write-Log "--- Starting Transparency Fixer ---"

# Search for errors in build_output.log
if (Test-Path -LiteralPath $BUILD_LOG) {
    Write-Log "Analyzing $BUILD_LOG..."
    
    $logContent = Get-Content -LiteralPath $BUILD_LOG -Raw
    $cleanLog = [regex]::Replace($logContent, '\x1b\[[0-9;]*m', '') # Strip ANSI
    $logLines = $cleanLog -split '\r?\n'

    $filesToFix = @()
    $errorCount = 0

    for ($i = 0; $i -lt $logLines.Count; $i++) {
        $line = $logLines[$i]
        if ($line -match "has transparent pixel but is not an indexed image" -or 
            $line -match "transparent pixel at .* reference a different palette" -or
            $line -match "RGB image width should be >= 128 to store palette data") {
            
            $errorCount++
            $foundFile = $null

            # Case 1: Next line contains file info
            if ($i + 1 -lt $logLines.Count -and $logLines[$i+1] -match "File: '([^']+)'") {
                $foundFile = $matches[1]
            }
            # Case 2: Nearby "cannot compile resource"
            for ($j = $i; $j -le $i + 3 -and $j -lt $logLines.Count; $j++) {
                if ($logLines[$j] -match "cannot compile resource 'SPRITE \w+ ""([^""]+)"" ") {
                    $relPath = $matches[1]
                    $absPath = Join-Path (Join-Path $pwd.Path "res") $relPath
                    if (Test-Path $absPath) { $foundFile = $absPath }
                    elseif (Test-Path $relPath) { $foundFile = [IO.Path]::GetFullPath($relPath) }
                    elseif (Test-Path (Join-Path $pwd.Path $relPath)) { $foundFile = Join-Path $pwd.Path $relPath }
                }
            }

            if ($foundFile) {
                $filesToFix += $foundFile
            } else {
                Write-Log ("[WARN] Could not identify file path for error at line {0}: {1}" -f $i, $line)
            }
        }
    }

    $filesToFix = $filesToFix | Select-Object -Unique
    Write-Log "Found $($filesToFix.Count) unique files to fix."

    if ($filesToFix.Count -gt 0) {
        # Circuit Breaker check
        if ($errorCount -gt $CIRCUIT_BREAKER_THRESHOLD) {
            Write-Log "[CRITICAL] Too many errors ($errorCount). Circuit breaker triggered. Please check resources manually."
            exit 1
        }

        $ensureSafeImage = Join-Path $PSScriptRoot "ensure_safe_image.ps1"
        if (-not (Test-Path -LiteralPath $ensureSafeImage)) {
            Write-Log "[ERROR] ensure_safe_image.ps1 not found. Cannot perform automatic fixes."
            exit 1
        }

        foreach ($file in $filesToFix) {
            if (-not (Test-Path $file)) {
                Write-Log "[SKIP] File not found: $file"
                continue
            }

            $success = $false
            for ($attempt = 1; $attempt -le $MAX_RETRIES; $attempt++) {
                Write-Log "Attempting fix on $file (Attempt $attempt/$MAX_RETRIES)..."
                
                try {
                    & $ensureSafeImage -File $file -Force

                    if ($LASTEXITCODE -eq 0) {
                        Write-Log "[OK] Fixed $file"
                        $success = $true
                        break
                    } else {
                        Write-Log "[WARN] ensure_safe_image.ps1 failed with exit code $LASTEXITCODE for $file"
                    }
                } catch {
                    Write-Log "[ERROR] Exception during fix for $($file): $($_.Exception.Message)"
                }

                if (-not $success) {
                    Write-Log "Retrying in $RETRY_DELAY_MS ms..."
                    Start-Sleep -Milliseconds $RETRY_DELAY_MS
                }
            }

            if (-not $success) {
                Write-Log "[FAIL] Failed to fix $file after $MAX_RETRIES attempts."
            }
        }
    }
} else {
    Write-Log "No build output log found. Nothing to do."
}

Write-Log "--- Transparency Fixer Finished ---"
