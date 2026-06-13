[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$LogFile
)

$resolvedLog = $LogFile
if (-not [System.IO.Path]::IsPathRooted($resolvedLog)) {
    $resolvedLog = Join-Path (Get-Location).Path $resolvedLog
}

if (-not (Test-Path -LiteralPath $resolvedLog)) {
    exit 0
}

$pattern = '^make\[\d+\]: \[.*\.ltrans\d+\.ltrans\.o\] Error 127 \(ignored\)$'
$lines = Get-Content -LiteralPath $resolvedLog
$filtered = New-Object System.Collections.Generic.List[string]

foreach ($line in $lines) {
    if ($line -notmatch $pattern) {
        [void]$filtered.Add($line)
    }
}

if ($filtered.Count -ne $lines.Count) {
    Set-Content -LiteralPath $resolvedLog -Value $filtered -Encoding Ascii
}
