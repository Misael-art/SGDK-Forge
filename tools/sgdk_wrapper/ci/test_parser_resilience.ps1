<#
.SYNOPSIS
  Harness de resiliencia para parse_blastem_sram_runtime.ps1.

.DESCRIPTION
  Gera SRAM sinteticos em tempdir e valida que o parser rejeita entradas
  corrompidas com mensagem descritiva, mas aceita entradas validas.

  Cenarios cobertos:
    1) SRAM valida minima (wordCount=64, 0 samples)       -> sucesso + JSON
    2) SRAM com assinatura errada (nao-MDRT)              -> deve throw
    3) SRAM muito curta para o header                     -> deve throw
    4) SRAM com wordCount > MDRT_WORDCOUNT_MAX (8192)     -> deve throw (guarda anti-DoS)
    5) SRAM com wordCount < 64                            -> deve throw
    6) SRAM com payload truncado (declara 100, tem 50)    -> deve throw
    7) SRAM com 1800 samples realistas                    -> sucesso + avg calculado

.NOTES
  Exit 0: todos os cenarios passaram.
  Exit 1: pelo menos um cenario divergiu do esperado.

.EXAMPLE
  PS> tools\sgdk_wrapper\ci\test_parser_resilience.ps1
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [switch]$Verbose
)

$ErrorActionPreference = 'Continue'
Set-StrictMode -Version 3.0

$parser = Join-Path $PSScriptRoot '..\parse_blastem_sram_runtime.ps1'
if (-not (Test-Path -LiteralPath $parser)) {
    Write-Error "Parser nao encontrado: $parser"
    exit 2
}

$tempRoot = Join-Path $env:TEMP ('mdrt_parser_harness_' + [guid]::NewGuid().ToString('N').Substring(0, 8))
New-Item -ItemType Directory -Path $tempRoot -Force | Out-Null

$failures = 0
$cases = 0

function Write-U16BE {
    param([byte[]]$Buffer, [int]$Offset, [int]$Value)
    $Buffer[$Offset] = [byte](($Value -shr 8) -band 0xFF)
    $Buffer[$Offset + 1] = [byte]($Value -band 0xFF)
}

function New-SyntheticMdrt {
    param(
        [int]$WordCount = 64,
        [int]$SamplesRecorded = 0,
        [int]$TargetFps = 60,
        [int]$SceneId = 1,
        [int]$SchemaVersion = 3,
        [int[]]$SampleValues = @(),
        [int]$PayloadWordCountOverride = -1
    )

    $headerStart = 0x200
    $payloadWords = if ($PayloadWordCountOverride -ge 0) { $PayloadWordCountOverride } else { $WordCount }
    $totalSize = $headerStart + 10 + ($payloadWords * 2)
    $buf = New-Object byte[] $totalSize

    # Magic "MDRT"
    $buf[$headerStart + 0] = [byte][char]'M'
    $buf[$headerStart + 1] = [byte][char]'D'
    $buf[$headerStart + 2] = [byte][char]'R'
    $buf[$headerStart + 3] = [byte][char]'T'
    Write-U16BE $buf ($headerStart + 4) 3    # schema
    Write-U16BE $buf ($headerStart + 6) (10 + $WordCount * 2) # total_bytes
    Write-U16BE $buf ($headerStart + 8) $WordCount

    # Header words (primeiros 32 words do payload, relativos)
    $payloadStart = $headerStart + 10
    Write-U16BE $buf ($payloadStart + (2 * 2)) 3          # schema_version idx=2
    Write-U16BE $buf ($payloadStart + (4 * 2)) $TargetFps # idx=4
    Write-U16BE $buf ($payloadStart + (5 * 2)) $SceneId   # idx=5
    Write-U16BE $buf ($payloadStart + (8 * 2)) $SamplesRecorded # frames_seen idx=8
    Write-U16BE $buf ($payloadStart + (9 * 2)) $SamplesRecorded # samples_recorded idx=9

    # Samples em idx 32..32+samples
    $i = 0
    foreach ($sv in $SampleValues) {
        Write-U16BE $buf ($payloadStart + ((32 + $i) * 2)) $sv
        $i++
        if ($i -ge $SamplesRecorded) { break }
    }

    return ,$buf
}

function Save-Binary {
    param([string]$Path, [byte[]]$Bytes)
    [System.IO.File]::WriteAllBytes($Path, $Bytes)
}

function Assert-Case {
    param(
        [string]$Name,
        [string]$SramPath,
        [ValidateSet('pass', 'throw')][string]$Expected,
        [string]$ExpectPattern = ''
    )

    $script:cases++
    $outJson = [System.IO.Path]::GetTempFileName()
    $stderr = $null
    $threw = $false
    $stdout = $null

    try {
        $stdout = & $parser -SramPath $SramPath -OutputPath $outJson -SramOffset 0x200 -FrameWindow 1800 2>&1
        $exitOk = ($LASTEXITCODE -eq 0 -or $null -eq $LASTEXITCODE)
    } catch {
        $threw = $true
        $stderr = $_.Exception.Message
    }

    $result = 'UNKNOWN'
    if ($Expected -eq 'pass') {
        if (-not $threw -and (Test-Path -LiteralPath $outJson) -and (Get-Item -LiteralPath $outJson).Length -gt 0) {
            $result = 'OK'
        } else {
            $errMsg = if ($stderr) { $stderr } else { 'sem JSON de saida' }
            $result = 'FAIL (esperado sucesso, mas: ' + $errMsg + ')'
            $script:failures++
        }
    } else {
        # Expected throw
        $msg = ''
        if ($threw) { $msg = $stderr }
        elseif ($stdout) { $msg = ($stdout | Out-String) }

        if (-not $threw -and -not ($stdout -match 'throw|invalido|nao contem|curta|Assinatura')) {
            # Parser silenciou um erro -> falha
            $result = "FAIL (esperado throw, mas nao houve; stdout=$($stdout | Out-String))"
            $script:failures++
        } elseif ($ExpectPattern -and $msg -notmatch $ExpectPattern) {
            $result = "FAIL (throw aconteceu mas mensagem nao bate pattern '$ExpectPattern': $msg)"
            $script:failures++
        } else {
            $result = 'OK (throw esperado)'
        }
    }

    Write-Host ("[{0,-42}] {1}" -f $Name, $result)
    if ($Verbose -and $stderr) { Write-Host "   stderr: $stderr" }

    if (Test-Path -LiteralPath $outJson) { Remove-Item -LiteralPath $outJson -Force -ErrorAction SilentlyContinue }
}

