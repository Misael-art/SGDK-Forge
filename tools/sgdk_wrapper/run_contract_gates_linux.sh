#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../.." && pwd)"

if [[ "$(uname -s)" != "Linux" ]]; then
    echo "contract_gate_environment_status=blocked blocker=unsupported_host" >&2
    exit 2
fi

pwsh_path="$("$script_dir/ensure_linux_pwsh.sh" | tail -n 1)"
java_path="$("$script_dir/ensure_linux_java.sh" | tail -n 1)"
python_deps_path="$("$script_dir/ensure_linux_python_deps.sh" | tail -n 1)"
java_bin="$(dirname "$java_path")"

export PATH="$script_dir/linux_shims:$java_bin:$(dirname "$pwsh_path"):$PATH"
export PYTHONPATH="$python_deps_path${PYTHONPATH:+:$PYTHONPATH}"

exec "$pwsh_path" -NoProfile -ExecutionPolicy Bypass -File "$script_dir/ci/run_all_contract_gates.ps1" "$@"
