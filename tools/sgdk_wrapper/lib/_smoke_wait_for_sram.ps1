[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$OutPath
)

$ErrorActionPreference = 'Stop'

$modulePath = Join-Path $PSScriptRoot 'blastem_automation.psm1'
$mod = Import-Module -Name $modulePath -Force -PassThru -ErrorAction Stop

$sb = {
    param($Watchers, $DeadlineUtc, $PollIntervalMs)
    Wait-ForSramChangeOrDeadline -Watchers $Watchers -DeadlineUtc $DeadlineUtc -PollIntervalMs $PollIntervalMs
}

$lines = @()

# Case 1: past deadline, no watchers -> should return 'deadline' immediately
$past = [datetime]::UtcNow.AddMilliseconds(-10)
$t0 = [datetime]::UtcNow
$r1 = & $mod $sb @() $past 400
$e1 = ([datetime]::UtcNow - $t0).TotalMilliseconds
$lines += ('CASE1 past-deadline result=' + $r1 + ' elapsed_ms=' + [int]$e1)

# Case 2: future deadline, no watchers -> should pace ~PollIntervalMs and return 'poll_tick'
$future = [datetime]::UtcNow.AddMilliseconds(1000)
$t0 = [datetime]::UtcNow
$r2 = & $mod $sb @() $future 150
$e2 = ([datetime]::UtcNow - $t0).TotalMilliseconds
$lines += ('CASE2 no-watchers-pacing result=' + $r2 + ' elapsed_ms=' + [int]$e2)

# Case 3: null watchers with future deadline -> same pacing behavior
$future2 = [datetime]::UtcNow.AddMilliseconds(1000)
$t0 = [datetime]::UtcNow
$r3 = & $mod $sb $null $future2 100
$e3 = ([datetime]::UtcNow - $t0).TotalMilliseconds
$lines += ('CASE3 null-watchers result=' + $r3 + ' elapsed_ms=' + [int]$e3)

# Case 4: future deadline, 1 empty watcher dir -> Start-BlastEmSaveWatchers returns zero usable -> pacing
$emptyDir = Join-Path $env:TEMP ('blastem_smoke_empty_' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Force -Path $emptyDir | Out-Null
try {
    $watchers = & $mod { param($p) @(Start-BlastEmSaveWatchers -RootPaths @($p)) } $emptyDir
    $future3 = [datetime]::UtcNow.AddMilliseconds(800)
    $t0 = [datetime]::UtcNow
    $r4 = & $mod $sb $watchers $future3 120
    $e4 = ([datetime]::UtcNow - $t0).TotalMilliseconds
    $lines += ('CASE4 one-watcher-no-event result=' + $r4 + ' elapsed_ms=' + [int]$e4 + ' watcher_count=' + @($watchers).Count)
    & $mod { param($w) Stop-BlastEmSaveWatchers -Watchers $w } $watchers
}
finally {
    if (Test-Path -LiteralPath $emptyDir) { Remove-Item -LiteralPath $emptyDir -Recurse -Force }
}

$lines += 'DONE'
Set-Content -LiteralPath $OutPath -Value ($lines -join [Environment]::NewLine) -Encoding UTF8

Remove-Module -Name 'blastem_automation' -Force -ErrorAction SilentlyContinue
