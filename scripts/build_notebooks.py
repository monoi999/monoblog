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

TOGGLE_STYLE = """
<style>
.output-toggle-button {
    margin: 6px 0 10px calc(var(--jp-cell-prompt-width) + 12px);
    padding: 6px 12px;
    border: 1px solid #d0d7de;
    border-radius: 6px;
    background: #f6f8fa;
    color: #24292f;
    cursor: pointer;
    font-size: 0.95rem;
}
.output-toggle-button:hover {
    background: #eef3f8;
}
</style>
"""

TOGGLE_SCRIPT = """
<script>
document.addEventListener('DOMContentLoaded', function () {
    const wrappers = document.querySelectorAll('.jp-Cell-outputWrapper');

    wrappers.forEach(function (wrapper) {
        if (wrapper.dataset.toggleReady === 'true') {
            return;
        }
        if (!wrapper.querySelector('.jp-OutputArea-child')) {
            return;
        }

        wrapper.dataset.toggleReady = 'true';
        wrapper.style.display = 'none';

        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'output-toggle-button';
        button.setAttribute('aria-expanded', 'false');
        button.textContent = '▶ 실행결과 보기';

        button.addEventListener('click', function () {
            const isHidden = wrapper.style.display === 'none';
            wrapper.style.display = isHidden ? '' : 'none';
            button.setAttribute('aria-expanded', isHidden ? 'true' : 'false');
            button.textContent = isHidden ? '▼ 실행결과 숨기기' : '▶ 실행결과 보기';
        });

        wrapper.parentNode.insertBefore(button, wrapper);
    });
});
</script>
"""


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


def add_output_toggles(html_path: Path) -> None:
    html = html_path.read_text(encoding="utf-8")
    if "output-toggle-button" in html:
        return

    if "</head>" not in html or "</body>" not in html:
        raise RuntimeError(f"Unexpected HTML structure: {html_path}")

    html = html.replace("</head>", f"{TOGGLE_STYLE}\n</head>", 1)
    html = html.replace("</body>", f"{TOGGLE_SCRIPT}\n</body>", 1)
    html_path.write_text(html, encoding="utf-8")


def main() -> int:
    notebooks = iter_notebooks()
    if not notebooks:
        print("No notebooks found.")
        return 0

    for notebook in notebooks:
        html_path = convert_notebook(notebook)
        add_output_toggles(html_path)
        print(f"Converted: {notebook.relative_to(ROOT)} -> {html_path.relative_to(ROOT)}")

        alias_target = ALIASES.get(notebook)
        if alias_target:
            alias_target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(html_path, alias_target)
            print(f"Updated alias: {alias_target.relative_to(ROOT)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
