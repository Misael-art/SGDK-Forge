#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../.." && pwd)"
project_root=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --project-root) project_root="$2"; shift 2 ;;
        *) echo "wine_bridge_status=blocked reason=unknown_argument argument=$1"; exit 2 ;;
    esac
done

if [[ "$(uname -s)" != "Linux" ]]; then
    echo "wine_bridge_status=blocked reason=unsupported_host"
    exit 2
fi
if [[ -z "$project_root" ]]; then
    echo "wine_bridge_status=blocked reason=project_root_required"
    exit 2
fi
for command_name in flatpak python3 sha256sum make; do
    if ! command -v "$command_name" >/dev/null 2>&1; then
        echo "wine_bridge_status=blocked reason=dependency_missing dependency=$command_name"
        exit 2
    fi
done

project_root="$(cd "$project_root" && pwd)"
source_gdk="$repo_root/sdk/sgdk-2.11"
tool_root="$repo_root/out/host_tools/sgdk_wine_flatpak"
staged_gdk="$tool_root/sgdk-2.11"
gdk_link="/mnt/sdcard/sgdk_forge_wine_211"
wine_app="org.winehq.Wine//wow64-24.08"
route_report="$project_root/out/logs/sgdk_build_route_report.json"
if ! python3 "$script_dir/select_sgdk_build_route.py" \
    --repo-root "$repo_root" \
    --project-root "$project_root" \
    --platform linux \
    --output "$route_report" >/dev/null; then
    echo "wine_bridge_status=blocked reason=build_route_selector_failed report=$route_report"
    exit 2
fi
if [[ ! -f "$source_gdk/makefile.gen" ]]; then
    echo "wine_bridge_status=blocked reason=sgdk_missing path=$source_gdk"
    exit 2
fi
if ! flatpak --user info org.winehq.Wine >/dev/null 2>&1; then
    echo "wine_bridge_status=blocked reason=wine_flatpak_missing required_ref=$wine_app"
    exit 2
fi

source_marker="$(sha256sum "$source_gdk/makefile.gen" | awk '{print $1}')"
staged_marker_path="$tool_root/source_makefile.sha256"
staged_marker=""
if [[ -f "$staged_marker_path" ]]; then
    staged_marker="$(tr -d '\r\n' < "$staged_marker_path")"
fi
if [[ "$source_marker" != "$staged_marker" || ! -d "$staged_gdk/bin" ]]; then
    mkdir -p "$tool_root"
    staging_copy="$tool_root/.sgdk-2.11.staging"
    rm -rf -- "$staging_copy"
    mkdir -p "$staging_copy"
    cp -a "$source_gdk/." "$staging_copy/"
    rm -rf -- "$staged_gdk"
    mv "$staging_copy" "$staged_gdk"
    printf '%s\n' "$source_marker" > "$staged_marker_path"
    rm -f -- "$tool_root/libmd_no_lto.sha256"
fi

python3 - "$staged_gdk" "$repo_root" "$wine_app" "$gdk_link" <<'PY'
import os
import stat
import sys
from pathlib import Path

