# GDD — Pequeno Príncipe: Crônicas das Estrelas VER.002

**Versão do documento:** 2.0
**Plataforma:** Sega Mega Drive / Genesis — SGDK 2.11
**Gênero:** Aventura Contemplativa 2D
**Tom:** Poético, melancólico, esperançoso

---

## Conceito Central

Um jogo que captura a essência literária de "O Pequeno Príncipe" de Antoine de Saint-Exupéry em pixels e sintetizador FM. Não há morte, não há game over, não há inimigos. Existe exploração, contemplação e conexão.

O jogador encarna o Pequeno Príncipe em sua jornada por 12 planetas, cada um habitado por um personagem que representa uma faceta da condição humana. Cada planeta exibe uma técnica VDP distinta. Cada viagem testa uma virtude emocional do protagonista.

---

## Pilares de Design

1. **Contemplação antes de ação** — nunca forçar pressa no jogador
2. **Beleza técnica** — cada planeta demonstra o máximo do VDP Mega Drive
3. **Narrativa como mecânica** — diálogo é gameplay
4. **Sem punição** — falhar em uma viagem apenas reinicia a viagem
5. **Progressão emocional** — o Príncipe aprende algo em cada planeta

---

## Controles

| Botão | Planeta | Viagem |
|-------|---------|--------|
| A | Interagir / Planar (segurar) | Ação especial da viagem |
| B | (reservado) | (reservado) |
| C | Pular | Pular / Confirmar |
| START | Pausa | Pausa |
| D-PAD | Mover | Controlar |

---

## Loop de Jogo

```
[Planeta]
  1. Chegar (animação de entrada)
  2. Explorar (mover, observar ambiente)
  3. Encontrar personagem
  4. Diálogo (máx 4 linhas por tela)
  5. Resolver situação (acionar objeto, completar ação)
  6. Desbloquear Codex + entrada de viagem ativa
  7. [Viagem] → próximo planeta
```

---

## Os 12 Planetas

### B-612 — Planeta de Origem
- **Técnica VDP:** Line scroll por linha (HSCROLL_LINE) + palette cycling + H-Int split
- **Personagem:** A Rosa (encontro final — memória da primeira visita)
- **Mecânica:** Cachecol animado (spring chain sinFix16, 5 segmentos)
- **Cor dominante:** Dourado e laranja — pôr do sol perpétuo
- **Objetivo:** Regar a Rosa e dizer adeus

### Planeta do Rei
- **Técnica VDP:** Parallax multicamada (Plano A + B velocidades distintas) + column scroll
- **Personagem:** O Rei (REI)
- **Mecânica:** Obedecer comandos absurdos do Rei (pressionar direções específicas)
- **Cor dominante:** Roxo real e dourado
- **Objetivo:** Tornar-se Ministro da Justiça e partir

### Planeta do Vaidoso
- **Técnica VDP:** Sprite scaling simulado via tiles gerados em runtime + flash de paleta
- **Personagem:** O Vaidoso (VAIDOSO)
- **Mecânica:** Aplaudir (pressionar A rapidamente) — contador de aplausos
- **Cor dominante:** Rosa e prata brilhante
- **Objetivo:** Aplaudir 20 vezes para satisfazer o Vaidoso

### Planeta do Bêbado
- **Técnica VDP:** Sine wave no hscroll (efeito de embriaguez) + flicker de sprites
- **Personagem:** O Bêbado (BEBADO)
- **Mecânica:** Navegar com scroll ondulante até encontrar a garrafa vazia
- **Cor dominante:** Azul noturno e amarelo desbotado
- **Objetivo:** Esconder a garrafa e consolar o Bêbado

### Planeta do Homem de Negócios
- **Técnica VDP:** Tilemap dinâmico (estrelas contadas em tiles, atualizadas em tempo real)
- **Personagem:** O Contador (CONTADOR)
- **Mecânica:** Contar estrelas (pressionar A a cada estrela piscante)
- **Cor dominante:** Cinza frio e branco azulado
- **Objetivo:** Contar todas as 42 estrelas

### Planeta do Acendedor
- **Técnica VDP:** H-Int line-level palette swap (dia/noite a cada frame via HINT)
- **Personagem:** O Acendedor (ACENDEDOR)
- **Mecânica:** Ajudar a sincronizar o acendedor com o ritmo do planeta (timing)
- **Cor dominante:** Laranja quente e preto profundo
- **Objetivo:** Acertar o ritmo 3 vezes seguidas

### Planeta do Geógrafo
- **Técnica VDP:** MAP API (mapa grande scrollado com detalhe) + window plane para mapa HUD
- **Personagem:** O Geógrafo (GEOGRAFO)
- **Mecânica:** Exploração lateral extensa (mapa maior que tela) — encontrar 3 marcos
- **Cor dominante:** Bege, terra e verde musgo
- **Objetivo:** Reportar os 3 marcos ao Geógrafo

### Planeta da Serpente
- **Técnica VDP:** Raster interrupt (deformação de background) + sprite blending
- **Personagem:** A Serpente (SERPENTE)
- **Mecânica:** Seguir o rastro da Serpente sem tocá-la (pathfinding simples)
- **Cor dominante:** Amarelo esverdeado e negro
- **Objetivo:** Ouvir o enigma e responder corretamente (A=sim, C=não)

