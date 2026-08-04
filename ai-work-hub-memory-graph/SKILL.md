---
name: ai-work-hub-memory-graph
description: Use when the user wants AI Work Hub to connect a live or historical project, BP, Feishu note, transcript, datapack, news item, financing event, GitHub project, technical topic, sector question, or valuation question to prior projects and durable investment knowledge. Initializes, retrieves from, synchronizes, validates, and maintains a sparse private Memory Graph of project cards, sector and technical views, valuation references, thesis entries, high-signal people, and genuinely important events. Also post-processes recurring reports without copying high-frequency low-value content. Organization Context Registries and portable Context Packages are optional advanced modes.
---

# AI Work Hub Memory Graph

## Core Contract

Treat the Memory Graph as the cross-project investment decision-memory layer for AI Work Hub. It is not a replacement for full project folders or daily/weekly reports. Store what the user currently believes, why, and what would change the view. Do not store every update merely because it happened.

Keep the skill public and reusable, but keep generated knowledge private or inside an authorized organization environment. Do not commit project cards, event cards, sector views, valuation anchors, deal notes, Feishu exports, or any private investment judgment to a public repo.

Default private knowledge base path:

```text
<workspace_root>/Memory Graph/
```

If the workspace root is unclear, ask one short question before writing. If the user explicitly requests chat-only work, do not create or update files.

Use local storage by default. Reading a Feishu/Lark link is source intake, not a
storage-profile switch. Only activate a Feishu Context Registry, hybrid sync,
or portable Context Package when the user explicitly requests organization
deployment, migration, cross-runtime handoff, or a bridge; then read
`references/advanced-deployment.md`.

## Initialize Local Profile

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
  08_人物卡片/
  待复核.md
  .system/
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
2. Build a bounded local context pack with `scripts/build_context_pack.py`. Retrieval is a shortlist, not evidence. If advanced organization deployment was explicitly activated, follow `references/advanced-deployment.md` instead.
3. Identify similar projects, useful counterexamples, valuation anchors, related technical themes, and active thesis entries.
4. Add a concise `Memory Graph 联想` section to the answer or running project memo:
   - 最相似的已看项目
   - 最有参考价值的反例
   - 相关赛道/技术观点
   - 可比估值锚点
   - 关键人物/团队 lineage
   - 这个项目必须证明的差异点

After the project view is formed or updated:

1. Create or update the project state and focused evidence ledger according to the companion diligence skill's evidence contract.
2. Create or update one project card in `01_项目卡片/`.
3. If the source includes a useful financing or transaction reference, apply `Valuation Capture` below without defaulting to agreement or closing verification.
4. Run `scripts/sync_project.py` or `scripts/rebuild_indexes.py`; never hand-append generated index records.
5. Add or update key people only when they meet the higher industry-standing threshold.
6. Apply clear reusable changes directly to the existing sector map, technical theme, valuation reference, thesis entry, person card, or major-event card. If no safe destination exists and the signal is important enough to revisit, add one concise line to the single `待复核.md`; do not create per-input proposal files.
7. Keep passed or archived projects when they are useful comparables or counterexamples.
8. Skip very low-quality projects that add no reusable learning.
9. When public news or an external report directly affects an existing project, append a dated, sourced note under that project card's `外部动态`. The automation may state a possible positive, negative, or neutral effect, but must not silently rewrite the project's formal investment decision.

Use the user's source material and local aliases to determine canonical project names. Do not introduce alternate names unless a source requires alias tracking.

Historical invested/pass reviews use the same project-card and relation
contracts. Retrieve them normally, retain their immutable
`historical_outcome`, and let current decision fields change if follow-up
reopens the project. Historical passes are often valuable counterexamples; do
not delete them merely because they are archived.

## Valuation Capture

Treat market price evidence and investment judgment as separate layers. Store a
valuation only when it is a useful comparable or affects price discipline.

The default record is intentionally light:

- project, date, round or operating stage;
- stated pre-money or post-money valuation when known;
- financing amount and currency when known;
- source context and source reference;
- relevant operating maturity or metric denominator when available;
- a short note explaining why it is or is not comparable.

Do not require agreements, payment proof,工商 changes, or exact closing status
for routine BP, interview, datapack, news, or radar intake. Add transaction
status, special rights, secondary components, or closing detail only when they
change ownership, portfolio marking, return math, closing risk, legal rights,
source conflict, or an active investment decision.

