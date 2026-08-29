#!/usr/bin/env python3
"""Mechanical Logic: formal mechanics for the Mechanical rendering.

The principles implemented, in the dictionary's own spirit:
  1. A declared RELATION inventory -- each relation has one surface form and
     one meaning, exactly as each word has one meaning.
  2. A small fixed sentence grammar: facts, "If ..., and ..., then ..." rules,
     and "It is at no time true that ..." integrity constraints.
  3. Deterministic reference: "an agent" introduces a new one, "the agent"
     means the most recent one, "the second agent" pins by order. The parser
     prints its resolved reading back, so the author sees what the machine saw.
  4. Every conforming sentence compiles to logic and runs on the same engine
     that already proved the Forfeiture cluster (le_forfeiture.py).
  5. Every content word must reconcile against the Mechanical vocabulary --
     the same reconciliation the rendering itself is gated by.

Usage:  python tools/mech_logic.py
Reads   dictionary/coherent-dictionary-logic.txt (the doctrine) and
tools/mech-logic-cases.txt (scenario, expectations, absences, planted
axioms) and exits 0 only if: everything parses with a unique reading, the
vocabulary check passes (when the local hook is present), all expectations
derive, all absences hold, the clean rulebook has zero violations, and the
planted axioms are caught.
"""
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import le_forfeiture as ENGINE                               # noqa: E402
from dict_parse import parse as parse_dictionary, CANON, LOGIC  # noqa: E402

# The vocabulary check needs local tooling that is never committed. The hook
# module lives outside the repo; without it the check is skipped and the
# parse/compile/derive/integrity core still runs on any clone.
VOCAB_DIR = os.environ.get('MECH_VOCAB_DIR') or os.path.expanduser('~/tmp')
sys.path.insert(0, VOCAB_DIR)
try:
    from mech_vocab_local import (APPROVED, DECLARED, IRREG_OK,  # noqa: E402
                                  TERM_FAMILY, tokens as vocab_tokens,
                                  _stem_candidates)
    HAVE_VOCAB = True
except Exception:
    HAVE_VOCAB = False

RULES_FILE = LOGIC
CASES_FILE = HERE / 'mech-logic-cases.txt'

# ------------------------------------------------------------- the relations
# One surface, one meaning. {Name:type} slots take a noun phrase of that type.
TYPES = ('agent', 'act', 'kind', 'restitution', 'transfer', 'thing')

