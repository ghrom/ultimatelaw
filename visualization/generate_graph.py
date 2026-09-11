#!/usr/bin/env python3
"""Generate dictionary structure artifacts: JSON graph, Mermaid, and embedded HTML."""

from __future__ import annotations

import json
import re
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DICTIONARY = ROOT / "dictionary" / "coherent-dictionary-of-simple-english.txt"
OUT_DIR = Path(__file__).resolve().parent / "output"

# Manual structure metadata (curated from coherence analysis)
CLUSTERS: dict[str, list[str]] = {
    "axioms": [
        "Law",
        "Golden Rule (Passive Version)",
        "Logic",
        "Belief",
        "Truth",
        "Error",
        "Reason",
    ],
    "mind_agency": [
        "Agent",
        "Agency",
        "Action",
        "Consciousness",
        "Self-Awareness",
        "Mind",
        "Free Will",
        "Intention",
        "Decision",
        "Choice",
        "Intelligence",
    ],
    "boundaries_rights": [
        "Boundary",
        "Consent",
        "Agreement",
        "Permission",
        "Rights",
        "Self-Ownership",
        "Autonomy",
        "Liberty",
        "Freedom",
        "Ownership",
        "Property",
    ],
    "harm_crime": [
        "Harm",
        "Damage",
        "Victim",
        "Crime",
        "Evil",
        "Good",
        "Violation",
        "Negligence",
        "Victimless",
        "Victimless Trade",
    ],
    "coercion_trade": [
        "Coercion",
        "Theft",
        "Fraud",
        "Deception",
        "Duress",
        "Force",
        "Violence",
        "Threat",
        "Government",
        "Regulation",
    ],
    "justice": [
        "Justice",
        "Guilt",
        "Punishment",
        "Punisher",
        "Proportion",
        "Retribution",
        "Restitution",
        "Forgiveness",
        "Revenge",
        "Self-Defense",
        "Murder",
        "Outlaw",
        "Mandate",
    ],
    "exchange": [
        "Trade",
        "Free Trade",
        "Deal",
        "Contract",
        "Contract Breach",
        "License",
        "Market",
        "Capitalism",
        "Socialism",
        "Money",
        "Currency",
        "Profit",
        "IOU",
        "Debt",
    ],
    "civilization": [
        "Civilization",
        "Civilizational Velocity",
        "Good News",
        "Perimeter",
        "Singleton",
        "Way of Happiness",
        "Happiness",
        "Voluntaryism",
        "Nomocracy",
        "War",
    ],
    "epistemology": [
        "Knowledge",
        "Model",
        "Prediction",
        "Evidence",
        "Learning",
        "Fallibility",
        "Wisdom",
        "Curiosity",
    ],
    "emergence": [
        "Infinite Change",
        "Emergence",
        "Pattern",
        "Time",
        "Universe",
        "Timeless Infinity",
    ],
}

LAYERS: dict[str, int] = {
    "Logic": 0,
    "Law": 0,
    "Golden Rule (Passive Version)": 0,
    "Truth": 0,
    "Agent": 1,
    "Agency": 1,
    "Harm": 1,
    "Boundary": 1,
    "Consent": 1,
    "Coercion": 2,
    "Fraud": 2,
    "Theft": 2,
    "Violation": 2,
    "Victim": 3,
    "Crime": 3,
    "Guilt": 3,
    "Justice": 4,
    "Self-Defense": 4,
    "Restitution": 4,
    "Retribution": 4,
    "Forgiveness": 4,
    "Punishment": 4,
    "Trade": 5,
    "Market": 5,
    "Civilization": 5,
    "Perimeter": 5,
    "Good News": 5,
}

STABILITY: dict[str, str] = {
    # green — tight logical closure
    "Crime": "green",
    "Victim": "green",
    "Theft": "green",
    "Coercion": "green",
    "Murder": "green",
    "Outlaw": "green",
    "Consent": "green",
    "Self-Defense": "green",
    "Justice": "green",
    "Proportion": "green",
    "Fraud": "green",
    "Contract Breach": "green",
    # blue — post-hoc additions after gap discovery
    "Duress": "blue",
    # yellow — defined but thin / edge-case pressure
    "Negligence": "yellow",
    "Lesser Evil": "yellow",
    "Faith": "yellow",
    "Democracy": "yellow",
    # gray — implementation / strategic, not pure moral core
    "Perimeter": "gray",
    "Nomocracy": "gray",
    "Good News": "gray",
    "Civilizational Velocity": "gray",
}

ALIASES: dict[str, str] = {
    "Golden Rule": "Golden Rule (Passive Version)",
    "passive Golden Rule": "Golden Rule (Passive Version)",
    "Ultimate Law": "Law",
    "no victim no crime": "Crime",
    "Contract": "Contract",
    "License": "License",
    "Restitution": "Restitution",
    "Perimeters": "Perimeter",
    "singletons": "Singleton",
    "outlaw": "Outlaw",
    "nomocracy": "Nomocracy",
}

