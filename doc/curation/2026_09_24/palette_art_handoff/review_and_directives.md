# Parecer: divisão entre engenharia e reautoria visual

2026-09-24. Proposta de revisão; nenhuma alteração de código, pixel, regra ou skill. Fonte: PR19, commit `c05f88bb6dce3ff079ce7dafeb932add818de388`. [Evidências reproduzidas](diagnostic_evidence.json).

## Decisão recomendada

Manter o agente atual como responsável técnico e integrador. Delegar trabalho visual delimitado a um agente capaz de inspecionar, gerar/editar e persistir imagens. A capacidade geral inferior não impede uma colaboração útil, desde que ele receba restrições claras, produza candidatos e não decida arquitetura, gameplay ou aprovação final.

Antes da encomenda visual, corrigir o medidor e fechar o contrato de paleta. O bloqueio atual não é exclusivamente artístico. Não recomendo merge do PR19 na forma auditada: o verificador contém erro que afeta seu resultado principal. Contrato/documentação e ferramenta corrigida podem ser integrados antes da arte, sem declarar migração concluída.

## Achados reproduzidos

### F1 — conversão VDP→RGB incorreta

`tools/mugen2sgdk_forge/mugen2sgdk_forge/palette_contract.py:28–29` desloca os canais por1/5/9 e depois usa máscara0xE. Esses deslocamentos já colocaram cada canal em bits0..2: a máscara deve preservar os três bits, não descartar o bit0.

|Palavra VDP|Atual|Decodificação coerente com a grade252 usada no conversor|
|---|---|---|
|0x002|(0,0,0)|(36,0,0)|
|0x00e|(109,0,0)|(252,0,0)|
|0xeee|(109,109,109)|(252,252,252)|

Correção candidata de extração: `((word >> shift) & 7)` para shifts1/5/9. A expansão RGB deve seguir o modelo de cor escolhido pelo pipeline: atualmente múltiplos de36; expansão normalizada até255 também preserva os oito níveis, mas não deve ser misturada silenciosamente com outra calibração. São aproximações RGB de trabalho, não caracterização analógica do console.

Ensaio sem escrita nos fontes: substituí apenas `_rgb` no processo Python e reexecutei o mesmo checker. Resultado atual20; com decodificação corrigida24, mantendo as outras hipóteses do algoritmo. Ambos reprovam; a magnitude e os agrupamentos mudam. **24 não é mínimo matemático nem requisito artístico definitivo.** Os dados de ΔE/mapeamento devem ser recalculados conforme a ferramenta que os produziu; não afirmar que todos os números antigos derivaram necessariamente desta função.

A suíte atual passou56/56. Falta teste com valores conhecidos de hardware; fixtures que fixam o20 calculado pelo mesmo código não detectam esse erro.

### F2 — slots reservados não são cores únicas necessárias

`slots_needed` soma todos os15 índices do corpo independentemente de uso/duplicação. Um contraexemplo com15 slots iguais em vermelho e um efeito verde é declarado16, embora use somente duas cores visíveis. Isso é estimativa conservadora da alocação atual, não solver de empacotamento nem prova de necessidade de reautoria.

No Ken real, os slots1 e6 são `0x68c` nas12 variantes. Há8 cores distintas nos9 slots estáveis. Um remapeamento coerente pode reduzir o corpo de15 para14 slots ocupados, preservando as seis entradas de roupa e liberando uma entrada para FX. Essa é oportunidade técnica, não autorização para alterar cor ou desenho. Comparar todos os frames/variantes antes/depois e revisar uso dinâmico de índices, flash e tabelas de materiais. Não usar índice0 para pixels opacos.

O novo relatório deve separar: slots reservados, índices usados, cores exatas por variante, classes com comportamento igual em todas as variantes, estimativa perceptiva, mapeamento proposto e validação do resultado convertido. Contagem com ΔE≤10 não prova igualdade física de cor: implica aproximação que precisa ser realizada e julgada.

### F3 — brief mistura dois orçamentos incompatíveis

Nove slots estáveis + seis de roupa já ocupam15. Não há mais cinco slots dedicados livres. Após a compactação exata acima, a hipótese é **oito estáveis + seis de roupa + um FX =15**. O artista pode redesenhar usando o conjunto estável, o único slot recuperado e a transparência; ele não pode inventar quatro slots restantes.

As cores estáveis atuais são predominantemente tons quentes de pele/cabelo e escuros. Preservar hadouken azul/branco com essa restrição é desafio de direção de arte, não consequência de quantização. Primeiro testar um ciclo piloto com uma cor azul dedicada e reaproveitamento dos tons claros. Se o resultado não atingir a leitura desejada, devolver alternativas medidas e solicitar decisão de compromisso: reformular rampas/materiais, aceitar mudança estética ou rever o contrato. Não responsabilizar o artista por incompatibilidade não resolvida.

