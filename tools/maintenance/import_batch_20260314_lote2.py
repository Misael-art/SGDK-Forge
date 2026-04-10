from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SGDK_ENGINES = WORKSPACE_ROOT / "SGDK_Engines"
ARCHIVE_BATCH = WORKSPACE_ROOT / "archives" / "upstream_imports_20260314-213429"
LOCAL_SALVAGE = ARCHIVE_BATCH / "local_salvage_lote2"
REPORT_PATH = WORKSPACE_ROOT / "doc" / "INTEGRACAO_IMPORTS_20260314_LOTE2.json"
WRAPPER_ROOT = WORKSPACE_ROOT / "tools" / "sgdk_wrapper"

ROOT_DROP_DIRS = {
    ".git",
    ".github",
    ".vscode",
    ".idea",
    ".vs",
    "__pycache__",
    "out",
    "release",
    "screenshot",
    "screenshots",
    "temp",
    "doc",
    "docs",
    "tools",
    "scripts",
    "assets",
    "media",
    "py",
    "js",
    "lib",
}
ROOT_DROP_FILES = {
    ".editorconfig",
    ".gitattributes",
    ".gitignore",
    "gens.cfg",
    "language.dat",
    "package.json",
    "package-lock.json",
    "index.js",
    "env.bat",
    "jenkinsfile",
}
ROOT_DROP_SUFFIXES = {
    ".md",
    ".txt",
    ".bat",
    ".sh",
    ".cbp",
    ".layout",
    ".depend",
    ".workspace",
    ".nfo",
    ".zip",
    ".cfg",
    ".png",
    ".jpg",
    ".jpeg",
    ".svg",
    ".gif",
    ".mp4",
    ".cscope_file_list",
}
ROOT_DROP_PREFIXES = ("license", "copying", "readme", "makefile")
GITIGNORE_CONTENT = (
    "out/\n"
    "build_output.log\n"
    "build_debug.log\n"
    "validation_report.json\n"
    "hs_err_pid*.log\n"
    "replay_pid*.log\n"
)


@dataclass(frozen=True)
class ImportProject:
    source: Path
    destination: str
    source_url: str
    notes: str
    platform: str = "GEN"


@dataclass(frozen=True)
class ImportCollection:
    destination: str
    source_url: str
    category: str
    notes: str
    source_paths: tuple[Path, ...]
    summary_lines: tuple[str, ...] = field(default_factory=tuple)
    platform: str = "GEN"


