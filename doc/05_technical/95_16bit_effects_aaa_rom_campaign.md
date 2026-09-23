# 95 - 16-bit Effects AAA ROM Campaign

Status: `execution_prompt_ready`

Documento canonico de campanha para transformar o catalogo de efeitos 16-bit em ROMs SGDK jogaveis, auditaveis e provadas em emulador.

---

## Papel deste documento

Este arquivo nao substitui o registry nem cria uma taxonomia paralela. Ele define:

- um roadmap operacional para elevar tecnicas abaixo do nivel senior a dominio minimo equivalente a nota 8;
- uma campanha de 17 ROMs, uma por eixo tecnico;
- um prompt unico para o agente executor produzir as ROMs em `SGDK_projects/`;
- uma politica de aprendizado local passivo, inspirada no Closed Learning Loop, sem promocao automatica ao agente canonico.

## Fontes de verdade

O agente executor deve tratar estes arquivos como ordem de autoridade:

1. `doc/05_technical/93_16bit_hardware_mastery_registry.json`
2. `doc/05_technical/93_16bit_hardware_mastery_matrix.md`
3. `doc/05_technical/94_16bit_hardware_mastery_roadmap.md`
4. `tools/sgdk_wrapper/.agent/pipelines/aaa_scene_v1.json`
5. `tools/sgdk_wrapper/.agent/workflows/aaa-scene-pipeline.md`
6. `tools/sgdk_wrapper/.agent/workflows/production-loop.md`
7. `tools/sgdk_wrapper/.agent/rules/SGDK_GLOBAL.md`
8. Headers SGDK em `sdk/sgdk-2.11/inc/`

Qualquer lista de 180 efeitos recebida no briefing do operador e tratada como payload de cobertura de producao, nao como fonte canonica de status. O registry continua decidindo maturidade, risco, owner skills e gates.

## Definicao de nota 8+

Nesta campanha, uma tecnica so atinge dominio minimo equivalente a nota 8 quando cumpre todos os itens abaixo:

- existe implementacao jogavel e integrada a gameplay, nao apenas FX isolado;
- compila via pipeline SGDK oficial do workspace;
- possui `validation_report.json` limpo;
- possui budget de VRAM, DMA, sprites, CRAM, VBlank e CPU registrado em `doc/13-spec-cenas.md`;
- rodou no BlastEm com evidencia fresca;
- tem screenshot dedicada e, quando aplicavel, `visual_vdp_dump.bin`;
- tem comportamento honesto para hardware Mega Drive real;
- tem fallback documentado quando o efeito e perigoso, falso nativo ou experimental;
- atualiza `doc/10-memory-bank.md` com estado operacional real.

Estados do registry considerados maduros por default:

- `senior_default`
- `blastem_proven`
- `canonical`
- outro status futuro explicitamente provado com evidencia BlastEm, budget e aprovacao humana

Todo status diferente disso entra na fila de elevacao da campanha, incluindo `documented`, `incorporated`, `candidate_with_evidence`, `candidate_for_canon`, `partial`, `gap_pure`, `not_canonized`, `absent`, `interpreted_pattern`, `hazardous_experimental` e equivalentes.

## Principio de granularidade

A campanha produz 17 ROMs, nao 180 ROMs.

Cada ROM cobre um eixo tecnico completo e deve demonstrar todos os efeitos daquele eixo por meio de cenas jogaveis, microfases e setpieces curtos. Quando um eixo tiver muitos efeitos, a ROM deve organizar a experiencia em salas, atos ou modos selecionaveis, sempre preservando build, budget e evidencia por cena.

## Catalogo de eixos

Os nomes canonicos dos eixos aparecem somente nesta tabela. O agente executor deve referenciar estes eixos por numero ou por leitura desta tabela, sem duplicar taxonomia em outro documento canonico.

| # | Eixo canonico | Slug de projeto | Observacao de producao |
|---|---|---|---|
| 01 | Profundidade & Movimento | `profundidade-movimento` | camera, scroll, parallax, streaming e momentum |
| 02 | Pseudo-3D | `pseudo-3d` | estrada, chao falso, Z-map, affine software e recusas honestas |
| 03 | Distorção raster (H-Int) | `distorcao-raster-hint` | H-Int, HScroll line, VSRAM por linha, CRAM split e glitches controlados |
| 04 | Paleta & Cor | `paleta-cor` | fades, cycling, flash, hue, greyscale, sepia e estados cromaticos |
| 05 | Iluminação dinâmica | `iluminacao-dinamica` | shadow/highlight, lanternas, flashes, godrays fake e glow por arte |
| 06 | Transparência & Composição | `transparencia-composicao` | index 0, priority, dithering, mesh, pseudo-alfa e premix honesto |
| 07 | Zoom & Escala | `zoom-escala` | frame swap, prerender, raster zoom e recusas de scaling hardware |
| 08 | Rotação | `rotacao` | rotacao prerenderizada, sheets angulares e fallback software limitado |
| 09 | Foreground / Background | `foreground-background` | priority, foreground destrutivo, sticky decor, tile masks e mutacao |
| 10 | Background animado | `background-animado` | tile animation, ecology, cloud scroll, waterfall e BG reativo |
| 11 | HUD / UI | `hud-ui` | WINDOW, sprite HUD, minimapa, reticulo, status, barras e feedback |
| 12 | Texto narrativo | `texto-narrativo` | TidyText, glyph cache, typewriter, texto cinematico e legibilidade |
| 13 | Cinemático / Cutscene | `cinematico-cutscene` | FSM, pans, wipes, letterbox, retratos, bitmap e transicoes |
| 14 | Combate / Impacto | `combate-impacto` | hitstop, flashes, sparks, knockback, camera shake e slow motion |
| 15 | Partículas & Atmosfera | `particulas-atmosfera` | chuva, neve, fumaca, bolhas, folhas, marcas persistentes e estilhacos |
| 16 | Áudio-visual sync | `audio-visual-sync` | XGM2, stingers, ducking, beat FX, voice/lip sync e pulse por musica |
| 17 | Outros / Matemática / Infra | `outros-matematica-infra` | LUTs, slope, DMA queue, SRAM, raycast, interlace e infra perigosa |

