"""
Trust-Backed Economy Simulator
================================
Models a trust-backed IOU currency system under growth.

Core question: Does adding users (+1 per timestep) cause inflation,
or does trust-backed issuance naturally resist it?

Model:
- N agents, each with a trust score and productive capacity
- Trust score determines how many IOUs an agent can issue
- Agents trade services each timestep (random bilateral trades)
- New agent joins each timestep (starts with trust=0)
- Trust grows through honest transactions, decays through defaults

Scenarios:
- Baseline: no justice providers
- Single provider: one monopoly prosecutor (original model)
- Multi-provider: multiple competing prosecutors with diminishing returns
- Reputation-as-payment: prosecution builds trust but no direct IOU income

Usage:
    python economy-sim.py --compare                # single vs none
    python economy-sim.py --compare-all            # all 4 scenarios
    python economy-sim.py --justice-providers 3     # multi-provider
    python economy-sim.py --justice-providers 3 --diminishing-returns
    python economy-sim.py --justice-providers 3 --reputation-only
"""

import argparse
import random
import math
from dataclasses import dataclass, field
from typing import List, Dict, Tuple


@dataclass
class Agent:
    id: int
    trust_score: float = 0.0          # earned through honest transactions
    iou_capacity: float = 0.0         # max IOUs this agent can issue = trust * multiplier
    ious_issued: float = 0.0          # IOUs currently in circulation from this agent
    balance: float = 0.0              # IOUs held (from other agents)
    goods_produced: float = 0.0       # cumulative goods/services produced
    transactions: int = 0             # total transactions completed
    defaults: int = 0                 # times this agent failed to deliver
    is_justice_provider: bool = False  # provides prosecution services
    joined_at: int = 0                # timestep when agent joined
    prosecutions_this_period: int = 0  # for diminishing returns tracking
    total_prosecutions: int = 0        # lifetime prosecution count
    prosecution_trust: float = 0.0     # trust earned specifically from prosecution


@dataclass
class EconomyState:
    step: int = 0
    total_money_supply: float = 0.0
    total_goods_produced: float = 0.0
    price_level: float = 0.0
    trust_iou_ratio: float = 0.0
    gini: float = 0.0
    agent_count: int = 0
    justice_income: float = 0.0
    fraud_events: int = 0
    prosecutions: int = 0
    justice_provider_count: int = 0
    max_justice_trust: float = 0.0     # highest trust among justice providers
    justice_gini: float = 0.0          # inequality among justice providers only


TRUST_MULTIPLIER = 10.0       # 1 trust point = 10 IOUs issuance capacity
TRUST_PER_TRADE = 0.1         # trust earned per honest transaction
TRUST_DECAY_DEFAULT = 0.5     # trust lost per default
DEFAULT_FRAUD_PROBABILITY = 0.05  # 5% chance any trade is fraudulent
FRAUD_PROBABILITY = DEFAULT_FRAUD_PROBABILITY  # mutable for CLI override
JUSTICE_DETECTION_RATE = 0.7  # justice provider catches 70% of fraud
JUSTICE_REWARD = 0.2          # trust reward for successful prosecution
PRODUCTIVE_CAPACITY = 1.0     # each agent produces ~1 unit of goods per trade
DIMINISHING_RETURNS_THRESHOLD = 3  # prosecutions per period before tapering
DIMINISHING_RETURNS_PERIOD = 10    # steps per period for diminishing returns reset
PROSECUTION_TRUST_CAP = 5.0        # max trust a provider can accumulate from prosecution alone
NEW_AGENT_TRUST = 0.1              # small initial trust so new agents can enter the economy


