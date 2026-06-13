import argparse
import json
import os
import re
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_ROOT = WORKSPACE_ROOT / "tools" / "sgdk_wrapper" / "modelo"
NESTED_TEMPLATE_ROOT = WORKSPACE_ROOT / "tools" / "sgdk_wrapper" / "templates" / "project-template-nested"
ARCHIVE_ROOT = WORKSPACE_ROOT / "archives" / "manual_review"
DEFAULT_ROOTS = ("SGDK_Engines", "SGDK_projects")
KNOWN_TAGS_KIND = {"ENGINE", "GAME", "TEMPLATE", "ESTUDO", "EDITOR"}
KNOWN_TAGS_PLATFORM = {"GEN", "SMS"}
NOISE_NAMES = {
    ".git",
    ".hg",
    ".svn",
    ".vscode",
    ".mddev",
    "doc",
    "docs",
    "out",
    "archives",
    "archive",
    "manual_review",
    "tmp",
    "temp",
    "dist",
    "build",
    "node_modules",
}
WRAPPER_NAMES = ("build.bat", "clean.bat", "run.bat", "rebuild.bat")
LEGACY_SCRIPT_NAMES = {
    "compilar.bat",
    "compilar-rodar.bat",
    "limpar.bat",
    "copilar.bat",
    "run update.bat",
    "compilar_relativo.bat",
    "build_and_run.bat",
    "compilar_testar.bat",
    "compilar_atualizar.bat",
    "compile_teste.bat",
    "RA_SMGP.bat",
}
LEGACY_SCRIPT_NAMES_LOWER = {name.lower() for name in LEGACY_SCRIPT_NAMES}
LOG_PATTERNS = (
    re.compile(r"build_.*\.log$", re.IGNORECASE),
    re.compile(r"validation_report\.json$", re.IGNORECASE),
    re.compile(r"hs_err_pid\d+\.log$", re.IGNORECASE),
    re.compile(r"replay_pid\d+\.log$", re.IGNORECASE),
)
ROOT_BIN_EXTENSIONS = {".bin", ".out", ".o", ".d"}
ORPHAN_ENTRY_DIR_NAMES = ("src", "res", "inc")


@dataclass
class ProjectLayout:
    entry_root: Path
    sgdk_root: Path
    layout: str
    reason: str
    warnings: list[str] = field(default_factory=list)

    @property
    def rel_entry(self) -> str:
        return str(self.entry_root.relative_to(WORKSPACE_ROOT))

    @property
    def rel_sgdk(self) -> str:
        return str(self.sgdk_root.relative_to(WORKSPACE_ROOT))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Canonicaliza projetos do MegaDrive_DEV com manifesto, docs e wrappers padronizados."
    )
    parser.add_argument(
        "--roots",
        nargs="*",
        default=list(DEFAULT_ROOTS),
        help="Raizes para varrer. Padrao: SGDK_Engines SGDK_projects",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Aplica alteracoes. Sem esta flag o script roda em dry-run.",
    )
    parser.add_argument(
        "--include-examples",
        action="store_true",
        help="Inclui a pasta examples na varredura.",
    )
    parser.add_argument(
        "--report-json",
        help="Escreve um relatorio JSON no caminho informado.",
    )
    return parser.parse_args()


def validate_template_roots() -> None:
    required_paths = (
        TEMPLATE_ROOT,
        TEMPLATE_ROOT / "doc",
        TEMPLATE_ROOT / "README.md",
        NESTED_TEMPLATE_ROOT,
        NESTED_TEMPLATE_ROOT / "README.md",
    )
    missing = [path for path in required_paths if not path.exists()]
    if missing:
        joined = ", ".join(str(path.relative_to(WORKSPACE_ROOT)) for path in missing)
        raise RuntimeError(f"Templates canonicos ausentes para canonicalizacao: {joined}")


def is_project_like(path: Path) -> bool:
    if not path.is_dir():
        return False
    return (path / "src").is_dir() or (path / "res").is_dir() or (path / "inc").is_dir()


def child_candidates(path: Path) -> list[tuple[Path, int]]:
    candidates: list[tuple[Path, int]] = []
    for child in path.iterdir():
        if not child.is_dir():
            continue
        if child.name.lower() in NOISE_NAMES:
            continue
        score = 0
        if (child / "src").is_dir():
            score += 5
        if (child / "res").is_dir():
            score += 3
        if (child / "inc").is_dir():
            score += 1
        if any(child.glob("*.bat")):
            score += 1
        if any(child.glob("*.sh")):
            score += 1
        if score >= 5:
            candidates.append((child, score))
    return sorted(candidates, key=lambda item: item[1], reverse=True)


