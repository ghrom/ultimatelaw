# Gloss closure under the closed-vocabulary ruling (2026-09-05)

Ruling (Piotr, 2026-09-05): every gloss obeys the Mechanical closed vocabulary, and no gloss loses a feature to satisfy it.

Remedy chosen: entry, not rewording. Every original gloss stands as written. The words the glosses needed were entered as declared vocabulary in `mechanical-vocabulary.md`, section 3b, category "Words entered for gloss closure" (215 rows, 38 extra listed forms). Each entered gloss was gated for well-foundedness against the vocabulary as it stood before the batch.

Gate (`tools/glosscheck.py` in ultimatelaw-publishing, the master's own rules):
- index words and listed forms are legal; base words are exact-form;
- a regular inflection is legal when `tools/sync_mechanical.py` `_stems` maps it onto a declared, term, overridden or family word (section 3b);
- the declaration itself is vocabulary whether or not a word occurs in the rendering (rules 1.1 / 1.5 / 1.12);
- text in double quotes or backticks is quoted data (rule 8.6); hyphenated index words stay whole;
- a gloss may not cite its own headword.

Result: 0 rows offending (was 353). Index unchanged at 1,194 rows.

Other edits: `forfeits` received its missing base gloss; `identity` and `describe` no longer use `properties` in a sense that clashes with the overridden `property`. Fifteen base rows whose headword was entered (falls, lets, looks, ...) are pinned as declared rows with their original glosses verbatim, so the sync does not fold them.
