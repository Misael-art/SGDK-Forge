# 10 - Memory Bank & Context Tracker — METAL_SLUG_URBAN_SUNSET

**Ultima atualizacao:** 2026-04-07
**Fase atual:** runtime refeito com crop VDP-viavel; visual revalidado no BlastEm, gate canonico ainda parcial por falha de `save.sram`
**Proxima fase:** fechar a captura canonica do BlastEm e entao medir runtime/budget real antes de decidir a integracao do foreground C

> **DIRETRIZ:** Este e o bloco de memoria primario do projeto.
> Leia integralmente antes de qualquer codigo ou decisao.
> Atualize ao encerrar sessoes relevantes.

---

## 1. ESTADO ATUAL DO PROJETO

### O que existe e funciona

- O caso de curadoria `metal_slug_urban_sunset_scene` ja tem mapa semantico A/B/C, variantes basic e elite e relatorio de analise em `tools/image-tools/specs/translation_cases/metal_slug_urban_sunset_scene.json` e `assets/reference/translation_curation/metal_slug_urban_sunset_scene/reports/`.
- O projeto SGDK agora materializa um runtime de prova com dois planos reais, line scroll por zonas em BG_B, scroll base em BG_A e bloco de evidencia em SRAM via `src/main.c`.
- Os assets de runtime ja existem em `res/gfx/` e `resources.res` foi alinhado para nomear BG_B e BG_A de acordo com os arquivos reais.
- Os assets de runtime foram refeitos a partir do aprendizado semantico consolidado, com recorte oficial `336x224` em vez do panorama `584x224` que estourava o budget visual/VDP.
- O slice atual foi visto no BlastEm por screenshot dedicado em `out/captures/benchmark_visual.png`; a exposicao vazia na lateral direita desapareceu e a cena voltou a ler corretamente.
- O gate canonico `testado_em_emulador` ainda nao pode ser fechado nesta passada porque o wrapper do BlastEm segue falhando ao materializar `save.sram`/`visual_vdp_dump.bin` desta build especifica.

### O que e placeholder

- O foreground C continua isolado na curadoria, mas ainda nao foi aprovado como plano independente no runtime final.
- O gate final de entrega ainda nao esta fechado com performance, audio e budget validados em artefatos rastreaveis dentro da arvore revisada nesta sessao.
- O wrapper de captura visual ainda apresenta intermitencia no `save.sram`; nesta passada a janela do BlastEm chegou a renderizar corretamente e a screenshot foi atualizada, mas o `save.sram` nao foi persistido.
- A captura complementar de runtime via BizHawk ainda nao esta pronta porque o projeto nao expoe `g_mdRuntimeProbe` no binario atual.
- O foreground C continua isolado como asset proprio (`layer_c_front_elite.png`), mas o runtime jogavel atual segue bakeando a massa frontal principal dentro do BG_A para preservar budget.

### O que falta para o slice ser completo

- Fechar a persistencia canonica da evidencia do BlastEm (`save.sram` + `visual_vdp_dump.bin`) para a ROM atual.
- Medir em ROM a viabilidade do foreground como faixa de sprites limitada; se falhar, fundir de forma controlada a massa frontal na faixa inferior do BG_A.
- Integrar `g_mdRuntimeProbe` para produzir `runtime_metrics.json` e transformar `performance` / `validado_budget` em estados medidos, nao inferidos.
- Validar budget real de VRAM, DMA e SAT depois da retomada dinamica.
- Fechar os 7 eixos de QA antes de declarar entrega.

### Metricas de codigo

- Runtime atual: 1 modulo principal de cena em `src/main.c`, 3 imagens declaradas em `res/resources.res`, 0 sprites ativos no loop atual.
- Topologia atual do runtime: 2 planos scrollaveis reais + WINDOW apenas para overlay textual.
- Efeito atual buildado: line scroll em 224 linhas para BG_B e BG_A, com duas velocidades no fundo e movimento automatico de camera em ping-pong.
- Crop runtime atual: `336x224`, viewport `320x224`, camera travel `16px`.
- Estimativa atual dos PNGs de runtime apos a refacao: `bg_b = 563` tiles unicos, `bg_a = 942`, `bg_c = 214`, total ativo do slice jogavel `1505` para `BG_B + BG_A`.
- Paletas de runtime hoje: 2 ativas para a cena estaticamente carregada; estrategia alvo reserva 1 paleta adicional para foreground e 1 para efeitos.

---

## 2. O QUE ACABOU DE ACONTECER

**2026-04-07 — Runtime foi refeito com crop VDP-viavel e voltou a ler corretamente no BlastEm**

- Os assets `city_bg_a_elite.png`, `city_bg_b_elite.png` e `layer_c_front_elite.png` foram regenerados a partir das camadas manuais autoritativas do caso de curadoria.
- O panorama `584x224` foi mantido apenas como referencia humana em `reports/`; a exportacao de runtime passou a usar um crop budgetado `336x224` em `x=96`.
- O `BG_A` anterior entrava na ROM com detalhe demais e estourava a viabilidade do slice; a nova exportacao reduziu o custo ativo para `1505` tiles unicos estimados em `BG_B + BG_A`.
- A nova ROM foi vista no BlastEm e o screenshot dedicado mostra a cena correta, sem o bloco vazio/maroon que apareceu na tentativa de panorama largo.
- O wrapper de captura ainda nao conseguiu fechar `save.sram`, entao o projeto nao deve ser descrito como `testado_em_emulador` nesta iteracao apesar da validacao visual por screenshot.

**2026-04-05 — Continuidade da curadoria foi canonizada e aplicada no runtime**

- O rascunho manual da sessao anterior foi consolidado nos documentos canonicos do projeto, removendo o estado de template do GDD e da especificacao tecnica da cena.
- O spec do caso de curadoria recebeu uma estrategia formal de retomada para runtime dinamico, cobrindo quebra de profundidade, mapeamento BG_A/B, politica de foreground, paletas, tile-first e checklist pre-gate.
- O runtime passou a usar `HSCROLL_LINE`, com BG_B dividido em zona de ceu e zona de skyline e BG_A movendo a arquitetura como plano principal.
- O rebuild do projeto fechou com sucesso no wrapper, mas a evidencia antiga foi invalidada por mudanca de identidade da ROM.

---

## 3. DECISOES PENDENTES

- Aprovar ou rejeitar foreground por sprites limitados apos medir SAT e VRAM em emulador.
- Decidir entre widen/stream do conteudo horizontal ou recuo controlado do camera travel para eliminar a exposicao lateral direita.
- Definir o corte exato entre ceu e skyline para line scroll em BG_B sem provocar serrilhado ou ruido.
- Integrar a sonda `g_mdRuntimeProbe` antes de exigir medicao automatica de frame stability, sprite pressure e FX load.
- Medir se a particao padrao de VRAM do sprite engine precisa ser reduzida com `SPR_initEx(u16 vramSize)` para devolver espaco ao background.

---

## 4. REFERENCIAS RAPIDAS

- GDD: `doc/11-gdd.md`
- Spec cenas: `doc/13-spec-cenas.md`
- Diretrizes agente: `doc/00-diretrizes-agente.md`
