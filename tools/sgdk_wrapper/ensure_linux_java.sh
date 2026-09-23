#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../.." && pwd)"
manifest_path="$script_dir/linux_host_dependencies.json"
tool_root="$repo_root/out/host_tools/java"

if [[ "$(uname -s)" != "Linux" ]]; then
    echo "linux_java_status=blocked reason=unsupported_host"
    exit 1
fi

for required_command in python3 curl tar sha256sum mktemp; do
    if ! command -v "$required_command" >/dev/null 2>&1; then
        echo "linux_java_status=blocked reason=dependency_missing dependency=$required_command"
        exit 1
    fi
done

mapfile -t manifest_values < <(
    python3 -c 'import json,sys; p=json.load(open(sys.argv[1], encoding="utf-8"))["java"]; print(p["version"]); print(p["url"]); print(p["sha256"])' "$manifest_path"
)
java_version="${manifest_values[0]}"
java_url="${manifest_values[1]}"
java_sha256="${manifest_values[2]}"
install_dir="$tool_root/$java_version"
java_path="$install_dir/bin/java"

if [[ -x "$java_path" ]]; then
    echo "linux_java_status=ready version=$java_version path=$java_path source=cache"
    printf '%s\n' "$java_path"
    exit 0
fi

mkdir -p "$tool_root"
staging_dir="$(mktemp -d "$tool_root/.java-$java_version.XXXXXX")"
archive_path="$staging_dir/temurin-jre.tar.gz"

cleanup() {
    if [[ -d "$staging_dir" ]]; then
        rm -rf -- "$staging_dir"
    fi
}
trap cleanup EXIT

curl --fail --location --proto '=https' --tlsv1.2 --output "$archive_path" "$java_url"
actual_sha256="$(sha256sum "$archive_path" | awk '{print $1}')"
if [[ "$actual_sha256" != "$java_sha256" ]]; then
    echo "linux_java_status=blocked reason=sha256_mismatch expected=$java_sha256 actual=$actual_sha256"
    exit 1
fi

mkdir -p "$staging_dir/extracted"
tar -xzf "$archive_path" --strip-components=1 -C "$staging_dir/extracted"

if [[ ! -x "$staging_dir/extracted/bin/java" ]]; then
    echo "linux_java_status=blocked reason=java_missing_after_extract"
    exit 1
fi
if [[ -e "$install_dir" ]]; then
    echo "linux_java_status=blocked reason=partial_install_present path=$install_dir"
    exit 1
fi
mv "$staging_dir/extracted" "$install_dir"

echo "linux_java_status=ready version=$java_version path=$java_path source=download"
printf '%s\n' "$java_path"
