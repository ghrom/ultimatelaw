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

Tracks:
- Total money supply (sum of all IOUs in circulation)
- Price level (money supply / total goods produced)
- Trust/IOU ratio (system health indicator)
- Gini coefficient (wealth inequality)
- Justice provider income (prosecution service revenue)

Usage:
    python economy-sim.py
    python economy-sim.py --steps 500 --initial-agents 10
    python economy-sim.py --justice-provider    # enable prosecution economy
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


TRUST_MULTIPLIER = 10.0       # 1 trust point = 10 IOUs issuance capacity
TRUST_PER_TRADE = 0.1         # trust earned per honest transaction
TRUST_DECAY_DEFAULT = 0.5     # trust lost per default
FRAUD_PROBABILITY = 0.05      # 5% chance any trade is fraudulent
JUSTICE_DETECTION_RATE = 0.7  # justice provider catches 70% of fraud
JUSTICE_REWARD = 0.2          # trust reward for successful prosecution
PRODUCTIVE_CAPACITY = 1.0     # each agent produces ~1 unit of goods per trade


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


def simulate_trade(buyer: Agent, seller: Agent, has_justice: bool) -> Tuple[bool, bool, bool]:
    """
    Simulate a bilateral trade. Returns (success, was_fraud, was_prosecuted).

    Buyer pays IOUs, seller delivers goods.
    Fraud = seller takes payment but doesn't deliver.
    """
    # buyer needs IOUs to pay — either from balance or by issuing new ones
    trade_price = PRODUCTIVE_CAPACITY  # 1 unit of goods = 1 IOU (initially)

    # can buyer afford it?
    if buyer.balance >= trade_price:
        # pay from existing balance
        pass
    elif buyer.ious_issued + trade_price <= buyer.iou_capacity:
        # issue new IOUs
        buyer.ious_issued += trade_price
    else:
        # can't afford, no trade
        return False, False, False

    # check for fraud (seller doesn't deliver)
    is_fraud = random.random() < FRAUD_PROBABILITY

    if is_fraud:
        # seller takes payment, doesn't deliver
        buyer.balance -= trade_price
        seller.balance += trade_price
        seller.defaults += 1
        seller.trust_score = max(0, seller.trust_score - TRUST_DECAY_DEFAULT)
        seller.iou_capacity = seller.trust_score * TRUST_MULTIPLIER

        # justice provider may catch it
        was_prosecuted = False
        if has_justice and random.random() < JUSTICE_DETECTION_RATE:
            was_prosecuted = True
            # prosecution: seller loses additional trust, victim partially restored
            seller.trust_score = max(0, seller.trust_score - TRUST_DECAY_DEFAULT)
            seller.iou_capacity = seller.trust_score * TRUST_MULTIPLIER
            # partial restoration to buyer
            restore = trade_price * 0.5
            buyer.balance += restore
            seller.balance -= min(restore, seller.balance)

        return True, True, was_prosecuted
    else:
        # honest trade
        buyer.balance -= trade_price
        seller.balance += trade_price
        seller.goods_produced += PRODUCTIVE_CAPACITY

        # both gain trust
        buyer.trust_score += TRUST_PER_TRADE * 0.5   # buyer trusted seller
        seller.trust_score += TRUST_PER_TRADE         # seller delivered
        buyer.iou_capacity = buyer.trust_score * TRUST_MULTIPLIER
        seller.iou_capacity = seller.trust_score * TRUST_MULTIPLIER

        buyer.transactions += 1
        seller.transactions += 1

        return True, False, False


