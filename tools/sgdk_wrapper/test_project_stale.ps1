[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$WorkDir,

    [Parameter(Mandatory = $true)]
    [string]$RomPath,

    [ValidateSet("Batch", "Json")]
    [string]$OutputFormat = "Batch",

    [switch]$InvalidateEvidence
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Convert-ToBatchLine {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][AllowEmptyString()][string]$Value
    )

    $safe = $Value.Replace('"', '""')
    return ('set "{0}={1}"' -f $Name, $safe)
}

function Get-NewestInput {
    param([Parameter(Mandatory = $true)][string]$BaseDir)

    $candidates = @()
    foreach ($name in @("src", "res", "inc")) {
        $path = Join-Path $BaseDir $name
        if (-not (Test-Path -LiteralPath $path -PathType Container)) {
            continue
        }

        $candidates += Get-ChildItem -LiteralPath $path -File -Recurse -ErrorAction SilentlyContinue
    }

    if (-not $candidates -or $candidates.Count -eq 0) {
        return $null
    }

    return $candidates | Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
}

function Get-SafeString {
    param($Value, [string]$Default = "")

    if ($null -eq $Value) {
        return $Default
    }

    $text = [string]$Value
    if ([string]::IsNullOrWhiteSpace($text)) {
        return $Default
    }

    return $text
}

function Resolve-ExistingPathOrNull {
    param($PathValue)

    $text = Get-SafeString $PathValue ""
    if (-not $text) {
        return $null
    }

    try {
        if (Test-Path -LiteralPath $text) {
            return [System.IO.Path]::GetFullPath((Resolve-Path -LiteralPath $text).Path)
        }
    }
    catch {
    }

    return [System.IO.Path]::GetFullPath($text)
}

function Get-DateOrNull {
    param($Value)

    if ($null -eq $Value) {
        return $null
    }

    if ($Value -is [datetimeoffset]) {
        return [datetimeoffset]$Value
    }

    if ($Value -is [datetime]) {
        return [datetimeoffset]$Value
    }

    $text = Get-SafeString $Value ""
    if (-not $text) {
        return $null
    }

    try {
        return [datetimeoffset]::Parse($text, [System.Globalization.CultureInfo]::InvariantCulture, [System.Globalization.DateTimeStyles]::RoundtripKind)
    }
    catch {
        try {
            return [datetimeoffset]::Parse($text, [System.Globalization.CultureInfo]::CurrentCulture, [System.Globalization.DateTimeStyles]::AllowWhiteSpaces)
        }
        catch {
            return $null
        }
    }
}

function Get-FileIdentity {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }

    $item = Get-Item -LiteralPath $Path
    $stream = [System.IO.File]::OpenRead($Path)
    try {
        $sha256 = [System.Security.Cryptography.SHA256]::Create()
        try {
            $hashBytes = $sha256.ComputeHash($stream)
            $hash = ([System.BitConverter]::ToString($hashBytes).Replace("-", "")).ToLowerInvariant()
        }
        finally {
            $sha256.Dispose()
        }
    }
    finally {
        $stream.Dispose()
    }

    return [ordered]@{
        path = $item.FullName
        size_bytes = [int64]$item.Length
        last_write_utc = $item.LastWriteTimeUtc.ToString("o")
        sha256 = $hash
    }
}

