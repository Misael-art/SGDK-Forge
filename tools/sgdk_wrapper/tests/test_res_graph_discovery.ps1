$ErrorActionPreference = 'Stop'
$root = Join-Path ([System.IO.Path]::GetTempPath()) ("res_graph_discovery_" + [guid]::NewGuid().ToString('N'))
try {
    New-Item -ItemType Directory -Path (Join-Path $root 'res'), (Join-Path $root 'rascunho/copy/res') -Force | Out-Null
    Set-Content -LiteralPath (Join-Path $root 'res/active.res') -Value 'IMAGE active active.png NONE'
    Set-Content -LiteralPath (Join-Path $root 'rascunho/copy/res/stale.res') -Value 'IMAGE active active.png NONE'
    Import-Module (Join-Path $PSScriptRoot '../lib/res_graph.psm1') -Force
    $active = @(Get-SgdkResFiles -ProjectRoot $root)
    if ($active.Count -ne 1 -or $active[0].Name -ne 'active.res') {
        throw "Default discovery included a draft: $($active.FullName -join ', ')"
    }
    $draft = @(Get-SgdkResFiles -ProjectRoot $root -ResPath @('rascunho/copy/res/stale.res'))
    if ($draft.Count -ne 1 -or $draft[0].Name -ne 'stale.res') {
        throw 'Explicit -ResPath did not select the draft'
    }
    Write-Output 'res_graph_discovery=passed'
}
finally {
    Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction SilentlyContinue
}
