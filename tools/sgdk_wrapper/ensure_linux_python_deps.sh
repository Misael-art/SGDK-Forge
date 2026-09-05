#!/usr/bin/env bash
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

if PYTHONPATH="$install_dir" python3 -c 'import sys; from pathlib import Path; from importlib.metadata import distribution, version; root=Path(sys.argv[1]).resolve(); assert version("jsonschema") == "4.25.1"; assert version("pillow") == "12.3.0"; assert Path(distribution("jsonschema").locate_file("")).resolve().is_relative_to(root); assert Path(distribution("pillow").locate_file("")).resolve().is_relative_to(root)' "$install_dir" >/dev/null 2>&1; then
    echo "linux_python_deps_status=ready jsonschema=4.25.1 pillow=12.3.0 path=$install_dir source=cache"
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

PYTHONPATH="$staging_dir" python3 -c 'import sys; from pathlib import Path; from importlib.metadata import distribution, version; root=Path(sys.argv[1]).resolve(); assert version("jsonschema") == "4.25.1"; assert version("pillow") == "12.3.0"; assert Path(distribution("jsonschema").locate_file("")).resolve().is_relative_to(root); assert Path(distribution("pillow").locate_file("")).resolve().is_relative_to(root)' "$staging_dir"
rm -rf -- "$install_dir"
mv "$staging_dir" "$install_dir"

echo "linux_python_deps_status=ready jsonschema=4.25.1 pillow=12.3.0 path=$install_dir source=download"
printf '%s\n' "$install_dir"