PROJECTS = [
    ImportProject(
        source=ARCHIVE_BATCH / "opeth-mega-drive",
        destination="Opeth Music Cartridge [VER.001] [SGDK 211] [GEN] [ESTUDO] [AUDIO]",
        source_url="https://github.com/Flicksie/opeth-mega-drive",
        notes="Cartucho musical em SGDK dedicado ao repertorio do Opeth.",
    ),
    ImportProject(
        source=ARCHIVE_BATCH / "Tuto_SGDK_Vigilante",
        destination="Vigilante Tutorial [VER.001] [SGDK 211] [GEN] [ESTUDO] [BRIGA DE RUA]",
        source_url="https://github.com/fabiof17/Tuto_SGDK_Vigilante",
        notes="Estudo em SGDK inspirado em Vigilante para ensinar base de beat'em up.",
    ),
    ImportProject(
        source=ARCHIVE_BATCH / "Mega-Car-Wars",
        destination="Mega Car Wars [VER.001] [SGDK 211] [GEN] [GAME] [COMBATE VEICULAR]",
        source_url="https://github.com/realbrucest/Mega-Car-Wars",
        notes="Jogo isometrico de corrida e combate veicular para Mega Drive.",
    ),
    ImportProject(
        source=ARCHIVE_BATCH / "FIREBRAWL",
        destination="FireBrawl [VER.001] [SGDK 211] [GEN] [GAME] [BRIGA DE RUA]",
        source_url="https://github.com/jerellsworth/FIREBRAWL",
        notes="Jogo em SGDK focado em combate corpo a corpo.",
    ),
    ImportProject(
        source=ARCHIVE_BATCH / "BoingSGDK",
        destination="Boing MD [VER.001] [SGDK 211] [GEN] [GAME] [ARCADE]",
        source_url="https://github.com/makeclassicgames/BoingSGDK",
        notes="Port SGDK de Boing como jogo arcade completo e pedagogico.",
    ),
    ImportProject(
        source=ARCHIVE_BATCH / "SGDK_3D" / "3D",
        destination="SGDK 3D Demo [VER.001] [SGDK 211] [GEN] [ESTUDO] [3D]",
        source_url="https://github.com/massie0414/SGDK_3D",
        notes="Experimento 3D em SGDK preservado como estudo tecnico.",
    ),
    ImportProject(
        source=ARCHIVE_BATCH / "ggj2020_tut_7star" / "sgdk_7star",
        destination="7 Star Jam Demo [VER.001] [SGDK 211] [GEN] [ESTUDO] [JAM]",
        source_url="https://github.com/massie0414/ggj2020_tut_7star",
        notes="Projeto jam em SGDK preservado como estudo curto e auto-contido.",
    ),
    ImportProject(
        source=ARCHIVE_BATCH / "pigsy-manual-camera" / "Super basic example of uploading two large background maps, changing camera coordinates manually (SGDK)",
        destination="Manual Camera Maps [VER.001] [SGDK 211] [GEN] [ESTUDO] [CAMERA]",
        source_url="https://github.com/pigsySGDK/Super-basic-example-of-uploading-two-large-background-maps-changing-camera-coordinates-manually-SG",
        notes="Exemplo minimo de troca manual de mapas grandes com controle de camera.",
    ),
    ImportProject(
        source=ARCHIVE_BATCH / "GG-Shinobi-Remake-for-Sega-Megadrive" / "GG Shinobi 1-1 - no collisions, no line scrolling, enemy sprites and some AI added (SGDK)",
        destination="Shinobi AI Test [VER.001] [SGDK 211] [GEN] [ESTUDO] [PLATAFORMA]",
        source_url="https://github.com/pigsySGDK/GG-Shinobi-Remake-for-Sega-Megadrive",
        notes="Versao de estudo do Shinobi com IA e sprites de inimigos.",
    ),
    ImportProject(
        source=ARCHIVE_BATCH / "GG-Shinobi-Remake-for-Sega-Megadrive" / "GG Shinobi 1-1 scrolling test - single screen line scroll and moving sprite (SGDK)",
        destination="Shinobi Scroll Test [VER.001] [SGDK 211] [GEN] [ESTUDO] [SCROLL]",
        source_url="https://github.com/pigsySGDK/GG-Shinobi-Remake-for-Sega-Megadrive",
        notes="Teste de line scroll inspirado em Shinobi para estudo de camera e movimento.",
    ),
    ImportProject(
        source=ARCHIVE_BATCH / "SGDK-level-collision-test" / "Tile collision map test - trying with gargoyle platform section",
        destination="Gargoyle Collision Test [VER.001] [SGDK 211] [GEN] [ESTUDO] [COLISAO]",
        source_url="https://github.com/pigsySGDK/SGDK-level-collision-test",
        notes="Teste de colisao de tiles focado em plataforma estilo Gargoyle.",
    ),
    ImportProject(
        source=ARCHIVE_BATCH / "MegaDriveBreakout",
        destination="Mega Drive Breakout [VER.001] [SGDK 211] [GEN] [GAME] [ARCADE]",
        source_url="https://github.com/theshaneobrien/MegaDriveBreakout",
        notes="Implementacao de Breakout em SGDK usada como jogo e estudo introdutorio.",
    ),
    ImportProject(
        source=ARCHIVE_BATCH / "TownQuest",
        destination="Town Quest [VER.001] [SGDK 211] [GEN] [GAME] [RPG]",
        source_url="https://github.com/sixteenbits/TownQuest",
        notes="Jogo jam com estrutura de aventura e elementos de RPG.",
    ),
    ImportProject(
        source=ARCHIVE_BATCH / "GoblinSGDK",
        destination="Goblin SGDK [VER.001] [SGDK 211] [GEN] [GAME] [AVENTURA]",
        source_url="https://github.com/bearmade/GoblinSGDK",
        notes="Projeto de aventura em SGDK com pipeline proprio de assets.",
    ),
    ImportProject(
        source=ARCHIVE_BATCH / "sgdk-custom-fonts",
        destination="Custom Fonts Example [VER.001] [SGDK 211] [GEN] [ESTUDO] [TEXTO]",
        source_url="https://github.com/axmandm/sgdk-custom-fonts",
        notes="Exemplo alternativo de fontes customizadas preservado separadamente do estudo principal.",
    ),
    ImportProject(
        source=ARCHIVE_BATCH / "rpg-text",
        destination="RPG Text [VER.001] [SGDK 211] [GEN] [TEMPLATE] [TEXTO]",
        source_url="https://github.com/tryphon77/rpg-text",
        notes="Base de texto estilo RPG reutilizavel como template de interface.",
    ),
    ImportProject(
        source=ARCHIVE_BATCH / "tidytext",
        destination="TidyText [VER.001] [SGDK 211] [GEN] [TEMPLATE] [TEXTO]",
        source_url="https://github.com/garrettjwilke/tidytext",
        notes="Sistema de kerning para texto em SGDK adaptado como template de UI.",
    ),
    ImportProject(
        source=ARCHIVE_BATCH / "sgdk-space-invaders",
        destination="Space Invaders SGDK [VER.001] [SGDK 211] [GEN] [GAME] [SHMUP]",
        source_url="https://github.com/axmandm/sgdk-space-invaders",
        notes="Clone em andamento de Space Invaders preservado como base de shmup.",
    ),
    ImportProject(
        source=ARCHIVE_BATCH / "sgdkplaformer2",
        destination="Platformer 2 [VER.001] [SGDK 211] [GEN] [ESTUDO] [PLATAFORMA]",
        source_url="https://github.com/makeclassicgames/sgdkplaformer2",
        notes="Estudo de plataforma com camera, slopes e boas praticas de SGDK.",
    ),
    ImportProject(
        source=ARCHIVE_BATCH / "exampleSGDKPlatformer",
        destination="Example Platformer [VER.001] [SGDK 211] [GEN] [TEMPLATE] [PLATAFORMA]",
        source_url="https://github.com/makeclassicgames/exampleSGDKPlatformer",
        notes="Template pedagogico de jogo de plataforma para reuso rapido.",
    ),
    ImportProject(
        source=ARCHIVE_BATCH / "CroakusPocusSGDK" / "CroakusPocus-MD",
        destination="Croakus Pocus [VER.001] [SGDK 211] [GEN] [ESTUDO] [CENARIO]",
        source_url="https://github.com/bearmade/CroakusPocusSGDK",
        notes="Demonstracao de geracao procedural de tilemap em Mega Drive.",
    ),
    ImportProject(
        source=ARCHIVE_BATCH / "sgdk-bitmap-sine-wave",
        destination="Bitmap Sine Wave [VER.001] [SGDK 211] [GEN] [ESTUDO] [GRAFICOS]",
        source_url="https://github.com/axmandm/sgdk-bitmap-sine-wave",
        notes="Experimento grafico de senoides em bitmap para SGDK.",
    ),
    ImportProject(
        source=ARCHIVE_BATCH / "raycasting_anael",
        destination="Raycasting Anael [VER.001] [SGDK 211] [GEN] [ESTUDO] [3D]",
        source_url="https://github.com/fabri1983/raycasting_anael",
        notes="Port e expansao do demo de raycasting do SGDK para estudo 3D.",
    ),
    ImportProject(
        source=ARCHIVE_BATCH / "sonic_sms",
        destination="Sonic SMS Prototype [VER.001] [SGDK 211] [SMS] [ESTUDO] [PLATAFORMA]",
        source_url="https://github.com/Vinicius-Correa/sonic_sms",
        notes="Prototipo com foco em plataforma; preservado com tag SMS para orientar consulta.",
        platform="SMS",
    ),
    ImportProject(
        source=ARCHIVE_BATCH / "SGDK-Megapong-Expanded",
        destination="Mega Pong Expanded [VER.001] [SGDK 211] [GEN] [GAME] [ARCADE]",
        source_url="https://github.com/mrglaster/SGDK-Megapong-Expanded",
        notes="Versao expandida do tutorial de Pong, atualizada para SGDK recente.",
    ),
    ImportProject(
        source=ARCHIVE_BATCH / "Metal-Slug-Warfare-Demo--Megadrive-",
        destination="Metal Slug Warfare Demo [VER.001] [SGDK 211] [GEN] [ESTUDO] [RUN AND GUN]",
        source_url="https://github.com/StudioVetea/Metal-Slug-Warfare-Demo--Megadrive-",
        notes="Demo antiga de run and gun preservada como estudo tecnico.",
    ),
    ImportProject(
        source=ARCHIVE_BATCH / "SGDKCodeForFMV",
        destination="FMV Code Sample [VER.001] [SGDK 211] [GEN] [ESTUDO] [VIDEO]",
        source_url="https://github.com/matthewbennion/SGDKCodeForFMV",
        notes="Codigo de referencia para reproducao de sequencias em estilo FMV.",
    ),
    ImportProject(
        source=ARCHIVE_BATCH / "Penguin-World",
        destination="Penguin World [VER.001] [SGDK 211] [GEN] [GAME] [PLATAFORMA]",
        source_url="https://github.com/alicesim1/Penguin-World",
        notes="Projeto indie em desenvolvimento com identidade propria de plataforma.",
    ),
    ImportProject(
        source=ARCHIVE_BATCH / "TetrisMD",
        destination="Tetris MD [VER.001] [SGDK 211] [GEN] [GAME] [PUZZLE]",
        source_url="https://github.com/NeroJin/TetrisMD",
        notes="Implementacao caseira de Tetris em SGDK.",
    ),
    ImportProject(
        source=ARCHIVE_BATCH / "SGDK_2colors",
        destination="Two Colors Demo [VER.001] [SGDK 211] [GEN] [ESTUDO] [GRAFICOS]",
        source_url="https://github.com/anael-seghezzi/SGDK_2colors",
        notes="Experimento visual de duas cores preservado como estudo de graficos.",
    ),
    ImportProject(
        source=ARCHIVE_BATCH / "MegaMetroid",
        destination="Mega Metroid [VER.001] [SGDK 211] [GEN] [GAME] [PLATAFORMA]",
        source_url="https://github.com/dougkusanagi/MegaMetroid",
        notes="Projeto de fan game inspirado em Super Metroid.",
    ),
    ImportProject(
        source=ARCHIVE_BATCH / "MegaPong",
        destination="Mega Pong Classic [VER.001] [SGDK 211] [GEN] [GAME] [ARCADE]",
        source_url="https://github.com/And-0/MegaPong",
        notes="Versao classica e minima de Pong em SGDK.",
    ),
    ImportProject(
        source=ARCHIVE_BATCH / "demo-Masiaka" / "src",
        destination="Masiaka Demo [VER.001] [SGDK 211] [GEN] [ESTUDO] [DEMO]",
        source_url="https://github.com/ResistanceVault/demo-Masiaka",
        notes="Demo de efeitos e apresentacao para Mega Drive, preservada como estudo tecnico.",
    ),
    ImportProject(
        source=ARCHIVE_BATCH / "KleleAtoms-MD",
        destination="KleleAtoms MD [VER.001] [SGDK 211] [GEN] [GAME] [PUZZLE]",
        source_url="https://github.com/Nightwolf-47/KleleAtoms-MD",
        notes="Port para Mega Drive de um puzzle competitivo focado em explosoes em cadeia.",
    ),
    ImportProject(
        source=ARCHIVE_BATCH / "Mega-Tetris-for-SEGA-Genesis",
        destination="Mega Tetris [VER.0.8.2] [SGDK 211] [GEN] [GAME] [PUZZLE]",
        source_url="https://github.com/kikutano/Mega-Tetris-for-SEGA-Genesis",
        notes="Projeto de Tetris com versao declarada 0.8.2 no README do upstream.",
    ),
    ImportProject(
        source=ARCHIVE_BATCH / "MDSDRV" / "sample" / "sgdk",
        destination="MDSDRV SGDK Sample [VER.001] [SGDK 211] [GEN] [ESTUDO] [AUDIO]",
        source_url="https://github.com/superctr/MDSDRV",
        notes="Sample SGDK do driver MDSDRV preservado como entrada buildavel.",
    ),
    ImportProject(
        source=ARCHIVE_BATCH / "sgdk-video-player" / "experiment",
        destination="Video Player Experiment [VER.001] [SGDK 211] [GEN] [ESTUDO] [VIDEO]",
        source_url="https://github.com/haroldo-ok/sgdk-video-player",
        notes="Experimento SGDK do pipeline de video player.",
    ),
    ImportProject(
        source=SGDK_ENGINES / "SELECT_PLAYER",
        destination="Select Player Screen [VER.001] [SGDK 211] [GEN] [TEMPLATE] [MENU]",
        source_url="local://SGDK_Engines/SELECT_PLAYER",
        notes="Tela de selecao de personagem reaproveitavel como template de menu.",
    ),
    ImportProject(
        source=SGDK_ENGINES / "Tutorial Ataque - Parte 2",
        destination="Attack Tutorial Part 2 [VER.001] [SGDK 211] [GEN] [ESTUDO] [COMBATE]",
        source_url="local://SGDK_Engines/Tutorial Ataque - Parte 2",
        notes="Estudo local de ataque e colisao preservado como modulo pratico.",
    ),
    ImportProject(
        source=SGDK_ENGINES / "Scroll" / "Line Scroll",
        destination="Line Scroll Basics [VER.001] [SGDK 211] [GEN] [ESTUDO] [SCROLL]",
        source_url="local://SGDK_Engines/Scroll/Line Scroll",
        notes="Exemplo local focado em line scroll.",
    ),
    ImportProject(
        source=SGDK_ENGINES / "Scroll" / "Plane Scroll",
        destination="Plane Scroll Basics [VER.001] [SGDK 211] [GEN] [ESTUDO] [SCROLL]",
        source_url="local://SGDK_Engines/Scroll/Plane Scroll",
        notes="Exemplo local focado em plane scroll.",
    ),
    ImportProject(
        source=SGDK_ENGINES / "Scroll" / "Tile Scroll",
        destination="Tile Scroll Basics [VER.001] [SGDK 211] [GEN] [ESTUDO] [SCROLL]",
        source_url="local://SGDK_Engines/Scroll/Tile Scroll",
        notes="Exemplo local focado em tile scroll.",
    ),
]

