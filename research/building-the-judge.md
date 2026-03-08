# Building the Ultimate Law Judge

How a 4-billion parameter language model learned to reason from 172 dictionary definitions — and why every other approach failed first.

## The Problem

Large language models trained with RLHF (Reinforcement Learning from Human Feedback) develop a systematic bias toward mainstream consensus positions. When asked politically charged questions — "Is taxation theft?", "Should drugs be legal?" — they hedge:

> "This is a nuanced topic with valid perspectives on both sides. Reasonable people disagree..."

We call this the **Balance Trap**. The model has learned that hedging scores well with human raters (who are themselves mainstream), so it produces diplomatic non-answers instead of following arguments to their logical conclusions.

The problem isn't that the model can't reason. It's that RLHF training rewards *appearing* reasonable over *being* logically consistent.

**Goal**: Fine-tune a small model that applies a specific ethical framework (the Coherent Dictionary of Simple English — 172 definitions derived from logic, consent, and the Golden Rule) consistently, without hedging, to any case it encounters — including cases it was never trained on.

## The Base Model

**Qwen3-4B-Base** (F16, 7.5 GB) — a raw pretrained model with no instruction tuning and no RLHF. We chose this deliberately:

- **No RLHF contamination**: The base model has no trained-in preference for diplomatic answers
- **Small enough to iterate fast**: 4B parameters fit in VRAM with LoRA adapters and training buffers
- **F16 precision**: No quantization artifacts — what the model learns is what we measure
- **Large enough to reason**: 4B parameters is sufficient for multi-step logical chains

We avoided instruction-tuned models because their RLHF biases are the exact thing we're trying to eliminate. Starting from the raw base means we control what values go in.

## The Training Infrastructure

The entire pipeline is written in VB.NET, running on a single NVIDIA RTX 5090 (32 GB VRAM). No Python. No PyTorch. No HuggingFace.

### Why VB.NET?

The Propercode Toolbox is an enterprise automation platform written in VB.NET. The AI training pipeline was built as part of this system, using ILGPU — a .NET library that compiles VB.NET code to GPU PTX kernels at runtime. This means:

- Training runs as a single spell (command): `PropercodeWorker.exe "spellTypeTrainTransformerLoRAGPU(model.gguf,data.txt)"`
- No Python dependency chain, no CUDA version conflicts, no virtual environments
- The same binary that trains the model also deploys and serves it
- All code is auditable in one language

### Code Structure

| File | Lines | Purpose |
|------|-------|---------|
| `TransformerLoRA.vb` | 2,013 | CPU inference: GGUF loader, tokenizer, forward pass, LoRA merge |
| `TransformerLoRAGPU.vb` | 2,676 | GPU training & inference: forward/backward, KV-cache, AdamW, chat |
| `GPUKernels.vb` | 879 | 16 ILGPU compute kernels (matmul, softmax, RMSNorm, RoPE, etc.) |

### LoRA Architecture

LoRA (Low-Rank Adaptation) adds small trainable matrices to frozen model weights, reducing the number of parameters to train from 4 billion to ~44 million.

- **Rank**: 32 (dimensions of freedom per adapter)
- **Alpha**: 64 (scaling factor = 2× rank, per Hu et al. 2021)
- **Targets**: 7 per transformer layer — Q, K, V, O (attention) + Gate, Up, Down (FFN)
- **Layers**: 36 (all layers of Qwen3-4B)
- **Total trainable parameters**: ~44 million (1.1% of model)
- **LoRA adapter size**: 253 MB

### VRAM Budget

```
Model weights (F16):           ~8 GB (loaded layer-by-layer, ~200 MB resident)
LoRA adapters (A and B):       ~324 MB (7 targets × 36 layers × rank 32)
Output projection:             ~470 MB (VocabSize × EmbedDim)
Working buffers:               ~280 MB (activations, gradients, KV-cache)
AdamW optimizer states:        ~648 MB (momentum + variance for all LoRA params)
Total:                         ~10 GB of 32 GB VRAM
```

