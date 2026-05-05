from __future__ import annotations

import shutil
from pathlib import Path


def safe_remove_file(path: Path) -> None:
    """
    Safely remove a file if it exists.
    On Windows, ignore permission errors if the file is still temporarily locked.
    """
    try:
        if path.exists() and path.is_file():
            path.unlink()
    except PermissionError:
        pass


def safe_remove_dir(path: Path) -> None:
    """
    Safely remove a directory if it exists.
    """
    if path.exists() and path.is_dir():
        shutil.rmtree(path, ignore_errors=True)