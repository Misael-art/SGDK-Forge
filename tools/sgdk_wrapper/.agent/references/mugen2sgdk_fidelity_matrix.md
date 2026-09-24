# Matriz de fidelidade MUGEN → SGDK

**Proposta.** Implementado significa código no escopo indicado, não equivalência total nem aprovação audiovisual. Fonte 12c63349d72fb8d96ecd16148fcfe9a9bde5965c. O JSON adjacente contém caminhos, cadeia e custos por conceito.

|Conceito|Estado|Mecanismo/perda|Custo e prova|
|---|---|---|---|
|DEF e resolução de pacote|implementado|Source + character.load resolvem arquivos e registram hash; escopo de pacotes aceitos limitado|offline; sem custo de leitura ZIP no console; teste sintético; não todos os pacotes|
|CNS constantes/física|aproximado|subset em MgConstants e common_forge; física 24.8|CPU por tick; RAM de jogador; harness de movimentos|
|Statedef versus rótulo State|implementado|controlador pertence ao último Statedef|offline; test_controller_belongs_to_last_statedef_not_label|
|ST, negativos e transições|aproximado|ordem e transições no mesmo tick; subset de regras do motor|CPU proporcional a controladores executados; harness vivo; cobertura total ausente|
|Expressões/triggers|aproximado|compilação para bytecode; opcodes e domínios suportados finitos|VM e pool ROM; 13865 bytes de bytecode no report; test_expr.py; domínio fora do subset gera notes|
|CMD direções/botões|implementado|B e b separados|offline; máscara de input runtime; test_cmd_case_back_vs_button; movimento B:2 chega 261|
|Buffer, carga e sequência|aproximado|buckets e listas prog/live com limites32; máximo160 comandos|RAM arrays; CPU por transição; não custo zero; 11 sequências de movimentos; fronteiras de capacidade não cobertas|
|IA por comandos|aproximado|IA ativa comandos nomeados; não emula inputs físicos|reduz reconhecedor CPU; CPU fight >20danos/>60estados/>100sons; não equivalência humana|
|AIR timing/eixos/loop|aproximado|frames, durações e loop; limite255 elementos e pivots após split|upload por mudança de frame; RAM animação; test_air_boxes_and_defaults; falta corpus flips/timing|
|Clsn1/Clsn2/push|aproximado|hit/hurt em boxes e push por largura|1526 boxes ROM; custo de pares em colisão; harness combate; não prova todo trade/corner|
|SFFv1/PCX e links|implementado|decoder v1, paleta e sprites linked; não SFFv2|offline e ROM de sheets; sem decoder PCX runtime; test_sprites_palette_and_sheets; escopo v1|
|ACT/quantização/roupas|aproximado|15cores visíveis por bloco; corpo/FX e ramps vivid_clothing|CRAM compartilhada por 4 slots de paleta; test_vivid_clothing_ramp_meets_targets_and_respects_intent|
|Anel até4 partes|aproximado|split_parts preserva regiões ocupadas; até4 objetos SGDK, não4HW|scanline/SAT e DMA reais a compor;11 imagens divididas; test_large_frame_is_split_into_valid_parts + host super|
|Fundo super/paleta/espelhamento|aproximado|BG_B, mirror_4,272tiles;16paletas; raios mudam|8704B tiles;28B cores/update + tilemap; ownership PAL0; host bg730_ticks>0; report strategy; revisão visual completa pendente|
|Helpers|aproximado|um helper por lado, states do dono, sem nested/hitdefs/atingibilidade|pool fixo; tick extra; test_super_effects_ring_parts_and_background|
|SuperPause|aproximado|pause/movetime e spawn pos via enums; animação comum indisponível aproxima|tick e explod; upload FX durante pausa; alinhamento de schema e super ativo; falta asserção específica de coordenadas|
|Pause/HitStop|aproximado|subset de pause_time e pausetime; diferentes relógios envolvidos|CPU por tick; não confundir hold intencional com atraso; compilado e combate; falta trace exato de freeze/cancel|
|HitDef/hitstates/targets|aproximado|subset dano/guarda/velocidade/target; parâmetros armazenados não garantem uso|CPU colisão e transições; harness positivo; sem oráculo MUGEN completo|
|Juggle/prioridade de HitDef|degradado|juggle e prioridade lidos/armazenados; aplicação equivalente ausente|enforcement adicional exigiria contador/arbitragem; busca de usos + README divergências; não validado|
|HitOverride/identidade avançada|ignorado|HitOverride fora do schema; não prometer regras de re-hit completas|custo futuro não medido; SCHEMA não contém HitOverride|
|ChangeAnim2/custom animation|degradado|redireciona à animação do próprio personagem|economia de lookup, altera semântica de throw; 4ocorrências approximate no report|
|46 elementos AIR com blending|degradado|flag gerada; renderer desenha opaco|equivalente S/H/dither requer budget adicional; fidelity.anims.blend_frames=46; não contagem de imagens únicas|
|Sprite ausente e frames sem sheet|degradado|fonte falta820,1; missing_frame_sprites=50 inclui rotas sem sheet|quadro invisível sem upload; não métrica de qualidade; reconciliação executada:2 source_missing +48 plane_routed =50; evidence/missing_frame_reconciliation.json|
|AfterImage/PalFX/EnvColor|ignorado|unsupported; não traduzido automaticamente para dither ou CRAM|custo futuro sprites/CRAM e conflitos; 17AfterImage e1PalFX no report Ken|
|SND→PCM XGM2|aproximado|WAV8/16bits; mono16 a13300Hz; rescomp8signed; ignora samples não usados|214142B estimados de PCM; concorrência Z80 não medida; pipeline e host contam sons; P5 dummy não prova áudio|
|PlaySnd/StopSnd canais|degradado|play/stop via SOUND_PCM_CH_AUTO; canal MUGEN não preservado integralmente|prioridade PCM/BGM e DMA a medir; fonte runtime; teste de mix/stop seletivo ausente|
|DisplayToClipboard/debug|ignorado|controlador fora SCHEMA, sem clipboard console|telemetria alternativa teria custo próprio; aceitável só com escopo debug declarado|
|HUD/lifebars|aproximado|conversor separado de lifebars; tiles e mensagens; não UI MUGEN geral|PAL0 slots9..15/Window e sprites de mensagens; teste cores/segmentos + screenshot P5 observado|
|Sombra derivada/dither|aproximado|silhueta autoral achatada32x8 e meia-tinta; não S/H|4tiles e1sprite/lutador; descarte residual deve ficar visível no gate; P5 screenshot inspecionado; memo estima overflow0,20%|
|Limites e truncamentos|degradado|geração usa slices255; bitmap -1 limitado8words; pools finitos|limite evita memória dinâmica mas perde semântica se excedido; inspeção de código; faltam fixtures de fronteira/erro|
|Prioridade de desenho|aproximado|sprpriority mapeado para profundidade de sprites; planos e HUD têm política fixa|SAT/VRAM/CRAM compartilhados; prioridade não éalpha; fonte mg_fight.c; combos deoclusão não cobertos|