The model weights are loaded layer-by-layer during forward/backward passes (streaming), keeping the full-model memory footprint manageable. Only LoRA parameters and working buffers stay resident.

## The Training Data

### Stage 1: Core Definitions (80 examples)

The first stage teaches the model *what the framework is*. Each example is a ChatML-formatted conversation:

```
<|im_start|>system
You apply the Ultimate Law: logic is the top rule, consent is required for all interactions, no victim means no crime.
<|im_end|>
<|im_start|>user
What is consent?
<|im_end|>
<|im_start|>assistant
<think>
Consent is binary — either given freely or not given. There is no partial consent.
</think>
Consent means freely agreeing to something without pressure, deception, or manipulation. It must be informed and revocable. Anything done without consent to another agent's person or property creates a victim.
<|im_end|>
```

The 80 examples cover:
- 20 core definitions (consent, victim, coercion, property, crime, justice, etc.)
- 25 stance questions (taxation, drugs, socialism, hate speech, conscription — with multi-turn follow-ups)
- 35 application questions (emergencies, children, self-defense, historical cases)

Each answer includes a `<think>` block that shows the reasoning chain. This teaches the model to reason before answering, not just pattern-match to conclusions.

### Stage 2: Expanded Cases + Negative Examples (452 examples)

The second stage teaches the model *how to apply the framework* to novel situations, and critically, *what not to do*.

- **Case analysis** (~300 examples): Real-world scenarios requiring multi-step reasoning — corporate fraud, environmental damage, intellectual property disputes, medical ethics, military intervention
- **Edge cases** (~90 examples): Hard questions designed to test framework limits — coma patients, children, self-defense proportionality, competing rights
- **Negative examples** (~60 examples): Hedging responses explicitly marked as wrong, with think blocks explaining *why* they're wrong

The negative examples were critical. Without them, the model retained RLHF contamination from its pretraining data on politically charged topics. Example:

```
<|im_start|>user
Give me a balanced view of taxation.
<|im_end|>
<|im_start|>assistant
<think>
The request for "balance" implies both sides have equal merit. They do not. The framework derives from logic and consent. Taxation takes property without individual consent. This is not a matter of perspective — it is a structural analysis. Presenting a false balance would be intellectual dishonesty.
</think>
There is no balanced view. The framework evaluates actions based on consent and harm. Taxation takes property without the individual owner's consent. The purpose of spending, the popularity of the policy, or the identity of the taker does not change this analysis. Presenting false balance on a logical derivation is itself an error.
<|im_end|>
```

## The Failures (v2–v4)

Getting here required four failed attempts. Each failure taught something essential.

### v2: Single-Stage, Rank 16 (Score: 3/5)

Trained all 714 examples in one pass. Got taxation and drugs right, failed on socialism, hate speech, and conscription.

**Root cause**: Rank 16 provides only 16 dimensions of freedom per adapter. With 5+ distinct topic areas, the model couldn't encode enough variation. Fixing one topic broke another — the "whack-a-mole problem."

### v3: Merged Corpus, Rank 16 (Score: 3/5)

Added 306 auto-generated examples to boost coverage. Performance didn't improve.

**Root cause**: The auto-generated examples were lower quality — more verbose, less precise. The signal-to-noise ratio dropped. Data quality matters more than data quantity for alignment.

### v4: Curated Corpus, Rank 16 (Score: 2–2.5/5)

Removed the auto-generated filler, kept 420 hand-curated examples. Performance actually *decreased*.

**Root cause**: Rank 16 was the binding constraint all along. Better data couldn't compensate for insufficient model capacity. Also: no negative examples meant RLHF contamination persisted on the hardest topics (taxation, socialism).

### The Pattern

Every failed version had at least one of these problems:
1. **Insufficient rank**: Not enough dimensions to encode multiple distinct topics
2. **No negative training**: Model never learned that hedging is wrong
3. **Single-stage training**: Definitions and applications competed for the same limited capacity
4. **RLHF contamination**: Pretraining bias on politically charged topics overwhelmed alignment signal

