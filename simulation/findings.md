# Trust-Backed Economy Simulation: Findings

## Date: 2026-02-02
## Tool: economy-sim.py

## Core Question
Does a trust-backed IOU currency resist inflation under user growth (+1 per timestep)?
Can justice services be sustainably funded without "printing money"?

## Key Findings

### 1. Trust-backed currency experiences moderate inflation under growth
- Standard scenario (10 initial, +1/step, 300 steps): +149% inflation
- Stress test (20 initial, +2/step, 500 steps): +95% inflation
- This is significantly less than unbacked fiat (which can inflate arbitrarily)
- The trust backing provides a natural ceiling but does not eliminate inflation entirely

### 2. Justice provider REDUCES inflation
- Standard: price level 0.320 → 0.260 (19% reduction)
- Stress: price level 0.386 → 0.284 (26% reduction)
- Mechanism: prosecution removes trust from fraudulent actors, reducing their IOU capacity. This contracts the money supply from bad actors while preserving it for honest ones.
- The justice provider acts as a natural monetary policy tool — fraud prosecution IS deflationary policy.

### 3. Justice provider IMPROVES trust/IOU ratio
- Standard: 0.413 → 0.465
- Stress: 0.336 → 0.421
- Higher trust/IOU ratio = healthier economy. More trust backing each unit of currency.

### 4. CRITICAL: Single justice provider creates extreme inequality
- Standard Gini: 0.013 (no justice) → 0.046 (with justice)
- Stress Gini: 0.011 (no justice) → 0.989 (with justice)
- The justice provider accumulates trust rewards from every prosecution, compounding their IOU capacity. Over long runs, they hold nearly all economic power.
- This is the "prosecutor monopoly" problem: even honest prosecution, if concentrated in one entity, creates a dangerous power imbalance.

## Design Implications

### Problem: Monopoly prosecution creates inequality
Even if the prosecutor is honest and the framework is open, a single provider accumulates disproportionate economic power through trust rewards.

### Solutions (ranked by alignment with framework):

**A. Multiple competing justice providers**
- Any agent can file prosecutions using the open framework
- Competition prevents monopoly accumulation
- Quality is maintained by community vote on prosecution outcomes
- Natural market: if one prosecutor is unfair, others can counter-prosecute

**B. Diminishing trust returns from prosecution**
- First N prosecutions per period earn full trust rewards
- After threshold, rewards taper (logarithmic curve)
- Prevents runaway accumulation while still incentivizing prosecution work

**C. Reputation-as-payment (not direct IOU income)**
- Prosecution builds trust score (reputation) but does NOT directly issue IOUs
- Higher trust = more IOU issuance capacity, but you still need willing trade partners
- Cannot "cash out" reputation — it only enables future voluntary exchanges
- Most aligned with the framework: you earn the ability to participate more, not a direct payout

**D. Community-funded prosecution pool (rejected)**
- Percentage of all transactions funds prosecution services
- Rejected because: requires mandatory extraction (tax), which violates voluntary interaction principle
- However: a VOLUNTARY "commons protection" subscription could work — agents opt in

### Recommended design: C + A
Reputation-as-payment with multiple competing providers. The framework is open (anyone can prosecute). Reputation is earned (not extracted). Competition prevents monopoly. The simulation shows this combination would:
- Reduce inflation (prosecution removes bad-actor IOU capacity)
- Maintain healthy trust ratios
- Prevent wealth concentration (no single provider dominates)
- Align with Ultimate Law principles (voluntary, no coercion, no extraction)

## Multi-Provider Simulation Results (2026-02-02)

### Methodology
Extended `economy-sim.py` with 6 scenarios, stress-tested at 500 steps, 20 initial agents, +2/step, 20% fraud rate:

| Scenario | Description | Final Gini | Inflation vs A | Trust/IOU |
|---|---|---|---|---|
| A | No justice (baseline) | 0.078 | baseline (+3.4%) | 0.098 |
| B | Single provider (monopoly) | 0.124 | -29.9% | 0.177 |
| C | 3 competing providers | 0.164 | -29.0% | 0.180 |
| D | 3 providers + diminishing returns | 0.164 | -29.0% | 0.113 |
| E | 3 + diminishing + reputation-only | 0.173 | -34.2% | 0.112 |
| F | 3 + diminishing + rep-only + trust cap | **0.103** | **-31.4%** | 0.073 |

### Key Findings

**5. Multiple providers alone make inequality WORSE, not better**
- C (3 providers, Gini 0.164) is worse than B (1 provider, Gini 0.124)
- Having more prosecutors doesn't fix the wealth concentration problem — it diffuses prosecution trust across more agents but doesn't cap it
- Detection rate is fixed (70%) regardless of provider count, so the total prosecution effect is the same

**6. Diminishing returns alone are insufficient**
- D identical to C (Gini 0.164) — the logarithmic taper doesn't bind hard enough at this prosecution volume
- The threshold (3 per period) is rarely hit when prosecution events are spread across multiple providers

**7. Reputation-only creates the best deflation control**
- E achieves -34.2% deflation vs baseline — best inflation control of any scenario
- Without direct IOU fees, money supply grows slower
- But Gini (0.173) is slightly worse — prosecutors still accumulate trust advantage from IOU capacity

**8. Trust cap is the critical mechanism**
- F achieves Gini 0.103 — only +0.025 above baseline with no justice
- The prosecution trust cap (5.0) prevents unbounded trust accumulation from prosecution
- Combined with reputation-only (no direct IOU income) and diminishing returns, this creates:
  - Strong inflation control (-31.4%)
  - Near-baseline inequality
  - Competition (3 providers, no monopoly)
  - Natural ceiling on prosecutor economic power

**9. Model fix: new-agent bootstrap**
- Original model gave new agents trust=0, balance=0 — permanently excluding them from the economy
- This created artificial Gini inflation (0.992) as hundreds of zero-wealth agents accumulated
- Fix: small initial trust (0.1) lets new agents issue limited IOUs and enter the economy
- Real economies have analogues: initial credit lines, community introductions, probationary trust

### Revised Design Recommendation

**Optimal: Scenario F — Multiple providers + diminishing returns + reputation-only + trust cap**

The trust cap is the key innovation. Without it, even well-designed multi-provider systems create inequality. The cap works because:
1. Prosecutors can earn trust through prosecution up to a ceiling
2. Beyond the ceiling, they must earn trust through regular honest trade like everyone else
3. This preserves the incentive to prosecute (you DO earn trust) while preventing role-based wealth concentration
4. Combined with reputation-only (no direct fees), prosecution is rewarded with participation capacity, not extraction

This maps directly to the framework principle: justice should be compensated with reputation (ability to participate more in the economy), not with direct payment (which creates conflict of interest).

## Next Steps
- [ ] Test adversarial scenarios: what if a justice provider files false prosecutions?
- [ ] Calibrate trust cap value — is 5.0 optimal, or is there a principled way to derive it?
- [ ] Model justice provider entry/exit — what happens when a new provider enters a market with established incumbents?
- [ ] Test with variable fraud rates across agents (some agents more fraud-prone than others)
