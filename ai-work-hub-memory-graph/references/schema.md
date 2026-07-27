# Memory Graph Schema v2

Use four explicit layers:

1. `项目/<项目名>/` is the complete source-of-truth layer.
2. `<项目名>_项目状态.json` is the machine-readable current project state.
3. Memory Graph Markdown cards are compressed human-readable views.
4. JSONL indexes are generated caches. Rebuild them from cards and state; do not hand-maintain them.

Cross-project thesis, sector, or event-triggered changes are proposals until reviewed. Store them in `09_待确认更新/`. Store sync and rebuild audit records in `10_运行记录/`.

## Naming

Use date-prefixed files when the card is first created:

```text
01_项目卡片/YYYY-MM-DD_项目名.md
06_事件卡片/YYYY-MM-DD_事件短名.md
08_人物卡片/YYYY-MM-DD_姓名.md
```

Use stable sector and theme files:

```text
02_赛道地图/AI原生应用与工作流.md
03_技术主题/VLA.md
04_估值锚点/具身智能与机器人.md
05_观点账本/观点账本.md
```

## Project Card Markdown

```markdown
# 项目卡片｜项目名

- Schema Version: 2
- 项目 ID: project:项目名
- 创建日期:
- 最近更新:
- 最近同步:
- 主赛道:
- 标签:
- 别名: []
- 资料模式: live / historical_review
- 历史结果: not_applicable / invested / pass / unknown
- 复盘状态: not_applicable / pending / in_progress / reviewed / refresh_due
- 历史决策日期:
- 复盘基准日:
- 项目状态: active / archived
- 流程阶段: screening / diligence / ic / closing / monitoring / archived
- 投资判断: invest / continue / pause / pass / observe / invested
- 建议打法: lead / co_lead / follow / small_option / none / tbd
- 仓位: standard / small / symbolic / tbd
- 价格判断: cheap / reasonable / expensive / unacceptable / unknown
- 判断置信度: low / medium / high
- 当前投资判断: 人类可读组合结论
- 融资阶段:
- 估值摘要:
- 状态文件:
- 证据账本:
- 资料来源:
- 同步哈希:
- 证据回填状态: complete / pending / partial

## 一句话

## 公司与产品

## 技术路线

## 客户与商业化

## 团队技术背景

## 估值与融资

## 已验证事实

## 公司/来源自述

## 仍需确认

## 相似项目

## 反例项目

## 相关赛道/技术观点

## 对投资判断的启发

## 下次触发更新的信号
```

## Project State JSON

The state JSON lives inside the project folder and owns all current decision
fields. See the companion diligence skill's
`references/evidence-contract.md` for the complete schema.

Do not encode project lifecycle, diligence stage, decision, role, sizing, and
price in one status string.

Historical projects use the same schema. Keep `historical_outcome` immutable as
the original result while current decision fields may change when the project
is reopened.

## Project Index JSONL

One generated line per project:

```json
{"schema_version":2,"type":"project","project_id":"project:Project Name","name":"Project Name","aliases":[],"primary_sector":"AI原生应用与工作流","tags":["AI应用"],"project_status":"active","process_stage":"diligence","investment_decision":"continue","recommended_play":"follow","position_size":"small","price_view":"reasonable","confidence":"medium","judgment_display":"继续推进；建议跟投，小仓位","stage":"","valuation":"","source_path":"01_项目卡片/YYYY-MM-DD_Project Name.md","state_path":"项目/Project Name/输出文档/Project Name_项目状态.json","evidence_ledger_path":"项目/Project Name/解析文本/证据账本.jsonl","related_projects":[],"counterexamples":[],"updated_at":"YYYY-MM-DD","summary":"One-sentence compressed view."}
```

## Relationship Index JSONL

`00_索引/关系索引.jsonl` is generated. Every target has an explicit kind.
Unresolved public comparables remain `external_entity`; do not pretend they are
local project cards.

```json
{"schema_version":2,"type":"relationship","relation_id":"relation:...","from_kind":"project","from_id":"project:A","from_name":"A","relation_type":"comparable_to","to_kind":"project","to_id":"project:B","to_name":"B","source_path":"01_项目卡片/...","updated_at":"YYYY-MM-DD"}
```

Allowed relation types:

- `comparable_to`
- `counterexample_of`
- `supports_thesis`
- `contradicts_thesis`
- `linked_person`
- `affected_by`
- `uses_valuation_anchor`

## Person Card Markdown

Create person cards only for high-signal people with reusable industry, academic, technical, or operator standing: notable founders, professors, scientists, lab leads, repeat founders, major maintainers, or technical/product leaders whose independent public work materially changes project judgment. Do not create person cards for ordinary project founders or team members whose importance is limited to one deal. Do not store private contact details or sensitive personal information.

