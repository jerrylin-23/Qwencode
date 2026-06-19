import json
from pathlib import Path
from typing import Dict, Any
from code_model_lab.models.ollama_client import OllamaClient
from code_model_lab.models import prompt_templates
from code_model_lab.repo_repair.index_repo import index_repository

def localize_bug(repo_path: Path, issue_desc: str, client: OllamaClient) -> Dict[str, Any]:
    """
    Identifies the files and symbols likely causing the bug described in the issue.
    """
    file_list = index_repository(repo_path)
    
    prompt = prompt_templates.REPO_REPAIR_LOCALIZE.format(
        issue=issue_desc,
        file_list=json.dumps(file_list, indent=2)
    )
    
    response = client.generate(prompt, temperature=0.0)
    
    # Try parsing response as JSON
    try:
        # Find JSON block if it's wrapped in markdown
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            json_str = response.split("```")[1].split("```")[0].strip()
        else:
            json_str = response.strip()
            
        data = json.loads(json_str)
        # Verify structure
        if "likely_files" in data:
            return data
    except Exception:
        pass
        
    # Fallback to simple matching if parsing fails or client outputs prose
    likely_files = []
    for f in file_list:
        # If the file base name (e.g. calculator) is mentioned in the issue
        f_name = Path(f).stem
        if f_name.lower() in issue_desc.lower():
            likely_files.append({"path": f, "reason": "File name matches issue description keywords."})
            
    if not likely_files and file_list:
        likely_files.append({"path": file_list[0], "reason": "Default file fallback."})
        
    return {
        "likely_files": likely_files,
        "likely_symbols": []
    }
