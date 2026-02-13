"""
Ultimate Law LoRA Fine-Tuning Script
=====================================
Uses Unsloth for 2-5x faster QLoRA training on RTX 5090 (32GB VRAM).

Two-phase training:
  Phase 1: Raw text (corpus/dictionary) — teaches vocabulary and definitions
  Phase 2: Chat pairs (dialogues/cases) — teaches reasoning patterns

Usage:
  python train_qlora.py                    # Default: qwen3-8b
  python train_qlora.py --model qwen3-32b  # Larger model
  python train_qlora.py --model gemma3-4b  # Smaller model
  python train_qlora.py --phase 1          # Raw text only
  python train_qlora.py --phase 2          # Chat pairs only
"""

import argparse
import os
import torch

# MUST import unsloth first (patches transformers/trl/peft)
from unsloth import FastLanguageModel
from trl import SFTTrainer, SFTConfig
from datasets import load_dataset, Dataset

# === Configuration ===

MODELS = {
    "qwen3-8b": "unsloth/Qwen3-8B",
    "qwen3-4b": "unsloth/Qwen3-4B",
    "qwen3-32b": "unsloth/Qwen3-32B",
    "gemma3-4b": "unsloth/gemma-3-4b-it",
    "gemma3-12b": "unsloth/gemma-3-12b-it",
    "llama-8b": "unsloth/Llama-3.1-8B-Instruct",
}

TRAINING_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_TEXT_FILE = os.path.join(TRAINING_DIR, "ul_raw_text.txt")
CHAT_PAIRS_FILE = os.path.join(TRAINING_DIR, "ul_chat_pairs.jsonl")
OUTPUT_DIR = os.path.join(TRAINING_DIR, "output")

# LoRA hyperparameters
LORA_R = 32                # Rank (32 for small dataset, increase to 64 for larger)
LORA_ALPHA = 32            # Usually = r
LORA_DROPOUT = 0.0         # 0 is optimized by Unsloth
MAX_SEQ_LENGTH = 4096      # Context window for training
LEARNING_RATE = 2e-4
EPOCHS = 3
BATCH_SIZE = 2
GRAD_ACCUM = 4


def load_model(model_key):
    """Load base model with 4-bit quantization."""
    model_name = MODELS.get(model_key, model_key)
    print(f"\nLoading model: {model_name}")
    print(f"Max sequence length: {MAX_SEQ_LENGTH}")
    print(f"Loading in 4-bit (QLoRA)...")

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_name,
        max_seq_length=MAX_SEQ_LENGTH,
        load_in_4bit=True,
        dtype=None,  # Auto-detect (bf16 on Ampere+)
    )

    # Apply LoRA adapters
    model = FastLanguageModel.get_peft_model(
        model,
        r=LORA_R,
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj",
        ],
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=3407,
        max_seq_length=MAX_SEQ_LENGTH,
    )

    return model, tokenizer


def train_phase1_raw_text(model, tokenizer, model_key):
    """Phase 1: Train on raw text corpus (vocabulary and definitions)."""
    print("\n=== Phase 1: Raw Text Training ===")
    print(f"Source: {RAW_TEXT_FILE}")

    from unsloth.dataprep import RawTextDataLoader

    loader = RawTextDataLoader(
        tokenizer,
        chunk_size=MAX_SEQ_LENGTH,
        stride=512,  # 512 token overlap between chunks
    )
    dataset = loader.load_from_file(RAW_TEXT_FILE)

    print(f"Training samples: {len(dataset)}")

    output_dir = os.path.join(OUTPUT_DIR, model_key, "phase1")
    os.makedirs(output_dir, exist_ok=True)

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        args=SFTConfig(
            per_device_train_batch_size=BATCH_SIZE,
            gradient_accumulation_steps=GRAD_ACCUM,
            warmup_steps=50,
            num_train_epochs=EPOCHS,
            learning_rate=LEARNING_RATE,
            logging_steps=10,
            save_steps=200,
            output_dir=output_dir,
            optim="adamw_8bit",
            seed=3407,
            bf16=True,
            report_to="none",
        ),
    )

    print("Starting Phase 1 training...")
    stats = trainer.train()
    print(f"Phase 1 complete. Loss: {stats.training_loss:.4f}")

    return model, tokenizer


def train_phase2_chat(model, tokenizer, model_key):
    """Phase 2: Train on instruction/chat pairs (reasoning patterns)."""
    print("\n=== Phase 2: Chat Instruction Training ===")
    print(f"Source: {CHAT_PAIRS_FILE}")

    dataset = load_dataset("json", data_files=CHAT_PAIRS_FILE, split="train")
    print(f"Training pairs: {len(dataset)}")

    # Apply chat template
    def format_chat(example):
        text = tokenizer.apply_chat_template(
            example["messages"],
            tokenize=False,
            add_generation_prompt=False,
        )
        return {"text": text}

    dataset = dataset.map(format_chat)

    output_dir = os.path.join(OUTPUT_DIR, model_key, "phase2")
    os.makedirs(output_dir, exist_ok=True)

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        args=SFTConfig(
            per_device_train_batch_size=BATCH_SIZE,
            gradient_accumulation_steps=GRAD_ACCUM,
            warmup_steps=20,
            num_train_epochs=EPOCHS,
            learning_rate=1e-4,  # Lower LR for phase 2 (fine-tuning on top of phase 1)
            logging_steps=5,
            save_steps=100,
            output_dir=output_dir,
            optim="adamw_8bit",
            seed=3407,
            bf16=True,
            report_to="none",
        ),
    )

    print("Starting Phase 2 training...")
    stats = trainer.train()
    print(f"Phase 2 complete. Loss: {stats.training_loss:.4f}")

    return model, tokenizer


