function Test-PremiumManifestProperty {
    param(
        [object]$Object,
        [string]$Name
    )

    return ($null -ne $Object -and $null -ne $Object.PSObject.Properties[$Name])
}

function Get-PremiumManifestProperty {
    param(
        [object]$Object,
        [string]$Name,
        $DefaultValue = $null
    )

    if (Test-PremiumManifestProperty -Object $Object -Name $Name) {
        return $Object.PSObject.Properties[$Name].Value
    }

    return $DefaultValue
}

function Get-PremiumManifestString {
    param(
        [object]$Object,
        [string]$Name,
        [string]$DefaultValue = ''
    )

    $Value = Get-PremiumManifestProperty -Object $Object -Name $Name -DefaultValue $DefaultValue
    if ($null -eq $Value) {
        return $DefaultValue
    }

    return [string]$Value
}

function ConvertTo-PremiumManifestArray {
    param($Value)

    if ($null -eq $Value) {
        return @()
    }

    return @($Value)
}

function Test-PremiumManifestSha256 {
    param([string]$Value)

    if ([string]::IsNullOrWhiteSpace($Value)) {
        return $false
    }

    return ($Value -match '^[a-fA-F0-9]{64}$')
}

function Read-PremiumSourceManifest {
    param([Parameter(Mandatory = $true)][string]$ManifestPath)

    $ResolvedPath = (Resolve-Path -LiteralPath $ManifestPath).Path
    return Get-Content -Raw -LiteralPath $ResolvedPath | ConvertFrom-Json
}

function Get-PremiumSourceManifestCompatibilityMode {
    param([object]$Manifest)

    $ReportKind = Get-PremiumManifestString -Object $Manifest -Name 'report_kind'
    $SchemaVersion = Get-PremiumManifestString -Object $Manifest -Name 'schema_version'

    if ($ReportKind -eq 'premium_source_manifest' -or $SchemaVersion -match '^2\.') {
        return 'v2'
    }

    if (Test-PremiumManifestProperty -Object $Manifest -Name 'assets') {
        return 'v1_root_assets'
    }

    if (
        (Test-PremiumManifestProperty -Object $Manifest -Name 'asset_id') -and
        (Test-PremiumManifestProperty -Object $Manifest -Name 'source_file') -and
        (Test-PremiumManifestProperty -Object $Manifest -Name 'source_sha256')
    ) {
        return 'v1_single_asset'
    }

    throw 'premium_source_manifest shape is not recognized'
}

function ConvertTo-LegacyPremiumAsset {
    param([object]$Asset)

    $AssetId = Get-PremiumManifestString -Object $Asset -Name 'asset_id' -DefaultValue 'legacy_unknown_asset'
    $AssetRole = Get-PremiumManifestString -Object $Asset -Name 'asset_role' -DefaultValue 'unknown'
    $Criticality = Get-PremiumManifestString -Object $Asset -Name 'criticality' -DefaultValue 'critical'
    $SourceFile = Get-PremiumManifestString -Object $Asset -Name 'source_file'
    $SourceHash = Get-PremiumManifestString -Object $Asset -Name 'source_sha256'
    $Author = Get-PremiumManifestString -Object $Asset -Name 'author' -DefaultValue 'unknown'
    $License = Get-PremiumManifestString -Object $Asset -Name 'license' -DefaultValue 'unknown'

    return [pscustomobject][ordered]@{
        asset_id = $AssetId
        asset_role = $AssetRole
        criticality = $Criticality
        authoring_method = 'unknown'
        source_origin = 'legacy_manifest'
        source_classification = 'unknown'
        tool = [pscustomobject][ordered]@{
            name = 'legacy_unknown'
            version = 'unknown'
            model = $null
        }
        source_files = @(
            [pscustomobject][ordered]@{
                path = $SourceFile
                sha256 = $SourceHash
                role = 'source'
            }
        )
        transformations = @()
        variants = [pscustomobject][ordered]@{
            basic = $null
            elite = $null
        }
        license = [pscustomobject][ordered]@{
            name = $License
            author = $Author
            usage = 'legacy_requires_reapproval'
        }
    }
}