```markdown
# 人物卡片｜姓名或待核验称呼

- 创建日期:
- 最近更新:
- 当前机构/角色:
- 相关项目:
- 相关赛道:
- 标签:
- 信息口径: public / project-material / transcript / interview-note / pending-verification
- 当前判断:

## 一句话

## 身份消歧

## 学术与技术背景

## 论文 / 专利 / GitHub / 开源

## 创业与产业履历

## 跨项目关系

## 对投资判断的启发

## 风险与待确认

## 来源
```

## Person Index JSONL

One line per high-signal person who meets the industry-standing threshold. Use `identity_status` to avoid overstating uncertain identities. Avoid pending person-index entries unless the role itself is clearly industry-significant; otherwise keep pending identity checks inside the project card.

```json
{"type":"person","name":"Person Name","aliases":[],"identity_status":"verified / pending / partial","roles":["founder","chief scientist"],"current_org":"","related_projects":["Project Name"],"primary_sectors":["具身智能与机器人"],"tags":["world model","professor"],"source_path":"08_人物卡片/YYYY-MM-DD_Person Name.md","source_tier":"public / project-material / transcript / interview-note / pending-verification","updated_at":"YYYY-MM-DD","summary":"Why this person matters for investment judgment."}
```

## Event Card Markdown

```markdown
# 事件卡片｜事件短名

- 日期:
- 来源:
- 主赛道:
- 标签:
- 事件类型: financing / product / technical / policy / market / public-company / macro / open-source
- 影响等级: high / medium / low

## 事件

## 为什么重要

## 影响哪些项目/赛道

## 估值或技术含义

## 后续跟踪
```

## Event Index JSONL

```json
{"type":"event","title":"事件短名","date":"YYYY-MM-DD","primary_sector":"半导体与硬件基础设施","tags":["存储芯片","算力"],"impact":"high","source_path":"06_事件卡片/YYYY-MM-DD_事件短名.md","related_projects":[],"updates":["04_估值锚点/半导体与硬件基础设施.md"],"summary":"Why this matters."}
```

## Sector Map Markdown

```markdown
# 赛道地图｜赛道名

## 当前判断

## 子方向

## 强信号

## 弱信号 / 伪命题

## 已看项目

## 代表性反例

## 估值锚点

## 最近改变判断的事件

## 下一步想找的机会
```

## Technical Theme Markdown

```markdown
# 技术主题｜主题名

## 当前理解

## 技术路线与关键变量

## 商业化映射

## 可验证信号

## 常见风险

## 相关项目

## 相关事件

## 会改变判断的新信号
```

## Valuation Anchor Markdown

```markdown
# 估值锚点｜赛道名

## 使用口径

## 上市公司可比

## 一级市场可比

## 商业模式分层

### SaaS / ARR

### API / usage-based

### 硬件收入

### 项目制 / SI-like

### 模型或技术授权

## 我们自己的价格纪律

## 最近更新
```

## Thesis Ledger Markdown

```markdown
# 观点账本

## 观点

- 观点:
- 状态: active / strengthened / weakened / retired
- 置信度: low / medium / high
- 支持证据:
- 反向证据:
- 相关项目:
- 相关事件:
- 什么信号会推翻:
- 最近更新:
```

The first empty template block is not valid data. Index only thesis sections
whose `观点` value is non-empty.

## Operational Commands

```bash
python3 scripts/migrate_memory_graph_v2.py --workspace-root "<workspace_root>"
python3 scripts/rebuild_indexes.py --workspace-root "<workspace_root>"
python3 scripts/validate_memory_graph.py --workspace-root "<workspace_root>"
python3 scripts/build_context_pack.py --workspace-root "<workspace_root>" --query "<project or topic>"
python3 scripts/sync_project.py --workspace-root "<workspace_root>" --state "<state.json>" --graph-delta "<optional-delta.json>"
```

Run rebuild and validation after any batch mutation. `sync_project.py` may update
the project card automatically, but thesis and sector proposals stay in the
review queue.

## Sector Values

The initialization script creates these default primary sectors:

- AI基础设施与开发者工具
- AI原生应用与工作流
- 具身智能与机器人
- AI硬件与边缘智能
- 半导体与硬件基础设施
- 基础模型与前沿技术
- 观察与非核心机会

These are defaults, not universal requirements. If a user's workspace has a different taxonomy, follow the user's sector files under `Memory Graph/02_赛道地图/` and keep JSONL `primary_sector` values aligned with that local taxonomy.
