#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../.." && pwd)"
manifest_path="$script_dir/linux_host_dependencies.json"
tool_root="$repo_root/out/host_tools/powershell"

if [[ "$(uname -s)" != "Linux" ]]; then
    echo "linux_pwsh_status=blocked reason=unsupported_host"
    exit 1
fi

for required_command in python3 curl tar sha256sum mktemp; do
    if ! command -v "$required_command" >/dev/null 2>&1; then
        echo "linux_pwsh_status=blocked reason=dependency_missing dependency=$required_command"
        exit 1
    fi
done

mapfile -t manifest_values < <(
    python3 -c 'import json,sys; p=json.load(open(sys.argv[1], encoding="utf-8"))["powershell"]; print(p["version"]); print(p["url"]); print(p["sha256"])' "$manifest_path"
)
pwsh_version="${manifest_values[0]}"
pwsh_url="${manifest_values[1]}"
pwsh_sha256="${manifest_values[2]}"
install_dir="$tool_root/$pwsh_version"
pwsh_path="$install_dir/pwsh"

if [[ -x "$pwsh_path" ]]; then
    echo "linux_pwsh_status=ready version=$pwsh_version path=$pwsh_path source=cache"
    printf '%s\n' "$pwsh_path"
    exit 0
fi

mkdir -p "$tool_root"
staging_dir="$(mktemp -d "$tool_root/.pwsh-$pwsh_version.XXXXXX")"
archive_path="$staging_dir/powershell.tar.gz"

cleanup() {
    if [[ -d "$staging_dir" ]]; then
        rm -rf -- "$staging_dir"
    fi
}
trap cleanup EXIT

curl --fail --location --proto '=https' --tlsv1.2 --output "$archive_path" "$pwsh_url"
actual_sha256="$(sha256sum "$archive_path" | awk '{print $1}')"
if [[ "$actual_sha256" != "$pwsh_sha256" ]]; then
    echo "linux_pwsh_status=blocked reason=sha256_mismatch expected=$pwsh_sha256 actual=$actual_sha256"
    exit 1
fi

mkdir -p "$staging_dir/extracted"
tar -xzf "$archive_path" -C "$staging_dir/extracted"
chmod +x "$staging_dir/extracted/pwsh"

if [[ -e "$install_dir" ]]; then
    echo "linux_pwsh_status=blocked reason=partial_install_present path=$install_dir"
    exit 1
fi
mv "$staging_dir/extracted" "$install_dir"

echo "linux_pwsh_status=ready version=$pwsh_version path=$pwsh_path source=download"
printf '%s\n' "$pwsh_path"