def detect_layout(entry_root: Path) -> ProjectLayout:
    entry_has_src = (entry_root / "src").is_dir()
    entry_has_res = (entry_root / "res").is_dir()
    entry_has_inc = (entry_root / "inc").is_dir()
    candidates = child_candidates(entry_root)
    complete_children = [item for item in candidates if (item[0] / "src").is_dir() and (item[0] / "res").is_dir()]
    warnings: list[str] = []

    if entry_has_src and entry_has_res:
        if len(complete_children) == 1 and not entry_has_inc:
            warnings.append("entry-root also has src/res but looks incomplete compared to nested child")
            return ProjectLayout(entry_root, complete_children[0][0], "nested", "nested-complete-child", warnings)
        return ProjectLayout(entry_root, entry_root, "flat", "direct-complete", warnings)

    if entry_has_src and not entry_has_res:
        if len(complete_children) == 1:
            warnings.append("entry-root has src but nested child is the only complete SGDK root")
            return ProjectLayout(entry_root, complete_children[0][0], "nested", "entry-missing-res-single-complete-child", warnings)
        return ProjectLayout(entry_root, entry_root, "flat", "direct-src-only", warnings)

    if len(candidates) == 1:
        return ProjectLayout(entry_root, candidates[0][0], "nested", "single-child-candidate", warnings)

    if len(candidates) > 1:
        if len(candidates) >= 2 and candidates[0][1] > candidates[1][1]:
            warnings.append("multiple nested candidates found, highest score chosen")
            return ProjectLayout(entry_root, candidates[0][0], "nested", "highest-score-child", warnings)
        names = ", ".join(candidate[0].name for candidate in candidates)
        raise RuntimeError(f"Estrutura ambigua em {entry_root}: {names}")

    raise RuntimeError(f"Nao foi possivel localizar SGDK root em {entry_root}")


def iter_project_entries(roots: list[str]) -> list[Path]:
    entries: list[Path] = []
    for root_name in roots:
        root = WORKSPACE_ROOT / root_name
        if not root.is_dir():
            continue
        for child in sorted(root.iterdir()):
            if not child.is_dir():
                continue
            if is_project_like(child) or child_candidates(child):
                entries.append(child)
    return entries


def infer_metadata(project_dir_name: str) -> dict[str, str]:
    tags = re.findall(r"\[([^\]]+)\]", project_dir_name)
    display_name = project_dir_name.split("[", 1)[0].strip() or project_dir_name
    platform = next((tag for tag in tags if tag in KNOWN_TAGS_PLATFORM), "GEN")
    kind = next((tag for tag in tags if tag in KNOWN_TAGS_KIND), "GAME")
    category = tags[-1] if tags else "NA"
    return {
        "display_name": project_dir_name,
        "title_name": display_name,
        "platform": platform,
        "kind": kind,
        "category": category,
    }


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def render_text(template: str, replacements: dict[str, str]) -> str:
    rendered = template
    for old, new in replacements.items():
        rendered = rendered.replace(old, new)
    return rendered


