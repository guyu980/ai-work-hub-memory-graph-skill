# AI Work Hub Memory Graph

[中文说明](README.zh-CN.md)

A Codex skill for building private, durable investment memory. It accepts project inputs and reusable non-project expert interviews or thematic materials, then connects diligence, recurring AI intelligence, GitHub radar, sector research, technical themes, valuation evidence, important events, and high-signal people without turning the graph into a second document archive.

## What It Solves

When a new project or news item arrives, the workflow can recall:

- similar projects and counterexamples;
- current sector understanding;
- relevant technical mechanisms and proof standards;
- valuation references and price discipline;
- durable external changes;
- people with reusable industry or technical significance.

It then writes only the new knowledge that will improve a later decision.

## Knowledge Model

```text
Project files / non-project knowledge sources
  -> project state / one core source note
  -> compressed Markdown knowledge objects
  -> generated JSONL retrieval indexes
```

Non-project sources live in a sibling source layer:

```text
知识来源/
  专家访谈/YYYY/YYYY-MM-DD_Expert_Topic/
  主题资料/YYYY/YYYY-MM-DD_Source_Topic/
  templates/核心整理模板.md
```

`知识来源/` is not a new graph-card layer and has no generated source index.

Active layout:

```text
Memory Graph/
  00_索引/
  01_项目卡片/
  02_赛道地图/
  03_技术主题/
  04_估值锚点/
  05_事件卡片/
  06_人物卡片/
  待复核.md
  .system/
  config/
  templates/
```

There is no separate thesis ledger. Reusable views live in the sector, technical, valuation, project, or workflow-rule object where they will be retrieved.

The sector taxonomy is user-configurable. The skill's defaults are examples, not mandatory classifications.

## Routing Rules

| New information | Store it in |
| --- | --- |
| One company's current view or evidence | Project folder and project card |
| Reusable expert interview or thematic material not owned by one company | One source folder under `知识来源/` |
| Formal systematic thematic report | `行业研究/<主题>/`, with only reusable increments written to the graph |
| Public news about a known project | Its dated `外部动态` entry |
| Cross-company market pattern | Sector map |
| Technical route, bottleneck, or validation method | Technical theme |
| Useful market or financing price | Valuation anchor |
| Durable standalone external change | Event card |
| Independently important person | People card |
| Important but unresolved destination | One `待复核.md` entry |
| Duplicate or low-signal detail | Source/report archive only |

## Install From GitHub

```bash
mkdir -p ~/Documents/skills-repos ~/.codex/skills
cd ~/Documents/skills-repos
git clone https://github.com/guyu980/ai-work-hub-memory-graph-skill.git
ln -s "$(pwd)/ai-work-hub-memory-graph-skill/ai-work-hub-memory-graph" \
  ~/.codex/skills/ai-work-hub-memory-graph
```

Initialize a private graph:

```bash
python3 ai-work-hub-memory-graph-skill/ai-work-hub-memory-graph/scripts/init_memory_graph.py \
  --workspace-root "$HOME/Documents/AI Work Hub"
```

Initialize the non-project source layer:

```bash
python3 ai-work-hub-memory-graph-skill/ai-work-hub-memory-graph/scripts/init_knowledge_source.py \
  --workspace-root "$HOME/Documents/AI Work Hub" \
  --init-only
```

Create an expert-interview source:

```bash
python3 ai-work-hub-memory-graph-skill/ai-work-hub-memory-graph/scripts/init_knowledge_source.py \
  --workspace-root "$HOME/Documents/AI Work Hub" \
  --kind expert-interview \
  --date YYYY-MM-DD \
  --name "Expert name" \
  --topic "Interview topic"
```

Update the installed skill later with:

```bash
cd ~/Documents/skills-repos/ai-work-hub-memory-graph-skill
git pull --ff-only
```

The generated `Memory Graph/` is private workspace data and must not be pushed to this public repository.

## Use It

```text
Use $ai-work-hub-memory-graph to connect this project to prior projects, sector and technical views, and valuation anchors before updating the graph.
```

For recurring intelligence:

```text
Use $ai-work-hub-memory-graph after this report is archived. Keep low-signal items in the report and route only durable increments to the most direct graph object.
```

## Core Commands

Retrieve compact ranked matches:

```bash
python3 ai-work-hub-memory-graph/scripts/retrieve_memory.py \
  --workspace-root "$HOME/Documents/AI Work Hub" \
  --query "company sector technology business model"
```

Rebuild and validate:

```bash
python3 ai-work-hub-memory-graph/scripts/rebuild_indexes.py \
  --workspace-root "$HOME/Documents/AI Work Hub"
python3 ai-work-hub-memory-graph/scripts/validate_memory_graph.py \
  --workspace-root "$HOME/Documents/AI Work Hub"
```

Normalize an older v2 graph:

```bash
python3 ai-work-hub-memory-graph/scripts/migrate_memory_graph_v2.py \
  --workspace-root "$HOME/Documents/AI Work Hub"
```

## Integration

This skill is the default intake for non-project sources and owns lightweight source analysis and routing. The companion [AI Work Hub Diligence](https://github.com/guyu980/ai-work-hub-diligence-skill) skill takes over only when a source changes a specific project judgment. [AI Work Hub Deep Research](https://github.com/guyu980/ai-work-hub-deep-research-skill) takes over when external validation or systematic research is needed.

Daily/weekly intelligence and GitHub radar can also use the graph after their reports are complete. There is no fixed write quota: low-signal items stay in the archive, while every material increment is routed to the most direct existing object.

Automations may append sourced external news to project cards, but they must not silently change the formal investment decision, participation, position, price view, or confidence.

`sync_project.py` creates the first project card when needed and rejects duplicate cards.

## Repository Boundary

This public repository contains workflow instructions, scripts, templates, and schemas only. Never commit real project cards, source materials, private judgments, Feishu tokens, or generated indexes from a live workspace.

Contributions should arrive through pull requests. Repository owners review and merge them.

License: [MIT](LICENSE)