RELATIONS = [
    "{A:act} is an act of {X:agent} crossing {K:kind} boundary of {Y:agent}",
    "{V:agent} consented to {E:act}",
    "{V:agent} gives permission for {E:act}",
    "{V:agent} takes back the permission for {E:act} at {W:act}",
    "the permission for {E:act} has ended",
    "the conduct of {V:agent} shows the intention of consent to {E:act}",
    "the words of {V:agent} show consent to {E:act}",
    "{V:agent} accepts the terms of {E:act} in an agreement",
    "{D:agent} deceived {V:agent} about {E:act}",
    "duress caused the consent of {V:agent} to {E:act}",
    "the circumstances fix the meaning of {E:act} as consent by {V:agent}",
    "the consent of {V:agent} to {E:act} stands outside words and conduct",
    "{T:transfer} is a conditional transfer from {A:agent} to {V:agent}",
    "the condition of {T:transfer} occurs at {W:act}",
    "{A:agent} holds the value of {T:transfer}",
    "{A:agent} refuses to give the value of {T:transfer} at {E:act}",
    "the value of {T:transfer} is the property of {V:agent}",
    "{C:transfer} is the stated thing of {T:transfer} that moves on failure",
    "{E:act} is the failure of {T:transfer} from {A:agent}",
    "{E:act} is the trade of {T:transfer} by {A:agent} to {V:agent}",
    "{A:agent} had no intention to give the value of {T:transfer}",
    "{A:agent} hides the facts that made {T:transfer} not possible",
    "{E:act} is a promise by {A:agent} to {V:agent}",
    "{J:act} is a judgment that {A:agent} caused the harm of {E:act} to {V:agent}",
    "{X:agent} disproves the facts of {J:act}",
    "the authority of {J:act} has ended",
    "the moral debt of {A:agent} to {V:agent} from {E:act} stands outside causation",
    "{G:thing} is a scarce thing",
    "{A:agent} takes {G:thing} into first use at {E:act}",
    "{A:agent} gives {G:thing} to {V:agent} at {E:act}",
    "{G:thing} is the property of {A:agent}",
    "{A:agent} makes {G:thing} at {E:act}",
    "the ownership of {G:thing} stands outside first use and transfer",
    "{E:act} is Theft by {A:agent} from {V:agent}",
    "{T:transfer} is commanded by authority on {A:agent} for {V:agent}",
    "the ownership of the value of {T:transfer} stands outside consent",
    "{A:agent} lies to {V:agent} in {E:act}",
    "{E:act} is Fraud by {A:agent} on {V:agent}",
    "{X:agent} is part of the group of {A:agent}",
    "the harm of {E:act} reaches {K:kind}",
    "{E:act} is a hostile crossing of {V:agent} by {A:agent} in {K:kind}",
    "{E:act} stands in a Forfeiture",
    "{F:act} stops a crossing that continues with the minimum force",
    "{A:agent} forfeits {K:kind} to {V:agent} after {E:act}",
    "the forfeiture of {A:agent} to {V:agent} has ended",
    "{F:act} is later than {E:act}",
    "{X:agent} holds a mandate from {V:agent}",
    "{E:act} makes no victim",
    "{E:act} is a crime by {A:agent} with victim {V:agent}",
    "the moral debt of {A:agent} to {V:agent} from {E:act} exists",
    "{E:act} is murder by {A:agent} of {V:agent}",
    "{A:agent} is an outlaw",
    "{E:act} is revenge by {A:agent} on {V:agent}",
    "{A:agent} intended {E:act}",
    "{D:agent} threatens {V:agent} about {E:act}",
    "{D:agent} threatens {K:kind} boundary of {V:agent} at {E:act}",
    "{D:agent} forces {V:agent} in {E:act}",
    "the crime of {A:agent} in {E:act} stands outside the act",
    "{E:act} is commanded by a vote on {V:agent}",
    "{T:transfer} is commanded by a vote on {A:agent} for {V:agent}",
    "{G:thing} is the body of {A:agent}",
    "{G:thing} is a pattern",
    "the ownership of {G:thing} stands outside its agent",
    "{J:act} stands in Error",
    "{E:act} stands exempt by authority for {A:agent}",
    "{J:act} is a collection by {X:agent} on the debt from {E:act}",
    "{V:agent} releases the debt from {E:act}",
    "the moral debt of {A:agent} to {V:agent} from {E:act} is closed by justice",
    "the moral debt of {A:agent} to {V:agent} from {E:act} is closed",
    "{R:restitution} is a restitution by {A:agent} to {V:agent} for {E:act}",
    "the damage of {E:act} is repaired",
    "the moral debt of {A:agent} to {V:agent} from {E:act} remains open",
    "the debt of {A:agent} to {V:agent} from {E:act} is closed outside Justice",
    "{F:act} was caused by the fraud of {D:agent}",
    "{D:agent} is responsible for {F:act}",
]

SLOT = re.compile(r'\{([A-Z][A-Za-z0-9]*):([a-z]+)\}')
ORDINALS = ['first', 'second', 'third', 'fourth']


def np_pattern(typ):
    """The noun-phrase forms one slot accepts, as one regex alternation."""
    ords = '|'.join(ORDINALS)
    return ('(?:'
            f'(?P<<N>_fresh>an? (?:(?:{ords}) )?{typ}(?: of)?)'
            '|'
            f'(?P<<N>_ref>the (?:(?:{ords}) )?{typ}(?: of)?)'
            '|'
            f'(?P<<N>_const>(?:the )?[a-z][a-z0-9_]*)'
            ')')


