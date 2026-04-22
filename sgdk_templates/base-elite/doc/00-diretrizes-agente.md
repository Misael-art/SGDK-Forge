# 00 - Diretrizes para Agentes de IA

**Status:** Template
**Plataforma:** Mega Drive / Genesis via SGDK 2.11
**Projeto:** __PROJECT_NAME__

> Este documento codifica como agentes de IA devem trabalhar neste projeto.
> Ele impede alucinacao, escopo falso, regressao silenciosa e gambiarra.

---

## 1. FLUXO OBRIGATORIO

Antes de escrever codigo, criar arquivos ou propor mudancas:

1. Ler `doc/10-memory-bank.md` — saber onde o projeto parou.
2. Ler `doc/11-gdd.md` — saber o que o jogo e e o que nao e.
3. Ler `doc/13-spec-cenas.md` — saber os limites tecnicos da cena afetada.
4. Ler `doc/12-roteiro.md` se a tarefa tocar dialogos, encontros ou narrativa.
5. Ler `doc/03-arquitetura.md` se for criar ou mover arquivos.
6. Em projeto novo ou escopo ainda difuso, usar `planning/game-design-planning` para seedar GDD, roteiro, spec, `first_playable_slice` e `front_end_profile`.
7. Se a tarefa tocar menu, title screen ou front-end, alinhar `front_end_profile` no GDD antes de abrir arte ou runtime.
8. Responder com `[Contexto Carregado]` e um plano antes de gerar codigo.

**SE VOCE NAO SEGUIR ESTE FLUXO, O TRABALHO DEVE SER TRATADO COMO NAO CONFIAVEL.**

---

## 2. ACOES PROIBIDAS

| # | Acao proibida | Por que |
|---|---------------|---------|
| 1 | Usar `float`, `double` ou aritmetica de ponto flutuante | 68000 nao tem FPU; use `fix16`/`fix32` |
| 2 | Usar `malloc()`, `free()` ou alocacao dinamica no loop | Fragmenta heap, causa crash imprevisivel |
| 3 | Adicionar biblioteca externa ao SGDK | Viola stack aprovado |
| 4 | Criar cena ou mecanica nao prevista no GDD | Scope creep |
| 5 | Alterar dialogos sem consultar `doc/12-roteiro.md` | Quebra coerencia narrativa |
| 6 | Exceder budget de VRAM, DMA ou sprites de uma cena | Hardware real trava ou corrompe |
| 7 | Duplicar logica de build nos scripts do projeto | Viola arquitetura do wrapper |
| 8 | Criar arquivos fora da arvore documentada | Polui o projeto |
| 9 | Declarar entrega sem build.bat verde e ROM testavel | Falso positivo |
| 10 | Usar APIs SGDK deprecadas (VDP_setPalette, SPR_addSpriteEx 6 args, etc.) | Incompativel com SGDK 2.11 |
| 11 | Modificar `tools/sgdk_wrapper` sem necessidade comprovada | Impacta todos os projetos do workspace |
| 12 | Ignorar `doc/13-spec-cenas.md` ao alterar efeitos visuais | Pode estourar VBlank |
| 13 | Inventar APIs, funcoes ou macros que nao existem no SGDK 2.11 | Gera codigo que nao compila |
| 14 | Usar DMA fora de VBlank sem justificativa documentada | Corrompe VRAM |

---

## 3. RESTRICOES DE HARDWARE (REFERENCIA RAPIDA)

Estas sao restricoes fisicas do Mega Drive. Nao sao sugestoes.

| Recurso | Limite | Nota |
|---------|--------|------|
| VRAM total | 64 KB (2048 tiles de 8x8) | Compartilhada entre BG_A, BG_B, sprites e window |
| Paletas | 4 paletas x 16 cores (15 visiveis + transparente) | Total 61 cores simultaneas |
| Sprites por scanline | 20 (max) | Depois disso, invisivel |
| Sprites totais | 80 link entries | Inclui todos os meta-sprites |
| DMA por VBlank (NTSC) | ~7.2 KB | ~3600 words a 60Hz |
| DMA por VBlank (PAL) | ~14 KB | ~7000 words a 50Hz |
| CPU clock | 7.67 MHz | Toda logica + render tem que caber em 1/60s |
| H-Int | 1 callback por frame | Reconfigurar e caro; centralizar em modulo proprio |
| Window plane | Nao scrollavel | Ideal para HUD e dialogos |
| BG planes | 2 (BG_A + BG_B) | Parallax simulado com line/column scroll |

---

## 4. CHECKLIST PRE-CODIGO

Antes de escrever qualquer linha, valide:

- [ ] Li o Memory Bank e sei onde o projeto parou?
- [ ] A tarefa pertence ao escopo atual do GDD?
- [ ] Se o projeto ainda esta nascendo, o `first_playable_slice` e o roadmap de cenas ja foram seedados?
- [ ] Sei os limites de VRAM/DMA/sprites da cena afetada (ver `doc/13-spec-cenas.md`)?
- [ ] Se a cena for menu/title/front-end, a identidade visual e o comportamento de idle/selecao estao declarados no GDD?
- [ ] Meu codigo usa apenas `u8`, `u16`, `s16`, `u32`, `fix16`, `fix32`?
- [ ] Nao estou alocando memoria dinamica no loop?
- [ ] Os dialogos respeitam o roteiro aprovado?
- [ ] Consigo compilar com `build.bat` e gerar ROM?

---

## 5. GATE DE ENTREGA

Uma tarefa so pode ser considerada concluida quando:

1. `build.bat` compila sem erro e gera ROM em `out/rom.bin`.
2. A ROM roda com evidencia rastreavel em emulador; BlastEm fecha o gate e BizHawk apenas complementa telemetria.
3. A cena afetada nao apresenta jitter, tearing, sprite overflow ou corrupcao de VRAM visivel.
4. Os budgets de `doc/13-spec-cenas.md` nao foram violados.
5. Os 7 eixos de QA foram reportados: build, validation_report, boot_emulador, gameplay_basico, performance, audio e memoria operacional canonica.
6. `doc/10-memory-bank.md` foi atualizado com o que mudou.
7. Nenhum documento canonico ficou em conflito com o estado real.

**Termos proibidos sem satisfazer os gates acima:**
`pronto`, `completo`, `fechado`, `funcional`, `validado`.

---

## 6. REGRAS ANTI-POLUICAO

- Nao criar modulo, arquivo ou pipeline duplicado quando ja existe um canonico.
- Nao manter documento desatualizado referenciado por outro.
- Nao esconder falha atras de `TODO`, stub ou comentario vago.
- Nao commitar assets de terceiros sem licenca documentada.
- Se uma feature nao esta pronta, documentar explicitamente como `parcial` ou `placeholder`.
- Se uma refatoracao remove comportamento, provar que foi intencional.
- Preferir correcao in-place a criar fork de arquivo.

---

## 7. PROTOCOLO DE HANDOFF

Ao encerrar sessao relevante:

1. Atualizar `doc/10-memory-bank.md` com o que aconteceu.
2. Se o GDD ou roteiro mudaram, atualizar os documentos correspondentes.
3. Se um budget mudou, atualizar `doc/13-spec-cenas.md`.
4. Nunca alterar `doc/13-spec-cenas.md` sem ordem expressa do usuario.

---

**[Fim das Diretrizes]**
