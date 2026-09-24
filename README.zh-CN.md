# AI Work Hub Memory Graph

[English](README.md)

把项目尽调、专家访谈、公开对谈、行业研究和日报/周报连接成持续更新的私人投资认知库。新材料到来时先联想旧知识，分析后只沉淀未来有用的变化。

## 信息放在哪里

| 层次 | 职责 |
| --- | --- |
| 项目 | 一份持续判断与todo，保存公司完整资料 |
| 知识来源 | 每次非项目访谈或主题材料一份核心整理 |
| 行业研究 / 自动化归档 | 保存正式研究和报告全文 |
| Memory Graph | 项目、赛道、技术、估值、事件、人物六类压缩知识 |
| JSONL索引 | 自动生成的检索缓存，不人工维护 |

同类内容使用一致结构：当前认识在前、关键变量和适用边界清楚、来源可回看。估值按统一字段及交易性质分组；赛道页链接项目当前判断，不重复抄录价格或投资决定。重要变化重写现有结论，不把页面变成新闻流水账。

分类、关注名单和投资偏好由使用者自定义。Skill是通用工作机制，知识库保存在使用者自己的目录，不能上传到本公开仓库。

## 安装与更新

先确定私人工作区路径。可直接对Codex说：

> 请从 https://github.com/guyu980/ai-work-hub-memory-graph-skill 安装 ai-work-hub-memory-graph，先检查是否已安装，避免重复副本；再在我确认的私人工作区初始化。

也可采用Git源码加软链接，便于持续更新。已有同名安装时先检查，不覆盖：

```bash
mkdir -p ~/Documents/skills-repos ~/.codex/skills
cd ~/Documents/skills-repos
git clone https://github.com/guyu980/ai-work-hub-memory-graph-skill.git
ln -s "$(pwd)/ai-work-hub-memory-graph-skill/ai-work-hub-memory-graph" \
  ~/.codex/skills/ai-work-hub-memory-graph
```

脚本使用Python 3.10+；共享写锁支持macOS/Linux。安装后重新载入Skill；更新时在源码仓库运行 `git pull --ff-only`。软链接安装会同步使用更新后的机制，私人知识不随Git上传。

## 日常使用

- “分析这次专家访谈”：保存原文/解析和一份核心整理，连接相关旧知识。
- “这个新项目让我想起哪些旧项目”：按业务、技术和价格检索，解释可比与不可比之处。
- “把这期报告的重要变化沉淀下来”：更新现有对象，不为普通新闻逐条建事件。
- 明确说“不保存”时只在对话中分析；正式深度研究需明确提出。

[尽调Skill](https://github.com/guyu980/ai-work-hub-diligence-skill)负责具体公司的连续判断；[研究Skill](https://github.com/guyu980/ai-work-hub-deep-research-skill)负责正式系统报告。本Skill负责非项目来源与跨项目记忆。主动发现复用已授权的日报/周报等任务，不会自行新增定时任务。

## 维护机制

检索覆盖卡片正文、核心整理、研究报告、项目持续判断及结构化GitHub雷达线索，控制总结果量并返回一层相关对象。它仍是关键词检索，重要结果应读回原文和日期，必要时换一种问法。

写回采用短时文件锁和原文哈希检查，冲突时重新读取并合并，避免日报与雷达互相覆盖。内容变更后统一重建、校验索引；只读问题不做全库维护。自动化可提示项目需要重评，但不能静默改变正式投资决定。

```bash
python3 ai-work-hub-memory-graph/scripts/init_memory_graph.py --workspace-root "<私人工作区>"
python3 ai-work-hub-memory-graph/scripts/retrieve_memory.py --workspace-root "<私人工作区>" --query "<具体问题>"
python3 ai-work-hub-memory-graph/scripts/validate_memory_graph.py --workspace-root "<私人工作区>"
```

详细执行约定见[SKILL](ai-work-hub-memory-graph/SKILL.md)、[内容结构与写回格式](ai-work-hub-memory-graph/references/schema.md)、[公开访谈发现](ai-work-hub-memory-graph/references/public-interviews.md)。

## 贡献与边界

只提交通用机制、脚本、模板和虚拟例子；不提交真实项目、私人判断、来源原文、自动化目的地或凭据。通过PR贡献，由维护者审核合并。

[MIT License](LICENSE)
