# AI Work Hub Memory Graph Skill

[English](README.md)

这是一个用于维护本地私有“投资认知库”的 Codex skill。

它把新 BP、飞书纪要、datapack、新闻、GitHub 项目、技术主题和估值问题，连接到过去看过的项目、赛道地图、技术观点、估值锚点和持续更新的观点账本。

## 它能做什么

- 在 AI Work Hub 工作区里初始化本地私有 `Memory Graph/` 知识库。
- 创建和更新项目卡片、事件卡片、赛道地图、技术主题、估值锚点和观点账本。
- 只跟踪具备可复用行业地位、学术/技术谱系或操盘记录的高信号人物，不做成通讯录、CRM 或项目团队花名册。
- 看新项目之前，检索相似项目、反例项目、估值锚点、赛道观点和技术主题。
- 将 AI科技与宏观事件日报/周报、GitHub 全球项目雷达里的高信号事件沉淀为事件卡片。
- 保持 skill 本身公开可复用，但知识库内容只保存在本地，不上传 GitHub。

## 安装说明

通过 GitHub 安装：

```bash
mkdir -p ~/Documents/skills-repos
cd ~/Documents/skills-repos
git clone https://github.com/guyu980/ai-work-hub-memory-graph-skill.git
cd ai-work-hub-memory-graph-skill
```

软链到 Codex skills 目录：

```bash
mkdir -p ~/.codex/skills
ln -s "$(pwd)/ai-work-hub-memory-graph" ~/.codex/skills/ai-work-hub-memory-graph
```

如果本地已经有同名 skill，先备份旧版本：

```bash
mv ~/.codex/skills/ai-work-hub-memory-graph ~/.codex/skills/ai-work-hub-memory-graph.backup
ln -s "$(pwd)/ai-work-hub-memory-graph" ~/.codex/skills/ai-work-hub-memory-graph
```

初始化本地私有知识库：

```bash
python3 ai-work-hub-memory-graph/scripts/init_memory_graph.py \
  --workspace-root "$HOME/Documents/AI Work Hub"
```

生成目录：

```text
~/Documents/AI Work Hub/Memory Graph/
```

这个生成出来的 `Memory Graph/` 是私有知识库，不要上传到 public GitHub。

## 第一次使用

把新项目和历史认知连接起来：

```text
Use $ai-work-hub-memory-graph to connect this BP to prior projects, sector views, technical themes, and valuation anchors.
```

初始化或修复本地知识库：

```text
Use $ai-work-hub-memory-graph to initialize my Memory Graph under ~/Documents/AI Work Hub.
```

处理日报/周报：

```text
Use $ai-work-hub-memory-graph to extract high-signal event cards from this AI科技与宏观事件日报.
```

沉淀高信号创始人、科学家或技术负责人：

```text
Use $ai-work-hub-memory-graph to add this founder/scientist as a key-person signal only if they have reusable industry standing beyond this one project.
```

## 分类方式

初始化脚本会创建一套默认赛道分类，方便开箱即用；这只是默认模板，不是固定规则。用户可以直接修改 `Memory Graph/02_赛道地图/` 下的赛道文件，并让项目索引里的 `primary_sector` 跟随自己的分类方式。

## 更新这个 Skill

这个 repo 只作为公开 skill 的 source of truth。

修改后：

```bash
git status
git add ai-work-hub-memory-graph README.md README.zh-CN.md LICENSE .gitignore
git commit -m "Update memory graph skill"
git push
```

其他用户更新：

```bash
git pull
```

## 不要提交这些内容

不要提交生成出来的本地知识库、项目资料、飞书登录态、token、私有交易笔记、公司保密信息、私人联系方式、敏感个人信息或用户个人本地配置。

## License

MIT. See [`LICENSE`](LICENSE).
