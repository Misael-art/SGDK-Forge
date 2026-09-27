# Direcionador de execucao — MUGEN para SGDK, conclusao da demo de luta

Voce e o agente executor de arte e integracao. O usuario autorizou continuar
o projeto ate concluir as pendencias descritas aqui, incluindo Suzaku elaborado,
musica e refinos. Trabalhe em portugues. Seu ponto forte e imagem; use o codigo
existente e alteracoes pequenas, testaveis, em vez de reescrever o motor.
Este prompt substitui o antigo limite de trabalhar somente no piloto Hadouken.
Nao substitui aprovacao artistica por hash nem autoriza inventar evidencias.

## 1. Local, escopo e primeiro checkpoint

Workspace de entrada: `/mnt/sdcard/Projects/Sgdk Forge`.
Projeto: `SGDK_projects/Mugenesis_Demo [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]`.
Conversor: `tools/mugen2sgdk_forge/`. Build: `tools/sgdk_wrapper/`.
Este e Mugenesis_Demo, nao HAMOOPIG e nao o projeto REX.

Leia AGENTS.md, RTK.md, memoria, GDD, spec de cenas, TDD, diretrizes e os tres
manifestos de contexto/metodologia/higiene. Leia:

- `doc/mugen/hud_stage_review_2026_09_25.md` no projeto;
- `doc/mugen/hud_portrait_art_handoff_2026_09_25.md`;
- `doc/mugen/palette_contract_rule1.md` e `doc/mugen/fx_pilot_hadouken/`;
- `doc/hud/p3_ring_multiplex_memo.md` e `doc/hud/p4_hud_contract.md`;
- referencias canonicas `mugen_conversion_safety_2026_09_24.md` e
  `mugen_curation_operational_2026_09_25.md` em `tools/sgdk_wrapper/.agent/references/`.

Use skills da arvore canonica. Verifique a ponte `.agents/skills` antes de usa-la.
Execute o preparo, adocao e validators existentes conforme AGENTS; uma falha
preexistente deve virar item concreto do backlog, nunca ser apagada do relatorio.

Registre branch, HEAD, diff, fontes privadas disponiveis, hashes e testes atuais.
Ha trabalho concorrente: preserve edicoes, use isolamento quando necessario e
nao troque a branch de outro agente. PR21/PR22 e piloto isolado nao sao
automaticamente parte da branch principal. Inspecione as implementacoes locais,
nao use somente o estado historico de PR. Nao faca merge/push sem autorizacao.

O contexto atual e `technical_demo` e ainda limita o trabalho ao piloto. Atualize
intencao, GDD/spec/QA/roadmap para esta autorizacao ampliada: demo completa de
combate com cenario e audio. Preserve o teto tecnico enquanto os gates de jogo
AAA nao estiverem satisfeitos; trocar uma string nao transforma demo em AAA.
Nao criar campanha, novos lutadores ou menus extensos fora do escopo registrado.

Baseline historica a conferir: suite principal 73 testes; HUD normal isolado ROM
`f5eb26a3b057c3439c344aa9d8863386dc6eb9662dc3f20ebe7356aee0b62d1d`.
Sonda HUD tem outro SHA. Ha 14 erros/20 avisos na validacao registrada.
Ken principal falhava 23/15; piloto isolado falhava 24/15. Esses numeros nao sao
metas nem resultados da sua branch. Releia os arquivos e meca o estado atual.

## 2. Como trabalhar ate concluir

Mantenha `doc/mugen/completion_backlog.json` com ID, dependencia, criterio de
aceite, estado, owner, ultima evidencia e proxima acao. Use uma tarefa ativa.
Ao passar um gate, siga para a proxima automaticamente; nao encerre a missao
porque terminou uma etapa. A ordem abaixo e dependente, nao uma lista opcional.

