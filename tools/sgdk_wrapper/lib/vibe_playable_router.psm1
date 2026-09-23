function ConvertTo-VibePlayableFoldedText {
    param([string]$Text)

    if ([string]::IsNullOrWhiteSpace($Text)) {
        return ''
    }

    $Normalized = $Text.Normalize([System.Text.NormalizationForm]::FormD)
    $Builder = New-Object System.Text.StringBuilder
    foreach ($Character in $Normalized.ToCharArray()) {
        $Category = [System.Globalization.CharUnicodeInfo]::GetUnicodeCategory($Character)
        if ($Category -ne [System.Globalization.UnicodeCategory]::NonSpacingMark) {
            [void]$Builder.Append($Character)
        }
    }

    $Folded = $Builder.ToString().Normalize([System.Text.NormalizationForm]::FormC).ToLowerInvariant()
    $Folded = $Folded -replace '[^a-z0-9_ -]+', ' '
    $Folded = $Folded -replace '\s+', ' '
    return $Folded.Trim()
}

function Read-VibePlayableIntentRules {
    param([string]$RulesPath)

    if ([string]::IsNullOrWhiteSpace($RulesPath)) {
        $RulesPath = Join-Path $PSScriptRoot '..\.agent\references\vibe_playable_intent_rules.json'
    }

    $ResolvedRulesPath = (Resolve-Path -LiteralPath $RulesPath).Path
    return Get-Content -Raw -LiteralPath $ResolvedRulesPath | ConvertFrom-Json
}

function Test-VibePlayableKeywordMatch {
    param(
        [string]$NormalizedText,
        [string]$Keyword
    )

    if ([string]::IsNullOrWhiteSpace($Keyword)) {
        return $false
    }

    $FoldedKeyword = ConvertTo-VibePlayableFoldedText -Text $Keyword
    $EscapedKeyword = [regex]::Escape($FoldedKeyword)
    return [regex]::IsMatch($NormalizedText, "(^|[^a-z0-9_])$EscapedKeyword([^a-z0-9_]|$)")
}

function Get-VibePlayableIntentMatches {
    param(
        [string]$RequestText,
        [object]$Rules
    )

    $NormalizedText = ConvertTo-VibePlayableFoldedText -Text $RequestText
    $Matches = @()

    foreach ($Rule in @($Rules.rules)) {
        $MatchedTerms = @()
        foreach ($Keyword in @($Rule.keywords_any)) {
            if (Test-VibePlayableKeywordMatch -NormalizedText $NormalizedText -Keyword $Keyword) {
                $MatchedTerms += [string]$Keyword
            }
        }

        if ($MatchedTerms.Count -gt 0) {
            $Matches += [pscustomobject]@{
                rule = $Rule
                rule_id = [string]$Rule.rule_id
                language = [string]$Rule.language
                intent = [string]$Rule.intent
                confidence = [double]$Rule.confidence
                matched_terms = @($MatchedTerms)
            }
        }
    }

    return @($Matches)
}

function Get-VibePlayableDetectedLanguage {
    param([object[]]$Matches)

    if ($Matches.Count -eq 0) {
        return 'unknown'
    }

    $Portuguese = @($Matches | Where-Object { $_.language -eq 'pt' }).Count
    $English = @($Matches | Where-Object { $_.language -eq 'en' }).Count

    if ($Portuguese -ge $English) {
        return 'pt'
    }

    return 'en'
}

function Get-VibePlayableTargetId {
    param(
        [string]$Type,
        [string]$Role
    )

    switch ($Type) {
        'scene' { return 'target_scene_playable_stage' }
        'player_character' { return 'target_player_hero' }
        'boss' { return 'target_boss_primary' }
        'ui' { return 'target_ui_player_facing' }
        'fx' { return 'target_fx_motion_or_action' }
        'unknown_visual' { return 'target_unknown_visual_request' }
        default {
            $SafeRole = ConvertTo-VibePlayableFoldedText -Text $Role
            $SafeRole = $SafeRole -replace '[^a-z0-9]+', '_'
            $SafeRole = $SafeRole.Trim('_')
            if ([string]::IsNullOrWhiteSpace($SafeRole)) {
                $SafeRole = 'primary'
            }
            return "target_${Type}_$SafeRole"
        }
    }
}

function Get-VibePlayableDetectedTargets {
    param([object[]]$Matches)

    $TargetMap = [ordered]@{}

    foreach ($Match in @($Matches)) {
        $Template = $Match.rule.target_template
        if ($null -eq $Template) {
            continue
        }

        $TargetId = Get-VibePlayableTargetId -Type ([string]$Template.type) -Role ([string]$Template.role)
        if (-not $TargetMap.Contains($TargetId)) {
            $TargetMap[$TargetId] = [pscustomobject]@{
                target_id = $TargetId
                type = [string]$Template.type
                role = [string]$Template.role
                criticality = [string]$Template.criticality
                actions_requested = @([string]$Match.intent)
                animation_required = [bool]$Template.animation_required
                assets = @($Template.assets | ForEach-Object { [string]$_ })
                owners = @($Template.owners | ForEach-Object { [string]$_ })
            }
        }
        elseif (@($TargetMap[$TargetId].actions_requested) -notcontains [string]$Match.intent) {
            $TargetMap[$TargetId].actions_requested += [string]$Match.intent
        }
    }

    $Targets = @()
    foreach ($Key in $TargetMap.Keys) {
        $Targets += $TargetMap[$Key]
    }

    return @($Targets)
}

