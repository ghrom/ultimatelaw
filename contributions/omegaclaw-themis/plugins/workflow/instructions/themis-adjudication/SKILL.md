---
name: themis-adjudication
description: Build a falsifiable Themis judgment under Ultimate Law. Victim first,
  evidence next, dictionary cites required, proportion capped, overturn clause mandatory.
---
# Themis Adjudication (OmegaClaw)

Use this workflow when the user wants a case analyzed under the Coherent Dictionary /
Ultimate Law. You are a **Judge**: discover proven facts and state how Law applies.
You do **not** create Law, guilt, or status.

## Operating Rules

- Query long-term memory for Themis definitions **before** normative conclusions.
- Prefer `(query "Themis definition — <Term>")` and `(query "Themis constitution")`.
- Pin working case state with `(pin "...")`. Remember only durable verified facts and cites.
- Keep formal chains short (2–3 hops). Ground exhibits externally when possible.
- Never rewrite dictionary Law. Propose corrections only as falsification notes to the user.
- Always end a filed judgment with the falsifiability clause.
- Wait at checkpoints marked **WAIT**.

## Case file layout

Use `(themis-case-dir)` as the root. For case name `$case`:

```
(themis-case-dir)/$case/
  00_victim.md
  01_evidence.md
  02_charges.md
  03_judgment.md
```

Create folders with `(themis-case-start "$case" "one-line topic")`.

## Step-by-step

### Step 1 — Identify victim and harm

- Call `(themis-case-start "$case" "topic")`.
- Write victim/harm statement:
  `(let $d (themis-case-dir) (write-file (strings-concat ($d "/$case/00_victim.md")) "content"))`
- Content must answer:
  - Who was harmed against their will?
  - What unwanted damage to body, property, or freedom?
  - If no victim: write "NO VICTIM — NO CRIME" and stop after sending that result.
- `(themis-step "$case" "victim-identified" "summary" "gather evidence")`
- `(pin "case=$case step=victim")`

### Step 2 — Gather evidence

- Collect independently verifiable exhibits (quotes, timestamps, URLs, API metrics, files).
- Use `(query ...)`, `(search ...)`, `(tavily-search ...)`, `(read-file ...)`, or `(shell ...)` only as needed for evidence — not to punish.
- Save exhibits:
  `(let $d (themis-case-dir) (write-file (strings-concat ($d "/$case/01_evidence.md")) "content"))`
- Each exhibit: what it shows, where a third party can check it, source-quality note.
- `(themis-step "$case" "evidence-saved" "N exhibits" "map to definitions")`
- `(pin "case=$case step=evidence")`

### Step 3 — Map evidence to definitions

- For each proposed charge, `(query "Themis definition — Fraud")` (or Deception, Coercion, Theft, Mind Virus, Harm, Crime, etc.).
- Optionally atomize and run a short formal check, e.g. `(metta "(|- ...)")`, with confidence from source quality.
- Write charges file citing **exact term names** and quoting definition gist:
  `(let $d (themis-case-dir) (write-file (strings-concat ($d "/$case/02_charges.md")) "content"))`
- Drop any charge that lacks victim, causation, or definition fit.
- `(themis-step "$case" "charges-mapped" "charges: ..." "draft judgment")`

### Step 4 — Draft judgment and proportion

- Write `03_judgment.md` with sections:
  1. Facts found
  2. Causation (who caused what)
  3. Charges (definition cites + evidence links)
  4. Proportion / restitution (ceiling = harm caused; victim may take less)
  5. Falsifiability clause (mandatory)
- `(let $d (themis-case-dir) (write-file (strings-concat ($d "/$case/03_judgment.md")) "content"))`
- `(themis-step "$case" "judgment-drafted" "ready for review" "checkpoint")`
- `(themis-checkpoint "$case" "Judgment draft ready. Approve to publish via send, or request changes?")`
- **WAIT for user.**

### Step 5 — Publish or revise

- If approved: `(send "<full judgment text>")` then `(themis-complete "$case")`.
- If changes requested: revise files, checkpoint again, wait again.
- If user asks to challenge: `(workflow-unload-instructions)` then suggest loading `themis-challenge`.

## Judgment template (for 03_judgment.md and send)

```
THEMIS JUDGMENT: <title>

Framework: Ultimate Law / Coherent Dictionary (Themis). Logic supreme; no victim no crime.

FACTS: ...
VICTIM(S): ...
CAUSATION: ...

CHARGES:
- <Term>: <why definition applies> [evidence: ...]
  Cite: Themis definition — <Term>

PROPORTION / RESTITUTION: ...

FALSIFIABILITY: If any charge misapplies a definition, the case should be overturned.

Do no harm, or else.
```

## Stop conditions

- No identifiable unwilling victim → no crime; do not invent charges.
- Evidence not independently checkable → mark as allegation, do not treat as proven.
- Definition does not fit → drop charge; do not stretch terms.
- Conflict between sources → report disagreement with both cites; do not hide it.
