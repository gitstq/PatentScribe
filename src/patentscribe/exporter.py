"""导出器：把结构化交底书渲染为 Markdown / HTML / DOCX。

* Markdown：纯文本，便于 Git 版本管理；
* HTML：自包含单文件（内联样式，无外链）；
* DOCX：仅用标准库 ``zipfile`` 拼装最小可用的 OOXML 文档，
  可直接用 Microsoft Word / WPS / LibreOffice 打开编辑。
"""

from __future__ import annotations

import html as _html
import zipfile
from pathlib import Path
from typing import Dict, List, Union

from .claim_parser import analyze_claims, parse_claims
from .models import CheckReport, Disclosure, Severity

PathLike = Union[str, Path]


# ----------------------------------------------------------------------
# 公共工具
# ----------------------------------------------------------------------
def _claims_numbered(disclosure: Disclosure) -> List[str]:
    claims = parse_claims(disclosure.claims_text)
    if claims:
        return [f"{c.number}. {c.text}" for c in claims]
    # 没有解析出编号时原样返回非空行
    return [line.strip() for line in disclosure.claims_text.splitlines() if line.strip()]


def _section_blocks(disclosure: Disclosure) -> List[tuple[str, str]]:
    """统一的章节顺序（标题层级，正文）。"""
    problems = "\n".join(f"- {p}" for p in disclosure.problems)
    effects = "\n".join(f"- {e}" for e in disclosure.effects)
    drawings = "\n".join(
        f"- **{d.get('figure', '')}**：{d.get('desc', '')}"
        + (f"（标记：{d.get('marks')}）" if d.get("marks") else "")
        for d in disclosure.drawings
    )
    blocks = [
        ("一、技术领域", disclosure.field),
        ("二、背景技术", disclosure.background),
        ("三、现有技术存在的问题", problems),
        ("四、技术方案（发明内容）", disclosure.solution),
        ("五、有益效果", effects),
        ("六、附图说明", drawings),
        ("七、具体实施方式", disclosure.embodiments),
    ]
    return blocks


# ----------------------------------------------------------------------
# Markdown
# ----------------------------------------------------------------------
def to_markdown(disclosure: Disclosure, report: CheckReport | None = None) -> str:
    lines: List[str] = []
    lines.append(f"# 技术交底书：{disclosure.title or '（未命名）'}")
    meta = [
        f"- 专利类型：{disclosure.patent_type}",
        f"- 发明人：{'、'.join(disclosure.inventors) if disclosure.inventors else '（待补充）'}",
        f"- 核心关键词：{ '、'.join(disclosure.keywords) if disclosure.keywords else '（待补充）'}",
    ]
    lines.extend(meta)
    lines.append("")
    for heading, body in _section_blocks(disclosure):
        lines.append(f"## {heading}")
        lines.append(body if body else "（待补充）")
        lines.append("")

    lines.append("## 八、权利要求书")
    for item in _claims_numbered(disclosure):
        lines.append(item)
    lines.append("")
    lines.append("## 九、摘要")
    lines.append(disclosure.abstract or "（待补充）")
    lines.append("")

    claims = parse_claims(disclosure.claims_text)
    if claims:
        graph, _ = analyze_claims(claims)
        lines.append("## 附：权利要求依赖树")
        lines.append("```text")
        lines.append(graph.render_tree() or "（无）")
        lines.append("```")
        lines.append("")

    if report is not None:
        lines.append("## 附：自检结果")
        lines.append(
            f"- 错误 {len(report.errors)} 项 / 警告 {len(report.warnings)} 项 / "
            f"提示 {len(report.infos)} 项 / 结论：{'通过' if report.passed else '未通过'}"
        )
        for issue in report.issues:
            lines.append(
                f"- [{issue.severity.label_cn}][{issue.code}] {issue.location}："
                f"{issue.message}"
                + (f"（建议：{issue.suggestion}）" if issue.suggestion else "")
            )
    return "\n".join(lines).rstrip() + "\n"


