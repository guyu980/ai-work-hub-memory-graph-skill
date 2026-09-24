---
name: ai-work-hub-memory-graph
description: Analyze and preserve non-project expert interviews, public conversations and thematic sources; recall prior projects, sector and technical views, valuations and important people before a decision. Maintain private, structured investment memory across diligence, research and authorized intelligence tasks. Persist reusable sources unless saving is excluded; formal deep research requires an explicit request.
---

# AI Work Hub Memory Graph

## Contract

This is a continuous private decision-memory workflow, not a second document archive. Go deep on important mechanisms and opposing explanations; keep routine handling small. Attributed company or expert inputs are usable without independently proving every claim. Investigate gaps only when they can change a conclusion or useful action.

- Project folders own company materials and the one running judgment; project state owns the machine-readable decision.
- `知识来源/` owns reusable non-project source analysis. Preserve it by default, even for “看看/总结”, unless the user excludes saving or the content is disposable.
- Formal research and intelligence archives keep their full reports; graph Markdown keeps reusable synthesis.
- Update existing objects. Rewrite current understanding when it changes; do not only append dated paragraphs.
- JSONL indexes are generated caches, never hand-edited. No new database, Evidence Ledger, thesis ledger or source-card layer.
- Automation can flag project impact and reassessment signals, not silently change formal investment status, participation, price or confidence.
- Public Skill files contain generic mechanisms only. Real projects, graph data, personal taxonomy/watchlists and credentials remain private.

Read `references/schema.md` when writing graph objects or changing their structure. Read other references only for the relevant source/workflow.

## Route The Input

| Input / increment | Owner |
| --- | --- |
| One company's BP, datapack or diligence interview | `ai-work-hub-diligence`; `项目/<name>/` |
| Non-project expert interview, podcast or thematic material | This Skill; one source under `知识来源/` |
| Explicit formal/systematic research request | `ai-work-hub-deep-research`; report plus selected graph deltas |
| Known-project public news | Its card's dated external signal, with affected assumption and possible reassessment |
| Cross-company market/value-capture view | Existing sector map |
| Mechanism, technical route, bottleneck or economics | Existing technical theme |
| Useful comparable price | Existing valuation page, using the shared observation columns |
| Durable standalone external change | Event card only when its independent value warrants one |
| Independently important founder/scientist/operator | Person card, not a team roster or CRM |
| Duplicate or low-value detail | Original report/source only |

A source can merit a substantive core note without producing any graph change. Important information has no fixed count cap. Use the existing small review note only when an important signal genuinely has no safe destination, not as a default news queue.

Fund operations, deal execution and post-investment tasks keep their task-specific source files; do not restart BP screening or copy their entire workpapers into a company card. Shared organizational deployments have separate authorization boundaries: a private graph match is not permission to publish it.

## Source Analysis

Read `references/knowledge-sources.md` for source layout, Feishu handling and core-note expectations.

1. Confirm the workspace on first use if unknown, then determine source ownership and deduplicate the conversation across platforms.
2. Preserve the original file/link once. For Feishu, find original text/transcript and relevant nested links; smart minutes are navigation. State unavailable content rather than implying a full reading.
3. Read useful prior knowledge before final analysis. Explain what this source reinforces, revises or contradicts.
4. Maintain one evolving core note: clear content or Q&A, important takeaways, mechanisms, opposing interpretations, source boundaries, relevant connections and worthwhile follow-ups.
5. Do bounded public checks when they materially help. Do not escalate one interview into formal Deep Research or a company audit.
6. Route durable increments to existing objects and link the source note. Record the actual writeback or explicitly state that no graph delta was material.

Source labels belong near meaningful facts. A transcript confirms what was said, not that the underlying claim is true. Do not duplicate the same subject under separate source-tier sections merely to satisfy a checklist.

## Public Discovery

Read `references/public-interviews.md` for interviews, podcasts, talks and authorized discovery.

Reuse existing intelligence tasks; this Skill does not schedule itself. Discover through substantive people, current questions and useful channels. For proactive selection, prioritize firsthand contribution, industry/research standing and depth of reasoning; popularity or a desire to fill a quota is insufficient. This filter does not reject material the user explicitly asks to analyze.

Screen cheaply, then read worthwhile original content and preserve one core note. Keep access/transcription limits explicit. Reports carry discoveries; only reusable changes enter the graph. Personal watchlists and editorial priorities are private and customizable.

## Retrieve Before Judging

