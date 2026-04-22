# Windows Toolchain Gotchas

## 1. Build no shell correto

No ambiente Windows do workspace:

- `build.bat` sozinho pode falhar dependendo do shell
- preferir sempre:

```bat
cmd //c "F:\\path\\absoluto\\build.bat"
```

## 2. Paths com colchetes

Diretorios com `[` e `]` podem quebrar o CMD.

Resposta canonica:

- usar caminho absoluto bem quotado
- se necessario, resolver short path `8.3`

## 3. Wrapper primeiro

- build de projeto SGDK deve passar pelo wrapper canonico
- evitar `cd` manual + make artesanal quando a tarefa for build oficial

## 4. ResComp e memoria Java

- sprites grandes podem exigir `-Xmx2g`
- isso ja deve existir no ambiente, mas a skill nao pode presumir que o usuario sabe

## 5. PNG indexado compativel com SGDK

Padrao util com Pillow:

```python
img = Image.new('P', size)
img.putpalette(palette)
img.save(path, transparency=0)
```

Regra:

- `transparency=0` precisa ser explicita quando o index `0` for transparente

## 6. Evidencia de build

Sempre registrar:

- caminho absoluto do projeto
- comando real executado
- hash da ROM gerada
- se a sessao de emulador corresponde a essa build
