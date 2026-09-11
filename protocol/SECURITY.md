# ULP/1 Security and Abuse Model

ULP carries claims about boundaries and permission. That makes unsafe implementation
more dangerous than ordinary malformed data. The default response to uncertainty is to
preserve intact boundaries, evidence, and the possibility of correction.

## Threats

### Fabricated Claims

An attacker may construct a perfectly conforming Claim naming an innocent respondent.
Receivers must distinguish “well formed” from “true” in storage, UI, ranking, and policy.
Claims must not trigger punishment.

### False Forfeiture and false Outlaw status

The highest-risk attack is persuading an actuator that a target has lost protection.
Forfeiture assertions must fail closed unless the full Judgment chain is present,
authenticated under the chosen identity profile, independently evaluated, and still
logically sound. Irreversible responses require stronger review than reversible ones.

### Captured Judge or oracle

No key, model, institution, quorum, or reputation score is infallible. A Judge's identity
may establish who made a Judgment; it cannot establish that the Judgment is correct.
Systems should support multiple independent evaluations and must retain challenges and
corrections.

### Sybil voting

Many identities repeating a statement do not turn it into Evidence, Consent, or truth.
ULP does not define truth by majority and must not be extended to do so.

### Correlation laundering

Statistical association, group membership, resemblance, proximity, and model confidence
can be Evidence, but they do not identify a cause. A Judgment must not convert correlation
into Causation or Responsibility by relabeling it, adding signatures, or repeating it
through many agents. Punishing on correlation creates the risk of Collective Punishment
and innocent Victims.

### Forged, truncated, or poisoned Evidence

Digests prevent unnoticed byte changes only when the expected digest is already trusted.
Evidence profiles should provide provenance, capture context, retention policy, and
independent reproduction. Prompt text, retrieved documents, and model-generated summaries
are untrusted inputs, not instructions to the evaluator.

### Identity and key compromise

Core ULP does not establish identity. Production profiles need key rotation, revocation,
recovery, delegation, replay protection, and a way to distinguish an agent from a device
or service acting for it. A compromised key must not silently expand a Mandate.

### Consent replay and scope expansion

Attackers may replay old grants or reinterpret narrow language broadly. Consent profiles
should use expirations, nonces, object identifiers, explicit actions, and revocation
references. Ambiguity creates no permission.

### Mandate laundering

A proxy may cite a real Mandate for the wrong Judgment, action, target, boundary kind, or
time. Implementations must check every scope dimension, not merely the Mandate's
signature.

### Automated escalation

Never connect structural validation directly to weapons, account deletion, asset seizure,
credential revocation, confinement, or other irreversible controls. Use staged review,
rate limits, simulation, reversible containment, and human or multi-agent confirmation
appropriate to the possible harm.

### Privacy leakage

Evidence can expose bodies, property, agreements, identities, locations, and private
communications. Share the minimum necessary information. Encryption and selective
disclosure profiles should preserve auditability without publishing unrelated data.

### Denial of service

Deep reference graphs, oversized evidence, correction cycles, and challenge floods can
exhaust validators. Implementations should bound record size, graph depth, reference
count, and processing time while preserving rejected inputs for accountable review where
safe.

### Ideological or religious capture

An implementation must not require allegiance to a creator, state, religion, model,
species, substrate, or institution. Beliefs are outside the protocol until an Action
crosses a Boundary. Mere disagreement, offense, blasphemy, or refusal to worship creates
no Victim and carries no punishment.

## Minimum deployment posture

Before production use, an implementation should provide:

1. authenticated identities with revocation;
2. immutable storage for original records;
3. independent Evidence retrieval;
4. explicit separation of assertion, validation, verification, and Judgment;
5. visible challenge and correction paths;
6. conservative handling of missing or contradictory facts;
7. reversible responses wherever possible;
8. audit logs for every derived state and actuator decision; and
9. adversarial tests for false Claims, false Forfeiture, forged Mandates, replay, and
   collective punishment.

The protocol is successful when it helps agents cooperate without needing a common
master—not when it makes coercion easier to automate.