### F4 — Suzaku precisa de orçamento conjunto e contrato atualizado

O memo do estágio ainda descreve a alocação antiga, com8 cores de cenário e90 tiles livres. São dados daquele estado, não orçamento final após migração/recuperação de VRAM. Na REGRA1, BG_A e BG_B compartilham **uma mesma PAL0**, com no máximo15 entradas visíveis no contrato: não são15 cores diferentes para cada plano.

O agente técnico deve atualizar orçamento, largura/câmera, corte vertical, posição do piso, planos, tiles residentes, uploads e restauração depois do super. O artista pode estudar uma faixa representativa enquanto esses dados são preparados; o cenário completo só deve avançar quando o contrato estiver medido.

O memo local identifica fonte MUGEN em320×240 e corte240→224. Não aplicar automaticamente escala384→320 ao estágio. Para corpo do Ken, ocupação horizontal de tela e aspecto de exibição são problemas distintos:5/6 é uma alternativa estética medida, não restauração universal de proporção. Não redimensionar corpo ou hitboxes nesta rodada de paleta.

### F5 — waiver e flash precisam de limites explícitos

`--waiver` retorna0 mesmo com `fits=false`. Pode registrar uma exceção de investigação, mas não deve converter reprovação de recursos em aprovação de build/arte/entrega. Consumidores precisam verificar os estados explícitos. LimiteΔE infinito/NaN ou entrada malformada também precisa de política validada, não verde acidental.

Com corpo e efeitos na mesma linha, um flash que troca cores da linha pode afetar também projéteis e efeitos ativos daquele lutador. Declarar se isso é desejado; testar duas personagens, projétil distante, hitstop, hits consecutivos, super, KO, pausa e restauração. Estar dentro da linha correta não prova isolamento ao corpo.

## Divisão de trabalho

|Responsável|Pode fazer agora|Aceite e limite|
|---|---|---|
|Agente técnico atual|Corrigir e testar decodificador; auditar uso de índices/duplicatas; produzir remap sem perda; recalcularΔE; corrigir brief|Oito níveis distintos por canal, testes independentes, comparação exata em todas as variantes; nenhuma mudança de desenho|
|Agente técnico atual|Atualizar budget VRAM/DMA/scanline, medir pico com áudio, preparar restauração de paleta e testes do flash|Números por ROM/estado; contagem e pixels/linha; probe e captura separados da cadência|
|Agente técnico atual|Implementar mapeamento de PALs e integração atrás de estado explicitamente experimental, preparar fixtures sintéticas|Não marcar migração concluída nem promover assets incompatíveis; integrar arte final só após aceite|
|Agente visual|Piloto de uma família de FX; estudar forma, energia, contrastes e ciclo com paleta alvo|Arquivo persistido, coerência de silhueta/pivot/timing e comparação; candidato até aprovação|
|Agente visual|Uma faixa de Suzaku incluindo materiais de céu, arquitetura e piso; propostas de simplificação modular|Paleta compartilhada real, escala e profundidade; nenhuma promessa de orçamento a partir de imagem bonita|
|Agente técnico + revisor visual/humano|Converter/indexar, verificar restrições, integrar e avaliar em ROM/AV|Validação técnica não substitui julgamento visual; imagem isolada não aprova movimento|

O mesmo agente pode exercer direção técnica e preparar as perguntas da revisão visual se conseguir inspecionar imagens. Se não consegue vê-las, designar explicitamente um revisor visual; não inferir aprovação a partir de métricas.

## Ordem e pacote de passagem

1. CorrigirF1/F2 e retestar PR19. Publicar relatório de capacidades, fonte/ROM/arte hashes, tabela exata de slots e o que pode mudar. Não é preciso gerar imagem para essa etapa.
2. Compactar duplicação sem perda e provar equivalência. Fixar um contrato versão/hash para o piloto. Manter análise de outras oportunidades sem prometer ganho não medido.
3. Entregar ao agente visual os frames da família escolhida, AIR de origem, pivots, bounding boxes, timings, paleta em palavras VDP e PNG, mapa de slots, contexto de fundo claro/escuro e dois lutadores. Não solicitar roster inteiro.
4. Propor duas leituras visuais justificadas. Avaliar um ciclo completo de ataque/FX em tamanho nativo; três poses isoladas não aprovam o ciclo. A ferramenta de geração produz fonte/candidato; exportação indexada e fidelidade temporal precisam de pipeline e revisão.
5. Integrar o vencedor, capturar ROM com áudio e validar composição/fluidez. Só depois estender às demais famílias. Suzaku segue contrato próprio após atualização de budgets, podendo ter estudos visuais em paralelo.

Entradas mínimas do pacote: `brief.md`, `palette_roles.json`, `asset_inventory.json`, `source_hashes.json`, `frame_contract.json`, `budget_report.json`, referência visual, critérios de revisão e limitações de capacidade do executor. Os nomes são proposta de artefatos do caso, não novos schemas canônicos já existentes.

