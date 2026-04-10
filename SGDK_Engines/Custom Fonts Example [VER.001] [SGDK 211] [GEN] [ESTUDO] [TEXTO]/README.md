# Custom Fonts Example [VER.001] [SGDK 211] [GEN] [ESTUDO] [TEXTO]

Bem-vindo ao desenvolvimento homebrew para **Sega Mega Drive / Genesis**!
Este template foi criado para que voce comece a programar seu jogo de forma
rapida e organizada, usando o **SGDK v2.11**.

---

## Estrutura do Projeto

```
meu-projeto/
├── .mddev/                 # Manifesto estrutural consumido pelo wrapper central
│   └── project.json        # Diz onde esta o SGDK root real do projeto
│
├── doc/                    # Documentacao tecnica e guias pedagogicos
│   ├── README.md           #   Indice da documentacao
│   ├── 01-visao-geral.md
│   ├── 02-build-wrapper.md
│   ├── 03-arquitetura.md
│   ├── 04-recursos-e-pipeline.md
│   ├── 05-guia-de-desenvolvimento.md
│   └── 06-debug-migracao.md
│
├── src/                    # Codigo-fonte C do jogo
│   └── main.c              #   Ponto de entrada - comece editando aqui
│
├── res/                    # Recursos para o ResComp (compilador de recursos)
│   └── resources.res       #   Definicoes de sprites, imagens, sons e musicas
│
├── inc/                    # Headers personalizados (.h) do seu projeto
│                           #   Crie aqui seus arquivos .h quando necessario
│
├── out/                    # Saida da compilacao (gerado automaticamente)
│   └── rom.bin             #   Sua ROM - o arquivo que roda no emulador!
│
├── .vscode/                # Configuracoes do Visual Studio Code
│   ├── c_cpp_properties.json  # IntelliSense para headers do SGDK
│   ├── settings.json          # Associacoes de arquivo
│   └── tasks.json             # Atalhos: Ctrl+Shift+B = Build
│
├── build.bat               # Compilar o projeto (delega ao wrapper central)
├── clean.bat               # Limpar artefatos de compilacao
├── run.bat                 # Executar ROM no emulador (compila se necessario)
├── rebuild.bat             # Limpar + Compilar de uma vez
├── .gitignore              # Ignora arquivos gerados (out/, *.bin, etc.)
└── README.md               # Este arquivo - documentacao do seu projeto
```

### O que cada pasta faz?

| Pasta | Finalidade | Voce edita? |
|-------|-----------|-------------|
| `src/` | Codigo C do jogo (logica, input, colisoes) | Sim |
| `res/` | Recursos visuais e sonoros (.png, .wav, .vgm) e seus .res | Sim |
| `inc/` | Headers compartilhados entre seus arquivos .c | Sim |
| `out/` | ROM compilada e arquivos intermediarios | Nao (gerado) |
| `doc/` | Documentacao tecnica e guias do projeto | Sim |
| `.mddev/` | Manifesto estrutural para o wrapper central | Raramente |
| `.vscode/` | Configuracao do editor | Raramente |

---

## Como Comecar

### 1. Compilar o projeto

```bat
build.bat
```
Ou no VSCode: **Ctrl+Shift+B** (atalho padrao).

### 2. Rodar no emulador

```bat
run.bat
```
Se a ROM nao existir ou estiver desatualizada, o script compila automaticamente antes de executar.

### 3. Limpar e recompilar

```bat
rebuild.bat
```

### 4. Ler a documentacao tecnica

Comece por `doc/README.md` e depois siga a ordem sugerida.

---

## Fluxo de Desenvolvimento

```
 Editar codigo    Compilar ROM      Testar no emulador
 ┌──────────┐    ┌──────────┐      ┌──────────────────┐
 │ src/*.c   │───>│ build.bat │────>│     run.bat       │
 │ res/*.res │    │ (SGDK)   │     │  (abre emulador)  │
 └──────────┘    └──────────┘      └──────────────────┘
       │              │                     │
       └──────────────┴─────────────────────┘
                   Repita!
```

### Ciclo tipico:

1. Edite `src/main.c` - adicione sua logica de jogo
2. Adicione graficos em `res/` e declare no `resources.res`
3. Compile com `build.bat` ou Ctrl+Shift+B
4. Teste com `run.bat`
5. Repita ate ficar satisfeito!

---

## Adicionando Recursos (Graficos, Sons, Musica)

### Sprites (personagens, inimigos, itens)