function Get-RomIdentityFromSession {
    param($Session)

    if (-not $Session) {
        return $null
    }

    $sessionRomPath = Resolve-ExistingPathOrNull $Session.rom_path
    $sessionSha = Get-SafeString $Session.rom_sha256 ""
    $sessionLastWriteUtc = $null
    $sessionLastWriteUtcValue = Get-DateOrNull $Session.rom_last_write_utc
    if ($sessionLastWriteUtcValue) {
        $sessionLastWriteUtc = $sessionLastWriteUtcValue.ToString("o")
    }
    else {
        $sessionLastWriteUtc = Get-SafeString $Session.rom_last_write_utc ""
    }
    $sessionSizeBytes = $null
    if ($null -ne $Session.rom_size_bytes -and [string]$Session.rom_size_bytes -ne "") {
        try {
            $sessionSizeBytes = [int64]$Session.rom_size_bytes
        }
        catch {
            $sessionSizeBytes = $null
        }
    }

    if (-not $sessionRomPath -and -not $sessionSha -and -not $sessionLastWriteUtc -and $null -eq $sessionSizeBytes) {
        return $null
    }

    return [ordered]@{
        path = $sessionRomPath
        size_bytes = $sessionSizeBytes
        last_write_utc = if ($sessionLastWriteUtc) { $sessionLastWriteUtc } else { $null }
        sha256 = if ($sessionSha) { $sessionSha } else { $null }
    }
}

function Get-RomIdentityFromReport {
    param($Report)

    if (-not $Report -or -not $Report.evidence) {
        return $null
    }

    $identity = $Report.evidence.rom_identity
    if (-not $identity) {
        return $null
    }

    $reportRomPath = Resolve-ExistingPathOrNull $identity.path
    $reportSha = Get-SafeString $identity.sha256 ""
    $reportLastWriteUtc = Get-SafeString $identity.last_write_utc ""
    $reportSizeBytes = $null
    if ($null -ne $identity.size_bytes -and [string]$identity.size_bytes -ne "") {
        try {
            $reportSizeBytes = [int64]$identity.size_bytes
        }
        catch {
            $reportSizeBytes = $null
        }
    }

    if (-not $reportRomPath -and -not $reportSha -and -not $reportLastWriteUtc -and $null -eq $reportSizeBytes) {
        return $null
    }

    return [ordered]@{
        path = $reportRomPath
        size_bytes = $reportSizeBytes
        last_write_utc = if ($reportLastWriteUtc) { $reportLastWriteUtc } else { $null }
        sha256 = if ($reportSha) { $reportSha } else { $null }
    }
}

function Set-PropertyValue {
    param(
        [Parameter(Mandatory = $true)]$Object,
        [Parameter(Mandatory = $true)][string]$Name,
        $Value
    )

    $property = $Object.PSObject.Properties[$Name]
    if ($property) {
        $Object.$Name = $Value
    }
    else {
        $Object | Add-Member -NotePropertyName $Name -NotePropertyValue $Value
    }
}

function Ensure-ObjectProperty {
    param(
        [Parameter(Mandatory = $true)]$Object,
        [Parameter(Mandatory = $true)][string]$Name
    )

    $property = $Object.PSObject.Properties[$Name]
    if ($property -and $null -ne $Object.$Name) {
        return $Object.$Name
    }

    $child = [pscustomobject]@{}
    Set-PropertyValue -Object $Object -Name $Name -Value $child
    return $child
}

function Get-Array {
    param($Value)

    if ($null -eq $Value) {
        return @()
    }

    if ($Value -is [string]) {
        return @($Value)
    }

    return @($Value)
}

function Normalize-RiskTaxonomyLevel {
    param($Level)

    $normalized = (Get-SafeString $Level "").ToUpperInvariant()
    switch ($normalized) {
        "WARN" { return "WARNING" }
        "WARNING" { return "WARNING" }
        "ERROR" { return "ERROR" }
        "INFO" { return "INFO" }
        default { return "OTHER" }
    }
}

function New-RiskTaxonomyBucket {
    return [ordered]@{
        count = 0
        levels = [ordered]@{
            INFO = 0
            WARNING = 0
            ERROR = 0
            OTHER = 0
        }
        types = @()
    }
}

function New-RiskTaxonomy {
    return [ordered]@{
        asset_risk = (New-RiskTaxonomyBucket)
        validator_config_risk = (New-RiskTaxonomyBucket)
        runtime_risk = (New-RiskTaxonomyBucket)
    }
}

