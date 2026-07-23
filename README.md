# AI Work Hub Memory Graph Skill

[中文说明](README.zh-CN.md)

A Codex skill for maintaining a private cross-project investment knowledge base.

It connects new BPs, Feishu notes, datapacks, news items, GitHub projects, technical themes, and valuation questions to prior project cards, sector maps, technical views, valuation anchors, and a running thesis ledger.

## What It Does

- Initializes a local private `Memory Graph/` knowledge base inside an AI Work Hub workspace.
- Creates and updates project cards, event cards, sector maps, technical themes, valuation anchors, and thesis entries.
- Tracks only high-signal people with reusable industry, academic, technical, or operator standing, without becoming a CRM or team roster.
- Retrieves similar projects, counterexamples, valuation anchors, and sector or technical views before a new project judgment.
- Post-processes AI technology daily/weekly reports and GitHub radar outputs into high-signal event cards.
- Keeps the public skill reusable while keeping private investment knowledge local.

## Quick Install

Clone the public repo:

```bash
mkdir -p ~/Documents/skills-repos
cd ~/Documents/skills-repos
git clone https://github.com/guyu980/ai-work-hub-memory-graph-skill.git
cd ai-work-hub-memory-graph-skill
```

Link the skill into Codex:

```bash
mkdir -p ~/.codex/skills
ln -s "$(pwd)/ai-work-hub-memory-graph" ~/.codex/skills/ai-work-hub-memory-graph
```

If a skill with that name already exists, back it up first:

```bash
mv ~/.codex/skills/ai-work-hub-memory-graph ~/.codex/skills/ai-work-hub-memory-graph.backup
ln -s "$(pwd)/ai-work-hub-memory-graph" ~/.codex/skills/ai-work-hub-memory-graph
```

Initialize the private knowledge base:

```bash
python3 ai-work-hub-memory-graph/scripts/init_memory_graph.py \
  --workspace-root "$HOME/Documents/AI Work Hub"
```

This creates:

```text
~/Documents/AI Work Hub/Memory Graph/
```

Do not upload that generated `Memory Graph/` folder to a public repository.

## First Use

Connect a new project to prior knowledge:

```text
Use $ai-work-hub-memory-graph to connect this BP to prior projects, sector views, technical themes, and valuation anchors.
```

Initialize or repair the local knowledge base:

```text
Use $ai-work-hub-memory-graph to initialize my Memory Graph under ~/Documents/AI Work Hub.
```

Post-process a daily or weekly report:

```text
Use $ai-work-hub-memory-graph to extract high-signal event cards from this AI科技与宏观事件日报.
```

Track a high-signal founder, scientist, or technical leader:

```text
Use $ai-work-hub-memory-graph to add this founder/scientist as a key-person signal only if they have reusable industry standing beyond this one project.
```

## Updating The Skill

This repo should be the public source of truth for the skill only.

After editing:

```bash
git status
git add ai-work-hub-memory-graph README.md README.zh-CN.md LICENSE .gitignore
git commit -m "Update memory graph skill"
git push
```

Users can update with:

```bash
git pull
```

## Do Not Commit

Do not commit generated local knowledge bases, project materials, Feishu auth state, tokens, private deal notes, company confidential data, private contact details, sensitive personal information, or user-specific local overrides.

## License

MIT. See [`LICENSE`](LICENSE).