### Planeta do Deserto
- **Técnica VDP:** Dithering de paleta (gradiente de areia por dithering 2-tone) + particles
- **Personagem:** O Vento (VENTO) — personagem invisível, apenas efeito
- **Mecânica:** Caminhar contra o vento (hscroll reverso) para encontrar o poço
- **Cor dominante:** Ocre e céu azul claro
- **Objetivo:** Encontrar o poço no fundo do mapa

### Jardim das Rosas
- **Técnica VDP:** Sprites em grid (100 rosas via sprite engine) + palette morph
- **Personagem:** As Rosas (ROSAS)
- **Mecânica:** Andar entre as rosas percebendo que nenhuma é a sua
- **Cor dominante:** Rosa, verde e branco
- **Objetivo:** Chegar ao centro do jardim e sair

### O Poço no Deserto
- **Técnica VDP:** Zoom-in simulado (tiles redimensionados progresso) + echo de audio
- **Personagem:** O Aviador (AVIADOR)
- **Mecânica:** Puxar a corda do poço (pressionar C rhythmicamente)
- **Cor dominante:** Azul noite e estrelas brancas
- **Objetivo:** Puxar a água e compartilhar com o Aviador

### B-612 Retorno
- **Técnica VDP:** Todos os FX anteriores combinados — momento culminante
- **Personagem:** A Rosa (última despedida)
- **Mecânica:** Caminhar devagar até a Rosa — sem obstáculos
- **Cor dominante:** Dourado + gradiente para preto profundo
- **Objetivo:** Tocar a Rosa — créditos

---

## As 11 Viagens

### Travel A — Coragem (B-612 → Rei)
- **Tipo:** Pseudo-3D Space Harrier — floor line scroll com perspectiva
- **Virtude:** CORAGEM
- **Mecânica:** Desviar de asteroides enquanto avança

### Travel B — Determinação (Rei → Vaidoso)
- **Tipo:** Shmup horizontal
- **Virtude:** DETERMINACAO
- **Mecânica:** Avançar contra corrente de ventos/nebulosas

### Travel C — Humildade (Vaidoso → Bêbado)
- **Tipo:** Plataforma vertical (subir)
- **Virtude:** HUMILDADE
- **Mecânica:** Pular de estrela em estrela subindo

### Travel D — Compaixão (Bêbado → Contador)
- **Tipo:** Contemplativa (auto-scroll) — nenhuma ação requerida
- **Virtude:** COMPAIXAO
- **Mecânica:** Apenas observar as estrelas passarem

### Travel E — Confiança (Contador → Acendedor)
- **Tipo:** Plataforma com gravidade reversa
- **Virtude:** CONFIANCA
- **Mecânica:** Pular entre plataformas com gravidade invertendo

### Travel F — Perseverança (Acendedor → Geógrafo)
- **Tipo:** Shmup vertical (subir)
- **Virtude:** PERSEVERANCA
- **Mecânica:** Subir sem parar contra gravidade de meteoros

### Travel G — Criatividade (Geógrafo → Serpente)
- **Tipo:** Puzzle de tiles (girar fragmentos de caminho)
- **Virtude:** CRIATIVIDADE
- **Mecânica:** Montar rota entre 2 pontos

### Travel H — Esperança (Serpente → Deserto)
- **Tipo:** Top-down (visão superior) — caminhar em espiral
- **Virtude:** ESPERANCA
- **Mecânica:** Seguir trilha de luz

### Travel I — Amizade (Deserto → Jardim)
- **Tipo:** Plataforma lateral com helper NPC (raposa)
- **Virtude:** AMIZADE
- **Mecânica:** Raposa ajuda a alcançar plataformas altas

### Travel J — Fidelidade (Jardim → Poço)
- **Tipo:** Auto-scroll lento (contemplativo)
- **Virtude:** FIDELIDADE
- **Mecânica:** Manter a rosa imaginária "viva" pressionando A periodicamente

### Travel K — Sabedoria (Poço → B-612 Retorno)
- **Tipo:** Queda livre (descida em espiral)
- **Virtude:** SABEDORIA
- **Mecânica:** Navegar a queda de volta para casa

---

## Sistema Codex

- Desbloqueado ao completar cada planeta
- 12 entradas: uma por planeta
- Texto técnico-poético descrevendo o planeta e sua técnica VDP
- Acessado via START → CODEX no menu de pausa

---

## Cachecol (Assinatura Visual)

5 segmentos em spring chain:
- Posição: `scarf[i].x += (scarf[i-1].x - scarf[i].x) * damping`
- Damping: `FIX16(0.25)` por segmento
- Ondulação de vento: `sinFix16(frame * 4 + i * 16) >> 3`
- Cada segmento: sprite 8×8, paleta PAL1

---

## Painel de Status Inicial

| Eixo | Estado |
|------|--------|
| documentado | sim |
| implementado | sim (estrutura) |
| buildado | pendente |
| testado_em_emulador | pendente |
| validado_budget | pendente |
| placeholder | art (cenário 3) |
| agent_bootstrapped | pendente |
