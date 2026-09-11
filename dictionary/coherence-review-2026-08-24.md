# Coherence Review of the Coherent Dictionary of Simple English

Date: 2026-08-24
Scope: all 192 terms of `dictionary/coherent-dictionary-of-simple-english.txt` (canonical),
cross-checked against `dictionary/coherent-dictionary-mechanical.txt` (STE rendering),
`AGENTS.md` (embedded constitution copy), and the extension appendix.
Metrics tested: internal logical consistency against the dictionary's own axioms; cross-entry
consistency of the title-transfer cluster; structural consistency of the term set.

## Summary

The dictionary is in good internal health. The term set is complete, ordered, duplicate-free,
and the three copies (canonical, ASD rendering, AGENTS.md) are in sync. No definition
contradicts a core axiom (logic, passive Golden Rule, free trade, no-victim-no-crime,
self-emergence). The uncommitted title-transfer pass (Contract / Contract Breach / Debt and
their satellites) has improved coherence in one spot (inability is no longer conflated with
theft) but introduced one genuine gap (Theft was not widened to cover post-title retention)
and two ambiguities of direction (Debt, IOU).

## Structural findings (mechanical)

1. **No duplicate or missing terms: all good.** The set of 192 terms is identical across the canonical file,
   the ASD rendering, and AGENTS.md; no duplicates; the ASD rendering's "192 terms" claim is
   accurate. (`dictionary/coherent-dictionary-extended.txt` is a different artifact, a
   WordNet-aligned export, not the normative dictionary — not part of the 192-term set.)

2. **Alphabetical-order violations (minor).** The header promises "entries are alphabetical."
   Two entries break strict alphabetical order:
   - `Free Will` appears before `Freedom`, `Freedom of Speech`, `Free Trade`, and `Free
     Communication`. (Strict order for the Free-* group: Free Communication, Freedom,
     Freedom of Speech, Free Trade, Free Will — so Freedom should precede Free Will, and
     Free Will should come last of all.)
   - `Right to Free Trade` appears before `Rights`. (Strictly, `rights` sorts before
     `righttofreetrade` — the `o`/`s` difference at the 6th letter — so Rights should
     precede Right to Free Trade.)
   Both look like deliberate grouping of "Free X" / "Right X" together rather than errors.
   Either keep them and drop the "alphabetical" promise, or reorder. Low priority.

## Logical findings (substance)

### A. Genuine gap: Theft was not updated by the title-transfer pass
The new doctrine routes every retention-through-title through Theft:
- Contract: "a holder who keeps it back commits Theft"
- Debt: "A debtor who holds it and refuses to deliver commits Theft"
- IOU: "An issuer who holds what the note names and refuses to deliver commits Theft"
- Currency: "An issuer who holds what the title names and refuses to deliver commits Theft"

But the **Theft** entry itself still reads:
> Taking what belongs to another without consent...

"Keeping back," "refusing to deliver," "holding after title passes" are *retentions*, not
*takings*. Under the new title-transfer doctrine, the moral wrong moved from "taking" to
"retaining after title passed." The Theft definition was left un-updated)Skip, so the
satellites now cite a "Theft" whose own definition does not, on its face, cover their case.
**Recommendation:** widen Theft to "Taking, or keeping back, what belongs to another without
consent" (or add "including retaining what a transfer has already made theirs").
This is the one real coherence defect introduced by the current uncommitted pass.

