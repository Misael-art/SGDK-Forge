# MegaDrive_DEV Build Resilience System

Este documento descreve todas as estrategias de resiliencia, validacao e auto-correcao
implementadas no pipeline de build do SGDK.

---

## Visao Geral do Pipeline

```
build.bat                          # Converte para short path (8.3)
  └─ build_inner.bat               # Orquestrador principal
        ├─ fix_migration_issues.ps1 # Pre-processamento (APIs, boot, recursos)
        ├─ validate_resources.ps1   # Validacao pre-build (-Fix se AUTO_FIX=1)
        ├─ ensure_safe_image.ps1    # Sanitizacao de imagens individuais
        ├─ make -f makefile.gen     # Compilacao SGDK
       └─ [em caso de erro]
            ├─ Analise de log (findstr por padroes conhecidos)
            ├─ Aplicacao de fixers automaticos
            └─ Retry (ate 3 tentativas)
```

---

## 1. Paths com Colchetes [SGDK 211]

### Problema
Projetos em paths contendo colchetes (ex.: `BLAZE_ENGINE [VER.001] [SGDK 211]`)
causam falhas no CMD: o parser interpreta `[]` como padrao glob, corrompendo
comandos (`set`→`et`, `echo`→`cho`, labels nao reconhecidos).

### Solucao
1. **build.bat**: Converte para short path (8.3) e executa `build_inner.bat`
   no contexto do caminho curto.
2. **build_inner.bat**: Contem toda a logica; executa sempre em short path.
3. **Scripts PowerShell**: Rodam em subprocessos; usam `-LiteralPath` para
   evitar interpretacao de brackets.

### Requisito
O volume deve suportar nomes 8.3 (habilitado por padrao no Windows).

---

## 2. Boot Files Incompativeis (sega.s / rom_head.c)

### Problema
Projetos SGDK 160/200 possuem boot customizado em `src/boot/` que e
incompativel com SGDK 211. O `sega.s` do SGDK 211 define callbacks de
excecao (`zeroDivideCB`, `chkInstCB`, etc.) que nao existiam nas versoes
anteriores.

### Sintoma
```
undefined reference to 'zeroDivideCB'
undefined reference to 'chkInstCB'
```

### Solucao (Automatica)
`fix_migration_issues.ps1` Secao 2: compara MD5 hash do `src/boot/sega.s`
e `rom_head.c` do projeto com os padroes do SGDK 211. Se diferentes,
substitui automaticamente.

---

## 3. APIs Deprecadas (SGDK 160 → 211)

### Problema
SGDK 211 renomeou e reestruturou diversas APIs. Codigo escrito para SGDK 160
nao compila sem migracao.

### Sintoma
```
error: This method is deprecated, use PAL_setColors(..) instead
error: too many arguments to function 'SPR_addSpriteEx'
error: implicit declaration of function 'VDP_setPalette'
```

### Solucao (Automatica)
`fix_migration_issues.ps1` Secao 3: tabela de regras com regex e word
boundaries. Cada regra documenta a transformacao:

| API Antiga | API Nova | Transformacao |
|------------|----------|---------------|
| `VDP_setPaletteColors(a,b,c)` | `PAL_setColors(a,b,c, DMA)` | Adiciona TransferMethod |
| `VDP_setPaletteColor` | `PAL_setColor` | Rename simples |
| `VDP_setPalette(a,b)` | `PAL_setPalette(a,b, DMA)` | Adiciona TransferMethod |
| `PAL_setColorsDMA(a,b,c)` | `PAL_setColors(a,b,c, DMA)` | Remove variante DMA |
| `PAL_setPaletteDMA(a,b)` | `PAL_setPalette(a,b, DMA)` | Remove variante DMA |
| `SPR_addSpriteEx(6 args)` | `SPR_addSpriteEx(5 args)` | Remove sprIndex |
| `SPR_FLAG_AUTO_SPRITE_ALLOC` | `SPR_FLAG_AUTO_VRAM_ALLOC` | Rename |
| `VDP_showFPS(1 arg)` | `VDP_showFPS(3 args)` | Adiciona x,y |

### Seguranca das Regras
- **Word boundaries** (`\b`): evitam matches parciais (ex: `VDP_setPaletteColor`
  nao matcha dentro de `VDP_setPaletteColors`).
- **Ordem especifica→generica**: nomes mais longos sao processados primeiro.
- **Logging por regra**: cada aplicacao e registrada com arquivo, linha e regra.

---

## 4. Dependencias (.d) com Paths Absolutos

