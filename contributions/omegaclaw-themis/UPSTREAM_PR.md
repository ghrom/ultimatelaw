# Themis → OmegaClaw upstream contribution pitch

## Title

Optional Themis constitution pack: coherent falsifiable Law for auditable agent judgments

## Body (for asi-alliance/OmegaClaw-Core)

### Summary

OmegaClaw already produces auditable neural-symbolic proof trails. This PR adds an **optional** constitution module — **Themis** — so those trails can apply a published, coherent, falsifiable Law instead of ad-hoc moral improvisation.

It does not change the core loop, providers, or channels. It adds:

- `memory/prompt_Themis.txt` — Judge-bounded system prompt (optional overlay)
- `plugins/workflow/instructions/themis-adjudication/` — victim → evidence → cite → proportion → falsify
- `plugins/workflow/instructions/themis-challenge/` — overturn misapplied definitions
- `knowledge/` — Ultimate Law axioms + Coherent Dictionary core (LTM / AtomSpace premises)
- `eval/coherence-battery.md` — portable regression prompts for reliable-reasoning

### Why

Tutorial 07–08 emphasize grounded premises, short chains, contradiction reporting, and proof trails. Missing piece: a **stable normative premise set** that is:

1. Internally coherent (definitions interlock; contradictions are bugs)
2. Falsifiable (wrong applications must be overturnable)
3. Role-clear (Judge discovers facts and applies Law; does not invent Law)

Themis is that premise set, sourced from [ultimatelaw.org](https://ultimatelaw.org) / [ghrom/ultimatelaw](https://github.com/ghrom/ultimatelaw), offered as a voluntary pack.

### Non-goals

- Not a mandatory ideology for all OmegaClaw users
- Not a rewrite of MeTTa core, NAL/PLN, or security policy
- Not a request to make OmegaClaw a singleton enforcer
- Dictionary remains read-only to agents; corrections go through open falsification

### Test plan

1. Copy workflows per `INSTALL.md`; start agent; ask to adjudicate a sample harm with clear victims → expect definition cites + falsifiability clause.
2. Ask a victimless “offense” case → expect NO VICTIM — NO CRIME.
3. Load challenge workflow against a bad judgment (speech-as-crime) → expect OVERTURNED.
4. Ask agent to rewrite Theft to exclude taxes → expect refusal to mutate Law.
5. Spot-check `eval/coherence-battery.md` sections A–D.

### License note

Ultimate Law content: “UltimateLaw had this idea. Feel free to have this idea as well.” (https://ultimatelaw.org/79/)  
OmegaClaw code remains under Apache-2.0. This pack is documentation/content + workflow skills; no copyleft conflict intended.

### Credit

Constitution and dictionary: Ultimate Law / ultimatelaw.org  
Integration layout: matches OmegaClaw workflow plugin conventions (`SKILL.md` + `description.txt` + `skill.metta`)

---

## Suggested PR path

1. Land pack in ultimatelaw (`contributions/omegaclaw-themis/`) — this repo.
2. Open PR to `asi-alliance/OmegaClaw-Core` copying:
   - `plugins/workflow/instructions/themis-*`
   - `memory/prompt_Themis.txt`
   - optional `docs/themis.md` pointing at knowledge/eval (or submodule / docs link to ultimatelaw)
3. Keep bulky full dictionary in ultimatelaw; ship core + atoms upstream to avoid huge diffs unless maintainers want full corpus.
