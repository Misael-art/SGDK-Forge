# Portfolio local de otimizações VDP sob pressão

Estado: **opções candidatas, não aprovadas nem implementadas**. Este catálogo
registra alternativas autorizadas para investigação quando uma cena concreta
exceder um limite medido do Mega Drive. Não é uma licença para reduzir arte,
piscar objetos por conveniência ou fechar um budget por estimativa.

## Gatilho comum

Só testar uma opção depois de reproduzir o pico no estado de jogo mais pesado e
identificar o recurso que estourou: sprites por linha, pixels por linha,
VRAM contígua, CRAM, ciclos do 68000, fila DMA ou janela de VBlank. Registrar a
ROM, os inputs, o estado visual de referência, o pico anterior e o valor depois
da variante. Manter a mesma coreografia no A/B. Aceitação visual fica humana e
vinculada ao SHA; nenhuma técnica abaixo autoriza promoção automática.

## Recurso que cada alternativa pode realmente liberar

- Sombras P1/P2 alternadas liberam apenas entries/pixels de sprite nas scanlines
  em que a sombra omitida estaria visível. Não reduzem automaticamente tiles de
  VRAM, ROM, CRAM, custo do 68000 ou bytes de DMA. Se a sombra já usa o shadow
  bit ou é parte da arte do lutador, nem o ganho de scanline existe.
- Alternar halos/adornos de dois especiais tem o mesmo limite: reduz pressão de
  sprite por scanline enquanto omite os adornos. Só reduz VRAM se um sistema
  separado descarregar os tiles durante a janela e provar a nova residência;
  piscar sem esse caminho não libera tiles.
- Reutilizar cores do HUD pode reduzir o número de índices CRAM distintos que
  um FX precisa, desde que os valores CRAM sejam iguais. Não economiza tile,
  VRAM, scanline, DMA nem CPU por si só; aproximação de cor pode piorar a leitura.
- Apontar o backdrop do VDP para uma palavra CRAM já carregada pode evitar uma
  cor exclusiva para o campo de fundo. Tornar preenchimento plano transparente
  pode remover tiles se o código de pixel 0 ficar realmente exposto; não remove
  entradas do mapa e não poupa o slot se tiles opacos ainda usam essa cor.
- Desligar sombras durante duas magias simultâneas é fallback de scanline. Deve
  restaurar a exibição em todos os estados de interrupção do golpe e round.

As categorias não são intercambiáveis: pressão de tiles se resolve com
residência, deduplicação exata, recorte, janela de animação, streaming ou
reautoria; pressão de scanline se resolve com decomposição de sprites,
prioridade e multiplexação cosmética medida; pressão de CRAM se resolve com
paleta, índice compartilhado ou troca explicitamente controlada. Não somar uma
economia de um recurso a outro.

## Alternativas disponíveis