class Reading:
    """Per-sentence variable state: deterministic reference resolution."""

    def __init__(self):
        self.vars = {t: [] for t in TYPES}   # introduction order per type
        self.n = 0

    def fresh(self, typ, ordinal=None):
        idx = len(self.vars[typ])
        if ordinal is not None and ordinal != idx:
            raise SyntaxError(
                f'"a {ORDINALS[ordinal]} {typ}" but {idx} {typ}(s) exist')
        self.n += 1
        name = 'V%d' % self.n
        self.vars[typ].append(name)
        return name

    def ref(self, typ, ordinal=None):
        if not self.vars[typ]:
            raise SyntaxError(f'"the {typ}" but no {typ} was introduced')
        if ordinal is None:
            return self.vars[typ][-1]
        if ordinal >= len(self.vars[typ]):
            raise SyntaxError(
                f'"the {ORDINALS[ordinal]} {typ}" but only '
                f'{len(self.vars[typ])} exist')
        return self.vars[typ][ordinal]


def relation_regexes():
    out = []
    for surface in RELATIONS:
        parts, last, slots = [], 0, []
        for i, m in enumerate(SLOT.finditer(surface)):
            parts.append(re.escape(surface[last:m.start()]))
            slots.append((m.group(1), m.group(2)))
            parts.append(np_pattern(m.group(2)).replace('<N>', 'S%d' % i))
            last = m.end()
        parts.append(re.escape(surface[last:]))
        out.append((surface, re.compile('^' + ''.join(parts) + '$'), slots))
    return out


REL_RX = relation_regexes()


def parse_np(text, typ, reading, mode):
    """Resolve one matched noun phrase to a variable or constant."""
    t = re.sub(r' of$', '', text.strip())
    if mode == 'const':
        t = re.sub(r'^the ', '', t)
        return t, t
    words = t.split()
    ordinal = None
    for i, o in enumerate(ORDINALS):
        if o in words:
            ordinal = i
    if mode == 'fresh':
        return '{%s}' % reading.fresh(typ, ordinal), t
    return '{%s}' % reading.ref(typ, ordinal), t


def parse_clause(text, reading):
    """Match one clause against the relation inventory; must be unique."""
    text = text.strip().rstrip('.')
    hits = []
    for surface, rx, slots in REL_RX:
        m = rx.match(text)
        if m:
            hits.append((surface, m, slots))
    if not hits:
        raise SyntaxError(f'no relation matches: "{text}"')
    if len(hits) > 1:
        raise SyntaxError(f'ambiguous ({len(hits)} relations): "{text}"')
    surface, m, slots = hits[0]
    atom = surface
    for i, (name, typ) in enumerate(slots):
        for mode in ('fresh', 'ref', 'const'):
            g = m.group(f'S{i}_{mode}')
            if g is not None:
                val, _ = parse_np(g, typ, reading, mode)
                break
        atom = SLOT.sub(lambda mm: val, atom, count=1)  # noqa: B023
    return atom


NEG = 'it is not true that '


def parse_sentence(line):
    """One ML sentence -> ('rule'|'fact'|'never', payload).
    Rules compile into the engine's 'HEAD IF C AND NOT C' string format."""
    s = line.strip()
    s = s[0].lower() + s[1:] if s[:3] in ('If ', 'It ') else s
    reading = Reading()
    if s.startswith('if '):
        body, _, head = s[3:].partition(', then ')
        if not head:
            raise SyntaxError(f'rule without ", then ": "{line}"')
        conds = []
        for c in re.split(r', and ', body):
            c = c.strip()
            if c.startswith(NEG):
                conds.append('NOT ' + parse_clause(c[len(NEG):], reading))
            else:
                conds.append(parse_clause(c, reading))
        h = parse_clause(head, reading)
        return 'rule', h + ' IF ' + ' AND '.join(conds)
    if s.startswith('it is at no time true that '):
        rest = s[len('it is at no time true that '):].rstrip('.')
        a, _, b = rest.partition(' while ')
        atoms = [parse_clause(a, reading)]
        if b:
            atoms.append(parse_clause(b, reading))
        return 'never', atoms
    return 'fact', parse_clause(s, reading)


# ------------------------------------------------------- vocabulary residue
def vocab_ok_fn():
    term_words = set()
    for e in parse_dictionary(CANON):
        for w in re.findall(r"[A-Za-z][A-Za-z\-]*", e['term']):
            term_words.add(w.lower())
            for c in _stem_candidates(w.lower()):
                term_words.add(c)

    def ok(w):
        lw = w.lower()
        cands = [lw] + _stem_candidates(lw)
        if lw in IRREG_OK:
            base = IRREG_OK[lw]
            return base in APPROVED or base in DECLARED or base in term_words
        return (any(c in APPROVED for c in cands)
                or lw in term_words or any(c in term_words for c in cands)
                or lw in DECLARED or any(c in DECLARED for c in cands)
                or lw in TERM_FAMILY
                or ('-' in w and all(ok(p) for p in w.split('-') if p)))
    return ok