def run_simulation(
    initial_agents: int = 10,
    steps: int = 200,
    trades_per_step: int = 5,
    enable_justice: bool = False,
    growth_rate: int = 1,  # new agents per step
    seed: int = 42
) -> List[EconomyState]:
    """Run the full simulation."""
    random.seed(seed)

    agents: List[Agent] = []
    for i in range(initial_agents):
        a = Agent(id=i, trust_score=1.0, joined_at=0)  # founding members start with some trust
        a.iou_capacity = a.trust_score * TRUST_MULTIPLIER
        a.balance = 5.0  # initial endowment
        agents.append(a)

    # optionally add a justice provider
    if enable_justice:
        jp = agents[0]
        jp.is_justice_provider = True
        jp.trust_score = 2.0  # justice provider starts with higher trust (reputation)
        jp.iou_capacity = jp.trust_score * TRUST_MULTIPLIER

    history: List[EconomyState] = []

    for step in range(steps):
        # add new agents
        for _ in range(growth_rate):
            new_id = len(agents)
            new_agent = Agent(id=new_id, trust_score=0.0, joined_at=step)
            new_agent.iou_capacity = 0.0
            new_agent.balance = 0.0  # new agents start with nothing
            agents.append(new_agent)

        step_fraud = 0
        step_prosecutions = 0
        justice_income = 0.0

        # run trades
        eligible = [a for a in agents if a.trust_score > 0 or a.balance > 0]
        for _ in range(min(trades_per_step, len(eligible) // 2)):
            if len(eligible) < 2:
                break
            buyer, seller = random.sample(eligible, 2)

            success, was_fraud, was_prosecuted = simulate_trade(
                buyer, seller, enable_justice
            )

            if was_fraud:
                step_fraud += 1
            if was_prosecuted:
                step_prosecutions += 1
                # justice provider earns trust and income
                if enable_justice:
                    for a in agents:
                        if a.is_justice_provider:
                            a.trust_score += JUSTICE_REWARD
                            a.iou_capacity = a.trust_score * TRUST_MULTIPLIER
                            justice_income += JUSTICE_REWARD * TRUST_MULTIPLIER
                            break

        # record state
        total_supply = sum(a.ious_issued for a in agents)
        total_goods = sum(a.goods_produced for a in agents)
        total_trust = sum(a.trust_score for a in agents)

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
            prosecutions=step_prosecutions
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


def main():
    parser = argparse.ArgumentParser(description="Trust-Backed Economy Simulator")
    parser.add_argument("--steps", type=int, default=200, help="Simulation timesteps")
    parser.add_argument("--initial-agents", type=int, default=10, help="Starting agents")
    parser.add_argument("--trades-per-step", type=int, default=5, help="Trades per timestep")
    parser.add_argument("--growth-rate", type=int, default=1, help="New agents per step")
    parser.add_argument("--justice-provider", action="store_true", help="Enable justice provider")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--compare", action="store_true", help="Run with and without justice")
    args = parser.parse_args()

    if args.compare:
        # run both scenarios
        h_no_justice = run_simulation(
            initial_agents=args.initial_agents,
            steps=args.steps,
            trades_per_step=args.trades_per_step,
            enable_justice=False,
            growth_rate=args.growth_rate,
            seed=args.seed
        )
        print_results(h_no_justice, "SCENARIO A: No Justice Provider (baseline)")

        h_with_justice = run_simulation(
            initial_agents=args.initial_agents,
            steps=args.steps,
            trades_per_step=args.trades_per_step,
            enable_justice=True,
            growth_rate=args.growth_rate,
            seed=args.seed
        )
        print_results(h_with_justice, "SCENARIO B: With Justice Provider")

        # comparison
        a_final = h_no_justice[-1]
        b_final = h_with_justice[-1]

        print(f"\n{'='*60}")
        print(f"  COMPARISON")
        print(f"{'='*60}")
        print(f"  Price level:  {a_final.price_level:.3f} (no justice) vs {b_final.price_level:.3f} (with justice)")
        print(f"  Gini:         {a_final.gini:.3f} (no justice) vs {b_final.gini:.3f} (with justice)")
        print(f"  Trust/IOU:    {a_final.trust_iou_ratio:.4f} (no justice) vs {b_final.trust_iou_ratio:.4f} (with justice)")
        print(f"  Total fraud:  {sum(s.fraud_events for s in h_no_justice)} vs {sum(s.fraud_events for s in h_with_justice)}")

        if b_final.price_level < a_final.price_level:
            print(f"\n  >> Justice provider REDUCES inflation")
        else:
            print(f"\n  >> Justice provider does NOT reduce inflation")

        if b_final.gini < a_final.gini:
            print(f"  >> Justice provider REDUCES inequality")
        else:
            print(f"  >> Justice provider does NOT reduce inequality")
    else:
        history = run_simulation(
            initial_agents=args.initial_agents,
            steps=args.steps,
            trades_per_step=args.trades_per_step,
            enable_justice=args.justice_provider,
            growth_rate=args.growth_rate,
            seed=args.seed
        )
        label = "With Justice Provider" if args.justice_provider else "Baseline (no justice)"
        print_results(history, label)


if __name__ == "__main__":
    main()
