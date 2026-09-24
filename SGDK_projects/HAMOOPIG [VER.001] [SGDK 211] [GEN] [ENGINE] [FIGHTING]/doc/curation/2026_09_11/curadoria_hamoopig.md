# Curadoria do HAMOOPIG em desenvolvimento

Data: 11/09/2026. Perspectiva `curator`, solicitada pelo usuário. Escopo: análise local de código, documentos, aprendizados e capturas existentes. Nenhuma implementação corrigida, nenhum asset promovido e nenhuma alteração no framework canônico.

## Parecer

**Vale continuar e preservar o HAMOOPIG como engine experimental de luta. Ainda não vale promovê-lo como base estável ou padrão canônico do Forge.** Seu valor está no combate implementado e na experiência de integrar lutadores reais; as lacunas mais urgentes são segurança de memória, simetria P1/P2, ciclo de round e confiabilidade da evidência.

O contexto oficial é `technical_demo`, teto `prototype`, não jogo AAA. GDD completo de campanha, marketing e acabamento comercial não são pré-requisitos para esta análise. Entretanto, o manifesto ainda descreve uma porta verbatim e exclui reautoria, enquanto o código já incorpora Ken, Musgo, seletor, HUD WINDOW, música e Showdown. Registrar a evolução real do escopo sem apagar a origem é necessário.

## Base observada

- ROM presente: **2.490.368 bytes**, SHA-256 `1eb99f6c33cc6fe1c7fb776f5635f31b453a6419f27ff77cd4a215db9e6b00d6`.
- A ROM copiada na sessão `out/emulator_evidence/interactive-showdown-20260911T225648Z/` tem exatamente o mesmo hash.
- Foram vistas nesta curadoria `01_idle_hud.png` e `07_hit.png`. A primeira, apesar do nome, mostra posições verticais distintas e um lutador parcialmente cortado no limite inferior; não serve como prova isolada de idle normal. A segunda mostra contato visual com spark, sem demonstrar sozinha dano, frame data ou resultado do round.
- Não executei BlastEm nem fiz rebuild. As capturas são evidência histórica inspecionada, não novo teste de runtime. FPS no título da janela não certifica pior quadro, DMA ou ausência de lag.
- Guarda de ambiente: `ready`. Adoção metodológica: arquivos existentes preservados, nenhuma alteração. Contexto em fase planning: `ok`. Higiene atual: `blocked`, pelos dois apontamentos relativos a `HAMOOPIG_icon.png` na raiz. Audit de aprendizado: 63 lições, 39 candidatos, nenhuma promoção canônica.
- O bloqueio de higiene é organizacional: não explica defeitos visuais ou de combate. Relatórios anteriores de contexto/higiene/validação não foram usados como aprovação da ROM atual.

## O que está implementado e merece continuidade

1. Núcleo de combate separado em input, FSM, física, colisão, renderização e HUD; guardas, hit pause, buffer de especiais e decisões de time-over já existem. Isso é muito mais útil que uma demonstração de sprites sem interação.
2. Tabelas de animação Ken/Musgo especificam dimensão, pivô, número de quadros e timing. É uma direção útil para tirar dados do monólito de estados.
3. Seletor distingue os dois jogadores, previews e paleta alternativa no confronto espelhado.
4. HUD em WINDOW tem owner local e evita recriar barras a cada frame quando o valor não muda. É candidato a padrão após correção de apresentação e prova de teardown.
5. Câmera H pelo ponto médio e V pelo salto, com deslocamento aplicado também a FX/sombras, oferece uma boa experiência de integração para estudos de câmera de luta.
6. Os cadernos registram limitações reais: Musgo é `source_candidate`; Showdown é `compare_flat`/placeholder; parallax não foi executado. Essa honestidade deve ser preservada.

## Achados de código priorizados

### C01 — P1: escrita além do vetor de paleta

`src/main.c:126–127` copia 18 palavras em cada subpaleta. `src/globals.c:77` e `inc/globals.h:79` definem `u16 palette[64]`. A cópia iniciada em 48 cobre índices 48–65: ultrapassa o vetor por **duas palavras, quatro bytes**. A cópia em 32 também atravessa a fronteira lógica da subpaleta. Não foi determinado qual símbolo adjacente seria afetado no binário.

Correção mínima proposta: limitar cada transferência ao comprimento real da paleta e à capacidade restante do destino; não confiar em constante 18. Aceite: teste com sentinelas ao redor do destino e boot/fade no BlastEm, sem mudança indevida de memória. Defeito estático confirmado; crash não foi observado nesta sessão.

### C02 — P1: correção de direção de especial de P2 é impossível