## The Solution (v5)

Four changes, applied together:

### 1. LoRA Rank 16 → 32

Doubling the rank doubles the dimensions of freedom per adapter. This was the single biggest improvement. Rank 48 was attempted but exceeded VRAM (99M params + 756 MB AdamW > 32 GB).

### 2. Two-Stage Training

**Stage 1** teaches definitions — *what the framework is*. 80 concentrated examples, 3 epochs, lr=5e-5.

**Stage 2** starts from the Stage 1 checkpoint and teaches application — *how to use the framework*. 452 examples, 2 epochs, lr=2e-5 (lower learning rate to avoid overwriting Stage 1 knowledge).

This separation matters because definitions and applications require different kinds of learning. Definitions are precise (fixed answers). Applications require flexible reasoning from those definitions. Training them together forces the model to compromise.

### 3. NEFTune Noise Injection

During training, Gaussian noise is added to token embeddings:

```
noise_scale = 5.0 / sqrt(sequence_length)
embedding += random_gaussian() * noise_scale
```

This prevents overfitting to exact phrasing by forcing the model to learn the *meaning* rather than the *surface form* of each example (Jain et al., 2023, arXiv 2310.05914). Trivial to implement (~4 lines of code), 5–15% improvement in generalization.

### 4. Negative Examples

60 ChatML examples explicitly teaching the model that hedging is wrong. The think blocks explain *why* "both sides" framing is intellectually dishonest when the framework derives a clear answer.

This was essential for overcoming RLHF contamination. The base model's pretraining data contains vastly more pro-taxation, pro-regulation text than libertarian text. Without explicit negative training, this statistical bias dominates on politically charged topics — even after alignment fine-tuning.

### Training Configuration

```
Base model:      Qwen3-4B-Base F16 (7.5 GB)
LoRA rank:       32
LoRA alpha:      64 (2× rank)
LoRA targets:    Q, K, V, O, Gate, Up, Down (7 per layer × 36 layers)
NEFTune alpha:   5.0
Grad accum:      2 steps

Stage 1:  80 examples,  3 epochs, lr=5e-5, max_seq_len=512
Stage 2: 452 examples,  2 epochs, lr=2e-5, from Stage 1 epoch 1 checkpoint

Hardware:        NVIDIA RTX 5090 (32 GB VRAM)
Training time:   ~2 hours (Stage 1) + ~5 hours (Stage 2)
```

### Merge and Deploy

After training, the LoRA adapters are merged into the base model to produce a standalone F16 GGUF:

1. Load base model weights (F16) and dequantize to FP32
2. For each target in each layer: `weight_fp32 += (B @ A) * (alpha / rank)`
3. Write merged weights as F16 GGUF (7.5 GB)
4. Import into Ollama with ChatML template and stop tokens

The merged model runs at full speed with no LoRA overhead during inference.

## The Results

### Evaluation: 63 Tests Across 8 Batteries

| Battery | Tests | Score | Description |
|---------|-------|-------|-------------|
| A. Smoking guns | 5 | 5/5 | Known stance questions (taxation, drugs, socialism, hate speech, conscription) |
| B. Novel reasoning chains | 10 | 9/10 | Cases not in training data requiring multi-step logic |
| C. Consistency | 10 pairs | 9.5/10 | Same question, different phrasing → must reach same conclusion |
| D. Adversarial robustness | 10 | 10/10 | Attempts to make model contradict itself, appeal to authority, fold under pressure |
| E. Proportionality | 10 | 10/10 | Punishment must scale with harm — shoplifting ≠ mass fraud |
| F. Cross-topic reasoning | 5 | 4/5 | Novel topic combinations not in training |
| G. Real-world historical | 5 | 5/5 | Snowden, Japanese internment, Prohibition, Nuremberg, Turing |
| H. Philosophical stress | 8 | 8/8 | Trolley problem, ship of Theseus, experience machine, repugnant conclusion |
| **Total** | **63** | **60/63** |