function ConvertTo-CanonicalPremiumAsset {
    param([object]$Asset)

    $Tool = Get-PremiumManifestProperty -Object $Asset -Name 'tool'
    if ($null -eq $Tool) {
        $Tool = [pscustomobject]@{ name = 'unknown'; version = 'unknown'; model = $null }
    }

    $SourceFiles = @()
    foreach ($SourceFile in (ConvertTo-PremiumManifestArray -Value (Get-PremiumManifestProperty -Object $Asset -Name 'source_files'))) {
        $SourceFiles += [pscustomobject][ordered]@{
            path = (Get-PremiumManifestString -Object $SourceFile -Name 'path')
            sha256 = (Get-PremiumManifestString -Object $SourceFile -Name 'sha256')
            role = (Get-PremiumManifestString -Object $SourceFile -Name 'role' -DefaultValue 'source')
        }
    }

    $Transformations = @()
    foreach ($Transformation in (ConvertTo-PremiumManifestArray -Value (Get-PremiumManifestProperty -Object $Asset -Name 'transformations'))) {
        $Transformations += [pscustomobject][ordered]@{
            step = (Get-PremiumManifestString -Object $Transformation -Name 'step')
            tool = (Get-PremiumManifestString -Object $Transformation -Name 'tool')
            input_sha256 = (Get-PremiumManifestString -Object $Transformation -Name 'input_sha256')
            output_sha256 = (Get-PremiumManifestString -Object $Transformation -Name 'output_sha256')
            notes = (Get-PremiumManifestString -Object $Transformation -Name 'notes')
        }
    }

    return [pscustomobject][ordered]@{
        asset_id = (Get-PremiumManifestString -Object $Asset -Name 'asset_id')
        asset_role = (Get-PremiumManifestString -Object $Asset -Name 'asset_role' -DefaultValue 'unknown')
        criticality = (Get-PremiumManifestString -Object $Asset -Name 'criticality' -DefaultValue 'critical')
        authoring_method = (Get-PremiumManifestString -Object $Asset -Name 'authoring_method' -DefaultValue 'unknown')
        source_origin = (Get-PremiumManifestString -Object $Asset -Name 'source_origin' -DefaultValue 'unknown')
        source_classification = (Get-PremiumManifestString -Object $Asset -Name 'source_classification' -DefaultValue 'unknown')
        tool = [pscustomobject][ordered]@{
            name = (Get-PremiumManifestString -Object $Tool -Name 'name' -DefaultValue 'unknown')
            version = (Get-PremiumManifestString -Object $Tool -Name 'version' -DefaultValue 'unknown')
            model = (Get-PremiumManifestProperty -Object $Tool -Name 'model' -DefaultValue $null)
        }
        source_files = @($SourceFiles)
        transformations = @($Transformations)
        variants = (Get-PremiumManifestProperty -Object $Asset -Name 'variants')
        license = (Get-PremiumManifestProperty -Object $Asset -Name 'license')
    }
}