function Get-VibePlayableRequiredOwners {
    param(
        [object]$Rules,
        [bool]$VisualRouteRequired
    )

    if (-not $VisualRouteRequired) {
        return @()
    }

    return @($Rules.owner_order | ForEach-Object { [string]$_ })
}

function New-VibePlayableCompactContext {
    param([object]$RouteCore)

    return [pscustomobject][ordered]@{
        schema_version = $RouteCore.schema_version
        report_kind = 'vibe_playable_compact_context'
        visual_route_required = [bool]$RouteCore.visual_route_required
        runtime_open_allowed = [bool]$RouteCore.runtime_open_allowed
        detected_intents = @($RouteCore.detected_intents)
        detected_targets = @($RouteCore.detected_targets)
        required_owners = @($RouteCore.required_owners)
        dispatch = $RouteCore.dispatch
        blocking_statuses = @($RouteCore.blocking_statuses)
        forbidden_claims_until_evidence = @($RouteCore.forbidden_claims_until_evidence)
    }
}

function New-VibePlayableRouteReport {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RequestText,
        [string]$ProjectRoot,
        [switch]$SkipGraphify,
        [string]$RulesPath
    )

    $Rules = Read-VibePlayableIntentRules -RulesPath $RulesPath
    $NormalizedText = ConvertTo-VibePlayableFoldedText -Text $RequestText
    $Matches = @(Get-VibePlayableIntentMatches -RequestText $RequestText -Rules $Rules)
    $DetectedTargets = @(Get-VibePlayableDetectedTargets -Matches $Matches)
    $Ambiguous = ($Matches.Count -eq 0 -and -not [string]::IsNullOrWhiteSpace($RequestText))

    if ($Ambiguous) {
        $DetectedTargets = @(
            [pscustomobject]@{
                target_id = 'target_unknown_visual_request'
                type = 'unknown_visual'
                role = 'ambiguous_player_facing_request'
                criticality = 'critical'
                actions_requested = @('ambiguous_visual_safety_fallback')
                animation_required = $false
                assets = @('direction_brief_required')
                owners = @('skills/art/art-direction-selector', 'skills/art/art-asset-diagnostic')
            }
        )
    }

    $VisualRouteRequired = ($Matches.Count -gt 0 -or $Ambiguous)
    $RequiredOwners = @(Get-VibePlayableRequiredOwners -Rules $Rules -VisualRouteRequired $VisualRouteRequired)

    $DetectedIntents = @()
    $MatchedRules = @()
    foreach ($Match in $Matches) {
        $DetectedIntents += [pscustomobject][ordered]@{
            intent = [string]$Match.intent
            confidence = [double]$Match.confidence
            rule_id = [string]$Match.rule_id
            matched_terms = @($Match.matched_terms | ForEach-Object { [string]$_ })
        }
        $MatchedRules += [pscustomobject][ordered]@{
            rule_id = [string]$Match.rule_id
            intent = [string]$Match.intent
            confidence = [double]$Match.confidence
            matched_terms = @($Match.matched_terms | ForEach-Object { [string]$_ })
        }
    }

    $IntentConfidence = 0.0
    if ($Matches.Count -gt 0) {
        $IntentConfidence = [math]::Round((($Matches | Measure-Object -Property confidence -Average).Average), 2)
    }

    $RuntimeOpenAllowed = -not $VisualRouteRequired
    $RuntimeStatus = 'technical_runtime_candidate'
    $RuntimeReason = 'no_player_facing_visual_route_detected'
    $BlockingStatuses = @()
    $ForbiddenClaims = @()

    if ($VisualRouteRequired) {
        $RuntimeOpenAllowed = $false
        $RuntimeStatus = 'blocked_visual_route_required'
        $RuntimeReason = 'player_facing request requires visual direction, source, approval, VDP translation and BlastEm evidence before production runtime'
        $BlockingStatuses = @(
            'blocked_visual_route_required',
            'blocked_no_premium_source',
            'blocked_no_human_asset_approval',
            'blocked_no_blastem_evidence'
        )
        $ForbiddenClaims = @(
            'final_visual_delivery',
            'premium_visual_claim',
            'aaa_visual_claim',
            'runtime_validated_visual'
        )
    }

    $DispatchMode = 'no_visual_dispatch'
    if ($VisualRouteRequired) {
        $DispatchMode = 'explicit_router_dispatch'
    }

    $GraphifyMode = 'consultative_cache_or_timeout'
    $GraphifyTimeout = 15
    if ($SkipGraphify) {
        $GraphifyMode = 'skipped_by_test'
        $GraphifyTimeout = 0
    }

    $RouteCore = [pscustomobject][ordered]@{
        schema_version = '1.0.0'
        report_kind = 'vibe_playable_route_report'
        generated_at = (Get-Date).ToUniversalTime().ToString('o')
        input_text = [string]$RequestText
        normalized_input = [string]$NormalizedText
        detected_language = (Get-VibePlayableDetectedLanguage -Matches $Matches)
        detected_intents = @($DetectedIntents)
        intent_confidence = [double]$IntentConfidence
        matched_rules = @($MatchedRules)
        ambiguity_fallback = [pscustomobject][ordered]@{
            used = [bool]$Ambiguous
            reason = $(if ($Ambiguous) { 'no_rule_matched_non_empty_request' } else { 'deterministic_rules_matched_or_empty_request' })
        }
        ambiguity_status = $(if ($Ambiguous) { 'ambiguous_visual_safety_fallback' } else { 'resolved_by_deterministic_rules' })
        fallback_decision = $(if ($Ambiguous) { 'block_runtime_until_human_direction_classification' } else { 'use_matched_rules' })
        visual_route_required = [bool]$VisualRouteRequired
        runtime_open_allowed = [bool]$RuntimeOpenAllowed
        technical_runtime_candidate = [bool](-not $VisualRouteRequired)
        detected_targets = @($DetectedTargets)
        required_owners = @($RequiredOwners)
        dispatch = [pscustomobject][ordered]@{
            mode = $DispatchMode
            art_direction_selector_lifecycle = [pscustomobject][ordered]@{
                allow_implicit_invocation = $false
                activation_method = $(if ($VisualRouteRequired) { 'explicit_router_dispatch' } else { 'not_activated' })
                reason = 'art-direction-selector remains non-implicit; vibe_playable router records deterministic activation when player-facing visuals are detected'
            }
            owner = $(if ($VisualRouteRequired) { 'skills/art/art-direction-selector' } else { '' })
        }
        runtime_admission = [pscustomobject][ordered]@{
            status = $RuntimeStatus
            reason = $RuntimeReason
            runtime_admitted = $false
            technical_runtime_admitted = [bool](-not $VisualRouteRequired)
            runtime_lab_admitted = $false
        }
        graphify = [pscustomobject][ordered]@{
            required_for_routing = $false
            mode = $GraphifyMode
            timeout_seconds = $GraphifyTimeout
            degradation = 'canonical_files_remain_authoritative'
        }
        blocking_statuses = @($BlockingStatuses)
        forbidden_claims_until_evidence = @($ForbiddenClaims)
    }

    $CompactContext = New-VibePlayableCompactContext -RouteCore $RouteCore
    $CompactJson = $CompactContext | ConvertTo-Json -Depth 100 -Compress
    $CompactBytes = [System.Text.Encoding]::UTF8.GetByteCount($CompactJson)

    return [pscustomobject][ordered]@{
        schema_version = $RouteCore.schema_version
        report_kind = $RouteCore.report_kind
        generated_at = $RouteCore.generated_at
        input_text = $RouteCore.input_text
        normalized_input = $RouteCore.normalized_input
        detected_language = $RouteCore.detected_language
        detected_intents = @($RouteCore.detected_intents)
        intent_confidence = $RouteCore.intent_confidence
        matched_rules = @($RouteCore.matched_rules)
        ambiguity_fallback = $RouteCore.ambiguity_fallback
        ambiguity_status = $RouteCore.ambiguity_status
        fallback_decision = $RouteCore.fallback_decision
        visual_route_required = $RouteCore.visual_route_required
        runtime_open_allowed = $RouteCore.runtime_open_allowed
        technical_runtime_candidate = $RouteCore.technical_runtime_candidate
        detected_targets = @($RouteCore.detected_targets)
        required_owners = @($RouteCore.required_owners)
        dispatch = $RouteCore.dispatch
        compact_context = $CompactContext
        compact_context_bytes = $CompactBytes
        runtime_admission = $RouteCore.runtime_admission
        graphify = $RouteCore.graphify
        blocking_statuses = @($RouteCore.blocking_statuses)
        forbidden_claims_until_evidence = @($RouteCore.forbidden_claims_until_evidence)
    }
}

Export-ModuleMember -Function `
    ConvertTo-VibePlayableFoldedText, `
    Read-VibePlayableIntentRules, `
    Get-VibePlayableIntentMatches, `
    Get-VibePlayableDetectedLanguage, `
    Get-VibePlayableDetectedTargets, `
    Get-VibePlayableRequiredOwners, `
    New-VibePlayableCompactContext, `
    New-VibePlayableRouteReport
