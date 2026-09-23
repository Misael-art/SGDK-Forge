"""Gera definicoes vazias para os simbolos extern de headers do rescomp (so para o host)."""
import re, sys
print('#include "genesis.h"')
for path in sys.argv[1:]:
    for line in open(path):
        m = re.match(r"extern const (SpriteDefinition|u8) (\w+)(\[\d+\])?;", line.strip())
        if m:
            kind, name, arr = m.groups()
            print(f"const SpriteDefinition {name};" if kind == "SpriteDefinition" else f"const u8 {name}{arr or '[1]'};")