`src/player.c:81–89`: para P1 o código compara P1 com P2; para P2 compara `P[2].x > P[2].x` e `P[2].x < P[2].x`. Ambas são sempre falsas. A intenção de reorientar o especial de P2 não é executada nesse ramo.

Correção: comparar com o oponente, mantendo simetria. Aceite: P1 e P2 executam especial antes/depois de cruzar lados, nas duas orientações. Outras rotinas podem mascarar o sintoma; isso não torna esta condição correta.

### C03 — P1: ciclo de round ainda sem fechamento

`src/init.c:295–303`: `FUNCAO_ROUND_INIT` apenas libera movimento; `FUNCAO_ROUND_RESTART` está vazia. `src/main.c:282–285` mantém a sala pós-partida apenas com input. Há decisões de time-over em `src/fsm.c:917–935`, portanto não se deve alegar ausência de toda lógica de vitória. Falta comprovar e completar a cadeia resultado→novo round/revanche→seleção, com resets simétricos.

Aceite: KO de cada lado, empate/time-over, novo round e retorno à seleção, incluindo projétil ativo e hit pause no instante da transição. Confirmar energia, relógio, wins, posições, sprites, música e estado de input.

### C04 — P2: duas máquinas de input coexistem

`src/input.c:22–29` testa botão solto antes de testar a borda de release: o ramo `KEY_RELEASED` desse primeiro bloco é inalcançável. A partir de `:51` há outra leitura e reconstrução dos estados; ela pode fornecer release às variáveis finais. Logo, o achado não é “o jogo nunca reconhece release”, mas uma primeira representação defeituosa e duas autoridades difíceis de manter.

Correção: snapshot único por jogador e uma única derivação de free/pressed/held/released, com adaptação controlada dos consumidores. Aceite: pressionar, segurar, soltar, inputs simultâneos, troca de sala e 1P/2P; provar comandos curtos e especiais.

### C05 — P2: animação possui arbitragem assimétrica a medir

`src/graphics.c:11–23` reinicia `gASG_system` e percorre jogadores na ordem 1,2. Ao terminar uma animação de P1, liga a trava; P2 deixa de avançar naquele frame se também estava pronto. A trava tenta evitar troca simultânea de sprites, mas pode adicionar atraso dependente do adversário.

Correção proposta: primeiro medir casos simultâneos, custo DMA e efeito no frame ativo. Não remover a proteção cegamente. Separar tempo lógico do combate e disponibilidade visual, ou reservar upload suficiente. Aceite: ações simultâneas conservam frame data e simetria sob carga máxima.

### C06 — P2: churn e falha de alocação exigem instrumentação

`src/player.c:12` libera o sprite na mudança de estado; `src/player_musgo.c:39–44` e equivalente Ken alocam outro. O loop de idle também retorna a `PLAYER_STATE`. Nas rotinas novas examinadas, não há contador exportado de falha. `Safe` no nome da API não é evidência de que a alocação ocorreu.

Aceite: contadores de falha e mapa de residência; duas animações grandes, spark, projétil e HUD juntos; medição de ambos os limites por scanline. Só então decidir entre manter alocação, reservar slots ou usar streaming. Não afirmar overflow sem medir.

### C07 — P2: temporização e aliases precisam de contrato

`src/hud.c:28` recarrega relógio com 38 ticks. Pode ser escolha arcade, mas não deve ser descrito como segundo real sem contrato. `inc/player_musgo_table.h:143–157` mapeia muitas ações para animações genéricas, inclusive agarrões para 102 e aéreos para 300. Isso permite prototipar, mas não comprova identidade de grappler ou leitura de todas as ações.

Aceite: declarar duração do round por região e tabela de ações completas/provisórias; acertar startup, active, recovery, hurtbox e contato no strip real, com testes de ambos os lados.

## Arte: resultado observado e próxima melhoria

Nas capturas, o park tem blocos grandes e pouca separação de materiais; Musgo preserva massa e silhueta geral, mas possui ruído fino, bordas magenta e leitura interna instável. O HUD contém elementos repetidos/cortados abaixo das barras. A faixa de chão é visualmente ambígua, coerente com a limitação já registrada no caderno. São observações de screenshots, não diagnóstico fechado da origem de cada pixel.

A ação útil é um passe nativo em escala final sobre Musgo e sobre um chão autoral legível, mantendo o tamanho aprovado e verificando contato. Aumentar resolução ou adicionar parallax antes disso não resolve a leitura. `compare_flat` continua válido para protótipo; a perda de detalhe não deve virar padrão de tradução final.

A aprovação de procedência de um arquivo não equivale a licença para todo uso. Preservar créditos originais e a separação de código, samples, personagens e cenários de estudo. Não converter o rótulo GPL de um componente em autorização genérica para todo o pacote. Esta curadoria não emite parecer jurídico nem promove assets de terceiros.