function Resolve-RiskDomain {
    param($Type, $Resource, $File)

    $normalizedType = (Get-SafeString $Type "").ToUpperInvariant()
    $normalizedResource = (Get-SafeString $Resource "").ToLowerInvariant()
    $normalizedFile = (Get-SafeString $File "").ToLowerInvariant()

    if (
        $normalizedResource -eq "validator_config" -or
        $normalizedType -eq "INDEX0_THRESHOLD_INVALID_OVERRIDE" -or
        $normalizedType -eq "RUNTIME_THRESHOLDS"
    ) {
        return "validator_config_risk"
    }

    if (
        $normalizedResource -in @("runtime", "emulator", "rom", "code", "heap") -or
        $normalizedType -like "RUNTIME_*" -or
        $normalizedType -like "EMULATOR_*" -or
        $normalizedType -in @("ROM_SIZE", "AGENT_BOOTSTRAP", "BANNED_API", "CODE_SCAN") -or
        $normalizedFile.EndsWith("runtime_metrics.json") -or
        $normalizedFile.EndsWith("emulator_session.json") -or
        $normalizedFile.EndsWith("rom.bin")
    ) {
        return "runtime_risk"
    }

    return "asset_risk"
}

function Get-RiskTaxonomyFromDetails {
    param($Details)

    $taxonomy = New-RiskTaxonomy
    $normalizedDetails = @()

    foreach ($detail in Get-Array $Details) {
        $type = if ($detail.PSObject.Properties["type"]) { Get-SafeString $detail.PSObject.Properties["type"].Value "" } else { "" }
        $resource = if ($detail.PSObject.Properties["resource"]) { Get-SafeString $detail.PSObject.Properties["resource"].Value "" } else { "" }
        $file = if ($detail.PSObject.Properties["file"]) { Get-SafeString $detail.PSObject.Properties["file"].Value "" } else { "" }
        $riskDomain = if ($detail.PSObject.Properties["risk_domain"]) { Get-SafeString $detail.PSObject.Properties["risk_domain"].Value "" } else { "" }
        if (-not $riskDomain) {
            $riskDomain = Resolve-RiskDomain -Type $type -Resource $resource -File $file
        }
        Set-PropertyValue -Object $detail -Name "risk_domain" -Value $riskDomain

        if (-not $taxonomy.Contains($riskDomain)) {
            $taxonomy[$riskDomain] = New-RiskTaxonomyBucket
        }

        $bucket = $taxonomy[$riskDomain]
        $bucket.count = [int]$bucket.count + 1

        $normalizedLevel = Normalize-RiskTaxonomyLevel $detail.level
        if (-not $bucket.levels.Contains($normalizedLevel)) {
            $bucket.levels[$normalizedLevel] = 0
        }
        $bucket.levels[$normalizedLevel] = [int]$bucket.levels[$normalizedLevel] + 1

        if ($type) {
            $existingTypes = @($bucket.types)
            if ($existingTypes -notcontains $type) {
                $bucket.types = @($existingTypes + $type)
            }
        }

        $normalizedDetails += $detail
    }

    return [pscustomobject]@{
        taxonomy = $taxonomy
        details = @($normalizedDetails)
    }
}

function Get-IdentityMismatchReason {
    param(
        [Parameter(Mandatory = $true)]$CurrentRomIdentity,
        $ReferenceIdentity,
        $ReferenceTimestamp,
        [Parameter(Mandatory = $true)][string]$FallbackOlderReason
    )

    if ($ReferenceIdentity) {
        if ($CurrentRomIdentity.path -and $ReferenceIdentity.path -and $CurrentRomIdentity.path -ne $ReferenceIdentity.path) {
            return "rom_path_mismatch"
        }

        $shaMismatch = $ReferenceIdentity.sha256 -and $CurrentRomIdentity.sha256 -and ($ReferenceIdentity.sha256 -ne $CurrentRomIdentity.sha256)
        $sizeMismatch = ($null -ne $ReferenceIdentity.size_bytes) -and ($null -ne $CurrentRomIdentity.size_bytes) -and ([int64]$ReferenceIdentity.size_bytes -ne [int64]$CurrentRomIdentity.size_bytes)
        $writeMismatch = $ReferenceIdentity.last_write_utc -and $CurrentRomIdentity.last_write_utc -and ($ReferenceIdentity.last_write_utc -ne $CurrentRomIdentity.last_write_utc)
        $hasComparableHash = $ReferenceIdentity.sha256 -and $CurrentRomIdentity.sha256
        if ($shaMismatch -or $sizeMismatch -or ((-not $hasComparableHash) -and $writeMismatch)) {
            return "rom_identity_mismatch"
        }

        return $null
    }

    $referenceDate = Get-DateOrNull $ReferenceTimestamp
    if ($referenceDate -and $CurrentRomIdentity.last_write_utc) {
        $romLastWrite = [datetimeoffset]::Parse($CurrentRomIdentity.last_write_utc)
        if ($referenceDate -lt $romLastWrite) {
            return $FallbackOlderReason
        }
    }

    return $null
}

