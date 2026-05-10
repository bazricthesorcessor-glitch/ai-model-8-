import os
import subprocess
from pathlib import Path
from datetime import datetime

commit_message = (
    "Update codebase snapshot - "
    + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
)
ROOT_DIR = Path.home() / "ai-model-8"

CODEBASE_FILE = ROOT_DIR / "codebase.txt"
TREE_FILE = ROOT_DIR / "tree.txt"

IGNORE_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "node_modules",
}

IGNORE_FILES = {
    "codebase.txt",
    "tree.txt",
}


# =========================
# STEP 1 — GENERATE CODEBASE
# =========================

with open(CODEBASE_FILE, "w", encoding="utf-8") as outfile:

    for path in ROOT_DIR.rglob("*"):

        if any(part in IGNORE_DIRS for part in path.parts):
            continue

        if path.name in IGNORE_FILES:
            continue

        if path.is_file():

            try:

                relative = path.relative_to(ROOT_DIR)

                outfile.write("\n")
                outfile.write("=" * 80 + "\n")
                outfile.write(f"FILE: {relative}\n")
                outfile.write("=" * 80 + "\n\n")

                content = path.read_text(encoding="utf-8")

                outfile.write(content)
                outfile.write("\n\n")

            except Exception as e:

                outfile.write(f"\nERROR READING {path}: {e}\n")


print("Updated codebase.txt")


# =========================
# STEP 2 — GENERATE TREE
# =========================

result = subprocess.run(
    ["tree", "-L", "99"],
    cwd=ROOT_DIR,
    capture_output=True,
    text=True
)

TREE_FILE.write_text(result.stdout, encoding="utf-8")

print("Updated tree.txt")


# =========================
# STEP 3 — GIT COMMIT
# =========================

subprocess.run(["git", "add", "."], cwd=ROOT_DIR)

subprocess.run(
    ["git", "commit", "-m", commit_message],
    cwd=ROOT_DIR
)

subprocess.run(
    ["git", "push", "origin", "main"],
    cwd=ROOT_DIR
)

print("Pushed to GitHub")