### Problema
Arquivos `.d` gerados pelo ResComp podem conter caminhos absolutos do
computador original (ex: `C:/Users/Bionica/Documents/...`). O make tenta
reconstruir essas dependencias inexistentes.

### Sintoma
```
cp: cannot stat 'res/gfx.d': No such file or directory
```

### Solucao (Automatica)
1. **build_inner.bat**: Antes do build, varre `out/` e deleta `.d` que
   contenham `C:/Users` ou `D:/Users`.
2. **build_inner.bat**: Apos falha com "cannot stat .d", cria stubs vazios
   e faz retry.

---

## 5. Inconsistencias de Paleta e Transparencia

### Problema
ResComp falha se imagens PNG nao estiverem indexadas ou possuirem
transparencia em indices de paleta incorretos.

### Sintoma
```
has transparent pixel but is not an indexed image
transparent pixel at position (X,Y)
```

### Solucao (Automatica)
`fix_transparency.ps1`: usa ImageMagick para forcar conversao para 16 cores
(Palette type) e desativar canais Alpha problematicos. Implementa retry
(3 tentativas) e circuit breaker.

---

## 6. Desalinhamento de Dimensoes de Sprites

### Problema
ResComp exige que dimensoes W/H no `.res` sejam multiplos de 8 e
correspondam as dimensoes reais da imagem.

### Solucao (Automatica)
`autofix_sprite_res.ps1`: le dimensoes reais via ImageMagick e atualiza
o `.res`. Busca generica em subdiretorios (sem mapeamento hardcoded).

---

## 7. Limite VDP (16 Sprites Internos)

### Problema
O VDP do Mega Drive suporta no maximo sprites compostos de 16 sprites
internos (hardware sprites de 1x1 a 4x4 tiles). Sprites grandes excedem
esse limite.

### Solucao (Automatica)
`autofix_sprite_res.ps1`: estima sprites internos e adiciona
`NONE 1 1` (opt_type=SPRITE) quando excede o limite.
`validate_resources.ps1`: detecta e reporta em `out/logs/validation_report.json`.

---

## 8. Erros de Compilacao C (Retry Inteligente)

### Problema
Erros de API deprecada, argumentos incorretos ou declaracoes implicitas
podem ser corrigiveis pelo `fix_migration_issues.ps1` se novas regras
forem adicionadas.

### Sintoma
```
error: This method is deprecated
error: too many arguments to function
error: implicit declaration of function
```

### Solucao (Automatica)
`build_inner.bat`: detecta esses padroes no log, re-executa
`fix_migration_issues.ps1 -Force` e faz retry. Permite que regras
novas adicionadas ao script sejam aplicadas automaticamente.

---

## 9. Erros de Linker (Diagnostico)

### Problema
Erros de linker requerem intervencao manual mas devem ser diagnosticados
claramente.

### Sintoma
```
undefined reference to 'funcao'
multiple definition of 'simbolo'
```

### Solucao (Diagnostico)
`build_inner.bat`: detecta padroes de linker e exibe mensagens de
diagnostico com causas comuns e solucoes sugeridas:
- `undefined reference to zeroDivideCB`: boot file incompativel
- `undefined reference to <funcao>`: funcao removida/renomeada no SGDK 211
- `multiple definition`: duplicacao de includes ou globais

---

## 10. Erros de Java/ResComp

### Problema
ResComp (compilador de recursos em Java) pode falhar por falta de memoria
ou recursos corrompidos.

### Sintoma
```
Exception in thread "main"
OutOfMemoryError
```

### Solucao (Diagnostico)
`build_inner.bat`: detecta e sugere aumentar `JAVA_OPTS` (atual: `-Xmx2g`).

---

## 11. Idempotencia (Marker File)

### Problema
`fix_migration_issues.ps1` roda a cada build. Em projetos grandes
(ex: HAMOOPIG com 7000+ linhas), re-parsear o arquivo inteiro com N
regexes a cada build e desperdicio.

### Solucao
Apos migracao bem-sucedida, o script cria `.sgdk_migration_state.json`
contendo o hash SHA-256 do script. No proximo build:
- Se marker existe e hash bate → pula migracao (fast path)
- Se hash diferente (script atualizado) → re-executa migracao
- `-Force` ignora marker e sempre re-processa

---

## 12. Modo Dry-Run

### Uso
```powershell
& fix_migration_issues.ps1 "C:\path\to\project" -DryRun
```

