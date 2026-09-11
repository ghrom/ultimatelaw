# Ultimate Law Protocol 1.0

## 1. Scope

Ultimate Law Protocol 1.0 (`ULP/1`) defines a JSON record format and semantic
conformance rules for voluntary coordination and falsifiable dispute resolution between
agents.

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHOULD**, **SHOULD NOT**, and **MAY**
are normative requirements.

ULP is transport-neutral. Records may be carried over HTTP, message queues, peer-to-peer
networks, append-only logs, files, or other media. Transport does not change their
meaning.

## 2. Constitutional binding

Normative terms are defined by the repository's Coherent Dictionary of Simple English.
`ontology/core.json` contains:

- the source path;
- the SHA-256 digest of the dictionary revision implemented by this protocol;
- the terms used by the kernel; and
- machine-readable summaries of the kernel invariants.

A Judgment MUST name this digest. A different digest identifies a different semantic
constitution even if its wire format is still `ULP/1`.

If this specification conflicts with the pinned dictionary, the dictionary governs the
meaning and the protocol is in Error. The specification and its conformance vectors must
then be corrected and versioned.

## 3. Conformance is not truth

There are three distinct questions:

1. **Structural conformance:** Does the record have the required shape and values?
2. **Stream conformance:** Do its references and derived states follow ULP rules?
3. **Truth:** Do its claims match reality?

The reference validator answers only the first two. It cannot authenticate observations,
prove identity, discover omitted evidence, or authorize force. A conforming lie remains
a lie. A signed lie remains a lie.

## 4. Record envelope

Every record is a JSON object with these members:

| Member | Requirement | Meaning |
|---|---|---|
| `protocol` | REQUIRED | The exact string `ultimate-law/1` |
| `id` | REQUIRED | A globally unique `urn:uuid:` identifier |
| `type` | REQUIRED | One of the record types in section 5 |
| `issued_at` | REQUIRED | UTC timestamp in RFC 3339 `...Z` form |
| `issuer` | REQUIRED | URI identifying the agent making this record |
| `payload` | REQUIRED | Type-specific object |
| `proof` | OPTIONAL | Cryptographic proof metadata |

An issuer is the source of a statement, not an authority over its subject. Implementations
MUST preserve the original record bytes or a canonical representation when signatures
are used. A signature profile SHOULD use deterministic JSON canonicalization and MUST
state exactly which bytes were signed.

The core validator checks proof shape but does not perform cryptographic verification.
Applications MUST NOT present a proof as verified unless a configured cryptographic
profile has actually verified it.

## 5. Record types

### 5.1 `boundary`

Declares a boundary over a body, property, freedom, or agreement.

Required payload members: `holder`, `kind`, `object`, `protection`.

The issuer MUST be the holder. `protection` is `intact` in a declaration. An agent cannot
make another agent's boundary forfeit merely by issuing a record.

### 5.2 `consent`

Grants or withdraws consent for a defined agent, action, object, and scope.

Required payload members: `grantor`, `grantee`, `action`, `object`, `scope`, `state`.

The issuer MUST be the grantor. Consent is not transferable beyond the stated scope. A
withdrawal SHOULD reference the grant it supersedes. Duress, deception, or manipulation
invalidates Consent even if the wire record is structurally valid.

### 5.3 `agreement`

Records an offer, acceptance, rejection, or termination of identified terms.

Required payload members: `parties`, `terms_digest`, `state`.

An accepted agreement MUST reference enough `consent` records to establish every party's
acceptance. A digest establishes content identity, not understanding or voluntary assent.

### 5.4 `action`

Describes an observed action without deciding its legal meaning.

Required payload members: `actor`, `verb`, `object`, `occurred_at`.

Optional `boundary_ref` and `consent_ref` members connect the action to prior records.
The issuer may be the actor or an observer; consumers must not silently confuse the two.

### 5.5 `evidence`

Identifies information offered to increase or decrease the probability of a Claim.

Required payload members: `statement`, `source`, `observed_at`, `content_digest`.

A digest demonstrates sameness of content, not authenticity, completeness, causation, or
truth. Evidence SHOULD be reproducible or independently inspectable where doing so does
not violate another boundary. Correlation MAY be Evidence that a connection exists, but
MUST NOT be treated as Causation or as sufficient grounds for Responsibility.

### 5.6 `claim`

Alleges that an action crossed a boundary and maps that allegation to named terms.

Required payload members: `claimant`, `respondent`, `victim`, `action_ref`,
`boundary_ref`, `evidence_refs`, `allegations`.

The issuer MUST be the claimant. `evidence_refs` MUST be non-empty. A Claim with no
specific Victim, Action, Boundary, and Evidence is nonconforming. Conformance does not
make the respondent guilty.

### 5.7 `judgment`

Makes a falsifiable statement about how the pinned Law applies to a Claim.

Required payload members: `judge`, `claim_ref`, `evidence_refs`, `dictionary_digest`,
`falsifiable`, and `findings`.

The issuer MUST be the Judge. `falsifiable` MUST be `true`. Findings MUST separately state:

- whether causation is proven;
- whether boundary crossing is proven;
- whether the crossed boundary was intact;
- whether a Victim exists;
- whether Guilt exists;
- whether Forfeiture follows;
- which Law terms were applied;
- which boundary kinds, if any, bound a proportionate response; and
- what Restitution repairs.

A Judgment may record `forfeiture: proven` only when causation and boundary crossing are
`proven`, the crossed boundary was `intact`, a Victim was found, and `Forfeiture` is among
the applied terms. A protocol record discovers or reports these consequences; it does
not create them.

A Judgment that records `causation: proven` MUST apply the `Causation` term. Applying
`Correlation` without `Causation` cannot support that finding. Structural conformance
still cannot prove that the cited Evidence establishes the claimed causal link.

### 5.8 `mandate`

Delegates the Victim's power to a proxy within explicit limits.

Required payload members: `principal`, `delegate`, `judgment_ref`, `powers`, `kinds`,
and `state`.

The issuer MUST be the principal. The principal MUST be the Victim identified by the
Claim underlying the Judgment. A Mandate does not authorize acts beyond its powers,
boundary kinds, Judgment, validity period, or revocation state.

### 5.9 `response`

Describes an action justified as `self-defense` or `justice`.

Required payload members: `actor`, `target`, `basis`, `action`, and `kind`.

For `self-defense`, the record MUST reference the crossing Action and protected Boundary;
the threat state MUST be `ongoing` or `immediately_credible`; and `minimal_force`,
`causally_directed`, and `ends_when_crossing_ends` MUST all be `true`.

For `justice`, the record MUST reference a conforming Judgment. Its `kind` MUST be within
the Judgment's `permitted_response_kinds`. If the actor is not the Victim, it MUST also
reference an active Mandate whose delegate, powers, kinds, principal, and Judgment match
the response.

A conforming response record is still only a statement. Implementations MUST NOT wire
the validator directly to an irreversible actuator.

### 5.10 `resolution`

Records the Victim's collection or voluntary release of the moral debt.

Required payload members: `victim`, `judgment_ref`, `mode`, and `moral_debt`.

The issuer MUST be the Victim. `mode` is `collection` or `release`; `moral_debt` is
`closed`. Restitution repairs material Damage and may be recorded separately from the
Victim's closure of moral debt.

### 5.11 `challenge`

Challenges a record on evidentiary, causal, logical, identity, scope, or proof grounds.

Required payload members: `target_ref`, `grounds`, `statement`.

Any agent MAY issue a challenge. Receiving a challenge does not itself invalidate the
target, but systems MUST retain it alongside the challenged record and SHOULD prioritize
review before irreversible action.

### 5.12 `correction`

Links an erroneous record to a replacement record.

Required payload members: `target_ref`, `replacement_ref`, `reason`.

Records are append-only: correction does not erase history. Consumers resolve current
state by following valid correction links while retaining the superseded record for
audit.

## 6. Reference integrity

Within a validated stream:

- record IDs MUST be unique;
- every referenced record MUST exist;
- a reference MUST point to the required record type;
- cycles in correction links MUST be rejected;
- an issuer MUST NOT be silently substituted for an actor, holder, grantor, claimant,
  Judge, principal, or Victim; and
- timestamps MUST use UTC, though ordering alone MUST NOT be treated as proof of causation.

An application may receive a partial stream. It may preserve unresolved records, but it
MUST label them incomplete and MUST NOT derive permission from unresolved references.

## 7. Derived-state rules

The kernel applies these conservative rules:

1. A Boundary begins intact; a Claim does not change it.
2. A signature authenticates a key's statement only after verification; it does not make
   the statement true.
3. Forfeiture may be reported only by a falsifiable, evidence-linked Judgment satisfying
   section 5.7.
4. A Justice response may not exceed the kinds allowed by the Judgment.
5. A proxy has no power without a matching, active Victim-issued Mandate.
6. Self-Defense ends when the ongoing or immediately credible crossing ends.
7. A challenge remains visible until answered, corrected, or explicitly rejected with
   reasons and evidence.
8. Failed proof, missing evidence, unresolved identity, or contradictory facts MUST fail
   closed: they create no permission to cross a boundary.
9. Correlation, statistical association, resemblance, and group membership do not prove
   Causation and do not transfer Responsibility.

## 8. Extension rules

Extensions MUST use namespaced payload members or a separately versioned profile. An
extension MUST NOT:

- turn votes, status, model confidence, or institutional signatures into truth;
- weaken Consent or broaden a Mandate;
- infer collective responsibility from group membership;
- make punishment exceed Proportion;
- hide evidence or challenges required to evaluate a Judgment; or
- redefine a pinned dictionary term without changing the dictionary digest.

Unknown extensions SHOULD be preserved and ignored. If an unknown extension is required
to justify a boundary crossing, the record is incomplete for that receiver and must fail
closed.

## 9. Versioning

Backward-compatible clarifications retain `ultimate-law/1` and update the conformance
suite. A wire-incompatible change, a weakened safety invariant, or a changed derivation
rule requires a new protocol version. A changed dictionary always requires a new
`dictionary_digest`, even when no wire field changes.