function Mark-OriginEvidenceState {
    param(
        [Parameter(Mandatory = $true)][string]$WorkDirFull,
        [Parameter(Mandatory = $true)][string]$RomFull,
        [Parameter(Mandatory = $true)]$RomIdentity
    )

    $logDir = Join-Path $WorkDirFull "out\logs"
    $sessionPath = Join-Path $logDir "emulator_session.json"
    $reportPath = Join-Path $logDir "validation_report.json"
    $session = $null
    $report = $null

    if (Test-Path -LiteralPath $sessionPath -PathType Leaf) {
        $session = Get-Content -LiteralPath $sessionPath -Raw | ConvertFrom-Json
    }
    if (Test-Path -LiteralPath $reportPath -PathType Leaf) {
        $report = Get-Content -LiteralPath $reportPath -Raw | ConvertFrom-Json
    }

    $sessionIdentity = Get-RomIdentityFromSession -Session $session
    $reportIdentity = Get-RomIdentityFromReport -Report $report
    $sessionReason = if ($session) { Get-IdentityMismatchReason -CurrentRomIdentity $RomIdentity -ReferenceIdentity $sessionIdentity -ReferenceTimestamp $session.timestamp -FallbackOlderReason "session_older_than_rom" } else { $null }
    $reportReason = if ($report) { Get-IdentityMismatchReason -CurrentRomIdentity $RomIdentity -ReferenceIdentity $reportIdentity -ReferenceTimestamp $report.timestamp -FallbackOlderReason "report_older_than_rom" } else { $null }
    $reason = if ($sessionReason) { $sessionReason } else { $reportReason }
    $markedAt = (Get-Date).ToString("o")

    $result = [ordered]@{
        stale_detected = $false
        stale_reason = ""
        session_updated = $false
        report_updated = $false
        session_path = $sessionPath
        report_path = $reportPath
    }

    if (-not $reason) {
        return $result
    }

    $result.stale_detected = $true
    $result.stale_reason = $reason

    if ($session) {
        Set-PropertyValue -Object $session -Name "evidence_stale" -Value $true
        Set-PropertyValue -Object $session -Name "stale_reason" -Value $reason
        Set-PropertyValue -Object $session -Name "stale_marked_at" -Value $markedAt
        Set-PropertyValue -Object $session -Name "stale_against_rom_identity" -Value ([pscustomobject]$RomIdentity)
        $session | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $sessionPath
        $result.session_updated = $true
    }

    if ($report) {
        $evidence = Ensure-ObjectProperty -Object $report -Name "evidence"
        $summary = Ensure-ObjectProperty -Object $report -Name "summary"
        $statusPanel = Ensure-ObjectProperty -Object $report -Name "status_panel"
        $qaAxes = Ensure-ObjectProperty -Object $report -Name "qa_axes"

        Set-PropertyValue -Object $report -Name "timestamp" -Value $markedAt
        Set-PropertyValue -Object $evidence -Name "validation_report_path" -Value $reportPath
        Set-PropertyValue -Object $evidence -Name "emulator_session_path" -Value $(if (Test-Path -LiteralPath $sessionPath -PathType Leaf) { $sessionPath } else { $null })
        Set-PropertyValue -Object $evidence -Name "rom_path" -Value $RomFull
        Set-PropertyValue -Object $evidence -Name "rom_identity" -Value ([pscustomobject]$RomIdentity)
        Set-PropertyValue -Object $evidence -Name "emulator_session_rom_path" -Value $(if ($sessionIdentity) { $sessionIdentity.path } else { $null })
        Set-PropertyValue -Object $evidence -Name "emulator_session_rom_identity" -Value $(if ($sessionIdentity) { [pscustomobject]$sessionIdentity } else { $null })
        $sessionTimestampValue = if ($session) { Get-DateOrNull $session.timestamp } else { $null }
        Set-PropertyValue -Object $evidence -Name "emulator_session_timestamp" -Value $(if ($sessionTimestampValue) { $sessionTimestampValue.ToString("o") } else { $null })
        Set-PropertyValue -Object $evidence -Name "emulator_evidence_reason" -Value $reason

        $existingDetails = @(Get-Array $report.details | Where-Object {
            $detailType = if ($_.PSObject.Properties["type"]) { Get-SafeString $_.PSObject.Properties["type"].Value "" } else { "" }
            $detailOrigin = if ($_.PSObject.Properties["origin"]) { Get-SafeString $_.PSObject.Properties["origin"].Value "" } else { "" }
            -not (($detailType -eq "EMULATOR_EVIDENCE_ORIGIN") -or (($detailType -eq "EMULATOR_EVIDENCE") -and ($detailOrigin -eq "build_wrapper")))
        })
        $originDetail = [pscustomobject]@{
            message = ("Evidencia de emulador marcada como stale na origem: {0}." -f $reason)
            type = "EMULATOR_EVIDENCE_ORIGIN"
            level = "WARNING"
            resource = "emulator"
            file = if (Test-Path -LiteralPath $sessionPath -PathType Leaf) { $sessionPath } else { $reportPath }
            reason = $reason
            origin = "build_wrapper"
            stale_marked_at = $markedAt
            risk_domain = "runtime_risk"
        }
        $riskState = Get-RiskTaxonomyFromDetails -Details @($existingDetails + $originDetail)
        Set-PropertyValue -Object $report -Name "details" -Value $riskState.details
        Set-PropertyValue -Object $report -Name "risk_taxonomy" -Value $riskState.taxonomy

        $warningCount = @((Get-Array $report.details) | Where-Object { $_.level -eq "WARNING" }).Count
        $errorCount = @((Get-Array $report.details) | Where-Object { $_.level -eq "ERROR" }).Count
        Set-PropertyValue -Object $summary -Name "warnings" -Value ([int]$warningCount)
        Set-PropertyValue -Object $summary -Name "errors" -Value ([int]$errorCount)
        if (-not $summary.PSObject.Properties["checked"]) {
            Set-PropertyValue -Object $summary -Name "checked" -Value 0
        }
        if (-not $summary.PSObject.Properties["recovered"]) {
            Set-PropertyValue -Object $summary -Name "recovered" -Value 0
        }

        Set-PropertyValue -Object $statusPanel -Name "emulator_evidence_stale" -Value $true
        Set-PropertyValue -Object $statusPanel -Name "runtime_capture_present" -Value $false
        Set-PropertyValue -Object $statusPanel -Name "blastem_gate" -Value $false
        Set-PropertyValue -Object $statusPanel -Name "testado_em_emulador" -Value $false

        $buildStatus = Get-SafeString $qaAxes.build ""
        if ($buildStatus -eq "sucesso") {
            Set-PropertyValue -Object $qaAxes -Name "build" -Value "sucesso_com_warnings"
        }
        if ((Get-SafeString $qaAxes.boot_emulador "") -eq "ok") {
            Set-PropertyValue -Object $qaAxes -Name "boot_emulador" -Value "stale"
        }
        if ((Get-SafeString $qaAxes.gameplay_basico "") -eq "funcional") {
            Set-PropertyValue -Object $qaAxes -Name "gameplay_basico" -Value "stale"
        }
        Set-PropertyValue -Object $qaAxes -Name "validation_report" -Value "com_alertas"

        $sourceArtifacts = @()
        $statusSourceArtifacts = if ($statusPanel.PSObject.Properties["source_artifacts"]) { $statusPanel.PSObject.Properties["source_artifacts"].Value } else { @() }
        foreach ($artifact in Get-Array $statusSourceArtifacts) {
            $artifactText = Get-SafeString $artifact ""
            if ($artifactText) {
                $sourceArtifacts += $artifactText
            }
        }
        $sourceArtifacts += $reportPath
        if (Test-Path -LiteralPath $sessionPath -PathType Leaf) {
            $sourceArtifacts += $sessionPath
        }
        $sessionEvidenceFiles = if ($session -and $session.PSObject.Properties["evidence_files"]) { $session.PSObject.Properties["evidence_files"].Value } else { @() }
        if ($sessionEvidenceFiles) {
            foreach ($artifact in Get-Array $sessionEvidenceFiles) {
                $artifactText = Get-SafeString $artifact ""
                if ($artifactText) {
                    $sourceArtifacts += $artifactText
                }
            }
        }
        Set-PropertyValue -Object $statusPanel -Name "source_artifacts" -Value @($sourceArtifacts | Select-Object -Unique)

        $report | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $reportPath
        $result.report_updated = $true
    }

    return $result
}

