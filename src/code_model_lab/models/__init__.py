import os
from typing import Dict, Any

from code_model_lab.models.ollama_client import OllamaClient
from code_model_lab.models.hf_client import HFClient

def get_model_client(m_config: Dict[str, Any]) -> Any:
    """
    Returns the appropriate model client instance based on config parameters.
    """
    model_type = m_config.get("model_type", "ollama")
    eval_mode = os.getenv("EVAL_MODE", m_config.get("eval_mode", "mock"))
    
    if eval_mode == "mock":
        # Always default to OllamaClient's mock implementation
        return OllamaClient(eval_mode="mock")
        
    if model_type == "hf":
        model_name = m_config.get("model_name", "Qwen/Qwen2.5-Coder-7B-Instruct")
        adapter_path = m_config.get("adapter_path")
        load_in_4bit = m_config.get("load_in_4bit", True)
        return HFClient(
            model_id=model_name,
            adapter_path=adapter_path,
            load_in_4bit=load_in_4bit
        )
    else:
        # Default to Ollama/API completions client
        return OllamaClient(
            model_name=m_config.get("model_name", "qwen2.5-coder:7b"),
            api_base=m_config.get("api_base", "http://localhost:11434/api"),
            eval_mode=eval_mode,
            timeout=m_config.get("timeout", 300.0),
        )
