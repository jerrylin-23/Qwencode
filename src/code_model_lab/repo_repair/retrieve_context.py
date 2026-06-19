from pathlib import Path

def retrieve_file_contexts(repo_path: Path, files: list) -> str:
    """
    Reads the content of specified files and returns a structured string.
    """
    context = []
    for file_rel_path in files:
        full_path = repo_path / file_rel_path
        if full_path.exists():
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
                context.append(f"--- File: {file_rel_path} ---\n{content}\n")
            except Exception as e:
                context.append(f"--- File: {file_rel_path} (Error reading: {e}) ---\n")
        else:
            context.append(f"--- File: {file_rel_path} (File not found) ---\n")
    return "\n".join(context)
