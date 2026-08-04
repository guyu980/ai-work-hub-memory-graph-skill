# AI Work Hub Memory Graph

[English](README.md)

这是一个为投资项目建立私有、长期记忆的 Codex skill。它把项目尽调、AI 日报/周报、GitHub 雷达、赛道研究、技术主题、估值信息、重大事件和高信号人物连接起来，但不会把图谱变成第二份材料仓库。

## 它解决什么问题

面对一个新项目或新事件时，可以自动联想到：

- 相似项目和反例；
- 当前赛道判断；
- 相关技术路线、瓶颈和验证标准；
- 估值锚点和价格纪律；
- 会长期影响判断的外部变化；
- 具有跨项目价值的人物。

完成判断后，只把未来还能复用的知识增量写回图谱。

## 知识模型

```text
项目原始资料
  -> 项目状态和聚焦证据
  -> 压缩后的 Markdown 知识对象
  -> 自动生成的 JSONL 检索索引
```

当前目录：

```text
Memory Graph/
  00_索引/
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

不再单独维护观点账本。可复用的投资观点进入最容易被再次调用的赛道、技术、估值、项目或工作流规则。

赛道分类由用户自定义；skill 提供的默认分类只是起点，不是强制标准。

## 写入路由

| 新信息 | 保存位置 |
| --- | --- |
| 单个公司的当前判断或证据 | 项目文件夹和项目卡片 |
| 已知项目的公开新闻 | 项目卡片带日期的 `外部动态` |
| 跨公司的市场规律 | 赛道地图 |
| 技术路线、瓶颈或验证方法 | 技术主题 |
| 有复用价值的融资或市场价格 | 估值锚点 |
| 具有独立、持久价值的外部变化 | 事件卡片 |
| 具有独立行业地位的人物 | 人物卡片 |
| 重要但暂时无明确归宿 | 单一 `待复核.md` 条目 |
| 重复或低信号信息 | 只留在项目或报告归档 |

## 通过 GitHub 安装

```bash
mkdir -p ~/Documents/skills-repos ~/.codex/skills
cd ~/Documents/skills-repos
git clone https://github.com/guyu980/ai-work-hub-memory-graph-skill.git
ln -s "$(pwd)/ai-work-hub-memory-graph-skill/ai-work-hub-memory-graph" \
  ~/.codex/skills/ai-work-hub-memory-graph
```

初始化私有图谱：

```bash
python3 ai-work-hub-memory-graph-skill/ai-work-hub-memory-graph/scripts/init_memory_graph.py \
  --workspace-root "$HOME/Documents/AI Work Hub"
```

后续更新：

```bash
cd ~/Documents/skills-repos/ai-work-hub-memory-graph-skill
git pull --ff-only
```

生成的 `Memory Graph/` 是私有工作区数据，不能推送到这个公开仓库。

## 怎么使用

```text
使用 $ai-work-hub-memory-graph，在更新图谱之前，把这个项目和历史项目、赛道判断、技术主题及估值锚点连接起来。
```

日报、周报或 GitHub 雷达完成后：

```text
使用 $ai-work-hub-memory-graph 处理这份已经归档的报告。低信号内容留在报告，只把有长期价值的增量写入最直接的图谱对象。
```

## 常用命令

生成精简检索包：

```bash
python3 ai-work-hub-memory-graph/scripts/build_context_pack.py \
  --workspace-root "$HOME/Documents/AI Work Hub" \
  --query "项目 赛道 技术 商业模式"
```

重建并校验：

```bash
python3 ai-work-hub-memory-graph/scripts/rebuild_indexes.py \
  --workspace-root "$HOME/Documents/AI Work Hub"
python3 ai-work-hub-memory-graph/scripts/validate_memory_graph.py \
  --workspace-root "$HOME/Documents/AI Work Hub"
```

整理旧版 v2 图谱：

```bash
python3 ai-work-hub-memory-graph/scripts/migrate_memory_graph_v2.py \
  --workspace-root "$HOME/Documents/AI Work Hub"
```

## 与其他工作流联动

配套的 [AI Work Hub Diligence](https://github.com/guyu980/ai-work-hub-diligence-skill) skill 负责项目原始资料、持续判断和 todo；本 skill 负责跨项目检索和可复用知识写回。

AI 日报/周报和 GitHub 雷达也可以在报告完成后更新图谱。更新数量不设固定上限：低信号内容留在归档，真正重要的增量全部按最直接的对象写入。

自动化可以向项目卡片追加带来源的外部新闻，但不能静默修改正式投资判断、参与方式、仓位、价格判断或置信度。

## 高级部署

本地 Markdown 和自动生成的 JSONL 已经构成完整默认工作流。组织级 Registry、混合存储、bridge 和可移植 Context Package 都是可选高级能力，见 [`advanced-deployment.md`](ai-work-hub-memory-graph/references/advanced-deployment.md)。

## 仓库边界

公开仓库只包含机制、脚本、模板和 schema。不要提交真实项目卡片、原始资料、私有投资判断、飞书 token 或工作区生成的索引。

其他人通过 Pull Request 提交修改，由仓库维护者审核和合并。

许可证：[MIT](LICENSE)
