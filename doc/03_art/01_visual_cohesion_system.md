# Visual Cohesion System — Mega Drive AAA

Toda cena deve ser escrupulosamente coerente. Elementos não podem existir no vácuo tecnológico.

## Regra 1 — Luz unificada
- Existe uma direção de luz clara definida na arte.
- Todos os elementos (Foreground, Background, Sprites) respeitam essa luz.
- Sprites e cenário compartilham a mesma lógica de sombreamento e highlight.

## Regra 2 — Paleta integrada
- Todos os elementos pertencem à mesma família de cores globais.
- FX respeitam obrigatoriamente a paleta base (exemplo: tela de hit flasheia usando cores harmônicas da paleta existente ou inverte com coerência).
- EVITAR cores isoladas (gambiarras de slot livre que parecem "coladas" em cima).

## Regra 3 — Materiais consistentes
- Água parece água (reflexível, maleável).
- Metal parece metal (highlights estourados, contraste agudo).
- Pedra parece pedra (textura opaca, dithering rústico).

Cada material deve estampar via pixel art:
- Cor base
- Sombra direcional
- Highlight

## Regra 4 — FX afetam o mundo
- **Chuva** → afeta chão (reflexo / brilho / splash particles).
- **Vento** → afeta partículas, folhagem, inércia.
- **Fogo** → afeta a iluminação local (glow palette swapp / fumaça).
- **Impacto** → afeta câmera, somatório das partículas e deforma ambiente.

## Regra 5 — Camadas conversam entre si
- Foreground NÃO é decorativo (deve abraçar o gameplay).
- Background reage ao gameplay sempre que possível.
- FX conectam os planos (ex: chuva começa pequena no plano B e larga no plano A).

## Proibição absoluta
- FX isolados existindo por pura estética sem interação ambiental.
- Cores desconectadas por falta de planejamento de palette lines.
- Elementos que não interagem (como um personagem andando e não projetando sombra ou peso no chão).

## Teste final
"Todos os elementos parecem fazer parte do MESMO mundo?"
Se algo parece um adesivo colado: **REFAZER.**