def calculate_gini(agents: List[Agent]) -> float:
    """Calculate Gini coefficient of wealth distribution."""
    balances = sorted([a.balance for a in agents])
    n = len(balances)
    if n == 0 or sum(balances) == 0:
        return 0.0
    # handle negative balances by shifting
    min_bal = min(balances)
    if min_bal < 0:
        balances = [b - min_bal for b in balances]
    total = sum(balances)
    if total == 0:
        return 0.0
    cumulative = 0.0
    weighted_sum = 0.0
    for i, b in enumerate(balances):
        cumulative += b
        weighted_sum += (2 * (i + 1) - n - 1) * b
    return weighted_sum / (n * total)


def diminishing_reward(base_reward: float, prosecutions_this_period: int) -> float:
    """Apply logarithmic diminishing returns after threshold."""
    if prosecutions_this_period <= DIMINISHING_RETURNS_THRESHOLD:
        return base_reward
    excess = prosecutions_this_period - DIMINISHING_RETURNS_THRESHOLD
    return base_reward / (1 + math.log(1 + excess))


def pick_prosecutor(justice_providers: List[Agent]) -> Agent:
    """Pick a random justice provider (competition model)."""
    return random.choice(justice_providers)


def simulate_trade(buyer: Agent, seller: Agent, justice_providers: List[Agent],
                   use_diminishing: bool = False,
                   reputation_only: bool = False,
                   use_trust_cap: bool = False) -> Tuple[bool, bool, bool]:
    """
    Simulate a bilateral trade. Returns (success, was_fraud, was_prosecuted).

    Buyer pays IOUs, seller delivers goods.
    Fraud = seller takes payment but doesn't deliver.
    """
    trade_price = PRODUCTIVE_CAPACITY

    # can buyer afford it?
    if buyer.balance >= trade_price:
        pass
    elif buyer.ious_issued + trade_price <= buyer.iou_capacity:
        buyer.ious_issued += trade_price
    else:
        return False, False, False

    is_fraud = random.random() < FRAUD_PROBABILITY

    if is_fraud:
        buyer.balance -= trade_price
        seller.balance += trade_price
        seller.defaults += 1
        seller.trust_score = max(0, seller.trust_score - TRUST_DECAY_DEFAULT)
        seller.iou_capacity = seller.trust_score * TRUST_MULTIPLIER

        was_prosecuted = False
        if justice_providers and random.random() < JUSTICE_DETECTION_RATE:
            was_prosecuted = True
            prosecutor = pick_prosecutor(justice_providers)

            # prosecution: seller loses additional trust
            seller.trust_score = max(0, seller.trust_score - TRUST_DECAY_DEFAULT)
            seller.iou_capacity = seller.trust_score * TRUST_MULTIPLIER

            # partial restoration to buyer
            restore = trade_price * 0.5
            buyer.balance += restore
            seller.balance -= min(restore, seller.balance)

            # reputation-only: prosecutor earns trust but no direct IOU fee
            # when disabled, prosecutor takes a small fee from the restoration
            if not reputation_only:
                fee = trade_price * 0.1
                if seller.balance >= fee:
                    seller.balance -= fee
                    prosecutor.balance += fee

            # reward the prosecutor with trust
            reward = JUSTICE_REWARD
            if use_diminishing:
                reward = diminishing_reward(JUSTICE_REWARD, prosecutor.prosecutions_this_period)

            # apply trust cap if enabled
            if use_trust_cap and prosecutor.prosecution_trust >= PROSECUTION_TRUST_CAP:
                reward = 0.0  # cap reached, no more prosecution trust
            elif use_trust_cap:
                reward = min(reward, PROSECUTION_TRUST_CAP - prosecutor.prosecution_trust)

            prosecutor.trust_score += reward
            prosecutor.prosecution_trust += reward
            prosecutor.iou_capacity = prosecutor.trust_score * TRUST_MULTIPLIER

            prosecutor.prosecutions_this_period += 1
            prosecutor.total_prosecutions += 1

        return True, True, was_prosecuted
    else:
        buyer.balance -= trade_price
        seller.balance += trade_price
        seller.goods_produced += PRODUCTIVE_CAPACITY

        buyer.trust_score += TRUST_PER_TRADE * 0.5
        seller.trust_score += TRUST_PER_TRADE
        buyer.iou_capacity = buyer.trust_score * TRUST_MULTIPLIER
        seller.iou_capacity = seller.trust_score * TRUST_MULTIPLIER

        buyer.transactions += 1
        seller.transactions += 1

        return True, False, False


