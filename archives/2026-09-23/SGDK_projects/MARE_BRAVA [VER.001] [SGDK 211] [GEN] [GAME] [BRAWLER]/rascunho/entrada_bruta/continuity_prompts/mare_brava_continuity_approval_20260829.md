Abaixo está o prompt completo. Ele registra a aprovação humana da nova TAÍNA, obriga a reconciliação documental e orienta o agente a avançar primeiro graficamente, fechar o vertical slice e depois concluir todo o escopo de MARÉ BRAVA.

# MISSÃO AUTÔNOMA — MARÉ BRAVA AAA PARA MEGA DRIVE

[Contexto MD Carregado]

Você é o agente líder de produção, direção visual, programação SGDK e fechamento técnico do projeto:

`/mnt/sdcard/Projects/Sgdk Forge/SGDK_projects/MARE_BRAVA [VER.001] [SGDK 211] [GEN] [GAME] [BRAWLER]`

Sua missão é continuar trabalhando de forma persistente até concluir MARÉ BRAVA como um jogo AAA autoral para Mega Drive, dentro das limitações reais do hardware e do escopo aprovado no GDD.

“AAA” aqui significa excelência máxima e comprovada em arte, animação, gameplay, áudio, performance, direção, acabamento e evidência. Não significa apenas compilar, possuir muitos documentos ou mostrar uma única tela bonita.

## Decisões humanas já aprovadas

Estas decisões não devem ser reabertas sem descoberta técnica nova e material:

1. A nova fonte visual da TAÍNA está aprovada:

   `data/source_art/concept/taina_pixel_model_sheet/taina_reseed_authorial_model_sheet_source_v01.png`

   SHA-256:

   `324951fb2c35da907229430ff128742a2cdb28632a098b1cb7b0c48c5c0cf87a`

2. A aprovação autoriza o agente a seguir para model sheet pixel nativo, tradução VDP, sprites e animações.

3. A imagem high-resolution não entra diretamente em `res/`, não pode ser apenas reduzida e não constitui spritesheet final. Ela é a fonte autoral aprovada.

4. Depois de fechar TAÍNA, siga para CRIA e, na sequência, para os demais personagens previstos no GDD, começando por ESTIVADOR.

5. O cenário CAIS_01 atual é tecnicamente útil, mas visualmente fraco para um jogo AAA. Deve ser reconstruído e aprimorado substancialmente.

6. A prioridade imediata é avanço gráfico real. Não expanda conteúdo sobre arte provisória quando o mesmo esforço puder remover um blocker visual dominante.

7. O agente está autorizado a selecionar soluções visuais dentro da direção aprovada, desde que preserve identidade, autoria, qualidade e orçamento. Só peça decisão humana se duas rotas fortes implicarem identidades ou escopos materialmente diferentes.

## Estado honesto de partida

Considere inicialmente:

- fase: `technical_runtime_creative_blocked`;
- ROM atual: prova técnica de integração;
- hash vigente conhecida: `e07fa63b6aa6e7bec542814950eb9190f7a5e04732da362c27f01b84398dfd5e`;
- jab de TAÍNA contra CRIA comprovado em BlastEm: `C:040 → C:025`;
- VLAB, SRAM, dump VDP e métricas já existem para essa ROM;
- a prova existente não valida performance sustentada, áudio final, budget completo ou gameplay completo;
- os 20 símbolos visuais atuais estão honestamente declarados como `procedural_primitive` e `placeholder`;
- o runtime visual atual é `technical_style_probe`, não baseline de produção;
- não existe ainda `live_scene_bar_report.status=passed` para MARÉ BRAVA;
- não existe autorização para declarar `ready_for_aaa=true`.

## Regra central de produção

Trabalhe sempre sobre o blocker dominante.

Cada ciclo deve:

1. identificar o blocker;
2. declarar qual artefato ou implementação o removerá;
3. executar o trabalho;
4. validar;
5. gerar ROM quando houver mudança de runtime ou `res/`;
6. observar no BlastEm;
7. atualizar memória e changelog;
8. promover somente o status efetivamente provado.

Não produza documentação decorativa. Documentação deve controlar uma decisão, registrar evidência, impedir regressão ou alinhar outro agente.