1. Query the actual question using company aliases, technical route, customer budget, business model or valuation terms, not just a broad sector name.
2. Retrieve a small combined result set, then read the best sources. The helper covers fresh card text, source notes, research, running judgments and structured GitHub radar candidates, plus bounded one-hop neighbors.
3. State useful analogy, counterexample, mechanism or price anchor and its limits. Links establish relevance, not independent evidence.
4. Check as-of dates. Historical facts do not become current because a file was reorganized. Reformulate weak lexical queries or do targeted full-text search; an empty result does not prove absence.
5. Do not rebuild for a read-only question or scan the whole workspace routinely.

```bash
python3 <skill_dir>/scripts/retrieve_memory.py \
  --workspace-root "<root>" --query "<decision-relevant terms>" --limit 8
```

The limit applies across direct results; neighbors are separately bounded. Output is temporary query material, not a new knowledge store.

## Same-Type Structure

Keep six object layers: `01_项目卡片`, `02_赛道地图`, `03_技术主题`, `04_估值锚点`, `05_事件卡片`, `06_人物卡片`.

- Project: business positioning, compact current projection, decisive variables, reusable lesson, relevant connections and next signals. Link the running judgment for transaction detail.
- Sector: value capture and subdirection comparison; link representative projects without duplicating current project decisions.
- Theme: core question, mechanisms/routes, supporting and contrary material, economic meaning and new signals.
- Valuation: common columns for object/date/round/price basis/financing/operating denominator/comparability/source; equity, M&A/licensing and debt are separate.
- Event: current state and durable effect, a few meaningful turning points if needed; not a daily log.
- Person: current identity, key work and important views with project/theme/source links; not every meeting participant.

Use explicit knowledge-as-of metadata for non-project objects and ordinary Markdown links. Preserve filename stability. Omit empty sections; no arbitrary length cap on important reasoning. Full templates and compatibility rules are in `references/schema.md`.

Routine prices from BPs, interviews or datapacks need attribution, not agreements or payment checks. Missing fields stay unknown. Investigate only when a specific uncertainty affects the actual decision, holding, return math or transaction risk.

## Write Back

For diligence, finalize the single project judgment/state first. Update the card's substance from it, including contradictory old prose; a refreshed header/hash does not establish semantic freshness. Keep latest fund/legal tasks separate from company positioning.

For reports, finish and archive the report first, then route only consequential increments. A changed assumption belongs in the current synthesis, not another news paragraph. For known projects, explain the impact and whether focused reassessment is worthwhile. Do not invent a task for every risk or silently modify formal decisions.

For all graph writers:

1. Refresh project headers from finalized state with `sync_project.py --skip-rebuild` when necessary.
2. Read affected files after any sync and capture their hashes with `write_graph.py --snapshot`.
3. Prepare the final Markdown outside active graph folders. Use the plan format in `references/schema.md`.
4. Apply the batch through `write_graph.py --plan`. It uses a short shared lock, rejects stale hashes and rebuilds indexes once; conflicts require rereading and merging both changes.
5. Validate after actual writes and read back affected current-view sections. Report precise failures; do not claim a successful write merely from a plan or hash.

Research and report preparation can remain parallel. The lock only covers shared writes. Scripts use POSIX file locking (macOS/Linux); do not claim cross-process protection for a writer that bypasses the entry point.

## Commands

```bash
python3 <skill_dir>/scripts/init_memory_graph.py --workspace-root "<root>"
python3 <skill_dir>/scripts/init_knowledge_source.py --workspace-root "<root>" --init-only
python3 <skill_dir>/scripts/init_knowledge_source.py --workspace-root "<root>" \
  --kind expert-interview --date YYYY-MM-DD --name "<expert>" --topic "<topic>"
python3 <skill_dir>/scripts/sync_project.py --workspace-root "<root>" --state "<state.json>" --skip-rebuild
python3 <skill_dir>/scripts/write_graph.py --workspace-root "<root>" --plan "<private-plan.json>"
python3 <skill_dir>/scripts/validate_memory_graph.py --workspace-root "<root>"
```

Use `--kind thematic-material` for thematic sources. Standalone `rebuild_indexes.py` repairs generated caches after maintenance; legacy `migrate_memory_graph_v2.py` normalizes old directories, not prose quality.

## Completion

Confirm source coverage, a single durable owner, coherent current understanding, meaningful links and dates, preserved formal decisions, successful changed-batch validation/readback, and privacy. No useful follow-up or no graph delta is a valid result.
