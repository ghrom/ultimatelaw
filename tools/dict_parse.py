#!/usr/bin/env python3
"""Shared parser and paths for the dictionary renderings.

Mirrors the site build's parsing: a term line, then definition paragraphs,
blank-line separated. Paths are repo-relative so any clone can run the tools.
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CANON = REPO / 'dictionary' / 'coherent-dictionary-of-simple-english.txt'
MECH = REPO / 'dictionary' / 'coherent-dictionary-mechanical.txt'
LOGIC = REPO / 'dictionary' / 'coherent-dictionary-logic.txt'


def parse(path):
    """Term entries with paragraph structure preserved."""
    lines = Path(path).read_text(encoding='utf-8').split('\n')
    i = 0
    while i < len(lines) and lines[i].strip() != 'Action':
        i += 1
    out = []
    while i < len(lines):
        line = lines[i].strip()
        if re.match(r'^[A-Z][A-Za-z /(),\-]+$', line) and len(line) < 80:
            term, i = line, i + 1
            paras = []
            while i < len(lines):
                dl = lines[i].strip()
                if not dl:
                    j = i + 1
                    while j < len(lines) and not lines[j].strip():
                        j += 1
                    if j < len(lines):
                        nxt = lines[j].strip()
                        if re.match(r'^[A-Z][A-Za-z /(),\-]+$', nxt) and len(nxt) < 80:
                            i = j
                            break
                    else:
                        i = len(lines)
                        break
                else:
                    paras.append(dl)
                    i += 1
            out.append({'term': term, 'paras': paras,
                        'definition': ' '.join(paras)})
        else:
            i += 1
    return out
