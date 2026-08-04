---
name: ai-work-hub-memory-graph
description: Use when a project, BP, Feishu note, transcript, datapack, news item, financing, GitHub project, technical question, sector question, or valuation question should connect to prior investment knowledge. Initializes, retrieves from, updates, rebuilds, and validates a sparse private Memory Graph of project cards, sector maps, technical themes, valuation anchors, durable events, and high-signal people. Integrates with diligence and recurring intelligence without copying every source item into the graph. Taxonomy is user-configurable.
---

# AI Work Hub Memory Graph

## Operating Contract

Memory Graph is a private decision-memory layer. It helps a future project recall prior projects, counterexamples, sector understanding, technical mechanisms, valuation references, durable external changes, and important people.

It is deliberately sparse.

Hard requirements:

- Project folders remain the full source of truth.
- Project state JSON owns the current machine-readable decision.
- Markdown cards are compressed, human-readable knowledge objects.
- `00_索引/*.jsonl` files are generated caches. Never hand-edit them.
- Update an existing object when possible; do not create a second object for the same idea.
- A report archive remains a report archive. Only reusable increments enter Memory Graph.
- Project-specific news never silently changes the formal investment decision.
- The local taxonomy belongs to the user. Public defaults are editable starting points.
- The generated `Memory Graph/` contains private investment context and must not be committed to the public skill repository.

Read `references/schema.md` before creating or changing structured objects.

## Active Layout

```text
Memory Graph/
  00_索引/
    项目索引.jsonl
    关系索引.jsonl
    赛道索引.jsonl
    技术主题索引.jsonl
    估值索引.jsonl
    事件索引.jsonl
    人物索引.jsonl
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

There is no separate thesis ledger. Reusable investment views belong in the sector, technical, valuation, project, or workflow-rule object that will actually retrieve them later.

## Route Every Increment

Put each material increment in its most direct home:

| Increment | Destination |
| --- | --- |
| Current view or evidence about one company | Project folder and `01_项目卡片/` |
| Public news directly affecting a known project | Dated entry in that project card's `外部动态` |
| Repeated pattern across companies or a market structure view | Existing `02_赛道地图/` file |
| Technical mechanism, route, benchmark, bottleneck, or validation method | Existing `03_技术主题/` file |
| Financing or market price useful for later comparison | Existing `04_估值锚点/` file |
| Standalone external change with durable decision value | `05_事件卡片/` |
| Person with reusable industry, academic, technical, or operator standing | `06_人物卡片/` |
| Important signal with no safe destination yet | One concise entry in `待复核.md` |
| Low-signal, duplicate, or one-off detail | Source project or report archive only |

Do not write the same fact into several new cards. A material event may update an existing project, sector, technical, or valuation object without needing its own event card.

## Retrieve Before A Decision

When Memory Graph exists and a project or thematic question is being judged:

1. Rebuild indexes if the Markdown changed or index freshness is uncertain.
2. Query with the company name, aliases, sector, product, technical route, and relevant business model.
3. Review the compact ranked results.
4. Open the source cards behind useful matches; do not rely only on index summaries.
5. Return a short connection set: similar projects, counterexamples, sector/technical views, valuation anchors, important people, and what must be different this time.

```bash
python3 <skill_dir>/scripts/retrieve_memory.py \
  --workspace-root "<workspace_root>" \
  --query "<project, sector, technology, and business-model terms>" \
  --output /tmp/memory-retrieval.json
```

The retrieval result is temporary query output, not a new knowledge store.

## Write After A Decision Or Report

For a diligence update:

1. Finalize the project judgment and project state first.
2. Sync the project card from the state.
3. Add only reusable cross-project learning to the direct higher-level object.
4. Rebuild indexes.
5. Validate the graph.
6. Report any graph failure without claiming success.

For a daily/weekly report or GitHub radar:

1. Finish and archive the report first.
2. Compare against the existing graph and latest report baseline.
3. Keep low-signal or duplicate items only in the report archive.
4. Route every material increment using the table above.
5. Do not impose a fixed update cap; materiality, not volume, controls writeback.
6. Rebuild and validate once after the batch.

Important public news can be written directly to the relevant project card. It does not need a proposal file. Automation may state a possible positive, negative, or neutral effect, but formal project status, investment decision, participation, position, price view, and confidence change only through the diligence workflow.

## Object Thresholds

### Project Cards

Create for active or historically useful projects. Preserve a weak project only when it is a meaningful counterexample or reopen candidate; very low-quality screens can remain archived without a first-class card.

Project cards compress, rather than duplicate, the project folder. Keep the current view, key evidence boundaries, comparable projects, counterexamples, external changes, and reopen/update signals.

### Event Cards

Create only when the event has standalone, durable value and changes at least one of:

- a sector or technical view;
- a reusable valuation reference;
- priority or risk for multiple active projects;
- a persistent regulatory, market-structure, or infrastructure assumption.

Ordinary financings, product launches, repository heat, quarterly project metrics, customer calls, and cash-conversion updates stay in reports or project objects unless they create a reusable cross-project change.

### People Cards

Create only for people whose independent importance extends beyond one project: recognized founders, professors, scientists, lab leaders, repeat operators, major maintainers, or technical/product leaders with industry standing.

Do not use the people layer as a CRM, team roster, meeting-attendee list, or contact database. Do not store private contact details or sensitive personal information.

## Valuation Discipline

Record routine valuation evidence lightly: project, date, round/stage, stated valuation, financing amount, source, operating maturity, and comparability note. Separate observed/company-stated price from internal price discipline.

Do not require agreements, payment proof,工商 changes, or exact closing status for ordinary BP, interview, news, report, or radar intake. Deepen only for ownership, portfolio marking, return math, legal/closing risk, source conflict, or a live investment decision.

## Operations

Initialize:

```bash
python3 <skill_dir>/scripts/init_memory_graph.py \
  --workspace-root "<workspace_root>"
```

Normalize an older v2 graph to the current sparse layout:

```bash
python3 <skill_dir>/scripts/migrate_memory_graph_v2.py \
  --workspace-root "<workspace_root>"
```

Sync a project:

```bash
python3 <skill_dir>/scripts/sync_project.py \
  --workspace-root "<workspace_root>" \
  --state "<project-state.json>"
```

If the project has no card yet, sync creates the first card from the finalized
state. A second card for the same project is treated as an error.

Rebuild and validate:

```bash
python3 <skill_dir>/scripts/rebuild_indexes.py \
  --workspace-root "<workspace_root>"
python3 <skill_dir>/scripts/validate_memory_graph.py \
  --workspace-root "<workspace_root>"
```

Successful sync metadata lives only in `.system/last-sync.json`. Detailed workflow run records and failures belong in the relevant archive, not in numbered graph directories.

## Completion Check

Before declaring graph work complete, verify:

1. The increment was routed to the most direct object.
2. No duplicate card or unnecessary event/person object was created.
3. Project-specific facts remain linked to their source project.
4. Reusable views live in sector, technical, valuation, project, or rule objects, not a separate thesis ledger.
5. Generated indexes were rebuilt, not hand-edited.
6. Validation passed, or the exact failure was reported.
7. Private workspace content remains outside the public repository.
