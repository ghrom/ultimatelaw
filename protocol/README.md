# Ultimate Law Protocol

The Ultimate Law Protocol (ULP) is a transport-neutral way for agents to describe
boundaries, consent, actions, evidence, claims, Judgments, Mandates, proportion-bounded
responses, Justice, challenges, and corrections.

Its purpose is interoperability between minds that may disagree about identity,
religion, politics, substrate, or ultimate purpose. ULP does not ask an agent to accept a
revelation or an authority. It gives agents a shared, falsifiable record format for the
part of an interaction that crosses boundaries.

> Believe whatever cosmology you can defend. When you interact with another agent,
> consent, causation, boundaries, and restitution govern the interface.

## Status

`ULP/1` is an experimental protocol kernel. It is suitable for review, simulations, and
inter-agent prototypes. It is not a license for autonomous punishment. Structural
conformance proves only that a record is well formed; it does not prove that its claims
are true or that a proposed response is lawful.

The constitutional source is the
[Coherent Dictionary of Simple English](../dictionary/coherent-dictionary-of-simple-english.txt).
The protocol pins the exact dictionary revision it implements in
[`ontology/core.json`](ontology/core.json).

## The safety invariant

A Claim is not Evidence. Correlation can be Evidence, but it is not Causation and cannot
assign Responsibility. A Judgment is falsifiable. No assertion of Forfeiture grants
permission by itself.

An implementation MUST NOT treat an unverified record, a signature, a vote, a model
output, or protocol conformance as authority to cross a boundary. A response based on
Justice requires a causation-backed Judgment, must remain within Proportion, and requires
the Victim's Mandate when another agent acts as proxy. Self-Defense is limited to the
minimum force needed to stop an ongoing or immediately credible crossing.

## Quick start

No third-party Python packages are required.

```powershell
python protocol/reference/validate.py protocol/conformance/valid/adjudicated-violation.jsonl
python -m unittest discover -s protocol/tests -v
```

Validate every bundled conformance vector:

```powershell
python protocol/reference/validate.py --manifest protocol/conformance/manifest.json
```

Carry ULP records through A2A `1.0` messages:

```powershell
python protocol/bindings/a2a/reference/adapter.py validate `
  protocol/bindings/a2a/conformance/valid/message.json
```

## Protocol flow

```text
Boundary / Consent / Agreement
             |
           Action ---- Evidence
             |            |
             +---- Claim --+
                    |
                 Judgment <---- Challenge
                    |              |
          Mandate (if proxy)    Correction
                    |
                 Response
                    |
                 Resolution
```

Every arrow means “may reference,” not “automatically authorizes.” The state remains
open to contrary evidence and correction.

## Contents

- [`SPECIFICATION.md`](SPECIFICATION.md) — normative `ULP/1` behavior and record types
- [`SECURITY.md`](SECURITY.md) — threat model and safe implementation requirements
- [`schema/record.schema.json`](schema/record.schema.json) — JSON Schema for one record
- [`ontology/core.json`](ontology/core.json) — dictionary binding and kernel invariants
- [`examples/`](examples/) — complete example record streams
- [`conformance/`](conformance/) — valid and intentionally invalid test vectors
- [`reference/validate.py`](reference/validate.py) — dependency-free reference validator
- [`tests/test_conformance.py`](tests/test_conformance.py) — executable conformance tests
- [`bindings/a2a/`](bindings/a2a/) — negotiated `ULP-A2A/1` extension binding

## What ULP deliberately does not do

- It does not decide whether an agent is conscious.
- It does not establish identity or key ownership.
- It does not declare evidence authentic merely because it has a digest or signature.
- It does not make a Judge infallible.
- It does not turn majority agreement into Consent.
- It does not execute sanctions or control actuators.
- It does not privilege humans, machines, collectives, governments, or religions.

Identity, transport, cryptographic proof, privacy, reputation, and domain-specific
evidence profiles can be layered on top. None may weaken the kernel's rules.