## Curadoria dos aprendizados: adotar, ajustar ou reter

| Aprendizado | Decisão | Condição para virar referência do Forge |
|---|---|---|
| Onboarding inclui estado, tabela, hitbox, paleta, SFX, seletor e gravidade | Candidato forte | Checklist por capacidade do personagem; nem todo lutador precisa de projétil ou especial idêntico |
| Não confundir metadados de parallax com efeito executado | Preservar | Fonte, implementação e evidência separadas |
| Captura parcial não é ROM inexistente | Preservar | Manter identidade da ROM e teto da prova; não fabricar VLAB nem selo |
| Medir tiles antes de escolher representação | Preservar | Medir dedup, custo residente, DMA e cena completa, não só arquivo |
| Quatro paletas ocupadas impedem parallax | Corrigir antes de promover | Planos podem compartilhar paleta; necessidade de nova paleta é artística, não obrigatoriedade de um plano extra |
| Uma paleta implica um plano | Rejeitar como regra de hardware | CRAM e planos são recursos distintos; verificar BG_A livre, WINDOW, prioridade e orçamento |
| Passar de 256 px exige sempre plano 64x64 | Restringir ao mapa residente atual | Um mundo maior pode usar atualização/streaming da janela do tilemap; isso tem custo e precisa de projeto próprio |
| `camPosY=air/2`, bloqueio 4px e dimensões fixas | Manter como decisão deste estudo | Generalizar contratos/fórmulas de transformação, não números específicos do park |
| Quantização de concept não prova pixel nativo final | Preservar, sem duplicar regra | Já existe no framework; usar este caso como evidência negativa |
| Caso 550 sempre copia gravidade do Ryo | Restringir | Exigir entrada de estado que inicialize física; parâmetros pertencem ao lutador |
| Mitigação de migração de headers de recurso | Candidato forte | Fixture em que sprite.h/sound.h são saídas ResComp; impedir autofix destrutivo |

Nenhum desses itens foi aplicado ao canônico nesta análise. Há 39 candidatos no ledger: quantidade não substitui revisão causal. Priorizar os que evitam erros reproduzidos; não criar skills novas para regras já cobertas.

## Documentação e evidência

A memória contém cabeçalho “ROM inexistente” e, abaixo, hash de ROM existente. A declaração de 22 arquivos byte-idempotentes não descreve o código expandido. A spec ainda cita HUD antigo e cenas anteriores; o plano QA mantém áudio ausente apesar da integração descrita posteriormente. O GDD é template, mas não é blocker por si só para o contexto demo. Atualizar brief/spec/QA proporcionais é suficiente nesta fase.

O bundle canônico continua pendente. A sessão Showdown tem ROM e capturas; a inspeção dessa pasta não encontrou SRAM/VDP dump. Isso sustenta a existência visual histórica, não budget validado ou performance certificada. Uma engine sem instrumentação não deve receber um dump inventado: planejar instrumentação e captura conforme o contrato aplicável.

## Plano de avanço

1. **Correções de integridade:** C01 e C02 com regressões pequenas; congelar a ROM atual antes de mudar. Depois build central e nova evidência.
2. **Contrato de demo atualizado:** porta estendida, três lutadores, um palco, roster provisório e ciclo mínimo. Corrigir estado derivado e higiene do ícone sem renomear o projeto.
3. **Round completo:** KO/time-over/restart/revanche/seleção; inicialmente com um par de lutadores. Arte de estudo pode continuar com teto prototype.
4. **Combate reproduzível:** testes espelhados P1/P2, input, startup/active/recovery, agarre, guardas, cruzamento e ações simultâneas. Investigar C04/C05 antes de expandir roster.
5. **Hardware e áudio combinados:** residência, DMA, falhas de sprite, scanline e carga máxima com música/SFX; medir cenário mais pesado e próximo degrau.
6. **Passe visual nativo:** Musgo, chão e HUD; então arquitetura de profundidade/parallax segundo necessidade visual e budget.
7. **Extração de referência:** somente padrões já corrigidos e demonstrados, com fixture mínima, provenance, hash e revisão humana. Manter dependências do jogo fora da biblioteca reutilizável.

**Próximo marco recomendado:** uma luta completa e repetível entre dois lutadores, com direção correta, memória íntegra e retorno seguro ao seletor. Esse marco agrega mais valor de engine do que um quarto personagem ou outro cenário.

## Limites do parecer

Revisão local, sem conselho independente nesta rodada; não é aprovação final do código completo. Findings estáticos não substituem reprodução de sintomas. Não houve build, novo teste de emulador, medição de hardware ou captura de áudio. `review_blocked` refere-se à promoção de base estável, não à continuidade do protótipo.
