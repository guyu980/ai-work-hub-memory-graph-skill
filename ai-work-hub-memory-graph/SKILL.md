---
name: ai-work-hub-memory-graph
description: Analyze reusable non-project interviews, public conversations and thematic sources; retrieve prior projects, mechanisms, sectors and valuation context. Maintain private investment memory across diligence, research and authorized intelligence, updating current understanding rather than accumulating news.
---

# AI Work Hub Memory Graph

## Ownership

This is continuous private decision memory, not a second report archive.

| Material | Durable owner |
| --- | --- |
| One company's materials/current investment judgment | Project folder and `ai-work-hub-diligence`; state owns the formal machine-readable decision |
| Reusable non-project interview, podcast or thematic source | One evolving core note under `知识来源/`, handled here |
| Explicit formal research | Report under `行业研究/` or the project; `ai-work-hub-deep-research` |
| Recurring intelligence | Its full report archive; only durable increments enter Graph |
| Reusable cross-project understanding | Existing Graph Markdown object |
| Indexes | Generated caches; never hand-edited |

Preserve reusable source analysis by default, including “看看/总结”, unless saving is excluded. A worthwhile source note need not produce a Graph change. Follow local configurable taxonomy; do not impose a user's sectors or watchlist through the public Skill. Fund/deal workpapers and organizational sharing have separate ownership/authorization.

## Working Loop

1. Confirm an unknown workspace on first use, identify ownership and find the existing object/source.
2. Read the original and useful prior memory. For Feishu, find original text/transcript and relevant nested links; smart minutes are navigation. Disclose inaccessible content.
3. Analyze the important mechanisms, strongest opposing interpretation and implications. Attributed expert/company inputs are usable without a universal verification exercise. Additional research is bounded by what could change the conclusion.
4. Maintain one core source note with context, content/Q&A, takeaways, reasoning, useful connections and only worthwhile follow-ups. See [knowledge-sources.md](references/knowledge-sources.md) for source handling.
5. Decide whether this changes reusable understanding, materially strengthens/challenges an assumption, supplies a useful comparable or offers an independently important event/person. Otherwise retain it only at the source/report.
6. Rewrite affected objects, apply the shared writer, and read back the changed reasoning.

No fixed cap on important analysis or Graph changes. No new Evidence Ledger, thesis ledger, source-card layer, CRM or proposal queue. Duplicate concerns do not warrant a new paragraph or task.

## Retrieve Before Judging

Query the actual decision: company/alias, mechanism, buyer, budget or price denominator. Retrieve a compact combined set, then read the useful source text and dates.

```bash
python3 <skill_dir>/scripts/retrieve_memory.py --workspace-root "<root>" --query "<specific question>" --limit 8
```

The helper searches fresh Graph text, core source notes, formal research, running judgments, structured GitHub radar candidates and existing cross-task sourcing reviews. It uses full entity names/aliases rather than generic-word prefixes. Similar research versions can share a result slot; `other_versions` preserves access to dated snapshots.

Check `updated_at` and `date_basis`: formal project-state date, explicit content metadata and filename fallbacks do not mean the same thing. A file reorganization does not refresh the facts. Results/one-hop links are relevance, not corroboration; lexical misses require a better query or targeted full-text search, not a claim of absence. Do not rebuild or audit the workspace for a read-only query.

## Structure And Updating

Six existing layers remain: projects, sectors, technical themes, valuation anchors, events and people. Read [schema.md](references/schema.md) for writing and compatibility.

- **Project:** business, current projection, decisive variables, reusable lesson and selected external signals. Formal investment decisions stay in the project judgment/state.
- **Sector:** buyer, value capture, subdirection economics, opportunities/counterarguments and representative project links.
- **Theme:** mechanism, key variables, supporting/contrary material, commercial implications and signals that would change understanding.
- **Valuation:** dated observations grouped by instrument and comparable denominator; explain which objects are useful for which business/stage.
- **Event:** a durable standalone change, not every report item.
- **Person:** independent industry/research/operating significance, not every founder, employee or meeting participant.

Start with the current view. Organize supporting changes by **assumption/mechanism**, not a daily news chronology. Merge repeated examples, retaining representative dated evidence and links to original detail. Preserve genuinely different evidence and meaningful turning points; do not flatten counterarguments merely to shorten a file.

Project external signals state the affected assumption and whether focused reassessment is useful. At a natural company update, Diligence can absorb selected unresolved questions into its existing todo. News never silently changes status, participation, price or confidence. No reminder is needed when there is no new material implication.

Sector/theme pages link the authoritative project decision; they do not maintain another live portfolio/transaction model. Company-stated valuation/financing is a valid screening input, not an automatic agreement/payment check.

## Discovery And Sourcing

Use [public-interviews.md](references/public-interviews.md) for public conversations and authorized discovery. Screen cheaply, select firsthand contribution, substantial people and useful reasoning, then read worthwhile originals. Existing intelligence tasks discover; the Skill does not schedule itself.

GitHub interest, technical merit and contact value are different judgments. Reuse radar and cross-task sourcing records before proposing outreach; follow company/repository aliases back to the people and commercial owner. Selected leads can remain in those records without creating project/person cards. No blanket demo, environment test or company audit before an informative first conversation.

## Shared Writes

For project work, finalize the running judgment/state before syncing the card header. For reports, complete the report before writing selected increments. Header/hash synchronization is not semantic freshness.

1. If needed, run `sync_project.py --skip-rebuild`.
2. Read affected files after sync and capture prior hashes with `write_graph.py --snapshot`.
3. Prepare final Markdown outside active Graph folders and use the plan format in [schema.md](references/schema.md).
4. Apply via `write_graph.py --plan`: short shared lock, stale-hash rejection and one index rebuild per batch.
5. On conflict, reread and merge both changes. Validate and read back the actual affected sections before claiming completion.

Preparation can proceed independently; the shared-write interval is serialized. POSIX locking supports macOS/Linux and does not protect writers that bypass the entry point.

## Setup And Acceptance

Initialize only when absent:

```bash
python3 <skill_dir>/scripts/init_memory_graph.py --workspace-root "<root>"
python3 <skill_dir>/scripts/init_knowledge_source.py --workspace-root "<root>" --kind expert-interview --date YYYY-MM-DD --name "<expert>" --topic "<topic>"
```

Use `--kind thematic-material` for thematic sources. Standalone `rebuild_indexes.py` repairs caches; legacy migration normalizes layout, not prose.

After writes, run `validate_memory_graph.py --workspace-root "<root>"` and read back dates, useful links, current reasoning and preserved formal decisions. No useful follow-up or no Graph delta is valid. Source coverage, private ownership and actual write success matter more than filling every section. Real knowledge, personal taxonomy, automation destinations and credentials never belong in the public repository.
