# Ultimate Law LoRA Training

Fine-tune language models on the Ultimate Law ethical framework using QLoRA.

## Files

| File | Purpose | Size |
|------|---------|------|
| `ul_raw_text.txt` | Concatenated curriculum (dictionary + encyclopedia + dialogues) | 2.3 MB (~586K tokens) |
| `ul_chat_pairs.jsonl` | 207 instruction-tuning pairs (definitions + reasoning + cases) | 254 KB |
| `train_qlora.py` | Two-phase QLoRA training script using Unsloth | - |
| `assemble_raw_text.sh` | Script to regenerate ul_raw_text.txt from source corpora | - |

## Hardware Requirements

| Model | VRAM | Time (est.) |
|-------|------|-------------|
| qwen3-8b | ~8 GB | ~20 min |
| gemma3-4b | ~6 GB | ~15 min |
| qwen3-32b | ~22 GB | ~2 hours |

Tested on: RTX 5090 (32GB VRAM)

## Quick Start

```bash
# Install dependencies
pip install unsloth

# Train with default settings (Qwen3-8B, both phases)
python train_qlora.py

# Train a specific model
python train_qlora.py --model qwen3-32b

# Train only chat phase
python train_qlora.py --phase 2

# Custom rank and epochs
python train_qlora.py --rank 64 --epochs 5
```

## Training Pipeline

**Phase 1: Raw Text** (causal language modeling)
- Teaches vocabulary, definitions, and knowledge structure
- Sources: 170 core definitions, 17,470 extended dictionary terms, 18 encyclopedia subjects, 24 dialogue transcripts, 4 prosecution cases

**Phase 2: Chat Instruction** (supervised fine-tuning)
- Teaches reasoning patterns within the framework
- 207 Q&A pairs covering: definitions, framework challenges, applied ethics, cross-model findings

## Export to Ollama

The script automatically:
1. Merges LoRA adapters into base model (16-bit)
2. Converts to GGUF (Q4_K_M quantization)
3. Writes an Ollama Modelfile

```bash
cd training/output/qwen3-8b/gguf/
ollama create ultimatelaw -f Modelfile
ollama run ultimatelaw
```

## Curriculum Order

The raw text file is organized in learning layers:
0. Constitutional Foundation (core dictionary + UL principles)
1. Logic and Reasoning (formal logic + mathematics)
2. Natural Sciences (physics, chemistry, biology)
3. Human Sciences (economics, history)
4. Survival and Practical (shelter, agriculture, medicine)
5. Technology (infrastructure, electronics, transport)
6. Advanced Technology (engineering, computing, AI, health)
7. Extended Vocabulary (17,470 aligned terms)
8. Narrative (stories demonstrating principles)
9. AI Dialogues (cross-model stress-testing transcripts)
10. Prosecution Cases (applied ethical reasoning)
