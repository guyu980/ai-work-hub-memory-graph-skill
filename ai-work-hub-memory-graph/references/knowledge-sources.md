# Non-Project Knowledge Sources

Use this contract when a useful source does not belong to one investment project.

## Ownership Boundary

| Material | Owner |
| --- | --- |
| BP, company datapack, company or customer call about one company | `项目/<项目名>/` through Diligence |
| Formal systematic report with an enduring research object | `行业研究/<主题>/` through Deep Research |
| Expert interview, meeting, course, podcast, institution note, or thematic material with reusable value | `知识来源/` through this skill |
| Low-value or disposable input, or an explicit user request not to save | Keep in the current task only; do not persist it |

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

Memory Graph Skill is the default entry point and performs substantive, decision-oriented source analysis. Requests to look, organize, summarize, analyze, or prepare follow-ups still persist a reusable source unless the user explicitly says not to save.

1. Preserve enough source context to understand who said what and when.
2. For interviews, organize the main questions and answers close to the original wording while correcting obvious transcription errors transparently.
3. Retrieve relevant Memory Graph objects and prior source notes before finalizing the analysis.
4. Extract three to seven decision-relevant takeaways and explain the technical or commercial mechanisms behind them; do not stop at a paragraph-by-paragraph recap.
5. Preserve the original link and separate verified facts, source opinions, unresolved claims, and transcription risks.
6. State what prior understanding was reinforced, revised, or contradicted and which projects or investment themes may be affected.
7. Record reusable implications and the few follow-up questions that can change a decision.
8. Link any actual graph writeback; do not create one graph card per source.

Use Diligence only when the source changes the judgment of a specific project. Bounded public calibration is allowed inside this workflow. Use Deep Research only when the user explicitly requests deep research, a formal systematic report, market sizing, competitive mapping, or broad cross-source validation.

## Feishu Sources

When the source is a Feishu link, follow the available Feishu CLI workflow and retrieve the original transcript or document body. Smart minutes may help navigation but are not a substitute for the original content. Preserve the source link in the core note.

## Writeback Threshold

The source note is durable even when it creates no graph update. Write to Memory Graph only when the source adds a reusable change to an existing project, sector, technical theme, valuation anchor, durable event, or independently important person.

Do not add a knowledge-source card type or generated source index in the MVP. Ordinary interview statements are not event cards, and ordinary participants are not people cards.
