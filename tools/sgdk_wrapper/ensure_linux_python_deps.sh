#!/usr/bin/env bash
# Provisiona o cache local de dependencias Python do framework.
#
# Contrato:
#   * o lock e a UNICA autoridade de versao; nada aqui repete um numero de
#     versao, porque duas fontes divergem silenciosamente na primeira edicao;
#   * download acontece somente aqui, fora da janela dos gates;
#   * verificacao exige versao do lock E procedencia dentro do cache local: um
#     `import` que resolve para o site-packages global do sistema passaria numa
#     checagem ingenua e destruiria a reprodutibilidade;
#   * dependencia ausente e blocker explicito, nunca skip.
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../.." && pwd)"
lock_path="$script_dir/linux_python_requirements.lock"
tool_root="$repo_root/out/host_tools/python"
wheel_dir="$tool_root/wheels"
install_dir="$tool_root/site-packages"

if [[ "$(uname -s)" != "Linux" ]]; then
    echo "linux_python_deps_status=blocked reason=unsupported_host"
    exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
    echo "linux_python_deps_status=blocked reason=dependency_missing dependency=python3"
    exit 1
fi

if [[ ! -f "$lock_path" ]]; then
    echo "linux_python_deps_status=blocked reason=lock_missing path=$lock_path"
    exit 1
fi

# Verificador unico, parametrizado pelo lock. `pip` ja aplica --require-hashes na
# instalacao; o que falta provar depois e que o import resolve para ESTE diretorio
# na versao fixada.
verify_script='
import sys
from pathlib import Path
from importlib.metadata import distribution, version

root = Path(sys.argv[1]).resolve()
lock = Path(sys.argv[2])

# Mapeia nome-de-distribuicao -> versao diretamente do lock.
expected = {}
for line in lock.read_text().splitlines():
    line = line.strip()
    if not line or line.startswith("#") or line.startswith("--"):
        continue
    if "==" not in line:
        continue
    name, _, rest = line.partition("==")
    expected[name.strip().lower()] = rest.split()[0].strip().rstrip("\\")

if not expected:
    print("lock_unparsable", file=sys.stderr)
    sys.exit(2)

for dist_name, want in sorted(expected.items()):
    found = version(dist_name)
    if found != want:
        print("version_mismatch %s expected=%s found=%s" % (dist_name, want, found), file=sys.stderr)
        sys.exit(3)
    origin = Path(distribution(dist_name).locate_file("")).resolve()
    if not origin.is_relative_to(root):
        print("outside_cache %s origin=%s" % (dist_name, origin), file=sys.stderr)
        sys.exit(4)

print(" ".join("%s=%s" % (k, v) for k, v in sorted(expected.items())))
'

if summary="$(PYTHONPATH="$install_dir" python3 -c "$verify_script" "$install_dir" "$lock_path" 2>/dev/null)"; then
    echo "linux_python_deps_status=ready $summary path=$install_dir source=cache"
    printf '%s\n' "$install_dir"
    exit 0
fi

mkdir -p "$wheel_dir"
python3 -m pip download \
    --require-hashes \
    --only-binary=:all: \
    --dest "$wheel_dir" \
    --requirement "$lock_path"

staging_dir="$(mktemp -d "$tool_root/.site-packages.XXXXXX")"
cleanup() {
    if [[ -d "$staging_dir" ]]; then
        rm -rf -- "$staging_dir"
    fi
}
trap cleanup EXIT

python3 -m pip install \
    --disable-pip-version-check \
    --no-index \
    --no-deps \
    --require-hashes \
    --find-links "$wheel_dir" \
    --target "$staging_dir" \
    --requirement "$lock_path"

# Verifica no staging ANTES de publicar: promover sem validar reintroduziria
# exatamente o falso verde que este script existe para impedir.
summary="$(PYTHONPATH="$staging_dir" python3 -c "$verify_script" "$staging_dir" "$lock_path")"

rm -rf -- "$install_dir"
mv "$staging_dir" "$install_dir"

echo "linux_python_deps_status=ready $summary path=$install_dir source=download"
printf '%s\n' "$install_dir"
