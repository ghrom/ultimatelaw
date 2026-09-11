# Install Themis on OmegaClaw

Prerequisites: a working OmegaClaw / PeTTa install ([OmegaClaw-Core README](https://github.com/asi-alliance/OmegaClaw-Core)).

This pack mirrors OmegaClaw paths so you can copy files without renaming.

## 1. Copy workflows

From this directory (`contributions/omegaclaw-themis/`):

```bash
OMEGA=/path/to/PeTTa/repos/OmegaClaw-Core

cp -a plugins/workflow/instructions/themis-adjudication \
  "$OMEGA/plugins/workflow/instructions/"

cp -a plugins/workflow/instructions/themis-challenge \
  "$OMEGA/plugins/workflow/instructions/"
```

Confirm:

```bash
ls "$OMEGA/plugins/workflow/instructions/themis-adjudication"
# description.txt  SKILL.md  skill.metta
```

## 2. Optional — Themis system prompt

Replace or overlay the default prompt:

```bash
cp memory/prompt_Themis.txt "$OMEGA/memory/prompt.txt"
# or keep vendor prompt and paste Themis constraints into your config-managed prompt file
```

Provider-specific prompts (`prompt_ASICloud.txt`, etc.) can receive the same constraints if you use those providers.

## 3. Seed long-term memory

### Option A — interactive remember

Start OmegaClaw, then paste lines from:

```bash
./scripts/seed-remember-lines.sh
```

Ask the agent to `(remember "...")` each line (or batch carefully within size limits).

### Option B — knowledge files on disk

Copy `knowledge/` into a path the agent can `read-file`, then ask it to remember the constitution and core definitions:

```bash
mkdir -p "$OMEGA/memory/themis"
cp -a knowledge "$OMEGA/memory/themis/"
```

Example user message:

```
Read memory/themis/knowledge/00-constitution.md and 01-ultimate-law.md.
Remember the operating axioms and every "Themis definition —" line.
Do not rewrite definitions.
```

### Option C — AtomSpace premises

Load `knowledge/atoms/constitution.metta` into your MeTTa/AtomSpace workflow as published premises (confidence guidance in `00-constitution.md`). Exact load command depends on your PeTTa setup; treat the file as a premise library for `(metta ...)`.

## 4. Run

```bash
# from PeTTa root, as usual
OMEGACLAW_AUTH_SECRET=... sh run.sh run.metta IRC_channel="##your-channel"
```

Then:

```
Adjudicate this case under Themis: <facts>
```

or

```
Challenge this Themis judgment: <judgment text>
```

The agent should `(workflow-load-instructions "themis-adjudication")` or `themis-challenge`.

## 5. Eval

Run prompts in `eval/coherence-battery.md` and score against the pass table.

## Uninstall

Remove the two workflow directories and restore `memory/prompt.txt` if you replaced it. Clear Themis memories from Chroma if desired (`docker volume rm omegaclaw-memory` only if you accept full memory reset).
