# Memory Graph Content Contract

## Ownership

Project materials and the one running judgment own company detail; project state JSON owns the current machine-readable decision. Knowledge-source core notes own original non-project analysis. Research reports and intelligence archives own their full deliverables. Graph Markdown holds reusable synthesis, and JSONL files are rebuildable caches.

Keep the existing 01–06 folders. No parallel thesis ledger, Evidence Ledger, source-card layer or relationship database. Local taxonomy, names and investment preferences belong to private configuration, not this public Skill.

## Shared Conventions

- One object per subject and decision question. Reuse its filename; split only when questions have genuinely different mechanisms. Keep an old entry as a short linked overview when needed for compatibility.
- Non-project objects use `内容截至: YYYY-MM-DD`, optional aliases and tags. This is the newest information actually incorporated, not migration time, file mtime, source publication date or a future milestone. A source being reread does not make its facts newly verified.
- Start with current understanding; rewrite it on a material change. Keep only meaningful turning points, not a daily append log. Preserve original detail at its owning source.
- Omit empty or inapplicable sections. Source attribution belongs next to the relevant fact; avoid duplicating a subject in separate “verified” and “company claim” narratives.
- Use ordinary relative Markdown links. On substantive analogies, explain the relationship and where it fails. A link is relevance, not corroboration.
- Selected operating metrics carry period, unit and actual/forecast/source labels. Do not turn this into claim-by-claim bookkeeping.
- Dates and historical prices remain historical unless a new observation replaces them. Do not refresh all numbers merely to reorganize a page.

## Six Object Types

| Object | Reader's question | Normal sections |
| --- | --- | --- |
| Project | What is this business, what is the current view, and what generalizes? | 一句话; 持续判断; 关键事实与判断变量; 可复用认识; 关联与类比; 更新信号; optional 外部动态 |
| Sector | Where is value captured, across which subdirections? | 当前判断; 子方向与经济机制; 机会与反对理由; 变化与后续信号; 项目入口; 估值入口; 主要来源 |
| Technical theme | How does this mechanism work and when does it matter? | 当前理解; 技术路线与关键变量; 支持与反对材料; 商业化映射; 关联对象; 会改变判断的新信号; 主要来源 |
| Valuation | Which observed prices are comparable, on which denominator? | 适用边界; instrument-grouped tables; 使用原则; 本地项目 |
| Event | Which durable external change affects decisions? | 事件与当前状态; 当前影响; optional 关键转折; 关联对象; 后续信号; 来源 |
| Person | Why does this person matter beyond one project? | 一句话; 身份与关键贡献; 重要观点与判断价值; 关联对象; 信息边界; 来源 |

Headings may adapt to the subject; stable meaning matters more than filling a template.

## Project Projection

The compact synchronized header contains `Schema Version: 2`, project ID, creation/update dates, sector, useful tags/aliases, status, current decision display, state path and source hash. Full source arrays, stage/participation/price enums and transaction calculations stay in state or the project judgment, not repeated in the card header.

The generated index still exposes state enums for machine consumers. Existing v2 state files remain compatible. Sync does not synthesize analysis: refresh the header from finalized state, then reread and prepare the prose batch from the current judgment. A source hash is not proof that prose is current.

Keep business positioning distinct from the latest transaction or fund task. Detailed clauses, budgets, portfolio math and customer-by-customer reconciliations remain in project papers. Sector and valuation pages link current project decisions instead of duplicating their price or participation thresholds.

Archived project background can remain useful, but date it as historical and do not present its old investment recommendation as current. External news identifies the affected assumption and whether reassessment is useful; it never silently changes formal status or decision.

## Valuation Observations

Use the same columns across pages:

| Object | Observation date / round | Price and basis | Financing / consideration | Operating denominator / period | Comparability and attribution | Source |
| --- | --- | --- | --- | --- | --- | --- |

Group equity financing, public-market observations, M&A/licensing, and debt separately. Mark pre/post-money, EV/equity and currencies when known. Keep financing-only news in the report unless it has reusable context. Operating data without a matched price can have a clearly labeled non-valuation section.

Company/interview/datapack prices are valid attributed screening inputs. Unknown fields remain unknown. Do not ask for agreements or payment evidence just to complete the table. Investigate only a material uncertainty for the actual investment or transaction question.

## Generated Relations And Retrieval

Relationships derive from explicit Markdown links plus project state membership and related-project fields. Supported types: `relates_to`, `comparable_to`, `counterexample_of`, `belongs_to`, `linked_person`, `affected_by`, `uses_valuation_anchor`, `draws_from`.

A project relationship is not automatically a financial comparable. Abstract failure patterns stay prose, not fabricated external companies. Unmodeled public companies remain source references; no forced card creation. Links to knowledge-source core notes can be indexed as source relationships without a new source-card directory.

Retrieval searches fresh graph text, core source notes, reports, running project judgments and structured GitHub radar candidates. The limit is across direct results, not per type; neighbors are ranked and bounded to one hop. Read the matched source and its as-of date before reasoning from it. Lexical search can miss synonyms: reformulate or use targeted full-text search, without adding a new database by default.

## Safe Writeback

Use `scripts/write_graph.py` for graph content batches. Prepare content outside active graph folders; record the original SHA-256 while reading. The manifest contains:

```json
{"changes":[{"path":"03_技术主题/Example.md","expected_sha256":null,"content_file":"/private/staging/Example.md"}]}
```

`null` is only for a new object. Existing objects require their full prior hash. Snapshot support:

```bash
python3 scripts/write_graph.py --workspace-root "<root>" --snapshot "03_技术主题/Example.md"
python3 scripts/write_graph.py --workspace-root "<root>" --plan "<private-plan.json>" --dry-run
python3 scripts/write_graph.py --workspace-root "<root>" --plan "<private-plan.json>"
python3 scripts/validate_memory_graph.py --workspace-root "<root>"
```

The writer takes a short shared file lock, checks all expected hashes before writing, verifies project headers against formal state, writes atomically per file and rebuilds indexes once. A conflict requires rereading and merging, not blind retry. Ordinary exceptions restore original files. This is not a crash-transaction database: after interruption, read back affected files and rebuild/validate before claiming completion. Legacy/manual writers must adopt this entry point to participate in locking.

`sync_project.py` and standalone rebuild use the same lock. Research and report preparation need not be serialized. Validate structure/index freshness and read back changed reasoning separately. Validation does not prove factual accuracy.

## Source Notes And Thresholds

One evolving `知识来源/.../核心整理.md` keeps source context, original-content coverage, takeaways, mechanism analysis, prior-memory connections and actual writeback. No fixed takeaway cap; omit empty follow-ups. Full original content is preserved once when available.

Events require standalone durable decision value. People require independent industry, research or operating importance; neither layer is a news log, contact list or meeting roster. Important signals without a safe destination may use the existing small review note, not a new proposal queue.

The legacy layout migrator only normalizes older directories. Content restructuring needs review, a private backup and source/link preservation; it is not an automatic summarizer.
