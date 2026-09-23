# LESSONS.md — Aprendizados do projeto GROK BUILD

> Desvios das instrucoes padrao do diretorio / do template, e o que medimos.

---

## L-001 — Bootstrap Linux com PATH limpo (2026-08-08)

**Problema:** `tools/sgdk_wrapper/new_project.sh` e `build.sh` quebram neste host
Linux porque `env.sh` prepende `$GDK/bin` (symlinks `cp.exe`/`mkdir.exe`/`rm.exe`)
e sombreia coreutils POSIX.

**Decisao:** bootstrap manual copiando `tools/sgdk_wrapper/modelo` com
`PATH=/usr/bin:/bin`, depois port seletivo do codigo validado do irmao CLOUDE.
Build exclusivo via `build_sgdk_wine_bridge.sh`.

**Nao corrigimos** `tools/sgdk_wrapper/` (canonico; exige aprovacao humana).

## L-002 — Heranca do memory-bank do template

O template materializa `doc/10-memory-bank.md` com historico de **outro**
trabalho. Na primeira sessao o arquivo e reescrito do zero (ver memory bank).

## L-003 — XGM2, nao XGM v1 (medicao vs brief)

Brief pedia PCM ~14–22 kHz. Hardware/driver XGM2 fixa **13.3 / 6.65 kHz**.
Ducking exige XGM2. Documentado em `doc/SOUNDMAP.md`. Regra: medicao manda.

## L-004 — Shadow/Highlight global

S/H e toggle global do VDP. Decisao: ligado sempre; tiles de fundo priority=1;
slots de operador na paleta 3. Teto efetivo de cores de gameplay: **58** (nao 61).

## L-005 — 4+ camadas com 2 planos

Camadas de ceu/montanha/colina = **mesmo BG_B** com bandas de line-scroll.
Nunca inventar terceiro plano BG. Ver `doc/ARCHITECTURE.md` §3.

## L-006 — Sprite 4x4 = 1 slot de hardware

Kirby 32×32 custa **1** sprite VDP, nao 4. O limite que morde no stress e
**sprites por scanline (20)**, nao o total de 80.

## L-007 — Arte AI exige quantizacao antes do gate

Toda imagem gerada por IA passa por reducao de cores → snap RGB333 → 4 bpp
antes de entrar em `res/` e nos gates de cor. Nunca contar PNG bruto no score.

## L-008 — Prior art CLOUDE e linha de base, nao entrega

Codigo de jogo, harness e contratos medidos do CLOUDE sao a espinha. Score AAA
e arte final deste projeto comecam do zero na arvore GROK BUILD.

## L-009 — Key color do sprite AI vazou na ROM (2026-08-08)

**Sintoma:** apos integrar `kirby_sheet_32x8_q.png` como `ph_kirby.png`, o BlastEm
mostrou um retangulo rosa solido atras do Kirby. Gates de hardware PASS; falha e
visual.

**Causa provavel:** quantizacao preservou magenta como cor opaca em pixels de
borda/bbox, ou a ordem de indices do PNG indexado nao ficou com transparencia
limpa no que o rescomp embala. O placeholder original ja estava no contrato
rescomp e nao vaza.

**Decisao:** ROM volta ao placeholder validado. Candidato R1 permanece em
`res/sprites/kirby_r1_candidate.png` e `data/source_art/ai_quantized/r1/` ate
passar por pipeline que (1) force mascara de transparencia pixel-perfect por
frame, (2) reindexe com 0 = transparente e 1..N = cores MD, (3) reconstrua com
gates + julgamento visual de captura.

**Licao:** integracao de arte AI exige captura visual, nao so gates de budget.

## L-010 — Stamp de 16 cores na imagem dona da paleta (2026-08-08)

**Problema:** sky/mount/hills compartilham PAL0, mas a cena carrega CRAM de
`img_ph_sky.palette`. Se o PNG do ceu so usa indices 0,3,7,8, o rescomp pode
exportar uma paleta incompleta e indices 9–15 (montanha/colina) viram cores
erradas (palmeiras amarelas).

**Fix:** carimbar 1 px de cada indice 0–15 no canto inferior direito de cada
PNG de paleta compartilhada antes do build. Placeholder original ja tinha a
tabela completa embutida.

**Licao:** dono de CRAM precisa conter **todos** os indices que qualquer
camada daquela linha de paleta referencia.

## L-011 — Palette masters absolutas (2026-08-08)

Carregar CRAM de `img_ph_sky.palette` falha quando o rescomp reordena ou
encurta a paleta do tileset. Solucao: `img_pal0_master` / `img_pal1_master` /
`spr_pal2_master` (16 cores canonicas, 1 coluna por indice) e
`PAL_setPalette(PALn, img_palN_master.palette->data, DMA)` em stage/boss.

Ainda assim, se o tileset de uma camada tiver indices remapeados localmente
pelo rescomp, as cores continuam erradas — o master so garante o CRAM, nao o
mapeamento pixel→indice do tileset. Camadas que compartilham PALn devem
nascer com a **mesma** ordem de indices absolutos 0..15.

**Pratica de ship (sessao 002):** hills/mount AI R2 renderizaram palmeiras em
creme (indice 6) apesar do PNG usar 11–13 verdes. Candidatos ficam em
`data/source_art/ai_quantized/r2/`; ROM hibrida = Kirby+sky AI + terrain
procedural ate o pipeline de tileset compartilhar indices byte-identicos com
o placeholder builder.

## L-012 — Sheet AI rosa no PNG, creme na ROM (2026-08-08)

**Sintoma:** `kirby_sheet_r2b.png` e rosa solido no preview; na ROM o Kirby
aparece oco/creme (gradiente H-int) com 0 pixels pink na captura. Restaurar
`ph_kirby_placeholder_backup.png` recupera pink imediatamente.

**Hipoteses abertas:**
1. rescomp SPRITE reordena paleta de forma incompativel com indices do tile
2. interacao com `img_pal0_master` / ordem de `PAL_setPalette`
3. frames com idx0 alto demais em idle (corpo classificado como key)

**Mitigacao ship:** placeholder na ROM; candidato AI versionado fora do path
critico. Proxima sessao: diff byte-a-byte do `SpriteDefinition` gerado vs
placeholder e teste isolado sem palette masters.

## L-013 — Index 0 no centro do corpo (forense 2026-08-08)

**Causa raiz confirmada** (doc/diagnostics/2026-08-08-kirby-index0-transparency.md):

1. VDP: indice 0 de sprite = transparencia de hardware (tese do operador: correta).
2. Nosso `is_key` largo classificava rosa base (255,146,182) como key → **72% do corpo**.
3. Esses pixels viravam **indice 0** no PNG indexado.
4. Forense: placeholder centro idx0=0%; AI R2 centro idx0=**80%** → so contorno/olhos.
5. "Kirby amarelo" = gradiente H-int creme **por tras do furo**, nao OAM na paleta errada
   (PAL2 estava correto no runtime).

**Fix R3:** key estrita (R alto, B alto, **G baixo ≤73**); corpo sempre indices 1–5;
gate automatico `center_idx0 < 5%` e `opaque > 35%` por frame. Instalacao recusada
se falhar.

**Prova:** stage_r3 gates PASS + **22728** pixels pink na captura (vs 0 no bug).
