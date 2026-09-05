param(
    [string]$ProjectRoot = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = "Stop"

function Read-ProjectFile {
    param([Parameter(Mandatory = $true)][string]$RelativePath)

    $path = Join-Path $ProjectRoot $RelativePath
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Arquivo ausente: $RelativePath"
    }
    return Get-Content -LiteralPath $path -Raw
}

function Assert-Contains {
    param(
        [Parameter(Mandatory = $true)][string]$Text,
        [Parameter(Mandatory = $true)][string]$Pattern,
        [Parameter(Mandatory = $true)][string]$Message
    )

    if ($Text -notmatch $Pattern) {
        throw $Message
    }
}

function Assert-NotContains {
    param(
        [Parameter(Mandatory = $true)][string]$Text,
        [Parameter(Mandatory = $true)][string]$Pattern,
        [Parameter(Mandatory = $true)][string]$Message
    )

    if ($Text -match $Pattern) {
        throw $Message
    }
}

$title = Read-ProjectFile "src/scenes/title_scene.c"
$road = Read-ProjectFile "src/race/road_renderer.c"
$hud = Read-ProjectFile "src/race/race_hud.c"
$resources = Read-ProjectFile "src/race/race_resources.c"
$entities = Read-ProjectFile "src/race/race_entities.c"
$race = Read-ProjectFile "src/scenes/race_scene.c"
$metrics = Read-ProjectFile "src/race/race_metrics.c"
$result = Read-ProjectFile "src/scenes/result_scene.c"

Assert-Contains $title "TITLE_BG_TILE_BASE" "Title precisa declarar base explicita de VRAM."
Assert-Contains $title "TILE_ATTR_FULL" "Title precisa carregar imagens com tile index explicito."
Assert-NotContains $title "VDP_drawImageEx\([^\r\n]+TILE_ATTR\(" "Title ainda carrega imagem em tile index zero."

Assert-Contains $road "VDP_loadTileSet" "Road precisa carregar o tileset sem desenhar uma IMAGE em tile zero."
Assert-Contains $road "TILE_ATTR_FULL" "Tilemap da estrada precisa carregar paleta e tile index explicitamente."
Assert-NotContains $road "VDP_drawImageEx" "Road nao deve usar VDP_drawImageEx apenas para carregar tiles."

Assert-Contains $hud "VDP_setWindowOnTop" "HUD precisa reservar a faixa fixa de WINDOW."
Assert-Contains $hud "VDP_setTextPlane\(WINDOW\)" "HUD precisa escrever no WINDOW, nao no BG_A rolavel."

Assert-Contains $resources "res\.pulse_cooldown--" "Cooldown do Pulse precisa diminuir a cada frame."
Assert-Contains $entities "COLLISION_LAYER_TRIGGER" "Entidades trigger precisam possuir caminho de runtime."

Assert-NotContains $race "u8 phase = Player_getVisualYOffset" "Offset negativo do salto nao pode ser convertido para u8."
Assert-NotContains $race "py \+ Player_getVisualYOffset\(\)" "Offset vertical do salto esta sendo aplicado duas vezes."
Assert-Contains $race "beacon_collected" "Conclusao do setor precisa depender do Beacon."
Assert-Contains $race "set_sprite_definition_checked" "Falha de SPR_setDefinition precisa ser tratada por helper."
Assert-Contains $race "return SPR_setDefinition\(sprite, def\)" "Helper precisa propagar falha de SPR_setDefinition."

Assert-Contains $metrics "static u32 pressure_sum" "Acumulador de Pressure precisa evitar overflow u16."
Assert-Contains $metrics "sector_cleared" "Metricas precisam diferenciar sucesso de falha."
Assert-Contains $result "sector_cleared" "Tela de resultado precisa diferenciar sucesso de falha."

Write-Host "[PASS] Sector 01 recovery contracts satisfied."