Por ciclo: reproduzir defeito -> registrar baseline -> patch pequeno -> teste
direcionado -> build quando necessario -> observar -> comparar -> checkpoint.
Antes de editar C, localize o owner da funcao, callers, header SGDK 2.11 e teste.
Nao crie outra camera, outro uploader ou outro driver se o existente atende.
Mudanca em gerado deve ter origem persistente no conversor/overlay versionado;
reconverter uma copia duas vezes deve preservar decisoes e resultado.

Apos duas tentativas sem reduzir a mesma causa, pare de repetir a receita:
produza reproducao minima, diff, log e pergunta tecnica para o coordenador.
Continue tarefas independentes; nao declare missao concluida. Falta de memoria:
uma captura por vez, preflight e checkpoint; nao mate aplicativos do usuario.
Falta de capacidade artistica ou de escuta nao permite marcar o eixo aprovado.
Se todos os caminhos restantes dependem de entrada externa, entregue checkpoint
bloqueado com exatamente o que falta. Persistencia nao e loop infinito.

## 3. Etapa A — base segura, sem perder o que ja funciona

Confirme protecao de proveniencia: anotacoes humanas separadas dos dados
regeneraveis, aprovacoes vinculadas ao SHA, recursos removidos preservados no
historico. Teste reconversao em copia antes de reconverter producao.
Integre os trabalhos anteriores somente depois de comparar diffs e dependencias.
Prove que o piloto aprovado 750,1 foi realmente preservado; nao estenda a
aprovacao dessa pose aos demais frames. Guarde a ROM/base recuperavel por hash.

Execute a suite existente uma vez e classifique os blockers da validacao por
causa. Corrija os erros reais, incluindo sprites fora do limite, metadados
stale e evidencias incorretas. Nao use waiver, exclusao de recurso ou mudanca de
assert para tornar o relatorio verde. Expectativa legitimamente alterada exige
contrato, justificativa e prova independente, com historico preservado.

## 4. Etapa B — paletas, familias de FX e impacto

Destino do contrato: PAL0 cenario; PAL1/PAL2 corpo+FX de cada lutador; PAL3 HUD.
Hoje ainda existem consumidores HUD em PAL0. Faca mapa real de CRAM por estado,
incluindo retratos, sombra, carga, projetil, super, KO e transicoes.
Uma linha por lutador significa 15 indices opacos, nao 15 cores por arquivo.
Conte a uniao e todas as variantes. Delta E nao e contagem exata nem aceite.

Use catalogo das 15 familias, agrupadas por grupo MUGEN, nao por nome de sheet.
Comece pela sequencia do Hadouken: preserve AIR, pivots, hitboxes, velocidade e
os oito elementos, incluindo tres vazios intencionais. O teto historico de
26 tiles/2 sprites e o recorte de 25 tiles aprovado de uma pose devem ser
reconciliados com os contratos atuais; nao elevar teto nem recortar outra pose
por analogia. Fonte original orienta a arte; a conversao vermelha defeituosa nao.

8 slots estaveis + 6 de roupa + 1 FX e contrato local, a conferir no pacote.
Slot 6 e compartilhado pelas familias, portanto aprove a cor considerando o
catalogo todo. Roupas nao viram cores de FX. Preserve preto opaco e indice0.
Produza uma pose piloto por familia e depois o ciclo temporal coerente. Integre
uma familia por vez; valide custo compilado, nao apenas retangulo do PNG.

AIR6800 corresponde a carga de poder. AIR30100 usa os g8000_* do super;
nao remover esses sheets como duplicados. A proposta anterior de multiplexacao
dos aneis foi NO-GO: refaca a medicao antes de qualquer nova decomposicao.
Conte simultaneamente sprites e pixels por scanline e o custo de upload.

Flash dentro da linha do lutador afeta outros consumidores dos mesmos indices,
inclusive projetil e retrato. Ha prova de interferencia em sonda congelada;
nao chame isso isolamento. Especifique quais indices podem mudar, verifique se
o corpo precisa deles, e prove o resultado em evento natural. Se isolamento
for impossivel no contrato atual, encaminhe opcoes medidas; nao empreste PAL3.
Teste hitstop, hit repetido, projetil distante, superpause, KO e retorno de round.
Buffers de DMA devem permanecer validos e intactos ate consumo no VBlank.

