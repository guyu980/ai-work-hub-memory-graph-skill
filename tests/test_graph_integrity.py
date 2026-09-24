import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ai-work-hub-memory-graph/scripts"))
from memory_graph_lib import content_date, content_hash, graph_lock, markdown_links, parse_markdown, section_entities
from rebuild_indexes import build_outputs, rebuild
from retrieve_memory import retrieve
from sync_project import compact_header, sync
from write_graph import apply_batch, target_path


class GraphTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.graph = self.root / "Memory Graph"

    def write(self, relative, text):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def test_content_date_does_not_take_future_milestone(self):
        p = self.write("topic.md", "# Topic\n- 内容截至: 2026-01-02\n\n## 当前理解\n截至2026-01-03，更新；计划2027-01-01发布")
        self.assertEqual(content_date(parse_markdown(p)), "2026-01-02")
        self.assertEqual(content_date({"fields": {}, "text": "截至2026-01-03，更新；计划2027-01-01发布"}), "2026-01-03")

    def test_links_and_cross_kind_relations(self):
        self.write("Memory Graph/03_技术主题/Cache.md", "# 技术主题｜Cache\n- 内容截至: 2026-01-01\n\n## 当前理解\nCache economics\n\n## 关联\n- [Ada](../06_人物卡片/Ada.md)：技术贡献。\n")
        self.write("Memory Graph/06_人物卡片/Ada.md", "# 人物卡片｜Ada\n\n## 一句话\nCache scientist")
        self.assertEqual(section_entities("- [Ada](../06_人物卡片/Ada.md)：技术贡献。"), ["Ada"])
        result = build_outputs(self.root, self.graph)
        self.assertEqual(result["关系索引.jsonl"][0]["relation_type"], "linked_person")
        self.assertEqual(result["技术主题索引.jsonl"][0]["updated_at"], "2026-01-01")

    def test_adjacent_links_do_not_merge_destinations(self):
        text = "[A](<../a b.md>); [B](../b.md)及[C](../c%20d.md)补充。 [D](https://example.test/a_(b))"
        self.assertEqual(markdown_links(text), [("A", "../a b.md"), ("B", "../b.md"),
                                               ("C", "../c d.md"), ("D", "https://example.test/a_(b)")])

    def test_event_sources_use_standard_source_section(self):
        self.write("Memory Graph/05_事件卡片/Event.md", "# 事件卡片｜Event\n- 内容截至: 2026-01-01\n\n## 当前影响\nA durable change\n\n## 来源\n[Official](https://example.test/notice)")
        result = build_outputs(self.root, self.graph)["事件索引.jsonl"][0]
        self.assertEqual(result["source_refs"], ["https://example.test/notice"])

    def test_batch_conflict_leaves_every_file_unchanged(self):
        a = self.write("Memory Graph/03_技术主题/A.md", "# A\nOld")
        b = self.write("Memory Graph/03_技术主题/B.md", "# B\nOld")
        staged = self.write("staged.md", "# New\n")
        changes = [{"path": p.relative_to(self.graph).as_posix(), "expected_sha256": content_hash(p), "content_file": str(staged)} for p in (a, b)]
        b.write_text("# B\nConcurrent update", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "conflict"):
            apply_batch(self.root, self.graph, changes)
        self.assertEqual(a.read_text(), "# A\nOld")
        self.assertIn("Concurrent", b.read_text())

    def test_batch_noop_and_rebuild_failure_rollback(self):
        a = self.write("Memory Graph/03_技术主题/A.md", "# A\nOld")
        staged = self.write("staged.md", "# New\n")
        change = {"path": "03_技术主题/A.md", "expected_sha256": content_hash(a), "content_file": str(a)}
        self.assertEqual(apply_batch(self.root, self.graph, [change]), 0)
        change["content_file"] = str(staged)
        with patch("write_graph.rebuild", side_effect=[RuntimeError("failed"), {}]):
            with self.assertRaises(RuntimeError):
                apply_batch(self.root, self.graph, [change])
        self.assertEqual(a.read_text(), "# A\nOld")
        self.assertEqual(apply_batch(self.root, self.graph, [change]), 1)

    def test_guard_and_reentrant_lock(self):
        with self.assertRaises(ValueError):
            target_path(self.graph, "../private.md")
        with graph_lock(self.graph):
            with graph_lock(self.graph):
                rebuild(self.root, self.graph)

    def test_process_cannot_enter_held_lock(self):
        scripts = str(Path(__file__).resolve().parents[1] / "ai-work-hub-memory-graph/scripts")
        code = f"import sys; sys.path.insert(0, {scripts!r}); from memory_graph_lib import graph_lock; from pathlib import Path\nwith graph_lock(Path({str(self.graph)!r})): print('acquired', flush=True)"
        with graph_lock(self.graph):
            proc = subprocess.Popen([sys.executable, "-c", code], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            with self.assertRaises(subprocess.TimeoutExpired):
                proc.communicate(timeout=0.2)
        out, err = proc.communicate(timeout=5)
        self.assertEqual(proc.returncode, 0, err)
        self.assertEqual(out.strip(), "acquired")

    def test_compact_header_keeps_body_not_sources_or_duplicate_decision_fields(self):
        text = compact_header({"schema_version": 2, "name": "Sample", "source_refs": ["long.md"], "judgment_display": "continue"}, "# 项目卡片｜Sample\n\n## 一句话\nUseful thesis", "项目/Sample/state.json")
        self.assertIn("Useful thesis", text)
        self.assertNotIn("long.md", text)
        self.assertIn("当前投资判断: continue", text)

    def test_retrieve_radar_and_running_judgment_total_limit(self):
        self.write("自动化归档/Radar/2026_projects.json", json.dumps({"projects": [{"repo": "acme/cache", "startup_entities": [{"name": "CacheWorks"}]}]}))
        self.write("项目/CacheWorks/输出文档/CacheWorks_项目判断与todo.md", "# CacheWorks\nA cache business")
        result = retrieve(self.root, self.graph, "CacheWorks", 1)
        self.assertEqual(sum(len(v) for k, v in result.items() if isinstance(v, list) and k != "related"), 1)
        result = retrieve(self.root, self.graph, "CacheWorks", 5)
        self.assertEqual(len(result["radar_candidates"]), 1)
        self.assertEqual(len(result["project_judgments"]), 1)

    def test_sync_preserves_judgment_and_writer_rejects_formal_change(self):
        original = {"schema_version": 2, "name": "CacheWorks", "project_id": "project:CacheWorks",
                    "created_at": "2026-01-01", "updated_at": "2026-01-02", "project_status": "active",
                    "investment_decision": "continue", "judgment_display": "continue", "summary": "Cache business"}
        state = self.write("项目/CacheWorks/state.json", json.dumps(original))
        card = sync(self.root, self.graph, state)
        self.assertEqual(json.loads(state.read_text())["investment_decision"], "continue")
        self.assertIn("Cache business", card.read_text())
        self.assertNotIn("## 风险", card.read_text())
        staged = self.write("staged.md", card.read_text().replace("当前投资判断: continue", "当前投资判断: invest"))
        change = {"path": card.relative_to(self.graph.resolve()).as_posix(), "expected_sha256": content_hash(card), "content_file": str(staged)}
        with self.assertRaisesRegex(ValueError, "conflicts with formal state"):
            apply_batch(self.root, self.graph, [change])
        self.assertIn("当前投资判断: continue", card.read_text())
        self.assertEqual(json.loads(state.read_text())["judgment_display"], "continue")

    def test_validator_detects_stale_index(self):
        topic = self.write("Memory Graph/03_技术主题/Cache.md", "# 技术主题｜Cache\n- 内容截至: 2026-01-01\n\n## 当前理解\nOld understanding")
        rebuild(self.root, self.graph)
        script = Path(__file__).resolve().parents[1] / "ai-work-hub-memory-graph/scripts/validate_memory_graph.py"
        args = [sys.executable, str(script), "--workspace-root", str(self.root)]
        self.assertEqual(subprocess.run(args, capture_output=True).returncode, 0)
        topic.write_text(topic.read_text().replace("Old", "New"), encoding="utf-8")
        result = subprocess.run(args, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("stale generated index", result.stdout)

    def test_source_link_is_retrievable_and_direct_matches_not_repeated(self):
        self.write("Memory Graph/03_技术主题/Cache.md", "# 技术主题｜Cache\n\n## 当前理解\nCache economics\n\n## 来源\n[Interview](../../知识来源/2026_核心整理.md)\n")
        self.write("知识来源/2026_核心整理.md", "# Expert interview\nHiddenCache insight")
        rebuild(self.root, self.graph)
        result = retrieve(self.root, self.graph, "Cache", 1)
        self.assertEqual(result["related"][0]["record"]["type"], "knowledge_source")
        result = retrieve(self.root, self.graph, "Cache HiddenCache", 8)
        self.assertEqual(result["related"], [])

    def test_generic_founder_does_not_match_unrelated_people(self):
        self.write("Memory Graph/06_人物卡片/Unrelated.md", "# 人物卡片｜Unrelated\n\n## 一句话\nAI 公司创始人")
        self.write("自动化归档/Radar/2026_projects.json", json.dumps({"projects": [{"repo": "acme/cache", "startup_entities": [{"name": "CacheWorks", "founder": "Ada"}]}]}))
        result = retrieve(self.root, self.graph, "CacheWorks 创始人 公司", 8)
        self.assertEqual(result["people"], [])
        self.assertEqual(len(result["radar_candidates"]), 1)


if __name__ == "__main__":
    unittest.main()