1. Crie uma imagem PNG com fundo transparente (magenta #FF00FF)
2. Tamanho deve ser multiplo de 8 pixels (ex: 32x32, 48x64)
3. Maximo 16 cores por paleta (incluindo transparencia)
4. Adicione no `res/resources.res`:

```
SPRITE spr_heroi "gfx/heroi.png" 4 4 BEST 6
```
- `4 4` = tamanho em tiles (4x8=32 pixels cada dimensao)
- `BEST` = melhor compressao
- `6` = frames de animacao

### Fundos e cenarios

```
IMAGE bg_fase1 "gfx/fase1.png" BEST
```

### Musica e efeitos sonoros

```
XGM2 mus_tema    "sfx/tema.vgm"
WAV  sfx_pulo    "sfx/pulo.wav" XGM2
```

### Usando no codigo C

```c
#include "resources.h"  // Gerado automaticamente pelo ResComp

// Carregar paleta
PAL_setPalette(PAL0, bg_fase1.palette->data, DMA);

// Desenhar fundo
VDP_drawImageEx(BG_A, &bg_fase1, TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, ind),
                0, 0, FALSE, TRUE);

// Criar sprite
SPR_addSprite(&spr_heroi, x, y, TILE_ATTR(PAL1, FALSE, FALSE, FALSE));
```

---

## Conceitos Importantes do Mega Drive

### Resolucao e Tiles

- Tela: **320x224** pixels (40x28 tiles)
- 1 tile = **8x8** pixels
- Maximo 64 tiles por sprite (ex: 8x8 tiles = 64x64 pixels)

### Paletas de Cores

- **4 paletas** de 16 cores cada (PAL0, PAL1, PAL2, PAL3)
- Total: **64 cores simultaneas** na tela
- Indice 0 de cada paleta = transparencia

### Sprites

- Maximo **80 sprites** simultaneos na tela
- Maximo **20 sprites** por scanline (linha horizontal)
- VDP usa **16 sprites internos** por tile de sprite complexo

### Planos de Fundo

- **2 planos**: BG_A (frente) e BG_B (fundo)
- Scroll independente (horizontal e vertical)
- Cada plano pode ter ate 64x64 tiles

### Game Loop a 60fps

```c
while (TRUE)
{
    // 1. Ler controles
    u16 joy = JOY_readJoypad(JOY_1);

    // 2. Atualizar logica
    if (joy & BUTTON_RIGHT) x += 2;
    if (joy & BUTTON_A)     pular();

    // 3. Atualizar graficos
    SPR_setPosition(sprite, x, y);
    SPR_update();

    // 4. Sincronizar (OBRIGATORIO - sempre por ultimo!)
    SYS_doVBlankProcess();
}
```

---

## Regras do Projeto

1. **Nunca modifique** `build.bat`, `clean.bat`, `run.bat` ou `rebuild.bat`
   - Eles delegam ao sistema centralizado em `tools/sgdk_wrapper/`
   - Melhorias no build sao feitas la e todos os projetos herdam

2. **Nao remova** `.mddev/project.json`
   - Ele informa ao wrapper onde esta o SGDK root do projeto
   - Se a estrutura mudar, atualize o manifesto em vez de duplicar scripts

3. **Codigo fonte** vai em `src/` e headers em `inc/`

4. **Recursos** (imagens, sons) vao em `res/` com definicoes em `.res`

5. **Documentacao tecnica** vai em `doc/`

6. **Nomenclatura de diretorio** segue o padrao:
   `NOME [VER.XXX] [SGDK 211] [GEN] [TIPO] [GENERO]`

---

## Solucao de Problemas

| Erro | Causa | Solucao |
|------|-------|---------|
| `GDK nao definido` | Ambiente nao configurado | Execute `setup-env.bat` na raiz |
| `transparent pixel` | Paleta PNG incorreta | O build corrige automaticamente |
| `ROM not found` | Build falhou | Verifique erros no terminal |
| `No emulator found` | Emulador nao detectado | Coloque em `tools/emuladores/` |
| `Java not found` | ResComp precisa de Java | Instale Java JRE/JDK |

---

## Links Uteis

- [SGDK Wiki](https://github.com/Stephane-D/SGDK/wiki) - Documentacao oficial
- [Mega Drive Technical Manual](https://segaretro.org/Sega_Mega_Drive/Technical_specifications)
- `doc/` na raiz do MegaDrive_DEV - Documentacao do workspace
- `doc/PADRAO_NOMENCLATURA.md` - Padrao de nomes de diretorio
