---
name: themis-challenge
description: Attempt to overturn a Themis judgment by finding misapplied definitions,
  broken causation, missing victims, or disproportionate sanctions.
---
# Themis Challenge (OmegaClaw)

Use this workflow to **falsify** a prior judgment or prosecution. Success is finding
a real error — not defending a side. Error is not evil; refusing to correct it is.

## Operating Rules

- Load the judgment under challenge (user paste, case file, or `(read-file ...)`).
- Query Themis definitions independently; do not trust the judgment's paraphrase.
- A single misapplied definition is enough to overturn the affected charge.
- If all charges survive, uphold — do not invent loopholes.
- Pin challenge state. Keep responses short and evidentiary.

## Challenge file layout

```
(themis-case-dir)/$case/challenge/
  00_target.md
  01_audit.md
  02_verdict.md
```

If `(themis-case-dir)` is unavailable (workflow helpers not loaded), create under
`(pluginWorkflowMemoryDir)/themis-cases/$case/challenge/` via shell mkdir, or ask
the user to load `themis-adjudication` helpers first.

Prefer: `(themis-challenge-start "$case")`.

## Step-by-step

### Step 1 — Lock the target

- `(themis-challenge-start "$case")`
- Save the exact judgment text or path into `challenge/00_target.md`.
- List each charge and the definition it claims to use.
- `(themis-step "$case" "challenge-target-locked" "N charges" "audit definitions")`
- `(pin "case=$case step=challenge-target")`

### Step 2 — Audit each charge

For every charge, check:

1. **Victim** — Is there an unwilling victim? If not, charge fails.
2. **Causation** — Does evidence show this defendant caused the harm?
3. **Definition fit** — `(query "Themis definition — <Term>")` and compare to application.
4. **Evidence quality** — Independently verifiable? Allegation only?
5. **Proportion** — Does proposed sanction exceed harm caused?

Write findings to `challenge/01_audit.md`.
`(themis-step "$case" "challenge-audit" "failures: ..." "draft verdict")`

### Step 3 — Verdict

Write `challenge/02_verdict.md`:

- **OVERTURNED** (whole case or listed charges) with the specific definition/causation error, or
- **UPHELD** with notes on what was stress-tested.

Include: what would need to change in evidence or Law for the opposite result.

`(themis-checkpoint "$case" "Challenge verdict ready. Approve to send?")`
**WAIT for user.**

### Step 4 — Publish

- If approved: `(send "<challenge verdict>")` then `(themis-complete "$case")` or `(workflow-unload-instructions)`.
- If the dictionary itself is contradictory, report the contradiction to the user as a constitution bug — do not silently patch Law in memory.

## Challenge verdict template

```
THEMIS CHALLENGE VERDICT: <title>

TARGET: <judgment id/title>
RESULT: OVERTURNED | PARTIAL | UPHELD

FAILED CHARGES (if any):
- <Term>: <exact error — missing victim / bad causation / misapplied definition / excess proportion>

SURVIVING CHARGES (if any):
- <Term>: still fits definition + evidence

CONSTITUTION NOTES:
- Dictionary contradiction found? yes/no
- Suggested open falsification (human publication), if any

If any charge misapplies a definition, the case should be overturned.
```
