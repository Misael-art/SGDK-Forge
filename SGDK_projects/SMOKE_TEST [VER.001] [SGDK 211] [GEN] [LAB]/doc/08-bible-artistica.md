# 08 - Bible Artistica - SMOKE_TEST [VER.001] [SGDK 211] [GEN] [LAB]

## Direcao congelada: Branding v3

A abertura deve demonstrar o potencial expressivo do Mega Drive por montagem, timing, paleta, scroll, sprites e audio. Cada slot tem uma linguagem propria, mas os tres pertencem ao mesmo universo industrial de assinatura.

- Engine: metal quente toma forma dentro da forja.
- Author: o selo pessoal `MO` assina a obra em fosforo e ouro.
- Project: uma prensa industrial aplica o carimbo final de aprovacao.

Referencia visual canonica:

- `out/logs/branding_v3_preview.png`
- `out/evidence/blastem_branding_v3_final/author_hold.png`
- `out/evidence/blastem_branding_v3_final/project_hold.png`
- `out/logs/branding_v3_lineage.json`

## Linguagem por slot

### Mega Forge Engine

- preto, ferro, vermelho quente, branco de impacto e cyan-steel no cooldown
- logo de metal laminado, massa pesada e highlight agressivo
- fundo de forja subordinado ao logo; heat-wave comunica temperatura real

### Misael Oliveira

- grid fosforo cyan escuro com ouro como pico de leitura
- monograma `MO` precisa ser reconhecido antes do nome completo
- halo sempre vazado e atras do selo; nunca cobrir a silhueta informativa
- moldura fina e assinatura limpa, sem parecer painel de debug

### Mega Master Games

- vermelho, preto, ferro claro e dourado de selo
- colunas de prensa e pistoes distinguem este slot da forja
- placa central e escudo carregam a leitura; `SMOKE TEST LAB` e assinatura secundaria

## Regras visuais

- leitura obrigatoria em 320x224 nativo
- 15 cores visiveis + index 0 transparente por paleta quando aplicavel
- tres estados por material principal: sombra, base e highlight
- metal usa contraste duro e highlights curtos; fosforo usa brilho contido
- BG_B respira, BG_A estrutura e sprite/logotipo decide
- efeitos precisam reforcar causa: calor deforma, impacto desloca e selo cai
- benchmarks sao referencia tecnica de presenca, ritmo e densidade, nunca fonte para copia

## Heuristica canonizada

`Halo De Assinatura Apagando O Monograma`, em `doc/03_art/02_visual_feedback_bank.md`, foi aplicada ao slot Author: miolo vazado, densidade periferica e ordem SAT com o monograma vencendo o glow.

## Estado visual

- conceito humano: aprovado
- assets v3: integrados e vistos em ROM
- direcao visual: `passed`; assets individuais continuam `needs_review` para promocao AAA
- claim maximo atual: `technical_lab_validated`
