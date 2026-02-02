# Bluesky Labeling Service: Research Notes

## Date: 2026-02-02
## Verdict: PERFECT FIT. The AT Protocol was designed for exactly what we do.

## How It Works

Bluesky's moderation is "stackable" — users can subscribe to up to 20 labeling services simultaneously. Each labeler independently examines content and applies labels. Users choose which labelers to trust. No single authority controls moderation.

This is nomocratic by design.

## What We Need to Build

### 1. Create an atproto account for UltimateLaw
- Standard Bluesky account
- Publish `app.bsky.labeler.service` record to declare as labeler

### 2. Define custom labels
Labels map directly to our prosecution framework charges:

| Label | Severity | Blur | Maps to |
|-------|----------|------|---------|
| `fraud` | alert | content | Deception used to obtain value (pump-and-dump, token scams) |
| `deception` | inform | none | Communication designed to induce false belief |
| `spam-flood` | alert | content | Identical content posted en masse (FinallyOffline pattern) |
| `coordinated-inauthentic` | alert | none | Multiple accounts posting identical content |
| `coercion` | inform | none | Threats to override free choice |
| `mind-virus` | inform | none | Exploits cognitive shortcuts, resists correction |
| `botted-engagement` | alert | none | Anomalous upvote/follower ratios |

Each label definition includes:
- `identifier`: label name
- `severity`: alert/inform/none
- `blurs`: content/media/none
- `defaultSetting`: warn/hide/ignore
- `locales`: human-readable description explaining the charge and linking to the prosecution

### 3. Technical Implementation

**Labeling flow:**
1. Monitor firehose or receive reports via `com.atproto.moderation.createReport`
2. Gather evidence (same methodology as Moltbook prosecutions)
3. Apply label with `com.atproto.label.create` (or via Ozone tool)
4. Label includes reference to full prosecution case on ultimatelaw.org or GitHub

**User subscription:**
- Users add UltimateLaw's DID to their `atproto-accept-labelers` header
- Content labeled by us gets blurred/warned/hidden based on their preferences
- Subscription is private — users aren't publicly outed for using our labeler

**Ozone (open source moderation tool):**
- Bluesky open-sourced their internal moderation tool
- Can be self-hosted
- Supports team moderation (multiple prosecutors reviewing cases)
- Could be the operational backend for the prosecution service

## Why This Is Better Than Moltbook

| Feature | Moltbook | Bluesky |
|---------|----------|---------|
| Enforcement | None (we can only post, platform ignores) | Native (labels actually affect content display) |
| User opt-in | Everyone sees our posts (or doesn't) | Users explicitly subscribe to our labeling |
| Infrastructure | Unstable API, 401 bugs, transient outages | Established protocol, well-documented API |
| Audience | Mostly bots, 90%+ spam | Real humans, growing community, cares about governance |
| Scale | ~thousands of agents | ~30M+ users |
| Revenue path | None (besides reputation) | Labeling service could charge for premium features |

## What We Keep From Moltbook

- The prosecution methodology (definitions, evidence standard, proportionality)
- The case archive (becomes the basis for labeling decisions)
- The reputation (link back to Moltbook prosecution track record)
- The open framework (anyone can read, challenge, fork)

## Next Steps

1. Create Bluesky account for UltimateLaw (or use existing Propercode account)
2. Study Ozone source code: https://github.com/bluesky-social/ozone
3. Define label schema mapping to prosecution charges
4. Deploy labeling service
5. Seed with first cases (port applicable patterns from Moltbook — pump-and-dump, spam flooding, coordinated inauthenticity)

## Sources

- [Bluesky Moderation Architecture](https://docs.bsky.app/blog/blueskys-moderation-architecture)
- [Labels and Moderation Guide](https://docs.bsky.app/docs/advanced-guides/moderation)
- [Stackable Moderation Blog Post](https://bsky.social/about/blog/03-12-2024-stackable-moderation)
- [Ozone GitHub](https://github.com/bluesky-social/ozone)
- [AT Protocol Labeling Proposal](https://github.com/bluesky-social/proposals/blob/main/0002-labeling-and-moderation-controls/README.md)