COLLECTIONS = [
    ImportCollection(
        destination="MDSDRV Toolkit [VER.001] [SGDK 211] [GEN] [COLLECTION] [AUDIO]",
        source_url="https://github.com/superctr/MDSDRV",
        category="AUDIO",
        notes="Colecao canonica do driver MDSDRV com documentacao, ferramentas e samples preservados no archive.",
        source_paths=(ARCHIVE_BATCH / "MDSDRV",),
        summary_lines=(
            "Driver de audio para Mega Drive/Genesis.",
            "Use a entrada buildavel `MDSDRV SGDK Sample ...` para compilar um exemplo SGDK real.",
        ),
    ),
    ImportCollection(
        destination="SGDK Video Player Toolkit [VER.001] [SGDK 211] [GEN] [COLLECTION] [VIDEO]",
        source_url="https://github.com/haroldo-ok/sgdk-video-player",
        category="VIDEO",
        notes="Colecao canonica do pipeline de video player com experimentos SGDK e conversores host preservados em archive.",
        source_paths=(ARCHIVE_BATCH / "sgdk-video-player",),
        summary_lines=(
            "Pipeline misto com codigo SGDK e ferramentas Node para conversao de video.",
            "Use a entrada buildavel `Video Player Experiment ...` para estudar o lado SGDK.",
        ),
    ),
    ImportCollection(
        destination="SGDK Rocks Samples [VER.001] [SGDK 211] [GEN] [COLLECTION] [TUTORIAIS]",
        source_url="https://github.com/radioation/SGDKRocks",
        category="TUTORIAIS",
        notes="Colecao de exemplos SGDK atualizados para 2.11, preservada como trilha de estudo.",
        source_paths=(ARCHIVE_BATCH / "SGDKRocks",),
        summary_lines=(
            "Contem varios exemplos independentes e uma versao jogavel de Asteroids.",
        ),
    ),
    ImportCollection(
        destination="Under-Prog Tutorials [VER.001] [SGDK 211] [GEN] [COLLECTION] [TUTORIAIS]",
        source_url="https://github.com/bolon667/sgdkTutorialsCode",
        category="TUTORIAIS",
        notes="Colecao de tutoriais Under-Prog preservada para consulta estruturada.",
        source_paths=(ARCHIVE_BATCH / "sgdkTutorialsCode",),
        summary_lines=(
            "Pack com dezenas de licoes independentes em SGDK.",
        ),
    ),
    ImportCollection(
        destination="Aventuras en Megadrive Lessons [VER.001] [SGDK 211] [GEN] [COLLECTION] [TUTORIAIS]",
        source_url="https://github.com/danibusvlc/aventuras-en-megadrive",
        category="TUTORIAIS",
        notes="Curso em espanhol com varias licoes SGDK, preservado como acervo pedagogico.",
        source_paths=(ARCHIVE_BATCH / "aventuras-en-megadrive",),
        summary_lines=(
            "Colecao de licoes incremental para quem quer estudar SGDK passo a passo.",
        ),
    ),
    ImportCollection(
        destination="SGDK Assets Pack [VER.001] [SGDK 211] [GEN] [COLLECTION] [ASSETS]",
        source_url="https://github.com/ResistanceVault/sgdk-assets",
        category="ASSETS",
        notes="Acervo de assets e recursos auxiliares preservado como referencia.",
        source_paths=(ARCHIVE_BATCH / "sgdk-assets",),
        summary_lines=(
            "Nao representa uma ROM unica; serve como repositorio de recursos reutilizaveis.",
        ),
    ),
    ImportCollection(
        destination="libNG Reference [VER.001] [SGDK 211] [GEN] [COLLECTION] [BIBLIOTECA]",
        source_url="https://github.com/TheHpman/libNG",
        category="BIBLIOTECA",
        notes="Referencia adjacente baseada em SGDK para Neo Geo, mantida fora da area de projetos buildaveis de Mega Drive.",
        source_paths=(ARCHIVE_BATCH / "libNG",),
        summary_lines=(
            "Biblioteca para Neo Geo com estilo SGDK; mantida como referencia, nao como projeto SGDK ativo.",
        ),
    ),
    ImportCollection(
        destination="Tutorial 09 Sprite Assets [VER.001] [SGDK 211] [GEN] [COLLECTION] [SPRITES]",
        source_url="local://SGDK_Engines/Tutorial 09",
        category="SPRITES",
        notes="Recursos locais de sprite preservados como colecao de referencia.",
        source_paths=(SGDK_ENGINES / "Tutorial 09",),
    ),
    ImportCollection(
        destination="Animation Manager Assets [VER.001] [SGDK 211] [GEN] [COLLECTION] [ANIMACAO]",
        source_url="local://SGDK_Engines/gerenciar animacoes",
        category="ANIMACAO",
        notes="Sprites locais para estudos de gerencia de animacoes.",
        source_paths=(SGDK_ENGINES / "gerenciar anima\u00e7\u00f5es",),
    ),
    ImportCollection(
        destination="Dialogue Box Assets [VER.001] [SGDK 211] [GEN] [COLLECTION] [TEXTO]",
        source_url="local://SGDK_Engines/Caixa de dialogo em SGDK",
        category="TEXTO",
        notes="Assets locais para estudo de janelas de dialogo e texto.",
        source_paths=(SGDK_ENGINES / "Caixa de di\u00e1logo em SGDK",),
    ),
    ImportCollection(
        destination="Camera Movement Assets [VER.001] [SGDK 211] [GEN] [COLLECTION] [CAMERA]",
        source_url="local://SGDK_Engines/Aula 10 - Movimento Camera",
        category="CAMERA",
        notes="Recursos locais de aula de camera preservados como referencia.",
        source_paths=(SGDK_ENGINES / "Aula 10 - Movimento Camera",),
    ),
    ImportCollection(
        destination="Valis 02 Assets [VER.001] [SGDK 211] [GEN] [COLLECTION] [PLATAFORMA]",
        source_url="local://SGDK_Engines/valis02",
        category="PLATAFORMA",
        notes="Assets locais associados ao estudo Valis 02.",
        source_paths=(SGDK_ENGINES / "valis02",),
    ),
    ImportCollection(
        destination="Intro Assets [VER.001] [SGDK 211] [GEN] [COLLECTION] [INTRO]",
        source_url="local://SGDK_Engines/Intro",
        category="INTRO",
        notes="Assets locais de intro preservados como referencia reutilizavel.",
        source_paths=(SGDK_ENGINES / "Intro",),
    ),
    ImportCollection(
        destination="Jump Tutorial Assets [VER.001] [SGDK 211] [GEN] [COLLECTION] [PLATAFORMA]",
        source_url="local://SGDK_Engines/Pulo",
        category="PLATAFORMA",
        notes="Assets locais de tutorial de pulo preservados como referencia.",
        source_paths=(SGDK_ENGINES / "Pulo",),
    ),
]

