import os
from pathlib import Path
from typing import List

def index_repository(repo_path: Path) -> List[str]:
    """
    Returns a list of all source files in the repository (excluding tests, caches, etc.).
    """
    files = []
    for root, _, filenames in os.walk(repo_path):
        for name in filenames:
            file_path = Path(root) / name
            rel_path = file_path.relative_to(repo_path)
            
            # Skip hidden files, tests, and non-python files
            if any(part.startswith(".") for part in rel_path.parts):
                continue
            if "tests" in rel_path.parts:
                continue
            if "__pycache__" in rel_path.parts:
                continue
            if rel_path.suffix != ".py":
                continue
                
            files.append(str(rel_path))
    return sorted(files)
