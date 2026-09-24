# Orientações do ecossistema original da HAMOOPIG — revisão planejada da engine

**Projeto:** HAMOOPIG [VER.001] [SGDK 211] [GEN] [ENGINE] [FIGHTING]  
**Data do registro:** 2026-09-12  
**Status:** documentado; revisão da engine planejada, ainda não promovida para implementação  
**Fonte principal:** canais do servidor RETRODEVBR, incluindo `#ff-rheo-bout`  

## 1. Escopo e atribuição

Este documento registra práticas e observações encontradas nos canais do Discord indicados pelo usuário para orientar uma futura revisão técnica da HAMOOPIG.

O desenvolvedor original/maintainer da HAMOOPIG é **GameDevBoss / Daniel Moura**. Quando uma orientação foi publicada por ele, a autoria é mantida. As demais orientações são complementos de Vagno, Titan Doom, SirMacho, rheo, Alan ARS, HelderEstrela e outros participantes; não devem ser atribuídas a Daniel Moura sem confirmação.

As mensagens são referências de desenvolvimento, não substituem os headers do SGDK, os contratos do projeto ou a medição no emulador.

## 2. Orientações de engenharia a revisar

### 2.1 SGDK, ROM e hardware real

- A HAMOOPIG é uma engine construída sobre o SGDK; a compilação gera uma ROM de Mega Drive (DanielMoura/GameDevBoss, `#hamoopig`, 04/08/2025 e 06/03/2026).
- O primeiro passo para usar a engine é compilar o SGDK e confirmar a toolchain.
- A engine não garante desempenho por si só: organização do programador, tamanho da ROM e limites do console determinam o resultado (Chev/danielt3, 09/01 e 06/03/2026).
- Emuladores podem aceitar estados que quebrariam no hardware. BlastEm foi recomendado por reproduzir melhor o hardware; Gens KMod foi recomendado para inspeção de planos, tabela de sprites e VRAM; ClownMDEmu foi recomendado para observar tiles, ordem, paletas, BGA e BGB (06/03 e 10/09/2026).
- A revisão deve manter uma validação cruzada: build SGDK, BlastEm e inspeção de VRAM/planos antes de qualquer afirmação de compatibilidade.

### 2.2 Resolução, paleta e conversão

- A conversa contrasta 320×224 com uma área 256×190 e mostra gameplays em 320×224. Isso deve ser tratado como referência de viewport/crop, não como constante de hardware sem confirmação.
- Arte deve ser preparada para a resolução, o grid e as paletas do console; não deve ser escalada arbitrariamente.
- A referência de versão Mega Drive usa 15 cores por conjunto visual. Para este projeto, aplicar o contrato existente: até 15 cores úteis por subpaleta, com transparência reservada.
- O estilo de alto contraste foi elogiado repetidamente; usar contraste deliberado em cenário, logos, barras e textos.
- Shadow/highlight deve ser tratado como uso adicional de paleta, com reserva explícita antes de amarrar a paleta da cena.

### 2.3 Tiles, tilesets, tilemaps, camadas e VRAM

- Sprites são desenhados por tiles e há limite de tiles processados por unidade de tempo; camadas também são limitadas (Alan ARS/S0c4F0F0, 23/11/2025).
- Deve-se contabilizar literalmente atualizações por frame através do barramento, ciclos de CPU e camadas inferiores (rheo, 23/11/2025).
- Separar e registrar: tileset do cenário, tilemap, área reservada para sprites, HUD/window e buffers temporários.
- Artefatos podem ser o cenário invadindo a área de sprites, não necessariamente um problema de DMA. Verificar endereçamento e fronteiras no emulador antes de trocar `DMA_QUEUE` por DMA normal (SirMacho/Titan Doom, 25/08/2026).
- `gInd_tileset` precisa estar inicializada antes de carregar tiles do cenário na VRAM.
- `SPR_initEx` reserva a quantidade de tiles da área de sprites. O valor deve ser medido, não deixado em um número superdimensionado como 720; reservar somente o necessário para os sprites gerais e efeitos (Titan Doom, 25/08/2026).
- Em alocação manual, a área inteira do spritesheet deve ser reservada; em alocação automática, conferir o intervalo efetivamente utilizado.
- A área transparente de um frame ainda consome VRAM. Aumentar o quadro ou spritesheet aumenta a reserva mesmo quando há poucos pixels opacos.
- Quando um frame excede o bounding box, primeiro recuar a imagem e corrigir o offset no código. Se a animação for muito maior, usar spritesheet próprio e `SPR_setDefine` (Vagno/HelderEstrela, 21/03 e 21/06/2026).
- Reduzir tiles do cenário é uma correção plausível para artefatos; confirmar com dump/visualização da VRAM e não apenas pela aparência da tela.

