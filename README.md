# AI Work Hub Memory Graph

[中文说明](README.zh-CN.md)

**Cross-project investment memory.** Connect diligence, interviews, public conversations, research and intelligence. Recall prior reasoning, then revise useful understanding instead of accumulating news.

## Install And Update

Ask Codex to install the Skill from this repository and inspect any existing installation first. A Git checkout plus one symlink keeps personal and shared versions on the same source:

```bash
mkdir -p ~/Documents/skills-repos ~/.codex/skills
cd ~/Documents/skills-repos
git clone https://github.com/guyu980/ai-work-hub-memory-graph-skill.git
ln -s "$(pwd)/ai-work-hub-memory-graph-skill/ai-work-hub-memory-graph" ~/.codex/skills/ai-work-hub-memory-graph
```

Inspect an existing destination instead of overwriting it or creating duplicate Skills. Python scripts require Python 3.10+; Graph locking supports macOS/Linux. Reload Codex after installation. To update:

```bash
cd ~/Documents/skills-repos/ai-work-hub-memory-graph-skill
git pull --ff-only
```

The symlink uses the updated source directly. Keep the private workspace separate.

## Daily Use

```text
Use $ai-work-hub-memory-graph to preserve and analyze this expert interview, connecting it to prior work.
Which earlier projects, mechanisms and prices are relevant to this new opportunity?
Absorb meaningful changes from these archived reports into existing sector and technical views.
```

Confirm an unknown private workspace path once. Reusable sources are saved under `知识来源/` with one evolving core note unless saving is excluded.

Six object layers hold projects, sectors, technical themes, valuation anchors, durable events and independently important people. Full sources/reports stay with their owners; formal company decisions stay in project judgments/state. Merge changes by assumption and retain meaningful evidence/turning points rather than a daily chronology. Taxonomy and watchlists are customizable.

Retrieval includes fresh Graph text, source notes, research, running judgments, radar candidates and existing cross-task sourcing reviews. Dates expose their basis; similar research versions retain snapshot links. Matches are relevance, not independent evidence.

```bash
python3 ai-work-hub-memory-graph/scripts/init_memory_graph.py --workspace-root "<private-root>"
python3 ai-work-hub-memory-graph/scripts/retrieve_memory.py --workspace-root "<private-root>" --query "<specific question>"
```

Initialize only when absent. Shared writes use expected hashes and a short lock; reread/merge conflicts and validate actual changes. Automation flags project impact without silently changing investment decisions or manufacturing follow-up queues.

## How The Skills Connect

[Diligence](https://github.com/guyu980/ai-work-hub-diligence-skill) owns current company decisions; [Memory Graph](https://github.com/guyu980/ai-work-hub-memory-graph-skill) owns non-project sources and cross-project synthesis; [Deep Research](https://github.com/guyu980/ai-work-hub-deep-research-skill) owns explicitly requested formal studies. Companions are optional and installable separately. Authorized intelligence tasks discover; Skills do not schedule themselves.

This repository contains generic mechanisms, scripts and fictional examples only. Real projects, knowledge, reports, watchlists, delivery destinations and credentials remain private. Contribute via PR for maintainer review. Model selection belongs in runtime settings.

[Agent instructions](ai-work-hub-memory-graph/SKILL.md) · [MIT License](LICENSE)
