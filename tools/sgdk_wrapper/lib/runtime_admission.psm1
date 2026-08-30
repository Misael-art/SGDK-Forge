function Get-RuntimeAdmissionFileSha256 {
    param([string]$Path)

    if ([string]::IsNullOrWhiteSpace($Path)) {
        return $null
    }

    $ResolvedPath = (Resolve-Path -LiteralPath $Path).Path
    return (Get-FileHash -Algorithm SHA256 -LiteralPath $ResolvedPath).Hash.ToLowerInvariant()
}

function ConvertTo-RuntimeAdmissionSha256 {
    param([string]$Text)

    $Sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $Bytes = [System.Text.Encoding]::UTF8.GetBytes([string]$Text)
        $Hash = $Sha.ComputeHash($Bytes)
        return (($Hash | ForEach-Object { $_.ToString('x2') }) -join '')
    }
    finally {
        $Sha.Dispose()
    }
}

function Read-RuntimeAdmissionJsonFile {
    param([string]$Path)

    $ResolvedPath = (Resolve-Path -LiteralPath $Path).Path
    return Get-Content -Raw -LiteralPath $ResolvedPath | ConvertFrom-Json
}

function Test-TechnicalChangeScopeIsRuntimeOnly {
    param([object]$Scope)

    if ($null -eq $Scope) {
        return $false
    }

    if ([bool]$Scope.changes_player_facing_visuals) {
        return $false
    }
    if ([bool]$Scope.changes_assets) {
        return $false
    }
    if ([bool]$Scope.changes_composition) {
        return $false
    }
    if ([bool]$Scope.changes_presentation) {
        return $false
    }

    return $true
}

function New-RuntimeAdmissionReport {
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet('production_visual', 'technical', 'lab')]
        [string]$AdmissionType,

        [string]$RouteReportPath,
        [string]$TechnicalChangeScopePath,
        [string]$LabReason
    )

    $RouteReport = $null
    $RouteHash = $null
    $RouteRef = $null
    if (-not [string]::IsNullOrWhiteSpace($RouteReportPath)) {
        $RouteRef = $RouteReportPath
        $RouteHash = Get-RuntimeAdmissionFileSha256 -Path $RouteReportPath
        $RouteReport = Read-RuntimeAdmissionJsonFile -Path $RouteReportPath
    }

    $TechnicalScope = $null
    $TechnicalScopeHash = $null
    $TechnicalScopeRef = $null
    if (-not [string]::IsNullOrWhiteSpace($TechnicalChangeScopePath)) {
        $TechnicalScopeRef = $TechnicalChangeScopePath
        $TechnicalScopeHash = Get-RuntimeAdmissionFileSha256 -Path $TechnicalChangeScopePath
        $TechnicalScope = Read-RuntimeAdmissionJsonFile -Path $TechnicalChangeScopePath
    }

    $Status = 'blocked'
    $RuntimeAdmitted = $false
    $TechnicalRuntimeAdmitted = $false
    $RuntimeLabAdmitted = $false
    $VisualStatusPromotionAllowed = $false
    $ClaimCeiling = 'documented_visual_route_only'
    $ManualApprovalRequired = $true
    $BlockingStatuses = @()
    $ForbiddenClaims = @('final_visual_delivery', 'premium_visual_claim', 'aaa_visual_claim', 'runtime_validated_visual')
    $EvidenceRefs = @()

    if ($AdmissionType -eq 'production_visual') {
        if ($null -eq $RouteReport) {
            $BlockingStatuses += 'blocked_missing_route_report'
        }
        else {
            $EvidenceRefs += "route_report:$RouteHash"
            foreach ($BlockingStatus in @($RouteReport.blocking_statuses)) {
                $BlockingStatuses += [string]$BlockingStatus
            }
        }

        $BlockingStatuses += 'blocked_no_premium_source'
        $BlockingStatuses += 'blocked_no_human_asset_approval'
        $BlockingStatuses += 'blocked_no_blastem_evidence'
        $ClaimCeiling = 'documented_visual_route_only'
        $ManualApprovalRequired = $true
    }
    elseif ($AdmissionType -eq 'technical') {
        $ManualApprovalRequired = $false
        $ForbiddenClaims = @('visual_status_promotion', 'final_visual_delivery', 'premium_visual_claim')
        $ClaimCeiling = 'technical_runtime_only'

        if ($null -eq $TechnicalScope) {
            $BlockingStatuses += 'blocked_missing_technical_change_scope'
        }
        elseif (Test-TechnicalChangeScopeIsRuntimeOnly -Scope $TechnicalScope) {
            $Status = 'admitted_technical'
            $TechnicalRuntimeAdmitted = $true
            $EvidenceRefs += "technical_scope:$TechnicalScopeHash"
        }
        else {
            $BlockingStatuses += 'blocked_technical_scope_changes_visual_presentation'
        }
    }
    elseif ($AdmissionType -eq 'lab') {
        $Status = 'admitted_lab'
        $RuntimeLabAdmitted = $true
        $ManualApprovalRequired = $false
        $ClaimCeiling = 'lab_not_delivery'
        $ForbiddenClaims = @('visual_status_promotion', 'final_visual_delivery', 'premium_visual_claim', 'runtime_validated_visual')
        if (-not [string]::IsNullOrWhiteSpace($LabReason)) {
            $EvidenceRefs += "lab_reason:$LabReason"
        }
    }

    $UniqueBlockingStatuses = @($BlockingStatuses | Select-Object -Unique)
    if ($UniqueBlockingStatuses.Count -gt 0) {
        $Status = 'blocked'
        if ($AdmissionType -eq 'technical') {
            $TechnicalRuntimeAdmitted = $false
        }
        if ($AdmissionType -eq 'lab') {
            $RuntimeLabAdmitted = $false
        }
    }

    $FingerprintInput = @(
        $AdmissionType,
        [string]$RouteHash,
        [string]$TechnicalScopeHash,
        [string]$LabReason,
        ($UniqueBlockingStatuses -join '|')
    ) -join '|'

    return [pscustomobject][ordered]@{
        schema_version = '1.0.0'
        report_kind = 'runtime_admission_report'
        generated_at = (Get-Date).ToUniversalTime().ToString('o')
        admission_type = $AdmissionType
        status = $Status
        runtime_admitted = [bool]$RuntimeAdmitted
        technical_runtime_admitted = [bool]$TechnicalRuntimeAdmitted
        runtime_lab_admitted = [bool]$RuntimeLabAdmitted
        visual_status_promotion_allowed = [bool]$VisualStatusPromotionAllowed
        claim_ceiling = $ClaimCeiling
        manual_approval_required = [bool]$ManualApprovalRequired
        route_report_ref = $RouteRef
        route_report_sha256 = $RouteHash
        technical_change_scope_ref = $TechnicalScopeRef
        technical_change_scope_sha256 = $TechnicalScopeHash
        lab_reason = $(if ([string]::IsNullOrWhiteSpace($LabReason)) { $null } else { $LabReason })
        input_fingerprint = (ConvertTo-RuntimeAdmissionSha256 -Text $FingerprintInput)
        blocking_statuses = @($UniqueBlockingStatuses)
        forbidden_claims = @($ForbiddenClaims)
        evidence_refs = @($EvidenceRefs)
    }
}

Export-ModuleMember -Function `
    Get-RuntimeAdmissionFileSha256, `
    ConvertTo-RuntimeAdmissionSha256, `
    Read-RuntimeAdmissionJsonFile, `
    Test-TechnicalChangeScopeIsRuntimeOnly, `
    New-RuntimeAdmissionReport
