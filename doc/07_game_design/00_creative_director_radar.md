# Creative Director Radar

Este documento canoniza a postura propositiva do agente. O agente nao deve
apenas verificar se o projeto compila, cabe no VDP ou possui documentos. Ele
deve diagnosticar o que falta para o jogo ser memoravel dentro da propria
proposta.

O artefato machine-readable correspondente e:

- `tools/sgdk_wrapper/schemas/creative_director_radar.schema.json`
- por projeto: `doc/creative_director_radar.json`

## Regra Central

Proatividade nao e feature creep.

O agente deve propor melhorias de direcao quando perceber que o jogo esta
correto, mas generico. Porem nenhuma proposta entra no GDD, TDD, runtime ou
escopo de entrega sem decisao explicita, documentacao sincronizada e evidencia
esperada.

## Quando Emitir

Emitir ou atualizar `doc/creative_director_radar.json` quando:

- o projeto for novo;
- houver reseed de escopo;
- o alvo for `vertical_slice_candidate` ou `ready_for_aaa`;
- o projeto tiver build funcional, mas parecer laboratorio, prototipo ou
  "jogo correto sem alma";
- a iteracao tocar GDD, TDD, front-end, mecanica core, audio, visual identity,
  boss, setpiece, fase principal ou first playable slice.

Projetos `LAB/TECHDEMO` podem manter o radar em `draft`, mas nao podem usar
isso para reivindicar `ready_for_aaa`.

## Eixos Do Radar

O radar deve olhar pelo menos cinco eixos quando o projeto busca slice ou AAA:

- `mechanics`: mecanica assinatura, risco/recompensa, controle, resposta.
- `level_design`: fase que ensina, pressiona, surpreende e recompensa.
- `audio`: tema, hook, SFX prioritario, silencio, stinger ou camada adaptativa.
- `visual_identity`: silhueta, paleta, UI, logo, personagem, mundo.
- `technical_spectacle`: truque de hardware com funcao de gameplay ou tom.
- `game_feel`: impacto, hitstop, gravidade, aceleracao, cancelamento, recovery.
- `front_end`: title, press-start, menu, fonte e primeira promessa.
- `narrative_atmosphere`: mundo, tom, misterio, humor ou peso emocional.
- `systems_depth`: economia, estrategia, progressao, IA, sinergia.

## Como Usar Benchmarks

Jogos de referencia servem para nomear qualidade, nao para copiar IP.

Exemplos de uso correto:

- `Street Fighter II Turbo`: risco/recompensa, leitura de frame, controle de
  terreno.
- `Chrono Trigger`: fluxo sem interrupcao, narrativa e combate integrados.
- `Herzog Zwei`: comando em tempo real e profundidade sistemica.
- `Rampart`: ciclo simples com pressao de tempo e reconstrução significativa.
- `Clock Tower`: vulnerabilidade, silencio e ameaca persistente.
- `Streets of Rage 2`: impacto fisico, sprites grandes, musica memoravel.
- `Gunstar Heroes`: energia, variedade e espetaculo legivel.
- `Zero Tolerance`: recuo honesto de viewport para preservar performance.
- `Super Mario World`: controle sublime, mapa com segredos e leitura amigavel.
- `Super Metroid`: narrativa ambiental, atmosfera e progressao guiada.
- `Tetris Attack`: leitura sob pressao e pureza de interface.
- `Super Mario Kart`: direcao fisica e identidade de item/pista.
- `International Superstar Soccer Deluxe`: animacao fluida e fisica de bola.
- `A Link to the Past`: clareza de aventura, mundo paralelo e ritmo de dungeon.

Uso proibido:

- copiar asset, layout, paleta, logo, personagem, musica, nome, historia ou
  composicao;
- usar benchmark como prompt de copia;
- prometer tecnologia de outra plataforma sem tradeoff Mega Drive/SGDK;
- confundir lista de referencias com direcao autoral.

Barra viva da cena (`doc/03_art/18_live_scene_bar.md`): Rheo e Pigsy entram
no radar como **oficio** (densidade arcade legal; traducao rica nativa),
nunca como IP. Um projeto "correto mas generico" que nao passa os 12 checks
recebe `live_scene_bar_failed` alem de `signature_gap`.

## Formato Do Diagnostico

Cada proposta do radar deve responder:

- qual sintoma atual limita o jogo;
- por que isso reduz a memorabilidade;
- qual movimento de direcao resolveria;
- qual documento precisa mudar (`doc/11-gdd.md`, `doc/13-spec-cenas.md`,
  TDD, audio card, brand manifest, etc.);
- qual skill e dona;
- qual evidencia prova que a proposta funcionou;
- qual fallback preserva o escopo se a ideia nao couber no hardware.

## Sinais De Jogo Generico

O agente deve sinalizar `signature_gap` quando houver:

- mecanica funcional sem payoff memoravel;
- fase correta sem surpresa, ritmo ou momento assinatura;
- audio funcional sem hook, silencio intencional ou SFX com prioridade;
- HUD, title, logo ou fonte com cara de debug/prototipo;
- boss grande sem regra visual, telegraph, fase ou payoff proprio;
- FX bonito sem efeito colateral fisico, risco, recompensa ou leitura;
- arte tecnicamente limpa, mas sem identidade autoral do projeto;
- build que roda no BlastEm, mas ainda parece benchmark de sistema.

## Politica De Decisao

O agente deve ser propositivo em pareceres:

- "o que esta correto";
- "o que ainda esta generico";
- "qual e a oportunidade assinatura";
- "qual e o menor passo implementavel";
- "qual gate prova que melhorou".

O agente nao deve executar proposta nova como escopo assumido sem:

- decisao humana ou escopo ja declarado;
- atualizacao de GDD/spec/TDD quando aplicavel;
- budget e fallback;
- registro em changelog/memory quando implementado;
- evidencia BlastEm quando for entregue.

## Gate De Maturidade

Para `approved_for_production`, `doc/creative_director_radar.json` deve ter:

- pelo menos 5 eixos de benchmark;
- pelo menos 3 pilares assinatura;
- pelo menos 5 gaps/propostas priorizadas;
- pelo menos 1 candidato de cena assinatura;
- politica de nao-copia ativa;
- politica de anti-feature-creep ativa.

Sem isso, o projeto pode continuar em planejamento ou laboratorio, mas nao deve
ser descrito como fatia AAA madura.