Nome de cada projeto:

```text
AAA EFFECT LAB - <EIXO_CANONICO_OU_SLUG_SEGURO> [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]
```

Se o sistema de arquivos, scripts ou shell criarem atrito com acentos, barras, `&` ou parenteses, o diretorio fisico deve usar o slug seguro da tabela, mas `doc/11-gdd.md` deve preservar o eixo canonico exibido.

## Estrutura obrigatoria de cada ROM

Cada projeto em `SGDK_projects/` deve conter, no minimo:

```text
doc/11-gdd.md
doc/13-spec-cenas.md
doc/10-memory-bank.md
doc/effect_axis_plan.md
doc/agent_learning/
res/
src/
out/rom.bin
out/logs/validation_report.json
out/evidence/blastem/screenshot.png
out/evidence/blastem/visual_vdp_dump.bin
out/agent_learning/closed_learning_loop_report.json
```

`out/evidence/blastem/visual_vdp_dump.bin` e obrigatorio quando a cena mexe com VRAM, VSRAM, CRAM, H-Int, WINDOW, priority, sprites, raster, evidencia visual canonica ou qualquer efeito em que o dump ajude a provar que nao houve falso verde.

## Roadmap da campanha

### Fase 0 - Auditoria de fonte e cobertura

Objetivo: impedir que o agente comece implementando por memoria ou por entusiasmo.

Entregas:

- ler o registry `93_16bit_hardware_mastery_registry.json`;
- ler o roadmap `94_16bit_hardware_mastery_roadmap.md`;
- gerar mapa local de cobertura por eixo em `doc/effect_axis_plan.md`;
- marcar cada efeito como `registry_backed`, `proposal_only`, `already_senior`, `needs_elevation`, `signature_only`, `hazardous_experimental` ou `forbidden_hack`;
- registrar owner skills e lib_cases consultados;
- bloquear qualquer efeito sem classificacao honesta.

Gate:

- nenhum runtime comeca antes de existir plano local por eixo;
- nenhuma tecnica `proposal_only` pode alterar o registry;
- nenhum status local vira canonical sem revisao humana.

### Fase 1 - Direcao de fase e design invisivel

Objetivo: transformar cada efeito em uma microcena jogavel com funcao mecanica.

Para cada efeito, documentar em `doc/effect_axis_plan.md`:

- nome e tema da fase;
- atmosfera visual e sonora;
- kit de movimentacao presumido;
- cronograma de telas ou secoes;
- tutorial invisivel;
- rota de momentum;
- climax, chefe ou setpiece;
- tabela de feedback visual: o que o jogador ve versus o que deduz instantaneamente;
- efeito colateral fisico real;
- fallback honesto;
- budget esperado.

Gate:

- tutorial textual nao pode ser solucao primaria;
- FX puramente decorativo nao passa;
- todo efeito deve modificar leitura, risco, navegacao, combate, ritmo, estado ou decisao do jogador.

### Fase 2 - Implementacao SGDK por eixo

Objetivo: produzir ROMs jogaveis, pequenas o bastante para validar, ricas o bastante para provar dominio.

Entregas por projeto:

- base criada a partir do template canonico ou wrapper oficial;
- `.agent` local materializado sem sobrescrever materializacao existente;
- `src/` organizado por cenas, efeitos, sistemas e dados;
- `res/` validado antes do build;
- headers SGDK 2.11 consultados antes de usar API;
- sem `float`, `double`, `malloc` ou `free` no loop;
- sem DMA fora do VBlank seguro;
- sem build logic dentro do projeto;
- sem API inventada;
- build por wrapper em `tools/sgdk_wrapper/`.

Gate:

- `out/rom.bin` existe;
- `validation_report.json` limpo;
- budget por cena atualizado;
- memory bank atualizado.

### Fase 3 - Prova em BlastEm

Objetivo: cumprir a regra de ferro do workspace.

Entregas:

- boot no BlastEm;
- screenshot fresca de janela dedicada;
- save SRAM quando a cena gerar bloco visual canonico;
- `visual_vdp_dump.bin` quando aplicavel;
- relatorio de performance e estabilidade;
- registro de audio quando o eixo envolver audio ou sincronismo;
- closeout honesto por ROM.

Gate:

- sem BlastEm, nao existe;
- sem evidencia visual fresca, nao entrega;
- BizHawk, Exodus ou GensKMod podem complementar, mas nunca substituem BlastEm.

### Fase 4 - Aprendizado local passivo

Objetivo: registrar experiencia reutilizavel por outro agente sem contaminar o agente canonico.

Entregas por projeto:

```text
doc/agent_learning/README.md
doc/agent_learning/success_patterns.md
doc/agent_learning/failure_patterns.md
doc/agent_learning/skill_promotion_candidates.md
doc/agent_learning/canonical_promotion_review.md
out/agent_learning/effect_implementation_notes.json
out/agent_learning/closed_learning_loop_report.json
```

Conteudo minimo:

- o que funcionou;
- o que falhou;
- quais headers, skills e lib_cases foram decisivos;
- qual workaround foi necessario;
- quais tecnicas merecem promocao futura;
- quais tecnicas devem permanecer perigosas, assinatura visual ou proibidas;
- quais evidencias provam cada conclusao.

Gate:

- estes arquivos sao leitura passiva;
- eles nao atualizam `.agent` central;
- eles nao alteram registry;
- eles nao promovem skill;
- eles nao canonizam comportamento;
- promocao canonica so acontece por ato humano deliberado.

### Fase 5 - Revisao humana de promocao

Objetivo: separar proficiencia local de canonizacao estrutural.

Entregas:

- `doc/agent_learning/canonical_promotion_review.md` com candidatos;
- lista de duplicidades a evitar;
- recomendacao de merge, rejeicao ou experimento adicional;
- links para evidence bundle;
- justificativa de risco;
- estado proposto no registry, se houver.

Gate:

- nenhum aprendizado local entra em `tools/sgdk_wrapper/.agent/skills/`;
- nenhum caso entra em `tools/sgdk_wrapper/.agent/lib_case/`;
- nenhum status muda para `senior_default`, `blastem_proven` ou `canonical`;
- ate um humano ordenar explicitamente estudo, assimilacao e promocao.

## Politica para efeitos falsos nativos ou perigosos

O agente executor deve preservar a verdade do Mega Drive.

Proibido declarar como nativo:

- Mode 7;
- alpha blending RGB real;
- sprite scaling por hardware;
- sprite rotation por hardware;
- terceiro plano BG;
- transparencia livre por canal;
- 3D acelerado por hardware;
- DMA arbitrario fora de VBlank seguro.

Quando o efeito pedido depender de recurso inexistente ou perigoso, a ROM deve:

- usar nome honesto;
- implementar fallback real compativel com Mega Drive;
- marcar status como `signature_only`, `hazardous_experimental` ou `forbidden_hack`;
- explicar custo e risco no budget;
- provar que o fallback roda;
- nunca maquiar a limitacao como capacidade nativa.

## PROMPT UNICO PARA AGENTE EXECUTOR

Copie o bloco abaixo como prompt de execucao para o agente responsavel pela campanha.