try {
    $workDirFull = [System.IO.Path]::GetFullPath((Resolve-Path -LiteralPath $WorkDir).Path)
    $romFull = [System.IO.Path]::GetFullPath($RomPath)
    $romExists = Test-Path -LiteralPath $romFull -PathType Leaf
    $newestInput = Get-NewestInput -BaseDir $workDirFull
    $evidenceState = [ordered]@{
        stale_detected = $false
        stale_reason = ""
        session_updated = $false
        report_updated = $false
    }

    $result = [ordered]@{
        SGDK_ROM_EXISTS       = if ($romExists) { "1" } else { "0" }
        SGDK_ROM_NEEDS_BUILD  = "0"
        SGDK_ROM_REASON       = "current"
        SGDK_ROM_NEWEST_INPUT = ""
        SGDK_EVIDENCE_STALE   = "0"
        SGDK_EVIDENCE_REASON  = ""
    }

    if ($newestInput) {
        $result["SGDK_ROM_NEWEST_INPUT"] = $newestInput.FullName
    }

    if (-not $romExists) {
        $result["SGDK_ROM_NEEDS_BUILD"] = "1"
        $result["SGDK_ROM_REASON"] = "missing"
    } elseif ($newestInput -and $newestInput.LastWriteTimeUtc -gt (Get-Item -LiteralPath $romFull).LastWriteTimeUtc) {
        $result["SGDK_ROM_NEEDS_BUILD"] = "1"
        $result["SGDK_ROM_REASON"] = "stale"
    }

    if ($InvalidateEvidence -and $romExists) {
        $romIdentity = Get-FileIdentity -Path $romFull
        if ($romIdentity) {
            $evidenceState = Mark-OriginEvidenceState -WorkDirFull $workDirFull -RomFull $romFull -RomIdentity $romIdentity
            if ($evidenceState.stale_detected) {
                $result["SGDK_EVIDENCE_STALE"] = "1"
                $result["SGDK_EVIDENCE_REASON"] = [string]$evidenceState.stale_reason
            }
        }
    }

    if ($OutputFormat -eq "Json") {
        [PSCustomObject]@{
            rom = [PSCustomObject]$result
            evidence = [PSCustomObject]$evidenceState
        } | ConvertTo-Json -Depth 6
        exit 0
    }

    foreach ($pair in $result.GetEnumerator()) {
        Convert-ToBatchLine -Name $pair.Key -Value ([string]$pair.Value)
    }
}
catch {
    Write-Error $_
    exit 1
}
