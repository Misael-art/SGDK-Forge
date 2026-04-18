# 📍 CORE Level - Essencial (Nível 1)

## O Que é CORE?

CORE é a **versão minimalista** de um plataformador para Mega Drive. Contém apenas os conceitos essenciais:
- Sprite renderizado
- Detecção de colisão básica
- Entrada de controle (directional pad)
- Game loop fundamental (init → update → render → repeat)

**Objetivo**: Entender os blocos básicos sem ruído.

---

## Conceitos-Chave Ensinados

1. **Sprite Rendering** — Como desenhar um jogador na tela
2. **Game Loop** — Como estruturar init/update/render/VBlank
3. **Input Handling** — Como ler o controle (joy_readJoypad)
4. **Collision Detection** — Detecção simples (caixas AABB)
5. **Positioning** — Sistema de coordenadas X/Y

---

## Estrutura

```
core/
├── src/main.c
│   ├── main()         ← Ponto de entrada
│   ├── init()         ← Inicializa jogo
│   ├── update()       ← Lógica por frame
│   ├── render()       ← Desenha na tela
│   └── VBlank ISR     ← Sincroniza com VBlank
├── inc/
│   └── types.h        ← Tipos de dados básicos
├── res/
│   └── resources.rc   ← Assets (sprite, paleta)
├── doc/               ← Documentação
└── examples/
    └── 01_hello_platformer/  ← Exemplo simples
```

---

## Como Usar CORE

### 1. Compile
```bash
cd core
build.bat
```

### 2. Rode no Emulador
```bash
run.bat
```

### 3. Estude o Código
Abra `src/main.c` e leia os comentários (código didático).

### 4. Modifique e Teste
- Mude a cor do sprite
- Mude a velocidade
- Recompile: `rebuild.bat`

---

## Próximos Passos Após Dominar CORE

❌ Não está pronto
- [ ] O sprite se move, mas não há gravidade
- [ ] Sem inimigos
- [ ] Sem score
- [ ] Sem múltiplos níveis

✅ Está pronto para → **STANDARD Level**

Quando se sentir confortável, vá para `standard/doc/README.md`.

---

## Troubleshooting

**Erro: "ROM não compila"**
→ Verifique se `tools/sgdk_wrapper/` existe e está acessível

**Erro: "Sprite não aparece"**
→ Verifique `res/resources.rc` — paleta carregada?

**Emulador não abre**
→ Verifique `tools/emuladores/BlastEm.exe`

Para mais, veja `doc/TROUBLESHOOTING.md` na raiz.

---

## Tips & Tricks

- **VBlank Safety**: Nunca compile durante VBlank (código no callback ISR)
- **Fix16**: Use `fix16_t` para posições, não `float`
- **Palette**: Máximo 64 cores por paleta (Mega Drive hardware)
- **VRAM**: Limited a ~64KB; não aloque sprites sem medida

---

**Tempo estimado**: 2-4 horas para compreender completamente.

**Próxima etapa**: Leia `reference/UPSTREAM_INFO.md` para entender a evolução do projeto.
