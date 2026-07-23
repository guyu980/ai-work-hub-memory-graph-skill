---
name: ai-work-hub-memory-graph
description: Use when the user wants AI Work Hub to connect a new project, BP, Feishu note, transcript, datapack, news item, financing event, GitHub project, technical topic, sector question, or valuation question to prior projects, sector maps, technical themes, valuation anchors, and a running investment thesis. Also use to initialize or maintain the local private Memory Graph knowledge base, create project/event cards, update sector or technical views, or run post-processing after the AI科技与宏观事件日报/周报 or ai-work-hub-diligence workflows.
---

# AI Work Hub Memory Graph

## Core Contract

Treat the Memory Graph as the cross-project investment knowledge layer for AI Work Hub. It is not a replacement for project folders or daily/weekly reports. It stores compressed, structured knowledge so new projects, news, technology directions, and valuations can be compared against prior work.

Keep the skill public and reusable, but keep the generated knowledge base local and private. Do not commit project cards, event cards, sector views, valuation anchors, deal notes, Feishu exports, or any private investment judgment to a public repo.

Default private knowledge base path:

```text
<workspace_root>/Memory Graph/
```

If the workspace root is unclear, ask one short question before writing. If the user explicitly requests chat-only work, do not create or update files.

## Initialize

When the user asks to create or prepare the Memory Graph, run:

```bash
python3 <skill_dir>/scripts/init_memory_graph.py --workspace-root "<workspace_root>"
```

The script creates the directory layout, index files, sector maps, valuation files, and templates without overwriting existing files.

Use this layout:

```text
Memory Graph/
  README.md
  00_索引/
    项目索引.jsonl
    事件索引.jsonl
    人物索引.jsonl
    观点索引.jsonl
    估值索引.jsonl
  01_项目卡片/
  02_赛道地图/
  03_技术主题/
  04_估值锚点/
  05_观点账本/
  06_事件卡片/
  07_周度沉淀/
  templates/
```

Read `references/schema.md` before creating or updating cards, indexes, sector views, valuation anchors, or thesis entries.

## Taxonomy

Treat taxonomy as user-configurable. The initialization script creates a useful default set of sector maps, but users may rename, add, remove, or merge sectors. Do not force the default taxonomy if the user's workspace already has a custom `Memory Graph/02_赛道地图/` structure.

When classifying a new item:

- Prefer the user's existing sector map over the default categories.
- Use one primary sector and any number of tags.
- If a project naturally crosses sectors, choose the sector that best matches the investment comparison set, then capture the rest as tags.
- If no existing category fits, create a new sector file or ask the user whether to add one.
- Keep classification useful for future comparison, not taxonomic perfection.

## Project Intake Workflow

Use this workflow before and after `ai-work-hub-diligence` or any project review.

Before judging a new project:

1. Extract the project name, sector, technical route, business model, customer type, stage, valuation, founder/team entities, and source date from the material.
2. Search `Memory Graph/00_索引/` and relevant `02_赛道地图/`, `03_技术主题/`, and `04_估值锚点/` files.
3. Identify similar projects, useful counterexamples, valuation anchors, related technical themes, and active thesis entries.
4. Add a concise `Memory Graph 联想` section to the answer or running project memo:
   - 最相似的已看项目
   - 最有参考价值的反例
   - 相关赛道/技术观点
   - 可比估值锚点
   - 这个项目必须证明的差异点

After the project view is formed or updated:

1. Create or update one project card in `01_项目卡片/`.
2. Append or update one line in `00_索引/项目索引.jsonl`.
3. Update sector maps, technical theme files, valuation anchors, or thesis entries only when the new evidence changes reusable knowledge.
4. Keep passed or archived projects in the Memory Graph if they are useful future comparables or counterexamples.
5. Skip very low-quality projects that add no reusable learning; record a generic thesis note instead only if it sharpens a pattern.

Use the user's source material and local aliases to determine canonical project names. Do not introduce alternate names unless a source requires alias tracking.

## Daily And Weekly Report Post-Processing

After the `AI科技与宏观事件日报/周报` workflow generates and archives a report, run a light Memory Graph pass:

1. Read the finalized local report body, not just the chat summary.
2. Extract only high-signal events that may affect investment judgment, valuation anchors, sector direction, technical direction, or watchlist priorities.
3. Create event cards in `06_事件卡片/` for those events.
4. Append one JSONL line per event to `00_索引/事件索引.jsonl`.
5. Update relevant sector maps, technical themes, valuation anchors, or thesis entries only when there is real incremental learning.

Do not save the full daily/weekly report inside Memory Graph. Do not convert every news item into an event card. Low-signal news should remain only in the daily/weekly archive.

## GitHub Radar Post-Processing

For GitHub global project radar outputs, use the same post-processing pattern:

1. Treat each truly high-value repo as an event card, project card, or technical-theme update depending on what it teaches.
2. Separate heat from durable technical signal.
3. Prefer updating technical themes and sector maps over creating many thin project cards.

## Output Style

When answering the user, make Memory Graph output decision-useful:

- Lead with what prior knowledge it connects to.
- Distinguish confirmed facts, company/source claims, and current interpretation.
- Keep cross-project linkage short enough to be read inside a diligence answer.
- State when a new input changes the sector map or thesis ledger.
- Avoid generic industry summaries that do not change a judgment.

## Quality Checks

Before finishing:

1. Confirm private Memory Graph files were written only under the user's workspace, not the public skill repo.
2. Confirm skill files and templates do not contain private project materials.
3. Confirm project cards use one primary sector from the taxonomy.
4. Confirm indexes use JSONL with one valid JSON object per line.
5. Confirm low-value projects are not over-preserved.
6. Confirm daily/weekly post-processing extracted only high-signal events.
