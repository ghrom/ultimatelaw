#!/usr/bin/env python3
"""The Forfeiture cluster as executable rules: a Logical-English-shaped encoding.

Rules are controlled-English sentences with capitalized variables, parsed by
template into Horn clauses. Events are evaluated in temporal order (e1, e2, ...)
because the doctrine is temporal: whether an act is sanctioned depends on the
forfeitures that PRIOR acts created, never on later ones. Within a step the
strata run in doctrine order: what the act is -> whether it is sanctioned ->
verdicts -> what it forfeits -> what it closes. A final pass derives what
remains open, unlawful closures, and responsibility.

"Only Justice closes it" is itself encoded: a closed debt with no justice
ground derives an unlawful-closure atom, which is an integrity violation.

Selftest discipline: the run FAILS unless
  1. every expected consequence is derived (thief ceiling, escalation, phases,
     outlaw, closure, never-real forfeiture, responsibility),
  2. the clean rulebook produces ZERO integrity violations, and
  3. a planted axiom (the day-one Restitution bug: "restitution by itself
     closes the moral debt") produces a flagged contradiction.

Usage: python tools/le_forfeiture.py     Exit 0 = all three hold.
"""
import re
import sys

# ------------------------------------------------------------- the rulebook
# 'IF' separates head from conditions, 'AND' separates conditions, 'NOT '
# prefixes negation-as-failure. STEP_STRATA run per event step, in order;
# FINAL_STRATA run once after the last step.

STEP_STRATA = [
    # 1. what the act is, and what its harm reaches
    [
        "the harm of {E} reaches kind {K} IF {E} is an act of {A} crossing the {K} boundary of {V}",
        "{E} is a hostile crossing of {V} by {A} in kind {K} IF {E} is an act of {A} crossing the {K} boundary of {V} AND NOT {V} consented to {E}",
    ],
    # 2. whether the act is sanctioned (judged against PRIOR forfeitures)
    [
        "{F} is covered by a forfeiture IF {F} is an act of {X} crossing the {K} boundary of {Y} AND {Y} forfeits kind {K} to {X} after {E} AND {F} is later than {E} AND NOT the forfeiture of {Y} to {X} has ended",
        "{F} is covered by a forfeiture IF {F} is an act of {X} crossing the {K} boundary of {Y} AND {Y} forfeits kind {K} to {V} after {E} AND {F} is later than {E} AND NOT the forfeiture of {Y} to {V} has ended AND {X} holds a mandate from {V}",
        "{F} is sanctioned IF {F} is covered by a forfeiture",
        "{F} is sanctioned IF {F} halts an ongoing crossing with minimal force",
        "{F} is sanctioned IF {F} is an act of {X} crossing the {K} boundary of {Y} AND {Y} is an outlaw",
    ],
    # 3. verdicts on the act
    [
        "{E} creates no victim IF {E} is a hostile crossing of {V} by {A} in kind {K} AND {E} is sanctioned",
        "{E} is a crime by {A} with victim {V} IF {E} is a hostile crossing of {V} by {A} in kind {K} AND NOT {E} is sanctioned",
        "the moral debt of {A} to {V} from {E} is created IF {E} is a crime by {A} with victim {V}",
        "{E} is murder by {A} of {V} IF {E} is a crime by {A} with victim {V} AND {E} is an act of {A} crossing the life boundary of {V}",
        "{A} is an outlaw IF {E} is murder by {A} of {V}",
    ],
    # 4. what an unsanctioned crossing forfeits: every kind the harm reached
    [
        "{A} forfeits kind {K2} to {V} after {E} IF {E} is a hostile crossing of {V} by {A} in kind {K} AND NOT {E} is sanctioned AND the harm of {E} reaches kind {K2}",
    ],
    # 5. justice and repair
    [
        "the moral debt of {A} to {V} from {E} is closed by justice IF {J} is a collection by {X} on the debt from {E} AND {J} is sanctioned AND the moral debt of {A} to {V} from {E} is created AND NOT {A} is an outlaw",
        "the moral debt of {A} to {V} from {E} is closed by justice IF {V} releases the debt from {E} AND the moral debt of {A} to {V} from {E} is created AND NOT {A} is an outlaw",
        "the moral debt of {A} to {V} from {E} is closed IF the moral debt of {A} to {V} from {E} is closed by justice",
        "the forfeiture of {A} to {V} has ended IF the moral debt of {A} to {V} from {E} is closed",
        "the damage of {E} is repaired IF {R} is a payment of restitution by {A} to {V} for {E}",
    ],
]

