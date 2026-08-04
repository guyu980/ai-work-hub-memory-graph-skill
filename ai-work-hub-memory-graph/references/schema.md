# Memory Graph Schema v2

This schema describes the default local graph. Read `advanced-deployment.md` only for explicit organization-storage or cross-runtime requests.

## Data Layers

1. `项目/<项目名>/` is the complete source-of-truth layer.
2. `<项目名>_项目状态.json` is the current machine-readable project decision.
3. Memory Graph Markdown files are compressed human-readable knowledge objects.
4. `00_索引/*.jsonl` files are generated retrieval caches.

Update Markdown and project state first. Rebuild indexes; never edit generated JSONL by hand.

## Paths

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
  01_项目卡片/YYYY-MM-DD_项目名.md
  02_赛道地图/赛道名.md
  03_技术主题/主题名.md
  04_估值锚点/赛道名.md
  05_事件卡片/YYYY-MM-DD_事件短名.md
  06_人物卡片/YYYY-MM-DD_姓名.md
  待复核.md
  .system/last-sync.json
```

There is no thesis file or thesis index. Reusable views belong in the object that owns the decision context: sector, technical theme, valuation anchor, project/counterexample, or workflow rule.

## Project Card

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
- 当前投资判断:
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
## 外部动态
## 相似项目
## 反例项目
## 相关赛道/技术主题
## 对投资判断的启发
## 下次触发更新的信号
```

The companion diligence skill's `references/evidence-contract.md` defines project state and evidence records. Historical projects use the same schema; preserve the original outcome while current decision fields may change after reopening.

Generated project record:

```json
{"schema_version":2,"type":"project","project_id":"project:Example","name":"Example","aliases":[],"primary_sector":"AI原生应用与工作流","tags":["AI应用"],"project_status":"active","process_stage":"diligence","investment_decision":"continue","recommended_play":"follow","position_size":"small","price_view":"reasonable","confidence":"medium","judgment_display":"继续推进；建议跟投，小仓位","stage":"","valuation":"","source_path":"01_项目卡片/YYYY-MM-DD_Example.md","state_path":"项目/Example/输出文档/Example_项目状态.json","evidence_ledger_path":"项目/Example/解析文本/证据账本.jsonl","related_projects":[],"counterexamples":[],"updated_at":"YYYY-MM-DD","summary":"Compressed current view."}
```

## Relationship Index

Relationships are generated from project-card links. An unresolved public comparable remains an `external_entity`; do not pretend it is a local project.

```json
{"schema_version":2,"type":"relationship","relation_id":"relation:...","from_kind":"project","from_id":"project:A","from_name":"A","relation_type":"comparable_to","to_kind":"project","to_id":"project:B","to_name":"B","source_path":"01_项目卡片/...","updated_at":"YYYY-MM-DD"}
```

Allowed relation types:

- `comparable_to`
- `counterexample_of`
- `linked_person`
- `affected_by`
- `uses_valuation_anchor`

## Sector Map

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

Generated sector record:

```json
{"schema_version":2,"type":"sector","sector_id":"sector:...","title":"赛道名","primary_sector":"赛道名","tags":[],"summary":"当前判断","strong_signals":[],"related_projects":[],"counterexamples":[],"updated_at":"YYYY-MM-DD","source_path":"02_赛道地图/赛道名.md"}
```

## Technical Theme

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

Generated technical-theme record:

```json
{"schema_version":2,"type":"technical_theme","theme_id":"technical-theme:...","title":"主题名","tags":[],"summary":"当前理解","key_variables":"关键变量","validation_signals":[],"related_projects":[],"updated_at":"YYYY-MM-DD","source_path":"03_技术主题/主题名.md"}
```

## Valuation Anchor

```markdown
# 估值锚点｜赛道名

## 使用口径
## 上市公司可比
## 一级市场可比
### 公司 / 材料 / 公开口径
### 深度交易核验（仅在必要时）
## 商业模式分层
## 我们自己的价格纪律
## 最近更新
```

For each useful observation, capture project, date, round or operating stage, stated valuation, financing amount, source context, maturity or metric denominator, and a short comparability note. Separate market/company price from internal price discipline.

Generated valuation record:

```json
{"schema_version":2,"type":"valuation_anchor","valuation_id":"valuation:...","sector":"赛道名","summary":"内部价格纪律","updated_at":"YYYY-MM-DD","source_path":"04_估值锚点/赛道名.md"}
```

## Event Card

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

Generated event record:

```json
{"schema_version":2,"type":"event","event_id":"event:...","title":"事件短名","date":"YYYY-MM-DD","primary_sector":"赛道名","tags":[],"event_type":"policy","impact":"high","source_refs":[],"source_path":"05_事件卡片/YYYY-MM-DD_事件短名.md","related_projects":[],"summary":"Why this matters."}
```

## Person Card

```markdown
# 人物卡片｜姓名或待核验称呼

- 创建日期:
- 最近更新:
- 别名:
- 身份状态: verified / partial / pending
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

Generated person record:

```json
{"schema_version":2,"type":"person","person_id":"person:...","name":"Person Name","aliases":[],"identity_status":"verified","current_org_role":"","related_projects":[],"primary_sectors":[],"tags":[],"source_tiers":["public"],"source_path":"06_人物卡片/YYYY-MM-DD_Person Name.md","updated_at":"YYYY-MM-DD","summary":"Why this person matters."}
```

## Optional Graph Delta

Use only for unresolved advanced handoff; clear updates should go directly to their target Markdown object.

```json
{
  "schema_version": 2,
  "project": "<项目名>",
  "relations_add": [],
  "sector_updates": [],
  "technical_theme_updates": [],
  "valuation_updates": [],
  "event_triggers": [],
  "person_updates": []
}
```

## Operations

```bash
python3 scripts/rebuild_indexes.py --workspace-root "<workspace_root>"
python3 scripts/validate_memory_graph.py --workspace-root "<workspace_root>"
```

To normalize an older v2 layout, first review where reusable ledger content belongs, then run:

```bash
python3 scripts/migrate_memory_graph_v2.py --workspace-root "<workspace_root>"
```

The migration archives the old thesis ledger and index, renumbers event and people folders, updates active path references, rebuilds indexes, and preserves the archived snapshot outside active retrieval.
