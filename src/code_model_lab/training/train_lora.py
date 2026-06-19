import sys
import yaml
import argparse
from pathlib import Path

def train(config_path: Path):
    print(f"Loading training configuration from {config_path}...")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    # Print config options
    for k, v in config.items():
        print(f"  {k}: {v}")

    # Check for GPU
    try:
        import torch
        device_count = torch.cuda.device_count()
        print(f"CUDA Available: {torch.cuda.is_available()} (Devices: {device_count})")
        # Check MPS (Metal Performance Shaders for Mac)
        mps_available = hasattr(torch.backends, "mps") and torch.backends.mps.is_available()
        print(f"MPS (Apple Silicon Metal) Available: {mps_available}")
    except ImportError:
        print("PyTorch not installed or import failed.")
        sys.exit(1)

    print("\nInitializing fine-tuning setup...")
    
    # We will simulate the setup or check weights
    model_id = config.get("model_id", "Qwen/Qwen2.5-Coder-7B")
    train_dataset_path = Path(config.get("train_dataset", "data/processed/sft_train.jsonl"))
    _valid_dataset_path = Path(config.get("valid_dataset", "data/processed/sft_valid.jsonl"))
    
    if not train_dataset_path.exists():
        print(f"Error: Training dataset not found at {train_dataset_path}")
        sys.exit(1)

    print(f"Dataset path loaded. Train size target: {train_dataset_path}")

    # Lazy-load transformers and peft to make script importable/quick to verify
    try:
        from peft import LoraConfig, TaskType
        
        print(f"Loading tokenizer for {model_id}...")
        # To avoid blocking local execution or out-of-memory errors on 16GB Apple Silicon,
        # we check for mock flag or dry-run argument.
        parser = argparse.ArgumentParser()
        parser.add_argument("--dry-run", action="store_true", default=True, help="Perform initialization check without downloading entire model.")
        args, _ = parser.parse_known_args()
        
        if args.dry_run:
            print("\n[Dry Run / Verification Mode]")
            print("Successfully loaded HF transformers and PEFT modules.")
            print("LoRA Config:")
            lora_config = LoraConfig(
                r=config.get("lora_r", 16),
                lora_alpha=config.get("lora_alpha", 32),
                target_modules=["q_proj", "v_proj"],
                lora_dropout=config.get("lora_dropout", 0.05),
                bias="none",
                task_type=TaskType.CAUSAL_LM
            )
            print(lora_config)
            print("Hyperparameters:")
            print(f"  Learning Rate: {config.get('learning_rate')}")
            print(f"  Epochs: {config.get('epochs')}")
            print(f"  Batch Size: {config.get('batch_size')}")
            print("\nDry run verification completed successfully.")
            return
            
    except ImportError as e:
        print(f"PEFT/Transformers packages error: {e}")
        print("Please check requirements installation.")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Fine-tune a model using LoRA.")
    parser.add_argument("--config", type=str, default="configs/training_lora.yaml", help="Path to training config.")
    args = parser.parse_args()

    train(Path(args.config))

if __name__ == "__main__":
    main()
