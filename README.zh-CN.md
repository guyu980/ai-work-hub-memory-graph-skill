# AI Work Hub Memory Graph

[English](README.md)

**跨项目投资记忆**。把项目尽调、专家访谈、公开对谈、正式研究和日常信息中的关键认识接起来。新材料先联想旧知识，重要变化再更新现有认识，而不是堆积新闻。

## 安装与更新

也可以直接让 Codex 从此 GitHub 仓库安装 Skill，并先检查是否已有安装。推荐 Git 克隆加单个软链接，让自用版和分享版使用同一源码：

```bash
mkdir -p ~/Documents/skills-repos ~/.codex/skills
cd ~/Documents/skills-repos
git clone https://github.com/guyu980/ai-work-hub-memory-graph-skill.git
ln -s "$(pwd)/ai-work-hub-memory-graph-skill/ai-work-hub-memory-graph" ~/.codex/skills/ai-work-hub-memory-graph
```

已有同名目录时先检查，不覆盖安装，避免出现重复 Skill。Python 脚本需要 Python 3.10+；Graph 共享锁支持 macOS/Linux。安装后重新加载 Codex。更新时：

```bash
cd ~/Documents/skills-repos/ai-work-hub-memory-graph-skill
git pull --ff-only
```

软链接立即使用同一份代码，无需复制另一份 Skill。私人工作区与仓库分开。

## 日常使用

```text
用 $ai-work-hub-memory-graph 整理这场专家访谈，保存一份核心整理并联系已有认识。
这个新项目与之前看过哪些项目、技术方向和估值有关？
从这些已归档报告中吸收重要变化，更新现有赛道与技术主题。
```

首次确认私人工作区路径。非项目来源默认保存在 `知识来源/`，每个来源一份持续核心整理；可以要求只在对话中分析。

Graph 保留六类对象：项目、赛道、技术主题、估值锚点、重大事件、重要人物。项目决定仍在原项目文档；完整来源、研究和日报仍在各自归档。Graph 按同类结构保存可复用分析，按关键假设合并重复变化，不保存第二份报告或逐条证据账本。分类、关注名单和投资偏好可以自定义。

检索覆盖图谱、核心整理、研究、持续判断、GitHub 雷达及已有跨任务 sourcing 复盘；区分内容日期及日期来源，近似研究版本保留快照入口。检索只是相关性提示，需要读取原文和边界。

```bash
python3 ai-work-hub-memory-graph/scripts/init_memory_graph.py --workspace-root "<私人工作区>"
python3 ai-work-hub-memory-graph/scripts/retrieve_memory.py --workspace-root "<私人工作区>" --query "<具体问题>"
```

已存在图谱不必重复初始化。共享写入使用原文哈希和短时锁，冲突后重读合并；只在实际变化后重建与校验。自动化可提示项目影响和重评信号，不静默改正式决定，也不批量创建项目或待办。

## 三个 Skill 如何衔接

[尽调](https://github.com/guyu980/ai-work-hub-diligence-skill)维护单公司现行判断；[Memory Graph](https://github.com/guyu980/ai-work-hub-memory-graph-skill)整理非项目来源和跨项目记忆；[深度研究](https://github.com/guyu980/ai-work-hub-deep-research-skill)负责明确要求的正式报告。安装同伴 Skill 可以联动，也可单独使用。新闻与 GitHub 发现由已授权的自动化任务执行，Skill 本身不自动创建定时任务。

公开仓库只保存通用机制、脚本和虚拟案例。实际项目、知识库、报告、私人关注名单、交付地址和凭据保留本地，不上传。贡献通过 PR，由维护者审阅合并。模型选择属于运行设置，Skill 不绑定某个模型。

[Agent 执行入口](ai-work-hub-memory-graph/SKILL.md) · [MIT](LICENSE)
