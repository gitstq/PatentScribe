"""PatentScribe 命令行入口。

子命令一览：
  init       生成交底书 JSON 模板
  mine       从技术笔记中挖掘发明点，生成交底书骨架
  lint       形式审查 + 权要自检，输出问题清单
  claims     解析权利要求并输出依赖树
  novelty    与对比文件做术语重合度比对
  export     导出 markdown / html / docx
  report     生成完整自检报告（Markdown）
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Sequence

from . import __version__
from .builder import dump_template, load_disclosure, save_json
from .claim_parser import analyze_claims, parse_claims
from .exporter import to_docx, to_html, to_markdown
from .linter import lint_disclosure
from .miner import mine_text
from .models import Severity
from .novelty import compare_prior_art

# ANSI 颜色（可被 --no-color 关闭）
_COLORS = {
    Severity.ERROR: "\033[31m",
    Severity.WARN: "\033[33m",
    Severity.INFO: "\033[34m",
}
_RESET = "\033[0m"


# ----------------------------------------------------------------------
# 输出辅助
# ----------------------------------------------------------------------
def _print_issues(issues, use_color: bool) -> None:
    for issue in issues:
        color = _COLORS[issue.severity] if use_color else ""
        reset = _RESET if use_color else ""
        print(
            f"{color}[{issue.severity.label_cn}][{issue.code}]{reset} "
            f"{issue.location} — {issue.message}"
        )
        if issue.suggestion:
            print(f"        建议：{issue.suggestion}")


def _read_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


# ----------------------------------------------------------------------
# 子命令实现
# ----------------------------------------------------------------------
def cmd_init(args: argparse.Namespace) -> int:
    template = dump_template(args.type)
    out = Path(args.output)
    save_json(template, out)
    print(f"已生成交底书模板：{out}（类型：{args.type}）")
    print("下一步：填写后运行 `patentscribe lint -i <file>` 自检。")
    return 0


def cmd_mine(args: argparse.Namespace) -> int:
    text = _read_text(args.input)
    result = mine_text(text, patent_type=args.type)
    if args.format == "json":
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        print("=== 候选发明点（问题 → 手段 → 效果） ===")
        for ip in result.inventive_points:
            print(f"[{ip['id']}] 手段：{ip['technical_means']}")
            if ip["solves"]:
                print(f"      解决：{ip['solves']}")
            if ip["benefit"]:
                print(f"      效果：{ip['benefit']}")
        print("\n=== 提取关键词 ===")
        print("、".join(result.keywords))
    if args.output:
        if args.skeleton:
            save_json(result.skeleton, args.output)
            print(f"\n交底书骨架已写入：{args.output}", file=sys.stderr)
        else:
            save_json(result.to_dict(), args.output)
            print(f"\n挖掘结果已写入：{args.output}", file=sys.stderr)
    return 0


def cmd_lint(args: argparse.Namespace) -> int:
    disclosure = load_disclosure(args.input)
    report = lint_disclosure(disclosure)
    if args.json:
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(
            f"共 {len(report.claims)} 项权利要求；"
            f"错误 {len(report.errors)}，警告 {len(report.warnings)}，提示 {len(report.infos)}"
        )
        _print_issues(report.issues, not args.no_color)
        print("结论：", "通过 ✅" if report.passed else "未通过 ❌（存在错误级问题）")
    return 0 if report.passed else 1


def cmd_claims(args: argparse.Namespace) -> int:
    disclosure = load_disclosure(args.input)
    claims = parse_claims(disclosure.claims_text)
    if not claims:
        print("未解析到权利要求，请检查 claims_text。", file=sys.stderr)
        return 2
    graph, issues = analyze_claims(claims)
    print(f"共解析 {len(claims)} 项（独权 {sum(c.is_independent for c in claims)} 项，"
          f"从权 {sum(not c.is_independent for c in claims)} 项）")
    print("\n=== 依赖树 ===")
    print(graph.render_tree())
    print("\n=== 深度统计 ===")
    for c in claims:
        print(f"  权项 {c.number}: 深度 {graph.depth_of(c.number)}，引用 {c.refs or '—'}")
    if issues:
        print("\n=== 问题 ===")
        _print_issues(issues, not args.no_color)
    return 0 if not [i for i in issues if i.severity == Severity.ERROR] else 1


def cmd_novelty(args: argparse.Namespace) -> int:
    disclosure = load_disclosure(args.input)
    prior = [(Path(p).name, _read_text(p)) for p in args.prior]
    result = compare_prior_art(disclosure, prior)
    payload = result.to_dict()
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    print("=== 对比文件重合度（词面统计，仅供检索方向参考） ===")
    for m in result.matches:
        print(
            f"- {m.name}：包含度 {m.containment:.1%}，Jaccard {m.jaccard:.1%}，"
            f"重合术语 {m.overlap_size} 个，风险档：{m.level}"
        )
        top = "、".join(t for t, _ in m.shared_terms[:10])
        if top:
            print(f"  高频重合：{top}")
    if result.riskiest:
        print(f"\n最接近的对比文件：{result.riskiest.name}")
    print("\n提示：词面重合不等于缺乏新颖性/创造性，正式结论需结合专利检索与法律判断。")
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    disclosure = load_disclosure(args.input)
    report = lint_disclosure(disclosure) if args.with_check else None
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    stem = args.name or Path(args.input).stem
    formats = ["md", "html", "docx"] if args.format == "all" else [args.format]
    written: List[Path] = []
    for fmt in formats:
        if fmt == "md":
            p = outdir / f"{stem}.md"
            p.write_text(to_markdown(disclosure, report), encoding="utf-8")
        elif fmt == "html":
            p = outdir / f"{stem}.html"
            p.write_text(to_html(disclosure, report), encoding="utf-8")
        elif fmt == "docx":
            p = to_docx(disclosure, outdir / f"{stem}.docx")
        else:  # pragma: no cover - argparse choices 已拦截
            raise SystemExit(f"不支持的格式：{fmt}")
        written.append(p)
        print(f"已导出：{p}")
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    disclosure = load_disclosure(args.input)
    report = lint_disclosure(disclosure)
    md = to_markdown(disclosure, report)
    if args.output:
        Path(args.output).write_text(md, encoding="utf-8")
        print(f"完整自检报告已写入：{args.output}")
    else:
        print(md)
    return 0 if report.passed else 1


# ----------------------------------------------------------------------
# 参数解析
# ----------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="patentscribe",
        description="PatentScribe — 中国专利交底书撰写、权要自检与多格式导出工具（零依赖、离线）",
    )
    parser.add_argument("--version", action="version", version=f"PatentScribe {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="生成交底书 JSON 模板")
    p_init.add_argument("-o", "--output", default="disclosure.json")
    p_init.add_argument("--type", default="发明", choices=["发明", "实用新型", "外观设计"])
    p_init.set_defaults(func=cmd_init)

    p_mine = sub.add_parser("mine", help="从技术笔记挖掘发明点")
    p_mine.add_argument("-i", "--input", required=True, help="技术笔记 txt 文件")
    p_mine.add_argument("-o", "--output", help="结果输出 JSON 路径")
    p_mine.add_argument("--skeleton", action="store_true", help="输出可直接填写的交底书骨架")
    p_mine.add_argument("--type", default="发明", choices=["发明", "实用新型", "外观设计"])
    p_mine.add_argument("--format", choices=["text", "json"], default="text")
    p_mine.set_defaults(func=cmd_mine)

    p_lint = sub.add_parser("lint", help="形式审查与权要自检")
    p_lint.add_argument("-i", "--input", required=True)
    p_lint.add_argument("--json", action="store_true", help="输出 JSON 结果")
    p_lint.add_argument("--no-color", action="store_true")
    p_lint.set_defaults(func=cmd_lint)

    p_claims = sub.add_parser("claims", help="权利要求依赖树分析")
    p_claims.add_argument("-i", "--input", required=True)
    p_claims.add_argument("--no-color", action="store_true")
    p_claims.set_defaults(func=cmd_claims)

    p_nov = sub.add_parser("novelty", help="与对比文件做重合度比对")
    p_nov.add_argument("-i", "--input", required=True, help="交底书 JSON")
    p_nov.add_argument("-p", "--prior", nargs="+", required=True, help="对比文件 txt（可多个）")
    p_nov.add_argument("--json", action="store_true")
    p_nov.set_defaults(func=cmd_novelty)

    p_exp = sub.add_parser("export", help="导出 md/html/docx")
    p_exp.add_argument("-i", "--input", required=True)
    p_exp.add_argument("-f", "--format", choices=["md", "html", "docx", "all"], default="all")
    p_exp.add_argument("-o", "--outdir", default="dist")
    p_exp.add_argument("--name", help="输出文件名（不含扩展名）")
    p_exp.add_argument("--with-check", action="store_true", help="把自检结果一并写入产物")
    p_exp.set_defaults(func=cmd_export)

    p_rep = sub.add_parser("report", help="生成完整 Markdown 自检报告")
    p_rep.add_argument("-i", "--input", required=True)
    p_rep.add_argument("-o", "--output")
    p_rep.set_defaults(func=cmd_report)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except BrokenPipeError:
        # 输出被 head/less 等下游关闭时安静退出（类 Unix 工具惯例）
        try:
            sys.stdout.close()
        except Exception:
            pass
        return 0
    except FileNotFoundError as exc:
        print(f"错误：文件不存在 — {exc.filename}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
