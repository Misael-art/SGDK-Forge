# Audio Tools — SGDK/XGM2

Ferramentas determinísticas para preparar e auditar áudio do Mega Drive. Este
diretório cobre conformidade e autoria de laboratório; não transforma um som em
`final` sem escuta contextual, integração SGDK e evidência fresca no BlastEm.

## Rotas

| Ferramenta | Entrada → saída | Claim máximo isolado |
|---|---|---|
| `audio_core.py` | funções numéricas WAV/VGM/XGM2 | conformidade numérica |
| `vgm_to_xgm2.py` | VGM → XGM/XGC pelo jar oficial | conversão técnica |
| `sample_convert.py` | WAV → payload PCM signed | payload compatível |
| `sfx_synth.py` | parâmetros → WAV de autoria | fonte sintetizada de laboratório |
| `loop_clipper.py` | WAV → recorte em zero crossing | candidato de loop |
| `audit_audio_provenance.py` | manifesto + `.res` → parecer | proveniência/formato |

WAV PCM de 8 bits usa bytes **unsigned** com silêncio em 128. O bloco SDAT do
XGM2 usa amostras **signed**. `audio_core` faz essa conversão explicitamente;
misturar as duas representações cria offset DC e áudio distorcido.

## Uso seguro

Execute primeiro todos os self-checks:

```bash
for tool in tools/audio-tools/*.py; do
  python3 "$tool" --self-check
done
```

Converta música sem forçar região quando o VGM já a declara:

```bash
python3 tools/audio-tools/vgm_to_xgm2.py \
  --input data/source_audio/music.vgm --out out/audio/music.xgm
```

Audite um projeto e rederive os hashes:

```bash
python3 tools/audio-tools/audit_audio_provenance.py \
  --project-root "SGDK_projects/<projeto>" --verify-hashes
```

O manifesto deve validar contra
`tools/sgdk_wrapper/schemas/sfx_bank_manifest.schema.json`. Caminhos absolutos,
traversal, IDs duplicados e divergência de path/tipo/taxa contra
`res/resources.res` são blockers.

## Gates que continuam externos

- direção sonora, arranjo FM/PSG e identidade;
- masking entre BGM e SFX críticos;
- prioridade e ownership observados em runtime;
- loop percebido sem clique ou fadiga;
- budget de ROM, Z80/DMA e cena pesada com áudio;
- escuta humana e evidência BlastEm vinculada à ROM.

SFX `synthesized` e `procedural_primitive` podem ser `lab` ou `placeholder`,
nunca `final` apenas porque passaram nestas ferramentas.
