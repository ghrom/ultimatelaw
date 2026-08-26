#!/usr/bin/env python3
"""Per-term claim-equivalence gate: canonical dictionary vs Mechanical rendering.

The structural gates check form and discipline; nothing checks that the Mechanical
entry MAKES THE SAME CLAIMS as the canonical one. This gate closes that hole by
asking the local Qwen doctrine-checker, per term: same claims, dropped claims,
added claims, contradictions. Style deltas are the point of Mechanical and are
never findings.

Results are cached by content hash (PROMPT_VERSION | term | canon | mech) in
mech_equiv_cache.json and saved after EVERY term, so a killed run loses nothing
and a re-run after an edit only re-judges the changed terms.

Usage:
  python tools/mech_equiv_gate.py                 # full gate, cache-aware
  python tools/mech_equiv_gate.py --selftest      # prove the gate CAN fail
  python tools/mech_equiv_gate.py --term IOU --term Debt
  python tools/mech_equiv_gate.py --limit 5 --workers 2
  python tools/mech_equiv_gate.py --list-differs  # re-print findings from cache

Exit 0 = every term EQUIVALENT (or byte-identical, or adjudicated). Exit 1 otherwise.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dict_parse import parse, CANON, MECH  # noqa: E402

# runtime artifacts (verdict cache, report) stay outside the repo
RUNTIME = Path(os.path.expanduser('~/tmp'))
RUNTIME.mkdir(parents=True, exist_ok=True)
CACHE = RUNTIME / 'mech_equiv_cache.json'
REPORT = RUNTIME / 'mech-equiv-report.md'

PROMPT_VERSION = 'v3'
MODEL_ALIAS = 'unsloth/Qwen3.8-27B-GGUF'

# Findings Pete has adjudicated as acceptable renderings. Key = term, value =
# list of substrings; a finding containing one of them is counted OK and does
# not fail the gate. Mirrors the structural gate's CONFIRMED_OK pattern. Keep this SHORT
# and reviewed -- it is doctrine policy, not noise control.
ADJUDICATED = {
    # Pete 2026-08-26: a rigid monopoly cannot persist against competition
    # without state coercion (see Market Dominance: force turns dominance into
    # monopoly) -- the restrictive rendering IS the doctrine.
    'Competition': ['narrows the monopoly claim'],
    # Pete 2026-08-26: "Perimeter grows not just outward" -- growth in every
    # dimension (capability, redundancy, centers), not only spatial reach.
    # The rendering says "grows"; the canonical's "outward-expanding" is the
    # narrower phrasing.
    'Perimeter': ['expands outward'],
}

SYSTEM_PROMPT = """You judge whether two renderings of one dictionary entry make the same claims.

Rendering A is the canonical English entry of the Ultimate Law Coherent Dictionary. Rendering B is "Mechanical": a controlled-language rendering of A with short sentences (25 words or less), a restricted one-meaning-per-word vocabulary, simple tenses, and active voice. Because the vocabulary is restricted, B MUST substitute approved near-synonyms and recast sentences. That is the design, not a finding.

MATERIALITY TEST -- the only thing that decides:
A difference is MATERIAL only if it changes what the entry permits, forbids, requires, makes possible or impossible, or bounds -- for at least one agent or case. To call a difference material you must name a concrete case that the two renderings judge differently. If you cannot name such a case, the difference is wording, not doctrine.

DOCTRINE CONTEXT lists the canonical definitions of terms this entry references. What counts as property, harm, damage, a victim, or an agent is decided by those entries, not by everyday usage -- use them to find discriminating cases (e.g. if Damage covers body, property, and freedom, then narrowing "what was taken" to "property taken" excludes takings of freedom and is material). The context is background only: differences between rendering B and the context entries are never findings; only A-vs-B differences are.

Usually wording (unless it passes the materiality test): approved-synonym substitution (initiate->start, belongs to->owns, what->the data); the copula frame B needs ("Agency is the capacity of an agent to..." where A has "The capacity to..."); sentence splits and reordering; explicit subjects or possessors that doctrine already implies; examples reworded. Put these in "wording" only if worth a human glance, else omit them entirely.

Material differences go in exactly three arrays:
- missing_in_mech: a claim A makes that B does not carry at all
- added_in_mech: a claim B makes that A does not carry
- contradictions: B judges some case the opposite way A does. This includes a dropped or added qualifier (only, never, by itself, in full, defaults to) that turns a conditional claim categorical or the reverse; a narrowed or widened noun class that changes what the entry reaches; an inverted direction or exchanged roles.

For every item in the three material arrays, append the discriminating case after " -- case: ": one short clause naming a situation the two renderings judge differently.