REASONING_CHAINS = [
    {
        "id": "taxation",
        "conclusion": "Taxation is theft",
        "premises": ["Theft", "Democracy", "Government"],
        "derived": True,
    },
    {
        "id": "voluntary-slavery",
        "conclusion": "Voluntary slavery is impossible",
        "premises": ["Self-Ownership", "Consent", "Property"],
        "derived": True,
    },
    {
        "id": "price-gouging",
        "conclusion": "Disaster price gouging is coercion",
        "premises": ["Consent", "Duress", "Coercion"],
        "derived": True,
    },
    {
        "id": "murder-outlaw",
        "conclusion": "Murder creates permanent outlaw status",
        "premises": ["Murder", "Justice", "Outlaw"],
        "derived": True,
    },
    {
        "id": "ip-vs-license",
        "conclusion": "IP monopoly is coercion; voluntary license is contract",
        "premises": ["Intellectual Property", "License", "Contract", "Coercion"],
        "derived": True,
    },
]

STABILITY_COLORS = {
    "green": "#3d9970",
    "yellow": "#f5c842",
    "blue": "#4a9eff",
    "gray": "#8b949e",
    "default": "#c9d1d9",
}

CLUSTER_COLORS = {
    "axioms": "#e06c75",
    "mind_agency": "#d19a66",
    "boundaries_rights": "#98c379",
    "harm_crime": "#e5c07b",
    "coercion_trade": "#c678dd",
    "justice": "#61afef",
    "exchange": "#56b6c2",
    "civilization": "#be5046",
    "epistemology": "#abb2bf",
    "emergence": "#7f848e",
    "other": "#6e7681",
}


