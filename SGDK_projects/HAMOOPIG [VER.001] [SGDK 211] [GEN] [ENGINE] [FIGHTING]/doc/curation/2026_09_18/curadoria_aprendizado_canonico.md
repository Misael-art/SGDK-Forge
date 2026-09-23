# Curadoria incremental HAMOOPIG — 18 de setembro de 2026

## Parecer

O HAMOOPIG ja oferece aprendizado reutilizavel de engine: combate dirigido por eventos, persistencia de recursos graficos, transicoes de estado e instrumentacao rastreavel. Sua contribuicao mais forte ao agente e ensinar a diagnosticar interacoes entre sistemas, reproduzir a falha e limitar a conclusao ao que foi medido. Ainda nao demonstra producao ponta a ponta de um jogo com qualidade equivalente ou superior as referencias comerciais apresentadas.

Esta rodada **aplicou curadoria canonica**, autorizada pelo pedido do usuario, mesmo com o projeto incompleto. Foram inventariados 74 registros JSON de curadoria anteriores; oito fontes foram selecionadas para oito principios, com suporte adicional em codigo e testes. Os demais registros permanecem inventariados, sem promocao automatica. Nao sao 74 capacidades novas comprovadas.

## O que entrou no agente canonico

Referencia compartilhada: `tools/sgdk_wrapper/.agent/references/hamoopig_engine_learning_2026_09_18.md`, relativa a raiz do workspace. Ela ja pertence ao escopo `references` do framework_manifest; nao foi criada uma arvore paralela.

| Aprendizado assimilado | Skill existente | Efeito pratico no proximo projeto |
|---|---|---|
| Identidade de ataque persiste entre ticks; consumidores aplicam efeitos uma vez | collision-system-architect | Evita dano/medidor repetidos por overlap prolongado |
| Alcance de comando precisa ser realizavel depois de pushboxes e limites | collision-system-architect | Testa geometria real e os dois lados antes de ajustar numeros |
| Adiamento de uploads exige contrato entre animacao e colisao | vram-streaming-dma-queue | Evita corrigir fila DMA criando golpe visualmente atrasado |
| Sprites persistentes, aliases e debug precisam de owners e ciclo de vida | vram-streaming-dma-queue; game-state-transition-architect | Investiga vazamento e realocacao antes de culpar o HUD |
| Transicao coordena input, fade, filas, paletas e conclusao das transferencias | game-state-transition-architect | Impede escrita concorrente e heranca de estado entre cenas |
| Probe informa unidade, schema, saturacao e limites de cobertura | emulator-vdp-evidence-curator | Impede usar bytes enfileirados como tempo de CPU ou budget completo |
| Matriz precisa separar configuracao solicitada de observada e probe de partida | emulator-vdp-evidence-curator | Evita falso verde por quantidade de capturas |
| Janela offline e metadata nao equivalem a streaming executado | vram-streaming-dma-queue | Exige slots, misses, uploads e seams medidos na ROM |

Quatro SKILL.md receberam instrucoes de acionamento e link para a referencia. Nenhuma skill nova foi necessaria; nenhuma especializacao subiu para MESTRE e nenhuma tecnica de registry foi promovida. A `.agent` local do HAMOOPIG foi preservada.

## Evidencia e limites

ROM encontrada nesta auditoria: `4c273bd5803913acbd62a55e6386f7c1e50e4d707cd14fd2fdd6c715ffa0ebbc`.

- Os 33 scripts `tests/test_*.py` foram executados nesta rodada e passaram. A suite mistura contratos estaticos com testes comportamentais; o resultado nao significa 33 testes de gameplay no console.
- `test_combat_event_contract.py` compila/executa o modulo C com stubs de tipos. Sustenta deduplicacao e consumo nos casos cobertos, sem provar sincronismo visual ou todos os cenarios multihit.
- O self-check do decoder HPRB passou, incluindo dump truncado, schema incorreto e contadores sem validade. Isso prova os casos de parser exercitados; nao torna todos os limites nominais do relatorio limites fisicos certificados.
- Existem registros de 36 combinacoes P10 vinculadas a ROM atual e de throws por input normal. A integridade verificada pela suite nao equivale a observar cada selecao no runtime nem a completar cada partida.
- Os registros de L074/L075 e transicoes preservam hashes historicos. Servem como casos de causa/correcao, sem revalidar automaticamente o binario atual.
- Esta rodada nao executou nova sessao de BlastEm, novo build, escuta critica ou avaliacao visual independente. Nao emite novo status `testado_em_emulador`, `validado_budget` ou `ready_for_aaa`.

## Lacunas que merecem trabalho

