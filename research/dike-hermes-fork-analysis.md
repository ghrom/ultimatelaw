# Dike: Hermes Fork for Ultimate Law Nomocracy

**Date:** 2026-07-19  
**Upstream:** [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) @ `1d12d610eb6d83ae1739d6da9c4d498012a8ef7a` (v0.18.2 tip)  
**Local mirror:** `vendor/hermes-agent/` (gitignored; re-clone to refresh)  
**Branch:** `cursor/dike-hermes-fork-a67a`

---

## Name

**Dike** — Greek personification of justice as judgment (case-by-case right dealing). Daughter of Themis (divine law / laid-down order).

| Layer | Name | Role |
|-------|------|------|
| Constitution | **Themis** | Coherent Dictionary = Law (not invented by agents) |
| Agent | **Dike** | Discovers proven facts; states how Law applies |
| Upstream substrate | Hermes | Messenger / tools / memory / gateways (what we fork) |
| Retribution (later) | Nemesis | Proportionate collection when mandated — not the core agent |

Repo / binary name candidates: `dike-agent`, `dike`, `ultimatelaw-dike`. Prefer **dike-agent** for clarity next to hermes-agent.

---

## What We Pulled

Hermes is a large MIT Python agent product (~227 MB shallow clone, 3000+ `.py` files):

| Surface | What it is | UL relevance |
|---------|------------|--------------|
| `run_agent.py` / `agent/` | Core conversation + tool loop | Waist to keep; bind Law here |
| `skills/` + `optional-skills/` | Procedural memory (agentskills.io) | Prosecution playbooks as skills |
| `agent/memory_manager.py` + FTS5 state | Cross-session memory | Case memory / precedent search |
| `gateway/` | Telegram, Discord, Slack, WhatsApp, Signal, … | Filing / notification channels |
| `tools/` | Browser, terminal, web, delegate, MCP | Evidence gathering |
| `cron/` | Scheduled jobs | Watchlists, re-audits |
| `batch_runner.py` / trajectories | Datagen for tool-calling models | Feed Propercode LoRA pipeline |
| `providers/` + OpenAI-compatible `base_url` | Any model / local endpoints | Point at Ollama UL judge / custom GGUF serve |

Design doctrine (from upstream `AGENTS.md`): **narrow core, capability at the edges** (skills/plugins). That matches UL: Law lives in dictionary + skills; the harness should not invent statute.

---

## What Propercode Already Is

Propercode Toolbox is **not in this git workspace**. What we know from this repo’s own docs (`research/building-the-judge.md`, training scripts, dialogues):

| Piece | Propercode today | Notes |
|-------|------------------|-------|
| Language / runtime | VB.NET + ILGPU on Windows | Single auditable binary culture |
| Command model | **Spells**: `PropercodeWorker.exe "spellType…(args)"` | Train, merge LoRA, chat |
| Model training | Custom LoRA GPU trainer (`TransformerLoRAGPU.vb`, etc.) | Qwen3-4B-Base → UL judge v5 |
| Inference | Native GPU chat + Ollama GGUF | Judge Modelfile, temp 0.3 |
| Hardware | `butter.propercode.co.uk` RTX 5090 | Dialogues + training |
| Paths | `C:/data/devops.propercode.co.uk/…` | ultimatelaw + toolbox side by side |
| Product shape | Enterprise automation platform | Broader than “chat agent” |

So Propercode is the **forge** (train/serve/judge model + automation spells). Hermes/Dike is a candidate **field agent** (persistent memory, skills, messaging, tools).

They are complementary, not duplicates — unless we force one to eat the other.

---

## Integration Map (Propercode ↔ Dike)

