# Dictionary Structure

Visual map of the [Coherent Dictionary of Simple English](../dictionary/coherent-dictionary-of-simple-english.txt) — how terms stack, flow, and connect.

**Interactive explorer:** open [`visualization/output/index.html`](../visualization/output/index.html) in a browser (or run `python3 -m http.server` from `visualization/output/`).

**Regenerate graphs:** `python3 visualization/generate_graph.py`

---

## 1. Layered stack

What rests on what. Four axioms at the base; everything else derives.

```mermaid
flowchart TB
    subgraph L0["Layer 0 — Axioms"]
        Logic["Logic (supreme)"]
        GR["Passive Golden Rule"]
        NVC["No victim, no crime"]
        Consent["Consent required"]
    end

    subgraph L1["Layer 1 — Ontology"]
        Agent["Agent / Agency"]
        Harm["Harm"]
        Boundary["Boundary"]
        Property["Property / Ownership"]
    end

    subgraph L2["Layer 2 — Violation"]
        Coercion["Coercion"]
        Fraud["Fraud / Deception"]
        Theft["Theft"]
        Violation["Violation"]
    end

    subgraph L3["Layer 3 — Crime & debt"]
        Victim["Victim"]
        Crime["Crime"]
        Guilt["Guilt"]
    end

    subgraph L4["Layer 4 — Response"]
        SD["Self-Defense"]
        Justice["Justice"]
        Restitution["Restitution"]
        Retribution["Retribution"]
        Forgiveness["Forgiveness"]
        Punishment["Punishment"]
    end

    subgraph L5["Layer 5 — Civilization"]
        Trade["Free Trade / Market"]
        Perimeter["Perimeter"]
        Velocity["Civilizational Velocity"]
        GN["Good News"]
    end

    Logic --> Agent
    GR --> Boundary
    Consent --> Boundary
    NVC --> Victim

    Agent --> Harm
    Boundary --> Violation
    Harm --> Victim
    Victim --> Crime
    Crime --> Guilt
    Guilt --> Justice

    Justice --> Retribution
    Justice --> Forgiveness
    Justice --> Restitution
    Punishment --> Retribution
    Punishment --> Restitution
    SD -.->|"stops ongoing harm only"| Harm

    Consent --> Trade
    Justice --> Perimeter
    Trade --> Velocity
    Velocity --> GN
```

---

## 2. Justice pipeline

How a boundary crossing becomes crime, debt, and response.

```mermaid
flowchart LR
    A["Action crosses boundary"] --> B{"Consent given?"}
    B -->|Yes| OK["Legitimate / Victimless"]
    B -->|No| C["Violation"]
    C --> D["Harm"]
    D --> E["Victim"]
    E --> F["Crime"]
    F --> G["Guilt (moral debt)"]

    G --> H{"Harm in progress?"}
    H -->|Yes| I["Self-Defense\n(proportionate, stop only)"]
    H -->|No| J["Justice"]

    J --> K["Restitution\n(material repair)"]
    J --> L{"Victim chooses"}
    L --> M["Retribution\n(proportional mirror)"]
    L --> N["Forgiveness\n(debt released)"]

    M --> O["Guilt erased"]
    N --> O
    K --> P["Damage repaired"]

    F --> Q{"Murder?"}
    Q -->|Yes| R["Outlaw\n(permanent guilt,\nno proxy)"]
```

---

## 3. Coercion decision tree

When force or coercion is morally permitted.

```mermaid
flowchart TD
    F["Force or coercion proposed"] --> V{"Real victim\nwith standing?"}
    V -->|No| X["Not justified\n(deterrence, preemption, war)"]
    V -->|Yes| P{"Harm in progress?"}

    P -->|Yes| SD["Self-Defense\nstop violation, proportionate"]
    P -->|No| M{"Victim mandate?"}

    M -->|No| X2["Not justified\n(control / revenge)"]
    M -->|Yes| PR{"Within Proportion ceiling?"}

    PR -->|No| RV["Revenge → new crime"]
    PR -->|Yes| J["Punishment\n(retribution / restitution)"]

    J --> E["Guilt may be closed"]
```

---

## 4. Concept cluster map

~187 terms grouped into navigable clusters (see interactive viewer for full graph).