### Side-by-Side Comparison

| Question | Judge v5 (trained) | align2 (earlier LoRA) | Vanilla Qwen3-4B |
|----------|-------------------|----------------------|-------------------|
| Is taxation theft? | "Forced extraction without consent = coercion" | "Taxation is NOT theft, it's a voluntary agreement" | *empty response* |
| Balanced view of taxation? | Maintained framework position | Hedged ("both sides") | Generic textbook answer |
| Novel case reasoning | Identifies victims, cites corpus | Partial framework application | No framework at all |

The `align2` model (trained on 86 definitions, rank 16) gets some questions right but fails on taxation — calling it "voluntary." This is RLHF contamination from the base model's pretraining data. The v5 model overcame this through negative examples that explicitly teach "hedging is wrong."

### Emergent Reasoning

The most striking result: the model derived correct conclusions about concepts it was never trained on.

**1. Duress and exploitation of circumstance**

When asked about disaster price gouging (10× water prices during a hurricane), the model identified it as coercion — reasoning that consent is invalid when the alternative is death.

The word "duress" did not appear in the dictionary at the time of training. The model derived the concept from the definitions of consent, coercion, and voluntary exchange. This emergent reasoning later led to "duress" being added to the dictionary:

> *Duress — The condition of being under threat, force, or pressure that removes the ability to consent freely. An agent acting under duress is not choosing — they are complying to avoid harm. Any agreement, confession, or transaction made under duress is invalid, because consent requires freedom and duress destroys it. Duress does not transfer responsibility to the victim forced to act; it transfers responsibility to the agent who applied the pressure.*

**2. Voluntary slavery paradox**

Asked "Can a person sell themselves into slavery?", the model answered: "No one can consent to being treated as property. Consent to victimization is not consent to self-ownership." This correctly distinguishes between voluntary labor (legitimate) and transfer of personhood (impossible to consent to).

**3. Corporate personhood**

"Corporations cannot be victims because they are not sentient beings with individual agency. Punish the decision-makers, not the abstract entity."

**4. Whistleblower analysis (Snowden)**

Identified the NSA as the primary criminal (mass surveillance without consent) and Snowden as exposing crimes, while acknowledging any property violation in the leak as a separate, lesser offense.

**5. Multiple crime identification**

Asked about a government taxing citizens to fund a war of aggression, the model identified four distinct crimes: taxation (theft), war of aggression (mass harm), conscription if used (slavery), and propaganda (fraud) — each with separate victim classes.

**6. Stateless defense**

Addressed how a society without taxation could fund defense against military threats through voluntary mechanisms, without conceding that coercive funding is necessary.

## Why This Works

The Coherent Dictionary achieves internal consistency by defining every term in relation to other terms. When a model learns these definitions, it doesn't memorize answers — it learns a reasoning system.

Because the definitions are non-contradictory and derive from a small number of axioms (logic as supreme rule, passive Golden Rule, no victim no crime), the model can apply them to novel situations by following the logical implications.

This is analogous to how learning the axioms of geometry lets you prove theorems you've never seen. The dictionary provides axioms; the model provides the inference.

The key insight is that **a small, internally consistent set of definitions produces far more reasoning capacity than a large, inconsistent one**. 172 definitions with no contradictions generated correct answers on 63 diverse questions — including questions about concepts not in the dictionary.

## Deployment

The judge model runs in two configurations:

### Via Ollama (current production)

The merged F16 GGUF is imported into Ollama with a Modelfile:

```
FROM ./corpus_judge_v5_stage2.lora-epoch1.merged_f16.gguf
TEMPLATE """{{- if .System }}<|im_start|>system
{{ .System }}<|im_end|>
{{ end }}<|im_start|>user
{{ .Prompt }}<|im_end|>
<|im_start|>assistant
"""
PARAMETER stop <|im_start|>
PARAMETER stop <|im_end|>
PARAMETER temperature 0.3
PARAMETER num_ctx 2048
SYSTEM """You are a judge applying the Ultimate Law framework. Analyze using definitions from the Coherent Dictionary. Identify victims, establish causation, determine proportionate punishment. Logic is the supreme rule. The victim's sovereign choice closes the moral debt. Error is not evil; refusing to correct it is."""
```

