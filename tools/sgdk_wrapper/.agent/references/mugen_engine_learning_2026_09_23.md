# Aprendizado MUGEN → Mega Drive — 2026-09-23

Status: **proposta de referência**, sem alteração das skills ou promoção de competência. Fonte auditada `12c63349d72fb8d96ecd16148fcfe9a9bde5965c`. Consulte a matriz de fidelidade adjacente e o pacote `doc/curation/2026_09_23/`.

Semântica original foi confrontada com [CNS da Elecbyte](https://www.elecbyte.com/mugendocs/cns.html), [controladores](https://www.elecbyte.com/mugendocs/sctrls.html) e [AIR](https://www.elecbyte.com/mugendocs-11b1/air.html). Versões da documentação não ampliam o escopo implementado do conversor. Abaixo, as conclusões de implementação são do código local, não alegações da documentação externa.

## 1. Pacote é contrato, não sheet

**Origem:** DEF liga constantes, estados, comandos, AIR, sprites, sons e paletas; um port visualmente parecido pode perder o comportamento.

**Preservado no MD:** Preservar hashes, resolução de arquivos e relações em IR; SFFv1/PCX é o escopo atual, não SFF universal.

**Limite e aceite proposto:** Versionar perfil aceito, recusar versão não suportada e nomes ambíguos em vez de escolher silenciosamente.

Fonte: [tools/mugen2sgdk_forge/mugen2sgdk_forge/source.py](https://github.com/Misael-art/SGDK-Forge/blob/12c63349d72fb8d96ecd16148fcfe9a9bde5965c/tools/mugen2sgdk_forge/mugen2sgdk_forge/source.py).

## 2. Ownership dos controladores

**Origem:** O bloco Statedef corrente determina o estado; o número no rótulo State não é chave confiável.

**Preservado no MD:** Parser já usa current; teste test_controller_belongs_to_last_statedef_not_label reproduz o erro clássico.

**Limite e aceite proposto:** Definir política de estados duplicados e fallback common_forge; o substituto comum não prova equivalência com todo common1.cns.

Fonte: [tools/mugen2sgdk_forge/mugen2sgdk_forge/parsers/cns.py](https://github.com/Misael-art/SGDK-Forge/blob/12c63349d72fb8d96ecd16148fcfe9a9bde5965c/tools/mugen2sgdk_forge/mugen2sgdk_forge/parsers/cns.py).

## 3. Tick e ordem fazem parte do golpe

**Origem:** Estados negativos, transições e regras do motor determinam quais ações ocorrem no mesmo tick.

**Preservado no MD:** mg_char.c interpreta estados e common_forge fornece regras básicas; preservar ordem nas otimizações.

**Limite e aceite proposto:** Usar traços de estado/tempo/input/dano, seeds e limites; uma luta CPU viva não prova todos os caminhos.

Fonte: [tools/mugen2sgdk_forge/runtime/mg_char.c](https://github.com/Misael-art/SGDK-Forge/blob/12c63349d72fb8d96ecd16148fcfe9a9bde5965c/tools/mugen2sgdk_forge/runtime/mg_char.c).

## 4. Comando não é botão

**Origem:** CMD distingue direção B de botão b; sequência, carga, simultaneidade e buffer têm significado.

**Preservado no MD:** Parser mantém distinção e runtime usa buckets, listas de progresso e bitmaps.

**Limite e aceite proposto:** Distinguir reconhecimento humano de IA que ativa comandos; medir facing, release, estrito, hitstop, 3/6 botões e lotação de pools.

Fonte: [tools/mugen2sgdk_forge/mugen2sgdk_forge/parsers/cmd.py](https://github.com/Misael-art/SGDK-Forge/blob/12c63349d72fb8d96ecd16148fcfe9a9bde5965c/tools/mugen2sgdk_forge/mugen2sgdk_forge/parsers/cmd.py).

## 5. AIR inclui colisão e tempo

**Origem:** Eixo, duração, loop, flips e Clsn1/Clsn2 participam do comportamento; quadros negativos podem ter funções distintas.

**Preservado no MD:** Dados de boxes e frames são gerados; o runtime resolve hit/hurt e animação.

**Limite e aceite proposto:** Preservar pivot após crop/split/flip e denunciar truncamento em 255 elementos. Pushbox não se deduz da silhueta nem da hurtbox.

Fonte: [tools/mugen2sgdk_forge/mugen2sgdk_forge/parsers/air.py](https://github.com/Misael-art/SGDK-Forge/blob/12c63349d72fb8d96ecd16148fcfe9a9bde5965c/tools/mugen2sgdk_forge/mugen2sgdk_forge/parsers/air.py).

## 6. Acerto não se resume a subtrair vida

**Origem:** HitDef, estado de dano, juggle, prioridade, identidade e alvos condicionam combos e interrupções.

**Preservado no MD:** Existe subset de HitDef, defesa, target e pausetime.

**Limite e aceite proposto:** Juggle apenas armazenado e prioridade sem arbitragem equivalente são perdas de regra, não polimento. Testar trade, throw, multi-hit, HitOverride e custom states com oráculos.

Fonte: [tools/mugen2sgdk_forge/runtime/mg_fight.c](https://github.com/Misael-art/SGDK-Forge/blob/12c63349d72fb8d96ecd16148fcfe9a9bde5965c/tools/mugen2sgdk_forge/runtime/mg_fight.c).

## 7. Helper é entidade semântica

**Origem:** Helpers podem executar estados próprios; equivalência depende de seu ciclo de vida e interações.

**Preservado no MD:** Implementação reduzida usa um slot por lado, estados do dono, sem helper aninhado; sustenta o fundo do super.

**Limite e aceite proposto:** Não anunciar helpers completos: HitDef é descartado em helper e atingibilidade não é modelada. Falha de capacidade deve ser explícita.

Fonte: [tools/mugen2sgdk_forge/runtime/mg_char.c](https://github.com/Misael-art/SGDK-Forge/blob/12c63349d72fb8d96ecd16148fcfe9a9bde5965c/tools/mugen2sgdk_forge/runtime/mg_char.c).

## 8. SuperPause precisa de contrato de parâmetros

**Origem:** Tempo, movetime, som, animação e posição são parâmetros independentes do controlador.

**Preservado no MD:** Runtime usa MG_P_SUPERPAUSE_POS_X/Y; índices gerados são o contrato IR/C.

**Limite e aceite proposto:** Teste de alinhamento de schema existe, mas a fixture sintética não menciona SuperPause; adicionar caso com pos não zero e facing invertido, verificando posição/timing exatos. O harness atual prova ativação, não esse detalhe.

Fonte: [tools/mugen2sgdk_forge/tests/test_pipeline.py](https://github.com/Misael-art/SGDK-Forge/blob/12c63349d72fb8d96ecd16148fcfe9a9bde5965c/tools/mugen2sgdk_forge/tests/test_pipeline.py).

## 9. Parte SGDK não é sprite de hardware

**Origem:** Quadros grandes podem ocupar regiões esparsas.

**Preservado no MD:** split_parts recorta por área ocupada, até quatro partes; rescomp ainda decompõe cada parte em sprites de hardware.

**Limite e aceite proposto:** Auditar SAT por linha e pixels por linha na composição real: H40 20/320 e H32 16/256. Medir DMA do par de lutadores mais FX/HUD; zeros na imagem não autorizam subestimar células emitidas.

Fonte: [tools/mugen2sgdk_forge/mugen2sgdk_forge/converters/sprites.py](https://github.com/Misael-art/SGDK-Forge/blob/12c63349d72fb8d96ecd16148fcfe9a9bde5965c/tools/mugen2sgdk_forge/mugen2sgdk_forge/converters/sprites.py).

## 10. Troca de paleta é transformação condicionada

**Origem:** Sequências com geometria idêntica podem diferir só na associação de cores.

**Preservado no MD:** bgfx.detect verifica remapeamento, usa BG_B 320×224 e 14 slots PAL0. Ken: mirror_4, 272 tiles, 16 imagens, 28 bytes de cores por atualização útil.

**Limite e aceite proposto:** Espelhamento altera raios: zero mean_level_error não prova fidelidade, pois esse campo mede a redução, não toda a transformação geométrica. Contrato deve separar crop, mirror e quantização.

Fonte: [tools/mugen2sgdk_forge/mugen2sgdk_forge/converters/bgfx.py](https://github.com/Misael-art/SGDK-Forge/blob/12c63349d72fb8d96ecd16148fcfe9a9bde5965c/tools/mugen2sgdk_forge/mugen2sgdk_forge/converters/bgfx.py).

## 11. Blending é classe de perda

**Origem:** AIR pode solicitar efeitos de mistura; opacidade comum não reproduz esses efeitos.

**Preservado no MD:** Flag de blend chega ao C; não foi encontrada composição equivalente no renderer. Report aponta 46 elementos.

**Limite e aceite proposto:** Registrar cada ação/elemento e sobreposição. S/H, dither, premix ou reautoria exigem decisão por cena e orçamento; não prometer alpha nativo.

Fonte: [tools/mugen2sgdk_forge/mugen2sgdk_forge/generators/sgdk.py](https://github.com/Misael-art/SGDK-Forge/blob/12c63349d72fb8d96ecd16148fcfe9a9bde5965c/tools/mugen2sgdk_forge/mugen2sgdk_forge/generators/sgdk.py).

## 12. Ausência precisa de causa

**Origem:** Referências AIR podem não ter imagem no pacote original.

**Preservado no MD:** Report distingue missing_sprites da fonte e frames sem sheet no gerador; bgfx renderizado em plano também não tem sheet.

**Limite e aceite proposto:** Não transformar missing_frame_sprites=50 em 50 bugs: reconciliar source_missing, plane_routed, intentionally_blank e unsupported. Reconciliação executada: duas ocorrências da imagem820,1 (ações100/105, elemento0) e48 elementos do grupo730 roteados ao plano somam50; preservar esse inventário.

Fonte: [tools/mugen2sgdk_forge/mugen2sgdk_forge/generators/sgdk.py](https://github.com/Misael-art/SGDK-Forge/blob/12c63349d72fb8d96ecd16148fcfe9a9bde5965c/tools/mugen2sgdk_forge/mugen2sgdk_forge/generators/sgdk.py).

## 13. Paleta é recurso com dono e duração

**Origem:** ACT e efeitos locais chegam com intenções cromáticas distintas.

**Preservado no MD:** Conversor separa corpo/FX e calibra roupa; HUD e super compartilham PAL0 em momentos distintos.

**Limite e aceite proposto:** Criar mapa temporal de slots e restauração no fim/interrupção/KO/revanche; validar com dois personagens diferentes. Saturação isolada não prova leitura.

Fonte: [tools/mugen2sgdk_forge/mugen2sgdk_forge/converters/sprites.py](https://github.com/Misael-art/SGDK-Forge/blob/12c63349d72fb8d96ecd16148fcfe9a9bde5965c/tools/mugen2sgdk_forge/mugen2sgdk_forge/converters/sprites.py).

## 14. SND convertido não é áudio aprovado

**Origem:** PlaySnd e StopSnd incluem semântica de reprodução que precisa de mapeamento.

**Preservado no MD:** sounds.py faz mono/reamostragem linear para WAV; rescomp gera PCM XGM2; runtime chama playPCM AUTO.

**Limite e aceite proposto:** Mapear canais, prioridades e interrupções, medir aliasing/clipping/mix e ouvir voz+BGM+FX. StopPCM AUTO exige teste contra o contrato real do driver, sem assumir equivalência ao canal MUGEN.

Fonte: [tools/mugen2sgdk_forge/mugen2sgdk_forge/converters/sounds.py](https://github.com/Misael-art/SGDK-Forge/blob/12c63349d72fb8d96ecd16148fcfe9a9bde5965c/tools/mugen2sgdk_forge/mugen2sgdk_forge/converters/sounds.py).

## 15. Host verifica lógica; console verifica custo

**Origem:** Conversor e harness permitem detectar regressões sem build de ROM a cada hipótese.

**Preservado no MD:** 39 testes passaram; harness compila runtime real com stubs e Ken local.

**Limite e aceite proposto:** Host não prova DMA, Z80, VDP, VRAM nem temporização real. Limitar claims de equivalência ao corpus de traços comparados; getSubTick tem 76.800 unidades/s, 1.280 a 60 Hz nominal.

Fonte: [tools/mugen2sgdk_forge/tests/test_host_runtime.py](https://github.com/Misael-art/SGDK-Forge/blob/12c63349d72fb8d96ecd16148fcfe9a9bde5965c/tools/mugen2sgdk_forge/tests/test_host_runtime.py).

## 16. Evidência tem escopo e identidade

**Origem:** Preservar intenção requer comparar fonte, tradução e execução no mesmo caso.

**Preservado no MD:** P5 tem cinco hashes válidos e captura legível de HUD, corpos e sombras.

**Limite e aceite proposto:** P5 usa áudio dummy e burst a 0,4 s: não aprova movimento/áudio. Manter integridade temporal, cadência, qualidade e cobertura como eixos separados; nenhum selo global nasce da imagem.

Fonte: [SGDK_projects/Mugenesis_Demo [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]/doc/hud/p5_shadow_memo.md](https://github.com/Misael-art/SGDK-Forge/blob/12c63349d72fb8d96ecd16148fcfe9a9bde5965c/SGDK_projects/Mugenesis_Demo%20%5BVER.001%5D%20%5BSGDK%20211%5D%20%5BGEN%5D%20%5BGAME%5D%20%5BFIGHTING%5D/doc/hud/p5_shadow_memo.md).
