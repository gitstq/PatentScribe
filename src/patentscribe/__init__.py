"""PatentScribe — 中国专利交底书与权利要求结构化撰写、自检与导出工具包。

PatentScribe is a zero-dependency, offline, deterministic rule engine that helps
inventors and patent engineers:

* structure an invention disclosure (技术交底书);
* mine candidate inventive points from raw technical notes;
* parse claims and verify their dependency graph (权利要求自检);
* run formal-compliance checks (形式审查辅助);
* estimate novelty overlap against prior-art documents (三性辅助比对);
* export Markdown / self-contained HTML / DOCX deliverables.

No LLM, no network, no third-party dependency — only the Python standard library.
"""

from .models import (
    Claim,
    Disclosure,
    Issue,
    Severity,
    CheckReport,
)
from .claim_parser import parse_claims, analyze_claims, ClaimGraph
from .linter import lint_disclosure
from .miner import mine_text, MiningResult
from .novelty import compare_prior_art, NoveltyResult
from .builder import load_disclosure, dump_template, DisclosureError
from .exporter import to_markdown, to_html, to_docx

__version__ = "1.0.0"
__all__ = [
    "Claim",
    "Disclosure",
    "Issue",
    "Severity",
    "CheckReport",
    "parse_claims",
    "analyze_claims",
    "ClaimGraph",
    "lint_disclosure",
    "mine_text",
    "MiningResult",
    "compare_prior_art",
    "NoveltyResult",
    "load_disclosure",
    "dump_template",
    "DisclosureError",
    "to_markdown",
    "to_html",
    "to_docx",
    "__version__",
]