def parse_dictionary(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    blocks = [b.strip() for b in text.split("\n\n") if b.strip()]
    start = next(i for i, b in enumerate(blocks) if b.split("\n")[0] == "Action")
    terms: dict[str, str] = {}
    for block in blocks[start:]:
        lines = block.split("\n")
        term = lines[0].strip()
        definition = "\n".join(lines[1:]).strip()
        terms[term] = definition
    return terms


def term_cluster(term: str) -> str:
    for cluster, members in CLUSTERS.items():
        if term in members:
            return cluster
    return "other"


def find_references(definition: str, term: str, all_terms: dict[str, str]) -> list[str]:
    refs: set[str] = set()
    haystack = definition

    for alias, target in ALIASES.items():
        if alias.lower() in haystack.lower() and target in all_terms and target != term:
            refs.add(target)

    for other in sorted(all_terms, key=len, reverse=True):
        if other == term:
            continue
        pattern = re.compile(r"\b" + re.escape(other) + r"\b")
        if pattern.search(haystack):
            refs.add(other)

    return sorted(refs)


def build_graph(terms: dict[str, str]) -> dict:
    nodes = []
    edges = []
    term_to_id = {name: i for i, name in enumerate(sorted(terms))}

    for name in sorted(terms):
        cluster = term_cluster(name)
        nodes.append(
            {
                "id": term_to_id[name],
                "name": name,
                "cluster": cluster,
                "layer": LAYERS.get(name, -1),
                "stability": STABILITY.get(name, "default"),
                "definition": terms[name],
                "color": STABILITY_COLORS.get(STABILITY.get(name, "default"), STABILITY_COLORS["default"]),
                "clusterColor": CLUSTER_COLORS.get(cluster, CLUSTER_COLORS["other"]),
            }
        )

    seen_edges: set[tuple[int, int]] = set()
    for name, definition in terms.items():
        for ref in find_references(definition, name, terms):
            src, dst = term_to_id[name], term_to_id[ref]
            key = (src, dst)
            if key not in seen_edges:
                seen_edges.add(key)
                edges.append({"source": src, "target": dst, "type": "references"})

    # Curated spine edges (structural, not just textual reference)
    spine = [
        ("Harm", "Victim"),
        ("Victim", "Crime"),
        ("Crime", "Guilt"),
        ("Guilt", "Justice"),
        ("Justice", "Punishment"),
        ("Justice", "Restitution"),
        ("Justice", "Retribution"),
        ("Justice", "Forgiveness"),
        ("Consent", "Boundary"),
        ("Boundary", "Violation"),
        ("Violation", "Harm"),
        ("Murder", "Outlaw"),
    ]
    for src_name, dst_name in spine:
        if src_name in term_to_id and dst_name in term_to_id:
            key = (term_to_id[src_name], term_to_id[dst_name])
            if key not in seen_edges:
                seen_edges.add(key)
                edges.append(
                    {
                        "source": term_to_id[src_name],
                        "target": term_to_id[dst_name],
                        "type": "spine",
                    }
                )

    hub_scores = {n["id"]: 0 for n in nodes}
    for e in edges:
        hub_scores[e["target"]] = hub_scores.get(e["target"], 0) + 1
    for n in nodes:
        n["inDegree"] = hub_scores.get(n["id"], 0)

    return {
        "meta": {
            "termCount": len(nodes),
            "edgeCount": len(edges),
            "source": str(DICTIONARY.relative_to(ROOT)),
        },
        "clusters": CLUSTERS,
        "layers": LAYERS,
        "stabilityLegend": {
            "green": "Tight closure",
            "yellow": "Thin / edge-case pressure",
            "blue": "Post-hoc addition",
            "gray": "Implementation / strategic",
            "default": "Standard definition",
        },
        "reasoningChains": REASONING_CHAINS,
        "nodes": nodes,
        "edges": edges,
    }


def write_mermaid(graph: dict, path: Path) -> None:
  lines = ["flowchart TB", "    %% Auto-generated dependency graph (hub terms only)"]
  hubs = sorted(graph["nodes"], key=lambda n: n["inDegree"], reverse=True)[:40]
  hub_names = {n["name"] for n in hubs}
  id_map = {n["name"]: re.sub(r"[^A-Za-z0-9]", "", n["name"]) or "Term" for n in hubs}

  for n in hubs:
      sid = id_map[n["name"]]
      label = n["name"].replace('"', "'")
      lines.append(f'    {sid}["{label}"]')

  for e in graph["edges"]:
      src = next(n for n in graph["nodes"] if n["id"] == e["source"])
      dst = next(n for n in graph["nodes"] if n["id"] == e["target"])
      if src["name"] in hub_names and dst["name"] in hub_names:
          lines.append(f"    {id_map[src['name']]} --> {id_map[dst['name']]}")

  path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_mermaid_layers(path: Path) -> None:
    content = textwrap.dedent(
        """
        flowchart TB
            subgraph L0["Layer 0 — Axioms"]
                Logic["Logic"]
                GR["Passive Golden Rule"]
                NVC["No victim, no crime"]
                ConsentA["Consent required"]
            end
            subgraph L1["Layer 1 — Ontology"]
                Agent["Agent"]
                Harm["Harm"]
                Boundary["Boundary"]
                Property["Property"]
            end
            subgraph L2["Layer 2 — Violation"]
                Coercion["Coercion"]
                Fraud["Fraud"]
                Theft["Theft"]
                Violation["Violation"]
            end
            subgraph L3["Layer 3 — Crime and debt"]
                Victim["Victim"]
                Crime["Crime"]
                Guilt["Guilt"]
            end
            subgraph L4["Layer 4 — Response"]
                SD["Self-Defense"]
                Justice["Justice"]
                Restitution["Restitution"]
                Punishment["Punishment"]
            end
            subgraph L5["Layer 5 — Civilization"]
                Trade["Free Trade"]
                Perimeter["Perimeter"]
                Velocity["Civilizational Velocity"]
                GN["Good News"]
            end
            Logic --> Agent
            GR --> Boundary
            ConsentA --> Boundary
            NVC --> Victim
            Agent --> Harm
            Boundary --> Violation
            Harm --> Victim
            Victim --> Crime
            Crime --> Guilt
            Guilt --> Justice
            Justice --> Restitution
            Justice --> Punishment
            SD -.-> Harm
            ConsentA --> Trade
            Justice --> Perimeter
            Trade --> Velocity
            Velocity --> GN
        """
    ).strip()
    path.write_text(content + "\n", encoding="utf-8")


def embed_html(graph: dict, template_path: Path, out_path: Path) -> None:
    template = template_path.read_text(encoding="utf-8")
    payload = json.dumps(graph, ensure_ascii=False)
    html = template.replace("/*__GRAPH_DATA__*/", f"const GRAPH_DATA = {payload};")
    out_path.write_text(html, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    terms = parse_dictionary(DICTIONARY)
    graph = build_graph(terms)

    (OUT_DIR / "dictionary-graph.json").write_text(
        json.dumps(graph, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    write_mermaid(graph, OUT_DIR / "dictionary-graph.mmd")
    write_mermaid_layers(OUT_DIR / "dictionary-layers.mmd")

    stats = {
        "termCount": len(terms),
        "edgeCount": graph["meta"]["edgeCount"],
        "topHubs": [
            {"name": n["name"], "inDegree": n["inDegree"]}
            for n in sorted(graph["nodes"], key=lambda x: x["inDegree"], reverse=True)[:15]
        ],
    }
    (OUT_DIR / "graph-stats.json").write_text(
        json.dumps(stats, indent=2) + "\n", encoding="utf-8"
    )

    template = Path(__file__).resolve().parent / "viewer.template.html"
    embed_html(graph, template, OUT_DIR / "index.html")

    print(f"Parsed {len(terms)} terms")
    print(f"Generated {graph['meta']['edgeCount']} edges")
    print(f"Output: {OUT_DIR}")


if __name__ == "__main__":
    main()
