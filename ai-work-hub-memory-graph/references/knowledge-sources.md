# Non-Project Knowledge Sources

Use this contract when a useful source does not belong to one investment project.

## Ownership Boundary

| Material | Owner |
| --- | --- |
| BP, company datapack, company or customer call about one company | `项目/<项目名>/` through Diligence |
| Formal systematic report with an enduring research object | `行业研究/<主题>/` through Deep Research |
| Expert interview, meeting, course, podcast, institution note, or thematic material with reusable value | `知识来源/` through this skill |
| Low-value or disposable input | Keep in the current task only; do not persist it |

Store a source once. Other project, research, and graph files link to its core note or original material rather than copying it.

## Layout

```text
知识来源/
  README.md
  专家访谈/
    YYYY/
      YYYY-MM-DD_专家_主题/
        原始资料/
        解析文本/
        YYYY-MM-DD_核心整理.md
        工作区/                    # optional
  主题资料/
    YYYY/
      YYYY-MM-DD_来源主体_主题/
        原始资料/
        解析文本/
        YYYY-MM-DD_核心整理.md
        工作区/                    # optional
  templates/
    核心整理模板.md
```

`原始资料/` owns the supplied files or links. `解析文本/` owns extracted text, including the original Feishu transcript when available. `工作区/` is optional and may hold temporary analysis artifacts.

## Analysis Contract

Memory Graph Skill is the default entry point and performs the lightweight source analysis:

1. Preserve enough source context to understand who said what and when.
2. For interviews, organize the main questions and answers close to the original wording.
3. Extract three to seven decision-relevant takeaways, not a paragraph-by-paragraph recap.
4. Preserve the original link and separate verified facts, source opinions, and unresolved claims.
5. State what prior understanding was reinforced, revised, or contradicted.
6. Record reusable implications and the few follow-up questions that matter.
7. Link any actual graph writeback; do not create one graph card per source.

Use Diligence only when the source changes the judgment of a specific project. Use Deep Research when external search, cross-source validation, or a systematic thematic report is needed.

## Feishu Sources

When the source is a Feishu link, follow the available Feishu CLI workflow and retrieve the original transcript or document body. Smart minutes may help navigation but are not a substitute for the original content. Preserve the source link in the core note.

## Writeback Threshold

The source note is durable even when it creates no graph update. Write to Memory Graph only when the source adds a reusable change to an existing project, sector, technical theme, valuation anchor, durable event, or independently important person.

Do not add a knowledge-source card type or generated source index in the MVP. Ordinary interview statements are not event cards, and ordinary participants are not people cards.