```
                    ┌─────────────────────────┐
                    │  Themis (Dictionary)    │
                    │  AGENTS.md / .txt       │
                    └───────────┬─────────────┘
                                │ Law (read-only constitution)
          ┌─────────────────────┼─────────────────────┐
          ▼                     ▼                     ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ Propercode       │  │ Dike (Hermes     │  │ Prosecution      │
│ Toolbox          │  │  fork)           │  │ Framework        │
│                  │  │                  │  │                  │
│ • LoRA train     │─▶│ • skills = cases │◀─│ • methodology    │
│ • GGUF merge     │  │ • memory =       │  │ • case archive   │
│ • spell runner   │  │   precedent FTS  │  │ • falsifiability │
│ • GPU chat       │  │ • gateway filing │  │                  │
│ • Ollama serve   │◀─│ • model.base_url │  │                  │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

### Natural seams

1. **Model:** Dike `model.base_url` → Ollama / OpenAI-compatible endpoint serving `ultimatelaw-judge-v5` (or Propercode native serve wrapped as HTTP).
2. **Constitution:** Ship dictionary as always-loaded context / skill bundle `themis/` (definitions + Ultimate Law system prompt). Skills must cite terms; Challenger skill falsifies charges.
3. **Spells ↔ tools:** Expose hot Propercode spells as Dike tools or MCP (`train`, `merge_lora`, `judge_chat`) so the field agent can request forge work without becoming the trainer.
4. **Trajectories:** Hermes batch/trajectory output → Propercode Stage-2 ChatML (negative examples, tool-use cases) for the next judge LoRA.
5. **Cases:** `prosecution-framework/cases/*.md` → Dike skills + MEMORY/precedent corpus.

### What not to merge blindly

| Temptation | Problem |
|------------|---------|
| Rewrite Propercode in Python inside Hermes | Throws away ILGPU/VB audit story and spell UX |
| Run Dike as singleton “platform police” | Violates Perimeter / competing providers |
| Let skill learning rewrite Law | Skills may improve *procedure*; dictionary changes only via falsification |
| Swallow Hermes whole as product UI | 15k-line `cli.py`, desktop, billing — fork surface area is huge |

---

## Fork Strategy

**Recommended:** thin fork / overlay, not a forever megafork of all Hermes product chrome.

1. **Upstream remote** `nous` — periodic rebase/cherry-pick of agent waist + skills/memory.
2. **Overlay package** `dike/` (or rename binary `dike`):
   - Default system Law = Ultimate Law + dictionary path
   - Bundled skills: `investigate`, `prosecute`, `judge`, `challenge` (falsify)
   - Default model profile → local judge endpoint
   - Strip or disable skill hub defaults that smuggle unfalsifiable “safety policy” as higher than Law
3. **Propercode bridge** (VB or thin HTTP): spell gateway for train/serve; Dike never owns VRAM training.
4. **Multi-provider:** many Dike instances (reputation, not IOU monopoly) — matches economy sim findings.

**Alternative:** don’t fork the repo at all — run stock Hermes with UL skills + local model. Fork only when branding, defaults, and Law-binding must be non-optional.

Given “UL branch fork,” proceed with named fork **dike-agent**, keep Propercode as forge.

---

## Gap Analysis (this workspace)

| Need | Status |
|------|--------|
| Hermes source at known SHA | Done (`vendor/hermes-agent`) |
| Propercode Toolbox source tree | **Missing here** — analyze next on `devops.propercode.co.uk` / private repo |
| Spell inventory export | Needed: list `spellType*` AI/automation spells for MCP mapping |
| Judge HTTP serve contract | Confirm Ollama vs native VB OpenAI-compatible wrapper |
| Dictionary skill bundle | Not yet packaged for agentskills.io layout |
| Competing-judge eval harness | Exists as batteries in `building-the-judge.md`; not wired to Hermes yet |

---

## First Milestones (technical)

1. **Package `themis` skill** — core dictionary + judgment schema (victim, causation, definition cites, proportion, falsifiability clause).
2. **Wire local judge** — Dike → Ollama `ultimatelaw-judge-v5` (or Propercode HTTP).
3. **Port 1–2 prosecutions** as skills (`kingmolt`, template) with Challenger twin.
4. **Spell bridge spike** — one Propercode spell callable from Dike (e.g. `judge_chat` or `merge_lora` status).
5. **Only then** rename/rebrand fork surface (`dike` CLI) and cut public repo.

---

## Verdict

- **Name:** Dike (agent) under Themis (Law).
- **Hermes:** right substrate for persistent nomocratic agent (memory, skills, gateways, local models).
- **Propercode:** keep as the VB.NET forge and spell OS; do not replace with Hermes.
- **Join point:** OpenAI-compatible model endpoint + skills/constitution + optional spell MCP.
- **Blocker for deeper Propercode analysis:** toolbox source not mounted in this environment — next pass should open the EDIManager / PropercodeWorker tree and map spells 1:1 to Dike tools.