FINAL_STRATA = [
    [
        "the moral debt of {A} to {V} from {E} remains open IF the moral debt of {A} to {V} from {E} is created AND NOT the moral debt of {A} to {V} from {E} is closed",
        "the closure of the debt of {A} to {V} from {E} is not lawful IF the moral debt of {A} to {V} from {E} is closed AND NOT the moral debt of {A} to {V} from {E} is closed by justice",
        "{D} is responsible for {F} IF {F} is a crime by {X} with victim {Y} AND {F} was procured by the fraud of {D}",
        "{X} is responsible for {F} IF {F} is a crime by {X} with victim {Y} AND NOT {F} was procured by the fraud of {D}",
    ],
]

# The planted axiom: the day-one Restitution bug, stated as doctrine.
PLANTED = ("the moral debt of {A} to {V} from {E} is closed IF "
           "{R} is a payment of restitution by {A} to {V} for {E} AND "
           "the moral debt of {A} to {V} from {E} is created")

# Integrity: pairs that can never both hold; atoms that may never exist.
CONSTRAINT_PAIRS = [
    ("{E} creates no victim", "{E} is a crime by {A} with victim {V}"),
    ("the moral debt of {A} to {V} from {E} is closed",
     "the moral debt of {A} to {V} from {E} remains open"),
]
CONSTRAINT_NEVER = [
    "the closure of the debt of {A} to {V} from {E} is not lawful",
]

# ---------------------------------------------------------------- the engine
VAR = re.compile(r'\{([A-Z][A-Za-z0-9]*)\}')


def parse_rule(text):
    head, _, body = text.partition(' IF ')
    conds = []
    for c in body.split(' AND '):
        c = c.strip()
        neg = c.startswith('NOT ')
        conds.append((neg, c[4:] if neg else c))
    return head.strip(), conds


def substitute(template, binding):
    return VAR.sub(lambda m: binding.get(m.group(1), '{' + m.group(1) + '}'), template)


def to_regex(template):
    out, last = [], 0
    for m in VAR.finditer(template):
        out.append(re.escape(template[last:m.start()]))
        out.append('(?P<%s>[a-z0-9_]+)' % m.group(1))
        last = m.end()
    out.append(re.escape(template[last:]))
    return re.compile('^' + ''.join(out) + '$')


def match_cond(cond, binding, facts):
    grounded = substitute(cond, binding)
    if '{' not in grounded:
        if grounded in facts:
            yield binding
        return
    rx = to_regex(grounded)
    for f in facts:
        m = rx.match(f)
        if m:
            groups = m.groupdict()
            if all(binding.get(k, groups[k]) == groups[k] for k in groups):
                yield {**binding, **groups}


def apply_rule(head, conds, facts):
    new = set()
    bindings = [{}]
    for neg, cond in conds:
        if neg:
            continue
        bindings = [b2 for b in bindings for b2 in match_cond(cond, b, facts)]
        if not bindings:
            return new
    for b in bindings:
        ok = True
        for neg, cond in conds:
            if not neg:
                continue
            grounded = substitute(cond, b)
            if '{' in grounded:
                rx = to_regex(grounded)
                if any(rx.match(f) for f in facts):
                    ok = False
            elif grounded in facts:
                ok = False
        if ok:
            h = substitute(head, b)
            if '{' not in h and h not in facts:
                new.add(h)
    return new


def run_strata(facts, strata):
    for stratum in strata:
        rules = [parse_rule(r) for r in stratum]
        while True:
            new = set()
            for head, conds in rules:
                new |= apply_rule(head, conds, facts) - facts
            if not new:
                break
            facts |= new
    return facts


def step_of(fact):
    ids = [int(n) for n in re.findall(r'\be(\d+)\b', fact)]
    return max(ids) if ids else 0


def run(scenario, step_strata, final_strata):
    facts = set()
    for k in sorted({step_of(f) for f in scenario}):
        facts |= {f for f in scenario if step_of(f) <= k}
        run_strata(facts, step_strata)
    run_strata(facts, final_strata)
    return facts


def violations(facts):
    out = []
    for a, b in CONSTRAINT_PAIRS:
        rx = to_regex(a)
        for f in facts:
            m = rx.match(f)
            if m:
                other = substitute(b, m.groupdict())
                if '{' in other:
                    rxb = to_regex(other)
                    out += [(f, g) for g in facts if rxb.match(g)]
                elif other in facts:
                    out.append((f, other))
    for never in CONSTRAINT_NEVER:
        rx = to_regex(never)
        out += [(f, '(this atom may never exist)') for f in facts if rx.match(f)]
    return out


