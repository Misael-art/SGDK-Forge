# MegaDrive_DEV [![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/)

<sup>Workspace de desenvolvimento homebrew para Sega Mega Drive / Genesis usando **SGDK v2.11**</sup>

Workspace ativo focado em projetos **SGDK 211**. Material legado, rascunhos e acervo de referencia foram reorganizados em `archives/`.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows-orange.svg)](#)
[![SGDK](https://img.shields.io/badge/SGDK-v2.11-red.svg)](https://www.sgdk.de/)

## ✨ Recursos Principais

- 🚀 **Sistema de Build Inteligente**: Detecção automática de erros e correção de paletas
- 💎 **Golden Template [ELITE]**: Estrutura rígida focada em 60FPS, XGM2 e qualidade AAA para Mega Drive
- 🔧 **Infraestrutura Centralizada**: Scripts wrapper garantem consistência entre projetos
- 📚 **Material de Aprendizado**: Acervo de tutoriais e exemplos preservado em `archives/`
- 🎨 **Ferramentas de Desenvolvimento**: Editores de tiles, paletas, e conversores
- 🌐 **Rigor Metodológico**: Projetos focados em superar as referências históricas do hardware

## 📚 Navegação Rápida

- 🚀 [Comece Aqui](#quick-start) - Setup básico em 4 passos
- 📖 [Documentação](doc/README.md) - Índice central em `doc/`
- 🗂️ [Catálogo SGDK 211](SGDK_Engines/README.md) - Escolha por status: validado, pendente ou coleção
- 🎮 [Motores de Jogo](#motores-de-jogo-disponíveis) - Escolha seu motor
- 💡 [Dicas de Desenvolvimento](#dicas-de-desenvolvimento) - Melhores práticas
- 🔧 [Solução de Problemas](#solução-de-problemas-comuns) - FAQ técnico
- 📁 [Estrutura do Projeto](#estrutura) - Detalhes da organização

## Estrutura

```
MegaDrive_DEV/
├── assets/              # Recursos visuais (sprites, tilesets, backgrounds)
├── doc/                 # Documentação centralizada (Rigor AAA)
│   ├── logs/            # Logs de build e integração arquivados
│   └── [subpastas numeradas]
├── scripts/             # Scripts de automação (new-project.bat, setup-env.bat)
├── sdk/sgdk-2.11/       # SGDK local
├── tools/               # Wrapper central + ferramentas auxiliares
│   └── maintenance/     # Scripts avulsos e manutenção
├── SGDK_projects/       # Reservado para projetos autorais ativos
├── SGDK_Engines/        # Engines de elite e jogos ativos em SGDK 211
├── SGDK_templates/      # Onde vive o Golden Template (base-elite)
├── .tmp/                # Arquivos temporários
└── archives/            # Legado, referência e backups
```

Depois da faxina de `2026-03-14` e reorganização de `2026-04-02`:

- versões `SGDK 160/200`, exemplos antigos e projetos de teste foram arquivados
- a árvore ativa de `SGDK_Engines/` ficou concentrada nas entradas `SGDK 211`
- o Git passou a viver em `F:\\Projects\\MegaDrive_DEV`, sem mais repositório acidental na raiz de `F:\\`
- `scripts/` consolidada na raiz para acesso rápido; ferramentas auxiliares em `tools/maintenance/`
- `Assets and Sprites/` renomeado para `assets/` para limpeza
- `tmp/` renomeado para `.tmp/` para indicar temporário
- logs de build movidos para `doc/logs/` e arquivados em `archives/logs_build_2026/`
- arquivos soltos em `SGDK_Engines/` movidos para `tools/maintenance/`

## Quick Start

```bat
REM 1. Configurar ambiente (primeira vez apenas)
setup-env.bat

REM 2. Criar novo projeto a partir do template
new-project.bat meu-jogo-legal

REM 3. Navegar para o projeto e abrir no VSCode
cd SGDK_projects\meu-jogo-legal
code .

REM 4. Desenvolver seu jogo
REM    - Edite src/main.c e os recursos em res/
REM    - Use Ctrl+Shift+B para compilar no VSCode

REM 5. Testar no emulador
run.bat
```

**Dica:** O primeiro build pode demorar mais devido à compilação das bibliotecas SGDK.

## Pre-requisitos

- Windows 10/11
- Java Runtime (para rescomp do SGDK)
- Python 3 (opcional, para scripts de conversão)
- ImageMagick (opcional, para manipulação de sprites)
- VSCode com extensao C/C++ (recomendado)
- Emulador Mega Drive (BlastEm, Gens, Kega Fusion)

---

## 🎮 Motores de Jogo Disponíveis

| Motor | Tipo | Complexidade | Recursos |
|-------|------|-------------|----------|
| **BLAZE ENGINE** | Luta | Avançado | Combos, 4 personagens, sistema de energia, efeitos visuais |
| **HAMOOPIG** | Plataforma | Intermediário | Física básica, câmera, sistema de tiles |
| **GEN_Mega_Snake** | Arcade | Iniciante | Jogo Snake completo, score system |
| **State Machine** | RPG | Intermediário | Sistema de estados finitos, diálogo simples |
| **Super Monaco GP** | Corrida | Avançado | Scroll lateral, múltiplos níveis, AI básica |

---

## Padrão de projeto e scripts canônicos

Todos os projetos usam os **scripts-wrapper** localizados em `tools\sgdk_wrapper`.
Esses arquivos (`build.bat`, `clean.bat`, `run.bat`, `env.bat`) centralizam a lógica
para configurar o ambiente, verificar variáveis, compilar, limpar e executar ROMs.
Qualquer melhoria, correção de bugs ou nova funcionalidade é feita apenas nesses
arquivos, garantindo portabilidade e consistência entre projetos.

### Como funcionam os wrappers

- `env.bat` determina o caminho raiz (`MEGADRIVE_DEV_ROOT`), configura `GDK` e
  adiciona a toolchain ao `PATH`. Ele também verifica se a instalação do SGDK
  está presente e exibe avisos caso contrário.
- `build.bat` chama `env.bat`, testa se `GDK` está definido e executa `make`.
- `clean.bat` faz a mesma preparação antes de rodar `make clean`.
- `run.bat` garante que a ROM existe e que há um emulador configurado antes de
  lançar o jogo.

Os scripts são invocados pelos projetos usando caminhos relativos, por exemplo
no template:

```bat
@echo off
call "%~dp0..\..\tools\sgdk_wrapper\build.bat" "%~dp0"
```

Isso permite mover a pasta `MegaDrive_DEV` para outro drive sem quebrar nada.

### Manifesto estrutural e layouts suportados

Cada projeto canônico agora pode declarar sua estrutura em `.mddev/project.json`.
Com isso, o wrapper central consegue resolver automaticamente:

- `flat`: quando `src/`, `res/` e `inc/` estão na própria raiz do projeto
- `nested`: quando a raiz humana do projeto contém `README.md`, `doc/` e `.bat`,
  mas o SGDK root real está em uma subpasta

O padrão completo está documentado em `doc/CANONICAL_WORKTREE.md`.

### Uso de templates

A pasta `templates\project-template` contém o esqueleto mínimo para um
novo jogo: subpastas `src`, `res`, `inc`, a pasta `doc/`, o manifesto
`.mddev/project.json` e os wrappers citados acima. O comando `new-project.bat`
copia esse template para `SGDK_projects\<nome>` e já deixa tudo pronto para
compilar com `build.bat`. Nunca edite diretamente os scripts do projeto;
mantenha as alterações em `tools\sgdk_wrapper` para que todos os novos
projetos herdem o comportamento.

### Canonicalização em lote

O script `tools\sgdk_wrapper\canonicalize_projects.py` padroniza projetos já
existentes em `SGDK_Engines` e `SGDK_projects`, criando manifesto, documentação
pedagógica e arquivando wrappers legados, logs e binários soltos em
`archives\manual_review\`.

### Exemplo de criação de projeto

```bat
setup-env.bat          REM configura o ambiente do Windows (Java, Python, etc.)
new-project.bat jogo1  REM copia o template e cria o diretório
cd SGDK_projects\jogo1
build.bat              REM compila usando os wrappers centrais
run.bat                REM executa no emulador configurado
```

Essa abordagem dá centralidade ao desenvolvimento dos scripts, facilitando
adições futuras (como verificação de dependências, logs, fallback para
instaladores, etc.) e mantém a estrutura portátil e pedagogicamente explicada.

---

---

## 🌟 Avançados & Comunidade

Adições recentes de motores e protótipos de código aberto para estudo avançado:

| Nome | Pasta | Diferencial |
|------|-------|-------------|
| **PlatformerEngine Toolkit** | `SGDK_Engines/PlatformerEngine Toolkit...` | Colecao pedagogica com engine buildavel, pipeline de mapas e assets preservados |
| **RaycastingEngine** | `SGDK_Engines/RaycastingEngine...` | Renderização 3D (estilo Doom/Wolf3D) no hardware original |
| **MegaDriving** | `SGDK_Engines/MegaDriving...` | Pseudo-3D road scrolling e efeitos de perspectiva |
| **PlatformerStudio**| `SGDK_Engines/PlatformerStudio...` | Ferramenta visual de autoria para SGDK |
| **SimpleGameStates**| `SGDK_templates/SimpleGameStates...` | Template de lógica modular com FSM |

> [!TIP]
> Use estes repositórios para estudar técnicas de otimização extrema e arquiteturas de código profissionais.

---

## 💡 Dicas de Desenvolvimento

### Para Iniciantes
- Comece com o template básico (`templates/project-template`)
- Consulte `archives/cleanup_20260314-190609/reference/examples/` para estudar os exemplos legados
- Crie novos projetos em `SGDK_projects/` para manter a árvore ativa limpa

### Para Desenvolvedores Experientes
- Explore o `SGDK_Engines/BLAZE_ENGINE` para jogos complexos
- Utilize os scripts em `tools/gen-scripts` para automação
- Consulte a documentação do SGDK para recursos avançados

### Melhores Práticas
- Nunca modifique os scripts dos projetos diretamente
- Mantenha todas as alterações em `tools/sgdk_wrapper`
- Use o sistema de controle de versão para seus projetos

---

## 🔧 Solução de Problemas Comuns

### Erros de Build
- **"transparent pixel"**: O sistema corrre automaticamente usando ImageMagick
- **GDK não definido**: Execute `setup-env.bat` e reinicie o terminal
- **Bibliotecas não encontradas**: Verifique se o SGDK está instalado corretamente

### Problemas de Execução
- **Emulador não encontrado**: Baixe e configure um emulador (BlastEm, Gens, Kega Fusion)
- **ROM não gerada**: Verifique se o build foi concluído sem erros
- **Performance issues**: Reduza o número de sprites ou otimize as colisões

---