def vocab_residue(text, extra_ok=()):
    ok = vocab_ok_fn()
    bad = {}
    for w in vocab_tokens(text):
        lw = w.lower()
        if lw in extra_ok:
            continue
        if re.fullmatch(r'e\d+|r\d+|v\d+', lw):
            continue                       # event / payment / variable names
        if not ok(w):
            bad.setdefault(lw, 0)
            bad[lw] += 1
    return bad


# ---------------------------------------------------------------- coverage
def coverage():
    """The ledger: every dictionary entry is either formalized (named in a
    '# From:' attribution), declared prose-only ('# Prose:' lines), or
    unaccounted. A term claimed both ways is a failure; a typo in a name
    simply leaves its term visibly unaccounted. Matching is exact term
    text (case-sensitive, word-bounded), so names with parentheses or
    slashes work."""
    raw = RULES_FILE.read_text(encoding='utf-8')
    known = {e['term'] for e in parse_dictionary(CANON)}

    def hits(line):
        # longest match wins: "Free Trade" does not also claim "Trade"
        spans = []
        for t in known:
            for m in re.finditer(
                    r'(?<![A-Za-z])' + re.escape(t) + r'(?![A-Za-z])', line):
                spans.append((m.start(), m.end(), t))
        out = set()
        for s, e, t in spans:
            if not any(s2 <= s and e <= e2 and (s2, e2) != (s, e)
                       for s2, e2, _ in spans):
                out.add(t)
        return out

    attributed, prose = set(), set()
    for m in re.finditer(r'^# From: ([^\n]+)', raw, re.M):
        attributed |= hits(m.group(1))
    for m in re.finditer(r'^# Prose: ([^\n]+)', raw, re.M):
        prose |= hits(m.group(1))
    return {
        'formalized': attributed - prose,
        'prose': prose - attributed,
        'conflict': attributed & prose,
        'unaccounted': known - attributed - prose,
        'total': len(known),
    }