def normalize_text(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def looks_like_generated_flat_readme(text: str, project_name: str) -> bool:
    required_fragments = (
        f"# {project_name}",
        "Bem-vindo ao desenvolvimento homebrew para **Sega Mega Drive / Genesis**!",
        "## Estrutura do Projeto",
        "meu-projeto/",
        "### O que cada pasta faz?",
        "## Como Comecar",
        "### 2. Rodar no emulador",
    )
    return all(fragment in text for fragment in required_fragments)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def manifest_content(layout: ProjectLayout, metadata: dict[str, str]) -> str:
    payload = {
        "schema_version": 1,
        "display_name": metadata["display_name"],
        "project_root": ".",
        "sgdk_root": "." if layout.entry_root == layout.sgdk_root else layout.sgdk_root.relative_to(layout.entry_root).as_posix(),
        "layout": layout.layout,
        "platform": metadata["platform"],
        "kind": metadata["kind"],
        "category": metadata["category"],
        "notes": "Gerado pela canonicalize_projects.py para o wrapper central do MegaDrive_DEV.",
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def canonical_wrapper_content(project_dir: Path, script_name: str) -> str:
    wrapper_root = WORKSPACE_ROOT / "tools" / "sgdk_wrapper"
    relative = Path(os.path.relpath(wrapper_root, project_dir)).as_posix().replace("/", "\\")
    command = Path(script_name).stem
    return f'@echo off\ncall "%~dp0{relative}\\{command}.bat" "%~dp0"\nexit /b %errorlevel%\n'


def archive_path(project: ProjectLayout, source: Path, bucket: str, timestamp: str) -> Path:
    rel_project = project.entry_root.relative_to(WORKSPACE_ROOT)
    base = ARCHIVE_ROOT / timestamp / rel_project / bucket
    if project.sgdk_root != project.entry_root and source.is_relative_to(project.sgdk_root):
        base = base / "sgdk_root"
    elif source.parent == project.entry_root:
        base = base / "entry_root"
    return base / source.name


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def move_to_archive(project: ProjectLayout, source: Path, bucket: str, timestamp: str, apply: bool, actions: list[str]) -> None:
    destination = archive_path(project, source, bucket, timestamp)
    actions.append(f"archive {source.relative_to(WORKSPACE_ROOT)} -> {destination.relative_to(WORKSPACE_ROOT)}")
    if not apply or not source.exists():
        return
    ensure_parent(destination)
    if destination.exists():
        if destination.is_file():
            destination.unlink()
        else:
            shutil.rmtree(destination)
    shutil.move(str(source), str(destination))


def ensure_file(project: ProjectLayout, path: Path, content: str, bucket: str, timestamp: str, apply: bool, actions: list[str]) -> None:
    if path.exists():
        current = path.read_text(encoding="utf-8", errors="ignore")
        if normalize_text(current) == normalize_text(content):
            return
        move_to_archive(project, path, bucket, timestamp, apply, actions)
    actions.append(f"write {path.relative_to(WORKSPACE_ROOT)}")
    if apply:
        write_text(path, content)


def ensure_missing_file(path: Path, content: str, apply: bool, actions: list[str]) -> None:
    if path.exists():
        return
    actions.append(f"create {path.relative_to(WORKSPACE_ROOT)}")
    if apply:
        write_text(path, content)


def copy_docs_from_template(project: ProjectLayout, metadata: dict[str, str], apply: bool, actions: list[str]) -> None:
    replacements = {
        "__PROJECT_NAME__": metadata["display_name"],
    }

    doc_sources = sorted((TEMPLATE_ROOT / "doc").glob("*.md"))
    if not doc_sources:
        raise RuntimeError("Template canonico sem docs em tools/sgdk_wrapper/modelo/doc")

    for source in doc_sources:
        target = project.entry_root / "doc" / source.name
        template = load_text(source)
        rendered = render_text(template, replacements)
        ensure_missing_file(target, rendered, apply, actions)


def desired_root_readme(project: ProjectLayout, metadata: dict[str, str]) -> tuple[str, str]:
    replacements = {
        "__PROJECT_NAME__": metadata["display_name"],
        "__SGDK_ROOT__": project.sgdk_root.relative_to(project.entry_root).as_posix() if project.sgdk_root != project.entry_root else ".",
    }

    flat_content = render_text(load_text(TEMPLATE_ROOT / "README.md"), replacements)
    if project.layout == "nested":
        nested_content = render_text(load_text(NESTED_TEMPLATE_ROOT / "README.md"), replacements)
        return nested_content, flat_content

    return flat_content, flat_content


def ensure_root_readme(project: ProjectLayout, metadata: dict[str, str], timestamp: str, apply: bool, actions: list[str]) -> None:
    readme_path = project.entry_root / "README.md"
    desired, flat_reference = desired_root_readme(project, metadata)

    if not readme_path.exists():
        actions.append(f"create {readme_path.relative_to(WORKSPACE_ROOT)}")
        if apply:
            write_text(readme_path, desired)
        return

    current = readme_path.read_text(encoding="utf-8", errors="ignore")
    current_norm = normalize_text(current)
    desired_norm = normalize_text(desired)
    flat_norm = normalize_text(flat_reference)

    if current_norm == desired_norm:
        return

    should_replace = current_norm == flat_norm
    if project.layout == "nested" and looks_like_generated_flat_readme(current_norm, metadata["display_name"]):
        should_replace = True

    if should_replace:
        move_to_archive(project, readme_path, "generated_docs", timestamp, apply, actions)
        actions.append(f"write {readme_path.relative_to(WORKSPACE_ROOT)}")
        if apply:
            write_text(readme_path, desired)


def archive_noisy_files(project: ProjectLayout, timestamp: str, apply: bool, actions: list[str]) -> None:
    roots = [project.entry_root]
    if project.sgdk_root != project.entry_root:
        roots.append(project.sgdk_root)

    for root in roots:
        for item in root.iterdir():
            if item.is_dir():
                if project.layout == "nested" and root == project.entry_root and item.name == "out":
                    move_to_archive(project, item, "generated_dirs", timestamp, apply, actions)
                continue

            if item.name.lower() in LEGACY_SCRIPT_NAMES_LOWER:
                move_to_archive(project, item, "legacy_scripts", timestamp, apply, actions)
                continue

            if any(pattern.search(item.name) for pattern in LOG_PATTERNS):
                move_to_archive(project, item, "generated_logs", timestamp, apply, actions)
                continue

            if item.suffix.lower() in ROOT_BIN_EXTENSIONS:
                move_to_archive(project, item, "root_binaries", timestamp, apply, actions)


def archive_orphan_entry_dirs(project: ProjectLayout, timestamp: str, apply: bool, actions: list[str]) -> None:
    if project.layout != "nested":
        return

    for name in ORPHAN_ENTRY_DIR_NAMES:
        candidate = project.entry_root / name
        if candidate.exists():
            move_to_archive(project, candidate, "orphan_dirs", timestamp, apply, actions)


def archive_nested_wrappers(project: ProjectLayout, timestamp: str, apply: bool, actions: list[str]) -> None:
    if project.layout != "nested":
        return

    for wrapper_name in WRAPPER_NAMES:
        candidate = project.sgdk_root / wrapper_name
        if candidate.exists():
            move_to_archive(project, candidate, "legacy_wrappers", timestamp, apply, actions)


def orphan_notes(project: ProjectLayout) -> list[str]:
    notes: list[str] = []
    if project.layout != "nested":
        return notes
    for name in ("src", "res", "inc"):
        candidate = project.entry_root / name
        if candidate.exists():
            notes.append(f"manual-review orphan dir at entry root: {candidate.relative_to(WORKSPACE_ROOT)}")
    return notes


def apply_project(project: ProjectLayout, timestamp: str, apply: bool) -> dict:
    metadata = infer_metadata(project.entry_root.name)
    actions: list[str] = []

    archive_noisy_files(project, timestamp, apply, actions)
    archive_orphan_entry_dirs(project, timestamp, apply, actions)
    archive_nested_wrappers(project, timestamp, apply, actions)

    manifest_path = project.entry_root / ".mddev" / "project.json"
    ensure_missing_file(manifest_path, manifest_content(project, metadata), apply, actions)

    copy_docs_from_template(project, metadata, apply, actions)
    ensure_root_readme(project, metadata, timestamp, apply, actions)

    for wrapper_name in WRAPPER_NAMES:
        ensure_file(
            project,
            project.entry_root / wrapper_name,
            canonical_wrapper_content(project.entry_root, wrapper_name),
            "legacy_wrappers",
            timestamp,
            apply,
            actions,
        )

    warnings = list(project.warnings)
    warnings.extend(orphan_notes(project))

    return {
        "entry_root": project.rel_entry,
        "sgdk_root": project.rel_sgdk,
        "layout": project.layout,
        "reason": project.reason,
        "warnings": warnings,
        "actions": actions,
    }


def main() -> int:
    args = parse_args()
    validate_template_roots()
    roots = list(args.roots)
    if args.include_examples and "examples" not in roots:
        roots.append("examples")

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    entries = iter_project_entries(roots)

    report: list[dict] = []
    failures: list[str] = []

    for entry in entries:
        try:
            layout = detect_layout(entry)
            report.append(apply_project(layout, timestamp, args.apply))
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{entry.relative_to(WORKSPACE_ROOT)}: {exc}")

    summary = {
        "apply": args.apply,
        "roots": roots,
        "processed": len(report),
        "failures": failures,
        "report": report,
    }

    if args.report_json:
        report_path = Path(args.report_json)
        ensure_parent(report_path)
        report_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"[canonicalize] processed={len(report)} apply={args.apply}")
    if failures:
        print(f"[canonicalize] failures={len(failures)}")
        for failure in failures:
            print(f"  - {failure}")

    sample = report[:10]
    for item in sample:
        print(f"- {item['entry_root']} -> {item['sgdk_root']} [{item['layout']}] actions={len(item['actions'])}")
        for warning in item["warnings"][:3]:
            print(f"    warning: {warning}")

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
