# Simulação das três rotas de posse de CRAM — comparação de custo (Etapa B1)

Data: 2026-09-25 · Branch `feat/mugenesis-impact-fx-v2` @ `7cf00ed8` · Medição em cópia (`rascunho/temporario/routes_sim/`), **sem tocar produção/res/ROM**.

Ferramentas usadas (self-check aprovado antes de qualquer leitura):
- `mugen2sgdk_forge palette-check --project <P> --id ken` → orçamento de slots da linha do corpo.
- `tools/sgdk_wrapper/.agent/scripts/vdp_scanline_simulator.py --self-check` → `passed`; depois as 3 cenas.

CRAM = 4 linhas × 16 palavras (índice 0 transparente). Cada `PAL_setColors(n)` = `n` escritas em CRAM (DMA). Cada `PAL_getColors(16)` = 16 leituras.

## Resultado central 1 — scanline é INVARIANTE à rota

Posse de paleta (CRAM) não altera geometria de sprite. As três rotas compartilham o mesmo teto de scanline. Medido (bounding-box superior; células transparentes ainda não aparadas por BALANCED):

| Cena | sprites/linha (lim 20) | px/linha (lim 320) | links (lim 80) | blockers |
|------|----|----|----|----|
| idle (2 lutadores + sombras) | 12 | 352 | 42 | pixel_over_320 |
| hadouken (+ projetil g750_fx) | 12 | 352 | 44 | pixel_over_320 |
| super_peak (g8000 + corpo + projetil + sombras) | **28** | **832** | **156** | sprites>20, pixel>320, links>80 |

Conclusão: o gargalo de FX (super estoura os DOIS limites por scanline) existe em i, ii e iii por igual. A escolha de rota **não** resolve scanline; resolve apenas a colisão de CRAM. A decomposição de sheets (Etapa B2, com aprovação humana por família) é obrigatória em qualquer rota.

## Resultado central 2 — orçamento de CRAM por rota

Estado atual (medido): PAL0 = stage[1..8](8) + HUD[9..15](7) = **15/15, zero folga**; PAL1/PAL2 corpo; PAL3 = linha FX única compartilhada (só fxpal de P1, `mg_fight.c:767`).

`palette-check` exato (Ken): `variants=12 body_used=14 (idx6 livre) stable=8 varying=6 lossless_merges={} fx_colours_exact=11 fx_dedicated=9` → **`exact_need=23` vs `line_slots=15` → `over_by=8`, `fits=false`, `status=fail`**.

### Rota (i) — HUD fica PAL0[9..15], stage PAL0[1..8], super restaura
- Linhas novas: **0**. Cabe hoje.
- Colisões: bgfx do super sobrescreve `PAL0[1..14]` (`mg_fight.c:539`) → invade stage E HUD ao mesmo tempo. Mitigação atual esconde HUD/sombra (`fight_hud.c:186-189`). **Custo DMA por super**: `PAL_getColors(0,..16)`=16 read no entrar + `PAL_setColors(1,saved,14)`=14 write no sair + `PAL_setColors(0..14,14)`≈14 write/elemento enquanto ativo (16 paletas/49 frames em `bgfx0_elem`).
- Veredito: **não bloqueia B2/C agora**, mas **impossibilita Etapa D** (stage elaborado + super + HUD simultâneos na mesma linha). É a rota mais barata e a mais limitada.

### Rota (ii) — FX sai de PAL3 para PAL1/PAL2 por jogador
- `palette-check` medido: corpo+FX = **23/15, over_by 8, lossless_merges vazio** → **não cabe** sem remapeamento lossy (perda de fidelidade, falha o gate de aprovação artística). Vale para PAL1 e PAL2.
- Não resolve colisão #3: retrato ainda consome PAL1/PAL2 (`fight_hud.c:125-126`), flash continua clareando retrato.
- Libera PAL3 inteira p/ HUD (7 slots caberiam), mas ao custo de estourar a linha do corpo em 8 slots.
- Veredito: **INVIAVEL no orçamento medido.** Descartada por número, não por opinião.

### Rota (iii) — motor de swap por consumidor (estende REGRA 1c)
- Mantém FX em PAL3 dedicada (linha do corpo fica 14/15 → **cabe**, sem remape).
- Isolamento por máscara de swap pré-declarada (extensão de `s_flash_tab`, `mg_fight.c:52-67`) para: flash(só corpo), retrato, projetil, HUD-sob-super, bgfx. ≈ **4–5 tabelas**.
- **Custo DMA**: swaps em transição de estado (início de round, entrar/sair super, KO), cada ≤16 palavras, pré-declarados — compatível com REGRA 1c e com "DMA só no VBlank".
- Resolve colisões #3, #4, #6 **sem linha CRAM nova**.
- Veredito: **cabe no hardware e resolve as colisões**, ao custo de código (um motor de swap). Único caminho que destrava B2 + C + D simultaneamente.

## Recomendação medida (decisão humana pendente)

- Se o escopo parar em demo sem stage elaborado: rota (i) é suficiente e de custo zero.
- Como o escopo ampliado inclui **Suzaku/stage (D) + retrato sem flash (C) + famílias FX (B2)**: rota (i) não acomoda stage+super+HUD, rota (ii) estoura CRAM em 8. **Rota (iii)** é a única compatível com o escopo aprovado — custo concentrado em código de swap, nenhum hardware extra, nenhum remape lossy.

Nenhuma rota deve "emprestar" linha sem dono/restauração medida (restrição do diretivo). A decisão de rota é humana; esta simulação fornece os números.