## Reconciliações obrigatórias

1. **126 estados parseados/gerados não são 126 estados exercitados.** O teste CPU exige mais de 60 estados distintos, mas não emite cobertura nominal com ações, transições e efeitos; o piso do assert não é uma medição de cobertura total.
2. **702 direct não significa fidelidade integral.** É classificação do compilador no subconjunto de parâmetros. Campos fora do schema e capacidades saturadas precisam de relatório próprio.
3. **50 frames sem sheet não são 50 imagens faltantes.** BGFX vai ao plano. A fonte registra o par ausente 820,1. O pacote com hash822936f0… foi reparseado: ações100/105, elemento0, somam2 ausências; grupo730 soma48 elementos roteados ao plano. Total50 reconciliado, conforme evidence/missing_frame_reconciliation.json no pacote de curadoria.
4. **46 blend_frames são elementos AIR.** Não são necessariamente 46 imagens SFF distintas nem 46 instantes vistos em vídeo.
5. **SuperPause:** há correção de índices e teste genérico de alinhamento; test_param_list_always_aligned_with_schema usa pacote sintético sem SuperPause explícito. Harness de super verifica ativação do anel/fundo, não coordenada precisa. Falta regressão focal antes de generalizar a cura.
6. **P3 anéis:** estudo compara decomposição estática e peças reutilizadas. Não é prova de SAT reescrita no meio do frame nem multiplexação temporal. A proposta de peças 16×16 excede 20/linha segundo memo; entradas não preservadas nele tornam a medição insuficiente para benchmark reproduzível.
7. **P5:** identidade de cinco artefatos confirmada. O dump é bloco de telemetria de 200 bytes, não dump completo da VRAM/SAT. Captura com áudio dummy e 12 imagens espaçadas 0,4 s não fecha movimento/áudio.