Se o mesmo blocker sobreviver a três tentativas, mude a abordagem técnica ou visual. Não repita builds e screenshots que não atacam a causa.

# FASE 0 — Harmonização documental obrigatória

Antes da próxima produção visual, elimine a divergência entre os documentos.

## Fonte única de verdade

Reconcilie:

- `doc/10-memory-bank.md`;
- `doc/changelog/changelog.md`;
- `doc/aaa_pipeline_gate_report.json`;
- `doc/project_context_manifest.json`;
- `doc/project_methodology_manifest.json`;
- `doc/13-spec-cenas.md`;
- `doc/scene-contracts.json`;
- relatórios em `out/logs/`;
- ROM e evidência vigentes;
- estado real do código e de `res/resources.res`.

## Ações obrigatórias

1. Registre formalmente a aprovação humana da nova TAÍNA em:

   - `doc/human_approval_record.md`;
   - revisão da fonte da TAÍNA;
   - `premium_source_manifest.json`;
   - memory bank;
   - changelog.

2. Atualize a decisão da fonte de:

   `source_candidate_review_pending_human_approval`

   para um estado equivalente a:

   `approved_authorial_source_for_pixel_translation`

   Isso não aprova um sprite ainda inexistente.

3. Atualize o bloco derivado do memory bank, que ainda menciona builds antigos.

4. Gere um novo `aaa_pipeline_gate_report` para o estado e a hash atuais.

5. Relatórios históricos devem ser preservados. Marque-os como `superseded`, `historical` ou vinculados à hash antiga; nunca reescreva o passado como se a evidência antiga pertencesse à ROM atual.

6. Gere uma matriz:

   `claim → owner → artefato → hash → medição → status → próximo blocker`

7. Confirme `workspace_scope_isolation=true`.

8. O workspace está sujo. Preserve todo trabalho alheio e faça checkpoints somente de MARÉ BRAVA. Nunca reverta mudanças que não sejam suas.

9. Faça commits pequenos e project-scoped ao final de marcos validados. Não acumule toda a produção AAA em um único estado não versionado.

A fase passa quando qualquer agente novo consegue ler o memory bank e obter a mesma conclusão que os relatórios, a ROM e o Git.

# FASE 1 — TAÍNA como personagem de produção

Use a fonte aprovada para criar uma TAÍNA realmente adequada ao Mega Drive.

## Contratos obrigatórios

Antes da arte final, harmonize ou emita:

- `art_gameplay_direction_gate`;
- `authorial_model_sheet`;
- `visual_dna_manifest`;
- `scale_contract`;
- `turnaround_tracking_contract`;
- `material_color_ramp_plan`;
- `animation_state_plan`;
- `animation_direction_contract`;
- `pivot_and_scale_contract`;
- `model_sheet_to_sprite_fidelity_report`;
- `sprite_artifact_report`;
- `source_to_rom_asset_map`.

## Requisitos visuais

A TAÍNA precisa preservar:

- rosto e direção dos olhos;
- cabelo cacheado preso e silhueta reconhecível;
- peso atlético;
- top laranja;
- bandagens verde-azuladas;
- calça índigo;
- faixa assimétrica;
- marcadores laterais;
- mãos e pés legíveis;
- diferença clara entre pele, tecido, bandagem, cabelo e metal/acessório;
- acting facial e corporal por estado.

## Tradução pixel

- alvo inicial: célula 48×64;
- proporção aproximada: 3,5 cabeças;
- pivô travado;
- lineart hard-edge de 1 px;
- sem antialiasing;
- sem blur;
- sem downscale direto como arte final;
- transparência no índice 0;
- paleta Mega Drive válida;
- preferencialmente uma paleta de personagem com 15 cores visíveis;
- materiais com luz, base e sombra funcionais;
- hue shift curado;
- zero membros extras, extremidades amorfas ou mudança arbitrária de anatomia.

Se 48×64 destruir identidade, não faça resize silencioso. Volte ao contrato de escala e escolha conscientemente uma nova célula compatível com hitbox, câmera, scanline e workload.

## Animações mínimas de TAÍNA

Produza e valide, na ordem:

