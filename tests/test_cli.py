import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

from patentscribe.cli import main


NOTES = """现有技术在高并发场景下存在请求排队时间长、资源利用率低的问题。
本发明通过引入动态权重调度器对请求进行实时分流。
从而将平均响应延迟降低40%，提升吞吐量。
"""


class TestCLI(unittest.TestCase):
    def run_cli(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_version(self):
        with self.assertRaises(SystemExit) as cm:
            self.run_cli(["--version"])
        self.assertEqual(cm.exception.code, 0)

    def test_init_lint_export_report_flow(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            disc = tmp / "disclosure.json"
            code, _, _ = self.run_cli(["init", "-o", str(disc)])
            self.assertEqual(code, 0)
            self.assertTrue(disc.exists())

            code, out, _ = self.run_cli(["lint", "-i", str(disc), "--no-color"])
            self.assertEqual(code, 0, msg=out)
            self.assertIn("结论", out)

            code, out, _ = self.run_cli(["claims", "-i", str(disc), "--no-color"])
            self.assertEqual(code, 0)
            self.assertIn("依赖树", out)

            code, out, _ = self.run_cli([
                "export", "-i", str(disc), "-f", "all", "-o", str(tmp / "dist"),
                "--name", "demo", "--with-check",
            ])
            self.assertEqual(code, 0)
            for ext in ("md", "html", "docx"):
                self.assertTrue((tmp / "dist" / f"demo.{ext}").exists())

            report = tmp / "report.md"
            code, _, _ = self.run_cli(["report", "-i", str(disc), "-o", str(report)])
            self.assertEqual(code, 0)
            self.assertTrue(report.exists())

    def test_lint_json_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            disc = Path(tmp) / "d.json"
            self.run_cli(["init", "-o", str(disc)])
            code, out, _ = self.run_cli(["lint", "-i", str(disc), "--json"])
            payload = json.loads(out)
            self.assertIn("passed", payload)
            self.assertIn("issues", payload)

    def test_lint_failure_exit_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.json"
            bad.write_text(json.dumps({
                "title": "", "patent_type": "玄学",
                "claims_text": "1. 根据权利要求9所述的方法，其特征在于，包括A。",
            }), encoding="utf-8")
            code, out, _ = self.run_cli(["lint", "-i", str(bad), "--no-color"])
            self.assertEqual(code, 1)
            self.assertIn("L104", out)

    def test_mine_skeleton(self):
        with tempfile.TemporaryDirectory() as tmp:
            note = Path(tmp) / "note.txt"
            note.write_text(NOTES, encoding="utf-8")
            skel = Path(tmp) / "skeleton.json"
            code, _, err = self.run_cli([
                "mine", "-i", str(note), "--skeleton", "-o", str(skel),
            ])
            self.assertEqual(code, 0)
            self.assertTrue(skel.exists())
            data = json.loads(skel.read_text(encoding="utf-8"))
            self.assertIn("problems", data)

    def test_novelty_flow(self):
        with tempfile.TemporaryDirectory() as tmp:
            disc = Path(tmp) / "d.json"
            self.run_cli(["init", "-o", str(disc)])
            prior = Path(tmp) / "prior.txt"
            prior.write_text("一种数据处理方法，包括获取待处理数据并执行滤波处理。", encoding="utf-8")
            code, out, _ = self.run_cli(["novelty", "-i", str(disc), "-p", str(prior)])
            self.assertEqual(code, 0)
            self.assertIn("包含度", out)

    def test_missing_file_exit_code(self):
        code, _, err = self.run_cli(["lint", "-i", "/no/such/file.json"])
        self.assertEqual(code, 2)
        self.assertIn("不存在", err)


if __name__ == "__main__":
    unittest.main()
