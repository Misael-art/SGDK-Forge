# Aprendizado incremental de engine: HAMOOPIG

Curadoria autorizada pelo usuario em 2026-09-18, com o projeto ainda incompleto.
Escopo: orientacao operacional reutilizavel; nenhuma promocao de proficiencia,
certificacao AAA, aprovacao de assets ou substituicao do runtime do projeto.
Caso de origem: `SGDK_projects/HAMOOPIG [VER.001] [SGDK 211] [GEN] [ENGINE] [FIGHTING]`.
As referencias abaixo sao relativas a esse projeto. O inventario com hashes e as
decisoes ficam em `doc/curation/2026_09_18/` nele. Nao importar seus numeros como
limites universais. Nao sobrescrever a `.agent` local para assimilar este caso.

## 1. Identidade de contato e consumo de eventos

**Owner:** `collision-system-architect`.

Overlap persistente nao e um novo ataque a cada tick. Definir identidade de
emissor, receptor, fonte e instancia do ataque; manter o gate alem da lista
temporaria de eventos do tick. Separar a identidade do resultado HIT/GUARD e
consumir dano, combo e medidor uma vez por evento aceito. Multihit exige regra
explicita de rearmamento; nao deve surgir do esvaziamento da fila.

Exigir fixtures: mesmo contato no tick e no tick seguinte, nova instancia,
corpo/projetil independentes, dois defensores, troca HIT/GUARD, reset de round,
capacidade esgotada, identificador invalido e wrap do contador. Definir politica
de overflow e ordem de consumo. Para multiplos impactos, associar delta de vida
ao evento por token, sem depender de procurar o ultimo evento do defensor.

Fonte: `doc/curation/2026_09_15/combat_event_persistent_gate.json` (L103),
`src/combat_event.c`, `tests/test_combat_event_contract.py`.
O teste compila e executa C real, mas nao cobre todas as fixtures acima. A
implementacao local usa contador `u8` e indexacao de fonte sem guarda completa;
nao copiar como biblioteca generica validada.

## 2. Alcance deve ser alcancavel pela fisica

**Owner:** `collision-system-architect`.

Medir o espacamento depois da resolucao de pushboxes, paredes, facing e camera;
nao definir alcance so pela distancia ideal entre origens. Reproduzir pelo input
normal, sem teletransportar os atores para provar um golpe. Comparar distancia
entre origens e entre bordas das caixas, escolhendo explicitamente a semantica.
Testar os dois lados, canto, troca de facing, limite exato e um pixel alem.
Corrigir geometria, ancora, janela ou alcance conforme design; ampliar alcance
nao e uma correcao universal. Revisar animacao e balanceamento separadamente.

Fonte: `doc/curation/2026_09_16/throw_range_bodyspace_alignment.json` (L119).
O valor local de 100 pixels nao e recomendacao canonica. Contador de throws
prova acionamento observado, nao qualidade do agarrão nem justica competitiva.

## 3. Upload adiado precisa de semantica de gameplay

**Owner:** `vram-streaming-dma-queue`.

Antes de desabilitar o adiamento de frames do sprite engine, medir a coincidencia
de uploads de lutadores, HUD, cenario e audio. Verificar o contrato dos flags nos
headers da versao ativa. Se o frame visual pode atrasar, definir como hitbox,
hurtbox e janela ativa permanecem coerentes: sincronizacao, reserva de budget
ou reducao autorada de custo. Fila abaixo do teto nao prova latencia aceitavel.

Testar dois atores mudando para frames grandes no mesmo VBlank, com HUD/FX/audio,
em cada modo de video suportado. Contabilizar frames adiados e atraso maximo.
Trocar DMA por escrita CPU nao elimina custo nem autoriza acesso fora da janela
segura; medir esse caminho e sua sincronizacao separadamente.

Fonte: `doc/curation/2026_09_15/ntsc_dma_backpressure.json` (L074).
Os 7008 bytes observados em NTSC pertencem a uma ROM/rota historica curta sem
combate; nao certificam o pior quadro do jogo atual.

## 4. Residencia estavel e aliases com owner explicito

**Owners:** `vram-streaming-dma-queue`, `game-state-transition-architect`.

Recriacao frequente de metasprites pode pressionar pools, realocacao e uploads.
Avaliar reaproveitamento do objeto e troca de definicao; verificar retorno de
alocacao, capacidade e custo da nova definicao nos headers, sem presumir que uma
troca nunca realoca VRAM. Alias de tiles compartilhados acompanha o indice do
owner apos movimento/compactacao e nao libera a memoria que nao possui.

Inventariar tambem sprites de debug. Reset libera ou reutiliza cada recurso uma
vez; medir pool/VRAM antes e depois de ciclos repetidos, com debug ligado e
desligado. Falha tardia no HUD pode ser vazamento de outro owner.

