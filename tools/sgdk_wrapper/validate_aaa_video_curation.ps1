param()

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$workspaceRoot = Split-Path -Parent (Split-Path -Parent $scriptDir)
$validator = Join-Path $scriptDir "validate_aaa_video_curation.py"

if (-not (Test-Path -LiteralPath $validator)) {
    throw "Missing validator: $validator"
}

$pythonCandidates = @("python", "py")
$lastError = $null

foreach ($candidate in $pythonCandidates) {
    try {
        & $candidate $validator
        exit $LASTEXITCODE
    } catch {
        $lastError = $_
    }
}

throw "Unable to execute Python validator from $workspaceRoot. Last error: $lastError"
