# ==============================================================================
# fix_migration_issues.ps1
# Pre-processamento automatico para migracao SGDK 160/200 -> 211.
#
# Secoes:
#   1. Recuperacao resiliente de recursos (.res) com fallback para versao 160
#   2. Substituicao de boot files (sega.s / rom_head.c) incompativeis
#   3. Migracao de APIs deprecadas no codigo C (tabela de regras com word boundary)
#
# Recursos de resiliencia:
#   - Logging estruturado por regra aplicada (arquivo + linha + antes/depois)
#   - Modo -DryRun para preview de mudancas sem escrita
#   - Marker file (.sgdk_migration_state.json) para idempotencia
#   - Parametro -Force para ignorar marker e re-processar
# ==============================================================================
param(
    [string]$projectDir,
    [switch]$DryRun,
    [switch]$Force
)

if (-not $projectDir) {
    $projectDir = Get-Location
}
$projectDir = $projectDir.Trim('"').Trim("'")

$LOG_DIR = if ($env:SGDK_LOG_DIR) { $env:SGDK_LOG_DIR } else { Join-Path $projectDir "out\logs" }
$DEBUG_LOG = if ($env:SGDK_DEBUG_LOG) { $env:SGDK_DEBUG_LOG } else { Join-Path $LOG_DIR "build_debug.log" }

function Write-MigrationLog($msg, $level = "INFO") {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $fullMsg = "[$timestamp] [MIGRATION] [$level] $msg"
    Write-Host $fullMsg
    if (-not (Test-Path -LiteralPath $LOG_DIR)) {
        New-Item -ItemType Directory -Force -Path $LOG_DIR | Out-Null
    }
    Add-Content -LiteralPath $DEBUG_LOG $fullMsg -ErrorAction SilentlyContinue
}