### B. Ambiguity of ownership direction in Debt and IOU (the changed cluster)
- **Debt** now opens with: "Title passes as the property reaches the debtor's hands: what the
  debtor holds when the date arrives belongs to the creditor."
  The clause "Title passes" names no recipient. Read literally it suggests title passes *to
  the debtor* at handover, which the very next clause contradicts (the property is the
  creditor's at maturity). The intended sense is possession passes to the debtor while title
  stays with (or returns to) the creditor — the old definition said this plainly ("property
  that already belongs to another but still sits in the debtor's hands"). Recommend rewording
  to state the recipient of title explicitly.
- **IOU** now says "title passes on the terms the parties set." This weakens the old,
  unambiguous claim ("The holder already owns what the IOU names"). The satellite clause
  "an issuer who holds what the note names and refuses to deliver commits Theft" requires the
  holder to already own the named thing — i.e., requires the *default* reading where title
  passed at issuance. As written, the entry is only coherent if "on the terms the parties
  set" is read as always passing title to the holder; if the terms may delay title, the
  theft clause has no basis. **Money** kept the strong form ("Whoever holds the note holds
  the title"), so IOU and Money now read at slightly different strengths. Standardize: either
  state that an IOU always passes title to its holder (Money's reading), or make the theft
  clause conditional on the terms.

### C. Restitution overstates when debt is erased (minor)
- **Restitution**: "Restitution erases debt caused by wrongdoing."
- **Guilt** / **Justice** / **Forgiveness**: only *Justice* (victim's collection *or* release)
  erases the moral debt; restitution alone merely *repairs material damage*.
  Restitution's wording implies it alone clears the moral debt. Tighten to "repairs material
  damage; the victim's collection or release closes the moral debt."

### D. Deterrence (minor, already coherent)
> "Deterrence targets fear in potential offenders, not justice for actual victims, and becomes
> injustice when it punishes without a victim."

This is consistent with no-victim-no-crime (a punitive threat with no underlying harm creates
a new victim, since force without a forfeiture crosses a boundary). No change needed; flagged
only to confirm it did not conflict with the Forfeiture cluster.

## Cross-checks that passed (no change needed)

The following inter-locking clusters are internally consistent:

1. **Crime / Victim / No-victim-no-crime.** Crime requires harm across an intact boundary;
   Victim requires intact protection; harm within a Forfeiture creates no victim. No conflict.
2. **Golden Rule / Retribution / Forfeiture.** The Golden Rule is the "no coercion" floor;
   Retribution is justified only across a forfeited boundary; Forfeiture is exactly the
   mechanism that lets force answer harm without creating a new crime. The circle closes.
3. **Proportion / Forfeiture ceiling.** Both say a thief's ceiling is loss of everything
   they own; death is the ceiling only when theft reaches lives. Proportion adds "ceiling not
   duty" (victim may take less). Consistent.
4. **Justice / Forgiveness / Punisher / Punishment / Mandate.** Punishment only for real
   victims; punisher only as proxy within a victim's mandate; forgiveness closes by release.
   Consistent.
5. **Property / Ownership / Intellectual Property / License / Software.** The famous tension
   (if ideas aren't property, how can software be licensed?) is resolved coherently: licenses
   are contracts binding only consenting parties, enforce *agreements* (not ideas), and reach
   no non-consenting third party. The IP entry's "restricting reproduction is coercion"
   applies to third parties who never consented, not to parties who did. Internally sound.
6. **Money / Currency / IOU (doctrine), except the B ambiguity above.** The intangible
   view (money is title, not promise) is consistent across all three once the title-passage
   moment is pinned down.
7. **Theft / Taxes / Government.** Consistent: coercive taxation is Theft by claimed
   authority.
8. **Effect / Causation / Correlation / Responsibility.** Causation carries responsibility;
   correlation does not; collective responsibility (without individual causation) is invalid.
   Consistent with the "no victim no crime" and fallibility axioms.
9. **Freedom / Speech / Expression.** Freedom of Speech limits harm to deception/threat/fraud,
   consistent with Expression and the "offense is not harm" strand in Proportion ("words that
   merely offend... there is no death for insulting a prophet").

## Things verified against the AGENTS.md copy and ASD rendering

- Canonical, AGENTS.md embedded dictionary, and ASD rendering agree on all 192 term headings.
- The uncommitted title-transfer edits are mirrored consistently across AGENTS.md and the
  canonical file (verified word-for-word on Contract, Contract Breach, Currency, Debt, IOU,
  License, Money, Software, Theft, Obligation). No divergence.
- The ASD rendering carries the same title-transfer doctrine in controlled language; its
  term set matches; no term lost or gained.

## Bottom line

Nothing in the dictionary contradicts its own axioms. The one defect worth fixing before
committing the title-transfer pass is **finding A (Theft not widened to cover retention)**.
Findings B and C are wording tightenings that would remove genuine ambiguities. Structural
finding 2 (alphabetical order) is optional. Everything else checks out.
