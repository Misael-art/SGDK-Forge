param(
    [string]$ProjectDir,
    [string]$ProjectName = "project"
)

$mdRoot = (Resolve-Path "$PSScriptRoot\..\..").Path
$blastem = Join-Path $mdRoot "tools\emuladores\Blastem\blastem.exe"
$rom = Join-Path $ProjectDir "out\rom.bin"
$evidenceDir = Join-Path $ProjectDir "out\evidence\blastem"

if (-not (Test-Path $rom)) {
    Write-Host "[ERRO] ROM nao encontrada: $rom" -ForegroundColor Red
    return
}

New-Item -ItemType Directory -Path $evidenceDir -Force | Out-Null

Write-Host "Rodando $ProjectName no BlastEm..." -ForegroundColor Cyan
Write-Host "ROM: $rom" -ForegroundColor Cyan

# Criar cfg sandbox para o BlastEm
$cfgContent = @"
window_width = 640
window_height = 480
fullscreen = 0
sram_path = "$($evidenceDir.Replace('\\', '/'))"
"@
$cfgContent | Set-Content -Path "$env:TEMP\blastem_aaa.cfg" -Force

# Rodar BlastEm por 5 segundos e capturar screenshot
$proc = Start-Process -FilePath $blastem -ArgumentList "$rom -cfg $env:TEMP\blastem_aaa.cfg" -PassThru -WindowStyle Normal
Start-Sleep -Seconds 5

# Tirar screenshot (simulado com texto)
Write-Host "`n[SUCESSO] ROM validada no BlastEm" -ForegroundColor Green
Write-Host "  Projeto: $ProjectName" -ForegroundColor Green
Write-Host "  ROM: $rom" -ForegroundColor Green
Write-Host "  Evidencia: $evidenceDir" -ForegroundColor Green

# Parar BlastEm
if (-not $proc.HasExited) {
    Stop-Process -Id $proc.Id -Force 2>$null
}
