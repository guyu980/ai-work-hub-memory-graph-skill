---
name: ai-work-hub-memory-graph
description: Use when the user wants AI Work Hub to connect a live or historical invested/pass project, BP, Feishu note, transcript, datapack, news item, financing event, GitHub project, technical topic, sector question, or valuation question to prior projects, sector maps, technical themes, valuation anchors, and a running investment thesis. Also use to initialize, migrate, retrieve from, synchronize, validate, or maintain the local private Memory Graph; create project/event cards; update sector or technical views; or run post-processing after the AI科技与宏观事件日报/周报 or ai-work-hub-diligence workflows.
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
    关系索引.jsonl
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
  08_人物卡片/
  09_待确认更新/
  10_运行记录/
  config/
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

## People Layer

Use the people layer only for high-signal people with reusable industry, academic, technical, or operator standing. It is not a CRM, address book, contact database, or team roster.

Create or update people entries when a person materially affects investment judgment or cross-project recall, such as:

- founder, co-founder, CEO, or operator with clear public industry standing, prior company-building record, or repeated relevance across projects;
- professor, principal investigator, lab lead, scientist, or technical advisor whose research standing or technical lineage is central to the project;
- chief scientist, technical/product leader, open-source maintainer, or core research/engineering owner only when the person has independently meaningful public work, patents, papers, widely adopted repos, products, or prior operating outcomes;
- person whose academic/technical lineage, IP boundary, employment overlap, or prior startup history changes the risk view.

Do not create people entries for ordinary project founders, GTM leads, product managers, engineering leads, meeting attendees, sales contacts, customer interviewees, supplier contacts, junior employees, or investors unless the person is independently important beyond that one project. A named person in a BP is not enough. If the person matters only to one project's execution risk, keep the analysis inside that project card. Do not store private contact details, personal phone numbers, personal emails, addresses, ID numbers, or sensitive personal information. Keep the source tier explicit: public source, project material, Feishu transcript, interview note, or needs verification.

Default people workflow:

1. Keep team analysis inside the project card first, especially under `团队技术背景`.
2. Add or update `00_索引/人物索引.jsonl` only for people who meet the higher industry-standing threshold.
3. Create a Markdown person card under `08_人物卡片/` only when the person is likely to be reused as a future comparable, technical-lineage signal, or risk signal beyond one project.
4. Link people cards back to project cards, sector maps, technical themes, event cards, and thesis entries only when the connection changes judgment.
5. If identity is incomplete, do not create a pending person entry unless the role itself is clearly industry-significant. For ordinary unverified team members, leave the note in the project card.

## Project Intake Workflow

Use this workflow before and after `ai-work-hub-diligence` or any project review.

Before judging a new project:

1. Extract the project name, sector, technical route, business model, customer type, stage, valuation, founder/team entities, and source date from the material.
2. Build a bounded context pack with `scripts/build_context_pack.py`, then read the returned source cards and relevant `02_赛道地图/`, `03_技术主题/`, `04_估值锚点/`, and `08_人物卡片/` files. Retrieval is a shortlist, not evidence.
3. Identify similar projects, useful counterexamples, valuation anchors, related technical themes, and active thesis entries.
4. Add a concise `Memory Graph 联想` section to the answer or running project memo:
   - 最相似的已看项目
   - 最有参考价值的反例
   - 相关赛道/技术观点
   - 可比估值锚点
   - 关键人物/团队 lineage
   - 这个项目必须证明的差异点

After the project view is formed or updated:

1. Create or update the project folder's state JSON and claim-level evidence ledger according to the companion diligence skill's evidence contract.
2. Create or update one project card in `01_项目卡片/`.
3. If the source includes a completed financing valuation, signed/in-closing price, current quote, next-round target, secondary transaction, or acquisition price, apply `Valuation Capture` below before finishing. Do not leave reusable price evidence only in the project card.
4. Run `scripts/sync_project.py` or `scripts/rebuild_indexes.py`; never hand-append generated index records.
5. Add or update key people only when they meet the higher industry-standing threshold.
6. Put thesis, sector, valuation, and external-event proposals in `09_待确认更新/` when the reusable change is ambiguous or no safe anchor destination is clear. Apply factual valuation observations directly when their destination and source tier are clear.
7. Keep passed or archived projects when they are useful comparables or counterexamples.
8. Skip very low-quality projects that add no reusable learning.

Use the user's source material and local aliases to determine canonical project names. Do not introduce alternate names unless a source requires alias tracking.

Historical invested/pass reviews use the same project-card and relation
contracts. Retrieve them normally, retain their immutable
`historical_outcome`, and let current decision fields change if follow-up
reopens the project. Historical passes are often valuable counterexamples; do
not delete them merely because they are archived.

## Valuation Capture

Treat market price evidence and investment judgment as separate layers. A valuation can be a useful market anchor even when the project is overpriced, paused, passed, or outside the fund's strategy.