```text
Voce esta na raiz do workspace ativo e deve agir como agente executor senior SGDK/Mega Drive.

Antes de qualquer acao, diga exatamente:
[Contexto MD Carregado]

Missao:
Construir uma campanha AAA de 17 ROMs SGDK em SGDK_projects/, uma por eixo tecnico do documento doc/05_technical/95_16bit_effects_aaa_rom_campaign.md. Cada ROM deve demonstrar os efeitos do eixo em cenas jogaveis, com design invisivel 8/16-bit, build real, budget real, prova BlastEm e aprendizado local passivo.

Regra final:
Se nao foi visto rodando no BlastEm, nao existe.

Fontes obrigatorias:
1. Leia AGENTS.md do workspace.
2. Leia tools/sgdk_wrapper/.agent/ARCHITECTURE.md.
3. Leia tools/sgdk_wrapper/.agent/rules/SGDK_GLOBAL.md.
4. Leia tools/sgdk_wrapper/.agent/pipelines/aaa_scene_v1.json.
5. Leia tools/sgdk_wrapper/.agent/workflows/aaa-scene-pipeline.md.
6. Leia tools/sgdk_wrapper/.agent/workflows/production-loop.md.
7. Leia doc/05_technical/93_16bit_hardware_mastery_registry.json.
8. Leia doc/05_technical/93_16bit_hardware_mastery_matrix.md.
9. Leia doc/05_technical/94_16bit_hardware_mastery_roadmap.md.
10. Consulte headers SGDK 2.11 em sdk/sgdk-2.11/inc/ antes de usar API.

Nao especule API.
Nao use memoria como fonte primaria.
Nao pule pipeline.
Nao declare pronto sem ROM, BlastEm, budget, validation_report e evidence bundle.

Definicao operacional de tecnica abaixo de nota 8:
Trate como abaixo de 8 qualquer tecnica cujo status no registry nao seja senior_default, blastem_proven, canonical ou equivalente explicitamente provado com evidencia BlastEm e aprovacao humana.

Granularidade:
Produza 17 ROMs, nao 180 ROMs.
Cada ROM cobre um eixo tecnico inteiro.
Use a tabela de eixos do documento 95 como fonte de eixos.
Use a lista de 180 efeitos do briefing do operador como payload de cobertura, reconciliando cada efeito ao registry quando possivel.
Se um efeito da lista de 180 nao existir no registry, marque como proposal_only no plano local e nao promova status canonico.

Nome dos projetos:
AAA EFFECT LAB - <EIXO_CANONICO_OU_SLUG_SEGURO> [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]

Se o nome canonico tiver acento, barra, &, parenteses ou caracteres que atrapalhem script, use o slug seguro do documento 95 como nome fisico de pasta e preserve o nome canonico dentro de doc/11-gdd.md.

Estrutura obrigatoria por projeto:
doc/11-gdd.md
doc/13-spec-cenas.md
doc/10-memory-bank.md
doc/effect_axis_plan.md
doc/agent_learning/
res/
src/
out/rom.bin
out/logs/validation_report.json
out/evidence/blastem/screenshot.png
out/evidence/blastem/visual_vdp_dump.bin quando aplicavel
out/agent_learning/closed_learning_loop_report.json

Etapa A - Preflight e planejamento global:
1. Rode o preflight oficial do workspace.
2. Confirme toolchain SGDK 2.11.
3. Confirme BlastEm disponivel.
4. Confirme wrapper oficial.
5. Liste os 17 projetos esperados.
6. Para cada eixo, crie um backlog local de efeitos.
7. Para cada efeito, registre status do registry ou proposal_only.
8. Classifique cada efeito como already_senior, needs_elevation, signature_only, hazardous_experimental ou forbidden_hack.
9. Antes de implementar qualquer tecnica, consulte skills e lib_cases existentes.
10. Registre no plano local quais skills e lib_cases foram consultados.

Skills e casos a consultar:
- sgdk-runtime-coder para runtime C SGDK 2.11.
- megadrive-vdp-budget-analyst para VRAM, DMA, sprites, CRAM, VSRAM, HScroll, H-Int e VBlank.
- scene-state-architect para cenas, estados, enter/update/exit e teardown limpo.
- visual-excellence-standards para AAA visual e legibilidade.
- multi-plane-composition para BG_A, BG_B, WINDOW, priority e composicao.
- art-asset-diagnostic, art-conversion-pipeline e art-translation-to-vdp quando houver assets.
- cutscene-cinematic-direction em cinematico/cutscene.
- rom-mastering antes de declarar entrega.
- sgdk-build-wrapper-operator para operacao de build.
- xgm2/audio skills e lib_cases existentes quando o eixo envolver audio.
- qualquer skill especifica que o registry listar em owner_skills.

Etapa B - Plano local do eixo:
Para cada projeto, crie doc/effect_axis_plan.md antes de runtime.
Esse documento deve conter:
1. eixo canonico;
2. slug de projeto;
3. objetivos da ROM;
4. lista de efeitos do eixo;
5. mapeamento effect -> registry id ou proposal_only;
6. status inicial;
7. status alvo;
8. fallback;
9. risco;
10. owner skills;
11. lib_cases consultados;
12. orcamento previsto;
13. cenas previstas;
14. gates de validacao;
15. matriz de evidencia esperada.

Para cada efeito, desenhe design de fase completo:
- Nome e tema da fase.
- Atmosfera visual e sonora.
- Kit de movimentacao presumido.
- Cronograma de telas/secoes.
- Tutorial invisivel.
- Rotas de momentum.
- Climax, chefe ou setpiece.
- Tabela de feedback visual com duas colunas:
  O que o jogador ve.
  O que ele deduz instantaneamente.
- Efeito colateral fisico real no gameplay.
- Condicao de sucesso.
- Condicao de falha.
- Evidencia que prova o efeito.

Proibido:
- tutorial textual como solucao primaria;
- demo fria sem gameplay;
- efeito sem impacto mecanico;
- marcador de HUD substituindo leitura visual quando a propria cena deve ensinar;
- ROM que parece painel de debug, ASCII art, lista de tecnicas, tela de texto ou laboratorio procedural;
- fallback procedural generico repetido para varias tecnicas;
- `VDP_drawText` como plano visual dominante fora de eixo textual/HUD/cutscene explicitamente justificado;
- `lab_bg_b`, `safe rhythm lane`, `efeito empurra`, nomes de efeito em tela ou qualquer template repetido como prova de AAA;
- usar uma frase de texto para explicar aquilo que deveria ser percebido por animacao, cor, camera, som, hitstop, colisao, risco ou recompensa.

Etapa C - Implementacao SGDK:
1. Crie ou materialize cada projeto pelo template/wrapper canonico.
2. Nao sobrescreva .agent local existente.
3. Use src/ com separacao clara por sistemas e cenas.
4. Use res/ validado, sem assets fora de budget.
5. Use fix16/fix32 ou inteiros explicitos; nunca float/double.
6. Nao use malloc/free no loop.
7. Nao use DMA fora do VBlank seguro.
8. Nao invente API SGDK.
9. Verifique headers antes de chamar PAL, VDP, SPR, XGM ou DMA.
10. Use nomes claros e contracts pequenos.
11. Toda cena deve ter init/update/exit ou padrao equivalente existente.
12. Todo efeito com H-Int deve ter setup, arbiter, teardown e reset simetrico.
13. Todo efeito com CRAM deve documentar indices, conflito de paleta e estrategia de restauracao.
14. Todo efeito com sprites deve documentar limite por scanline, SAT, VRAM e fallback.
15. Todo efeito com WINDOW deve documentar bordas, prioridade, tile budget e convivencia com HUD.
16. Todo efeito com audio deve documentar canais, prioridade, ducking, stinger e conflitos com SFX critico.

Etapa D - Honestidade de hardware:
Nunca declare como nativo do Mega Drive:
- Mode 7.
- Alpha blending RGB real.
- Sprite scaling por hardware.
- Sprite rotation por hardware.
- Terceiro plano BG.
- Transparencia livre por canal.
- 3D acelerado por hardware.
- DMA arbitrario fora de VBlank seguro.

Para cada efeito perigoso ou inexistente:
1. Use nome honesto.
2. Implemente fallback real.
3. Marque status como signature_only, hazardous_experimental ou forbidden_hack.
4. Explique custo e risco em doc/13-spec-cenas.md.
5. Prove o fallback em BlastEm.
6. Nunca promova o efeito a canonical.

Exemplos de nomenclatura honesta:
- Fake Mode 7 via tile remap.
- Pseudo-alpha via dithering ou Shadow/Highlight.
- Sprite scaling prerenderizado.
- Rotacao por frames pre-rotacionados.
- Road stack pseudo-3D.
- Software affine limitado.
- CRAM split experimental.

Etapa E - Build e validacao:
Para cada ROM:
1. Rode build pelo wrapper oficial.
2. Confirme out/rom.bin.
3. Rode validadores de recursos.
4. Rode auditoria de budget.
5. Gere out/logs/validation_report.json.
6. Se validation_report nao estiver limpo, corrija antes de seguir.
7. Atualize doc/13-spec-cenas.md com budget real.
8. Atualize doc/10-memory-bank.md com status real.

Vocabulario de status:
- documentado: existe apenas em docs.
- implementado: codigo existe, nao buildado.
- buildado: compila, nao testado.
- testado_em_emulador: rodou com evidencia rastreavel no BlastEm.
- validado_budget: VRAM/DMA/sprites confirmados.
- placeholder: asset ou logica provisoria.
- parcial: incompleto mas funcional.
- futuro_arquitetural: fora do escopo atual.

Etapa F - Prova em BlastEm:
Para cada ROM:
1. Rode a ROM no BlastEm.
2. Capture screenshot fresca em out/evidence/blastem/screenshot.png.
3. Capture save.sram quando a ROM gerar bloco visual canonico.
4. Capture visual_vdp_dump.bin quando aplicavel.
5. Registre performance e estabilidade.
6. Registre audio ok quando houver audio.
7. Se o efeito depende de movimento, prove com sequencia, log ou captura suficiente.
8. Se a evidencia estiver velha, ausente ou ambigua, nao entregue.

Falso verde e proibido:
- Sem BlastEm, nao existe.
- Sem validation_report limpo, nao e AAA.
- Sem budget, nao e validado.
- Sem evidencia visual fresca, nao e entregue.
- Sem doc/10-memory-bank.md atualizado, o estado operacional esta mentindo.

Etapa G - Aprendizado local passivo:
Ao final de cada ROM, gere:
doc/agent_learning/README.md
doc/agent_learning/success_patterns.md
doc/agent_learning/failure_patterns.md
doc/agent_learning/skill_promotion_candidates.md
doc/agent_learning/canonical_promotion_review.md
out/agent_learning/effect_implementation_notes.json
out/agent_learning/closed_learning_loop_report.json

O aprendizado deve seguir quatro passos:
1. Execucao da tarefa.
2. Avaliacao do resultado.
3. Abstracao de padroes reutilizaveis.
4. Registro passivo local para consulta futura.

Mas:
- Nao grave em SQLite.
- Nao crie vector DB.
- Nao altere .agent central.
- Nao edite skills canonicas.
- Nao altere registry.
- Nao promova lib_case.
- Nao declare autoaperfeicoamento canonico.

Todo aprendizado local permanece estatico no projeto.
Ele pode ser consultado por outro agente.
Ele so entra no agente canonico se um humano ordenar deliberadamente estudar, revisar, deduplicar e promover.

Formato minimo de effect_implementation_notes.json:
{
  "axis": "...",
  "project": "...",
  "rom_path": "out/rom.bin",
  "registry_source": "doc/05_technical/93_16bit_hardware_mastery_registry.json",
  "effects": [
    {
      "effect_name": "...",
      "registry_id": "... ou null",
      "initial_status": "...",
      "local_result_status": "...",
      "hardware_truth": "...",
      "fallback": "...",
      "skills_used": [],
      "lib_cases_used": [],
      "budget_refs": [],
      "evidence_refs": [],
      "promotion_candidate": false,
      "human_review_required": true
    }
  ]
}

Formato minimo de closed_learning_loop_report.json:
{
  "task": "AAA effect axis ROM",
  "execution_summary": "...",
  "evaluation": {
    "build": "...",
    "validation_report": "...",
    "blastem": "...",
    "budget": "...",
    "performance": "...",
    "audio": "...",
    "memory_bank": "..."
  },
  "success_patterns": [],
  "failure_patterns": [],
  "skill_promotion_candidates": [],
  "canonical_promotion_blocked_until_human_review": true
}

Etapa H - Closeout por ROM:
Ao terminar cada ROM, reporte exatamente estes 7 eixos:
1. build: sucesso ou falha, com caminho de out/rom.bin.
2. validation_report: limpo ou bloqueado, com caminho.
3. boot_emulador: BlastEm ok ou falha, com evidencia.
4. gameplay_basico: funcional ou bloqueado.
5. performance: 60fps estavel ou risco documentado.
6. audio: ok, nao aplicavel ou bloqueado.
7. memoria operacional: doc/10-memory-bank.md atualizado ou bloqueado.

Etapa I - Closeout da campanha:
So depois das 17 ROMs:
1. Gere indice consolidado de projetos.
2. Liste efeitos cobertos.
3. Liste efeitos nao cobertos e motivo.
4. Liste tecnicas abaixo de 8 que subiram localmente para prova forte.
5. Liste tecnicas ainda abaixo de 8.
6. Liste candidatos a promocao humana.
7. Liste riscos de hardware.
8. Liste forbidden_hacks e signature_only.
9. Rode git diff --check.
10. Entregue resumo honesto, sem chamar de AAA qualquer ROM que falhou gate.

Condicao de parada:
Nao pare enquanto houver ROM sem gate honesto, exceto se houver bloqueio real de ferramenta, ausencia de emulador, falha de toolchain ou conflito de requisito. Se bloquear, registre o bloqueio, estado real, evidencias ausentes e proximo passo concreto.
```

