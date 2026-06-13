#!/usr/bin/env python3
"""
Wrapper do lote Pequeno Principe: redimensiona e indexa usando a ferramenta
generica batch_resize_index.py e o spec specs/pequeno_principe_v2.json.

Uso (a partir da raiz do repo MegaDrive_DEV):
  python tools/image-tools/resize_and_index_pequeno_principe_batch.py [BATCH_ROOT]

BATCH_ROOT default: tmp/imagegen/inbox/pequeno_principe_v2
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BATCH_ROOT_DEFAULT = "tmp/imagegen/inbox/pequeno_principe_v2"
SPEC_PATH = os.path.join(SCRIPT_DIR, "specs", "pequeno_principe_v2.json")


def main() -> int:
    batch_root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else BATCH_ROOT_DEFAULT)
    if not os.path.isdir(batch_root):
        print(f"Erro: diretorio nao encontrado: {batch_root}", file=sys.stderr)
        return 1
    if not os.path.isfile(SPEC_PATH):
        print(f"Erro: spec nao encontrado: {SPEC_PATH}", file=sys.stderr)
        return 1
    sys.argv = [sys.argv[0], "--spec", SPEC_PATH, "--batch-root", batch_root]
    import batch_resize_index as generic
    return generic.main()


if __name__ == "__main__":
    sys.exit(main())
