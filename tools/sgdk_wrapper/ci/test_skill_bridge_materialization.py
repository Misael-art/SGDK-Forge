"""Skill bridge materialization gate (P0-000).

Guards the `.agents/skills` compatibility bridge.

Why this gate exists
--------------------
The bridge used to be committed as an ABSOLUTE symlink pointing at
``F:/Projects/Sgdk Forge/tools/sgdk_wrapper/.agent/skills``. That target is a
Windows drive path, so:

* on Linux the link never resolved;
* in any fresh clone the entry materialized as a 55-byte regular file;
* ``validate_skill_framework.py`` then failed with a bridge mismatch.

The consequence was worse than a broken link: the framework could not be
validated in a clean checkout at all, so every conformance claim had to be made
from a dirty worktree. This gate makes that regression impossible to
reintroduce silently.

Contract
--------
1. ``.agents/skills`` exists and is a real link, never a regular file. A
   regular file here means the checkout materialized the link as text.
2. The link target is RELATIVE. An absolute target cannot survive being cloned
   to a different root or a different operating system.
3. The target resolves to ``tools/sgdk_wrapper/.agent/skills`` -- the single
   canonical source of skills.
4. The resolved directory actually exposes skills.

On Windows the same path is materialized as a directory junction. Python's
``os.path.islink`` returns False for junctions, so the check accepts a reparse
point as an equivalent materialization instead of demanding a POSIX symlink.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BRIDGE = ROOT / ".agents" / "skills"
CANONICAL = ROOT / "tools" / "sgdk_wrapper" / ".agent" / "skills"

failures: list = []
passed = 0


def check(label, condition, detail=""):
    global passed
    if condition:
        passed += 1
        print("[ok]   " + label)
        return True
    failures.append(label + ": " + detail)
    print("[FAIL] " + label + ": " + detail)
    return False


def is_reparse_point(path):
    """Directory junctions are how Windows materializes this bridge."""
    if os.name != "nt":
        return False
    try:
        return bool(getattr(path.lstat(), "st_reparse_tag", 0))
    except OSError:
        return False


def main():
    if not check("bridge entry exists",
                 BRIDGE.is_symlink() or BRIDGE.exists(),
                 str(BRIDGE) + " not found"):
        return report()

    is_link = BRIDGE.is_symlink() or is_reparse_point(BRIDGE)
    check(
        "bridge is a link, not a materialized regular file",
        is_link,
        str(BRIDGE) + " is a regular file -- the checkout turned the link into "
        "text, which is what an absolute or cross-OS target produces",
    )

    if BRIDGE.is_symlink():
        target = os.readlink(BRIDGE)
        check(
            "link target is relative",
            not os.path.isabs(target) and ":" not in target,
            "target " + repr(target) + " is absolute; it cannot survive a "
            "different checkout root or a different OS",
        )

    if not is_link:
        return report()

    try:
        resolved = BRIDGE.resolve(strict=True)
    except OSError as exc:
        check("link resolves", False, str(exc))
        return report()

    check(
        "link resolves to the canonical skills root",
        resolved == CANONICAL.resolve(),
        "resolved to " + str(resolved) + ", expected " + str(CANONICAL.resolve()),
    )
    check("resolved target is a directory", resolved.is_dir(),
          str(resolved) + " is not a directory")

    skills = sorted(resolved.rglob("SKILL.md")) if resolved.is_dir() else []
    check("bridge exposes at least one skill", len(skills) > 0,
          "no SKILL.md reachable through the bridge")
    if skills:
        print("       (" + str(len(skills)) + " skills visible through the bridge)")

    return report()


def report():
    total = passed + len(failures)
    print()
    if failures:
        print("skill bridge materialization: " + str(passed) + "/" + str(total)
              + " passed, " + str(len(failures)) + " failed")
        for item in failures:
            print("- " + item)
        return 1
    print("skill bridge materialization: " + str(passed) + "/" + str(total)
          + " passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