# ----------------------------------------------------------------------
# HTML（自包含）
# ----------------------------------------------------------------------
_HTML_STYLE = """
:root{--ink:#1f2933;--muted:#667085;--brand:#0e7a5f;--bg:#f7f9fa;--card:#fff;--err:#c0392b;--warn:#b7791f;--info:#2b6cb0;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;line-height:1.75}
.wrap{max-width:860px;margin:0 auto;padding:40px 28px}
h1{font-size:26px;border-bottom:3px solid var(--brand);padding-bottom:12px}
h2{font-size:19px;margin-top:34px;color:var(--brand)}
.meta{background:var(--card);border:1px solid #e4e9ee;border-radius:10px;padding:14px 20px}
.meta li{margin:2px 0}
.section{background:var(--card);border:1px solid #e4e9ee;border-radius:10px;padding:6px 20px 14px;white-space:pre-wrap}
.claim{background:var(--card);border-left:4px solid var(--brand);margin:10px 0;padding:10px 16px;border-radius:6px}
pre.tree{background:#0f172a;color:#d7e3f0;padding:16px;border-radius:10px;overflow:auto;font-size:13px}
.tag{display:inline-block;border-radius:6px;padding:0 8px;font-size:12px;color:#fff;margin-right:8px}
.t-error{background:var(--err)}.t-warn{background:var(--warn)}.t-info{background:var(--info)}
.issue{background:var(--card);border:1px solid #e4e9ee;border-radius:8px;padding:8px 14px;margin:8px 0}
footer{margin-top:40px;color:var(--muted);font-size:12px;text-align:center}
"""


def to_html(disclosure: Disclosure, report: CheckReport | None = None) -> str:
    e = _html.escape
    parts: List[str] = []
    parts.append("<!DOCTYPE html><html lang='zh-CN'><head><meta charset='utf-8'>")
    parts.append("<meta name='viewport' content='width=device-width,initial-scale=1'>")
    parts.append(f"<title>{e(disclosure.title or '技术交底书')}</title>")
    parts.append(f"<style>{_HTML_STYLE}</style></head><body><div class='wrap'>")
    parts.append(f"<h1>技术交底书：{e(disclosure.title or '（未命名）')}</h1>")
    parts.append("<ul class='meta'>")
    parts.append(f"<li>专利类型：{e(disclosure.patent_type)}</li>")
    parts.append(f"<li>发明人：{e('、'.join(disclosure.inventors) or '（待补充）')}</li>")
    parts.append(f"<li>核心关键词：{e('、'.join(disclosure.keywords) or '（待补充）')}</li>")
    parts.append("</ul>")

    for heading, body in _section_blocks(disclosure):
        parts.append(f"<h2>{e(heading)}</h2>")
        parts.append(f"<div class='section'>{e(body or '（待补充）')}</div>")

    parts.append("<h2>八、权利要求书</h2>")
    for item in _claims_numbered(disclosure):
        parts.append(f"<div class='claim'>{e(item)}</div>")

    parts.append("<h2>九、摘要</h2>")
    parts.append(f"<div class='section'>{e(disclosure.abstract or '（待补充）')}</div>")

    claims = parse_claims(disclosure.claims_text)
    if claims:
        graph, _ = analyze_claims(claims)
        parts.append("<h2>附：权利要求依赖树</h2>")
        parts.append(f"<pre class='tree'>{e(graph.render_tree() or '（无）')}</pre>")

    if report is not None:
        parts.append("<h2>附：自检结果</h2>")
        badge = "通过" if report.passed else "未通过"
        parts.append(
            f"<p>错误 <b>{len(report.errors)}</b> · 警告 <b>{len(report.warnings)}</b> · "
            f"提示 <b>{len(report.infos)}</b> · 结论：<b>{badge}</b></p>"
        )
        cls = {Severity.ERROR: "t-error", Severity.WARN: "t-warn", Severity.INFO: "t-info"}
        for issue in report.issues:
            parts.append(
                "<div class='issue'>"
                f"<span class='tag {cls[issue.severity]}'>{issue.severity.label_cn}</span>"
                f"<b>[{e(issue.code)}] {e(issue.location)}</b>：{e(issue.message)}"
                + (f"<br><small>建议：{e(issue.suggestion)}</small>" if issue.suggestion else "")
                + "</div>"
            )
    parts.append("<footer>由 PatentScribe 离线生成 · Zero-dependency · No LLM</footer>")
    parts.append("</div></body></html>")
    return "".join(parts)


