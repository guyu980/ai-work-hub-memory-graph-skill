# AI Work Hub Memory Graph

[中文说明](README.zh-CN.md)

A Codex Skill for continuous, private investment memory. Connect diligence, interviews, public conversations, research and recurring intelligence so new material can recall prior reasoning and improve it.

## Knowledge Model

Project folders own the one running company judgment and full materials. Knowledge-source folders own one core note per non-project conversation. Research and report archives own complete deliverables. Six graph layers hold compressed project, sector, technical, valuation, event and person knowledge. JSONL indexes are generated caches.

Objects of the same kind use consistent structures. Rewrite current understanding, keep material turning points, and link sources. Separate equity, M&A/licensing and debt observations with common valuation columns. Link current project decisions rather than duplicating them across sector pages.

Taxonomy, watchlists and investment preferences are user-configurable private settings. No graph database, source-card layer or claim-by-claim ledger is required.

## Install And Update

Ask Codex to install `ai-work-hub-memory-graph` from this repository, checking for an existing installation first. Confirm your private workspace path before initialization.

For a Git checkout with a single symlink installation:

```bash
mkdir -p ~/Documents/skills-repos ~/.codex/skills
cd ~/Documents/skills-repos
git clone https://github.com/guyu980/ai-work-hub-memory-graph-skill.git
ln -s "$(pwd)/ai-work-hub-memory-graph-skill/ai-work-hub-memory-graph" \
  ~/.codex/skills/ai-work-hub-memory-graph
```

Inspect an existing destination instead of overwriting it. Scripts require Python 3.10+; shared file locking supports macOS/Linux. Reload the Skill after installation. Run `git pull --ff-only` in the checkout to update; the symlink uses the same source. Generated knowledge stays private and outside this repository.

## Use

Ask to analyze an expert interview, connect a new project to earlier work, or absorb meaningful changes from an archived report. Reusable sources are saved by default unless the user requests chat-only analysis.

[Diligence](https://github.com/guyu980/ai-work-hub-diligence-skill) owns company decisions. [Deep Research](https://github.com/guyu980/ai-work-hub-deep-research-skill) owns explicitly requested formal studies. This Skill owns non-project source analysis and cross-project memory. Proactive discovery reuses authorized intelligence tasks; the Skill does not schedule itself.

Retrieval covers fresh graph text, source notes, reports, running judgments and structured GitHub radar candidates, with a combined result limit and ranked one-hop neighbors. It is lexical retrieval: read sources and dates, and reformulate weak queries.

Shared writes use a short file lock and expected-content hashes. Conflicts require rereading and merging. Rebuild and validate after changes, not every read. Automation may flag reassessment but never silently changes a formal investment decision.

```bash
python3 ai-work-hub-memory-graph/scripts/init_memory_graph.py --workspace-root "<private-root>"
python3 ai-work-hub-memory-graph/scripts/retrieve_memory.py --workspace-root "<private-root>" --query "<specific question>"
python3 ai-work-hub-memory-graph/scripts/validate_memory_graph.py --workspace-root "<private-root>"
```

See the [Skill](ai-work-hub-memory-graph/SKILL.md), [content and writeback contract](ai-work-hub-memory-graph/references/schema.md), and [public discovery workflow](ai-work-hub-memory-graph/references/public-interviews.md).

## Contributions

Submit generic mechanisms, scripts, templates and fictional examples through a PR for maintainer review. Never submit real projects, private judgments, originals, automation destinations or credentials.

[MIT License](LICENSE)
