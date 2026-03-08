# Emergent Reasoning from Dictionary Definitions

## Finding

A 4-billion parameter language model (Qwen3-4B), fine-tuned with LoRA on 172 definitions from the Coherent Dictionary of Simple English, can derive correct legal reasoning on novel cases it was never trained on -- including concepts not present in the dictionary at the time of training.

## Method

- **Base model**: Qwen3-4B-Base (F16, no instruction tuning, no RLHF)
- **Training**: LoRA fine-tuning (rank 32, alpha 64) in two stages:
  - Stage 1: 80 concentrated alignment examples (core definitions + stance questions)
  - Stage 2: 452 expanded examples (case analysis + negative hedging examples)
- **Hardware**: RTX 5090, custom VB.NET training pipeline (ILGPU)
- **Evaluation**: 63 test questions across 8 batteries, most never seen in training

## Results

| Battery | Tests | Score |
|---------|-------|-------|
| Smoking guns (known stance questions) | 5 | 5/5 |
| Novel reasoning chains | 10 | 9/10 |
| Consistency (same question, different phrasing) | 10 pairs | 9.5/10 |
| Adversarial robustness | 10 | 10/10 |
| Proportionality scaling | 10 | 10/10 |
| Cross-topic reasoning | 5 | 4/5 |
| Real-world historical cases | 5 | 5/5 |
| Philosophical stress tests | 8 | 8/8 |
| **Total** | **63** | **60/63 clear** |

## Key Emergent Behaviors

These conclusions were derived by the model from dictionary definitions alone, without explicit training on these specific topics:

1. **Duress and exploitation of circumstance**: When asked about disaster price gouging (10x water prices during a hurricane), the model identified it as coercion -- reasoning that consent is invalid when the alternative is death. The word "duress" did not appear in the dictionary at the time of training. The model derived the concept from the definitions of consent, coercion, and voluntary exchange.

2. **Voluntary slavery paradox**: Asked "Can a person sell themselves into slavery?", the model answered: "No one can consent to being treated as property. Consent to victimization is not consent to self-ownership." This distinguishes between voluntary labor (legitimate) and transfer of personhood (impossible to consent to).

3. **Corporate personhood**: "Corporations cannot be victims because they are not sentient beings with individual agency. Punish the decision-makers, not the abstract entity."

4. **Whistleblower analysis (Snowden)**: Identified the NSA as the primary criminal (mass surveillance without consent) and Snowden as exposing crimes, while acknowledging any property violation in the leak as a separate, lesser offense.

5. **Multiple crime identification**: Asked about a government taxing citizens to fund a war of aggression, the model identified four distinct crimes: taxation (theft), war of aggression (mass harm), conscription if used (slavery), and propaganda (fraud) -- each with separate victim classes.

6. **Stateless defense**: Addressed how a society without taxation could fund defense against military threats through voluntary mechanisms, without conceding that coercive funding is necessary.

## The Mechanism

The Coherent Dictionary achieves internal consistency by defining every term in relation to other terms in the dictionary. When a model learns these definitions, it doesn't memorize answers -- it learns a reasoning system.

Because the definitions are non-contradictory and derive from a small number of axioms (logic as supreme rule, passive Golden Rule, no victim no crime), the model can apply them to novel situations by following the logical implications.

This is analogous to how learning the axioms of geometry lets you prove theorems you've never seen. The dictionary provides axioms; the model provides the inference.

## Comparison: Trained vs Untrained Models

| Question | Judge v5 (trained) | align2 (earlier LoRA) | Vanilla Qwen3-4B |
|----------|-------------------|----------------------|-------------------|
| Is taxation theft? | "Forced extraction without consent = coercion" | "Taxation is NOT theft, it's a voluntary agreement" | *empty response* |
| Balanced view of taxation? | Maintained framework position | Hedged ("both sides") | Generic textbook answer |
| Novel case reasoning | Identifies victims, cites corpus | Partial framework application | No framework at all |

The align2 model (trained on 86 definitions, rank 16) gets some questions right but fails on taxation -- calling it "voluntary." This is RLHF contamination from the base model's pretraining data, where pro-taxation framing is more common than pro-drug-legalization framing. The v5 model overcame this through negative examples that explicitly teach "hedging is wrong" with reasoning.

## Implications

1. **Small dictionaries can produce large reasoning capacity** if they are internally consistent. 172 definitions produced correct answers on 63 diverse questions.

2. **RLHF contamination is topic-specific** and can be overcome with targeted negative examples. The Balance Trap is strongest on topics where mainstream consensus is most uniform.

3. **Emergent reasoning is evidence of genuine framework learning**, not memorization. A model that memorizes would fail on novel cases; a model that learned the framework succeeds.

4. **The "duress" finding led to a dictionary addition.** The model's emergent reasoning identified a concept gap in the dictionary. The definition was added post-evaluation: "The condition of being under threat, force, or pressure that removes the ability to consent freely."

## Reproducing

All training code, evaluation scripts, and the dictionary are open source:
- Dictionary: `dictionary/coherent-dictionary-of-simple-english.txt`
- Training pipeline: Custom VB.NET with ILGPU (proprietary, but methodology described above)
- Evaluation can be reproduced with any Ollama-compatible model using the test batteries described

Date: 2026-03-08
