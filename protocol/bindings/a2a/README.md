# ULP-A2A/1 Binding

`ULP-A2A/1` carries complete Ultimate Law Protocol (`ULP/1`) record streams through
Agent2Agent (`A2A`) messages without changing either protocol's core objects.

The binding targets A2A `1.0` and was checked against the A2A `v1.0.1` specification.
It uses A2A's standard extension negotiation, `Message.extensions`, namespaced
`Message.metadata`, and structured `Part.data` content.

Upstream references are pinned to the
[A2A v1.0.1 release](https://github.com/a2aproject/A2A/releases/tag/v1.0.1), its
[extension rules](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/topics/extensions.md),
and its [protocol types](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto).

## Relationship

| Layer | Responsibility |
|---|---|
| A2A | Discovery, transport, messages, tasks, streaming, and authentication |
| ULP | Boundaries, Consent, Evidence, Claims, Judgments, Mandates, and Proportion |
| ULP-A2A | Negotiation and lossless carriage of ULP records through A2A |

A2A task state never substitutes for ULP state. In particular, task acceptance is not
Consent, authentication is not truth, task completion is not Judgment, and task
cancellation is not necessarily withdrawal of Consent.

## Identifiers

- Extension URI: `https://ultimatelaw.org/protocol/extensions/ulp/v1`
- Profile: `ULP-A2A/1`
- Record media type: `application/vnd.ultimatelaw.records+json;version=1`
- ULP wire protocol: `ultimate-law/1`

## Quick start

Wrap a conforming ULP stream as an A2A message:

```powershell
python protocol/bindings/a2a/reference/adapter.py wrap `
  protocol/conformance/valid/consented-action.jsonl `
  --role ROLE_USER `
  --message-id msg-001 `
  --context-id ctx-001
```

Validate and extract a bound message:

```powershell
python protocol/bindings/a2a/reference/adapter.py validate `
  protocol/bindings/a2a/conformance/valid/message.json

python protocol/bindings/a2a/reference/adapter.py unwrap `
  protocol/bindings/a2a/conformance/valid/message.json
```

Run all kernel and binding tests:

```powershell
python -m unittest discover -s protocol/tests -v
```

## Contents

- [`SPECIFICATION.md`](SPECIFICATION.md) — normative binding rules
- [`agent-card.fragment.json`](agent-card.fragment.json) — mergeable Agent Card declaration
- [`schema/`](schema/) — metadata, message-profile, and AgentExtension schemas
- [`reference/adapter.py`](reference/adapter.py) — dependency-free wrapping and extraction
- [`conformance/`](conformance/) — valid and intentionally invalid A2A vectors

## Deployment rule

This binding carries and checks records; it does not make them true and does not grant
permission to an actuator. A boundary-gating deployment must combine ULP validation with
identity verification, evidence evaluation, the application's mapping from operations
to boundaries, and a reversible execution policy.

Before public interoperability release, the extension URI must serve or redirect to the
published specification. Until then it is a stable identifier implemented by this
repository, not a claim that the public URL is already deployed.