Mostra todas as mudancas que seriam aplicadas sem escrever nenhum arquivo.
Util para:
- Diagnosticar problemas de migracao antes de aplicar
- Verificar quais regras afetam um projeto especifico
- Auditar mudancas propostas em revisao de codigo

---

## Mecanismos de Validacao e Monitoramento

### Logs
- `out/logs/build_output.log`: Saida bruta do make/ResComp
- `out/logs/build_debug.log`: Log detalhado dos scripts de resiliencia com timestamps
- `out/logs/validation_report.json`: Relatorio JSON estruturado da ultima validacao

### Arquivos de Estado
- `.sgdk_migration_state.json`: Marker de migracao (hash + timestamp + arquivos)

---
## Atualizacao Canonica do Pipeline de Assets

Esta secao substitui qualquer ambiguidade anterior sobre a origem dos assets.

### Regra oficial

Para projetos novos, o caminho oficial e:

- `res/data/` para os arquivos brutos;
- `res/data/backup/` para backups automaticos;
- `res/` para os arquivos finais consumidos pelo SGDK;
- `tools/sgdk_wrapper/modelo` como base de referencia para iniciar novos projetos.

### Proposito

- separar claramente a origem do asset da saida final;
- permitir correcao automatica sem apagar o estado anterior do arquivo;
- padronizar o fluxo para humanos, scripts e agentes de IA;
- falhar com diagnostico quando a extracao for ambigua, em vez de gerar uma ROM visualmente errada.

### Como o wrapper atua hoje

Quando `SGDK_AUTO_PREPARE_ASSETS=1` esta ativo, o wrapper:

1. escaneia `res/` e corrige ativos finais fora do padrao tecnico;
2. move o arquivo anterior para `res/data/backup/` antes de sobrescrever;
3. escaneia `res/data/` recursivamente;
4. ignora `res/data/backup/`;
5. converte e espelha a saida final para `res/`, mantendo subpastas e nomes;
6. gera `out/logs/asset_preparation.log`;
7. gera `out/logs/asset_preparation_report.json`;
8. gera `out/logs/asset_preparation_preview.png`;
9. aborta cedo quando a confianca da extracao nao e suficiente.

Se `res/data/` estiver vazio, o wrapper ainda suporta fallback para o fluxo legado baseado em `data/` e `res/*.res`.

### Transparencia e indexacao

O pipeline atual nao depende mais da heuristica destrutiva de "pixel (0,0) = transparencia" como regra principal.

A ordem de prioridade agora e:

1. alpha real;
2. transparencia de paleta;
3. metadados gerados pela preparacao automatica;
4. inferencia por borda apenas quando a confianca e suficiente.

### Base oficial para novos projetos

`tools/sgdk_wrapper/modelo` e a implementacao de referencia desse fluxo canonico.
13. Sanitizacao Proativa de Imagens (Inspirado em mugen2sgdk)

### Problema
Correcoes reativas (pos-falha) podem ser lentas em builds iterativos. Ativos podem passar na validacao basica mas falhar no ResComp por detalhes sutis de indexacao ou desalinhamento.

### Solucao
`ensure_safe_image.ps1`: age preventivamente sobre as imagens originais em `res/`.
- **Align 8x8**: Adiciona padding (NorthWest) para garantir multiplos de 8.
- **Palette Fix**: Forca 16 cores (4bpp) e tipo Palette (Indexado).
- **Index 0 Mapping**: Forca a cor do pixel (0,0) (ou Magenta) para o indice 0 de transparencia.

### Ativacao
Configurar `SGDK_AUTO_FIX_RESOURCES=1` no ambiente. Isso ativa a flag `-Fix` no `validate_resources.ps1` que por sua vez invoca o sanitizador para cada ativo fora dos padroes.

---
14. Preparacao Automatica de Sprite Sheets e Backgrounds

### Problema
Projetos com assets brutos em `data/` nao devem depender de recortes manuais ou da heuristica destrutiva de "pixel (0,0) = transparencia".

### Solucao
`prepare_assets.py`: etapa pre-build opcional ativada por `SGDK_AUTO_PREPARE_ASSETS=1`.

- Lê `res/*.res` para descobrir quais `SPRITE` e `IMAGE` precisam existir.
- Associa esses recursos aos arquivos de `data/` por similaridade de nome/tipo.
- Extrai automaticamente frames e crops.
- Gera `out/logs/asset_preparation_report.json`.
- Gera `out/logs/asset_preparation_preview.png`.
- Se a confianca da extracao for baixa, falha cedo com diagnostico.