### 2.4 Animação, gameplay e uniformidade visual

- Para obter fidelidade em uma conversão, usar sprites de referência, reduzir cores e reduzir o número de frames por animação quando necessário (Alan ARS, 19/07/2025).
- Uma compilação com hitsparks, IA e estilos de personagens incompatíveis perde uniformidade; HAMOOPIG deve manter arte, hitsparks, timings e regras coerentes entre lutadores (Slayer, 18/06/2025).
- Finalizações, intros e finais podem ser ripados/construídos na resolução nativa do Mega Drive; a referência `Real-Bout-Genesis-Intro.gif` deve ser tratada como estudo de composição, não como asset automaticamente reutilizável.
- O escopo deve priorizar estágios e personagens normais antes de extras (SSF2T, 10/09/2026). Personagens secretos, crossovers e transformações só entram se o GDD e o orçamento aprovarem.

### 2.5 Áudio

- Evitar piscadas rápidas de paleta sincronizadas à música; foi sugerida mudança controlada de paleta apenas quando a música toca, retornando ao normal ao parar (DanielMoura/GameDevBoss, 30/11/2024).
- Normalizar diferenças de volume entre músicas antes de release (Gamerisk, 02/12/2024).
- O canal de música registra teste de quatro PCM no XGM Driver e indica Sonniss/OpenGameArt como fontes gratuitas de efeitos; qualquer uso no HAMOOPIG deve manter proveniência e mapeamento de canais.

### 2.6 Manual, release e evidência

- Manuais precisam ser testados contra o jogo: foram encontrados erros reais de comando no Fatal Fury One e no Kunio (`Double Punch`/`Triple Punch` e `Pigskin Shot`).
- Toda ROM distribuída deve incluir README, comandos corretos, versão, créditos e contato do desenvolvedor.
- Projetos suspensos ou demos não devem ser descritos como full game; claims devem refletir o estado realmente demonstrado.
- Cenas e ROMs devem ser validadas no emulador e, quando possível, no hardware/flashcart; capturas de emuladores mais permissivos não bastam.

## 3. Aplicação planejada ao HAMOOPIG

1. Mapear a VRAM real da luta: início/fim do tileset do cenário, tilemap, área de sprites, HUD/window e sombra.
2. Confirmar `gInd_tileset`, `SPR_initEx` e a reserva efetiva de tiles; eliminar reservas arbitrárias.
3. Medir pior frame: bytes de VRAM, tiles, ciclos, camadas, sprites e áudio.
4. Comparar cenário em 320×224 nativo, crop seguro e compromisso 4× atual, sempre com contagem de tiles e contraste.
5. Revisar paletas do cenário, HUD e fonte com limite de cores e espaço para shadow/highlight.
6. Corrigir e validar animações de derrota/vitória sem ultrapassar spritesheet, VRAM ou endereços.
7. Normalizar BGM/SFX e validar os canais XGM/PSG conforme o manifesto de áudio.
8. Corrigir README/manual e registrar comandos testados, versão da ROM e hashes.
9. Repetir BlastEm, Gens KMod/ClownMDEmu, gates de render e captura de vídeo antes de promover qualquer resultado.

## 4. Relação com o estado atual

- O cenário atual já está em 14 cores e usa compromisso 4×; a revisão deve medir se o crop nativo pode ser recuperado sem invadir VRAM.
- O HUD usa WINDOW; sua prioridade e contraste devem ser confrontados com o orçamento de camadas.
- O experimento de derrota que causou `ADDRESS ERROR` permanece em quarentena até a revisão de spritesheet/VRAM.
- O texto pós-luta ainda não provou fidelidade à fonte autorada; aplicar a orientação de contraste e teste de legibilidade.
- O projeto permanece em teto `prototype`; esta pesquisa não promoveu nenhuma afirmação visual para `delivery`.

## 5. Canais consultados

`#ff-rheo-bout` (104 mensagens); `#tutoriais-exemplos-jogos-simples`; `#fatal-fury-one`; `#kunio-no-nekketsu-school-fighters`; `#street-fighter-1`; `#hamoopig`; `#blaze-engine`; `#sd89-engine`; `#ssf2-omega`; `#kofmd`; `#sfighter-vs-ffury`; `#art-of-fighting-special`; `#robocop`; `#musica`.

Os links originais permanecem no registro da solicitação e na sessão do Discord. Nenhum conteúdo foi publicado ou alterado nos canais.

**Próximo estado esperado:** revisão técnica da engine com medições reproduzíveis e atualização deste documento com resultados, hashes e evidência de emulador.
