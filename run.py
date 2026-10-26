"""Prepare the virtual environment and start the application."""

import os
import sys
import subprocess
import venv
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
VENV_DIR = PROJECT_DIR / ".venv"
REQUIREMENTS_FILE = PROJECT_DIR / "requirements.txt"
MAIN_FILE = PROJECT_DIR / "main.py"


def venv_python():
    """Return the Python executable inside the project's virtual environment."""
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def ensure_venv():
    python_executable = venv_python()
    if not python_executable.is_file():
        print("Creating virtual environment...")
        venv.create(VENV_DIR, with_pip=True)
    return python_executable


def install_dependencies(python_executable):
    if not REQUIREMENTS_FILE.is_file():
        raise FileNotFoundError(f"{REQUIREMENTS_FILE.name} was not found.")

    print("Checking dependencies...")
    subprocess.check_call(
        [
            str(python_executable),
            "-m",
            "pip",
            "install",
            "-r",
            str(REQUIREMENTS_FILE),
        ],
        cwd=PROJECT_DIR,
    )


def main():
    python_executable = ensure_venv()
    install_dependencies(python_executable)

    print("Starting Focus Timer...")
    os.execv(
        str(python_executable),
        [str(python_executable), str(MAIN_FILE), *sys.argv[1:]],
    )


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, subprocess.CalledProcessError) as error:
        print(f"Could not prepare or start the application: {error}", file=sys.stderr)
        raise SystemExit(1) from error
