from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEARCH_DIRS = [ROOT / "study"]
ALIASES = {
    ROOT / "study" / "chap2_example.ipynb": ROOT / "chap2_notebook.html",
}


def iter_notebooks() -> list[Path]:
    notebooks: list[Path] = []
    for base in SEARCH_DIRS:
        if not base.exists():
            continue
        for path in base.rglob("*.ipynb"):
            if ".ipynb_checkpoints" in path.parts:
                continue
            notebooks.append(path)
    return sorted(notebooks)


def convert_notebook(notebook: Path) -> Path:
    output_dir = notebook.parent
    cmd = [
        sys.executable,
        "-m",
        "jupyter",
        "nbconvert",
        "--to",
        "html",
        str(notebook),
        "--output",
        notebook.stem,
        "--output-dir",
        str(output_dir),
    ]
    subprocess.run(cmd, check=True)
    return output_dir / f"{notebook.stem}.html"


def main() -> int:
    notebooks = iter_notebooks()
    if not notebooks:
        print("No notebooks found.")
        return 0

    for notebook in notebooks:
        html_path = convert_notebook(notebook)
        print(f"Converted: {notebook.relative_to(ROOT)} -> {html_path.relative_to(ROOT)}")

        alias_target = ALIASES.get(notebook)
        if alias_target:
            alias_target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(html_path, alias_target)
            print(f"Updated alias: {alias_target.relative_to(ROOT)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