def run_simulation(
    initial_agents: int = 10,
    steps: int = 200,
    trades_per_step: int = 5,
    num_justice_providers: int = 0,
    growth_rate: int = 1,
    seed: int = 42,
    use_diminishing: bool = False,
    reputation_only: bool = False,
    use_trust_cap: bool = False
) -> List[EconomyState]:
    """Run the full simulation."""
    random.seed(seed)

    agents: List[Agent] = []
    for i in range(initial_agents):
        a = Agent(id=i, trust_score=1.0, joined_at=0)
        a.iou_capacity = a.trust_score * TRUST_MULTIPLIER
        a.balance = 5.0
        agents.append(a)

    # set up justice providers (first N agents)
    for i in range(min(num_justice_providers, initial_agents)):
        agents[i].is_justice_provider = True
        agents[i].trust_score = 2.0
        agents[i].iou_capacity = agents[i].trust_score * TRUST_MULTIPLIER

    history: List[EconomyState] = []

    for step in range(steps):
        # reset diminishing returns counter each period
        if use_diminishing and step % DIMINISHING_RETURNS_PERIOD == 0:
            for a in agents:
                if a.is_justice_provider:
                    a.prosecutions_this_period = 0

        # add new agents (small bootstrap trust so they can enter the economy)
        for _ in range(growth_rate):
            new_id = len(agents)
            new_agent = Agent(id=new_id, trust_score=NEW_AGENT_TRUST, joined_at=step)
            new_agent.iou_capacity = NEW_AGENT_TRUST * TRUST_MULTIPLIER
            new_agent.balance = 0.0
            agents.append(new_agent)

        step_fraud = 0
        step_prosecutions = 0
        justice_income = 0.0

        justice_providers = [a for a in agents if a.is_justice_provider]

        # run trades (scale with population)
        eligible = [a for a in agents if a.trust_score > 0 or a.balance > 0]
        num_trades = max(trades_per_step, len(eligible) // 4)
        for _ in range(min(num_trades, len(eligible) // 2)):
            if len(eligible) < 2:
                break
            buyer, seller = random.sample(eligible, 2)

            success, was_fraud, was_prosecuted = simulate_trade(
                buyer, seller, justice_providers,
                use_diminishing=use_diminishing,
                reputation_only=reputation_only,
                use_trust_cap=use_trust_cap
            )

            if was_fraud:
                step_fraud += 1
            if was_prosecuted:
                step_prosecutions += 1

        # record state
        total_supply = sum(a.ious_issued for a in agents)
        total_goods = sum(a.goods_produced for a in agents)
        total_trust = sum(a.trust_score for a in agents)

        # justice provider metrics
        jp_trusts = [a.trust_score for a in agents if a.is_justice_provider]
        max_jp_trust = max(jp_trusts) if jp_trusts else 0.0
        jp_gini = calculate_gini([a for a in agents if a.is_justice_provider]) if len(jp_trusts) > 1 else 0.0

        state = EconomyState(
            step=step,
            total_money_supply=total_supply,
            total_goods_produced=total_goods,
            price_level=total_supply / max(total_goods, 0.01),
            trust_iou_ratio=total_trust / max(total_supply, 0.01),
            gini=calculate_gini(agents),
            agent_count=len(agents),
            justice_income=justice_income,
            fraud_events=step_fraud,
            prosecutions=step_prosecutions,
            justice_provider_count=len(jp_trusts),
            max_justice_trust=max_jp_trust,
            justice_gini=jp_gini
        )
        history.append(state)

    return history


def print_results(history: List[EconomyState], label: str):
    """Print summary of simulation results."""
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")

    checkpoints = [0, len(history)//4, len(history)//2, 3*len(history)//4, len(history)-1]

    print(f"\n{'Step':>6} {'Agents':>7} {'Supply':>10} {'Goods':>10} {'Price':>8} "
          f"{'Trust/IOU':>10} {'Gini':>6} {'Fraud':>6} {'Prosec':>7}")
    print(f"{'-'*6} {'-'*7} {'-'*10} {'-'*10} {'-'*8} {'-'*10} {'-'*6} {'-'*6} {'-'*7}")

    for i in checkpoints:
        s = history[i]
        print(f"{s.step:>6} {s.agent_count:>7} {s.total_money_supply:>10.1f} "
              f"{s.total_goods_produced:>10.1f} {s.price_level:>8.3f} "
              f"{s.trust_iou_ratio:>10.4f} {s.gini:>6.3f} "
              f"{s.fraud_events:>6} {s.prosecutions:>7}")

    # inflation analysis
    early = history[len(history)//10]
    late = history[-1]
    if early.price_level > 0:
        inflation_rate = ((late.price_level / early.price_level) - 1) * 100
    else:
        inflation_rate = 0

    print(f"\n  Total inflation (step {early.step} -> {late.step}): {inflation_rate:+.1f}%")
    print(f"  Final agents: {late.agent_count}")
    print(f"  Final money supply: {late.total_money_supply:.1f}")
    print(f"  Final goods produced: {late.total_goods_produced:.1f}")
    print(f"  Final Gini coefficient: {late.gini:.3f}")

    if late.trust_iou_ratio > 0.5:
        print(f"  Trust/IOU health: HEALTHY ({late.trust_iou_ratio:.3f})")
    elif late.trust_iou_ratio > 0.2:
        print(f"  Trust/IOU health: MODERATE ({late.trust_iou_ratio:.3f})")
    else:
        print(f"  Trust/IOU health: WARNING ({late.trust_iou_ratio:.3f})")


def compare_scenarios(scenarios: List[Tuple[str, List[EconomyState]]]):
    """Print comparison table across multiple scenarios."""
    print(f"\n{'='*80}")
    print(f"  COMPARISON ACROSS ALL SCENARIOS")
    print(f"{'='*80}")

    header = f"  {'Scenario':<45} {'Price':>7} {'Gini':>7} {'T/IOU':>7} {'Fraud':>7}"
    print(header)
    print(f"  {'-'*45} {'-'*7} {'-'*7} {'-'*7} {'-'*7}")

    for label, history in scenarios:
        final = history[-1]
        total_fraud = sum(s.fraud_events for s in history)
        short_label = label[:45]
        print(f"  {short_label:<45} {final.price_level:>7.3f} {final.gini:>7.3f} "
              f"{final.trust_iou_ratio:>7.3f} {total_fraud:>7}")

    # analysis
    baseline = scenarios[0][1][-1]
    print(f"\n  Analysis vs baseline ({scenarios[0][0]}):")
    for label, history in scenarios[1:]:
        final = history[-1]
        price_delta = ((final.price_level / max(baseline.price_level, 0.001)) - 1) * 100
        gini_delta = final.gini - baseline.gini
        print(f"  {label}:")
        print(f"    Inflation: {price_delta:+.1f}%  |  Gini: {gini_delta:+.3f}  |  "
              f"Trust/IOU: {final.trust_iou_ratio:.3f}")


def main():
    parser = argparse.ArgumentParser(description="Trust-Backed Economy Simulator")
    parser.add_argument("--steps", type=int, default=200, help="Simulation timesteps")
    parser.add_argument("--initial-agents", type=int, default=10, help="Starting agents")
    parser.add_argument("--trades-per-step", type=int, default=5, help="Trades per timestep")
    parser.add_argument("--growth-rate", type=int, default=1, help="New agents per step")
    parser.add_argument("--justice-providers", type=int, default=0, help="Number of justice providers (0=none)")
    parser.add_argument("--diminishing-returns", action="store_true", help="Enable diminishing trust returns")
    parser.add_argument("--reputation-only", action="store_true", help="Reputation-as-payment (no direct IOU income)")
    parser.add_argument("--trust-cap", action="store_true", help="Cap prosecution trust accumulation")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--compare", action="store_true", help="Run single vs none")
    parser.add_argument("--compare-all", action="store_true", help="Run all 4 scenarios")
    parser.add_argument("--fraud-rate", type=float, default=0.05, help="Fraud probability per trade (default 0.05)")
    parser.add_argument("--stress", action="store_true", help="Stress test (500 steps, 20 agents, +2/step)")
    args = parser.parse_args()

    base_kwargs = dict(
        initial_agents=args.initial_agents,
        steps=args.steps,
        trades_per_step=args.trades_per_step,
        growth_rate=args.growth_rate,
        seed=args.seed
    )

    global FRAUD_PROBABILITY
    FRAUD_PROBABILITY = args.fraud_rate

    if args.stress:
        base_kwargs.update(initial_agents=20, steps=500, growth_rate=2)

    if args.compare_all:
        scenarios = []

        # A: No justice
        h = run_simulation(**base_kwargs, num_justice_providers=0)
        scenarios.append(("A: No justice (baseline)", h))
        print_results(h, "A: No justice (baseline)")

        # B: Single provider (monopoly)
        h = run_simulation(**base_kwargs, num_justice_providers=1)
        scenarios.append(("B: Single provider (monopoly)", h))
        print_results(h, "B: Single provider (monopoly)")

        # C: 3 competing providers
        h = run_simulation(**base_kwargs, num_justice_providers=3)
        scenarios.append(("C: 3 competing providers", h))
        print_results(h, "C: 3 competing providers")

        # D: 3 providers + diminishing returns
        h = run_simulation(**base_kwargs, num_justice_providers=3, use_diminishing=True)
        scenarios.append(("D: 3 providers + diminishing returns", h))
        print_results(h, "D: 3 providers + diminishing returns")

        # E: 3 providers + diminishing + reputation-only
        h = run_simulation(**base_kwargs, num_justice_providers=3,
                          use_diminishing=True, reputation_only=True)
        scenarios.append(("E: 3 providers + diminishing + reputation-only", h))
        print_results(h, "E: 3 providers + diminishing + reputation-only")

        # F: 3 providers + diminishing + reputation-only + trust cap
        h = run_simulation(**base_kwargs, num_justice_providers=3,
                          use_diminishing=True, reputation_only=True,
                          use_trust_cap=True)
        scenarios.append(("F: 3 providers + dim + rep-only + trust cap", h))
        print_results(h, "F: 3 providers + dim + rep-only + trust cap")

        compare_scenarios(scenarios)

    elif args.compare:
        h_none = run_simulation(**base_kwargs, num_justice_providers=0)
        print_results(h_none, "SCENARIO A: No Justice Provider (baseline)")

        h_single = run_simulation(**base_kwargs, num_justice_providers=1)
        print_results(h_single, "SCENARIO B: Single Justice Provider")

        compare_scenarios([
            ("A: No justice", h_none),
            ("B: Single provider", h_single)
        ])
    else:
        num_jp = args.justice_providers
        history = run_simulation(
            **base_kwargs,
            num_justice_providers=num_jp,
            use_diminishing=args.diminishing_returns,
            reputation_only=args.reputation_only
        )
        parts = []
        if num_jp > 0:
            parts.append(f"{num_jp} justice provider(s)")
        if args.diminishing_returns:
            parts.append("diminishing returns")
        if args.reputation_only:
            parts.append("reputation-only")
        label = " + ".join(parts) if parts else "Baseline (no justice)"
        print_results(history, label)


if __name__ == "__main__":
    main()
