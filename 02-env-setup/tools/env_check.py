import os
import platform
import sys
from pathlib import Path


def main():
    print("=== Environment Check ===")
    print(f"OS: {platform.system()} {platform.release()} ({platform.version()})")
    print(f"Python: {platform.python_version()} | Executable: {sys.executable}")
    print(f"Encoding: fs={sys.getfilesystemencoding()} | stdout={sys.stdout.encoding}")

    # venv detection
    in_venv = (hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))
    print(f"In venv: {in_venv}")
    if in_venv:
        scripts_dir = Path(sys.prefix) / ("Scripts" if os.name == "nt" else "bin")
        print(f"Venv path: {sys.prefix}")
        print(f"Venv Scripts: {scripts_dir}")

    # repo root guess: two levels up from this file
    repo_root = Path(__file__).resolve().parents[2]
    print(f"Repo root: {repo_root}")

    # simple write test to docs
    docs_dir = repo_root / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    marker = docs_dir / "env_check_ok.txt"
    marker.write_text("env_check: ok\n", encoding="utf-8")
    print(f"Wrote marker: {marker}")

    print("=== OK ===")


if __name__ == "__main__":
    main()
