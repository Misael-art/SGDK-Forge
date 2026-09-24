#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
manifest_path="$script_dir/linux_host_dependencies.json"

if [[ "$(uname -s)" != "Linux" ]]; then
    echo "linux_blastem_status=blocked reason=unsupported_host"
    exit 1
fi

for required_command in python3 flatpak xdotool import; do
    if ! command -v "$required_command" >/dev/null 2>&1; then
        echo "linux_blastem_status=blocked reason=dependency_missing dependency=$required_command"
        exit 1
    fi
done

mapfile -t manifest_values < <(
    python3 -c 'import json,sys; p=json.load(open(sys.argv[1], encoding="utf-8"))["blastem_linux"]; print(p["ref"]); print(p["commit"]); print(p["remote"]); print(p["version"])' "$manifest_path"
)
blastem_ref="${manifest_values[0]}"
blastem_commit="${manifest_values[1]}"
blastem_remote="${manifest_values[2]}"
blastem_version="${manifest_values[3]}"
blastem_app="com.retrodev.blastem"

if ! flatpak --user info "$blastem_app" >/dev/null 2>&1; then
    flatpak --user install --noninteractive "$blastem_remote" "$blastem_ref"
fi

installed_commit="$(flatpak --user info --show-commit "$blastem_app")"
if [[ "$installed_commit" != "$blastem_commit" ]]; then
    flatpak --user update --noninteractive --commit="$blastem_commit" "$blastem_ref"
    installed_commit="$(flatpak --user info --show-commit "$blastem_app")"
fi

if [[ "$installed_commit" != "$blastem_commit" ]]; then
    echo "linux_blastem_status=blocked reason=commit_mismatch expected=$blastem_commit actual=$installed_commit"
    exit 1
fi

echo "linux_blastem_status=ready version=$blastem_version ref=$blastem_ref commit=$installed_commit"