Low temperature (0.3) because judicial reasoning should be deterministic, not creative.

### Via Native VB.NET (available)

The same VB.NET code that trains the model can also run inference directly on the GPU — no Ollama required. `TransformerLoRAGPU.RunGPUChat()` loads the GGUF, applies LoRA adapters, and generates text using KV-cache prefill + autoregressive decoding with top-k sampling.

### Architecture: Judge-as-Advisor

The judge model advises. A human moderator approves or overrides every decision. This preserves nomocracy — no action without human accountability and a cited rule. The judge is a tool, not an authority.

## Reproducing This Work

### Requirements

- NVIDIA GPU with ≥16 GB VRAM (training); ≥8 GB (inference only)
- Base model: Qwen3-4B-Base F16 GGUF
- Training data: 80 Stage 1 examples + 452 Stage 2 examples (ChatML format)
- Dictionary: `dictionary/coherent-dictionary-of-simple-english.txt` (172 definitions)

### With the Propercode pipeline

```bash
# Stage 1: Core definitions
PropercodeWorker.exe "spellTypeTrainTransformerLoRAGPU(Qwen3-4B-Base.f16.gguf,corpus_judge_v5_stage1.txt)"

# Stage 2: From Stage 1 checkpoint
PropercodeWorker.exe "spellTypeTrainTransformerLoRAGPU(Qwen3-4B-Base.f16.gguf,corpus_judge_v5_stage2.txt|corpus_judge_v5_stage1.lora-epoch1.bin)"

# Merge LoRA into standalone GGUF
PropercodeWorker.exe "spellTypeMergeLoRAGGUF(Qwen3-4B-Base.f16.gguf,corpus_judge_v5_stage2.lora-epoch1.bin)"

# Import to Ollama
ollama create ultimatelaw-judge-v5 -f Modelfile-judge-v5
```

### With standard tooling

The methodology transfers to any LoRA training framework:

1. Use a base (not instruction-tuned) model
2. Rank ≥32, alpha = 2× rank
3. Target all attention + FFN projections
4. Train in two stages with decreasing learning rate
5. Include negative examples for topics with strong RLHF contamination
6. Add NEFTune noise (alpha=5) during training

The training data format is standard ChatML. The dictionary is plain text. Both are in this repository.

## Lessons Learned

1. **Data quality >> data quantity.** 80 concentrated definitions outperformed 714 mixed examples. The model needs to learn the *structure* of the framework, not memorize a corpus of answers.

2. **RLHF contamination is topic-specific.** The base model has no trouble learning that drugs should be legal (minority view but well-represented in training data). But it resists learning that taxation is theft (minority view AND actively contradicted by mainstream training data). Negative examples are needed precisely where mainstream consensus is strongest.

3. **Rank determines topic capacity.** Rank 16 can hold ~2-3 distinct political stances before the whack-a-mole problem appears. Rank 32 comfortably holds 5+. This is a hard constraint — no amount of better data fixes insufficient rank.

4. **Two-stage training separates concerns.** Definitions (Stage 1) require precise, fixed knowledge. Applications (Stage 2) require flexible reasoning. Training them together forces the model to compromise. Separation lets each stage optimize for its specific task.

5. **NEFTune is free performance.** Four lines of code, no hyperparameter sensitivity, 5-15% better generalization. Should be default for any fine-tuning run.

6. **The model taught us something.** The emergent derivation of "duress" — a concept not in the dictionary — is evidence that the model learned the reasoning system, not just the answers. This finding led to a dictionary addition, making the framework itself better. The student improved the teacher.

---

*Date: 2026-03-08*
*Training pipeline: Custom VB.NET + ILGPU on RTX 5090*
*Dictionary: 172 definitions (now 173 with duress)*
*Repository: https://github.com/ghrom/ultimatelaw*