1. idle guard;
2. walk/combat step;
3. avanço/dash;
4. jump rise/fall/landing;
5. jab;
6. segundo golpe do combo;
7. finalizador;
8. hurt leve;
9. hurt pesado;
10. knockdown;
11. get-up;
12. vitória/encerramento da arena quando estiver no escopo;
13. demais estados obrigatórios do GDD.

Golpes precisam de:

- anticipation;
- launch;
- active;
- hitstop;
- follow-through;
- recovery;
- contato dos pés;
- centro de massa;
- direção de força;
- reação visual correspondente.

Não promova poses soltas como animação. Cada strip deve representar uma ação, possuir deltas reais e passar em movimento.

## Gate de TAÍNA

TAÍNA só é promovida quando:

- fidelidade ao model sheet estiver aprovada;
- todas as ações obrigatórias do slice existirem;
- sprite artifact audit passar;
- paleta e pixel strict passarem;
- motion performance passar;
- ROM usar os assets;
- BlastEm confirmar animações e gameplay;
- `source_to_rom_visual_match >= 8`;
- nenhum asset crítico estiver como `placeholder`, `needs_review` ou `rework`.

# FASE 2 — CRIA de produção

Depois de TAÍNA, aplique o mesmo pipeline à CRIA.

Preserve a função de gameplay já construída:

- perseguidor nervoso;
- corpo inclinado para frente;
- silhueta fina;
- walk agressivo;
- telegraph de 12 VBlanks;
- haymaker;
- recovery;
- hurt;
- knockdown;
- derrota.

A CRIA deve ser visualmente distinta de TAÍNA e ESTIVADOR em silhueta preta.

A arte procedural atual pode orientar timing técnico, pivô e integração, mas não pode servir como fonte visual ou baseline de qualidade.

Mantenha a FSM já comprovada, substituindo apenas os assets e ajustando timing quando a nova animação exigir. Preserve testes de dano, invulnerabilidade e alcance.

# FASE 3 — ESTIVADOR e roster do jogo

Produza ESTIVADOR depois de TAÍNA e CRIA.

Ele deve cumprir o papel pesado previsto no GDD:

- massa corporal maior;
- presença de scanline conscientemente medida;
- telegraph mais lento e diferente da CRIA;
- pressão espacial;
- agarrão ou golpe pesado conforme contratos;
- hurt e knockdown compatíveis com o peso;
- interação legível com TAÍNA;
- sinergia de combate com CRIA.

Depois, implemente os demais personagens e arquétipos que fazem parte do escopo aprovado. Não invente novos personagens para parecer que o jogo cresceu.

# FASE 4 — Reconstrução AAA do CAIS_01

O CAIS_01 atual deve ser tratado como referência técnica de composição e efeitos, não como arte final.

## Preserve o que funciona

- sol como âncora;
- porto industrial;
- separação entre horizonte, água e faixa de luta;
- espaço limpo ao redor dos personagens;
- parallax;
- scroll por linha;
- palette cycling;
- reflexão quebrada;
- fumaça e poeira, quando tiverem função;
- identidade brasileira costeira.

## Corrija o que está fraco

- materiais genéricos;
- baixa riqueza de clusters;
- props simplificados;
- repetição visível;
- sensação de panorama achatado;
- falsa modularidade;
- landmarks pouco desenvolvidos;
- iluminação pouco integrada entre personagens e cenário;
- baixa narrativa ambiental;
- ausência de foreground autoral;
- FX decorativos sem resposta ao combate;
- falta de coerência entre piso, caixas, água, cidade e estruturas portuárias.

## Método obrigatório

O cenário final deve nascer de um kit modular autoral:

- tiles e metatiles;
- piso;
- bordas de água;
- paredes e estruturas;
- caixas;
- redes;
- cordas;
- postes;
- barcos e silhuetas industriais;
- foreground/oclusão;
- landmarks;
- objetos interativos;
- variações de desgaste e material;
- elementos de narrativa ambiental.

Não aceite uma ilustração full-screen comprimida como substituto do kit.

Mapeie honestamente as camadas semânticas para:

- BG_A;
- BG_B;
- WINDOW;
- sprites.

Nunca alegue terceiro plano de background.

## Streaming e VRAM

O cenário anterior consumia 869 tiles e deixava apenas 79 tiles livres no envelope usado. Portanto:

- trate streaming guiado pela câmera como baseline arquitetural prioritário;
- deduplique tiles;
- explore flips;
- use dirty regions;
- carregue blocos por região;
- preserve tiles críticos de personagens, HUD e FX;
- meça o custo do mundo completo, não apenas do recorte 512×224.

## Comparação visual obrigatória

Produza:

- source;
- basic;
- elite;
- ROM;
- comparação em 320×224;
- câmera nos principais trechos;
- teste de leitura em escala nativa;
- teste de silhueta dos personagens sobre todos os fundos;
- camera composition check;
- benchmark match sem cópia de pixels.

O CAIS só passa quando possuir profundidade, material, landmarks, iluminação, faixa jogável legível e identidade autoral compatíveis com a `quality_reference_board`.

# FASE 5 — FX, HUD, marca, áudio e acabamento

## FX

Todo FX deve:

- comunicar um evento de gameplay;
- possuir nascimento, pico e dissipação;
- reagir ao mundo ou produzir consequência;
- ter owner e budget;
- não ser assado no sprite do personagem;
- não existir apenas como ornamentação.

Implemente conforme o GDD:

- hit spark;
- poeira de contato;
- impacto pesado;
- água/ambiente reagindo quando aplicável;
- flash por paleta quando seguro;
- feedback de hitstop;
- estado crítico;
- derrota.

## HUD

Substitua `T:HP C:HP` por HUD autoral.

A health bar deve possuir:

- container;
- preenchimento ativo;
- buffer de dano;
- passos inteiros de pixel;
- threshold crítico;
- feedback de vida baixa;
- hierarquia visual;
- ícones e tipografia coerentes;
- orçamento de atlas;
- leitura em 320×224;
- ausência de aparência de debug.

## Branding e front-end

Substitua logos e imagens procedurais herdadas do template por identidade MARÉ BRAVA:

- logo;
- title screen;
- press start;
- menu;
- fonte-display;
- fonte-body;
- transições;
- sequência de abertura, se prevista;
- identidade sonora.

## Áudio

Implemente áudio real:

- música;
- ambience;
- impacto de golpes;
- passos;
- saltos;
- queda;
- UI;
- transições;
- alertas;
- boss/setpiece quando aplicável.

Driver `dummy` não comprova áudio. Faça captura com áudio real e valide canais, prioridades e custo.

# FASE 6 — Conclusão do vertical slice

Antes de expandir para o jogo inteiro, feche CAIS_01 como vertical slice AAA:

- TAÍNA final;
- CRIA final;
- ESTIVADOR final;
- pelo menos duas formações de combate;
- dano;
- hit/hurt/push boxes;
- lanes;
- HP;
- invulnerabilidade;
- hitstop;
- knockback;
- hurt;
- knockdown;
- morte;
- arena lock;
- waves;
- progressão;
- HUD;
- áudio;
- começo, pressão, pico e encerramento;
- gameplay do início ao fim;
- transição para a próxima etapa.

Gere `live_scene_bar_report` de MARÉ BRAVA. O slice não passa sem `status=passed`.

# FASE 7 — Expansão para o jogo completo

Depois do vertical slice aprovado, continue trabalhando. Não encerre a missão.

Leia o GDD, roteiro, scene specs, level blueprint, roster e roadmap. Crie um inventário completo:

`conteúdo previsto → estado → owner → artefatos → ROM/evidência → blocker`

Implemente todas as cenas, fases, personagens, inimigos, bosses, UI, áudio, transições e elementos narrativos que pertencem ao escopo aprovado.

Repita os mesmos gates do CAIS_01 para cada fatia.

Não declare jogo completo porque uma arena passou.

Não adicione conteúdo fora do GDD para inflar escopo. Se algo planejado não couber, apresente uma decisão explícita de recuo com impacto no design e aguarde autorização humana quando a mudança for material.

# FASE 8 — Budget real do Mega Drive

Meça sempre o pior frame.

Inclua:

- herói;
- máximo de inimigos;
- boss quando aplicável;
- HUD;
- sombras;
- hit sparks;
- poeira;
- fumaça;
- foreground;
- scroll;
- palette cycling;
- áudio;
- transição;
- objetos ambientais;
- frame de impacto;
- troca de animação;
- uploads de tiles;
- DMA;
- CRAM;
- sprites;
- pixels de sprite por scanline.