function ConvertTo-PremiumSourceManifestV2 {
    param([Parameter(Mandatory = $true)][object]$Manifest)

    $CompatibilityMode = Get-PremiumSourceManifestCompatibilityMode -Manifest $Manifest
    $Assets = @()
    $ProductionSourceReady = $false

    if ($CompatibilityMode -eq 'v2') {
        $ProductionSourceReady = [bool](Get-PremiumManifestProperty -Object $Manifest -Name 'production_source_ready' -DefaultValue $false)
        foreach ($Asset in (ConvertTo-PremiumManifestArray -Value (Get-PremiumManifestProperty -Object $Manifest -Name 'assets'))) {
            $Assets += ConvertTo-CanonicalPremiumAsset -Asset $Asset
        }
    }
    elseif ($CompatibilityMode -eq 'v1_root_assets') {
        foreach ($Asset in (ConvertTo-PremiumManifestArray -Value (Get-PremiumManifestProperty -Object $Manifest -Name 'assets'))) {
            $Assets += ConvertTo-LegacyPremiumAsset -Asset $Asset
        }
    }
    else {
        $Assets += ConvertTo-LegacyPremiumAsset -Asset $Manifest
    }

    return [pscustomobject][ordered]@{
        schema_version = '2.0.0'
        report_kind = 'premium_source_manifest'
        compatibility_mode = $CompatibilityMode
        production_source_ready = [bool]$ProductionSourceReady
        asset_count = @($Assets).Count
        assets = @($Assets)
    }
}

function Test-PremiumSourceManifest {
    param(
        [Parameter(Mandatory = $true)][object]$Manifest,
        [string]$ManifestPath = ''
    )

    $Normalized = ConvertTo-PremiumSourceManifestV2 -Manifest $Manifest
    $Blockers = @()
    $AllowedClassifications = @('human_authored', 'generated_bitmap', 'licensed_source', 'procedural_debug', 'unknown')

    foreach ($Asset in @($Normalized.assets)) {
        $IsCritical = ([string]$Asset.criticality -eq 'critical')
        $Classification = [string]$Asset.source_classification

        if ($AllowedClassifications -notcontains $Classification) {
            $Blockers += 'blocked_unknown_source_classification'
        }

        if ($IsCritical -and $Classification -eq 'unknown') {
            $Blockers += 'blocked_unknown_source_classification'
        }

        if ($IsCritical -and $Classification -eq 'procedural_debug') {
            $Blockers += 'blocked_procedural_debug_critical_asset'
        }

        if ($IsCritical -and @($Asset.source_files).Count -eq 0) {
            $Blockers += 'blocked_missing_source_files'
        }

        foreach ($SourceFile in @($Asset.source_files)) {
            if ([string]::IsNullOrWhiteSpace([string]$SourceFile.path) -or -not (Test-PremiumManifestSha256 -Value ([string]$SourceFile.sha256))) {
                $Blockers += 'blocked_missing_source_hash'
            }
        }
    }

    $UniqueBlockers = @($Blockers | Select-Object -Unique)
    $Status = 'passed'
    if ($UniqueBlockers.Count -gt 0) {
        $Status = 'blocked'
    }

    $EffectiveReady = ([bool]$Normalized.production_source_ready -and $Status -eq 'passed')

    return [pscustomobject][ordered]@{
        schema_version = '1.0.0'
        report_kind = 'premium_source_manifest_validation_report'
        manifest_path = $ManifestPath
        compatibility_mode = $Normalized.compatibility_mode
        status = $Status
        declared_production_source_ready = [bool]$Normalized.production_source_ready
        effective_production_source_ready = [bool]$EffectiveReady
        blockers = @($UniqueBlockers)
        normalized = [pscustomobject][ordered]@{
            schema_version = $Normalized.schema_version
            report_kind = $Normalized.report_kind
            production_source_ready = [bool]$Normalized.production_source_ready
            asset_count = [int]$Normalized.asset_count
            assets = @($Normalized.assets)
        }
    }
}

function Test-PremiumSourceManifestFile {
    param([Parameter(Mandatory = $true)][string]$ManifestPath)

    $Manifest = Read-PremiumSourceManifest -ManifestPath $ManifestPath
    return Test-PremiumSourceManifest -Manifest $Manifest -ManifestPath $ManifestPath
}

Export-ModuleMember -Function `
    Read-PremiumSourceManifest, `
    Get-PremiumSourceManifestCompatibilityMode, `
    ConvertTo-PremiumSourceManifestV2, `
    Test-PremiumSourceManifest, `
    Test-PremiumSourceManifestFile
