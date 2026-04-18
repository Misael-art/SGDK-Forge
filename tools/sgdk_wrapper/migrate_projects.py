import subprocess
import sys
from pathlib import Path


def main() -> int:
    script = Path(__file__).with_name("canonicalize_projects.py")
    command = [sys.executable, str(script), "--apply", *sys.argv[1:]]
    return subprocess.call(command)


if __name__ == "__main__":
    raise SystemExit(main())
