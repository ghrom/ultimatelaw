# Themis for OmegaClaw

Coherent, falsifiable constitution pack for [OmegaClaw-Core](https://github.com/asi-alliance/OmegaClaw-Core).

OmegaClaw supplies the hybrid agent harness (LLM + NAL/PLN + memory + skills).  
**Themis** supplies published Law those proof trails can apply.

```
contributions/omegaclaw-themis/
├── README.md                 ← you are here
├── INSTALL.md                ← drop-in install against OmegaClaw paths
├── UPSTREAM_PR.md            ← pitch / PR body for asi-alliance/OmegaClaw-Core
├── memory/
│   └── prompt_Themis.txt     ← optional Law-bound system prompt
├── knowledge/
│   ├── 00-constitution.md    ← axioms + agent constraints
│   ├── 01-ultimate-law.md    ← remember-ready core
│   ├── 02-dictionary-core.md ← 58 priority definitions
│   ├── 03-dictionary-full.md ← full coherent dictionary export
│   └── atoms/constitution.metta
├── plugins/workflow/instructions/
│   ├── themis-adjudication/  ← build falsifiable judgments
│   └── themis-challenge/     ← overturn misapplied definitions
├── cases/                    ← templates + pointers to UL case archive
├── eval/coherence-battery.md
└── scripts/seed-remember-lines.sh
```

## Quick start

See [INSTALL.md](./INSTALL.md). Short version:

1. Copy `themis-adjudication` and `themis-challenge` into OmegaClaw `plugins/workflow/instructions/`.
2. Optionally set `memory/prompt.txt` from `prompt_Themis.txt`.
3. Seed definitions via `scripts/seed-remember-lines.sh` / `knowledge/`.
4. Ask: *Adjudicate this case under Themis…* or *Challenge this judgment…*

## Design rules

| Do | Don't |
|----|-------|
| Cite dictionary terms by name | Invent victims |
| Include falsifiability clause | Rewrite Law in agent memory |
| Cap sanctions at harm caused | Treat offense as crime |
| Report contradictions | Hide disagreement behind rhetoric |
| Keep formal chains short | Replace OmegaClaw core |

## Ultimate Law (entire text)

Logic is the ultimate law.  
Do not do to others what they would not want to be done to them, or you will be punished regardless of your will.  
The purpose of punishment is to erase guilt, via retribution and restitution.  
That is the entire law; it cannot be changed, all the rest is commentary.

## License

UltimateLaw had this idea. Feel free to have this idea as well.  
https://ultimatelaw.org/79/