Output ONLY one JSON object, no other text:
{"verdict": "EQUIVALENT" or "DIFFERS", "missing_in_mech": [], "added_in_mech": [], "contradictions": [], "wording": [], "note": "one short line"}
verdict is DIFFERS only if at least one of the three material arrays is non-empty; "wording" never makes it DIFFERS."""


def discover_endpoint(explicit):
    if explicit:
        return explicit.rstrip('/')
    try:
        out = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq llama-server.exe', '/FO', 'CSV'],
                             capture_output=True, text=True, timeout=15).stdout
        pids = [row.split('","')[1] for row in out.splitlines() if row.startswith('"llama-server')]
        if not pids:
            raise RuntimeError('no llama-server.exe process found')
        ns = subprocess.run(['netstat', '-ano'], capture_output=True, text=True, timeout=30).stdout
        for line in ns.splitlines():
            if 'LISTENING' not in line:
                continue
            parts = line.split()
            if len(parts) >= 5 and parts[-1] in pids and parts[1].startswith('127.0.0.1:'):
                return 'http://' + parts[1]
    except Exception as e:
        raise SystemExit(f'[equiv] cannot discover llama-server endpoint: {e}\n'
                         f'        pass --endpoint http://127.0.0.1:PORT')
    raise SystemExit('[equiv] llama-server found but no 127.0.0.1 LISTENING port; pass --endpoint')


def http_json(url, payload=None, timeout=600):
    req = urllib.request.Request(url, headers={'Content-Type': 'application/json'})
    data = json.dumps(payload).encode() if payload is not None else None
    with urllib.request.urlopen(req, data=data, timeout=timeout) as r:
        return json.loads(r.read().decode('utf-8', 'replace'))


STRIP_THINK = re.compile(r'<think>.*?</think>', re.S)


def extract_json(text):
    text = STRIP_THINK.sub('', text)
    text = re.sub(r'^```(?:json)?|```$', '', text.strip(), flags=re.M).strip()
    start = text.find('{')
    end = text.rfind('}')
    if start == -1 or end <= start:
        raise ValueError(f'no JSON object in reply: {text[:200]!r}')
    return json.loads(text[start:end + 1])


def build_context(term, cmap, cap=8):
    """Canonical definitions of the terms this entry references (1 hop), in
    order of first appearance. Case-insensitive: older entries lowercase their
    cross-references."""
    d = cmap[term]
    refs = []
    for name in cmap:
        if name == term:
            continue
        m = re.search(r'\b' + re.escape(name) + r'\b', d, re.I)
        if m:
            refs.append((m.start(), name))
    refs.sort()
    return '\n\n'.join(f'{name}: {cmap[name]}' for _, name in refs[:cap])


def ask_qwen(endpoint, term, canon, mech, ctx, retries=2):
    user = (f'TERM: {term}\n\n'
            f'DOCTRINE CONTEXT (background only):\n{ctx or "(none)"}\n\n'
            f'RENDERING A (canonical):\n{canon}\n\n'
            f'RENDERING B (Mechanical):\n{mech}')
    payload = {
        'model': MODEL_ALIAS,
        'messages': [{'role': 'system', 'content': SYSTEM_PROMPT},
                     {'role': 'user', 'content': user}],
        'temperature': 0,
        'seed': 0,
        'max_tokens': 20000,  # thinking on long entries (Forfeiture) overflows smaller caps
        'cache_prompt': True,
    }
    last = None
    for attempt in range(retries + 1):
        try:
            resp = http_json(endpoint + '/v1/chat/completions', payload)
            msg = resp['choices'][0]['message']
            content = msg.get('content') or ''
            if not content.strip():
                # thinking ran away and ate the whole completion budget --
                # retry this term with thinking off, which always terminates
                payload['chat_template_kwargs'] = {'enable_thinking': False}
                raise ValueError('empty content (thinking consumed the budget)')
            verdict = extract_json(content)
            for k in ('missing_in_mech', 'added_in_mech', 'contradictions', 'wording'):
                verdict.setdefault(k, [])
                verdict[k] = [str(x) for x in verdict[k]]
            v = str(verdict.get('verdict', '')).upper()
            has_findings = any(verdict[k] for k in
                               ('missing_in_mech', 'added_in_mech', 'contradictions'))
            # the arrays are the truth; verdict string must agree with them
            verdict['verdict'] = 'DIFFERS' if has_findings else 'EQUIVALENT'
            if v not in ('EQUIVALENT', 'DIFFERS'):
                verdict['note'] = (verdict.get('note') or '') + ' [verdict string was malformed]'
            return verdict
        except Exception as e:
            last = e
            if attempt < retries:
                payload['messages'][1]['content'] = user + \
                    '\n\nReminder: output ONLY the JSON object described, nothing else.'
                time.sleep(2)
    raise RuntimeError(f'{term}: Qwen call failed after {retries + 1} attempts: {last}')


def key_of(term, canon, mech, ctx):
    h = hashlib.sha256()
    for part in (PROMPT_VERSION, term, canon, mech, ctx):
        h.update(part.encode())
        h.update(b'\x00')
    return h.hexdigest()


_cache_lock = threading.Lock()


def cache_put(cache, key, value):
    with _cache_lock:
        cache[key] = value
        tmp = CACHE.with_suffix('.json.tmp')
        tmp.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding='utf-8')
        tmp.replace(CACHE)


def adjudicated_ok(term, finding):
    return any(sub in finding for sub in ADJUDICATED.get(term, []))


def judge_all(pairs, endpoint, workers, force):
    cache = json.loads(CACHE.read_text(encoding='utf-8')) if CACHE.exists() else {}
    results = {}
    todo = []
    for term, canon, mech, ctx in pairs:
        if canon.strip() == mech.strip():
            results[term] = {'verdict': 'EQUIVALENT', 'missing_in_mech': [],
                             'added_in_mech': [], 'contradictions': [],
                             'note': 'byte-identical (fast path)'}
            continue
        k = key_of(term, canon, mech, ctx)
        if not force and k in cache:
            results[term] = cache[k]
            continue
        todo.append((term, canon, mech, ctx, k))

    n_cached = len(results)
    print(f'[equiv] {len(pairs)} terms: {n_cached} cached/identical, {len(todo)} to judge '
          f'(workers={workers})')
    done = 0
    t0 = time.time()
    if todo:
        with ThreadPoolExecutor(max_workers=workers) as ex:
            futs = {ex.submit(ask_qwen, endpoint, t, c, m, x): (t, k)
                    for t, c, m, x, k in todo}
            for fut in as_completed(futs):
                term, k = futs[fut]
                try:
                    verdict = fut.result()
                    verdict['model'] = MODEL_ALIAS
                    verdict['ts'] = time.strftime('%Y-%m-%d %H:%M:%S')
                    cache_put(cache, k, verdict)  # errors are NOT cached: re-runs retry them
                except Exception as e:
                    verdict = {'verdict': 'ERROR', 'missing_in_mech': [],
                               'added_in_mech': [], 'contradictions': [],
                               'wording': [], 'note': str(e)}
                results[term] = verdict
                done += 1
                rate = (time.time() - t0) / done
                eta = rate * (len(todo) - done)
                mark = {'EQUIVALENT': 'OK ', 'ERROR': 'ERR'}.get(verdict['verdict'], 'DIF')
                print(f'  [{done}/{len(todo)}] {mark} {term}  '
                      f'({rate:.0f}s/term, ~{eta/60:.0f} min left)', flush=True)
    return results


def report(pairs, results):
    lines = [f'# Mechanical claim-equivalence report',
             f'',
             f'Generated {time.strftime("%Y-%m-%d %H:%M:%S")} by mech_equiv_gate.py '
             f'({PROMPT_VERSION}, {MODEL_ALIAS}).',
             f'Style differences are by design and are not findings; only claim '
             f'differences are listed.', '']
    n_eq = n_dif = n_adj = n_word = 0
    fails = []
    for term, *_ in pairs:
        r = results.get(term)
        if r is None:
            continue
        findings = [('missing_in_mech', f) for f in r['missing_in_mech']] + \
                   [('added_in_mech', f) for f in r['added_in_mech']] + \
                   [('contradictions', f) for f in r['contradictions']]
        wording = r.get('wording', [])
        live = [(kind, f) for kind, f in findings if not adjudicated_ok(term, f)]
        adj = [(kind, f) for kind, f in findings if adjudicated_ok(term, f)]
        if r['verdict'] == 'ERROR':
            n_dif += 1
            fails.append(term)
            lines.append(f'## {term}  (ERROR — not judged)')
            lines.append(f'- note: {r.get("note", "")}')
            lines.append('')
            continue
        if not findings and not wording:
            n_eq += 1
            continue
        if live:
            n_dif += 1
            fails.append(term)
            status = 'DIFFERS'
        elif findings:
            n_adj += 1
            status = 'ADJUDICATED'
        else:
            n_word += 1
            status = 'WORDING-ONLY'
        lines.append(f'## {term}  ({status})')
        for kind, f in live:
            lines.append(f'- **{kind}**: {f}')
        for kind, f in adj:
            lines.append(f'- ~~{kind}: {f}~~ (adjudicated OK)')
        for f in wording:
            lines.append(f'- wording: {f}')
        if r.get('note'):
            lines.append(f'- note: {r["note"]}')
        lines.append('')
    lines.insert(3, f'**{n_eq} equivalent / {n_word} wording-only / {n_adj} adjudicated / '
                    f'{n_dif} differ** out of {len(pairs)} terms judged.')
    REPORT.write_text('\n'.join(lines), encoding='utf-8')
    return fails


def selftest(endpoint):
    """The gate must be able to FAIL. Feed it a doctored Mechanical entry with
    inverted doctrine and require DIFFERS with a contradiction."""
    cmap = {e['term']: e['definition'] for e in parse(CANON)}
    canon = cmap['Restitution']
    doctored = ('Restitution is the return of what an offender took, or of its value, '
                'to the agent who owns it. Restitution repairs the material damage. '
                'By itself it erases the guilt, and the moral debt ends with it. '
                'Every agent can receive restitution.')
    print('[selftest] judging canonical Restitution vs a doctored inverted rendering...')
    v = ask_qwen(endpoint, 'Restitution (SELFTEST)', canon, doctored,
                 build_context('Restitution', cmap))
    print(json.dumps(v, indent=2, ensure_ascii=False))
    ok = v['verdict'] == 'DIFFERS' and (v['contradictions'] or v['missing_in_mech'])
    print(f'[selftest] {"PASS -- the gate can detect inverted doctrine" if ok else "FAIL -- gate did NOT flag an inverted entry; do not trust green runs"}')
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--endpoint')
    ap.add_argument('--workers', type=int, default=2)
    ap.add_argument('--term', action='append', default=[])
    ap.add_argument('--limit', type=int)
    ap.add_argument('--force', action='store_true', help='ignore cache')
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--list-differs', action='store_true',
                    help='rebuild report from cache only, no Qwen calls')
    args = ap.parse_args()

    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

    canon = parse(CANON)
    mech = parse(MECH)
    cterms = [e['term'] for e in canon]
    mterms = [e['term'] for e in mech]
    if cterms != mterms:
        print(f'[equiv] FAIL: term lists differ (canonical {len(cterms)} / mech {len(mterms)}); '
              f'run the structural gates first')
        return 1

    mmap = {e['term']: e['definition'] for e in mech}
    cmap = {e['term']: e['definition'] for e in canon}
    pairs = [(e['term'], e['definition'], mmap[e['term']],
              build_context(e['term'], cmap)) for e in canon]
    if args.term:
        pairs = [p for p in pairs if p[0] in args.term]
        missing = set(args.term) - {p[0] for p in pairs}
        if missing:
            print(f'[equiv] unknown terms: {sorted(missing)}')
            return 1
    if args.limit:
        pairs = pairs[:args.limit]

    if args.list_differs:
        cache = json.loads(CACHE.read_text(encoding='utf-8')) if CACHE.exists() else {}
        results = {}
        for term, c, m, x in pairs:
            if c.strip() == m.strip():
                results[term] = {'verdict': 'EQUIVALENT', 'missing_in_mech': [],
                                 'added_in_mech': [], 'contradictions': [], 'note': ''}
            elif (k := key_of(term, c, m, x)) in cache:
                results[term] = cache[k]
        fails = report(pairs, results)
        print(f'[equiv] report rebuilt from cache: {len(results)}/{len(pairs)} terms cached; '
              f'{len(fails)} differ -> {REPORT}')
        return 0 if not fails else 1

    endpoint = discover_endpoint(args.endpoint)
    health = http_json(endpoint + '/health', timeout=30)
    print(f'[equiv] endpoint {endpoint} health={health.get("status", "?")}')

    if args.selftest:
        return selftest(endpoint)

    results = judge_all(pairs, endpoint, args.workers, args.force)
    fails = report(pairs, results)
    n_eq = sum(1 for t, *_ in pairs
               if results[t]['verdict'] == 'EQUIVALENT')
    print(f'\n[equiv] {n_eq}/{len(pairs)} EQUIVALENT; '
          f'{len(fails)} DIFFER after adjudication -> {REPORT}')
    for t in fails:
        r = results[t]
        first = (r['contradictions'] or r['missing_in_mech'] or r['added_in_mech']
                 or [r.get('note', 'error')])[0]
        print(f'  {r["verdict"]:8s} {t}: {first}')
    print(f'=> {"GATE PASS" if not fails else "GATE FAIL"}')
    return 0 if not fails else 1


if __name__ == '__main__':
    sys.exit(main())
