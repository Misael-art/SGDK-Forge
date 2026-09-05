# Sector 01 Closeout Recovery Design

## Goal

Fechar tecnicamente `sector_01_farol_quebrado` com uma ROM SGDK 2.11
rastreavel, duas rotas BlastEm (sucesso e falha), budget runtime medido e
closeout canonico suficiente para autorizar o inicio de:

- arte definitiva;
- audio;
- `upgrade_beacon_intermission`;
- Sector 02.

Esta autorizacao nao promove placeholders atuais para arte final e nao declara
o jogo `ready_for_aaa`.

## Truth Boundary

O fechamento depende de evidencias da mesma ROM:

- build central;
- regressao estatica e comportamental;
- screenshot da rota;
- `save.sram`;
- bloco `MDRT`;
- hash SHA-256;
- reports de recursos, tilemap, paleta, VRAM, sprites e budget;
- code review, mastering, freshness e scene closeout.

Build sem BlastEm continua sendo apenas `buildado`.

## Recovery Tracks

### 1. Runtime and Contracts

Corrigir somente contratos comprovadamente quebrados:

- tilemap da estrada deve armazenar atributos completos de paleta, prioridade,
  flips e indice;
- HUD deve possuir a faixa superior de `WINDOW`;
- metricas devem usar acumulador `u32`;
- sucesso e falha devem ser persistidos e exibidos de modo distinto;
- conclusao por sucesso depende do Beacon;
- transicoes devem limpar sprites, WINDOW, scroll e input de forma
  deterministica.

Cada mudanca exige teste vermelho antes do codigo.

### 2. QA Bootstrap and Runtime Metrics

Integrar dois mecanismos QA que nao alteram o fluxo normal:

- `SBIS` em SRAM para boot deterministico de cena durante captura;
- `MDRT` em SRAM para medir carga de CPU, frames acima do budget, uso total de
  sprites VDP e estado da cena.

O boot normal continua em Branding. O bootstrap so e consumido quando o payload
tem magic, schema, tamanho e checksum validos.

O valor de sprites por scanline nao sera inventado a partir de
`SPR_getUsedVDPSprite`; sera produzido por simulacao de pior quadro ou evidencia
equivalente.

### 3. Emulator Evidence

A evidencia sera dividida em:

- rota natural de sucesso:
  Title -> abertura -> inicio da corrida -> meio -> Pulse/Pressure/Pursuer/jump
  -> Beacon -> resultado de sucesso -> retorno ao Title;
- rota de falha:
  corrida -> dano/Pressure fatal -> resultado de falha -> retorno ao Title;
- captura deterministica de runtime via `SBIS` para a janela `MDRT`.

Input host so conta quando o probe `INP` da ROM comprovar que foi observado.
Se o transporte de input continuar bloqueado, a correcao deve ocorrer no
modulo canonico `blastem_automation.psm1`, acompanhada de teste proprio; nao
havera automacao paralela escondida.

### 4. Resource and Hardware Reports

Gerar reports reais para a implementacao atual:

- `scene_tilemap_conversion_report.json`;
- `per_tile_palette_conflict_report.json`;
- `vram_residency_report.json`;
- `sprite_scanline_pressure_report.json`;
- `palette_slot_audit.json`;
- `runtime_metrics.json`;
- `scene_budget_report.json`.

O parecer VDP deve separar:

- custo em ROM;
- set residente de VRAM;
- DMA de preload;
- DMA por frame;
- janela ativa de animacao;
- escopo local da cena;
- pressao de sprites por scanline.

## Release Decision

Os quatro proximos estagios podem ser autorizados quando:

- suites de regressao passam;
- build central passa;
- sucesso e falha foram observados no BlastEm;
- Pulse, Pressure Gate, perseguidor, salto, Beacon, HUD/WINDOW e retorno ao
  Title possuem evidencia;
- `MDRT` mostra zero frames acima do budget no intervalo aceito;
- budget VDP responde `cabe` ou `cabe com recuo` com recuo aplicado;
- reports de tilemap/paleta nao possuem blocker;
- code review nao possui achado critical/high aberto;
- mastering, freshness e scene closeout passam;
- memoria e changelog apontam para a mesma ROM selada.

`visual_gate_blocked` por placeholder deixa de impedir o inicio da producao de
arte, mas continua impedindo aprovacao visual final ate os assets definitivos
entrarem e serem recapturados.

## Explicit Non-Goals

- nao produzir arte definitiva nesta recuperacao;
- nao integrar musica ou SFX;
- nao implementar Upgrade Intermission;
- nao implementar Sector 02;
- nao corrigir por conveniencia sistemas fora dos blockers reproduzidos;
- nao declarar `ready_for_aaa`.

## Failure Handling

- Falha de teste: voltar ao blocker especifico, sem acumular patches.
- Falha de build: verificar API nos headers SGDK 2.11.
- Falha de input: provar foreground, transporte e `observed_input` em cada
  fronteira.
- Falha de budget: aplicar o recuo documentado e reconstruir antes de capturar.
- Rebuild apos captura: invalida o selo e exige nova captura.
