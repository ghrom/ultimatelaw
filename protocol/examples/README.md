# Examples

The conformance streams double as executable examples:

- [`consented-action.jsonl`](../conformance/valid/consented-action.jsonl) — a scoped
  property action with prior Consent
- [`accepted-agreement.jsonl`](../conformance/valid/accepted-agreement.jsonl) — an
  Agreement accepted by every party
- [`adjudicated-violation.jsonl`](../conformance/valid/adjudicated-violation.jsonl) —
  Boundary, Action, Evidence, Claim, falsifiable Judgment, Victim-issued Mandate,
  proportion-bounded response, and Resolution
- [`self-defense.jsonl`](../conformance/valid/self-defense.jsonl) — minimum response to an
  ongoing crossing, ending when the crossing ends
- [`challenged-judgment.jsonl`](../conformance/valid/challenged-judgment.jsonl) — contrary
  Evidence, Challenge, corrected Judgment, and append-only Correction

The [`invalid`](../conformance/invalid/) vectors are equally important. They demonstrate
that an accusation without Evidence, unsupported Forfeiture, an unmandated proxy, force
against a merely predicted threat, an unfalsifiable Judgment, a response beyond
Proportion, replayed withdrawn Consent, and correction cycles must all fail conformance.
