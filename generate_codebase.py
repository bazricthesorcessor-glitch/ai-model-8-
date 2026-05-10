#!/usr/bin/env python3

from pathlib import Path
import fnmatch

OUTPUT_FILE = "codebase_full.txt"

IGNORE_DIRS = {
    ".git",
    "__pycache__",
    "venv",
    ".venv",
    "node_modules",
    ".mypy_cache",
    ".pytest_cache",
    ".idea",
    ".vscode",
}

IGNORE_FILES = {
    OUTPUT_FILE,
}

IGNORE_PATTERNS = [
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "*.so",
    "*.dll",
    "*.exe",
    "*.bin",
    "*.safetensors",
    "*.gguf",
    "*.png",
    "*.jpg",
    "*.jpeg",
    "*.gif",
    "*.mp4",
    "*.mp3",
    "*.wav",
]

ROOT = Path(".").resolve()


def should_ignore(path: Path) -> bool:
    for part in path.parts:
        if part in IGNORE_DIRS:
            return True

    if path.name in IGNORE_FILES:
        return True

    for pattern in IGNORE_PATTERNS:
        if fnmatch.fnmatch(path.name, pattern):
            return True

    return False


all_files = []

for path in ROOT.rglob("*"):
    if path.is_file() and not should_ignore(path):
        all_files.append(path)

all_files.sort()

with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
    outfile.write("=" * 80 + "\n")
    outfile.write("FULL CODEBASE EXPORT\n")
    outfile.write("=" * 80 + "\n\n")

    for file_path in all_files:
        relative_path = file_path.relative_to(ROOT)

        outfile.write("\n")
        outfile.write("=" * 80 + "\n")
        outfile.write(f"FILE: {relative_path}\n")
        outfile.write("=" * 80 + "\n\n")

        try:
            content = file_path.read_text(encoding="utf-8")

            outfile.write(content)

        except Exception as e:
            outfile.write(f"\n[ERROR READING FILE: {e}]\n")

        outfile.write("\n\n")

print(f"Done. Output written to: {OUTPUT_FILE}")
