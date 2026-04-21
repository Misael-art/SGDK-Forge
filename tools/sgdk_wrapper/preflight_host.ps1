<#
.SYNOPSIS
  Verifica pre-requisitos do host Windows antes de build SGDK (Java, make, GDK, ferramentas opcionais).

.DESCRIPTION
  Exit codes:
    0 - Todos os checks obrigatorios OK (avisos opcionais podem ter sido impressos).
    1 - Falha obrigatoria (GDK/make/java ou MD_ROOT invalido).
    2 - Apenas avisos fortes (ex.: Python/Magick ausentes para validador estetico).

  Alinhado a env.bat (RESOLVE_GDK) e validate_resources.ps1 (Python/Magick nao-WindowsApps).

.PARAMETER RepoRoot
  Raiz do monorepo MegaDrive_DEV. Por omissao: avo de tools/sgdk_wrapper (este script).
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$RepoRoot = "",

    [Parameter(Mandatory = $false)]
    [string]$ProjectRoot = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "_lib\sgdk_common.ps1")

function Write-PreflightLog {
    param([string]$Level, [string]$Message)
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host ("[{0}] [{1}] {2}" -f $ts, $Level, $Message)
}

function Test-CommandExists {
    param([string]$Name)
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

function Resolve-MegaDriveRoot {
    param([string]$ExplicitRoot)
    if (-not [string]::IsNullOrWhiteSpace($ExplicitRoot)) {
        return [System.IO.Path]::GetFullPath($ExplicitRoot)
    }
    $wrapperDirInfo = [System.IO.DirectoryInfo]$PSScriptRoot
    $toolsDirInfo = $wrapperDirInfo.Parent
    $rootDirInfo = $toolsDirInfo.Parent
    return [System.IO.Path]::GetFullPath($rootDirInfo.FullName)
}

function Resolve-GdkPath {
    param([string]$MdRoot)
    $localGdk = Join-Path $MdRoot "sdk\sgdk-2.11"
    $candidates = @()
    if ($env:GDK -and (Test-Path -LiteralPath $env:GDK)) { $candidates += $env:GDK }
    if ($env:GDK_WIN -and (Test-Path -LiteralPath $env:GDK_WIN)) { $candidates += $env:GDK_WIN }
    $candidates += $localGdk
    $candidates += (Join-Path $env:USERPROFILE "sgdk\sgdk-2.11")
    $candidates += "C:\SGDK\sgdk-2.11"
    $candidates += "C:\sgdk\sgdk-2.11"
    foreach ($c in $candidates) {
        if (-not $c) { continue }
        $gen = Join-Path $c "makefile.gen"
        if (Test-Path -LiteralPath $gen -PathType Leaf) {
            return $c
        }
    }
    return $localGdk
}

function Get-UsablePythonPath {
    return SGDK_GetPythonPath
}

function Get-MagickPathResolved {
    return SGDK_GetMagickPath
}

$blockingFailures = 0
$softWarnings = 0
$lintWarnings = 0
$strictErrors = 0

$script:strictPromotableLints = @('dma-queue', 'center-magic')
$script:strictModeEnabled = $false
$strictEnvValue = $env:SGDK_LINT_STRICT
if ($null -ne $strictEnvValue) {
    $normalized = ($strictEnvValue.ToString()).Trim().ToLowerInvariant()
    if ($normalized -in @('1','true','yes','on')) {
        $script:strictModeEnabled = $true
    }
}

function Write-LintWarning {
    param(
        [Parameter(Mandatory = $true)][string]$LintId,
        [Parameter(Mandatory = $true)][string]$Message
    )
    $script:lintWarnings++
    Write-PreflightLog "WARN" ("lint:{0}: {1}" -f $LintId, $Message)
    if ($script:strictModeEnabled -and ($script:strictPromotableLints -contains $LintId)) {
        $script:strictErrors++
    }
}

function Get-NamedFunctionBodies {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(Mandatory = $true)][string]$NameSuffixRegex
    )
    $bodies = @()
    try {
        $content = [System.IO.File]::ReadAllText($FilePath)
    } catch {
        return $bodies
    }
    if ([string]::IsNullOrEmpty($content)) { return $bodies }

    $pattern = '(?m)\b\w*' + $NameSuffixRegex + '\s*\(\s*void\s*\)\s*\{'
    $regex = [regex]::new($pattern)
    foreach ($match in $regex.Matches($content)) {
        $openBraceIdx = $match.Index + $match.Length - 1
        $depth = 1
        $i = $openBraceIdx + 1
        while ($i -lt $content.Length -and $depth -gt 0) {
            $ch = $content[$i]
            if ($ch -eq '{') { $depth++ }
            elseif ($ch -eq '}') { $depth-- }
            $i++
        }
        if ($depth -eq 0) {
            $bodyLen = [Math]::Max(0, ($i - 1) - ($openBraceIdx + 1))
            $bodies += $content.Substring($openBraceIdx + 1, $bodyLen)
        }
    }
    return $bodies
}