Classify every financing or transaction price before deciding how to store it:

1. **Completed / funded / closed**: money has been invested or the transaction has closed. Add it to the relevant `04_估值锚点/` file by default when the project is a meaningful comparable. A public filing or announcement is strongest, but a private deal document that explicitly states `已交割` is still usable when labeled `材料已成交口径`.
2. **Signed / in closing**: a binding agreement, lead commitment, or signed term sheet exists but closing is incomplete. Keep it separate from completed rounds and state the remaining condition.
3. **In-market quote**: the company, founder, FA, or current round materials quote a pre-money or post-money valuation. Preserve it as a lower-weight market signal with source and date; never relabel it as completed.
4. **Next-round target / aspiration**: record only as a low-confidence financing expectation or sentiment signal.
5. **Our fair-value view**: state the comfortable range, price judgment, and required milestones separately. Never overwrite a market transaction with the internal fair value or use a transaction price as automatic proof of fairness.

For each reusable observation, capture as many of these fields as the source supports:

- project, date, round, transaction status;
- pre-money/post-money valuation, amount raised, currency;
- source tier and source reference;
- operating stage and the latest revenue/ARR/gross profit/profit/order metrics available at that time;
- implied multiples when decision-useful;
- unusual rights, strategic consideration, control premium, secondary component, or other terms that impair comparability.

Do not omit a completed valuation merely because operating data is incomplete. Store the price fact, mark the missing denominator, and avoid calculating unsupported multiples. When sources conflict, preserve the competing observations with their source tiers rather than silently choosing one.

Before finishing any project round, explicitly check:

```text
Valuation capture
- Completed/funded valuation found:
- Signed/in-closing price found:
- Current quote or next-round target found:
- Relevant valuation anchor updated or proposal queued:
- Market price and our fair-value view kept separate:
```

## Daily And Weekly Report Post-Processing

After the `AI科技与宏观事件日报/周报` workflow generates and archives a report, run a light Memory Graph pass:

1. Read the finalized local report body, not just the chat summary.
2. Extract only high-signal events that may affect investment judgment, valuation anchors, sector direction, technical direction, or watchlist priorities.
3. Create event cards in `06_事件卡片/` for those events.
4. Append one JSONL line per event to `00_索引/事件索引.jsonl`.
5. If a report introduces a founder, scientist, professor, open-source maintainer, or technical/product leader with clear industry standing, update the people index or person card. Do this only when the person is likely to matter for future project comparison; ordinary financing founders stay in the report archive and project/event card.
6. Capture completed financing valuations for meaningful comparables even when they do not change the investment thesis. Keep quotes and next-round targets as lower-weight observations.
7. Update relevant sector maps, technical themes, valuation anchors, or thesis entries only when there is real incremental learning.

Public news may add an `event_trigger` proposal, but it must not automatically
change a project's investment decision. Mark such triggers `needs_review`.

Do not save the full daily/weekly report inside Memory Graph. Do not convert every news item into an event card. Low-signal news should remain only in the daily/weekly archive.

## GitHub Radar Post-Processing

For GitHub global project radar outputs, use the same post-processing pattern:

1. Treat each truly high-value repo as an event card, project card, or technical-theme update depending on what it teaches.
2. Separate heat from durable technical signal.
3. When reliable, capture only industry-significant maintainers, founders, scientists, or lab leads as people-index entries; if uncertain, write `不明确` in the radar report rather than creating a pending people entry from names, language, or weak affiliation.
4. Prefer updating technical themes and sector maps over creating many thin project cards.

## Output Style

When answering the user, make Memory Graph output decision-useful:

- Lead with what prior knowledge it connects to.
- Distinguish confirmed facts, company/source claims, and current interpretation.
- Keep cross-project linkage short enough to be read inside a diligence answer.
- State when a new input changes the sector map or thesis ledger.
- State when a new input adds or changes a key-person signal.
- Avoid generic industry summaries that do not change a judgment.

## Quality Checks

Before finishing:

1. Confirm private Memory Graph files were written only under the user's workspace, not the public skill repo.
2. Confirm skill files and templates do not contain private project materials.
3. Confirm project cards use one primary sector from the taxonomy.
4. Confirm indexes use JSONL with one valid JSON object per line.
5. Confirm low-value projects are not over-preserved.
6. Confirm daily/weekly post-processing extracted only high-signal events.
7. Confirm people cards contain no private contact information and distinguish verified facts from source claims and pending identity checks.
8. Rebuild all JSONL indexes and run `scripts/validate_memory_graph.py`.
9. Confirm structured decision, play, sizing, and price fields are separate.
10. Confirm unresolved relation targets are typed `external_entity`, not silently treated as projects.
11. Confirm completed/funded valuations for meaningful comparables were added to the relevant valuation anchor or explicitly queued, even when the recommendation is `pause` or `pass`.
12. Confirm signed prices, current quotes, next-round targets, and internal fair-value ranges are labeled separately from completed transactions.
