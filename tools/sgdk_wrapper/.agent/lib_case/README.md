# Biblioteca de Retenção de Conhecimento (Agent Few-Shot Base)

Esta base serve para contornar a desintegração de contexto de um LLM Operacional. Ao tratar de conversões gráficas, heurísticas abstratas ("use layout", "faça edge detection") se degradam rapidamente sem referencial puro.

Sempre que a `SKILL.md` direcionar você a uma taxonomia complexa (como lidar com `editorial_board` vs `palette_panorama`), entre aqui.
Isto **NÃO É** código produtivo. Estes sao Casos Academicos destilados por taxonomia.

## Ponto de entrada canonico

Comece por:

- `tools/sgdk_wrapper/.agent/lib_case/art-translation/index.json`
- `tools/sgdk_wrapper/.agent/lib_case/sgdk-runtime/index.json`
- `doc/05_technical/92_sgdk_engine_pattern_frontdoor.md`
- `doc/05_technical/92_sgdk_engine_pattern_registry.json`

Ele mapeia taxonomia -> caso pedagogico -> arquivos de entrada -> casos reais canonicos no corpus.

No dominio de runtime, o fluxo correto e:

- `front door` para ler a classificacao e o status dos padroes
- `registry` para resolver ids, evidencias e promocao
- `lib_case/sgdk-runtime` para few-shot executavel

Regra:

- appendix de pesquisa nao substitui registry
- registry nao substitui `lib_case`
- nada disso promove canon automaticamente

## Contrato por taxonomia / dominio

Cada pasta de caso deve expor:

- `source.png`
- `parsing_example.py`
- `case_meta.json`
- `.json` de report quando existir

Estes sao os arquivos magnos por pasta:
- `source.png`: A evidência fotográfica canonica bruta.
- `parsing_example.py`: A implementação cirúrgica provando como a Engine Semântica opera nesta taxonomia.
- `.json` reports: A evidência logada de sucesso e IoU garantidos pra aquele arquivo.

### Taxonomias Presentes

- **`case_editorial_board/`**: Demonstra o uso de recortes espaciais puros (`A_BOX`, `B_BOX`) para isolar camadas em uma prancha pré-organizada separada em grade de arame no X e Y. Exemplo: _Metal Slug Sunset_.
- **`case_flat_panorama_palette/`**: Demonstra o uso de Conjunto Químico Semântico de Cores (Palette clustering) para extrair camadas por Z-Depth quando a prancha for inteiriça, sem bordas ou limites pre-estabelecidos. Exemplo: _Underwater Scene_.
- **`case_spritesheet_islands/`**: Demonstra o *Auto-Assembler AAA*. Para pranchas massivas ripadas com ruídos visuais. Usa detecção por Ilhas (BFS) com limite de massa, matando lixos literários, extrai os Bounding Boxes livremente e re-agrupa em *Action Strips* normalizadas por Y e múltiplo de 8. Exemplo: _Gaira Samurai Shodown_.
- **`case_cutscene_board/`**: Demonstra a extração de *Storyboards de Cutscene* ripados. Quadros fullscreen, close-ups e sprites isolados coexistem na mesma prancha com lixo editorial. Usa Islands BFS com massa alta (>=2000), classificação automática por dimensão, e gera DUAS versões de cada fullscreen: fixa (320x224) e scroll/panning (320xN). Quantização artística (interpretação estética, não conversão direta) com 60 cores para fullscreen e 15 para close-ups. Exemplo: _Castlevania Rondo of Blood Intro #2_.
- **`case_level_tilemap_lighting/`**: Demonstra a engenharia reversa de iluminação de cenários avançados (PS1/Saturn) para o sistema de *Highlight / Shadow* do Mega Drive. Separa a imagem nativa em um 'Base Tilemap' chapado (quantizado e grid-snapped para as restrições VDP) e duas Máscaras Booleanas de Luma: Highlight Mask (+Luma) e Shadow Mask (-Luma). Contém o motor analítico para re-projetar o render da Prova Virtual final combinando a conversão limpa com os blendings simulados do hardware. Exemplo: _Castlevania SotN Underground Caverns_.

> **Regra Suprema**: Leia o código de demonstração nestes diretórios antes de escrever seu próprio código algorítmico global.