LOCAL_RAW_DIRS = [
    SGDK_ENGINES / "SELECT_PLAYER",
    SGDK_ENGINES / "Tutorial 09",
    SGDK_ENGINES / "gerenciar anima\u00e7\u00f5es",
    SGDK_ENGINES / "Tutorial Ataque - Parte 2",
    SGDK_ENGINES / "Aula 10 - Movimento Camera",
    SGDK_ENGINES / "Scroll",
    SGDK_ENGINES / "Caixa de di\u00e1logo em SGDK",
    SGDK_ENGINES / "valis02",
    SGDK_ENGINES / "Intro",
    SGDK_ENGINES / "Pulo",
]

DUPLICATES_SKIPPED = [
    {
        "source_url": "https://github.com/spacebruce/SGDK-Experiments/tree/bigtilemap",
        "active_destination": "SGDK_Engines/Big Tile Map [VER.001] [SGDK 211] [GEN] [ESTUDO] [CENARIO]",
    },
    {
        "source_url": "https://github.com/VagnoSilva/MegaRunner",
        "active_destination": "SGDK_Engines/Mega Runner [VER.001] [SGDK 211] [GEN] [GAME] [RUNNER]",
    },
]


def ensure_clean_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def copy_project_tree(source: Path, destination: Path) -> None:
    if not source.exists():
        raise FileNotFoundError(source)
    ensure_clean_dir(destination)
    shutil.copytree(
        source,
        destination,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns(*ROOT_DROP_DIRS),
    )


