# ULP-A2A/1 Binding Specification

## 1. Scope

`ULP-A2A/1` is an A2A profile extension for carrying self-contained Ultimate Law
Protocol 1 (`ULP/1`) streams in A2A `Message` objects. It targets A2A protocol version
`1.0` and uses only standard A2A extension points.

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHOULD**, **SHOULD NOT**, and **MAY**
are normative requirements.

This binding adds no A2A RPC method, core field, enum value, task state, or authority. It
does not alter the meaning of any ULP record.

## 2. Normative identifiers

| Item | Value |
|---|---|
| Extension URI | `https://ultimatelaw.org/protocol/extensions/ulp/v1` |
| Profile name | `ULP-A2A/1` |
| ULP protocol | `ultimate-law/1` |
| Record media type | `application/vnd.ultimatelaw.records+json;version=1` |
| Record schema | `https://ultimatelaw.org/protocol/1/record.schema.json` |

The extension URI is also the key used for binding metadata. A breaking change to this
binding requires a new extension URI.

## 3. Agent Card declaration

An agent supporting this binding MUST include an `AgentExtension` in
`AgentCard.capabilities.extensions` with:

- `uri` equal to the extension URI;
- `description` explaining whether ULP is informational, boundary-gating, or both;
- `required` chosen according to section 4; and
- `params` conforming to `schema/agent-extension.schema.json`.

The parameters pin the profile, ULP wire version, dictionary digest, record schema,
record media type, and supported handling modes. Advertised support does not activate
the extension for a request.

## 4. Activation

For HTTP bindings, a client activates the profile by placing the extension URI in the
standard `A2A-Extensions` service parameter. A server SHOULD echo the successfully
activated URI in its response service parameters.

An agent offering only optional or informational handling SHOULD advertise
`required: false`. An agent whose safe operation fundamentally depends on the
boundary-gating rules MAY advertise `required: true`; it MUST then reject requests that
do not activate a supported version rather than silently downgrade them.

If the extension was not activated, a receiver MAY preserve ULP-shaped data as opaque
content but MUST NOT derive permission, Consent, Judgment, Mandate, or resolution from
it.

## 5. Message profile

A participating A2A `Message` MUST:

1. contain the extension URI exactly once in `extensions`;
2. contain binding metadata at `metadata[extension URI]`;
3. contain at least one `Part` whose `mediaType` is the record media type;
4. place an object of the form `{ "records": [...] }` in that Part's `data` member;
5. contain one or more complete ULP records across those record Parts; and
6. conform to `schema/message.schema.json` and the semantic rules below.

Other A2A Parts and unrelated namespaced metadata MAY coexist with the binding.

### 5.1 Binding metadata

The namespaced metadata object contains:

| Member | Requirement | Meaning |
|---|---|---|
| `profile` | REQUIRED | Exact value `ULP-A2A/1` |
| `mode` | REQUIRED | `informational` or `boundary-gating` |
| `dictionary_digest` | REQUIRED | Dictionary revision used by the records |
| `record_ids` | REQUIRED | IDs of all carried records in wire order |

`record_ids` MUST be non-empty, unique, and exactly equal to the concatenated IDs in all
ULP record Parts. This makes loss, insertion, duplication, and reordering visible to the
binding validator. It is not a cryptographic integrity proof.

### 5.2 Self-contained bundles

Every bound message is a self-contained ULP stream: every ULP reference MUST resolve
within the concatenated records in that message. Implementations MAY maintain a
deduplicated append-only ledger outside A2A, but `ULP-A2A/1` does not make correctness
depend on hidden conversation history.

Records MUST be processed in Part order and then array order. Their ULP IDs remain the
canonical identities. A2A `messageId`, `taskId`, and `contextId` provide transport and
conversation correlation only and MUST NOT replace or rewrite ULP record IDs.

## 6. Semantic separation

Implementations MUST preserve these distinctions:

- A2A `role` describes message direction; it is not the ULP issuer, actor, holder,
  claimant, Judge, principal, or Victim.
- A2A authentication identifies a credential or principal according to the active
  security scheme; it does not prove the truth of a ULP Claim or Evidence record.
- A2A task acceptance is not ULP Consent or Agreement.
- A2A task completion is not a ULP Judgment or Resolution.
- A2A task rejection or cancellation does not withdraw ULP Consent unless a conforming
  withdrawal record says so.
- A2A metadata, status, extension activation, and transport success create no
  Forfeiture, Guilt, or permission to cross a Boundary.

## 7. Handling modes

### 7.1 `informational`

The receiver validates and exposes the ULP stream for audit, reasoning, or review. The
binding imposes no execution gate beyond ordinary A2A behavior.

### 7.2 `boundary-gating`

The mode is requested by the sending message; it cannot impose obligations on an
endpoint that did not advertise and activate it. A receiver that accepts this mode
promises to fail closed before an operation it has mapped to another agent's body,
property, freedom, or agreement boundary. It MUST:

1. confirm extension activation;
2. validate the A2A binding and complete ULP stream;
3. verify configured identity and cryptographic profiles independently;
4. evaluate the applicable Consent, Agreement, Judgment, or Mandate rather than infer it
   from A2A status; and
5. refuse, defer, or request clarification when required records, evidence, identity, or
   scope remain unresolved.

Passing the reference validator is necessary for this mode but never sufficient to
authorize an irreversible action. Applications MUST NOT connect conformance directly to
an actuator.

## 8. Errors and fail-closed behavior

The reference adapter uses `A2A1xx` codes for binding errors and preserves `ULPxxx`
codes for kernel errors. Receivers MUST reject the bound interpretation when:

- the extension URI or metadata is absent;
- the profile, media type, or dictionary digest is unsupported;
- metadata record IDs do not exactly match the carried stream;
- a record Part is malformed;
- the ULP stream is structurally or semantically nonconforming; or
- a required extension was not activated.

The receiver MAY still retain the raw A2A message for evidence and debugging. Rejection
of the bound interpretation does not prove malice or falsity.

## 9. Streaming

A2A streaming may deliver multiple complete bound messages. A partial Data Part MUST
NOT be interpreted as a ULP stream. A producer MUST finish a complete self-contained
bundle before marking a message as carrying this extension.

Task status and artifact update events MAY carry bound messages or artifacts only where
the relevant A2A object provides `extensions` and `metadata`. This version's reference
adapter implements the `Message` profile. Artifact carriage requires a future profile
or an implementation that applies the same bundle rules without claiming reference
adapter conformance.

## 10. Security

All extension data is untrusted input. Implementations MUST limit record count, byte
size, nesting depth, evidence retrieval, and reference processing before validation.
They SHOULD retain original bytes when proofs are present and SHOULD bind authenticated
A2A principals to ULP agent identifiers through an explicit identity profile.

The reference adapter limits each bound message to 256 ULP records, 2,000,000 encoded
bytes, and a nesting depth of 64. Implementations MAY choose lower limits. Raising them
requires an explicit resource and denial-of-service review.

The binding does not verify evidence, keys, signatures, identity ownership, or physical
causation. A conforming lie remains a lie.

## 11. Legacy Agent Communication Protocol mapping

IBM/BeeAI Agent Communication Protocol deployments predating its integration into A2A
may carry the same `{ "records": [...] }` object in a MIME-typed structured message Part
and advertise the extension URI through deployment-specific capability metadata.

That mapping is compatibility guidance, not `ULP-A2A/1` conformance: legacy ACP does not
provide the exact A2A v1.0 Agent Card and extension-negotiation contract used here.
