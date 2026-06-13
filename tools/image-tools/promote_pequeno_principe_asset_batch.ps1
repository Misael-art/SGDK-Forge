param(
    [string]$BatchRoot = (Join-Path $PSScriptRoot '..\..\tmp\imagegen\inbox\pequeno_principe_v2'),
    [string]$ProjectRoot = (Join-Path $PSScriptRoot '..\..\SGDK_projects\Pequeno Principe Cronicas das Estrelas [VER.001] [SGDK 211] [GEN] [GAME] [AVENTURA]')
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$BatchRoot = [System.IO.Path]::GetFullPath($BatchRoot)
$ProjectRoot = [System.IO.Path]::GetFullPath($ProjectRoot)
$validator = Join-Path $PSScriptRoot 'validate_pequeno_principe_asset_batch.ps1'

& $validator -BatchRoot $BatchRoot
if ($LASTEXITCODE -ne 0)
{
    throw "Promocao cancelada: o lote nao passou na validacao."
}

$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$backupRoot = Join-Path $ProjectRoot "archives\promoted_asset_batches\$timestamp\previous_res"

$manifest = @(
    @{ Source = 'production\pal_sprite_stage_ref.png'; Dest = 'res\gfx\landmarks\pal_sprite_stage_ref.png' },
    @{ Source = 'indexed\pal_sprite_stage.bmp'; Dest = 'res\gfx\landmarks\pal_sprite_stage.bmp' },
    @{ Source = 'production\pp_base_tiles_shared.png'; Dest = 'res\gfx\pp_base_tiles_shared.png' },
    @{ Source = 'indexed\pp_base_tiles_shared.bmp'; Dest = 'res\gfx\pp_base_tiles_shared.bmp' },
    @{ Source = 'production\pp_player_body.png'; Dest = 'res\gfx\pp_player_body.png' },
    @{ Source = 'indexed\pp_player_body.bmp'; Dest = 'res\gfx\pp_player_body.bmp' },
    @{ Source = 'production\pp_player_scarf.png'; Dest = 'res\gfx\pp_player_scarf.png' },
    @{ Source = 'indexed\pp_player_scarf.bmp'; Dest = 'res\gfx\pp_player_scarf.bmp' },
    @{ Source = 'production\pp_player_halo.png'; Dest = 'res\gfx\pp_player_halo.png' },
    @{ Source = 'indexed\pp_player_halo.bmp'; Dest = 'res\gfx\pp_player_halo.bmp' },
    @{ Source = 'production\rose_mark.png'; Dest = 'res\gfx\landmarks\rose_mark.png' },
    @{ Source = 'indexed\rose_mark.bmp'; Dest = 'res\gfx\landmarks\rose_mark.bmp' },
    @{ Source = 'production\throne_mark.png'; Dest = 'res\gfx\landmarks\throne_mark.png' },
    @{ Source = 'indexed\throne_mark.bmp'; Dest = 'res\gfx\landmarks\throne_mark.bmp' },
    @{ Source = 'production\lamp_mark.png'; Dest = 'res\gfx\landmarks\lamp_mark.png' },
    @{ Source = 'indexed\lamp_mark.bmp'; Dest = 'res\gfx\landmarks\lamp_mark.bmp' },
    @{ Source = 'production\desert_mark.png'; Dest = 'res\gfx\landmarks\desert_mark.png' },
    @{ Source = 'indexed\desert_mark.bmp'; Dest = 'res\gfx\landmarks\desert_mark.bmp' },
    @{ Source = 'production\pp_ui_panels.png'; Dest = 'res\ui\pp_ui_panels.png' },
    @{ Source = 'indexed\pp_ui_panels.bmp'; Dest = 'res\ui\pp_ui_panels.bmp' },
    @{ Source = 'production\pp_orbit_icons.png'; Dest = 'res\ui\pp_orbit_icons.png' },
    @{ Source = 'indexed\pp_orbit_icons.bmp'; Dest = 'res\ui\pp_orbit_icons.bmp' },
    @{ Source = 'boards\board_title_scene.png'; Dest = 'res\gfx\boards\board_title_scene.png' },
    @{ Source = 'boards\board_b612.png'; Dest = 'res\gfx\boards\board_b612.png' },
    @{ Source = 'boards\board_king.png'; Dest = 'res\gfx\boards\board_king.png' },
    @{ Source = 'boards\board_lamp.png'; Dest = 'res\gfx\boards\board_lamp.png' },
    @{ Source = 'boards\board_desert.png'; Dest = 'res\gfx\boards\board_desert.png' },
    @{ Source = 'boards\board_travel.png'; Dest = 'res\gfx\boards\board_travel.png' }
)

$logLines = New-Object System.Collections.Generic.List[string]
$logLines.Add("Promocao de lote validado")
$logLines.Add("BatchRoot: $BatchRoot")
$logLines.Add("ProjectRoot: $ProjectRoot")
$logLines.Add("Timestamp: $timestamp")
$logLines.Add("")

foreach ($item in $manifest)
{
    $sourcePath = Join-Path $BatchRoot $item.Source
    $destPath = Join-Path $ProjectRoot $item.Dest
    $destDir = Split-Path -Parent $destPath

    New-Item -ItemType Directory -Path $destDir -Force | Out-Null

    if (Test-Path -LiteralPath $destPath)
    {
        $backupPath = Join-Path $backupRoot $item.Dest
        $backupDir = Split-Path -Parent $backupPath
        New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
        Copy-Item -LiteralPath $destPath -Destination $backupPath -Force
        $logLines.Add("BACKUP|$destPath|$backupPath")
    }

    Copy-Item -LiteralPath $sourcePath -Destination $destPath -Force
    $logLines.Add("PROMOTE|$sourcePath|$destPath")
}

$logPath = Join-Path $ProjectRoot "archives\promoted_asset_batches\$timestamp\promotion_manifest.txt"
$logDir = Split-Path -Parent $logPath
New-Item -ItemType Directory -Path $logDir -Force | Out-Null
[System.IO.File]::WriteAllLines($logPath, $logLines)

Write-Output "Lote promovido com sucesso."
Write-Output "Manifesto: $logPath"
