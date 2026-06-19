import re
from pathlib import Path

def apply_patch_to_repo(repo_path: Path, patch_content: str) -> bool:
    """
    Parses and applies a unified diff patch to a repository.
    Returns True if successfully applied, False otherwise.
    """
    if not patch_content.strip():
        return False

    # Standardize path headers and split diff by files
    # Typically patches have:
    # diff --git a/path/to/file b/path/to/file
    # --- a/path/to/file
    # +++ b/path/to/file
    file_patches = re.split(r"^diff --git ", patch_content, flags=re.MULTILINE)
    
    # If the patch doesn't start with "diff --git ", try split by "--- "
    if len(file_patches) <= 1:
        # Try split by --- 
        file_patches = re.split(r"^--- ", patch_content, flags=re.MULTILINE)
        # We need to prepend the splitter back for parsing if necessary, or parse directly
        
    success = False
    
    for file_patch in file_patches:
        if not file_patch.strip():
            continue
            
        # Extract file path
        # Try to find: --- a/src/calculator.py or --- src/calculator.py
        file_path_match = re.search(r"^--- (?:a/)?([^\n]+)", file_patch, re.MULTILINE)
        if not file_path_match:
            continue
            
        rel_file_path = file_path_match.group(1).strip()
        # Clean potential comments or dev/null indicators
        if rel_file_path.startswith("/dev/null") or " " in rel_file_path:
            # check the +++ line instead
            added_path_match = re.search(r"^\+\+\+ (?:b/)?([^\n]+)", file_patch, re.MULTILINE)
            if added_path_match:
                rel_file_path = added_path_match.group(1).strip()
                
        target_file = repo_path / rel_file_path
        if not target_file.exists():
            # Try to resolve relative path issues (e.g. if b/src/calculator.py -> src/calculator.py)
            cleaned_path = rel_file_path.replace("a/", "", 1).replace("b/", "", 1)
            target_file = repo_path / cleaned_path
            if not target_file.exists():
                print(f"File patch target does not exist: {target_file}")
                continue

        # Extract all hunks in this file patch
        hunks = re.split(r"^@@", file_patch, flags=re.MULTILINE)
        if len(hunks) <= 1:
            continue
            
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                file_lines = f.read().splitlines()
        except Exception as e:
            print(f"Error reading file {target_file}: {e}")
            continue

        modified_lines = list(file_lines)
        
        hunks_applied = 0
        for hunk in hunks[1:]:
            hunk_lines = hunk.splitlines()
            if not hunk_lines:
                continue
                
            # Hunk header is like: -10,3 +10,5 @@
            # Let's extract the lines to find and lines to replace
            find_lines = []
            replace_lines = []
            
            for line in hunk_lines[1:]: # Skip the header info line
                if line.startswith("-"):
                    find_lines.append(line[1:])
                elif line.startswith("+"):
                    replace_lines.append(line[1:])
                elif line.startswith(" "):
                    find_lines.append(line[1:])
                    replace_lines.append(line[1:])
                elif line.startswith("\\"):
                    # No newline at end of file indicator, skip
                    continue
                else:
                    # Treat as context
                    find_lines.append(line)
                    replace_lines.append(line)

            # Try to locate find_lines in modified_lines
            # We will use sliding window search
            found_idx = -1
            n_find = len(find_lines)
            
            if n_find == 0:
                # Append to end of file if it's purely addition
                modified_lines.extend(replace_lines)
                hunks_applied += 1
                continue

            for i in range(len(modified_lines) - n_find + 1):
                window = modified_lines[i : i + n_find]
                # Compare strip versions to handle minor indentation issues
                if all(w.strip() == f.strip() for w, f in zip(window, find_lines)):
                    found_idx = i
                    break
                    
            if found_idx != -1:
                # Replace the matched section with replace_lines
                modified_lines[found_idx : found_idx + n_find] = replace_lines
                hunks_applied += 1
            else:
                print(f"Warning: Could not match hunk in {target_file.name}")
                print(f"Hunk search lines: {find_lines}")
                
        if hunks_applied > 0:
            try:
                with open(target_file, "w", encoding="utf-8") as f:
                    f.write("\n".join(modified_lines) + "\n")
                success = True
            except Exception as e:
                print(f"Error writing file {target_file}: {e}")
                
    return success