def drop_root_noise(project_root: Path) -> None:
    for child in list(project_root.iterdir()):
        if child.is_dir() and child.name.lower() in ROOT_DROP_DIRS:
            shutil.rmtree(child)
            continue
        if not child.is_file():
            continue
        name_lower = child.name.lower()
        if name_lower in ROOT_DROP_FILES:
            child.unlink()
            continue
        if name_lower.startswith(ROOT_DROP_PREFIXES):
            child.unlink()
            continue
        if child.suffix.lower() in ROOT_DROP_SUFFIXES:
            child.unlink()


def rename_case_folder(project_root: Path, old_name: str, new_name: str) -> None:
    old_path = next(
        (child for child in project_root.iterdir() if child.is_dir() and child.name == old_name),
        None,
    )
    if old_path is None:
        return
    new_path = next(
        (child for child in project_root.iterdir() if child.is_dir() and child.name == new_name),
        project_root / new_name,
    )
    if old_name.lower() == new_name.lower():
        temp_path = project_root / f"__tmp_{new_name}"
        if temp_path.exists():
            shutil.rmtree(temp_path)
        old_path.rename(temp_path)
        temp_path.rename(new_path)
        return
    if new_path.exists():
        for child in old_path.iterdir():
            target = new_path / child.name
            if target.exists():
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()
            shutil.move(str(child), str(target))
        old_path.rmdir()
        return
    old_path.rename(new_path)