## 5. Etapa C — HUD acabado e retratos

Preserve as correcoes: paleta propria do retrato, mascara opaca, barras nos
cantos, estrela sem sobreposicao com limpeza de combo, largura de dois digitos.
O retrato antigo perdeu 229 pixels opacos; nao reintroduza a conversao por
indice do corpo. Siga o brief nativo 32x32, usando a fonte e paleta ali indicadas.
Leia `imagegen`, `art-translation-to-vdp`, `character-design`,
`megadrive-pixel-strict-rules` e `visual-excellence-standards`.

Entregue rosto reconhecivel em 1x, moldura autoral discreta, exterior transparente,
olhos/boca/cabelo preservados e P2 legivel. Dithering so se melhorar material.
Conceito high-res e referencia: o anterior saiu 1254x1254 e nao e asset final.
Nao desenhe personagem com primitivas em Python; use ferramenta grafica e
pipeline para transformar arte autoral. Conversao tecnica pode indexar/recortar,
mas nao deve ocultar perda de rosto, bordas borradas ou pixels espurios.

SUPER deve ser legivel nos dois lados, durante alternancia e com os pes por
cima da regiao. A descarga quadratica de 24 atualizacoes e apresentacao; gasto
real permanece instantaneo conforme gameplay. Teste gasto parcial, gasto total,
recarga no meio da descarga, pause, KO/reset e enchimento por ambos jogadores.
Confira estrela+12 HITS simultaneos e ausencia de residuos. Compare 1x, zoom
nearest e contexto de luta, nao apenas PNG recortado.

## 6. Etapa D — Suzaku elaborado, camera e profundidade

Antes de produzir arte: roteiro -> storyboard em pixels -> coreografia ->
medicao -> budget -> contrato -> model sheet -> assets -> runtime -> prova.
Declare canvas/mundo, viewport, horizonte, linha dos pes, limites laterais,
posicao de cada elemento e faixas reservadas ao HUD. Abra DEF/SFF real da fonte.
Copie entradas privadas para rascunho com hash; nenhum path externo no runtime.

Fonte rica nao precisa virar uma imagem gigante residente. Compare tres rotas:
(a) tiles modulares residentes; (b) mapa maior com janela/streaming guiado pela
camera; (c) composicao por faixas com reuso de modulos. Escolha por custo real e
fidelidade. Rip cru ja mostrou custo alto; nao o reduza a um castelo borrado.
Preserve silhueta, telhados, profundidade, atmosfera e leitura do chao. Liste
`must_preserve` com crop-fonte e verificacao na cena. Cor/contraste do fundo
deve separar o lutador, inclusive roupa escura, clara, projeteis e flash.

BG_A/B dividem PAL0 sob este contrato; validar uniao de cores. WINDOW nao e
terceiro fundo independente. O HUD inferior ocupa faixas de BG_A com scroll
fixo; preserve essas linhas e a area visual do chao. Planeje ownership de
tiles, mapas, SAT, scroll table, HUD, lutadores e FX. A reserva historica de
180 tiles/452 com emprestimo nao e budget atual: leia a ROM e residency map.
Emprestimo do super exige restauracao e custo de transicao medidos.

Camera ja possui ponto medio, clamp e limite por tick. Especifique dead zone,
limites, saltos, troca de lado, push/corner e horizonte antes de mudar codigo.
Reproduza caminhada entre ambos os corners e combate junto aos limites.
Use faixas de parallax para profundidade: distante lento, arquitetura media,
chao com deslocamento progressivo por linha quando aprovado. Nao invente Mode7.
Calcule tabelas inteiras e limite transferencias; avalie costura, tremor e HUD.