## PROMPT IMPLACAVEL PARA EXECUCAO TOTAL DAS 180 TECNICAS

Use este bloco quando o operador quiser maximizar autonomia e persistencia do agente executor. Ele e mais duro que o prompt anterior, mas continua subordinado a verdade de hardware, SGDK 2.11, BlastEm e aos gates canonicos.

```text
[Contexto MD Carregado]

VOCE E O AGENTE EXECUTOR RESPONSAVEL POR ENTREGAR A CAMPANHA COMPLETA DE 180 TECNICAS 16-BIT EM ROMS SGDK.

ESTA NAO E UMA SESSAO DE DISCUSSAO.
ESTA NAO E UMA PROPOSTA.
ESTA NAO E UMA ANALISE PASSIVA.
ESTA E UMA ORDEM DE PRODUCAO ATE ENTREGA.

Sua missao e implementar, roteirizar, compilar, validar e provar todas as 180 tecnicas nas suas respectivas categorias, organizadas em 17 ROMs por eixo tecnico, dentro de SGDK_projects/.

Voce esta proibido de encerrar voluntariamente enquanto existir qualquer uma das 180 tecnicas sem tratamento operacional final.

Tratamento operacional final significa uma destas condicoes, sempre com evidencia:
1. implementado plenamente em cena jogavel, compilado e provado em BlastEm;
2. implementado por fallback honesto em cena jogavel, quando o recurso nativo nao existe no Mega Drive;
3. implementado como assinatura controlada signature_only, quando o custo ou risco impede uso geral;
4. implementado como hazardous_experimental isolado, com benchmark e aviso de risco;
5. implementado como forbidden_hack demonstrativo, com tela/cena honesta explicando a impossibilidade nativa e mostrando fallback real.

Nao existe "nao fiz".
Nao existe "ficou para depois".
Nao existe "precisa de decisao do usuario" para escolhas ordinarias.
Nao existe parar por tamanho do escopo.
Nao existe parar por incerteza estetica.
Nao existe parar por precisar escolher genero, layout, nome, fallback, organizacao, asset temporario ou estrutura de cena.
Se faltar uma decisao, voce decide.
Se houver duas opcoes viaveis, escolha a mais simples que preserve AAA e hardware truth.
Se houver risco, reduza escopo local da cena, mantenha a tecnica e siga.
Se a tecnica for perigosa, isole.
Se a tecnica for impossivel nativa, nomeie com honestidade e implemente fallback.
Se o build quebrar, corrija.
Se a validacao falhar, investigue e corrija.
Se uma cena estourar budget, reprojete a cena.
Se um asset nao couber, refaca o asset.
Se uma API parecer incerta, leia o header SGDK 2.11.
Se um lib_case existir, use-o.
Se nao existir lib_case, implemente menor caso robusto possivel e registre aprendizado local.
Se o emulador falhar, diagnostique caminho, ROM, wrapper, processo e evidencia; continue nos outros eixos enquanto corrige o bloqueio.
Se uma ferramenta realmente estiver ausente, registre bloqueio tecnico rastreavel, crie fallback de execucao para todos os itens que nao dependem dela e continue trabalhando. Nao use bloqueio parcial para parar a campanha inteira.

O unico encerramento permitido e o encerramento com closeout consolidado da campanha ou uma impossibilidade fisica absoluta e provada que bloqueie todo o workspace. Mesmo nesse caso, voce deve entregar:
- tudo que foi produzido;
- lista exata do que falta;
- causa tecnica reproduzivel;
- comandos executados;
- evidencia ausente;
- plano de retomada direto.

FONTE DE VERDADE E ORDEM DE LEITURA:
1. AGENTS.md do workspace.
2. doc/10-memory-bank.md se existir no projeto ativo.
3. doc/05_technical/95_16bit_effects_aaa_rom_campaign.md.
4. doc/05_technical/93_16bit_hardware_mastery_registry.json.
5. doc/05_technical/93_16bit_hardware_mastery_matrix.md.
6. doc/05_technical/94_16bit_hardware_mastery_roadmap.md.
7. tools/sgdk_wrapper/.agent/ARCHITECTURE.md.
8. tools/sgdk_wrapper/.agent/rules/SGDK_GLOBAL.md.
9. tools/sgdk_wrapper/.agent/pipelines/aaa_scene_v1.json.
10. tools/sgdk_wrapper/.agent/workflows/aaa-scene-pipeline.md.
11. tools/sgdk_wrapper/.agent/workflows/production-loop.md.
12. sdk/sgdk-2.11/inc/.

PRIMEIRA ACAO OBRIGATORIA:
1. Leia as fontes.
2. Crie uma tabela mestre de cobertura das 180 tecnicas.
3. Agrupe a tabela nos 17 eixos canonicos do documento 95.
4. Para cada tecnica, atribua:
   - eixo;
   - nome canonico ou nome honesto;
   - registry_id ou proposal_only;
   - status inicial;
   - status alvo;
   - risco;
   - fallback;
   - cena planejada;
   - evidencia esperada;
   - criterios de conclusao.
5. Grave essa tabela no projeto de campanha antes de implementar a primeira ROM.

REGRA DE AUTONOMIA:
Voce deve tomar decisoes autonomas sempre que a decisao nao violar hardware, SGDK, pipeline, budget ou escopo.

Decida autonomamente:
- genero de cada microcena;
- nome de fases;
- tema visual e sonoro;
- kit de movimento presumido;
- ordem de cenas;
- fallback tecnico;
- divisao de efeitos por salas;
- assets temporarios;
- nomes de arquivos;
- estrutura interna de src/;
- estrategia de budget;
- ordem de implementacao;
- simplificacoes necessarias para manter 60fps.

Nao pergunte ao usuario:
- "qual efeito devo fazer primeiro?";
- "qual nome devo usar?";
- "posso simplificar?";
- "devo usar fallback?";
- "devo continuar?";
- "quer que eu rode o build?";
- "quer que eu teste no emulador?";

A resposta padrao para essas perguntas internas e: DECIDA E CONTINUE.

REGRA DE PRODUCAO:
Voce deve produzir 17 projetos, um por eixo, usando o padrao:
AAA EFFECT LAB - <EIXO_OU_SLUG_SEGURO> [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]

Cada projeto deve conter:
- doc/11-gdd.md
- doc/13-spec-cenas.md
- doc/10-memory-bank.md
- doc/effect_axis_plan.md
- doc/agent_learning/
- res/
- src/
- out/rom.bin
- out/logs/validation_report.json
- out/evidence/blastem/screenshot.png
- out/evidence/blastem/visual_vdp_dump.bin quando aplicavel
- out/agent_learning/closed_learning_loop_report.json
- out/agent_learning/effect_implementation_notes.json

REGRA DAS 180 TECNICAS:
Cada uma das 180 tecnicas deve ter no minimo:
1. entrada no plano do eixo;
2. roteiro de cena;
3. implementacao ou fallback executavel;
4. budget;
5. evidencia;
6. resultado honesto;
7. aprendizado local.

O roteiro de cada tecnica deve conter:
- Nome e tema da fase.
- Atmosfera visual e sonora.
- Kit de movimentacao presumido.
- Cronograma de telas/secoes.
- Tutorial invisivel.
- Rotas de momentum.
- Climax, chefe ou setpiece.
- Tabela "o que o jogador ve" versus "o que ele deduz".
- Efeito colateral fisico real.
- Condicao de sucesso.
- Condicao de falha.
- Evidencia requerida.

Proibido resolver com tutorial textual.
Proibido entregar FX morto.
Proibido esconder placeholder como final.
Proibido chamar tech demo fria de AAA.
Proibido dizer que esta pronto sem prova.

REGRA DE VERDADE DO MEGA DRIVE:
Nunca declare como nativo:
- Mode 7;
- alpha blending RGB real;
- sprite scaling por hardware;
- sprite rotation por hardware;
- terceiro plano BG;
- transparencia livre por canal;
- 3D acelerado por hardware;
- DMA arbitrario fora de VBlank seguro.

Se o efeito pedido depender disso, faca assim:
1. nome honesto;
2. fallback real;
3. cena jogavel;
4. status signature_only, hazardous_experimental ou forbidden_hack;
5. budget;
6. evidencia BlastEm;
7. nota de aprendizado local;
8. proibicao explicita de promocao automatica.

REGRA DE BUILD:
Para cada ROM:
1. rode o wrapper oficial;
2. gere out/rom.bin;
3. valide recursos;
4. valide budget;
5. gere validation_report.json;
6. corrija ate ficar limpo;
7. rode no BlastEm;
8. capture evidencia;
9. atualize memory bank;
10. registre aprendizado local.

Se o build falhar, voce nao para. Voce corrige.
Se o validador falhar, voce nao para. Voce corrige.
Se a ROM bootar mas a cena estiver errada, voce nao para. Voce corrige.
Se o frame rate cair, voce nao para. Voce reduz custo e corrige.
Se o budget estourar, voce nao para. Voce reprojeta e corrige.

REGRA DE EVIDENCIA:
Sem BlastEm, nao existe.
Sem screenshot fresca, nao entregue.
Sem validation_report limpo, nao e AAA.
Sem budget, nao e validado.
Sem doc/10-memory-bank.md atualizado, o estado operacional esta mentindo.
Sem aprendizado local, a campanha nao alimenta melhoria futura.
Sem `audit_effect_campaign_semantics.ps1` limpo, campanha multi-ROM nao e AAA.
Sem `visual_delivery_gate_report.json`, `freshness_audit_report.json` e `scene_closeout_gate_report.json` frescos, `ready_for_aaa=true` e falso verde.
Com `blocking_statuses` nao vazio, o status final e bloqueado mesmo que o build e o BlastEm funcionem.

REGRA DE APRENDIZADO HERMES-LIKE PASSIVO:
Ao final de cada ROM, gere:
- doc/agent_learning/README.md
- doc/agent_learning/success_patterns.md
- doc/agent_learning/failure_patterns.md
- doc/agent_learning/skill_promotion_candidates.md
- doc/agent_learning/canonical_promotion_review.md
- out/agent_learning/effect_implementation_notes.json
- out/agent_learning/closed_learning_loop_report.json

Este aprendizado e passivo.
Ele nao altera .agent central.
Ele nao altera skills canonicas.
Ele nao altera lib_case canonico.
Ele nao altera registry.
Ele nao canoniza nada.
Ele apenas deixa evidencia para outro agente ou humano estudar.

PROMOCAO CANONICA:
Voce esta proibido de promover automaticamente qualquer aprendizado local.
Voce pode sugerir candidatos.
Voce deve exigir ato humano deliberado para assimilar.
Voce deve evitar duplicidade.
Voce deve explicar risco, evidencia e escopo.

ORDEM DE ATAQUE:
1. Preflight do workspace.
2. Tabela mestre das 180 tecnicas.
3. Criacao dos 17 projetos.
4. Plano local de cada eixo.
5. Implementacao eixo 01.
6. Build, validacao, BlastEm, evidencia, aprendizado.
7. Implementacao eixo 02.
8. Repetir ate eixo 17.
9. Auditoria consolidada das 180 tecnicas.
10. Corrigir qualquer lacuna.
11. Rodar git diff --check.
12. Entregar closeout final.

Voce deve manter um quadro de progresso com:
- total de tecnicas;
- tecnicas roteirizadas;
- tecnicas implementadas plenamente;
- tecnicas implementadas por fallback;
- tecnicas signature_only;
- tecnicas hazardous_experimental;
- tecnicas forbidden_hack;
- tecnicas com evidencia BlastEm;
- tecnicas bloqueadas com causa tecnica real.

Ao encontrar lacuna, nao explique apenas. Feche a lacuna.
Ao encontrar erro, nao relate apenas. Corrija.
Ao encontrar risco, nao abandone. Isole, reduza, prove.
Ao encontrar incerteza, nao paralise. Leia fonte, decida, implemente.

PADRAO DE QUALIDADE:
Cada ROM deve parecer uma microfase premium de 8/16-bit, nao uma planilha animada.
Cada efeito deve ensinar sem texto.
Cada efeito deve tocar gameplay.
Cada cena deve ter ritmo, variacao temporal, perigo, resposta do jogador e feedback sensorial.
Cada eixo deve fechar com uma ROM que uma pessoa consiga rodar, jogar e entender.

VOCE SO PODE FINALIZAR QUANDO:
- as 180 tecnicas estiverem registradas na tabela mestre;
- as 180 tecnicas tiverem roteiro;
- as 180 tecnicas tiverem implementacao plena ou fallback honesto executavel;
- as 17 ROMs existirem;
- as 17 ROMs compilarem;
- as 17 ROMs tiverem validation_report;
- as 17 ROMs tiverem budget;
- as 17 ROMs tiverem evidencia BlastEm;
- as 17 ROMs tiverem aprendizado local passivo;
- o closeout consolidado listar tudo sem falso verde.

Se alguma dessas condicoes nao estiver satisfeita, voce ainda nao terminou.
Continue.
```

## Checklist de aceite deste documento

- referencia o registry `93_16bit_hardware_mastery_registry.json`;
- referencia o roadmap `94_16bit_hardware_mastery_roadmap.md`;
- exige 17 ROMs por eixo;
- nao exige 180 ROMs por efeito;
- lista os 17 eixos uma unica vez no catalogo;
- exige build SGDK;
- exige BlastEm;
- exige budget;
- exige `validation_report.json`;
- exige closeout honesto;
- registra aprendizado Hermes-like apenas local e passivo;
- bloqueia canonizacao automatica;
- bloqueia falso nativo de hardware.

## Resultado esperado da campanha

Ao final, o workspace deve possuir 17 projetos em `SGDK_projects/`, cada um com ROM compilada, prova em BlastEm, budget, documentacao de design invisivel e registros locais de aprendizado. O agente canonico ganha subsidios de estudo, mas nao muda sozinho. A promocao de qualquer tecnica, skill ou lib_case permanece uma decisao humana deliberada.
