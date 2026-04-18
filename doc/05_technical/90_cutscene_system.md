# Cutscene System — Mega Drive AAA

Aqui entra o diferencial técnico dos estúdios lendários da época (Treasure, Sega CS, Konami). Cutscene não é gameplay adaptado; Cutscene é uma disciplina separada.

## Regras Obrigatórias da Cutscene

**REGRA 1 — CUTSCENE NÃO É GAMEPLAY**
Por ser uma entidade isolada, a Cutscene:
- Pode quebrar as regras lógicas ou visuais do gameplay.
- Pode e DEVE mudar a escala (tamanho) das coisas e personagens na tela.
- Possui um "Pacing" completamente alheio ao jogo controlado.

**REGRA 2 — ECONOMIA INTELIGENTE**
Cutscenes NÃO devem focar em gastar VRAM excessiva detalhando movimento e "animar tudo" frame a frame. A melhor cutscene economiza na fluidez para abusar do "Truque Visual".

---

## O Arsenal de Elite: "Fake Cinema" (O Segredo Real)

Uma composição artística incrivelmente desenhada é sempre superior a uma animação média e cara. Use essas técnicas como prioridade:

🔥 **1. Cortes & Mudanças de Quadro:** Flashbacks, quebras repentinas no lugar de sprites caminhando.
🔥 **2. Pan & Scroll:** Mover virtualmente a câmera (através do mapeamento dinâmico de tiles ou scroll vertical/horizontal lento) revelando uma grande imagem estática, gerando epicidade colossal.
🔥 **3. Sprite Staging:** Controlar metodicamente as entradas e saídas de cena (teatro).
🔥 **4. Hold Frames:** Congelar a imagem deliberadamente (Hit Pause Narrativo) criando uma tensão respirável.
🔥 **5. Lighting como Narrativa:** Ao invés de redesenhar a cena de noite, manipular as Paletas de Hardware (escurecer tudo menos o personagem, ou piscar em alarme vermelho).
🔥 **6. Som como Força Principal:** Muitas vezes a cutscene opera apenas no **Silêncio**. E quando a ação acontece, o FX Sonoro entra como a espinha dorsal cortante. Timing é rei.
🔥 **7. Composição Base:** Uma arte estática colossal (*Imagem bem feita > Animação complexa*).

---

## Template Obrigatório de Cutscene (Documentação)

Se o agente propor ou codificar uma nova tela de narrativa, ELA TEM QUE RESPONDER ESTE DOCUMENTO SEM EXCEÇÃO ANTES DE QUALQUER PIXEL SER PROGRAMADO:

- `## intencao`: (O sentimento evocado)
- `## estrutura narrativa`: (Começo, meio, fim do quadro)
- `## linguagem cinematografica`: (Quais dos 3 métodos do `doc/01_game_design/30_cinematic_language.md` vão ser adotados)
- `## tecnicas utilizadas`: (Qual das 7 ferramentas de Fake Cinema acima foi selecionada)
- `## timeline`: (O script matemático, timings das paletas e delays em frames)
- `## uso de hardware`: (H-Int scanlines, VDP memory maps)
- `## signature moment`: (A grande virada emocional da cena)
