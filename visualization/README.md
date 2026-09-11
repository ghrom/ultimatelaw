# Dictionary Visualization

Tools for exploring the structure of the Coherent Dictionary.

## Quick start

```bash
# Generate all artifacts
python3 visualization/generate_graph.py

# Open interactive explorer (standalone — no server required)
xdg-open visualization/output/index.html   # Linux
open visualization/output/index.html       # macOS
```

Or serve locally if your browser blocks file access:

```bash
cd visualization/output && python3 -m http.server 8080
# → http://localhost:8080
```

## What gets generated

| Output | Purpose |
|--------|---------|
| `output/dictionary-graph.json` | Full graph for custom tooling |
| `output/dictionary-graph.mmd` | Mermaid dependency graph (top hubs) |
| `output/dictionary-layers.mmd` | Mermaid layer stack |
| `output/graph-stats.json` | Term count, edge count, hub ranking |
| `output/index.html` | Interactive D3 force-directed explorer |

## Interactive features

- **Search** — filter by term name or definition text
- **Cluster / stability filters** — narrow to justice, coercion, etc.
- **Color modes** — stability overlay, cluster, or layer
- **Click nodes** — definition, references, referenced-by
- **Reasoning chains** — click to walk derived conclusions
- **Spine edges** — blue links mark curated axiomatic chain

## Static documentation

See [`docs/dictionary-structure.md`](../docs/dictionary-structure.md) for Mermaid diagrams:

1. Layered stack
2. Justice pipeline
3. Coercion decision tree
4. Cluster map
5. Reasoning propagation
6. Stability overlay

## How references are detected

`generate_graph.py` parses the dictionary into term blocks, then:

1. Matches other term names (longest-first) with word boundaries
2. Applies aliases (`Golden Rule` → `Golden Rule (Passive Version)`)
3. Adds curated spine edges for the justice chain

Re-run after any dictionary edit to keep artifacts in sync.