try {
    # Case 1: minimo valido
    $p1 = Join-Path $tempRoot 'c1_minimo.sram'
    Save-Binary $p1 (New-SyntheticMdrt -WordCount 64 -SamplesRecorded 0)
    Assert-Case -Name 'C1: SRAM minima valida' -SramPath $p1 -Expected 'pass'

    # Case 2: assinatura errada
    $p2 = Join-Path $tempRoot 'c2_assinatura_ruim.sram'
    $bad = New-SyntheticMdrt -WordCount 64 -SamplesRecorded 0
    $bad[0x200] = [byte][char]'X'
    Save-Binary $p2 $bad
    Assert-Case -Name 'C2: Assinatura MDRT corrompida' -SramPath $p2 -Expected 'throw' -ExpectPattern 'Assinatura MDRT'

    # Case 3: muito curta (menos que header)
    $p3 = Join-Path $tempRoot 'c3_curta.sram'
    Save-Binary $p3 (New-Object byte[] 0x205)
    Assert-Case -Name 'C3: SRAM curta demais' -SramPath $p3 -Expected 'throw' -ExpectPattern 'curta|Assinatura'

    # Case 4: wordCount > 8192 (anti-DoS)
    $p4 = Join-Path $tempRoot 'c4_wordcount_huge.sram'
    $huge = New-Object byte[] 0x300
    # Magic
    $huge[0x200] = [byte][char]'M'; $huge[0x201] = [byte][char]'D'; $huge[0x202] = [byte][char]'R'; $huge[0x203] = [byte][char]'T'
    Write-U16BE $huge 0x204 3
    Write-U16BE $huge 0x206 20
    Write-U16BE $huge 0x208 65535  # wordCount inflado
    Save-Binary $p4 $huge
    Assert-Case -Name 'C4: wordCount > MAX (anti-DoS)' -SramPath $p4 -Expected 'throw' -ExpectPattern 'wordCount'

    # Case 5: wordCount < 64
    $p5 = Join-Path $tempRoot 'c5_wordcount_small.sram'
    $small = New-Object byte[] 0x300
    $small[0x200] = [byte][char]'M'; $small[0x201] = [byte][char]'D'; $small[0x202] = [byte][char]'R'; $small[0x203] = [byte][char]'T'
    Write-U16BE $small 0x204 3
    Write-U16BE $small 0x206 30
    Write-U16BE $small 0x208 10  # < MIN 64
    Save-Binary $p5 $small
    Assert-Case -Name 'C5: wordCount < MIN' -SramPath $p5 -Expected 'throw' -ExpectPattern 'wordCount'

    # Case 6: payload truncado (declara 128, mas arquivo tem so header + 50 words)
    $p6 = Join-Path $tempRoot 'c6_truncado.sram'
    $truncSize = 0x200 + 10 + (50 * 2)
    $trunc = New-Object byte[] $truncSize
    $trunc[0x200] = [byte][char]'M'; $trunc[0x201] = [byte][char]'D'; $trunc[0x202] = [byte][char]'R'; $trunc[0x203] = [byte][char]'T'
    Write-U16BE $trunc 0x204 3
    Write-U16BE $trunc 0x206 (10 + 128 * 2)
    Write-U16BE $trunc 0x208 128  # declara 128 mas arquivo so tem 50
    Save-Binary $p6 $trunc
    Assert-Case -Name 'C6: Payload truncado' -SramPath $p6 -Expected 'throw' -ExpectPattern 'payload|completo'

    # Case 7: 1800 samples realistas
    $p7 = Join-Path $tempRoot 'c7_full_samples.sram'
    $samples = 1..1800 | ForEach-Object { Get-Random -Minimum 1500 -Maximum 3500 }
    $words7 = 32 + 1800
    Save-Binary $p7 (New-SyntheticMdrt -WordCount $words7 -SamplesRecorded 1800 -SampleValues $samples)
    Assert-Case -Name 'C7: 1800 samples realistas' -SramPath $p7 -Expected 'pass'
}
finally {
    if (Test-Path -LiteralPath $tempRoot) {
        Remove-Item -LiteralPath $tempRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Write-Host ""
Write-Host ("Casos: {0}  Falhas: {1}" -f $cases, $failures)
if ($failures -gt 0) {
    Write-Host "HARNESS FALHOU" -ForegroundColor Red
    exit 1
}
Write-Host "HARNESS OK" -ForegroundColor Green
exit 0