| Prioridade | Lacuna observada | Acao e criterio de conclusao |
|---|---|---|
| P0 | `COMBAT_EVENTS_EMIT_SOURCE` indexa gates por fonte sem guarda completa; identidade usa u8 | Validar dominios antes de indexar; exercitar fonte invalida e wrap/reuso de instancia em teste C. Aceite: sem acesso fora de limites ou supressao indevida |
| P0 | Delta de vida e associado por busca do ultimo evento do defensor | Definir associacao explicita ao evento antes de multihit/projeteis simultaneos. Aceite: ordem diferente de eventos nao altera atribuicao de dano/medidor |
| P0 | Decoder pode emitir decisao baseada em DMA sem agregar overflow de sprites; conta sprites por linha, nao pixels | Corrigir agregacao e medir os dois limites de scanline, com fixtures negativas e self-check. Aceite: nenhum eixo reprovado produz budget global verde |
| P1 | Atraso de frame visual e janela de golpe ainda precisam ser cruzados | Medir dois lutadores, FX, HUD e audio na mesma cena pesada; registrar tick, frame visual e contato. Aceite: contrato temporal cumprido no pior quadro |
| P1 | Reset/retorno e parte da evidencia de HIT/audio possuem historico de outras ROMs | Recapturar somente os claims afetados no SHA vigente, com ciclos repetidos, estado inicial/final e inventario de recursos |
| P1 | Matriz comprova integridade de arquivos melhor que cobertura de gameplay | Registrar IDs realmente observados; cobrir guarda, throw, hit, KO, time-over, reset e partida completa nos recortes declarados |
| P1 | Streaming permanece futuro; medicao de janela nao cria cache | Implementar piloto somente apos budget/contrato; testar misses, seams, alta velocidade e retorno de camera. Medir proximo degrau acima do atual |
| P1 | Higiene falhou com entradas orfas e nomes nao canonicos | Inventariar dependencias e conteudo antes de mover; classificar `tests` e material bruto, isolar artefatos fragmentados. Aceite: validator sem blockers e evidencias ainda resolviveis |
| P1 | Memoria mistura bloco gerado atual com prosa de hashes antigos | Manter um resumo vigente inequivoco e rotular snapshots historicos; validar freshness antes de proximo fechamento |
| P2 | Palcos/personagem candidato e audio ainda carecem julgamento final | Revisao visual em movimento e escuta critica, com proveniencia por asset. Codigo licenciado nao certifica direitos de todo material importado |

A higiene apresentou dois tipos de blocker: `orphan_project_root_entry` e `noncanonical_project_entry_name`. Ha diretorios como `Forge`, `[SGDK` e `[FIGHTING]` e material bruto nao classificado. Os nomes sugerem problemas de tratamento de caminhos, mas a causa de criacao nao foi demonstrada; nao apagar como se fossem lixo comprovado.

O contexto validou como `technical_demo`, fase declarada `planning`. Essa classificacao passa no validator, mas a fase merece reconciliacao com a implementacao ja avancada. Nao converter para `aaa_game` so para aumentar a exigencia de claims.

## Plano de avanço

1. **Consolidar a base verificavel — owner runtime/QA.** Resolver P0 de eventos e medidor, reconciliar memoria/contexto e higiene. Entregar testes negativos, relatorios de contexto/higiene/freshness e lista de claims atuais. Nao refatorar toda a engine para cumprir este marco.
2. **Fechar uma luta representativa — owner combate/VDP.** Selecionar um matchup, um palco e ambos os modos regionais suportados. Percorrer input normal ate resultado e novo round, com audio; medir pior quadro, atraso visual e pressao completa de scanline. Entregar ROM selada, captura BlastEm e artefatos de estado exigidos.
3. **Expandir com custo conhecido — owner assets/streaming.** Medir degrau acima dos 864 tiles atuais, cenarios maiores e animacoes simultaneas; decidir residencia ou cache por medicao. Valores 100 de alcance e 588 de janela continuam locais. Entregar comparacao antes/depois e fallback autorado.
4. **Fechar experiencia — owner design/arte/audio.** Julgar leitura de golpes, feedback, ritmo, transicoes, mix e consistencia de estilo. Assets candidatos so viram finais com proveniencia e aprovacao propria; contadores e MSE nao substituem este trabalho.
5. **Demonstrar transferencia — owner agente canonico.** Aplicar os mesmos principios em outro projeto com fixtures e medicao proprias. Somente depois avaliar aumento de proficiencia pelo processo existente. A assimilacao de instrucoes realizada agora nao prova essa transferencia.

As referencias comerciais sao metas de oficio e impacto percebido. O HAMOOPIG atualmente ensina sobretudo combate, recursos e verificacao; nao demonstra FMV, SVP, raster de alta complexidade ou driver PCM customizado. Essas capacidades exigem experimentos e evidencia separados, vinculados a uma necessidade do jogo. Nenhuma comparacao de superioridade foi certificada.

## Rastreabilidade

- `curation_decisions.json`: autorizacao, alvos canonicos, fontes e hashes; distingue assimilacao de inventario.
- `host_tests.json`: saida e exit code de cada um dos 33 testes.
- `canonical_validation.json` e `validation_*.log`: verificacoes das skills, schemas e probe.
- `framework_baseline.log`: falhas anteriores a esta alteracao, para comparacao.
- `context_report.json` e `hygiene_report.json`: estado dos validadores do projeto.

A curadoria automatica Capture permanece local e sem promocao automatica. A assimilacao manual autorizada esta registrada separadamente neste documento e no arquivo de decisoes.

## Resultado das verificacoes canonicas

Quatro skills passaram em `quick_validate`; 84/84 casos da suite de schemas passaram. A validacao global do framework falhou antes e depois, com 15 apontamentos preexistentes e 0 apontamentos novos. As falhas abrangem contratos/politicas de outras skills e limites de contexto; nao foram ocultadas nem reparadas fora do escopo. Ver `framework_comparison.json`. Nao ha alegacao de framework integralmente verde.
