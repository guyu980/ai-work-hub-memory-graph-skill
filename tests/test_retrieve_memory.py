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


if __name__ == "__main__":
    unittest.main()
