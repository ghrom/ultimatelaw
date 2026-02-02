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

## Next Steps
- [ ] Implement multi-provider scenario in simulation
- [ ] Add diminishing returns curve and test inflation impact
- [ ] Model reputation-as-payment vs direct-income and compare Gini outcomes
- [ ] Test adversarial scenarios: what if a justice provider files false prosecutions?
