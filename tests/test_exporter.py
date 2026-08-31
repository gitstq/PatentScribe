import tempfile
import unittest
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

from patentscribe.builder import dump_template
from patentscribe.exporter import to_docx, to_html, to_markdown
from patentscribe.linter import lint_disclosure
from patentscribe.models import Disclosure


class TestExporter(unittest.TestCase):
    def setUp(self):
        self.d = Disclosure.from_dict(dump_template("发明"))

    def test_markdown_sections(self):
        md = to_markdown(self.d)
        for heading in ("技术领域", "背景技术", "技术方案", "具体实施方式", "权利要求书", "摘要"):
            self.assertIn(heading, md)
        # 权项编号被重新输出
        self.assertIn("1. ", md)
        self.assertIn("依赖树", md)

    def test_markdown_with_report(self):
        report = lint_disclosure(self.d)
        md = to_markdown(self.d, report)
        self.assertIn("自检结果", md)
        self.assertIn("通过", md)

    def test_html_self_contained(self):
        self.d.title = "测试<X>组件&模块"
        html = to_html(self.d)
        self.assertTrue(html.startswith("<!DOCTYPE html>"))
        # 无外链资源
        self.assertNotIn("src='http", html)
        self.assertNotIn('href="http', html)
        # HTML 转义生效，防止破坏页面结构
        self.assertIn("&lt;X&gt;", html)
        self.assertIn("&amp;", html)

    def test_docx_valid_zip_and_xml(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = to_docx(self.d, Path(tmp) / "a.docx")
            self.assertTrue(path.exists())
            with zipfile.ZipFile(path) as zf:
                names = zf.namelist()
                self.assertIn("[Content_Types].xml", names)
                self.assertIn("word/document.xml", names)
                # 所有 XML 部件必须可被标准 XML 解析器解析
                for name in names:
                    if name.endswith(".xml") or name.endswith(".rels"):
                        ET.fromstring(zf.read(name))
                doc = zf.read("word/document.xml").decode("utf-8")
                self.assertIn("技术交底书", doc)

    def test_docx_creates_parent_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = to_docx(self.d, Path(tmp) / "nested" / "deep" / "a.docx")
            self.assertTrue(path.exists())


if __name__ == "__main__":
    unittest.main()