# ---------------------------------------------------------------- the run
def load(path):
    lines = []
    for raw in path.read_text(encoding='utf-8').split('\n'):
        s = raw.strip()
        if not s or s.startswith('#'):
            continue
        lines.append(s)
    return lines


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

    # 1. parse the doctrine file: strata sections of rules + constraints
    strata, finals, nevers = [], [], []
    current = None
    planted_rules = []
    for line in load(RULES_FILE):
        low = line.lower()
        if low.startswith('stratum'):
            current = []
            strata.append(current)
            continue
        if low.startswith('final'):
            current = finals
            continue
        kind, payload = parse_sentence(line)
        if kind == 'rule':
            if current is None:
                raise SyntaxError('rule before any Stratum heading')
            current.append(payload)
        elif kind == 'never':
            nevers.append(payload)
        else:
            raise SyntaxError(f'facts do not belong in the rules file: {line}')

    # 2. parse the cases file: facts, expectations (present and absent),
    #    planted axiom
    scenario, expected, absent, section = [], [], [], None
    for line in load(CASES_FILE):
        low = line.lower()
        if low.startswith('scenario'):
            section = 'scenario'
            continue
        if low.startswith('expected'):
            section = 'expected'
            continue
        if low.startswith('absent'):
            section = 'absent'
            continue
        if low.startswith('planted'):
            section = 'planted'
            continue
        kind, payload = parse_sentence(line)
        if section == 'scenario':
            assert kind == 'fact', f'scenario lines must be facts: {line}'
            scenario.append(payload)
        elif section == 'expected':
            assert kind == 'fact', f'expected lines must be facts: {line}'
            expected.append((line, payload))
        elif section == 'absent':
            assert kind == 'fact', f'absent lines must be facts: {line}'
            absent.append((line, payload))
        elif section == 'planted':
            assert kind == 'rule', f'planted lines must be rules: {line}'
            planted_rules.append(payload)

    n_rules = sum(len(s) for s in strata) + len(finals)
    print(f'[ml] parsed: {n_rules} rules in {len(strata)} strata + final, '
          f'{len(nevers)} constraints, {len(scenario)} scenario facts, '
          f'{len(expected)} expectations, {len(planted_rules)} planted')

    # 3. echo three readings so the author can verify the mechanics
    print('\n[ml] sample compiled readings:')
    for src in load(RULES_FILE)[:40]:
        if src.lower().startswith('if '):
            print(f'  ML : {src}')
            print(f'  -> : {parse_sentence(src)[1]}')
            break

    # 4. vocabulary residue over the doctrine file (cases are test data:
    #    proper names there are exempt, like e1 itself)
    if HAVE_VOCAB:
        text = '\n'.join(
            l for l in RULES_FILE.read_text(encoding='utf-8').split('\n')
            if not l.strip().startswith('#')
            and not l.strip().lower().startswith(('stratum', 'final')))
        bad = vocab_residue(text)
        print(f'\n[ml] vocabulary residue: {len(bad)} distinct words')
        for w, n in sorted(bad.items()):
            print(f'   {w:<20} x{n}')
    else:
        bad = {}
        print('\n[ml] vocabulary check skipped (local vocabulary hook not found)')

    # 5. run: clean
    facts = ENGINE.run(scenario, strata, [finals])
    print(f'\n[ml] derived {len(facts) - len(scenario)} facts from {len(scenario)}')

    fails = 0
    print('\n[1] expectations (derived from the compiled doctrine):')
    for label, atom in expected:
        got = atom in facts
        fails += 0 if got else 1
        print(f'  {"PASS" if got else "FAIL"}  {label}')
    print('\n[1b] absences (what consent and its kin must PREVENT):')
    for label, atom in absent:
        got = atom not in facts
        fails += 0 if got else 1
        print(f'  {"PASS" if got else "FAIL"}  not derived: {label}')

    def violations(fs):
        out = []
        for atoms in nevers:
            if len(atoms) == 1:
                rx = ENGINE.to_regex(atoms[0])
                out += [(f, '(never)') for f in fs if rx.match(f)]
            else:
                rx = ENGINE.to_regex(atoms[0])
                for f in fs:
                    m = rx.match(f)
                    if m:
                        other = ENGINE.substitute(atoms[1], m.groupdict())
                        if '{' in other:
                            rxb = ENGINE.to_regex(other)
                            out += [(f, g) for g in fs if rxb.match(g)]
                        elif other in fs:
                            out.append((f, other))
        return out

    v = violations(facts)
    print('\n[2] integrity of the clean compiled rulebook:')
    for a, b in v:
        print(f'  CONTRADICTION: {a!r} vs {b!r}')
    clean_ok = not v
    print(f'  {"PASS" if clean_ok else "FAIL"}  zero contradictions expected')

    # 6. planted axiom
    strata_p = [list(s) for s in strata]
    strata_p[-1] = strata_p[-1] + planted_rules
    fp = ENGINE.run(scenario, strata_p, [finals])
    vp = violations(fp)
    print('\n[3] planted axiom (compiled from ML, not hand-written):')
    for a, b in vp[:3]:
        print(f'  caught: {a!r} vs {b!r}')
    planted_ok = bool(vp)
    print(f'  {"PASS" if planted_ok else "FAIL"}  the contradiction must be flagged')

    cov = coverage()
    print(f'\n[coverage] formalized {len(cov["formalized"])} / '
          f'prose-only {len(cov["prose"])} / '
          f'unaccounted {len(cov["unaccounted"])} of {cov["total"]} entries')
    cov_ok = not cov['conflict']
    if cov['conflict']:
        print(f'  FAIL  both formalized and prose-only: {sorted(cov["conflict"])}')
    if cov['unaccounted']:
        u = sorted(cov['unaccounted'])
        print(f'  not yet accounted: {", ".join(u[:12])}'
              + (f' ... and {len(u) - 12} more' if len(u) > 12 else ''))

    ok = fails == 0 and clean_ok and planted_ok and not bad and cov_ok
    print('\n=> %s' % ('ALL PASS -- Mechanical sentences ARE the executable doctrine'
                       if ok else 'FAILURES PRESENT'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