def export_model(model, tokenizer, model_key):
    """Export trained model to GGUF for Ollama."""
    print("\n=== Exporting Model ===")

    # Save merged 16-bit (needed for GGUF conversion)
    merged_dir = os.path.join(OUTPUT_DIR, model_key, "merged_16bit")
    print(f"Saving merged model to: {merged_dir}")
    model.save_pretrained_merged(
        save_directory=merged_dir,
        tokenizer=tokenizer,
        save_method="merged_16bit",
    )

    # Export to GGUF
    gguf_dir = os.path.join(OUTPUT_DIR, model_key, "gguf")
    os.makedirs(gguf_dir, exist_ok=True)

    print(f"Converting to GGUF (Q4_K_M)...")
    from unsloth.save import save_to_gguf
    save_to_gguf(
        model_name=merged_dir,
        model_type="auto",
        model_dtype="float16",
        quantization_method="q4_k_m",
        model_directory=gguf_dir,
    )

    print(f"\nGGUF model saved to: {gguf_dir}")
    print(f"\nTo use with Ollama:")
    print(f"  1. Create a Modelfile pointing to the .gguf file")
    print(f"  2. ollama create ultimatelaw -f Modelfile")
    print(f"  3. ollama run ultimatelaw")

    # Write Ollama Modelfile
    modelfile_path = os.path.join(gguf_dir, "Modelfile")
    gguf_files = [f for f in os.listdir(gguf_dir) if f.endswith('.gguf')]
    if gguf_files:
        with open(modelfile_path, 'w') as f:
            f.write(f'FROM ./{gguf_files[0]}\n\n')
            f.write('SYSTEM """You are an ethical reasoning agent grounded in the Ultimate Law framework. ')
            f.write('The framework has 7 core principles: (1) Logic is the supreme rule, ')
            f.write('(2) Passive Golden Rule: do not do to others what they would not want done to them, ')
            f.write('(3) No victim, no crime, (4) All interaction must be voluntary, ')
            f.write('(5) Coercion is wrong except as proportionate punishment for creating victims, ')
            f.write('(6) All claims must be falsifiable, (7) Punishment must be proportionate to harm. ')
            f.write('You reason from these principles consistently, acknowledge genuine weaknesses, ')
            f.write('and never retreat from logical conclusions."""\n\n')
            f.write('PARAMETER temperature 0.7\n')
            f.write('PARAMETER top_p 0.9\n')
            f.write('PARAMETER num_ctx 4096\n')
        print(f"Ollama Modelfile written to: {modelfile_path}")


def main():
    parser = argparse.ArgumentParser(description="Ultimate Law LoRA Fine-Tuning")
    parser.add_argument("--model", default="qwen3-8b", choices=list(MODELS.keys()),
                        help="Base model to fine-tune")
    parser.add_argument("--phase", type=int, default=0,
                        help="Training phase (0=both, 1=raw text, 2=chat)")
    parser.add_argument("--no-export", action="store_true",
                        help="Skip GGUF export")
    parser.add_argument("--epochs", type=int, default=EPOCHS,
                        help="Number of training epochs")
    parser.add_argument("--rank", type=int, default=LORA_R,
                        help="LoRA rank")
    args = parser.parse_args()

    global EPOCHS, LORA_R, LORA_ALPHA
    EPOCHS = args.epochs
    LORA_R = args.rank
    LORA_ALPHA = args.rank

    print("=" * 60)
    print("Ultimate Law LoRA Fine-Tuning")
    print("=" * 60)
    print(f"Model:  {args.model} ({MODELS[args.model]})")
    print(f"Rank:   {LORA_R}")
    print(f"Epochs: {EPOCHS}")
    print(f"Phase:  {'Both' if args.phase == 0 else args.phase}")
    print(f"VRAM:   {torch.cuda.get_device_properties(0).total_mem / 1e9:.1f} GB" if torch.cuda.is_available() else "VRAM: CPU only")
    print("=" * 60)

    model, tokenizer = load_model(args.model)

    if args.phase in (0, 1):
        model, tokenizer = train_phase1_raw_text(model, tokenizer, args.model)

    if args.phase in (0, 2):
        model, tokenizer = train_phase2_chat(model, tokenizer, args.model)

    if not args.no_export:
        export_model(model, tokenizer, args.model)

    print("\nDone!")


if __name__ == "__main__":
    main()