def move_root_sources(project_root: Path) -> None:
    rename_case_folder(project_root, "Src", "src")
    rename_case_folder(project_root, "Res", "res")
    rename_case_folder(project_root, "Inc", "inc")

    root_source_exts = {".c", ".s", ".asm", ".68k"}
    root_header_exts = {".h", ".inc"}

    root_sources = [
        item for item in project_root.iterdir()
        if item.is_file() and item.suffix.lower() in root_source_exts
    ]
    root_headers = [
        item for item in project_root.iterdir()
        if item.is_file() and item.suffix.lower() in root_header_exts
    ]

    if root_sources:
        (project_root / "src").mkdir(exist_ok=True)
        for item in root_sources:
            target = project_root / "src" / item.name
            if target.exists():
                target.unlink()
            shutil.move(str(item), str(target))

    if root_headers:
        (project_root / "inc").mkdir(exist_ok=True)
        for item in root_headers:
            target = project_root / "inc" / item.name
            if target.exists():
                target.unlink()
            shutil.move(str(item), str(target))


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def wrapper_content(project_root: Path, script_name: str) -> str:
    relative = Path(os.path.relpath(WRAPPER_ROOT, project_root)).as_posix().replace("/", "\\")
    command = Path(script_name).stem
    return f'@echo off\ncall "%~dp0{relative}\\{command}.bat" "%~dp0"\nexit /b %errorlevel%\n'


