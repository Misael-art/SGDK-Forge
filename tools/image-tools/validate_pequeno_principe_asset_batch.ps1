param(
    [string]$BatchRoot = (Join-Path $PSScriptRoot '..\..\tmp\imagegen\inbox\pequeno_principe_v2')
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$BatchRoot = [System.IO.Path]::GetFullPath($BatchRoot)

Add-Type -AssemblyName System.Drawing
Add-Type -ReferencedAssemblies 'System.Drawing.dll' @"
using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.Collections.Generic;

public class PpImageInfo
{
    public int Width;
    public int Height;
    public string PixelFormat;
    public int UniqueColors;
    public bool HasAlphaPixels;
    public bool HasPaletteTransparency;
    public bool IsIndexed;
}

public static class PpImageInspector
{
    public static PpImageInfo Inspect(string path)
    {
        using (var bmp = new Bitmap(path))
        {
            var info = new PpImageInfo();
            info.Width = bmp.Width;
            info.Height = bmp.Height;
            info.PixelFormat = bmp.PixelFormat.ToString();
            info.IsIndexed = (bmp.PixelFormat & PixelFormat.Indexed) != 0;

            var colors = new HashSet<int>();
            bool hasAlpha = false;
            bool hasPaletteTransparency = false;

            if (info.IsIndexed)
            {
                foreach (Color entry in bmp.Palette.Entries)
                {
                    if (entry.A < 255)
                    {
                        hasPaletteTransparency = true;
                        break;
                    }
                }
            }

            for (int y = 0; y < bmp.Height; y++)
            {
                for (int x = 0; x < bmp.Width; x++)
                {
                    Color pixel = bmp.GetPixel(x, y);
                    colors.Add(pixel.ToArgb());
                    if (pixel.A < 255)
                    {
                        hasAlpha = true;
                    }
                }
            }

            info.UniqueColors = colors.Count;
            info.HasAlphaPixels = hasAlpha;
            info.HasPaletteTransparency = hasPaletteTransparency;
            return info;
        }
    }
}
"@

function Join-Batch([string]$RelativePath)
{
    return Join-Path $BatchRoot $RelativePath
}

function Inspect-Asset([string]$Path)
{
    return [PpImageInspector]::Inspect($Path)
}

$productionSpecs = @(
    @{ Name = 'pal_sprite_stage_ref'; Rel = 'production\pal_sprite_stage_ref.png'; Width = 128; Height = 8; MaxColors = 16; RequireTransparency = $false; IndexedRel = 'indexed\pal_sprite_stage.bmp'; IndexedWidth = 16; IndexedHeight = 1 },
    @{ Name = 'pp_base_tiles_shared'; Rel = 'production\pp_base_tiles_shared.png'; Width = 32; Height = 32; MaxColors = 16; RequireTransparency = $false; IndexedRel = 'indexed\pp_base_tiles_shared.bmp'; IndexedWidth = 32; IndexedHeight = 32 },
    @{ Name = 'pp_player_body'; Rel = 'production\pp_player_body.png'; Width = 16; Height = 24; MaxColors = 16; RequireTransparency = $true; IndexedRel = 'indexed\pp_player_body.bmp'; IndexedWidth = 16; IndexedHeight = 24 },
    @{ Name = 'pp_player_scarf'; Rel = 'production\pp_player_scarf.png'; Width = 8; Height = 8; MaxColors = 16; RequireTransparency = $true; IndexedRel = 'indexed\pp_player_scarf.bmp'; IndexedWidth = 8; IndexedHeight = 8 },
    @{ Name = 'pp_player_halo'; Rel = 'production\pp_player_halo.png'; Width = 16; Height = 16; MaxColors = 16; RequireTransparency = $true; IndexedRel = 'indexed\pp_player_halo.bmp'; IndexedWidth = 16; IndexedHeight = 16 },
    @{ Name = 'rose_mark'; Rel = 'production\rose_mark.png'; Width = 16; Height = 16; MaxColors = 16; RequireTransparency = $true; IndexedRel = 'indexed\rose_mark.bmp'; IndexedWidth = 16; IndexedHeight = 16 },
    @{ Name = 'throne_mark'; Rel = 'production\throne_mark.png'; Width = 16; Height = 16; MaxColors = 16; RequireTransparency = $true; IndexedRel = 'indexed\throne_mark.bmp'; IndexedWidth = 16; IndexedHeight = 16 },
    @{ Name = 'lamp_mark'; Rel = 'production\lamp_mark.png'; Width = 16; Height = 16; MaxColors = 16; RequireTransparency = $true; IndexedRel = 'indexed\lamp_mark.bmp'; IndexedWidth = 16; IndexedHeight = 16 },
    @{ Name = 'desert_mark'; Rel = 'production\desert_mark.png'; Width = 16; Height = 16; MaxColors = 16; RequireTransparency = $true; IndexedRel = 'indexed\desert_mark.bmp'; IndexedWidth = 16; IndexedHeight = 16 },
    @{ Name = 'pp_ui_panels'; Rel = 'production\pp_ui_panels.png'; Width = 32; Height = 16; MaxColors = 16; RequireTransparency = $false; IndexedRel = 'indexed\pp_ui_panels.bmp'; IndexedWidth = 32; IndexedHeight = 16 },
    @{ Name = 'pp_orbit_icons'; Rel = 'production\pp_orbit_icons.png'; Width = 32; Height = 8; MaxColors = 16; RequireTransparency = $true; IndexedRel = 'indexed\pp_orbit_icons.bmp'; IndexedWidth = 32; IndexedHeight = 8 }
)

$boardSpecs = @(
    @{ Name = 'board_title_scene'; Rel = 'boards\board_title_scene.png'; Width = 320; Height = 224 },
    @{ Name = 'board_b612'; Rel = 'boards\board_b612.png'; Width = 320; Height = 224 },
    @{ Name = 'board_king'; Rel = 'boards\board_king.png'; Width = 320; Height = 224 },
    @{ Name = 'board_lamp'; Rel = 'boards\board_lamp.png'; Width = 320; Height = 224 },
    @{ Name = 'board_desert'; Rel = 'boards\board_desert.png'; Width = 320; Height = 224 },
    @{ Name = 'board_travel'; Rel = 'boards\board_travel.png'; Width = 320; Height = 224 }
)

$failures = New-Object System.Collections.Generic.List[string]
$rows = New-Object System.Collections.Generic.List[object]

foreach ($spec in $productionSpecs)
{
    $prodPath = Join-Batch $spec.Rel
    if (-not (Test-Path -LiteralPath $prodPath))
    {
        $failures.Add("Falta arquivo de producao: $($spec.Rel)")
        continue
    }

    $prodInfo = Inspect-Asset $prodPath
    $prodTransparency = $prodInfo.HasAlphaPixels -or $prodInfo.HasPaletteTransparency
    $prodSizeOk = ($prodInfo.Width -eq $spec.Width -and $prodInfo.Height -eq $spec.Height)
    $prodColorOk = ($prodInfo.UniqueColors -le $spec.MaxColors)
    $prodTransparencyOk = (-not $spec.RequireTransparency) -or $prodTransparency

    if (-not $prodSizeOk) { $failures.Add("$($spec.Rel) com tamanho incorreto: $($prodInfo.Width)x$($prodInfo.Height), esperado $($spec.Width)x$($spec.Height)") }
    if (-not $prodColorOk) { $failures.Add("$($spec.Rel) excede limite de cores: $($prodInfo.UniqueColors) cores") }
    if (-not $prodTransparencyOk) { $failures.Add("$($spec.Rel) sem transparencia util para asset recortado") }

    $indexedPath = Join-Batch $spec.IndexedRel
    if (-not (Test-Path -LiteralPath $indexedPath))
    {
        $failures.Add("Falta contraparte indexada: $($spec.IndexedRel)")
        $rows.Add([pscustomobject]@{
            File = $spec.Rel
            Kind = 'production'
            Size = "$($prodInfo.Width)x$($prodInfo.Height)"
            PixelFormat = $prodInfo.PixelFormat
            Colors = $prodInfo.UniqueColors
            Indexed = 'missing'
            Status = if ($prodSizeOk -and $prodColorOk -and $prodTransparencyOk) { 'WARN' } else { 'FAIL' }
        })
        continue
    }

    $indexedInfo = Inspect-Asset $indexedPath
    $indexedSizeOk = ($indexedInfo.Width -eq $spec.IndexedWidth -and $indexedInfo.Height -eq $spec.IndexedHeight)
    $indexedColorOk = ($indexedInfo.UniqueColors -le 16)
    $indexedFormatOk = $indexedInfo.IsIndexed

    if (-not $indexedSizeOk) { $failures.Add("$($spec.IndexedRel) com tamanho incorreto: $($indexedInfo.Width)x$($indexedInfo.Height), esperado $($spec.IndexedWidth)x$($spec.IndexedHeight)") }
    if (-not $indexedColorOk) { $failures.Add("$($spec.IndexedRel) excede limite de cores: $($indexedInfo.UniqueColors) cores") }
    if (-not $indexedFormatOk) { $failures.Add("$($spec.IndexedRel) nao esta indexado: $($indexedInfo.PixelFormat)") }

    $rows.Add([pscustomobject]@{
        File = $spec.Rel
        Kind = 'production'
        Size = "$($prodInfo.Width)x$($prodInfo.Height)"
        PixelFormat = $prodInfo.PixelFormat
        Colors = $prodInfo.UniqueColors
        Indexed = "$($indexedInfo.Width)x$($indexedInfo.Height) / $($indexedInfo.PixelFormat) / $($indexedInfo.UniqueColors)c"
        Status = if ($prodSizeOk -and $prodColorOk -and $prodTransparencyOk -and $indexedSizeOk -and $indexedColorOk -and $indexedFormatOk) { 'PASS' } else { 'FAIL' }
    })
}

foreach ($spec in $boardSpecs)
{
    $boardPath = Join-Batch $spec.Rel
    if (-not (Test-Path -LiteralPath $boardPath))
    {
        $failures.Add("Falta board de referencia: $($spec.Rel)")
        continue
    }

    $boardInfo = Inspect-Asset $boardPath
    $boardSizeOk = ($boardInfo.Width -eq $spec.Width -and $boardInfo.Height -eq $spec.Height)
    if (-not $boardSizeOk) { $failures.Add("$($spec.Rel) com tamanho incorreto: $($boardInfo.Width)x$($boardInfo.Height), esperado $($spec.Width)x$($spec.Height)") }

    $rows.Add([pscustomobject]@{
        File = $spec.Rel
        Kind = 'board'
        Size = "$($boardInfo.Width)x$($boardInfo.Height)"
        PixelFormat = $boardInfo.PixelFormat
        Colors = $boardInfo.UniqueColors
        Indexed = '-'
        Status = if ($boardSizeOk) { 'PASS' } else { 'FAIL' }
    })
}

Write-Output "BatchRoot: $BatchRoot"
Write-Output ''
$rows | Sort-Object Kind, File | Format-Table -AutoSize
Write-Output ''

if ($failures.Count -gt 0)
{
    Write-Output 'Falhas detectadas:'
    foreach ($failure in $failures)
    {
        Write-Output "- $failure"
    }
    exit 1
}

Write-Output 'Lote aprovado para integracao tecnica.'
exit 0
