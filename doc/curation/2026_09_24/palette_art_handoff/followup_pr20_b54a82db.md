# Revisão do PR20 — b54a82db

Fonte: `b54a82dbc37b495b089c9f449c835d4372a1f5d9`. Suíte reexecutada: **65 passed em30,18s, sem skips**. Nenhum código, asset ou PR alterado por esta revisão.

## Parecer

A fusão de paleta tem prova relevante de equivalência por índice/cor nas12 variantes e teste de exclusão do slot livre para a sombra. Aprovação técnica da fusão não aprova o piloto visual ou a migração de todas as famílias.

**Recomendo corrigir o pacote de passagem antes de integrar o PR20 completo.** São correções delimitadas; não dependem de geração de imagens nem devem virar reescrita geral da engine. A Etapa3 pode avançar em ramo separado enquanto isso.

## Ajustes do piloto

### P1 — transparência da fonte perdida

Em `fx_pilot.py`, `src.convert("RGBA")` é executado sem atribuir transparência ao índice0. No arquivo entregue `source_750_1.png`, todos os alphas são255; os414 pixels de índice0 do SFF viraram pixels opacos. O canto exportado é magenta `(250,0,250,255)`.

Produzir alpha0 para índice0 e alpha255 para índices visíveis, ou fornecer máscara explícita vinculada por hash e claramente documentada. Para o piloto atual, RGBA transparente é a passagem mais direta. Não transformar todos os pixels pretos em transparentes: o núcleo preto do efeito é visível e precisa sobreviver.

Aceite: comparar máscara exportada com os índices da fonte; zero divergências. Testar que preto visível continua opaco. Atualizar previews, arquivos e hashes. Isso é correção de exportação de arte existente, não nova autoria visual.

### P1 — orçamento humano e máquina divergentes

Brief: máximo2 spritesHW por quadro. `budget_report.json` e `fx_pilot.py:127`: permitem16. Definir campos numéricos explícitos para limites do candidato e gerar o texto a partir deles. Teste deve detectar divergência entre brief e contrato, sem depender de buscar uma palavra solta.

Os valores atuais têm origem estimada: `hw_sprites` vem de `_hw_estimate` (blocos32×32 não vazios), e `dma_bytes_if_uploaded` é a contagem de tiles não vazios×32. Esses cálculos não demonstram por si só a decomposição final do ResComp, seu custo de upload ou pressão da cena.

Aceite: limite de projeto declarado (por exemplo2HW e26tiles) separado da estimativa de fonte e da medição compilada. Confirmar os números finais após ResComp e na integração em ROM; não renomear estimativa como medição. Medir dois lutadores, HUD e FX juntos antes de aceite global.

### P2 — catálogo de cor tem apenas o resultado já degradado

`fx_catalog.json` é construído com `spr.fx_palette` e sheets convertidas. Isso é útil para diagnosticar o estado atual, mas perdeu cores da fonte; não basta para escolher o único slotFX que atenderá todas as famílias.

Adicionar inventário por família da fonte original, distinguindo transparência, cores visíveis, remapeamento atual e cores/material indispensáveis. Manter os dois lados e suas perdas. Não escolher a cor global com base apenas na paleta que já fez o núcleo preto virar vermelho e colapsou azuis.

## Proveniência: achado preexistente ainda sem proteção

Reverter manualmente as alterações protegeu esta execução. `provenance.write_visual` ainda substitui as entradas pelo prefixo; `write_audio` reescreve o documento. O defeito de preservação não foi resolvido apenas por registrá-lo em memória.

Antes da próxima reconversão sobre o projeto ativo, implementar proteção ou operação isolada com comparação e bloqueio de publicação. Solução recomendada: separar metadados derivados dos pareceres humanos, ligando decisões ao hash da fonte/asset. Preservar restrições, justificativas e histórico; se os pixels mudarem, invalidar a aplicação de uma aprovação anterior ao novo artefato sem apagar a aprovação histórica. Não carregar `final` cegamente nem apagá-lo sem trilha.

Teste mínimo: anotação humana e restrição de distribuição sobrevivem à reconversão; reconversão idêntica é idempotente; mudança de conteúdo exige nova aprovação; recursos removidos ficam identificáveis no histórico. É uma tarefa técnica prioritária, não bloqueio do agente gráfico.

## Etapa3 e performance

Pode desenvolver shake/flash em ramo próprio, com tabelas por lutador e testes de hitstop, acertos consecutivos, projétil distante, super, KO e pausa. Só declarar ausência de spill nos efeitos depois da migração real destes para a linha do lutador. Testes na alocação antiga permanecem parciais.

68/1200 versus70/1200 é uma diferença observada reportada pelo autor, não prova de regressão causal ou de equivalência de performance. Uma rodada não isola variação de execução; equivalência de pixels também não garante DMA idêntico. Não repetir captures sem objetivo: usar inputs/seed e configuração controlados quando necessário para decidir aceitação de desempenho.

Não fiz nova execução de ROM nesta revisão. Os16 arquivos listados no manifesto do piloto conferiram seus hashes; hashes corretos provam identidade, não corrigem transparência, orçamento ou fidelidade. Os testes passaram, mas não cobrem os dois erros de passagem reproduzidos acima.

## Direcionamento ao agente

Corrija transparência e contrato2/16 no gerador, regenere o pacote e atualize hashes/testes. Acrescente a fonte original ao catálogo de famílias antes de escolher o slot global. Integre o PR20 como fusão e preparação do piloto, mantendo o aceite artístico pendente. Prossiga com a Etapa3 em paralelo técnico e proteja a proveniência antes de outra reconversão no projeto ativo. Atualize os candidatos existentes com esses contraexemplos e testes, sem duplicar escolas ou canonizar automaticamente.