Fonte: `doc/curation/2026_09_15/hud_alias_and_stable_fighter_sprite.json` (L075).
Sprites persistentes sao uma estrategia a medir, nao proibicao de alocar em
transicoes nem garantia automatica contra fragmentacao.

## 5. Transicao e uma transacao de recursos

**Owner:** `game-state-transition-architect`.

Declarar ordem de bloqueio de input, fade, conclusao/invalidação de jobs,
teardown, carga da paleta destino, restauracao dos planos e liberacao de input.
Antes de misturar restauracao por DMA com escrita CPU no mesmo destino,
confirmar conclusao do DMA realmente iniciado. Esperar DMA ativo nao esvazia
automaticamente uma fila ainda nao processada. Nao usar atraso fixo como prova.

Cobrir titulo -> opcoes -> titulo -> luta -> resultado -> novo round -> titulo,
incluindo callbacks, aliases, debug, paletas, scroll e estado de input. Captura
intermediaria pode mostrar falha de captura: cruzar screenshot com estado VDP e
reproducao antes de atribuir causa ao hardware.

Fontes: `doc/curation/2026_09_15/title_dma_completion_barrier.json`,
`doc/curation/2026_09_16/title_fade_out_transaction.json`, `src/title.c`.

## 6. Telemetria com unidade, cobertura e limites

**Owner:** `emulator-vdp-evidence-curator`.

Versionar assinatura, tamanho, offsets, endian, unidade, saturacao e reset do
probe. Rejeitar schema desconhecido, dump truncado, zero amostras ou contador
saturado antes de usar numeros; exigir self-check positivo e negativo.
Distinguir video-frame de tick logico em PAL/NTSC e registrar altura efetiva.

Bytes enfileirados nao sao bytes efetivamente transferidos nem tempo de CPU.
Picos de componentes em frames diferentes nao podem ser somados como um quadro
observado. Pressao de scanline exige contagem de sprites E pixels; uma decisao
baseada apenas em DMA nao fecha budget quando outro eixo transborda. Medir
conjuntamente audio, FX, entidades, filas e pior quadro do percurso declarado.

Fonte: `tests/analyze_hprb_probe.py` (schemas 1–7). O decoder local tem envelopes
nominais e a decisao textual nao agrega todos os eixos; e objeto de aprendizado,
nao medidor canonico promovido. HSEM complementa semantica, sem julgar game feel.

## 7. Matriz solicitada nao equivale a cobertura observada

**Owner:** `emulator-vdp-evidence-curator`.

Vincular cada caso a hash da ROM, hashes dos artefatos, sequencia de input,
configuracao solicitada E configuracao observada no jogo. Um nome de arquivo
com dois lutadores nao prova que ambos foram selecionados. Separar boot/seleção,
probe curto, combate dirigido, partida completa, estabilidade prolongada e
avaliacao humana. Nao multiplicar casos curtos para declarar gameplay completo.

Detectores visuais usam ROI especifica e controle negativo: vida, especial,
mensagem e relogio nao compartilham uma unica medida de pixels. Captura de audio
nao silencioso nao prova ausencia de clipping, prioridade correta ou boa mixagem.
Evidencia historica continua util para a causa corrigida, mas recebe hash antigo;
nao e reetiquetada como evidencia de uma ROM nova.

Fontes: `tests/test_p10_evidence_integrity.py`, `doc/engine/p10_qa_matrix.json`,
L075. Os 36 casos locais nao autorizam concluir 36 partidas completas aprovadas.

## 8. Medicao de janela nao implementa streaming

**Owner:** `vram-streaming-dma-queue`.

Separar tiles unicos do mundo, resident set, pico da janela e bytes de recarga.
Metadata de modo futuro ou calculo offline nao constitui cache ativo. Exigir
runtime com slots, misses, invalidacao, fila, seams e pior deslocamento antes
de declarar streaming. Dado medido de um palco nao deve ser copiado para outro
sem nova medicao. Medir o degrau seguinte antes de fixar um teto autorado.

Fontes: `src/stage.c`, `doc/curation/2026_09_15/showdown_budget_next_degree.json`,
`doc/curation/2026_09_15/showdown_stream_window_measurement.json`.
864 tiles e janela de 588 sao dados locais, nao limites do SGDK/VDP. Paletas
compartilhadas entre planos sao possiveis; quatro paletas nao obrigam um unico
plano de fundo. Quantizacao com erro numerico baixo nao substitui julgamento
de silhueta, materiais e legibilidade em movimento.

## Reuso em outro projeto

Escolher apenas as secoes pertinentes; registrar owner, hipotese e fixture antes
de implementar. Executar regressao no projeto destino e medir sua ROM. Nao
transportar roster, assets, licencas, limites numericos ou status de maturidade.
O caso ensina a conduzir e verificar trabalho avancado; nao demonstra FMV, SVP,
rotacao raster, PCM customizado ou qualidade superior a jogos comerciais.
