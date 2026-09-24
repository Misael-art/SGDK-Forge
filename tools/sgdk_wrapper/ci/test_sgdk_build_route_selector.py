#!/usr/bin/env python3
"""Regression tests for select_sgdk_build_route.py."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "select_sgdk_build_route.py"
SPEC = importlib.util.spec_from_file_location("sgdk_build_route_selector", SCRIPT)
assert SPEC and SPEC.loader
SELECTOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SELECTOR)


def make_fixture(
    root: Path,
    *,
    compiler: str = "13.2.0",
    source_producer: str = "16.1.0",
    source_lto: bool = True,
    staged_producer: str | None = "13.2.0",
    staged_lto: bool = False,
    bridge: bool = True,
) -> Path:
    gdk = root / "sdk/sgdk-2.11"
    (gdk / "bin").mkdir(parents=True)
    (gdk / "lib").mkdir(parents=True)
    (gdk / "makefile.gen").write_text("# fixture\n", encoding="utf-8")
    (gdk / "bin/gcc.exe").write_bytes(
        f"/x-tools/m68k-elf/{compiler}/include".encode("ascii")
    )
    lto_marker = b" .gnu.lto_fixture" if source_lto else b""
    (gdk / "lib/libmd.a").write_bytes(
        f"GCC: (GNU) {source_producer}".encode("ascii") + lto_marker
    )
    (root / "tools/sgdk_wrapper").mkdir(parents=True)
    (root / "tools/sgdk_wrapper/build.bat").write_text("@echo off\n", encoding="utf-8")
    if bridge:
        (root / "tools/sgdk_wrapper/build_sgdk_wine_bridge.sh").write_text(
            "#!/usr/bin/env bash\n", encoding="utf-8"
        )
    if staged_producer:
        staged = root / "out/host_tools/sgdk_wine_flatpak/sgdk-2.11/lib"
        staged.mkdir(parents=True)
        staged_marker = b" .gnu.lto_fixture" if staged_lto else b""
        (staged / "libmd.a").write_bytes(
            f"GCC: (crosstool-NG UNKNOWN) {staged_producer}".encode("ascii")
            + staged_marker
        )
    project = root / "SGDK_projects/example"
    project.mkdir(parents=True)
    return project


class BuildRouteSelectorTests(unittest.TestCase):
    def test_linux_mismatch_selects_isolated_bridge(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = make_fixture(root)
            report = SELECTOR.build_report(root, project, "linux")
            self.assertEqual(report["status"], "ready")
            self.assertEqual(report["selected_route"], "linux_wine_bridge")
            self.assertFalse(report["source_library"]["direct_link_compatible"])
            self.assertTrue(report["linux_stage"]["link_compatible"])
            self.assertFalse(report["linux_stage"]["source_sdk_mutated"])

    def test_linux_missing_bridge_blocks_before_build(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = make_fixture(root, bridge=False)
            report = SELECTOR.build_report(root, project, "linux")
            self.assertEqual(report["status"], "blocked")
            self.assertIn(
                "linux_wine_bridge_missing",
                {item["code"] for item in report["blockers"]},
            )

    def test_windows_coherent_source_sdk_uses_batch_wrapper(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = make_fixture(root, source_producer="13.2.0")
            report = SELECTOR.build_report(root, project, "windows")
            self.assertEqual(report["status"], "ready")
            self.assertEqual(report["selected_route"], "windows_batch_wrapper")
            self.assertTrue(report["source_library"]["direct_link_compatible"])
            self.assertTrue(report["command"].startswith("cmd.exe /d /c "))
            self.assertNotIn("'", report["command"])

    def test_windows_lto_mismatch_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = make_fixture(root)
            report = SELECTOR.build_report(root, project, "windows")
            self.assertEqual(report["status"], "blocked")
            self.assertIn(
                "source_sdk_lto_version_mismatch",
                {item["code"] for item in report["blockers"]},
            )

    def test_non_lto_source_library_does_not_require_same_major(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = make_fixture(root, source_lto=False)
            report = SELECTOR.build_report(root, project, "windows")
            self.assertEqual(report["status"], "ready")
            self.assertTrue(report["source_library"]["direct_link_compatible"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