Always keep company/source-stated market prices separate from the internal
fair-value range. Preserve conflicting sources instead of forcing one number.

## Daily And Weekly Report Post-Processing

After the `AI科技与宏观事件日报/周报` workflow generates and archives a report, run a selective Memory Graph pass. Do not impose a fixed maximum on how many insights a report may contribute; use materiality and reuse value instead:

1. Read the finalized local report body, not just the chat summary.
2. Extract only changes that improve a later project judgment, sector or technical view, valuation comparison, person assessment, or durable thesis.
3. Update the most direct existing destination. Create an event card only when the event is independently important and durable, not when it is merely a project operating update or another copy of a financing item.
4. Rebuild generated indexes after Markdown updates; never hand-edit JSONL.
5. If a report introduces a founder, scientist, professor, open-source maintainer, or technical/product leader with clear industry standing, update the people index or person card. Do this only when the person is likely to matter for future project comparison; ordinary financing founders stay in the report archive and project/event card.
6. Capture meaningful valuation references with their source context and comparability note. Do not perform transaction-document verification unless the deeper status is decision-sensitive.
7. Update relevant sector maps, technical themes, valuation anchors, or thesis entries only when there is real incremental learning.

When public news directly affects an existing project, append a dated and sourced
`外部动态` note to that project card. State the possible effect, but do not
silently change formal investment-decision fields; the next diligence update
performs the re-rating when warranted. No separate review-queue file is needed
for ordinary news.

Do not save the full daily/weekly report inside Memory Graph. Do not convert every news item into an event card. Low-signal news should remain only in the daily/weekly archive.

## GitHub Radar Post-Processing

For GitHub global project radar outputs, use the same materiality-based pattern.
There is no fixed cap on Memory Graph updates, and a GitHub development may be
an event when it independently changes technical or investment understanding:

1. Treat each truly high-value repo as an event card, project card, sector update, or technical-theme update depending on what it teaches.
2. Separate heat from durable technical signal.
3. When reliable, capture only industry-significant maintainers, founders, scientists, or lab leads as people-index entries; if uncertain, write `不明确` in the radar report rather than creating a pending people entry from names, language, or weak affiliation.
4. Prefer updating existing technical themes and sector maps over creating thin duplicate cards, while allowing any number of genuinely material updates.

## Event Threshold

Create an event card only when the event has durable standalone value and
changes at least one of:

- a sector or technical view;
- a reusable valuation reference;
- the priority or interpretation of one or more active projects; or
- an investment thesis that will matter in future retrieval.

A project datapack, quarterly update, customer interview, or cash-conversion
change belongs in the project judgment and project card. Promote it to a sector
or thesis update only when it supports a reusable cross-project pattern. There
is no numeric event quota; the test is whether the card will still help a future
decision after the underlying report is forgotten.

## Advanced Deployment

Read `references/advanced-deployment.md` only when the user explicitly requests
canonical Feishu/Lark storage, local/organization synchronization, Context
Registry export, cross-runtime handoff, migration, or a bridge. Ordinary local
retrieval and Feishu-link reading do not require a storage profile or Context
Package.

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

1. Confirm private graph artifacts were written only under the user's workspace or authorized organization environment, not the public skill repo.
2. Confirm skill files and templates do not contain private project materials.
3. Confirm project cards use one primary sector from the taxonomy.
4. Confirm indexes use JSONL with one valid JSON object per line.
5. Confirm low-value projects and high-frequency project updates are not over-preserved as standalone graph objects.
6. Confirm recurring-report post-processing used materiality rather than a fixed quota and updated the most direct destination.
7. Confirm people cards contain no private contact information and distinguish verified facts from source claims and pending identity checks.
8. Rebuild all JSONL indexes and run `scripts/validate_memory_graph.py`; keep successful sync metadata only in `.system/last-sync.json`.
9. Confirm structured decision, play, sizing, and price fields are separate.
10. Confirm unresolved relation targets are typed `external_entity`, not silently treated as projects.
11. Confirm useful valuation references preserve source context and remain separate from internal fair value without unnecessary closing verification.
12. Confirm public news affecting an existing project appears as a sourced `外部动态` and did not silently overwrite formal decision fields.
13. Confirm advanced deployment was activated only by an explicit request and then followed `references/advanced-deployment.md`.
