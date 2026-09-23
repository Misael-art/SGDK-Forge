<#
.SYNOPSIS
    Tests the -Integrity switch on Test-SgdkRequiredFile in sgdk_artifact_contracts.psm1.
#>

[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$WrapperRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$ModulePath = Join-Path $WrapperRoot 'lib\sgdk_artifact_contracts.psm1'
if (-not (Test-Path -LiteralPath $ModulePath -PathType Leaf)) {
    throw "Module not found: $ModulePath"
}
Import-Module $ModulePath -Force

$script:passed = 0
$script:failed = 0
$TmpDir = Join-Path ([System.IO.Path]::GetTempPath()) ('sgdk_integrity_test_{0}' -f ([guid]::NewGuid().ToString('N')))
New-Item -ItemType Directory -Force -Path $TmpDir | Out-Null

function Assert-True {
    param([string]$Name, [bool]$Condition, [string]$Detail = '')
    if ($Condition) { $script:passed++; Write-Host "  [PASS] $Name" }
    else { $script:failed++; Write-Host "  [FAIL] $Name -- $Detail" }
}

function Write-BinaryFile {
    param([string]$Name, [byte[]]$Bytes)
    $path = Join-Path $TmpDir $Name
    [System.IO.File]::WriteAllBytes($path, $Bytes)
    return $path
}

function Write-TextFile {
    param([string]$Name, [string]$Content = 'test')
    $path = Join-Path $TmpDir $Name
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($path, $Content, $utf8NoBom)
    return $path
}

function Set-Ascii {
    param([byte[]]$Buffer, [int]$Offset, [string]$Value)
    [System.Text.Encoding]::ASCII.GetBytes($Value).CopyTo($Buffer, $Offset)
}

function Set-U16BE {
    param([byte[]]$Buffer, [int]$Offset, [int]$Value)
    $Buffer[$Offset] = [byte](($Value -shr 8) -band 0xFF)
    $Buffer[$Offset + 1] = [byte]($Value -band 0xFF)
}

function New-MdrtSram {
    param([int]$Offset = 0x200)
    $wordCount = 64
    $totalBytes = 10 + ($wordCount * 2)
    $bytes = New-Object byte[] ([Math]::Max(1024, $Offset + $totalBytes))
    Set-Ascii -Buffer $bytes -Offset $Offset -Value 'MDRT'
    Set-U16BE -Buffer $bytes -Offset ($Offset + 4) -Value 1
    Set-U16BE -Buffer $bytes -Offset ($Offset + 6) -Value $totalBytes
    Set-U16BE -Buffer $bytes -Offset ($Offset + 8) -Value $wordCount
    return ,$bytes
}

function New-VlabSram {
    param([int]$Offset = 0x200)
    $totalBytes = 16
    $bytes = New-Object byte[] ([Math]::Max(1536, $Offset + $totalBytes))
    Set-Ascii -Buffer $bytes -Offset $Offset -Value 'VLAB'
    Set-U16BE -Buffer $bytes -Offset ($Offset + 4) -Value 1
    Set-U16BE -Buffer $bytes -Offset ($Offset + 6) -Value $totalBytes
    return ,$bytes
}

function New-ReadySram {
    param([int]$Offset = 0x100)
    $bytes = New-Object byte[] 512
    Set-Ascii -Buffer $bytes -Offset $Offset -Value 'READY'
    return ,$bytes
}

Write-Host '--- Basic Test-SgdkRequiredFile ---'
$emptyFile = Write-TextFile 'empty.txt' ''
$nonEmptyFile = Write-TextFile 'nonempty.txt' 'hello'
Assert-True 'empty file returns false' (-not (Test-SgdkRequiredFile -FilePath $emptyFile))
Assert-True 'non-empty file returns true' (Test-SgdkRequiredFile -FilePath $nonEmptyFile) $nonEmptyFile
Assert-True 'missing file returns false' (-not (Test-SgdkRequiredFile -FilePath (Join-Path $TmpDir 'nope.txt')))

Write-Host '--- PNG Integrity ---'
$pngMagic = [byte[]]@(0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A)
$pngMinimal = $pngMagic + [byte[]]@(
    0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
    0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53, 0xDE,
    0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41, 0x54, 0x08, 0xD7, 0x63, 0x60, 0x00, 0x00, 0x00, 0x02,
    0x00, 0x01, 0xE5, 0x27, 0xDE, 0xFC, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44, 0xAE, 0x42,
    0x60, 0x82
)
$pngPath = Write-BinaryFile 'test.png' $pngMinimal
$fakePng = Write-TextFile 'fake.png' 'not a png'
Assert-True 'valid PNG passes integrity' (Test-SgdkRequiredFile -FilePath $pngPath -Integrity)
Assert-True 'fake PNG fails integrity' (-not (Test-SgdkRequiredFile -FilePath $fakePng -Integrity))
Assert-True 'PNG without -Integrity passes on size only' (Test-SgdkRequiredFile -FilePath $fakePng)

Write-Host '--- SRAM Integrity ---'
$sramBad = [byte[]]@(0xFF, 0xFF, 0xFF, 0xFF)
$sramPath = Write-BinaryFile 'test.sram' (New-MdrtSram -Offset 0x200)
$legacyMdrtPath = Write-BinaryFile 'legacy_mdrt.sram' (New-MdrtSram -Offset 0x0)
$sramBadPath = Write-BinaryFile 'bad.sram' $sramBad
Assert-True 'SRAM with MDRT at 0x200 passes integrity' (Test-SgdkRequiredFile -FilePath $sramPath -Integrity)
Assert-True 'SRAM with legacy MDRT at 0x0 passes integrity' (Test-SgdkRequiredFile -FilePath $legacyMdrtPath -Integrity)
Assert-True 'SRAM without magic fails integrity' (-not (Test-SgdkRequiredFile -FilePath $sramBadPath -Integrity))
Assert-True 'SRAM without -Integrity passes on size only' (Test-SgdkRequiredFile -FilePath $sramBadPath)

# VLAB
$vlab0Path = Write-BinaryFile 'vlab_0.sram' (New-VlabSram -Offset 0x0)
$vlab200Path = Write-BinaryFile 'vlab_200.sram' (New-VlabSram -Offset 0x200)
$vlab400Path = Write-BinaryFile 'vlab_400.sram' (New-VlabSram -Offset 0x400)
Assert-True 'SRAM with VLAB at 0x0 passes integrity' (Test-SgdkRequiredFile -FilePath $vlab0Path -Integrity)
Assert-True 'SRAM with VLAB at 0x200 passes integrity' (Test-SgdkRequiredFile -FilePath $vlab200Path -Integrity)
Assert-True 'SRAM with VLAB at 0x400 passes integrity' (Test-SgdkRequiredFile -FilePath $vlab400Path -Integrity)

# READY
$readyPath = Write-BinaryFile 'ready.sram' (New-ReadySram -Offset 0x100)
$readyAtZeroPath = Write-BinaryFile 'ready_zero.sram' (New-ReadySram -Offset 0x0)
$readyMdrt = New-MdrtSram -Offset 0x200
Set-Ascii -Buffer $readyMdrt -Offset 0x100 -Value 'READY'
$readyMdrtPath = Write-BinaryFile 'ready_mdrt.sram' $readyMdrt
Assert-True 'SRAM with READY at 0x100 passes integrity' (Test-SgdkRequiredFile -FilePath $readyPath -Integrity)
Assert-True 'SRAM with READY at 0x0 fails integrity' (-not (Test-SgdkRequiredFile -FilePath $readyAtZeroPath -Integrity))
Assert-True 'SRAM with READY at 0x100 and MDRT at 0x200 passes integrity' (Test-SgdkRequiredFile -FilePath $readyMdrtPath -Integrity)

Write-Host '--- VDP Dump Integrity (.bin) ---'
$vdpDump = [byte[]]@(0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F)
$vdpPath = Write-BinaryFile 'visual_vdp_dump.bin' $vdpDump
$uniformBin = [byte[]]@(0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF)
$uniformPath = Write-BinaryFile 'uniform.bin' $uniformBin
$tooShort = [byte[]]@(0x00, 0x01)
$shortPath = Write-BinaryFile 'short.bin' $tooShort
Assert-True 'VDP dump with variation passes integrity' (Test-SgdkRequiredFile -FilePath $vdpPath -Integrity)
Assert-True 'uniform VDP dump fails integrity' (-not (Test-SgdkRequiredFile -FilePath $uniformPath -Integrity -Kind VdpDump))
Assert-True 'too short VDP dump fails integrity' (-not (Test-SgdkRequiredFile -FilePath $shortPath -Integrity -Kind VdpDump))
$genericBinPath = Write-BinaryFile 'generic.bin' ([byte[]]@(0x01, 0x02, 0x03, 0x04))
Assert-True 'generic .bin with MinBytes passes integrity' (Test-SgdkRequiredFile -FilePath $genericBinPath -Integrity -MinBytes 4)
Assert-True 'generic .bin below MinBytes fails integrity' (-not (Test-SgdkRequiredFile -FilePath $genericBinPath -Integrity -MinBytes 8))

Write-Host '--- Extension fallback ---'
$txtPath = Write-TextFile 'notes.txt' 'some data'
Assert-True 'unknown extension without Integrity returns true' (Test-SgdkRequiredFile -FilePath $txtPath)
Assert-True 'unknown extension with Integrity returns false' (-not (Test-SgdkRequiredFile -FilePath $txtPath -Integrity))
Assert-True 'unknown extension with explicit Kind=Bin returns true' (Test-SgdkRequiredFile -FilePath $txtPath -Integrity -Kind Bin -MinBytes 4)

Remove-Item -LiteralPath $TmpDir -Recurse -Force

Write-Host ''
Write-Host "=== Results: $script:passed passed, $script:failed failed ==="
if ($script:failed -gt 0) { exit 1 }
exit 0
