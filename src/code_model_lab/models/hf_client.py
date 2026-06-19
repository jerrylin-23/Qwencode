import os
import torch
from typing import Optional

class HFClient:
    def __init__(self, model_id: str, adapter_path: Optional[str] = None, load_in_4bit: bool = True):
        self.model_id = model_id
        self.adapter_path = adapter_path
        self.load_in_4bit = load_in_4bit
        self.device = "cuda" if torch.cuda.is_available() else ("mps" if hasattr(torch.backends, "mps") and torch.backends.mps.is_available() else "cpu")
        
        print(f"Loading Hugging Face model: {model_id} on {self.device}...")
        
        # Lazy-import inside init to prevent import weight penalties for offline/mock scripts
        from transformers import AutoTokenizer, AutoModelForCausalLM
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # If running on CPU or Mac, disable 4-bit bitsandbytes quantization as it is Linux/CUDA-only
        if self.device == "cuda" and load_in_4bit:
            from transformers import BitsAndBytesConfig
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=torch.bfloat16
            )
            self.model = AutoModelForCausalLM.from_pretrained(
                model_id,
                quantization_config=bnb_config,
                device_map="auto"
            )
        else:
            # CPU/Metal fallback
            torch_dtype = torch.float16 if self.device != "cpu" else torch.float32
            self.model = AutoModelForCausalLM.from_pretrained(
                model_id,
                torch_dtype=torch_dtype,
                device_map="auto" if self.device != "cpu" else None
            )
            if self.device == "cpu":
                self.model = self.model.to(self.device)

        # Apply LoRA adapter if provided
        if adapter_path and os.path.exists(adapter_path):
            print(f"Applying LoRA adapter from {adapter_path}...")
            from peft import PeftModel
            self.model = PeftModel.from_pretrained(self.model, adapter_path)
            
        self.model.eval()

    def generate(self, prompt: str, temperature: float = 0.0, max_tokens: int = 2048) -> str:
        # Wrap prompt in standard Qwen chat template if appropriate
        messages = [{"role": "user", "content": prompt}]
        
        # Use tokenizer chat template formatting
        try:
            formatted_prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        except Exception:
            # Fallback format if template fails
            formatted_prompt = f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
            
        inputs = self.tokenizer(formatted_prompt, return_tensors="pt").to(self.device)
        
        # Configure generation parameters
        gen_kwargs = {
            "max_new_tokens": max_tokens,
            "do_sample": temperature > 0.0,
            "pad_token_id": self.tokenizer.pad_token_id or self.tokenizer.eos_token_id
        }
        if temperature > 0.0:
            gen_kwargs["temperature"] = temperature
            
        with torch.no_grad():
            outputs = self.model.generate(**inputs, **gen_kwargs)
            
        # Decode only the generated response (excluding the input prompt tokens)
        input_len = inputs.input_ids.shape[1]
        generated_tokens = outputs[0][input_len:]
        
        return self.tokenizer.decode(generated_tokens, skip_special_tokens=True)