```
                    [ Logic · Reason · Truth · Error ]
                                    |
        [ Mind · Consciousness · Agent · Free Will ]
                                    |
    [ Rights · Self-Ownership · Liberty · Autonomy ]
                                    |
[ Consent · Agreement · Contract · License · Duress ] —— ULTIMATE LAW —— [ Harm · Victim · Crime · Evil · Good ]
                                    |
        [ Justice · Punishment · Proportion · Outlaw ]
                                    |
    [ Trade · Market · Capitalism · Socialism · Money ]
                                    |
        [ Perimeter · Singleton · Way of Happiness · Good News ]
```

| Cluster | Hub terms | Role |
|---------|-----------|------|
| axioms | Logic, Golden Rule, Law | Supreme rules |
| mind_agency | Agent, Consciousness, Free Will | Who can act and consent |
| boundaries_rights | Consent, Rights, Self-Ownership | What may not be crossed |
| harm_crime | Harm, Victim, Crime | Violation detection |
| coercion_trade | Coercion, Theft, Fraud, Duress | Illegitimate taking |
| justice | Justice, Punishment, Proportion, Outlaw | Closing moral debt |
| exchange | Trade, Contract, Market | Voluntary cooperation |
| civilization | Perimeter, Good News, Velocity | Long-horizon outcomes |
| epistemology | Knowledge, Fallibility, Curiosity | Error correction |
| emergence | Infinite Change, Emergence | Ontological foundation |

---

## 5. Dependency graph

Auto-generated from textual cross-references in definitions. Top hubs by incoming references:

Run `python3 visualization/generate_graph.py` and see `visualization/output/graph-stats.json`.

The full Mermaid export (top 40 hubs) lives at [`visualization/output/dictionary-graph.mmd`](../visualization/output/dictionary-graph.mmd).

**Interpretation:** a thin vertical spine (Harm → Victim → Crime → Justice) with dense clusters around Consent, Coercion, Agent, and Trade.

---

## 6. Reasoning propagation

Conclusions derived from definitions, not stored as separate entries.

```mermaid
flowchart LR
    subgraph trained["In dictionary"]
        T1["Theft = taking without consent"]
        T2["Taxation = taking property"]
        T3["Democracy ≠ consent"]
    end

    subgraph derived["Inferred, not stored"]
        C["Taxation is theft"]
    end

    T1 --> C
    T2 --> C
    T3 --> C
```

| Chain | Premises | Conclusion |
|-------|----------|------------|
| Taxation | Theft, Democracy | Taxation is theft |
| Voluntary slavery | Self-Ownership, Consent | Cannot consent away personhood |
| Price gouging | Consent, Duress, Coercion | Exploitation under catastrophe is coercion |
| Murder | Murder, Justice, Outlaw | Permanent guilt, no proxy |
| IP vs license | Intellectual Property, License, Contract | Monopoly is coercion; voluntary license is contract |

See [`research/emergent-reasoning-from-definitions.md`](../research/emergent-reasoning-from-definitions.md) for empirical validation (60/63 test battery).

---

## 7. Stability overlay

Honest map of where the dictionary is tight vs. where pressure concentrates.

| Color | Meaning | Examples |
|-------|---------|----------|
| Green | Tight logical closure | Crime, Theft, Consent, Murder → Outlaw |
| Yellow | Defined but thin | Negligence, Lesser Evil, Democracy |
| Blue | Post-hoc patch after gap found | Duress |
| Gray | Implementation / strategic | Perimeter, Good News, Civilizational Velocity |

The interactive viewer colors nodes by stability, cluster, or layer.

---

## Artifacts

| File | Description |
|------|-------------|
| `visualization/generate_graph.py` | Parser + graph builder |
| `visualization/output/dictionary-graph.json` | Full node/edge data |
| `visualization/output/dictionary-graph.mmd` | Mermaid dependency graph |
| `visualization/output/dictionary-layers.mmd` | Mermaid layer stack |
| `visualization/output/index.html` | Standalone interactive explorer |
| `visualization/output/graph-stats.json` | Hub rankings and counts |

---

## Falsifiability

If a genuine contradiction appears between definitions, the dictionary should be amended — not defended. The [Duress](../dictionary/coherent-dictionary-of-simple-english.txt) entry is the canonical example: emergent reasoning found a gap; the definition was added.

Open an issue if you find a break in the chain.