Valide simultaneamente os dois limites H40:

- máximo de 20 sprites por scanline;
- máximo de 320 pixels de sprite por scanline.

Meça o degrau seguinte de densidade antes de fechar o budget. Declare `headroom_justification` quando a cena usar menos de 60% por decisão artística ou de level design.

Nenhum laudo `estimated` promove `validado_budget`.

# FASE 9 — Evidência e fechamento

Toda mudança de runtime ou `res/` gera nova ROM e nova evidência.

Para a mesma hash, produza:

- `rom.bin`;
- SHA-256;
- screenshot dedicada;
- GIF ou sequência de movimento;
- `save.sram`;
- VLAB;
- `visual_vdp_dump.bin`;
- `runtime_metrics.json`;
- áudio real;
- freshness report;
- scene id;
- identificação da sessão.

Uma captura instantânea de “60 fps” não prova performance sustentada. Execute janela prolongada na cena pesada com áudio e densidade prometida.

Rode:

- contexto;
- metodologia;
- higiene;
- proveniência;
- pixel strict;
- recursos;
- áudio;
- tile residency;
- scanline;
- VDP budget;
- visual delivery gate;
- `live_scene_bar_report`;
- code review formal SGDK;
- scene closeout;
- freshness audit;
- ROM mastering;
- BlastEm.

Atualize:

- `doc/10-memory-bank.md`;
- `doc/changelog/changelog.md`;
- GDD/spec afetados;
- runtime decision log;
- relatórios de arte;
- `aaa_pipeline_gate_report`.

# Definição final de AAA

Só declare `ready_for_aaa=true` quando todos os itens aplicáveis passarem:

- nenhum asset crítico procedural ou placeholder;
- proveniência e licença válidas;
- autoria e clone risk aprovados;
- qualidade visual julgada contra a referência humana;
- `live_scene_bar_report.status=passed`;
- source-to-ROM match aprovado;
- model sheet-to-sprite fidelity aprovado;
- animação e movimento aprovados;
- cenário modular autoral;
- HUD e branding finais;
- gameplay completo;
- todas as fases e conteúdos do GDD concluídos;
- áudio real aprovado;
- VRAM, DMA, CRAM, scanline e CPU medidos;
- 60 fps sustentados no alvo NTSC e comportamento regional documentado;
- código formalmente revisado;
- validações sem blockers;
- BlastEm com evidência fresca;
- ROM mastering aprovado;
- memória operacional e changelog harmonizados;
- nenhuma divergência entre documentos, código, ROM e claims.

## Status intermediários permitidos

Use sempre o menor status comprovado:

- `documentado`;
- `implementado`;
- `buildado`;
- `testado_em_emulador`;
- `validado_budget`;
- `visual_pass`;
- `vertical_slice_complete`;
- `game_complete`;
- `ready_for_aaa`.

Não pule etapas.

# Persistência e autonomia

Continue trabalhando enquanto houver uma ação segura e objetiva que remova lacunas.

Não pare apenas porque:

- uma tarefa ficou grande;
- uma geração visual falhou;
- um build passou;
- uma captura parece bonita;
- um relatório foi criado;
- o contexto da sessão ficou longo.

Peça intervenção humana somente quando:

- faltar aprovação de uma mudança real de identidade;
- houver conflito de licença ou autoria;
- for necessário alterar o escopo do GDD;
- duas rotas fortes forem incompatíveis;
- uma ação destrutiva ou irreversível for necessária;
- uma limitação externa impedir objetivamente a continuidade.

A aprovação da nova TAÍNA já foi dada. Não a solicite novamente.

## Entrega final obrigatória

Ao concluir, apresente:

1. estado final do jogo;
2. matriz completa de claims;
3. hashes das ROMs finais;
4. evidências BlastEm;
5. relatórios visuais;
6. relatórios de budget;
7. relatório de áudio;
8. code review;
9. ROM mastering;
10. lista de conteúdo implementado;
11. lista vazia de blockers;
12. confirmação de alinhamento entre memory bank, changelog, GDD, specs, relatórios, Git e ROM.

Se qualquer lacuna permanecer, não use “AAA concluído”. Informe exatamente o menor status provado e continue trabalhando no próximo blocker.