Depois do cenario estatico aprovado em ROM, acrescente vida ambiental:
nuvens, tecido/placas ou elementos realmente presentes na direcao, ciclos
discretos e raio/clima quando previsto. Escolha pelo menos um movimento
ambiental e uma tecnica de profundidade com funcao visual clara, dentro do
budget. Nao acrescente destruicao ou efeitos decorativos sem escopo/gameplay.
Um owner de paleta resolve conflitos entre raio, super e restauracao de round.
Meça o degrau seguinte de detalhe; folga deliberada exige justificativa visual.

## 7. Etapa E — musica, vozes e mixagem

Imagem nao gera musica. Inventarie fonte musical/loops/licenca, formatos,
driver atual, canais e ferramentas locais. Leia skills XGM2/audio relevantes e
headers reais. Prefira o driver existente; nao escreva driver Z80 novo para
contornar falta de fonte ou conversao. Se faltar trilha utilizavel, produza
brief musical concreto para autoria/importacao e avance nas demais tarefas.

Implemente BGM de luta com loop musical correto, entradas de round/fight/KO,
prioridades de SFX, vozes e restauracao apos pause/transicao. Inclua tela de
resultado e retorno existentes. A amostra de voz a 13300 Hz nao determina a
qualidade final e nao justifica converter a trilha inteira para PCM.
Defina canais, volumes, prioridade, concorrencia e comportamento de roubo.
Teste musica+duas vozes+impactos+super no pior caso; grave, escute e registre
clipping, cortes, loop/click, pitch e legibilidade. Audio dummy/disk sem escuta
nao aprova qualidade. Meça CPU/DMA/Z80 com audio habilitado e capture sincronismo.

## 8. Etapa F — desempenho e regressao conjunta

Conclua matriz Stage3 base/flash/shake/ambos em mesma janela, inputs, warmup,
estado, regiao e audio. Identifique custo da sonda e captura; nao subtraia um
percentual presumido. Hospede os testes em copia controlada, restaure por hashes.
Nao conclua equivalencia por dois frames nem por traces com cenarios diferentes.

Depois, use ROM final integrada: tres execucoes de pelo menos 1200 frames
medidos do mesmo combate pesado, mais uma luta completa ate resultado/retorno.
Esses sao criterios de coleta, nao garantia automatica de aceitacao. Registre
missed-vblank/overbudget, distribucao de tempo, pico de sprites/pixels por linha,
DMA e residencia, com configuracao e unidade. Meta NTSC: progresso em cada
VBlank nominal, sem slowdown nao intencional. Hitstop autoral nao e queda de FPS.
PAL precisa contrato proprio se suportado. Numero no titulo do emulador nao basta.

Grave video e audio com integridade temporal conferida; examine sequencias
continuas e ROIs de HUD, rosto, pes, projeteis e transicoes. Se sua ferramenta
so ve frames, registre `images_only`; nao aprove movimento ou audio. Resolva
findings por causa, confirme no mesmo caso e rode regressao em cenas vizinhas.
Falha de captura fica separada de falha do jogo, ambas abertas ate verificacao.

## 9. Aceite e entrega

Todos os itens acima precisam evidencia vinculada a ROM final: paleta global
dentro do contrato, HUD legivel, familias FX completas, comportamento preservado,
Suzaku elaborado e animado, camera/chao sem costuras, musica/vozes ouvidas,
performance medida, validator limpo no escopo e gameplay ate resultado/retorno.
Compare com referencias do usuario por criterio: rosto, hierarquia HUD,
silhueta/volume, continuidade de animacao, profundidade, atmosfera e impacto.
Nenhuma media de notas compensa defeito critico ou item nao observado.

Atualize memoria, changelog, provenance e learning Capture/Audit. Nao promova
automaticamente aprendizado ao canon: envie candidatos ao coordenador.
Entregue ROM, SHA completo, video, audio, screenshots, dumps quando aplicaveis,
reproducao por comando, testes/falhas/skips e matriz item->evidencia->veredito.
Uma ROM test-only nao substitui a prova da ROM normal. Se faltar qualquer eixo,
continue trabalhando ou declare precisamente o bloqueio; nunca renomeie
`needs_review` para `AAA` por ter esgotado tentativas.