function Get-ProjectCodeFiles {
    param([string]$Root)

    if ([string]::IsNullOrWhiteSpace($Root)) { return @() }
    if (-not (Test-Path -LiteralPath $Root -PathType Container)) { return @() }

    $srcDir = Join-Path $Root "src"
    $incDir = Join-Path $Root "inc"
    $dirs = @()
    if (Test-Path -LiteralPath $srcDir -PathType Container) { $dirs += $srcDir }
    if (Test-Path -LiteralPath $incDir -PathType Container) { $dirs += $incDir }
    if ($dirs.Count -eq 0) { return @() }

    $files = @()
    foreach ($d in $dirs) {
        $files += @(Get-ChildItem -LiteralPath $d -Recurse -File -Include *.c, *.h -ErrorAction SilentlyContinue)
    }
    return $files | Select-Object -ExpandProperty FullName
}

function Get-RelPath {
    param([string]$Base, [string]$Path)
    try {
        $baseFull = [System.IO.Path]::GetFullPath($Base)
        $pathFull = [System.IO.Path]::GetFullPath($Path)
        if ($pathFull.StartsWith($baseFull, [System.StringComparison]::OrdinalIgnoreCase)) {
            return $pathFull.Substring($baseFull.Length).TrimStart('\', '/')
        }
        return $pathFull
    } catch {
        return $Path
    }
}

function Invoke-ProjectLints {
    param([string]$Root)

    $files = Get-ProjectCodeFiles -Root $Root
    if ($files.Count -eq 0) { return }

    $disableAll = Select-String -Path $files -Pattern "SGDK_WRAPPER_LINT_DISABLE_ALL" -SimpleMatch -Quiet -ErrorAction SilentlyContinue
    if ($disableAll) { return }

    $yOutOfSafeAreaRegex = 'VDP_drawText\s*\(\s*[^,]+,\s*[^,]+,\s*(\d+)\s*\)'
    foreach ($hit in @(Select-String -Path $files -Pattern $yOutOfSafeAreaRegex -AllMatches -ErrorAction SilentlyContinue)) {
        foreach ($m in $hit.Matches) {
            if ($hit.Line -match "SGDK_WRAPPER_LINT_DISABLE_TEXT_SAFEAREA") { continue }
            if ($hit.Line -match "SGDK_WRAPPER_LINT_DISABLE_HUD_ROW_28") { continue }
            $y = [int]$m.Groups[1].Value
            if ($y -ge 28) {
                $rel = Get-RelPath -Base $Root -Path $hit.Path
                Write-LintWarning -LintId 'text-safearea' -Message (("{0}:{1} VDP_drawText y={2} (224p => linhas 0..27)" -f $rel, $hit.LineNumber, $y))
            }
        }
    }

    $yFillOutOfSafeAreaRegex = 'VDP_drawTextFill\s*\(\s*[^,]+,\s*[^,]+,\s*(\d+)\s*,\s*[^,\)]+\)'
    foreach ($hit in @(Select-String -Path $files -Pattern $yFillOutOfSafeAreaRegex -AllMatches -ErrorAction SilentlyContinue)) {
        foreach ($m in $hit.Matches) {
            if ($hit.Line -match "SGDK_WRAPPER_LINT_DISABLE_TEXT_SAFEAREA") { continue }
            if ($hit.Line -match "SGDK_WRAPPER_LINT_DISABLE_HUD_ROW_28") { continue }
            $y = [int]$m.Groups[1].Value
            if ($y -ge 28) {
                $rel = Get-RelPath -Base $Root -Path $hit.Path
                Write-LintWarning -LintId 'hud-row-28' -Message (("{0}:{1} VDP_drawTextFill y={2} (linha proibida)" -f $rel, $hit.LineNumber, $y))
            }
        }
    }

    $drawTextWithPercentRegex = 'VDP_drawText\s*\(\s*\"[^\"]*%[^\"]*\"'
    foreach ($hit in @(Select-String -Path $files -Pattern $drawTextWithPercentRegex -ErrorAction SilentlyContinue)) {
        if ($hit.Line -match "SGDK_WRAPPER_LINT_DISABLE_DRAWTEXT_FORMAT") { continue }
        $rel = Get-RelPath -Base $Root -Path $hit.Path
        Write-LintWarning -LintId 'drawtext-format' -Message (("{0}:{1} string literal contem '%'" -f $rel, $hit.LineNumber))
    }

    $sprintfHits = @(Select-String -Path $files -Pattern '\bsprintf\s*\(' -List -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Path)
    $drawTextHits = @(Select-String -Path $files -Pattern '\bVDP_drawText\s*\(' -List -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Path)
    $drawTextFillHits = @(Select-String -Path $files -Pattern '\bVDP_drawTextFill\s*\(' -List -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Path)
    $clearTextHits = @(Select-String -Path $files -Pattern '\bVDP_clearTextArea\s*\(' -List -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Path)
    $possibleGarbage = $sprintfHits | Where-Object { $drawTextHits -contains $_ } | Where-Object { ($drawTextFillHits -notcontains $_) -and ($clearTextHits -notcontains $_) }
    foreach ($p in $possibleGarbage | Select-Object -Unique) {
        $contentHasDisable = Select-String -Path $p -Pattern "SGDK_WRAPPER_LINT_DISABLE_OVERLAY_GARBAGE" -SimpleMatch -Quiet -ErrorAction SilentlyContinue
        if ($contentHasDisable) { continue }
        $rel = Get-RelPath -Base $Root -Path $p
        Write-LintWarning -LintId 'overlay-garbage' -Message (("{0} (sprintf + VDP_drawText sem Fill/ClearTextArea)" -f $rel))
    }

    foreach ($file in $files) {
        $disableFile = Select-String -Path $file -Pattern "SGDK_WRAPPER_LINT_DISABLE_DRAWTEXT_IN_UPDATE" -SimpleMatch -Quiet -ErrorAction SilentlyContinue
        if ($disableFile) { continue }
        $updateBodies = Get-NamedFunctionBodies -FilePath $file -NameSuffixRegex 'Update'
        foreach ($body in $updateBodies) {
            if ($body -match 'SGDK_WRAPPER_LINT_DISABLE_DRAWTEXT_IN_UPDATE') { continue }
            $hasSprintf = ($body -match '\bsprintf\s*\(')
            $hasDrawText = ($body -match '\bVDP_drawText\s*\(')
            $hasDrawFill = ($body -match '\bVDP_drawTextFill\s*\(')
            $hasClearArea = ($body -match '\bVDP_clearTextArea\s*\(')
            if ($hasSprintf -and $hasDrawText -and (-not $hasDrawFill) -and (-not $hasClearArea)) {
                $rel = Get-RelPath -Base $Root -Path $file
                Write-LintWarning -LintId 'drawText-in-update' -Message (("{0} sprintf+VDP_drawText dentro de *Update* sem Fill/ClearTextArea" -f $rel))
            }
        }
    }

    $dmaQueueHits = @(Select-String -Path $files -Pattern '\bDMA_QUEUE\b' -List -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Path)
    foreach ($p in $dmaQueueHits | Select-Object -Unique) {
        $contentHasDisable = Select-String -Path $p -Pattern "SGDK_WRAPPER_LINT_DISABLE_DMA_QUEUE" -SimpleMatch -Quiet -ErrorAction SilentlyContinue
        if ($contentHasDisable) { continue }
        $rel = Get-RelPath -Base $Root -Path $p
        Write-LintWarning -LintId 'dma-queue' -Message (("{0} (confirme cleanup de scroll/FX na saida da cena)" -f $rel))
    }

    $centerMagicHits = @(Select-String -Path $files -Pattern 'CAM_HALF_W\s*-\s*\d+' -List -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Path)
    foreach ($p in $centerMagicHits | Select-Object -Unique) {
        $contentHasDisable = Select-String -Path $p -Pattern "SGDK_WRAPPER_LINT_DISABLE_CENTER_MAGIC" -SimpleMatch -Quiet -ErrorAction SilentlyContinue
        if ($contentHasDisable) { continue }
        $rel = Get-RelPath -Base $Root -Path $p
        Write-LintWarning -LintId 'center-magic' -Message (("{0} (evite offsets magicos; prefira SPR_CENTER_X(def, cx))" -f $rel))
    }

    $textPal0Regex = 'VDP_setTextPalette\s*\(\s*PAL0\s*\)'
    foreach ($hit in @(Select-String -Path $files -Pattern $textPal0Regex -ErrorAction SilentlyContinue)) {
        if ($hit.Line -match "SGDK_WRAPPER_LINT_DISABLE_TEXT_PALETTE") { continue }
        $rel = Get-RelPath -Base $Root -Path $hit.Path
        Write-LintWarning -LintId 'text-palette' -Message (("{0}:{1} usa PAL0 (prefira PAL3 com paleta de alto contraste)" -f $rel, $hit.LineNumber))
    }

    foreach ($file in $files) {
        $disableFile = Select-String -Path $file -Pattern "SGDK_WRAPPER_LINT_DISABLE_TEXT_PALETTE" -SimpleMatch -Quiet -ErrorAction SilentlyContinue
        if ($disableFile) { continue }
        $enterBodies = Get-NamedFunctionBodies -FilePath $file -NameSuffixRegex 'Enter'
        foreach ($body in $enterBodies) {
            if ($body -match 'SGDK_WRAPPER_LINT_DISABLE_TEXT_PALETTE') { continue }
            if ($body -match 'VDP_setTextPalette\s*\(\s*PAL3\s*\)') {
                $hasGrey = ($body -match 'PAL_setPalette\s*\(\s*PAL3\s*,\s*palette_grey\b')
                if (-not $hasGrey) {
                    $rel = Get-RelPath -Base $Root -Path $file
                    Write-LintWarning -LintId 'text-palette' -Message (("{0} Enter usa VDP_setTextPalette(PAL3) sem PAL_setPalette(PAL3, palette_grey, ...)" -f $rel))
                }
            }
        }
    }

    foreach ($file in $files) {
        $disableFile = Select-String -Path $file -Pattern "SGDK_WRAPPER_LINT_DISABLE_SCROLLTILE_OVERLAY" -SimpleMatch -Quiet -ErrorAction SilentlyContinue
        if ($disableFile) { continue }
        $hasColumnTile = Select-String -Path $file -Pattern '\bVDP_setVerticalScrollTile\s*\(' -Quiet -ErrorAction SilentlyContinue
        $hasLineMode = Select-String -Path $file -Pattern 'HSCROLL_LINE' -SimpleMatch -Quiet -ErrorAction SilentlyContinue
        $hasColumnMode = Select-String -Path $file -Pattern 'VSCROLL_COLUMN' -SimpleMatch -Quiet -ErrorAction SilentlyContinue
        if (-not ($hasColumnTile -or $hasLineMode -or $hasColumnMode)) { continue }

        $hasText = Select-String -Path $file -Pattern '\bVDP_drawText(Fill)?\s*\(' -Quiet -ErrorAction SilentlyContinue
        $hasWindowPlane = (Select-String -Path $file -Pattern '\bVDP_setTextPlane\s*\(\s*WINDOW\s*\)' -Quiet -ErrorAction SilentlyContinue) -or
                          (Select-String -Path $file -Pattern '\bSCENE_overlayWindowBegin\s*\(' -Quiet -ErrorAction SilentlyContinue)
        if ($hasText -and (-not $hasWindowPlane)) {
            $rel = Get-RelPath -Base $Root -Path $file
            Write-LintWarning -LintId 'text-on-scrolled-plane' -Message (("{0} usa scroll nao-PLANE + texto sem VDP_setTextPlane(WINDOW) (overlay pode ficar ilegivel)" -f $rel))
        }
    }
}

try {
    $mdRoot = Resolve-MegaDriveRoot -ExplicitRoot $RepoRoot
    if (-not (Test-Path -LiteralPath $mdRoot -PathType Container)) {
        Write-PreflightLog "ERROR" "MD_ROOT invalido ou inexistente: $mdRoot"
        exit 1
    }
    Write-PreflightLog "INFO" "MD_ROOT=$mdRoot"

    $gdk = Resolve-GdkPath -MdRoot $mdRoot
    $makefileGen = Join-Path $gdk "makefile.gen"
    if (-not (Test-Path -LiteralPath $makefileGen -PathType Leaf)) {
        Write-PreflightLog "ERROR" "GDK sem makefile.gen. GDK candidato=$gdk. Defina GDK ou instale SGDK em sdk\sgdk-2.11."
        $script:blockingFailures++
    } else {
        Write-PreflightLog "OK" "GDK=$gdk"
    }

    if (-not (Test-CommandExists 'make')) {
        Write-PreflightLog "ERROR" "Comando 'make' nao encontrado no PATH (msys2 / toolchain SGDK)."
        $script:blockingFailures++
    } else {
        Write-PreflightLog "OK" "make encontrado."
    }

    if (-not (Test-CommandExists 'java')) {
        Write-PreflightLog "ERROR" "Comando 'java' nao encontrado no PATH. ResComp precisa de Java; build_inner.bat tenta corrigir PATH em alguns setups."
        $script:blockingFailures++
    } else {
        Write-PreflightLog "OK" "java encontrado."
    }

    $py = Get-UsablePythonPath
    if (-not $py) {
        Write-PreflightLog "WARN" "Python utilizavel nao encontrado (stub WindowsApps ignorado). validate_resources / analyze_aesthetic podem falhar."
        $script:softWarnings++
    } else {
        Write-PreflightLog "OK" "Python=$py"
    }

    $magick = Get-MagickPathResolved
    if (-not $magick) {
        Write-PreflightLog "WARN" "ImageMagick magick.exe nao encontrado. Validador pode degradar para header PNG."
        $script:softWarnings++
    } else {
        Write-PreflightLog "OK" "ImageMagick=$magick"
    }

    if (-not [string]::IsNullOrWhiteSpace($ProjectRoot)) {
        Invoke-ProjectLints -Root $ProjectRoot
    }

    if ($script:strictModeEnabled) {
        Write-PreflightLog "INFO" ("SGDK_LINT_STRICT=1 ativo. Lints promoviveis a erro: {0}" -f ($script:strictPromotableLints -join ','))
    }

    if ($script:blockingFailures -gt 0) {
        Write-PreflightLog "ERROR" ("Preflight FALHOU: {0} check(s) obrigatorio(s)." -f $script:blockingFailures)
        exit 1
    }
    if ($script:strictErrors -gt 0) {
        Write-PreflightLog "ERROR" ("Preflight FALHOU (strict): {0} lint(s) promovido(s) a erro." -f $script:strictErrors)
        exit 1
    }
    if (($script:softWarnings + $script:lintWarnings) -gt 0) {
        Write-PreflightLog "WARN" ("Preflight OK com {0} aviso(s) (opcionais+lints)." -f ($script:softWarnings + $script:lintWarnings))
        exit 2
    }
    Write-PreflightLog "INFO" "Preflight OK sem avisos."
    exit 0
}
catch {
    Write-PreflightLog "ERROR" "Excecao: $($_.Exception.Message)"
    exit 1
}