# ----------------------------------------------------------------------
# DOCX（标准库拼装 OOXML）
# ----------------------------------------------------------------------
def _xml_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _para(text: str, style: str | None = None) -> str:
    ppr = f"<w:pPr><w:pStyle w:val='{style}'/></w:pPr>" if style else ""
    runs = []
    for i, line in enumerate(text.split("\n")):
        if i:
            runs.append("<w:r><w:br/></w:r>")
        runs.append(
            "<w:r><w:rPr><w:rFonts w:eastAsia='宋体'/></w:rPr>"
            f"<w:t xml:space='preserve'>{_xml_escape(line) or ' '}</w:t></w:r>"
        )
    return f"<w:p>{ppr}{''.join(runs)}</w:p>"


def _document_xml(disclosure: Disclosure) -> str:
    body: List[str] = []
    body.append(_para(f"技术交底书：{disclosure.title or '（未命名）'}", "Title"))
    body.append(_para(f"专利类型：{disclosure.patent_type}"))
    body.append(_para(f"发明人：{'、'.join(disclosure.inventors) or '（待补充）'}"))
    body.append(_para(f"关键词：{'、'.join(disclosure.keywords) or '（待补充）'}"))
    for heading, text in _section_blocks(disclosure):
        body.append(_para(heading, "Heading1"))
        body.append(_para(text or "（待补充）"))
    body.append(_para("八、权利要求书", "Heading1"))
    for item in _claims_numbered(disclosure):
        body.append(_para(item))
    body.append(_para("九、摘要", "Heading1"))
    body.append(_para(disclosure.abstract or "（待补充）"))
    return (
        "<?xml version='1.0' encoding='UTF-8' standalone='yes'?>"
        "<w:document xmlns:w='http://schemas.openxmlformats.org/wordprocessingml/2006/main'>"
        f"<w:body>{''.join(body)}"
        "<w:sectPr><w:pgSz w:w='11906' w:h='16838'/>"
        "<w:pgMar w:top='1440' w:right='1440' w:bottom='1440' w:left='1440'/>"
        "</w:sectPr></w:body></w:document>"
    )


_STYLES_XML = """<?xml version='1.0' encoding='UTF-8' standalone='yes'?>
<w:styles xmlns:w='http://schemas.openxmlformats.org/wordprocessingml/2006/main'>
<w:style w:type='paragraph' w:styleId='Title'><w:name w:val='Title'/>
<w:pPr><w:jc w:val='center'/></w:pPr>
<w:rPr><w:b/><w:sz w:val='36'/><w:rFonts w:eastAsia='黑体'/></w:rPr></w:style>
<w:style w:type='paragraph' w:styleId='Heading1'><w:name w:val='heading 1'/>
<w:rPr><w:b/><w:sz w:val='28'/><w:color w:val='0E7A5F'/><w:rFonts w:eastAsia='黑体'/></w:rPr></w:style>
</w:styles>"""

_CONTENT_TYPES = """<?xml version='1.0' encoding='UTF-8' standalone='yes'?>
<Types xmlns='http://schemas.openxmlformats.org/package/2006/content-types'>
<Default Extension='rels' ContentType='application/vnd.openxmlformats-package.relationships+xml'/>
<Default Extension='xml' ContentType='application/xml'/>
<Override PartName='/word/document.xml' ContentType='application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml'/>
<Override PartName='/word/styles.xml' ContentType='application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml'/>
</Types>"""

_RELS = """<?xml version='1.0' encoding='UTF-8' standalone='yes'?>
<Relationships xmlns='http://schemas.openxmlformats.org/package/2006/relationships'>
<Relationship Id='rId1' Type='http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument' Target='word/document.xml'/>
</Relationships>"""

_DOC_RELS = """<?xml version='1.0' encoding='UTF-8' standalone='yes'?>
<Relationships xmlns='http://schemas.openxmlformats.org/package/2006/relationships'>
<Relationship Id='rId1' Type='http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles' Target='styles.xml'/>
</Relationships>"""


def to_docx(disclosure: Disclosure, path: PathLike) -> Path:
    """生成最小可用的 .docx，返回写入路径。"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", _CONTENT_TYPES)
        zf.writestr("_rels/.rels", _RELS)
        zf.writestr("word/_rels/document.xml.rels", _DOC_RELS)
        zf.writestr("word/styles.xml", _STYLES_XML)
        zf.writestr("word/document.xml", _document_xml(disclosure))
    return path