Saídas mínimas: fonte de edição e imagem persistida, alternativa selecionada, mapa de cores, inventário antes/depois, transformações realizadas, hashes, previews de ciclo, perda conhecida, relatório técnico e veredito visual separado. Se o canal só entrega imagemRGB, registrar essa capacidade e encaminhar a indexação; não anunciar PNG indexado sem verificar modo/tabela/pixels.

## Diretiva para o agente técnico

> Continue como responsável pela engine e integração. Antes de merge doPR19, reproduza os vetores0x002/0x00e/0xeee de `palette_contract._rgb`; corrija a extração dos três bits e alinhe a expansão RGB ao conversor. Acrescente regressões independentes para oito níveis por canal, duplicatas/índices não usados, variantes, transparência e waiver. Recalcule as métricas; não mantenha20 como expectativa fixa sem novo fundamento. Audite os slots1/6 iguais nas12 variantes e prepare remapeamento sem perda com prova por frame, variante e flash. Atualize o brief: o orçamento candidato após essa fusão é8estáveis+6roupa+1FX. Não corte rampas, não escale corpo/hitboxes e não reescreva arte por primitivas. Feche o orçamento atualizado do Suzaku para PAL0 compartilhada pelos dois planos. Prepare o piloto visual e prossiga com testes, profiling e flash isolado; mantenha migração e aprovação estética pendentes até evidência real. Registre decisões e contraexemplos como candidatas no intake existente, sem canonização automática.

## Diretiva para o agente visual

> Atue como produtor visual sob o contrato entregue pelo responsável técnico. Confirme capacidade de ver referências, produzir/editar e persistir imagem; registre limites de indexação e consistência de animação. Use somente contrato corrigido, versionado e com hashes. Primeiro produza um piloto de uma família de FX, preservando função, trajetória, ponto de origem, limites de quadro e timing; não redesenhe o corpo. Respeite a lista explícita de slots permitidos; não invente cores livres. Produza duas alternativas de direção e um ciclo completo da selecionada, com comparação no tamanho nativo e contextos claro/escuro. Geração de imagem é fonte candidata, não aceite automático de pixel art final. Entregue arquivos reais e relato de perdas; encaminhe a indexação/conversão ao pipeline técnico quando necessário. Não mude gameplay, caixas, paletas de outros donos, código ou critérios de aprovação. Se o contrato não permitir qualidade suficiente, demonstre o conflito e devolva alternativas de compromisso ao responsável técnico. Suzaku é uma segunda tarefa: começar por faixa representativa, sob paleta única compartilhada e orçamento atualizado de tiles; não produzir o cenário inteiro antes do aceite do piloto.

## Aprendizado reutilizável proposto

Acrescentar ao intake já existente, após deduplicação, os seguintes candidatos; não criar outro ledger concorrente:

|Candidato|Evidência|Regra proposta|Contraexemplo que precisa sobreviver|
|---|---|---|---|
|Medidor antes de reautoria|Branco109 em vez de252;56testes passaram|Testes com vetores independentes de cor antes de decisões artísticas|Teste que repete contagem errada doKen não é oráculo|
|Empacotamento sem perda antes de sacrifício|Slots1/6 idênticos nas12 variantes|Separar índice reservado, usado, duplicado e cor visual|Dois índices iguais em uma variante podem divergir em outra/flash|
|Handoff sob contrato realizável|9+6 já ocupa15; brief ainda fala em5FX|Fechar aritmética/ownership antes de delegar|Artista não pode resolver orçamento impossível apenas por ser mais capaz|
|Capacidade por tarefa, não reputação de modelo|GerarRGB não prova PNG indexado nem ciclo coerente|Separar visão, geração, edição, persistência, indexação, revisão e runtime|Imagem bonita não prova temporalidade ou montagem noVDP|
|Cenário compartilha paleta entre planos|REGRA1 dáPAL0 aBG_A+BG_B|Validar união das cores, não cada imagem isolada|Dois planos de15cores podem precisar30 na composição|

Cada entrada deve preservar: problema/gatilho, hipótese, método, evidência comhash, resultado/limite, alternativa rejeitada, custo/ganho, owner, caso contrário, teste executável, decisão humana e estado de promoção. Uma segunda aplicação em outro personagem/estágio é evidência de generalização; a observação noKen é suficiente para candidata, não para regra universal sem condições.

## Limites desta revisão

56 testes passaram nesta sessão; diagnósticos foram executados em processos isolados sem patch no projeto. Não houve imagem criada/editada, novaROM, execução de emulador, merge ou comentário enviado ao outro agente. A decisão é de organização e correção do diagnóstico, não aprovação de qualidade artística. A fonte da revisão pode evoluir; refazer os vetores no novoSHA antes de reutilizar o parecer.
