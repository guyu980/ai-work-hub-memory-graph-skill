import json
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ai-work-hub-memory-graph" / "scripts"))
from retrieve_memory import retrieve


class RetrievalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.graph = self.root / "Memory Graph"

    def write(self, path, content):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def query(self, query, limit=3):
        return retrieve(self.root, self.graph, query, limit)

    def test_body_only_valuation_and_unindexed_card(self):
        self.write("Memory Graph/04_估值锚点/Software.md", "# Software\n\nQuartzSample financing announced.")
        result = self.query("QuartzSample")["valuation_anchors"]
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["match_line"], 3)
        self.assertIn("QuartzSample", result[0]["match_excerpt"])
        self.assertNotIn("_body", result[0])

    def test_source_and_report_but_not_raw_or_working_files(self):
        self.write("知识来源/专家访谈/2026/example/2026-01-01_核心整理.md", "# Sample interview\n缓存 economics")
        self.write("知识来源/专家访谈/2026/example/解析文本/raw.md", "缓存 raw-only")
        self.write("行业研究/Sample/输出文档/report.md", "# Study\n缓存 economics")
        self.write("行业研究/Sample/输出文档/工作区/temporary.md", "缓存 work-only")
        self.write("项目/Sample/输出文档/03_研究与分析/report.md", "# Linked study\n缓存 economics")
        result = self.query("缓存")
        self.assertEqual(len(result["knowledge_sources"]), 1)
        self.assertEqual(len(result["research_reports"]), 2)
        self.assertEqual(result["knowledge_sources"][0]["source_scope"], "workspace_root")

    def test_one_hop_does_not_recursively_expand(self):
        records = [{"name": name, "project_id": "project:" + name,
                    "source_path": "01_项目卡片/" + name + ".md"} for name in ("Quartz", "Cedar", "Birch")]
        relations = [{"from_id": "project:" + a, "to_id": "project:" + b,
                      "relation_type": "comparable_to"} for a, b in (("Quartz", "Cedar"), ("Cedar", "Birch"))]
        self.write("Memory Graph/00_索引/项目索引.jsonl", "\n".join(json.dumps(r) for r in records))
        self.write("Memory Graph/00_索引/关系索引.jsonl", "\n".join(json.dumps(r) for r in relations))
        result = self.query("Quartz")
        self.assertEqual([r["record"]["name"] for r in result["related"]], ["Cedar"])
        reverse = self.query("Birch")
        self.assertEqual([r["record"]["name"] for r in reverse["related"]], ["Cedar"])

    def test_source_path_cannot_escape_root(self):
        self.write("outside.md", "ConfidentialTerm")
        self.write("Memory Graph/00_索引/估值索引.jsonl", json.dumps({"sector": "Example", "source_path": "../outside.md"}))
        self.assertEqual(self.query("ConfidentialTerm")["valuation_anchors"], [])

    def test_empty_unknown_and_limit(self):
        self.assertEqual(self.query("unknown")["projects"], [])
        self.assertEqual(self.query("")["related"], [])
        with self.assertRaises(ValueError):
            self.query("query", 0)
        for i in range(4):
            self.write(f"Memory Graph/03_技术主题/{i}.md", "# SearchTerm")
        self.assertEqual(len(self.query("SearchTerm", 2)["technical_themes"]), 2)

    def test_source_initializer_preserves_user_note_on_repeat(self):
        script = Path(__file__).resolve().parents[1] / "ai-work-hub-memory-graph/scripts/init_knowledge_source.py"
        args = [sys.executable, str(script), "--workspace-root", str(self.root),
                "--kind", "expert-interview", "--date", "2026-01-01",
                "--name", "Example", "--topic", "Cache economics"]
        self.assertEqual(subprocess.run(args, capture_output=True).returncode, 0)
        note = next(self.root.glob("知识来源/**/*核心整理.md"))
        note.write_text("User-maintained analysis", encoding="utf-8")
        self.assertEqual(subprocess.run(args, capture_output=True).returncode, 0)
        self.assertEqual(note.read_text(), "User-maintained analysis")

    def test_generic_prefix_is_not_a_company_alias(self):
        self.write("Memory Graph/01_项目卡片/Storage.md", '# 项目卡片｜Storage\n- 别名: ["数据基座"]\n\n数据客户复用权利。')
        self.write("Memory Graph/00_索引/项目索引.jsonl", json.dumps({"name": "Storage", "aliases": ["数据基座"], "source_path": "01_项目卡片/Storage.md"}))
        self.write("Memory Graph/03_技术主题/Touch.md", "# 触觉数据\n\n## 当前理解\n触觉数据权利决定跨客户复用。")
        result = self.query("触觉 数据 权利 跨客户复用", 1)
        self.assertEqual(len(result["technical_themes"]), 1)
        self.assertEqual(result["projects"], [])

    def test_company_name_does_not_match_substring_of_another_name(self):
        self.write("Memory Graph/01_项目卡片/Acorn.md", "# Acorn\nAcorn customer")
        self.write("Memory Graph/01_项目卡片/Acornish.md", "# Acornish\nAcornish customer")
        self.assertEqual([p["title"] for p in self.query("Acorn", 8)["projects"]], ["Acorn"])

    def test_running_state_date_and_dated_source_fallback(self):
        self.write("项目/Acorn/输出文档/Acorn_项目判断与todo.md", "# Acorn\n\n## History\n截至2025-01-01，历史收入。")
        self.write("项目/Acorn/输出文档/Acorn_项目状态.json", json.dumps({"name": "Acorn", "updated_at": "2026-01-03"}))
        self.write("知识来源/2026-01-02_核心整理.md", "# Acorn interview\nAn Acorn mechanism")
        result = self.query("Acorn", 8)
        self.assertEqual(result["project_judgments"][0]["updated_at"], "2026-01-03")
        self.assertEqual(result["project_judgments"][0]["date_basis"], "project_state")
        self.assertEqual(result["knowledge_sources"][0]["updated_at"], "2026-01-02")
        self.assertEqual(result["knowledge_sources"][0]["date_basis"], "filename")

    def test_later_sourcing_review_is_retrievable_without_new_cards(self):
        self.write("自动化归档/Radar/2026_projects.json", json.dumps({"generated_at": "2026-01-01", "projects": [{"repo": "acorn/search", "startup_entities": [{"name": "Acorn"}]}]}))
        self.write("自动化归档/跨任务复盘/2026-01-03_review_数据.json", json.dumps({"as_of": "2026-01-03", "candidates": [{"id": "A01", "name": "Acorn", "aliases": ["Acorn Search"], "repos": ["acorn/search"], "people": "Ada", "action": "Meet Ada about repeat purchases"}]}))
        result = self.query("Acorn", 8)
        self.assertEqual(result["sourcing_reviews"][0]["updated_at"], "2026-01-03")
        self.assertEqual(result["sourcing_reviews"][0]["entry_key"], "A01")
        self.assertEqual(result["sourcing_reviews"][0]["type"], "sourcing_review")
        self.assertEqual(result["related"], [])

    def test_similar_report_versions_do_not_use_two_result_slots(self):
        text = "# Cache industry\n\n## Main view\nCache pricing depends on repeated purchases.\n"
        self.write("行业研究/Cache/输出文档/2026-01-03_report.md", text)
        self.write("项目/Cache/输出文档/03_研究与分析/2026-01-01_report.md", text)
        result = self.query("Cache", 8)["research_reports"]
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["updated_at"], "2026-01-03")
        self.assertEqual(len(result[0]["other_versions"]), 1)

    def test_generic_company_suffix_does_not_pull_unrelated_leads(self):
        self.write("Memory Graph/01_项目卡片/Acorn Labs.md", "# Acorn Labs\nAcorn Labs company")
        self.write("自动化归档/跨任务复盘/2026-01-03_review_数据.json", json.dumps({
            "as_of": "2026-01-03", "candidates": [{"name": "Beacon Labs", "action": "Meet the team"}]}))
        result = self.query("Acorn Labs 团队", 8)
        self.assertEqual(result["sourcing_reviews"], [])

    def test_same_intro_does_not_merge_distinct_report_questions(self):
        intro = "# Cache industry\n\n" + "Common background.\n" * 150
        self.write("行业研究/Cache/输出文档/2026-01-03_report.md", intro + "Buyer economics.\n" * 150)
        self.write("项目/Cache/输出文档/03_研究与分析/2026-01-01_report.md", intro + "Technology tradeoffs.\n" * 150)
        self.assertEqual(len(self.query("Cache", 8)["research_reports"]), 2)

    def test_information_unique_to_an_older_version_stays_searchable(self):
        text = "# Cache industry\n\n" + "Cache pricing and customer economics.\n" * 40
        self.write("行业研究/Cache/输出文档/2026-01-03_report.md", text)
        self.write("行业研究/Cache/输出文档/2026-01-01_report.md", text + "LegacySensor mechanism.\n")
        result = self.query("LegacySensor", 8)["research_reports"]
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["updated_at"], "2026-01-01")
        self.assertEqual(result[0]["other_versions"][0]["updated_at"], "2026-01-03")


if __name__ == "__main__":
    unittest.main()