gdk = Path(sys.argv[1])
repo = Path(sys.argv[2])
wine_app = sys.argv[3]
host_gdk_link = sys.argv[4]
wine_gdk_link = "E:/sgdk_forge_wine_211"
bin_dir = gdk / "bin"
for executable in sorted(bin_dir.glob("*.exe")):
    wrapper = executable.with_suffix("")
    # Some SGDK distributions already expose extensionless symlinks such as
    # `sjasm -> sjasm.exe`. Writing through them would corrupt the PE binary.
    if wrapper.is_symlink() or wrapper.exists():
        wrapper.unlink()
    wrapper.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        'bin_dir="$(realpath "$(dirname "${BASH_SOURCE[0]}")")"\n'
        f'host_gdk_link="{host_gdk_link}"\n'
        f"wine_gdk_link='{wine_gdk_link}'\n"
        'converted=()\n'
        'for arg in "$@"; do\n'
        '    if [[ "$arg" == @* && -f "${arg#@}" ]]; then\n'
        '        response_file="${arg#@}"\n'
        '        converted_response="${response_file}.wine"\n'
        '        sed "s|$host_gdk_link|$wine_gdk_link|g" "$response_file" > "$converted_response"\n'
        '        if [[ "${SGDK_WINE_INSIDE_FLATPAK:-0}" == "1" ]]; then\n'
        '            wine_response="$(winepath -w "$converted_response")"\n'
        '        else\n'
        f'            wine_response="$(flatpak --user run --filesystem="/mnt/sdcard" --command=winepath {wine_app} -w "$converted_response")"\n'
        '        fi\n'
        '        converted+=("@$wine_response")\n'
        '    else\n'
        '        converted+=("${arg//$host_gdk_link/$wine_gdk_link}")\n'
        '    fi\n'
        'done\n'
        'if [[ "${SGDK_WINE_INSIDE_FLATPAK:-0}" == "1" ]]; then\n'
        f'    wine_exe="$(winepath -w "$bin_dir/{executable.name}")"\n'
        '    exec wine "$wine_exe" "${converted[@]}"\n'
        'fi\n'
        f'wine_exe="$(flatpak --user run --filesystem="/mnt/sdcard" --command=winepath {wine_app} -w "$bin_dir/{executable.name}")"\n'
        f'exec flatpak --user run --filesystem="/mnt/sdcard" --command=wine {wine_app} "$wine_exe" "${{converted[@]}}"\n',
        encoding="utf-8",
    )
    wrapper.chmod(wrapper.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

original = (gdk / "makefile.gen").read_text(encoding="utf-8")
needle = "include $(GDK)/common.mk\n"
if needle not in original:
    raise SystemExit("makefile.gen include anchor missing")
override = r'''

# Linux host + Flatpak Wine wrappers (Franticware SGDK_wine method, SGDK 2.11).
SHELL := /bin/sh
RM := rm
CP := cp
MKDIR := mkdir
AR := $(GDK)/bin/ar
CC := $(GDK)/bin/gcc
LD := $(GDK)/bin/ld
NM := $(GDK)/bin/nm
OBJCPY := $(GDK)/bin/objcopy
CONVSYM := $(GDK)/bin/convsym
ASMZ80 := $(GDK)/bin/sjasm
MACCER := $(GDK)/bin/mac68k
BINTOS := $(GDK)/bin/bintos
JAVA := java
SIZEBND := $(JAVA) $(JAVA_OPTS) -jar $(GDK)/bin/sizebnd.jar
RESCOMP := $(JAVA) $(JAVA_OPTS) -jar $(GDK)/bin/rescomp.jar
LTO_PLUGIN :=
LIBGCC := $(LIB)/libgcc.a
'''
(gdk / "makefile_wine.gen").write_text(original.replace(needle, needle + override, 1), encoding="utf-8")
makelib = (gdk / "makelib.gen").read_text(encoding="utf-8")
makelib = makelib.replace(needle, needle + override, 1)
makelib = makelib.replace(" -flto -flto=auto -ffat-lto-objects", "")
(gdk / "makelib_wine.gen").write_text(makelib, encoding="utf-8")
PY

ln -sfn "$staged_gdk" "$gdk_link"
# Restore canonical assembly sources if a previous staging cleanup removed one.
# Only dependency, object, resource-intermediate and listing files are generated;
# `.s` also contains real SGDK boot/runtime sources and must never be blanket-deleted.
while IFS= read -r -d '' assembly_source; do
    relative_source="${assembly_source#"$source_gdk"/}"
    if [[ ! -f "$staged_gdk/$relative_source" ]]; then
        mkdir -p "$(dirname "$staged_gdk/$relative_source")"
        cp "$assembly_source" "$staged_gdk/$relative_source"
    fi
done < <(find "$source_gdk/src" -type f -name '*.s' -print0)
java_path="$("$script_dir/ensure_linux_java.sh" | tail -n 1)"
export WINEDEBUG=-all
# Windows-generated dependencies may contain drive paths that native make
# interprets as /m68k/.... Rebuild objects so LTO=0 and changed resources are
# both applied; logs, evidence and the last ROM remain intact until relink.
find "$project_root/out" -type f \( -name '*.d' -o -name '*.o' -o -name '*.s' -o -name '*.rs' -o -name '*.lst' \) -delete 2>/dev/null || true
rm -f -- "$project_root/out/rom.out" "$project_root/out/cmd_"
lib_marker_path="$tool_root/libmd_no_lto.sha256"
lib_rebuild_required=true
if [[ -f "$lib_marker_path" && -f "$staged_gdk/lib/libmd.a" ]]; then
    expected_lib_hash="$(tr -d '\r\n' < "$lib_marker_path")"
    actual_lib_hash="$(sha256sum "$staged_gdk/lib/libmd.a" | awk '{print $1}')"
    if [[ "$expected_lib_hash" == "$actual_lib_hash" ]]; then
        lib_rebuild_required=false
    fi
fi
if [[ "$lib_rebuild_required" == "true" ]]; then
    lib_progress_marker="$tool_root/libmd_no_lto.in_progress"
    # Native make parses dependency files before it can execute cleanrelease.
    # A failed Wine attempt can leave drive-letter paths in those files, so
    # remove generated metadata on the host before invoking make. Preserve
    # already rebuilt non-LTO objects when resuming after an archive failure.
    find "$staged_gdk/src" "$staged_gdk/res" -type f \
        \( -name '*.d' -o -name '*.rs' -o -name '*.lst' \) \
        -delete 2>/dev/null || true
    if [[ ! -f "$lib_progress_marker" ]]; then
        find "$staged_gdk/src" "$staged_gdk/res" -type f -name '*.o' -delete 2>/dev/null || true
        : > "$lib_progress_marker"
    fi
    rm -f -- "$staged_gdk/lib/libmd.a" "$staged_gdk/cmd_"
    set +e
    flatpak --user run --filesystem="/mnt/sdcard" --command=sh "$wine_app" -c '
        export PATH="$1:$PATH"
        export SGDK_WINE_INSIDE_FLATPAK=1
        export WINEDEBUG=-all
        cd "$2"
        make GDK="$2" -f "$2/makelib_wine.gen" release
    ' sh "$(dirname "$java_path")" "$gdk_link"
    lib_build_rc=$?
    set -e
    if [[ $lib_build_rc -ne 0 || ! -f "$staged_gdk/lib/libmd.a" ]]; then
        echo "wine_bridge_status=blocked reason=libmd_rebuild_failed exit_code=$lib_build_rc"
        exit "${lib_build_rc:-2}"
    fi
    sha256sum "$staged_gdk/lib/libmd.a" | awk '{print $1}' > "$lib_marker_path"
    rm -f -- "$lib_progress_marker"
fi
started_at="$(python3 -c 'from datetime import datetime,timezone; print(datetime.now(timezone.utc).isoformat())')"
set +e
flatpak --user run --filesystem="/mnt/sdcard" --command=sh "$wine_app" -c '
    export PATH="$1:$PATH"
    export SGDK_WINE_INSIDE_FLATPAK=1
    export WINEDEBUG=-all
    cd "$2"
    make GDK="$3" LTO=0 -f "$3/makefile_wine.gen"
' sh "$(dirname "$java_path")" "$project_root" "$gdk_link"
build_rc=$?
set -e
completed_at="$(python3 -c 'from datetime import datetime,timezone; print(datetime.now(timezone.utc).isoformat())')"

report_path="$project_root/out/logs/linux_wine_build_report.json"
mkdir -p "$(dirname "$report_path")"
python3 - "$report_path" "$project_root" "$gdk_link" "$started_at" "$completed_at" "$build_rc" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

report_path, project_root, gdk_root, started_at, completed_at, build_rc = sys.argv[1:]
rom = Path(project_root) / "out/rom.bin"
digest = hashlib.sha256(rom.read_bytes()).hexdigest() if rom.is_file() else None
report = {
    "schema": "linux_wine_build_report.v2",
    "status": "buildado" if int(build_rc) == 0 and rom.is_file() else "blocked",
    "bridge_method": "native GNU make plus Flatpak Wine wrappers for SGDK 2.11 Windows executables, LTO disabled to consume the fat-object section of the workspace libmd.a",
    "method_source": "SGDK readme Linux recommendation plus Franticware/SGDK_wine",
    "canonical_wrapper_status": "host_validation_executed_windows_batch_wrapper_blocked_by_wine_powershell_stub",
    "project_root": project_root,
    "gdk_root": gdk_root,
    "started_at": started_at,
    "completed_at": completed_at,
    "exit_code": int(build_rc),
    "rom": {
        "path": str(rom),
        "size_bytes": rom.stat().st_size if rom.is_file() else 0,
        "sha256": digest,
    },
}
Path(report_path).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
PY

if [[ $build_rc -ne 0 ]]; then
    echo "wine_bridge_status=blocked reason=sgdk_make_failed exit_code=$build_rc report=$report_path"
    exit "$build_rc"
fi
echo "wine_bridge_status=buildado report=$report_path"