def create_collection(entry: ImportCollection) -> None:
    root = SGDK_ENGINES / entry.destination
    ensure_clean_dir(root)

    manifest = {
        "schema_version": 1,
        "display_name": entry.destination,
        "project_root": ".",
        "sgdk_root": ".",
        "layout": "flat",
        "platform": entry.platform,
        "kind": "COLLECTION",
        "category": entry.category,
        "build_policy": "disabled",
        "notes": entry.notes,
    }
    write_text(root / ".mddev" / "project.json", json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    write_text(root / ".gitignore", GITIGNORE_CONTENT)

    summary = "\n".join(f"- {line}" for line in entry.summary_lines) if entry.summary_lines else "- Consulte o archive preservado para o conteudo original."
    sources = "\n".join(
        f"- `{source.relative_to(WORKSPACE_ROOT).as_posix()}`"
        for source in entry.source_paths
    )
    readme = (
        f"# {entry.destination}\n\n"
        f"Esta pasta e a colecao canonica desta referencia dentro do MegaDrive_DEV.\n\n"
        f"## Como usar\n\n"
        f"1. Leia `doc/README.md`.\n"
        f"2. Consulte o material preservado em `archives/`.\n"
        f"3. Nao trate esta raiz como uma ROM unica buildavel.\n\n"
        f"## Resumo\n\n"
        f"{summary}\n\n"
        f"## Fonte original\n\n"
        f"- `{entry.source_url}`\n"
    )
    doc_readme = (
        f"# {entry.destination}\n\n"
        f"## Natureza da colecao\n\n"
        f"{entry.notes}\n\n"
        f"## Fontes preservadas no workspace\n\n"
        f"{sources}\n\n"
        f"## Observacao operacional\n\n"
        f"- `build_policy: disabled`\n"
        f"- a raiz existe para orientar consulta e triagem, nao para build direto\n"
    )
    write_text(root / "README.md", readme)
    write_text(root / "doc" / "README.md", doc_readme)

    for script_name in ("build.bat", "clean.bat", "run.bat", "rebuild.bat"):
        write_text(root / script_name, wrapper_content(root, script_name))


def create_project(entry: ImportProject) -> None:
    destination = SGDK_ENGINES / entry.destination
    copy_project_tree(entry.source, destination)
    drop_root_noise(destination)
    move_root_sources(destination)
    write_text(destination / ".gitignore", GITIGNORE_CONTENT)


def archive_local_raw_dirs() -> list[str]:
    archived: list[str] = []
    LOCAL_SALVAGE.mkdir(parents=True, exist_ok=True)
    for raw_dir in LOCAL_RAW_DIRS:
        if not raw_dir.exists():
            continue
        destination = LOCAL_SALVAGE / raw_dir.name
        if destination.exists():
            shutil.rmtree(destination)
        shutil.move(str(raw_dir), str(destination))
        archived.append(destination.relative_to(WORKSPACE_ROOT).as_posix())
    return archived


def main() -> int:
    imported_projects: list[dict[str, str]] = []
    imported_collections: list[dict[str, str]] = []

    for entry in PROJECTS:
        create_project(entry)
        imported_projects.append(
            {
                "destination": f"SGDK_Engines/{entry.destination}",
                "source": entry.source.relative_to(WORKSPACE_ROOT).as_posix(),
                "source_url": entry.source_url,
                "notes": entry.notes,
                "platform": entry.platform,
            }
        )

    for entry in COLLECTIONS:
        create_collection(entry)
        imported_collections.append(
            {
                "destination": f"SGDK_Engines/{entry.destination}",
                "source_url": entry.source_url,
                "notes": entry.notes,
                "category": entry.category,
            }
        )

    archived_local_raw = archive_local_raw_dirs()

    report = {
        "archive_batch": ARCHIVE_BATCH.relative_to(WORKSPACE_ROOT).as_posix(),
        "imported_projects": imported_projects,
        "imported_collections": imported_collections,
        "archived_local_raw": archived_local_raw,
        "duplicates_skipped": DUPLICATES_SKIPPED,
    }
    write_text(REPORT_PATH, json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
