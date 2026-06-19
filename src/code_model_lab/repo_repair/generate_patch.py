import re
from pathlib import Path
from code_model_lab.models.ollama_client import OllamaClient
from code_model_lab.models import prompt_templates
from code_model_lab.repo_repair.retrieve_context import retrieve_file_contexts

def extract_patch(model_output: str) -> str:
    """
    Extracts the unified diff patch from the model output.
    """
    # Look for diff block
    pattern = r"```diff\n(.*?)\n```"
    matches = re.findall(pattern, model_output, re.DOTALL)
    if matches:
        return matches[0]
        
    pattern_generic = r"```\n(.*?)\n```"
    matches_generic = re.findall(pattern_generic, model_output, re.DOTALL)
    if matches_generic and "diff" in matches_generic[0]:
        return matches_generic[0]
        
    # Check if output contains a diff directly
    if "diff --git" in model_output:
        lines = model_output.splitlines()
        cleaned = []
        in_diff = False
        for line in lines:
            if line.startswith("diff --git") or line.startswith("---") or line.startswith("+++"):
                in_diff = True
            if in_diff:
                cleaned.append(line)
        if cleaned:
            return "\n".join(cleaned)
            
    return model_output

def generate_bug_patch(repo_path: Path, issue_desc: str, likely_files: list, client: OllamaClient) -> str:
    """
    Generates a unified diff patch to repair the repository.
    """
    context = retrieve_file_contexts(repo_path, [f["path"] for f in likely_files])
    
    prompt = prompt_templates.REPO_REPAIR_PATCH.format(
        issue=issue_desc,
        context=context
    )
    
    response = client.generate(prompt, temperature=0.0)
    return extract_patch(response)