# --- Marker File (Idempotencia) ---
# Se o marker existe e o hash deste script nao mudou, pula migracao.
# Isso evita re-parsear arquivos grandes (ex: HAMOOPIG 7000+ linhas) em cada build.
$markerFile = Join-Path $projectDir ".sgdk_migration_state.json"
$scriptHash = (Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash

if (-not $Force -and -not $DryRun -and (Test-Path -LiteralPath $markerFile)) {
    try {
        $marker = Get-Content -LiteralPath $markerFile -Raw | ConvertFrom-Json
        if ($marker.scriptHash -eq $scriptHash) {
            Write-Host "[SGDK Wrapper] Migration already applied (marker valid). Use -Force to re-process."
            exit 0
        } else {
            Write-MigrationLog "Script updated (hash changed). Re-running migration." "INFO"
        }
    } catch {
        Write-MigrationLog "Marker file corrupted. Re-running migration." "WARN"
    }
}

if ($DryRun) {
    Write-Host "[SGDK Wrapper] DRY-RUN mode: showing changes without writing."
}
Write-Host "[SGDK Wrapper] Pre-processing migration issues in: $projectDir"

# ============================================================================
# SECAO 1: Recuperacao Resiliente de Recursos (.res)
# ============================================================================
$resDir = Join-Path $projectDir "res"
if (Test-Path -LiteralPath $resDir) {
    $projectName = Split-Path $projectDir -Leaf
    $parentDir = Split-Path $projectDir -Parent
    $sourceResFile = $null

    # Tenta encontrar versao SGDK 160 como fonte de recuperacao
    if ($projectName -like "*[SGDK 211]*") {
        $sourceProjectName = $projectName -replace '\[SGDK 211\]?\s*\[?', '[SGDK 160]'
        $sourcePath = Join-Path $parentDir $sourceProjectName
        $potentialRes = Join-Path $sourcePath "res/sprite.res"
        if (Test-Path -LiteralPath $potentialRes) {
            $sourceResFile = $potentialRes
            Write-MigrationLog "Found source recovery file: $sourceResFile"
        }
    }

    $resFiles = Get-ChildItem -LiteralPath $resDir -Filter "*.res" -ErrorAction SilentlyContinue
    foreach ($res in $resFiles) {
        Write-MigrationLog "Running resilient resource fixer on $($res.Name)..."
        $fixerScript = Join-Path $PSScriptRoot "autofix_sprite_res.ps1"
        if ((Test-Path -LiteralPath $fixerScript) -and -not $DryRun) {
            if ($sourceResFile -and $res.Name -eq "sprite.res") {
                powershell -NoProfile -ExecutionPolicy Bypass -Command "Set-Location -LiteralPath '$projectDir'; & '$fixerScript' '$($res.FullName)' '$sourceResFile'"
            } else {
                powershell -NoProfile -ExecutionPolicy Bypass -Command "Set-Location -LiteralPath '$projectDir'; & '$fixerScript' '$($res.FullName)'"
            }
        }

        $resContent = Get-Content -LiteralPath $res.FullName -Raw -ErrorAction SilentlyContinue
        if ($resContent) {
            $resOriginal = $resContent

            $resContent = [regex]::Replace(
                $resContent,
                '(?m)^(\s*WAV\s+\S+\s+(?:"[^"]+"|\S+)\s+)5(\s*)$',
                '$1XGM$2'
            )
            $resContent = [regex]::Replace(
                $resContent,
                '(?m)^(\s*WAV\s+\S+\s+(?:"[^"]+"|\S+))(\s*)$',
                '$1 XGM$2'
            )

            if ($resContent -ne $resOriginal) {
                if ($DryRun) {
                    Write-MigrationLog "[DRY-RUN] Would normalize legacy WAV driver syntax in $($res.Name)" "INFO"
                } else {
                    Set-Content -LiteralPath $res.FullName $resContent -NoNewline
                    Write-MigrationLog "Normalized legacy WAV driver syntax in $($res.Name)" "INFO"
                }
            }
        }
    }
}

# ============================================================================
# SECAO 2: Boot Files Guarantee (sega.s / rom_head.c)
# ============================================================================
# O makefile Elite depende de `src/boot/sega.s` e `src/boot/rom_head.c`.
# Projetos legados podem ter boot customizado (incompativel com SGDK 211) e
# projetos novos podem sequer ter `src/boot/`. Para eliminar divergencia,
# garantimos a presenca dos boot files padrao do SGDK 2.11 antes do build.
$bootDir = Join-Path $projectDir "src\boot"
$wrapperDir = $PSScriptRoot
$mdRoot = (Resolve-Path -LiteralPath (Join-Path $wrapperDir "..\..")).Path
$sdkBootDir = Join-Path $mdRoot "sdk\sgdk-2.11\src\boot"

if (-not (Test-Path -LiteralPath $sdkBootDir -PathType Container)) {
    Write-MigrationLog "SDK boot dir nao encontrado: $sdkBootDir" "ERROR"
} else {
    if (-not (Test-Path -LiteralPath $bootDir -PathType Container)) {
        if ($DryRun) {
            Write-MigrationLog "[DRY-RUN] Would create boot dir: $bootDir" "INFO"
        } else {
            New-Item -ItemType Directory -Path $bootDir -Force | Out-Null
            Write-MigrationLog "Created boot dir: $bootDir" "INFO"
        }
    }

    foreach ($bootFile in @("sega.s", "rom_head.c")) {
        $projFile = Join-Path $bootDir $bootFile
        $sdkFile = Join-Path $sdkBootDir $bootFile

        if (-not (Test-Path -LiteralPath $sdkFile -PathType Leaf)) {
            Write-MigrationLog "SDK boot file ausente: $sdkFile" "ERROR"
            continue
        }

        if (-not (Test-Path -LiteralPath $projFile -PathType Leaf)) {
            if ($DryRun) {
                Write-MigrationLog "[DRY-RUN] Would copy missing boot file: $bootFile" "INFO"
            } else {
                Copy-Item -LiteralPath $sdkFile -Destination $projFile -Force
                Write-MigrationLog "Fixed: missing $bootFile copied from SGDK 2.11 standard" "INFO"
            }
            continue
        }

        $projHash = (Get-FileHash -LiteralPath $projFile -Algorithm MD5).Hash
        $sdkHash = (Get-FileHash -LiteralPath $sdkFile -Algorithm MD5).Hash
        if ($projHash -ne $sdkHash) {
            if ($DryRun) {
                Write-MigrationLog "[DRY-RUN] Would replace $bootFile with SGDK 2.11 standard" "INFO"
            } else {
                Copy-Item -LiteralPath $sdkFile -Destination $projFile -Force
                Write-MigrationLog "Fixed: $bootFile replaced with SGDK 2.11 standard (old hash: $projHash)" "INFO"
            }
        }
    }

    if (-not $DryRun) {
        Get-ChildItem -LiteralPath $bootDir -Filter "*.old" -ErrorAction SilentlyContinue | Remove-Item -Force
    }
}

# ============================================================================
# SECAO 3: Migracao de APIs Deprecadas (Tabela de Regras)
# ============================================================================
# Cada regra e um objeto com:
#   - Name: identificador curto (para log)
#   - Pattern: regex com \b (word boundary) para evitar matches parciais
#   - Replacement: string de substituicao (pode conter $1, $2, etc.)
#   - Description: explicacao pedagogica
#
# ORDEM IMPORTA: regras mais especificas (nomes mais longos) ANTES das genericas.
# Ex: VDP_setPaletteColors antes de VDP_setPaletteColor, antes de VDP_setPalette.
$migrationRules = @(
    # --- includes legacy de SGDK 1.x --- 
    [PSCustomObject]@{
        Name        = "include_sound_h_to_snd_sound_h"
        Pattern     = '#include\s+"sound\.h"'
        Replacement = '#include "snd/sound.h"'
        Description = "sound.h direto -> snd/sound.h"
    },
    [PSCustomObject]@{
        Name        = "include_sprite_h_to_sprite_eng_h"
        Pattern     = '#include\s+"sprite\.h"'
        Replacement = '#include "sprite_eng.h"'
        Description = "sprite.h legacy -> sprite_eng.h"
    },

    # --- constantes e macros de planos / tiles --- 
    [PSCustomObject]@{
        Name        = "VDP_PLAN_A_to_VDP_BG_A"
        Pattern     = '\bVDP_PLAN_A\b'
        Replacement = 'VDP_BG_A'
        Description = "VDP_PLAN_A -> VDP_BG_A"
    },
    [PSCustomObject]@{
        Name        = "VDP_PLAN_B_to_VDP_BG_B"
        Pattern     = '\bVDP_PLAN_B\b'
        Replacement = 'VDP_BG_B'
        Description = "VDP_PLAN_B -> VDP_BG_B"
    },
    [PSCustomObject]@{
        Name        = "VDP_PLAN_WINDOW_to_VDP_WINDOW"
        Pattern     = '\bVDP_PLAN_WINDOW\b'
        Replacement = 'VDP_WINDOW'
        Description = "VDP_PLAN_WINDOW -> VDP_WINDOW"
    },
    [PSCustomObject]@{
        Name        = "PLAN_A_to_BG_A"
        Pattern     = '\bPLAN_A\b'
        Replacement = 'BG_A'
        Description = "PLAN_A -> BG_A"
    },
    [PSCustomObject]@{
        Name        = "PLAN_B_to_BG_B"
        Pattern     = '\bPLAN_B\b'
        Replacement = 'BG_B'
        Description = "PLAN_B -> BG_B"
    },
    [PSCustomObject]@{
        Name        = "PLAN_WINDOW_to_VDP_WINDOW"
        Pattern     = '\bPLAN_WINDOW\b'
        Replacement = 'VDP_WINDOW'
        Description = "PLAN_WINDOW -> VDP_WINDOW"
    },
    [PSCustomObject]@{
        Name        = "TILE_USERINDEX_to_TILE_USER_INDEX"
        Pattern     = '\bTILE_USERINDEX\b'
        Replacement = 'TILE_USER_INDEX'
        Description = "TILE_USERINDEX -> TILE_USER_INDEX"
    },

    # --- VDP helpers renomeados --- 
    [PSCustomObject]@{
        Name        = "VDP_setPlanSize_to_VDP_setPlaneSize"
        Pattern     = '\bVDP_setPlanSize\b'
        Replacement = 'VDP_setPlaneSize'
        Description = "VDP_setPlanSize -> VDP_setPlaneSize"
    },
    [PSCustomObject]@{
        Name        = "VDP_setPlaneSize_2to3"
        Pattern     = '\bVDP_setPlaneSize\s*\(\s*([^,]+)\s*,\s*([^\),\r\n]+)\s*\)'
        Replacement = 'VDP_setPlaneSize($1, $2, TRUE)'
        Description = "VDP_setPlaneSize legacy 2 args -> 3 args"
    },
    [PSCustomObject]@{
        Name        = "VDP_setTextPlan_to_VDP_setTextPlane"
        Pattern     = '\bVDP_setTextPlan\b'
        Replacement = 'VDP_setTextPlane'
        Description = "VDP_setTextPlan -> VDP_setTextPlane"
    },
    [PSCustomObject]@{
        Name        = "VDP_clearPlan_to_VDP_clearPlane"
        Pattern     = '\bVDP_clearPlan\b'
        Replacement = 'VDP_clearPlane'
        Description = "VDP_clearPlan -> VDP_clearPlane"
    },
    [PSCustomObject]@{
        Name        = "VDP_setTileMapDataRect_6to8"
        Pattern     = '\bVDP_setTileMapDataRect\s*\(\s*([^,\r\n]+),\s*([^,\r\n]+),\s*([^,\r\n]+),\s*([^,\r\n]+),\s*([^,\r\n]+),\s*([^,\)\r\n]+)\s*\)'
        Replacement = 'VDP_setTileMapDataRect($1, $2, $3, $4, $5, $6, $5, DMA)'
        Description = "VDP_setTileMapDataRect legacy 6 args -> 8 args (wm = w, tm = DMA)"
    },
    [PSCustomObject]@{
        Name        = "VDP_interruptFade_to_PAL_interruptFade"
        Pattern     = '\bVDP_interruptFade\b'
        Replacement = 'PAL_interruptFade'
        Description = "VDP_interruptFade -> PAL_interruptFade"
    },
    [PSCustomObject]@{
        Name        = "VDP_getPaletteColor_to_PAL_getColor"
        Pattern     = '\bVDP_getPaletteColor\b'
        Replacement = 'PAL_getColor'
        Description = "VDP_getPaletteColor -> PAL_getColor"
    },
    [PSCustomObject]@{
        Name        = "VDP_waitFadeCompletion_to_PAL_waitFadeCompletion"
        Pattern     = '\bVDP_waitFadeCompletion\b'
        Replacement = 'PAL_waitFadeCompletion'
        Description = "VDP_waitFadeCompletion -> PAL_waitFadeCompletion"
    },
    [PSCustomObject]@{
        Name        = "SPR_setPriorityAttribut_to_SPR_setPriority"
        Pattern     = '\bSPR_setPriorityAttribut\b'
        Replacement = 'SPR_setPriority'
        Description = "SPR_setPriorityAttribut -> SPR_setPriority"
    },
    [PSCustomObject]@{
        Name        = "VDPPlan_to_VDPPlane"
        Pattern     = '\bVDPPlan\b'
        Replacement = 'VDPPlane'
        Description = "VDPPlan -> VDPPlane"
    },

    # --- SPR_addSpriteEx: remover parametro sprIndex (6->5 params) ---
    [PSCustomObject]@{
        Name        = "SPR_addSpriteExSafe_6to5"
        Pattern     = 'SPR_addSpriteExSafe\s*\(\s*([^,]+)\s*,\s*([^,]+)\s*,\s*([^,]+)\s*,\s*((?:TILE_ATTR(?:_FULL)?\((?:[^()]|\([^()]*\))*\))|[^,]+)\s*,\s*[01]\s*,\s*([^)]+)\)'
        Replacement = 'SPR_addSpriteExSafe($1, $2, $3, $4, $5)'
        Description = "SPR_addSpriteExSafe: SGDK 211 removeu sprIndex (6->5 params)"
    },
    [PSCustomObject]@{
        Name        = "SPR_addSpriteEx_6to5"
        Pattern     = 'SPR_addSpriteEx\s*\(\s*([^,]+)\s*,\s*([^,]+)\s*,\s*([^,]+)\s*,\s*((?:TILE_ATTR(?:_FULL)?\((?:[^()]|\([^()]*\))*\))|[^,]+)\s*,\s*[01]\s*,\s*([^)]+)\)'
        Replacement = 'SPR_addSpriteEx($1, $2, $3, $4, $5)'
        Description = "SPR_addSpriteEx: SGDK 211 removeu sprIndex (6->5 params)"
    },

    # --- VDP_setPaletteColors -> PAL_setColors (3 args -> 3 args + DMA) ---
    # DEVE vir ANTES de VDP_setPaletteColor (nome mais longo primeiro)
    [PSCustomObject]@{
        Name        = "VDP_setPaletteColors_to_PAL_setColors"
        Pattern     = '\bVDP_setPaletteColors\s*\(([^,]+,\s*[^,]+,\s*[^,)]+)\)'
        Replacement = 'PAL_setColors($1, DMA)'
        Description = "VDP_setPaletteColors -> PAL_setColors com TransferMethod explicito"
    },

    # --- VDP_setPaletteColor -> PAL_setColor (singular) ---
    [PSCustomObject]@{
        Name        = "VDP_setPaletteColor_to_PAL_setColor"
        Pattern     = '\bVDP_setPaletteColor\b'
        Replacement = 'PAL_setColor'
        Description = "VDP_setPaletteColor -> PAL_setColor (funcao singular)"
    },

    # --- VDP_setPalette -> PAL_setPalette (2 args -> 2 args + DMA) ---
    [PSCustomObject]@{
        Name        = "VDP_setPalette_to_PAL_setPalette"
        Pattern     = '\bVDP_setPalette\s*\(([^,]+,\s*[^,)]+)\)'
        Replacement = 'PAL_setPalette($1, DMA)'
        Description = "VDP_setPalette -> PAL_setPalette com TransferMethod explicito"
    },

    # --- PAL_setColorsDMA -> PAL_setColors (variante DMA removida) ---
    [PSCustomObject]@{
        Name        = "PAL_setColorsDMA_to_PAL_setColors"
        Pattern     = '\bPAL_setColorsDMA\s*\(([^)]+)\)'
        Replacement = 'PAL_setColors($1, DMA)'
        Description = "PAL_setColorsDMA removida; usar PAL_setColors com DMA explicito"
    },

    # --- PAL_setPaletteDMA -> PAL_setPalette (variante DMA removida) ---
    [PSCustomObject]@{
        Name        = "PAL_setPaletteDMA_to_PAL_setPalette"
        Pattern     = '\bPAL_setPaletteDMA\s*\(([^)]+)\)'
        Replacement = 'PAL_setPalette($1, DMA)'
        Description = "PAL_setPaletteDMA removida; usar PAL_setPalette com DMA explicito"
    },

    # --- VDP_showFPS: assinatura mudou (1 arg -> 3 args) ---
    [PSCustomObject]@{
        Name        = "VDP_showFPS_1to3"
        Pattern     = '\bVDP_showFPS\s*\((TRUE|FALSE|1|0)\)'
        Replacement = 'VDP_showFPS($1, 1, 1)'
        Description = "VDP_showFPS agora requer (show, x, y) - 3 parametros"
    },
    [PSCustomObject]@{
        Name        = "BMP_showFPS_1to3"
        Pattern     = '\bBMP_showFPS\s*\((TRUE|FALSE|1|0)\)'
        Replacement = 'BMP_showFPS($1, 1, 1)'
        Description = "BMP_showFPS agora requer (show, x, y) - 3 parametros"
    },

    # --- SPR_FLAG_AUTO_SPRITE_ALLOC renomeada ---
    [PSCustomObject]@{
        Name        = "SPR_FLAG_AUTO_SPRITE_ALLOC_rename"
        Pattern     = '\bSPR_FLAG_AUTO_SPRITE_ALLOC\b'
        Replacement = 'SPR_FLAG_AUTO_VRAM_ALLOC'
        Description = "SPR_FLAG_AUTO_SPRITE_ALLOC -> SPR_FLAG_AUTO_VRAM_ALLOC"
    },

    # --- SPR_init: SGDK 211 usa assinatura sem parametros ---
    [PSCustomObject]@{
        Name        = "SPR_init_args_to_void"
        Pattern     = '\bSPR_init\s*\([^)]*\)'
        Replacement = 'SPR_init()'
        Description = "SPR_init agora usa assinatura sem parametros no SGDK 211"
    },

    # --- XGM legacy aliases --- 
    [PSCustomObject]@{
        Name        = "SND_setPCM_XGM_to_XGM_setPCM"
        Pattern     = '\bSND_setPCM_XGM\s*\('
        Replacement = 'XGM_setPCM('
        Description = "SND_setPCM_XGM -> XGM_setPCM"
    },
    [PSCustomObject]@{
        Name        = "SND_setPCMFast_XGM_to_XGM_setPCMFast"
        Pattern     = '\bSND_setPCMFast_XGM\s*\('
        Replacement = 'XGM_setPCMFast('
        Description = "SND_setPCMFast_XGM -> XGM_setPCMFast"
    },
    [PSCustomObject]@{
        Name        = "SND_startPlayPCM_XGM_to_XGM_startPlayPCM"
        Pattern     = '\bSND_startPlayPCM_XGM\s*\('
        Replacement = 'XGM_startPlayPCM('
        Description = "SND_startPlayPCM_XGM -> XGM_startPlayPCM"
    },
    [PSCustomObject]@{
        Name        = "SND_stopPlayPCM_XGM_to_XGM_stopPlayPCM"
        Pattern     = '\bSND_stopPlayPCM_XGM\s*\('
        Replacement = 'XGM_stopPlayPCM('
        Description = "SND_stopPlayPCM_XGM -> XGM_stopPlayPCM"
    },
    [PSCustomObject]@{
        Name        = "SND_startPlay_XGM_to_XGM_startPlay"
        Pattern     = '\bSND_startPlay_XGM\s*\('
        Replacement = 'XGM_startPlay('
        Description = "SND_startPlay_XGM -> XGM_startPlay"
    },
    [PSCustomObject]@{
        Name        = "SND_stopPlay_XGM_to_XGM_stopPlay"
        Pattern     = '\bSND_stopPlay_XGM\s*\('
        Replacement = 'XGM_stopPlay('
        Description = "SND_stopPlay_XGM -> XGM_stopPlay"
    },
    [PSCustomObject]@{
        Name        = "SND_pausePlay_XGM_to_XGM_pausePlay"
        Pattern     = '\bSND_pausePlay_XGM\s*\('
        Replacement = 'XGM_pausePlay('
        Description = "SND_pausePlay_XGM -> XGM_pausePlay"
    },
    [PSCustomObject]@{
        Name        = "SND_resumePlay_XGM_to_XGM_resumePlay"
        Pattern     = '\bSND_resumePlay_XGM\s*\('
        Replacement = 'XGM_resumePlay('
        Description = "SND_resumePlay_XGM -> XGM_resumePlay"
    },

    # --- PCM4 legacy aliases --- 
    [PSCustomObject]@{
        Name        = "SND_isPlaying_4PCM_to_PCM4"
        Pattern     = '\bSND_isPlaying_4PCM(?:_ENV)?\s*\('
        Replacement = 'SND_PCM4_isPlaying('
        Description = "SND_isPlaying_4PCM -> SND_PCM4_isPlaying"
    },
    [PSCustomObject]@{
        Name        = "SND_startPlay_4PCM_to_PCM4"
        Pattern     = '\bSND_startPlay_4PCM(?:_ENV)?\s*\('
        Replacement = 'SND_PCM4_startPlay('
        Description = "SND_startPlay_4PCM -> SND_PCM4_startPlay"
    },
    [PSCustomObject]@{
        Name        = "SND_stopPlay_4PCM_to_PCM4"
        Pattern     = '\bSND_stopPlay_4PCM(?:_ENV)?\s*\('
        Replacement = 'SND_PCM4_stopPlay('
        Description = "SND_stopPlay_4PCM -> SND_PCM4_stopPlay"
    },
    [PSCustomObject]@{
        Name        = "SND_getVolume_4PCM_to_PCM4"
        Pattern     = '\bSND_getVolume_4PCM(?:_ENV)?\s*\('
        Replacement = 'SND_PCM4_getVolume('
        Description = "SND_getVolume_4PCM -> SND_PCM4_getVolume"
    },
    [PSCustomObject]@{
        Name        = "SND_setVolume_4PCM_to_PCM4"
        Pattern     = '\bSND_setVolume_4PCM(?:_ENV)?\s*\('
        Replacement = 'SND_PCM4_setVolume('
        Description = "SND_setVolume_4PCM -> SND_PCM4_setVolume"
    },

    # --- fix32 legacy helpers -> F32_* / operadores --- 
    [PSCustomObject]@{
        Name        = "intToFix32_to_FIX32"
        Pattern     = '\bintToFix32\s*\('
        Replacement = 'FIX32('
        Description = "intToFix32 -> FIX32"
    },
    [PSCustomObject]@{
        Name        = "fix32ToInt_to_F32_toInt"
        Pattern     = '\bfix32ToInt\s*\('
        Replacement = 'F32_toInt('
        Description = "fix32ToInt -> F32_toInt"
    },
    [PSCustomObject]@{
        Name        = "fix32ToRoundedInt_to_F32_toRoundedInt"
        Pattern     = '\bfix32ToRoundedInt\s*\('
        Replacement = 'F32_toRoundedInt('
        Description = "fix32ToRoundedInt -> F32_toRoundedInt"
    },
    [PSCustomObject]@{
        Name        = "fix32ToFix16_to_F32_toFix16"
        Pattern     = '\bfix32ToFix16\s*\('
        Replacement = 'F32_toFix16('
        Description = "fix32ToFix16 -> F32_toFix16"
    },
    [PSCustomObject]@{
        Name        = "fix32Frac_to_F32_frac"
        Pattern     = '\bfix32Frac\s*\('
        Replacement = 'F32_frac('
        Description = "fix32Frac -> F32_frac"
    },
    [PSCustomObject]@{
        Name        = "fix32Int_to_F32_int"
        Pattern     = '\bfix32Int\s*\('
        Replacement = 'F32_int('
        Description = "fix32Int -> F32_int"
    },
    [PSCustomObject]@{
        Name        = "fix32Round_to_F32_round"
        Pattern     = '\bfix32Round\s*\('
        Replacement = 'F32_round('
        Description = "fix32Round -> F32_round"
    },
    [PSCustomObject]@{
        Name        = "fix32Mul_to_F32_mul"
        Pattern     = '\bfix32Mul\s*\('
        Replacement = 'F32_mul('
        Description = "fix32Mul -> F32_mul"
    },
    [PSCustomObject]@{
        Name        = "fix32Div_to_F32_div"
        Pattern     = '\bfix32Div\s*\('
        Replacement = 'F32_div('
        Description = "fix32Div -> F32_div"
    },

    # --- fix16 legacy helpers -> F16_* / operadores ---
    [PSCustomObject]@{
        Name        = "intToFix16_to_FIX16"
        Pattern     = '\bintToFix16\s*\('
        Replacement = 'FIX16('
        Description = "intToFix16 -> FIX16"
    },
    [PSCustomObject]@{
        Name        = "fix16ToInt_to_F16_toInt"
        Pattern     = '\bfix16ToInt\s*\('
        Replacement = 'F16_toInt('
        Description = "fix16ToInt -> F16_toInt"
    },
    [PSCustomObject]@{
        Name        = "fix16ToRoundedInt_to_F16_toRoundedInt"
        Pattern     = '\bfix16ToRoundedInt\s*\('
        Replacement = 'F16_toRoundedInt('
        Description = "fix16ToRoundedInt -> F16_toRoundedInt"
    },
    [PSCustomObject]@{
        Name        = "fix16ToFix32_to_F16_toFix32"
        Pattern     = '\bfix16ToFix32\s*\('
        Replacement = 'F16_toFix32('
        Description = "fix16ToFix32 -> F16_toFix32"
    },
    [PSCustomObject]@{
        Name        = "fix16Frac_to_F16_frac"
        Pattern     = '\bfix16Frac\s*\('
        Replacement = 'F16_frac('
        Description = "fix16Frac -> F16_frac"
    },
    [PSCustomObject]@{
        Name        = "fix16Int_to_F16_int"
        Pattern     = '\bfix16Int\s*\('
        Replacement = 'F16_int('
        Description = "fix16Int -> F16_int"
    },
    [PSCustomObject]@{
        Name        = "fix16Round_to_F16_round"
        Pattern     = '\bfix16Round\s*\('
        Replacement = 'F16_round('
        Description = "fix16Round -> F16_round"
    },
    [PSCustomObject]@{
        Name        = "fix16Mul_to_F16_mul"
        Pattern     = '\bfix16Mul\s*\('
        Replacement = 'F16_mul('
        Description = "fix16Mul -> F16_mul"
    },
    [PSCustomObject]@{
        Name        = "fix16Div_to_F16_div"
        Pattern     = '\bfix16Div\s*\('
        Replacement = 'F16_div('
        Description = "fix16Div -> F16_div"
    },
    [PSCustomObject]@{
        Name        = "fix16Add_to_operator"
        Pattern     = '\bfix16Add\s*\(([^,]+),\s*([^)]+)\)'
        Replacement = '(($1) + ($2))'
        Description = "fix16Add -> operador +"
    },
    [PSCustomObject]@{
        Name        = "fix16Sub_to_operator"
        Pattern     = '\bfix16Sub\s*\(([^,]+),\s*([^)]+)\)'
        Replacement = '(($1) - ($2))'
        Description = "fix16Sub -> operador -"
    },
    [PSCustomObject]@{
        Name        = "fix16Neg_to_operator"
        Pattern     = '\bfix16Neg\s*\(([^)]+)\)'
        Replacement = '(0 - ($1))'
        Description = "fix16Neg -> operador de negacao"
    },
    [PSCustomObject]@{
        Name        = "fix16Avg_to_F16_avg"
        Pattern     = '\bfix16Avg\s*\('
        Replacement = 'F16_avg('
        Description = "fix16Avg -> F16_avg"
    },
    [PSCustomObject]@{
        Name        = "fix16Log2_to_F16_log2"
        Pattern     = '\bfix16Log2\s*\('
        Replacement = 'F16_log2('
        Description = "fix16Log2 -> F16_log2"
    },
    [PSCustomObject]@{
        Name        = "fix16Log10_to_F16_log10"
        Pattern     = '\bfix16Log10\s*\('
        Replacement = 'F16_log10('
        Description = "fix16Log10 -> F16_log10"
    },
    [PSCustomObject]@{
        Name        = "fix16Sqrt_to_F16_sqrt"
        Pattern     = '\bfix16Sqrt\s*\('
        Replacement = 'F16_sqrt('
        Description = "fix16Sqrt -> F16_sqrt"
    },

    # --- VDP_fade* -> PAL_fade* (macros deprecadas em vdp_pal.h) ---
    [PSCustomObject]@{
        Name        = "VDP_fade_to_PAL_fade"
        Pattern     = '\bVDP_fade\b'
        Replacement = 'PAL_fade'
        Description = "VDP_fade -> PAL_fade"
    },
    [PSCustomObject]@{
        Name        = "VDP_fadeTo_to_PAL_fadeTo"
        Pattern     = '\bVDP_fadeTo\b'
        Replacement = 'PAL_fadeTo'
        Description = "VDP_fadeTo -> PAL_fadeTo"
    },
    [PSCustomObject]@{
        Name        = "VDP_fadeOut_to_PAL_fadeOut"
        Pattern     = '\bVDP_fadeOut\b'
        Replacement = 'PAL_fadeOut'
        Description = "VDP_fadeOut -> PAL_fadeOut"
    },
    [PSCustomObject]@{
        Name        = "VDP_fadeIn_to_PAL_fadeIn"
        Pattern     = '\bVDP_fadeIn\b'
        Replacement = 'PAL_fadeIn'
        Description = "VDP_fadeIn -> PAL_fadeIn"
    },
    [PSCustomObject]@{
        Name        = "VDP_fadePal_to_PAL_fadePalette"
        Pattern     = '\bVDP_fadePal\b'
        Replacement = 'PAL_fadePalette'
        Description = "VDP_fadePal -> PAL_fadePalette"
    },
    [PSCustomObject]@{
        Name        = "VDP_fadeToPal_to_PAL_fadeToPalette"
        Pattern     = '\bVDP_fadeToPal\b'
        Replacement = 'PAL_fadeToPalette'
        Description = "VDP_fadeToPal -> PAL_fadeToPalette"
    },
    [PSCustomObject]@{
        Name        = "VDP_fadeOutPal_to_PAL_fadeOutPalette"
        Pattern     = '\bVDP_fadeOutPal\b'
        Replacement = 'PAL_fadeOutPalette'
        Description = "VDP_fadeOutPal -> PAL_fadeOutPalette"
    },
    [PSCustomObject]@{
        Name        = "VDP_fadeInPal_to_PAL_fadeInPalette"
        Pattern     = '\bVDP_fadeInPal\b'
        Replacement = 'PAL_fadeInPalette'
        Description = "VDP_fadeInPal -> PAL_fadeInPalette"
    },
    [PSCustomObject]@{
        Name        = "VDP_fadeAll_to_PAL_fadeAll"
        Pattern     = '\bVDP_fadeAll\b'
        Replacement = 'PAL_fadeAll'
        Description = "VDP_fadeAll -> PAL_fadeAll"
    },
    [PSCustomObject]@{
        Name        = "VDP_fadeToAll_to_PAL_fadeToAll"
        Pattern     = '\bVDP_fadeToAll\b'
        Replacement = 'PAL_fadeToAll'
        Description = "VDP_fadeToAll -> PAL_fadeToAll"
    },
    [PSCustomObject]@{
        Name        = "VDP_fadeOutAll_to_PAL_fadeOutAll"
        Pattern     = '\bVDP_fadeOutAll\b'
        Replacement = 'PAL_fadeOutAll'
        Description = "VDP_fadeOutAll -> PAL_fadeOutAll"
    },
    [PSCustomObject]@{
        Name        = "VDP_fadeInAll_to_PAL_fadeInAll"
        Pattern     = '\bVDP_fadeInAll\b'
        Replacement = 'PAL_fadeInAll'
        Description = "VDP_fadeInAll -> PAL_fadeInAll"
    }
)

# Coleta arquivos .c e .h do projeto
$srcDir = Join-Path $projectDir "src"
$files = @()
if (Test-Path -LiteralPath $srcDir) {
    $files += Get-ChildItem -LiteralPath $srcDir -Filter "*.c" -Recurse -ErrorAction SilentlyContinue
    $files += Get-ChildItem -LiteralPath $srcDir -Filter "*.h" -Recurse -ErrorAction SilentlyContinue
}
# Alguns projetos tem main.c na raiz
$files += Get-ChildItem -LiteralPath $projectDir -Filter "*.c" -File -ErrorAction SilentlyContinue
$files += Get-ChildItem -LiteralPath $projectDir -Filter "*.h" -File -ErrorAction SilentlyContinue
$files = $files | Sort-Object -Property FullName -Unique

$hasLocalSpriteResourceHeader = Test-Path -LiteralPath (Join-Path $projectDir "res\sprite.h")
$hasLocalSoundResourceHeader = Test-Path -LiteralPath (Join-Path $projectDir "res\sound.h")

$totalChanges = 0
$changedFiles = @()

foreach ($file in $files) {
    $content = Get-Content -LiteralPath $file.FullName -Raw
    if (-not $content) { continue }
    $originalContent = $content
    $fileChanges = 0

    foreach ($rule in $migrationRules) {
        if ($hasLocalSpriteResourceHeader -and $rule.Name -eq "include_sprite_h_to_sprite_eng_h") {
            continue
        }
        if ($hasLocalSoundResourceHeader -and $rule.Name -eq "include_sound_h_to_snd_sound_h") {
            continue
        }
        $matches_found = [regex]::Matches($content, $rule.Pattern)
        if ($matches_found.Count -gt 0) {
            foreach ($m in $matches_found) {
                # Encontra numero da linha do match
                $beforeMatch = $content.Substring(0, $m.Index)
                $lineNum = ($beforeMatch -split "`n").Count
                $oldSnippet = $m.Value
                # Aplica substituicao neste match para preview
                $newSnippet = [regex]::Replace($oldSnippet, $rule.Pattern, $rule.Replacement)

                if ($DryRun) {
                    Write-MigrationLog "[DRY-RUN] $($file.Name):$lineNum [$($rule.Name)] `"$oldSnippet`" -> `"$newSnippet`"" "INFO"
                } else {
                    Write-MigrationLog "$($file.Name):$lineNum [$($rule.Name)] applied" "INFO"
                }
            }
            # Aplica a regra no conteudo completo
            $content = [regex]::Replace($content, $rule.Pattern, $rule.Replacement)
            $fileChanges += $matches_found.Count
        }
    }

    # Alguns projetos SGDK usam sprite.h / sound.h como headers de recurso gerados.
    # Se esses headers locais existem, garantimos que o include local continue presente
    # mesmo quando o wrapper adicionou os includes de API em uma migracao anterior.
    if ($hasLocalSpriteResourceHeader -and
        $content -match '#include\s+"sprite_eng\.h"' -and
        $content -notmatch '#include\s+"sprite\.h"') {
        $content = [regex]::Replace(
            $content,
            '#include\s+"sprite_eng\.h"',
            "#include `"sprite_eng.h`"`r`n#include `"sprite.h`"",
            1
        )
        $fileChanges += 1
        if ($DryRun) {
            Write-MigrationLog "[DRY-RUN] $($file.Name): restored local resource include sprite.h alongside sprite_eng.h" "INFO"
        } else {
            Write-MigrationLog "$($file.Name): restored local resource include sprite.h alongside sprite_eng.h" "INFO"
        }
    }

    if ($hasLocalSoundResourceHeader -and
        $content -match '#include\s+"snd/sound\.h"' -and
        $content -notmatch '#include\s+"sound\.h"') {
        $content = [regex]::Replace(
            $content,
            '#include\s+"snd/sound\.h"',
            "#include `"snd/sound.h`"`r`n#include `"sound.h`"",
            1
        )
        $fileChanges += 1
        if ($DryRun) {
            Write-MigrationLog "[DRY-RUN] $($file.Name): restored local resource include sound.h alongside snd/sound.h" "INFO"
        } else {
            Write-MigrationLog "$($file.Name): restored local resource include sound.h alongside snd/sound.h" "INFO"
        }
    }

    if ($content -ne $originalContent) {
        $totalChanges += $fileChanges
        $changedFiles += $file.FullName
        if (-not $DryRun) {
            Set-Content -LiteralPath $file.FullName $content -NoNewline
            Write-MigrationLog "Fixed $fileChanges issue(s) in $($file.FullName)" "INFO"
        } else {
            Write-MigrationLog "[DRY-RUN] Would fix $fileChanges issue(s) in $($file.FullName)" "INFO"
        }
    }
}

if ($totalChanges -eq 0) {
    Write-Host "[SGDK Wrapper] No migration changes needed (code is already SGDK 211 compatible)."
} else {
    $verb = if ($DryRun) { "Would apply" } else { "Applied" }
    Write-Host "[SGDK Wrapper] $verb $totalChanges migration fix(es) across $($changedFiles.Count) file(s)."
}

# --- Salvar Marker File ---
if (-not $DryRun) {
    $markerData = @{
        scriptHash = $scriptHash
        timestamp  = (Get-Date -Format "o")
        totalChanges = $totalChanges
        filesProcessed = $files.Count
        changedFiles = $changedFiles
    }
    $markerData | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath $markerFile -Force
    Write-MigrationLog "Migration marker saved: $markerFile" "INFO"
}