# ---------------------------------------------------------------- scenarios
SCENARIO = [
    # S1+S2: alice steals bob's gold; bob collects everything alice owns;
    # a vigilante then kills alice over the pure property theft.
    "e1 is an act of alice crossing the property boundary of bob",
    "e2 is an act of bob crossing the property boundary of alice",
    "e2 is later than e1",
    "e2 is a collection by bob on the debt from e1",
    "e3 is an act of vigilante crossing the life boundary of alice",
    "e3 is later than e1",

    # S3: an ongoing attack halted by a bystander with minimal force.
    "e4 is an act of attacker crossing the body boundary of walker",
    "e5 is an act of bystander crossing the body boundary of attacker",
    "e5 halts an ongoing crossing with minimal force",
    "e5 is later than e4",

    # S4: carol murders dan; dave ends carol the outlaw.
    "e6 is an act of carol crossing the life boundary of dan",
    "e7 is an act of dave crossing the life boundary of carol",
    "e7 is later than e6",

    # S5: a punisher ends frank on a forfeiture that was never real,
    # procured by a deceiver's fraud.
    "e8 is an act of punisher crossing the life boundary of frank",
    "e8 was procured by the fraud of deceiver",

    # S7: eve's theft runs deep enough to cost lives; the victim's proxy
    # reaches eve's life under the mandate.
    "e9 is an act of eve crossing the property boundary of grace",
    "the harm of e9 reaches kind life",
    "e10 is an act of proxy crossing the life boundary of eve",
    "e10 is later than e9",
    "proxy holds a mandate from grace",

    # S8: restitution paid on a separate theft, victim neither collects
    # nor releases -- the debt must remain open.
    "e11 is an act of henry crossing the property boundary of iris",
    "r1 is a payment of restitution by henry to iris for e11",
]

EXPECTED = [
    ("thief ceiling: collecting everything the thief owns is no crime",
     "e2 creates no victim"),
    ("thief's own theft is a crime with a victim",
     "e1 is a crime by alice with victim bob"),
    ("sanctioned collection closes the moral debt by justice",
     "the moral debt of alice to bob from e1 is closed by justice"),
    ("killing a pure property thief is a new crime",
     "e3 is a crime by vigilante with victim alice"),
    ("the escalator's act is murder",
     "e3 is murder by vigilante of alice"),
    ("the escalator becomes an outlaw",
     "vigilante is an outlaw"),
    ("minimal halting force is sanctioned for anyone",
     "e5 creates no victim"),
    ("the murderer is an outlaw",
     "carol is an outlaw"),
    ("ending an outlaw creates no victim",
     "e7 creates no victim"),
    ("ending a non-outlaw on a never-real forfeiture is a crime",
     "e8 is a crime by punisher with victim frank"),
    ("responsibility falls on the deceiver who procured it",
     "deceiver is responsible for e8"),
    ("a theft that cost lives reaches the body: death is within the ceiling",
     "e10 creates no victim"),
    ("restitution repairs the damage",
     "the damage of e11 is repaired"),
    ("restitution by itself does not close the moral debt",
     "the moral debt of henry to iris from e11 remains open"),
    ("the murderer's debt stays open forever",
     "the moral debt of carol to dan from e6 remains open"),
]


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

    n_rules = sum(len(s) for s in STEP_STRATA) + sum(len(s) for s in FINAL_STRATA)
    print('[le] rulebook: %d rules, %d scenario facts, events evaluated in order'
          % (n_rules, len(SCENARIO)))

    facts = run(SCENARIO, STEP_STRATA, FINAL_STRATA)
    print('[le] derived %d facts from %d' % (len(facts) - len(SCENARIO), len(SCENARIO)))

    fails = 0
    print('\n[1] expected consequences (derived, not asserted):')
    for label, atom in EXPECTED:
        ok = atom in facts
        fails += 0 if ok else 1
        print('  %s  %s' % ('PASS' if ok else 'FAIL', label))
        if not ok:
            print('        missing: %s' % atom)

    print('\n[2] integrity of the clean rulebook:')
    v = violations(facts)
    for a, b in v:
        print('  CONTRADICTION: %r vs %r' % (a, b))
    clean_ok = not v
    print('  %s  zero contradictions expected' % ('PASS' if clean_ok else 'FAIL'))

    print('\n[3] planted axiom (day-one Restitution bug: restitution alone closes the debt):')
    planted = [list(s) for s in STEP_STRATA]
    planted[4] = planted[4] + [PLANTED]
    fplanted = run(SCENARIO, planted, FINAL_STRATA)
    vp = violations(fplanted)
    for a, b in vp[:4]:
        print('  caught: %r vs %r' % (a, b))
    planted_ok = bool(vp)
    print('  %s  the contradiction must be flagged' % ('PASS' if planted_ok else 'FAIL'))

    ok = fails == 0 and clean_ok and planted_ok
    print('\n=> %s' % ('ALL PASS -- the cluster is formally coherent and the '
                       'engine can prove incoherence' if ok else 'FAILURES PRESENT'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
