# Do not damage *The Record*

This short is **sidecar only**. It never replaces the feature.

## Never touch these (the film)

In `C:\data\devops.propercode.co.uk\monument-director\`:

- `screenplay.json` — 52 scenes. Sacred.
- `assets.json` — locked faces and plates.
- `lexicon.json` — every proper noun in the feature.
- `state.json` — locks. Losing it loses decisions.
- `template.json` / `template_ref2va.json`
- `logo/` / `logo_prep.py` — read, do not overwrite
- `add_*.py`, `fix_*.py`, `rewrite_*.py`, `set_*.py` — do not re-run
- `*.biggle.json`, `screenplay.original.json`, `cast.json` — gitignored, local-only
- `C:\data\ComfyUI\output\director\` — feature stills
- `output\monument_takes\` — feature takes

A locked slot is sacred. No cascade. This package does not write any of the above.

## How to shoot this without touching the film

1. Copy the **software** (server, HTML, templates, `start_servers.ps1`) to a **sibling folder**, e.g. `C:\data\devops.propercode.co.uk\monument-director-peaceful-revolution\`.
2. Do **not** copy `state.json` from the film. Start with empty state in the sibling.
3. In the sibling only, point the director at these files (rename **there**, not in the film tree):
   - `pr.lexicon.json` → `lexicon.json`
   - `pr.assets.json` → `assets.json`
   - `pr.screenplay.json` → `screenplay.json`
4. Bind the sibling on a **different port** if the film director is already on 8189.
5. Stills/takes for this short go in a **new** output directory, not `ComfyUI\output\director\` of the film.

If the director cannot run two trees, do not shoot this until it can. Do not hot-swap the film's `screenplay.json`.

## Collision shield

Every id and `{{TOKEN}}` in this package is prefixed `pr_` / `PR_`. Union-merge into the film lexicon would still be a bad idea; the prefix is a seatbelt, not a licence.

| File | Role |
|------|------|
| [`pr.lexicon.json`](pr.lexicon.json) | Short-only nouns |
| [`pr.assets.json`](pr.assets.json) | One speaker, five locations |
| [`pr.screenplay.json`](pr.screenplay.json) | 6 scenes, 16 spoken takes |
| [`negative.txt`](negative.txt) | H3 negative tail for this short |
| [`vo.txt`](vo.txt) | Lines only |

Source: [`../pocket.md`](../pocket.md).