| Alternativa | Quando pode ajudar | Limites e condição de aceitação |
|---|---|---|
| Alternar as sombras cosméticas de P1/P2 | Só quando cada sombra é um objeto de sprite separado e a sonda mostra que as sombras contribuem para o estouro de sprites/pixels por scanline. Uma fase determinística alterna qual sombra é desenhada durante um evento curto. | Não economiza nada se a sombra já estiver embutida no sprite, num plano ou no shadow bit. Cada sombra passa a aparecer em quadros alternados; avaliar flicker na cadência real de 50/60 Hz, leitura do chão, pausa e hitstop. Nunca piscar o corpo, hurtbox, hitbox ou contorno essencial. Desligar a alternativa se causar cansaço ou perda de leitura. |
| Reutilizar cores existentes da paleta do HUD em FX | Quando os valores CRAM de um efeito, após a quantização real do Mega Drive, já coincidem com entradas existentes do HUD; isso pode deixar mais entradas das PAL1/PAL2 para o personagem ou outros FX. | É compartilhamento de valores existentes, não empréstimo de uma paleta em runtime. Não alterar CRAM do HUD durante a luta, nem atribuir PAL3 a sprites sem provar o atributo e o conflito por tile. Se as cores forem apenas aproximadas, medir ΔE no espaço correto, inspecionar cada frame em 1x e obter aprovação humana. Não sacrificar contraste do HUD, corpo ou silhueta do efeito. |
| Reusar índice de backdrop e remover preenchimento plano redundante | Quando o fundo plano harmoniza com uma palavra CRAM exata já carregada e o tilemap deixa regiões desse fundo transparentes. `VDP_setBackgroundColor(value)` usa o índice global CRAM `0..63`, não RGB. | Verificar fonte SGDK e CRAM real; mudanças numa entrada compartilhada também mudam o backdrop. Código de cor 0 revela a layer inferior antes do backdrop, então auditar BG_A/B, WINDOW, limites, super e transições. Só creditar VRAM quando ResComp provar que tile patterns foram removidos; o mapa continua ocupando entradas. Se tiles opacos ainda usam a cor, transparência não libera seu slot. |
| Multiplexar adornos de dois especiais grandes simultâneos | Só se os dois especiais ativos estourarem o budget e houver camadas redundantes separáveis: sombra, halo, cauda, brilho ou partículas periféricas. Alternar apenas esses adornos pode aliviar o pico instantâneo. | O núcleo reconhecível de cada projétil, sua trajetória, colisão e indicação de perigo continuam visíveis em todos os quadros. Primeiro medir cada especial sozinho e os dois juntos. Se o pico persistir, desligar temporariamente as sombras cosméticas durante a sobreposição e restaurá-las ao fim do evento. Restaurar também em interrupção, hitstop, superpause, KO, troca de round e saída da cena. Não piscar dois projéteis inteiros como solução padrão. |
| Mover FX geométricos para BG_A/B e animar a paleta | Quando a imagem é grande, a geometria dos frames é idêntica e apenas as cores mudam; substitui muitos sprites por tiles do plano e uma tabela de paleta predeclarada. | Só com verificação pixel a pixel da geometria, owner de plano/paleta, orçamento de VRAM/DMA e transição que não cubra HUD nem gameplay. Usar apenas quando a função visual e a prioridade em relação aos lutadores forem preservadas. |
| Aparar transparência e repartir sprites | Quando bounding boxes, margens vazias ou uma folha de sprites grande criam objetos/tile uploads desnecessários. | Comparar máscara alfa/index 0 pixel a pixel; preservar pivot, offset, AIR, hitboxes e sequência. Recompilar com ResComp e medir a folha final, pois a deduplicação e o alinhamento mudam o custo. |
| Desduplicar tiles com flip e preaquecer a janela visível | Quando o custo dominante é residência/streaming de cenário ou FX em placas. | Deduplicação deve preservar atributos e prioridade por tile. Streaming exige cache contíguo, prefetch e DMA explicitamente dentro do VBlank; nunca presumir que bytes livres totais formam um bloco utilizável. |
| Repartir o limite entre tiles fixos e pool automático de sprites | Quando o cenário precisa de mais índices fixos e a telemetria demonstra margem no maior bloco do allocator. No SGDK 2.11, reduzir `SPR_initEx(600)` para `SPR_initEx(446)` desloca o início do pool de 840 para994 e aumenta a janela de tiles fixos de824 para978 (+154). | Não cria VRAM; transfere capacidade do pool automático para assets fixos. A sonda atual observou pico353 usados e maior bloco livre72 sem palco e com audio dummy; isso não aprova pool446. A composição Suzaku de15 cores ainda precisa758 tiles no frame-âncora completo; somar154 e emprestar BGFX272 dá teto hipotético516, ainda 242 abaixo. Só testar em ROM descartável pareada com stage, áudio, projéteis, super, pressão de DMA, falhas de sprite e maior bloco contíguo. |

## Ordem de tentativa

1. Corrigir contagem e medir a causa real; remover duplicação exata de pixels,
   tiles e uploads sem mudar a imagem.
2. Otimizar recortes, segmentação e prefetch, preservando máscara, pivots e
   colisão.
3. Compartilhar entradas de paleta existentes somente se forem iguais após a
   conversão CRAM; aproximar cores requer aprovação visual.
4. Reduzir elementos periféricos, usar paleta animada ou transferir geometria
   equivalente a um plano se a cena comportar.
5. Multiplexar ou ocultar temporariamente **sombras decorativas** apenas sob
   pressão medida e durante a janela mínima necessária.
6. Se ainda não couber, redesenhar o efeito e seu orçamento com direção de arte;
   não degradar o núcleo legível do golpe para fazer o relatório passar.

## Verificação obrigatória da variante

- Comparação A/B com ROM/estado/inputs equivalentes e capturas do instante de
  pico, em BlastEm, com áudio habilitado quando o áudio participar da carga.
- Dois limites de sprites por scanline em H40: no máximo 20 objetos e 320
  pixels visíveis; registrar também o maior bloco contíguo de VRAM e o pico de
  DMA/VBlank. Uma das duas métricas de scanline não substitui a outra.
- Regressões de pausa, hitstop, superpause, KO, revanche e transição de cena;
  paletas e sombras retornam exatamente ao estado-base.
- Vídeo curto em velocidade real e inspeção humana da leitura de silhueta,
  contraste, flicker, continuidade e percepção de golpe.
- Manifesto de proveniência e aprovações amarradas ao SHA dos pixels. Sem isso,
  a alternativa permanece em `rascunho/`.

As sugestões foram registradas como possibilidades de portfólio por pedido do
usuário em 2026-09-26. Nenhuma foi testada ou promovida neste checkpoint.
