"""权利要求书解析与依赖图分析（确定性规则，零依赖）。

支持的权项编号写法：``1.`` / ``1、`` / ``1．`` / ``【1】`` / ``权利要求1.``，
支持引用写法：``根据权利要求1所述`` / ``如权利要求1-3任一项所述`` /
``根据权利要求1、2或3所述``。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from .models import Claim, Issue, Severity

# 权项起始标记：行首（或文本开头）的序号
_NUM_MARK = re.compile(
    r"(?:^|\n)\s*(?:【?权利要求\s*)?(\d{1,3})\s*[】]?\s*[\.、．]\s*"
)
# 引用其他权项的语言模式
_REF_PAT = re.compile(
    r"(?:根据|按照|依据|如)权利要求\s*([0-9]+(?:\s*[\-—~至到、,，和或及]\s*[0-9]+)*)"
)
_RANGE_SEP = re.compile(r"\s*[\-—~至到、,，和或及]\s*")
# 独立权利要求的特征分界
_FEATURE_SPLIT = re.compile(r"[；;]")
# 主题名称提取：到“其特征在于/特征在于/，包括/，包含/，具有/，其特征为”等为止
_SUBJECT_END = re.compile(
    r"[，,]\s*(?:其特征在于|特征在于|其特征为|特征为|包括以下步骤|包括|包含|具有|由以下步骤组成|由.*?组成)"
)
_TRAILING_PERIOD = re.compile(r"[。.]\s*$")
_FEATURE_MARK = re.compile(r"其特征在于|特征在于|其特征为|特征为")


def _split_number_list(raw: str) -> List[int]:
    """把 ``1、2或3`` / ``1-3`` / ``1,2`` 这样的引用串展开成编号列表。"""
    nums: List[int] = []
    # 先处理区间 a-b / a至b
    for m in re.finditer(r"(\d{1,3})\s*[\-—~至到]\s*(\d{1,3})", raw):
        a, b = int(m.group(1)), int(m.group(2))
        lo, hi = min(a, b), max(a, b)
        nums.extend(range(lo, hi + 1))
        raw = raw.replace(m.group(0), " ")
    for token in _RANGE_SEP.split(raw):
        token = token.strip()
        if token.isdigit():
            nums.append(int(token))
    # 去重并保持顺序
    seen: Set[int] = set()
    ordered: List[int] = []
    for n in nums:
        if n not in seen:
            seen.add(n)
            ordered.append(n)
    return ordered


def parse_claims(text: str) -> List[Claim]:
    """把权利要求书原文切分并解析为 :class:`Claim` 列表。

    解析过程只做确定性的结构识别，不做合法性判断；合法性判断在
    :func:`analyze_claims` 中完成，便于分层测试。
    """
    if not text or not text.strip():
        return []

    # 统一全角/半角空白与换行
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").strip()

    marks = list(_NUM_MARK.finditer(normalized))
    if not marks:
        # 没有编号时，按句号兜底切成单条（至少不丢内容）
        chunks = [s.strip() for s in re.split(r"(?<=。)\s*", normalized) if s.strip()]
        marks_data = [(i + 1, c) for i, c in enumerate(chunks)]
    else:
        marks_data = []
        for i, m in enumerate(marks):
            start = m.end()
            end = marks[i + 1].start() if i + 1 < len(marks) else len(normalized)
            body = normalized[start:end].strip()
            marks_data.append((int(m.group(1)), body))

    claims: List[Claim] = []
    for number, body in marks_data:
        body = re.sub(r"\s*\n\s*", " ", body).strip()
        body = _TRAILING_PERIOD.sub("", body).strip()

        refs: List[int] = []
        for rm in _REF_PAT.finditer(body):
            refs.extend(_split_number_list(rm.group(1)))
        seen: Set[int] = set()
        refs = [r for r in refs if not (r in seen or seen.add(r))]  # type: ignore[func-returns-value]

        kind = "dependent" if refs else "independent"

        subject = ""
        sm = _SUBJECT_END.search(body)
        if sm:
            subject = body[: sm.start()].strip()
        else:
            # 取第一个逗号前的片段作为主题
            subject = re.split(r"[，,]", body, maxsplit=1)[0].strip()

        # 技术特征：优先取“特征在于”之后的部分，再按分号切分
        feature_region = body
        fm = _FEATURE_MARK.search(body)
        if fm:
            feature_region = body[fm.end():].lstrip("，,：: ").strip()
        features = [
            seg.strip(" ，,：:。.") for seg in _FEATURE_SPLIT.split(feature_region)
            if seg.strip(" ，,：:。.")
        ]

        claims.append(
            Claim(
                number=number,
                text=body + "。",
                kind=kind,
                subject=subject,
                refs=refs,
                features=features,
            )
        )

    claims.sort(key=lambda c: c.number)
    return claims


@dataclass
class ClaimGraph:
    """权利要求依赖图。"""

    claims: List[Claim]
    children: Dict[int, List[int]] = field(default_factory=dict)
    roots: List[int] = field(default_factory=list)

    def ancestors_of(self, number: int) -> List[int]:
        """返回某权项的全部祖先（沿引用链向上）。"""
        result: List[int] = []
        stack = [number]
        visited: Set[int] = set()
        by_num = {c.number: c for c in self.claims}
        while stack:
            cur = stack.pop()
            claim = by_num.get(cur)
            if not claim:
                continue
            for ref in claim.refs:
                if ref in visited:
                    continue
                visited.add(ref)
                result.append(ref)
                stack.append(ref)
        return sorted(result)

    def depth_of(self, number: int) -> int:
        """权项在引用树中的深度（独权为 1）。"""
        by_num = {c.number: c for c in self.claims}

        def _depth(n: int, trail: Set[int]) -> int:
            claim = by_num.get(n)
            if not claim or not claim.refs:
                return 1
            return 1 + max(_depth(r, trail | {n}) for r in claim.refs if r not in trail)

        return _depth(number, set())

    def render_tree(self) -> str:
        """渲染 ASCII 依赖树，便于人工复核（多项引用只展开一次，其余位置标注同见）。"""
        lines: List[str] = []
        by_num = {c.number: c for c in self.claims}
        rendered: Set[int] = set()

        def _walk(n: int, prefix: str, is_last: bool) -> None:
            claim = by_num.get(n)
            if not claim:
                return
            connector = "└─ " if is_last else "├─ "
            tag = "独权" if claim.is_independent else "从权"
            alias = "" if n not in rendered else f"（同见上方展开）"
            lines.append(f"{prefix}{connector}{n} [{tag}] {claim.subject}{alias}")
            if n in rendered:
                return
            rendered.add(n)
            kids = self.children.get(n, [])
            child_prefix = prefix + ("   " if is_last else "│  ")
            for i, kid in enumerate(kids):
                _walk(kid, child_prefix, i == len(kids) - 1)

        for i, root in enumerate(self.roots):
            _walk(root, "", i == len(self.roots) - 1)
        return "\n".join(lines)


def build_graph(claims: List[Claim]) -> ClaimGraph:
    graph = ClaimGraph(claims=claims)
    for claim in claims:
        if claim.is_independent:
            graph.roots.append(claim.number)
        for ref in claim.refs:
            graph.children.setdefault(ref, []).append(claim.number)
    for kids in graph.children.values():
        kids.sort()
    return graph


def analyze_claims(claims: List[Claim]) -> Tuple[ClaimGraph, List[Issue]]:
    """对解析后的权项做形式与逻辑校验，返回依赖图与问题清单。

    规则覆盖：编号连续性、悬空引用、前引限制、引用环、独权存在性、
    多项引多项禁止（《专利法实施细则》及《专利审查指南》）、
    权项句号规范、独权缺少“特征在于”提示等。
    """
    issues: List[Issue] = []
    numbers = {c.number for c in claims}
    by_num = {c.number: c for c in claims}

    # C001 编号连续性
    expected = list(range(1, len(claims) + 1))
    actual = [c.number for c in claims]
    if actual != expected:
        missing = sorted(set(expected) - numbers)
        dup = sorted({n for n in actual if actual.count(n) > 1})
        detail = []
        if missing:
            detail.append(f"缺失编号 {missing}")
        if dup:
            detail.append(f"重复编号 {dup}")
        issues.append(Issue(
            code="C001", severity=Severity.ERROR, location="权利要求书",
            message="权项编号未从 1 开始连续编号：" + "；".join(detail),
            suggestion="按 1..N 连续编号，不要跳号或重号。",
        ))

    # C002 至少一条独权
    independents = [c for c in claims if c.is_independent]
    if not independents:
        issues.append(Issue(
            code="C002", severity=Severity.ERROR, location="权利要求书",
            message="缺少独立权利要求（全部权项都在引用其他权项）。",
            suggestion="至少撰写一条不引用其他权项的独立权利要求。",
        ))

    for claim in claims:
        loc = f"权利要求{claim.number}"

        # C003 悬空引用
        for ref in claim.refs:
            if ref not in numbers:
                issues.append(Issue(
                    code="C003", severity=Severity.ERROR, location=loc,
                    message=f"引用了不存在的权利要求 {ref}。",
                    suggestion=f"确认被引用权项编号，当前共 {len(claims)} 项。",
                ))
            # C004 只能引用在先权项
            elif ref >= claim.number:
                issues.append(Issue(
                    code="C004", severity=Severity.ERROR, location=loc,
                    message=f"引用了在后或同号权利要求 {ref}（只能引用在先权项）。",
                    suggestion="从属权利要求只能引用编号更小的在先权利要求。",
                ))

        # C005 独权缺少特征分界语
        if claim.is_independent and not _FEATURE_MARK.search(claim.text):
            issues.append(Issue(
                code="C005", severity=Severity.WARN, location=loc,
                message="独立权利要求未出现“其特征在于/特征在于”分界语。",
                suggestion="使用“前序部分 + 其特征在于 + 特征部分”的标准两段式写法。",
            ))

        # C006 句内句号（一条权项只能在末尾有一个句号）
        inner_periods = claim.text[:-1].count("。")
        if inner_periods > 0:
            issues.append(Issue(
                code="C006", severity=Severity.WARN, location=loc,
                message=f"权项内部出现 {inner_periods} 个句号，一条权项应仅在末尾使用一个句号。",
                suggestion="把内部句号改为分号或逗号，保持一权项一句。",
            ))

        # C007 从权却没有解析到引用 / 独权却出现引用语（结构异常提示）
        if claim.is_independent and _REF_PAT.search(claim.text):
            issues.append(Issue(
                code="C007", severity=Severity.INFO, location=loc,
                message="该权项包含引用表述但未解析出有效引用编号，请人工确认。",
                suggestion="检查引用编号写法是否规范。",
            ))

    # C008 多项引多项禁止：引用多项的从权，其引用对象中不能也有多引从权
    multi = {c.number for c in claims if len(c.refs) > 1}
    for claim in claims:
        if len(claim.refs) > 1:
            bad = [r for r in claim.refs if r in multi and r < claim.number]
            if bad:
                issues.append(Issue(
                    code="C008", severity=Severity.ERROR, location=f"权利要求{claim.number}",
                    message=f"构成多项引多项：该权项引用多项，而 {bad} 本身也引用多项。",
                    suggestion=(
                        "多项从属权利要求不得引用另一项多项从属权利要求；"
                        "请改为引用单项权项，或拆分为多条从权。"
                    ),
                ))

    # C009 引用环检测（正常前引不会成环，兜底防御）
    graph = build_graph(claims)
    for claim in claims:
        seen: Set[int] = set()
        stack = [claim.number]
        while stack:
            cur = stack.pop()
            node = by_num.get(cur)
            if not node:
                continue
            for ref in node.refs:
                if ref == claim.number:
                    issues.append(Issue(
                        code="C009", severity=Severity.ERROR, location=f"权利要求{claim.number}",
                        message="权利要求引用链存在环。",
                        suggestion="梳理引用关系，删除回指。",
                    ))
                    stack = []
                    break
                if ref not in seen:
                    seen.add(ref)
                    stack.append(ref)

    # C010 独权主题名称一致性（同一组独权主题类型应一致：方法/装置/介质）
    if len(independents) > 1:
        kinds_seen = set()
        for c in independents:
            for kw in ("方法", "装置", "设备", "系统", "介质", "产品", "用途"):
                if kw in c.subject:
                    kinds_seen.add(kw)
                    break
        if len(kinds_seen) > 1:
            issues.append(Issue(
                code="C010", severity=Severity.INFO, location="权利要求书",
                message=f"存在不同主题类型的独立权利要求：{sorted(kinds_seen)}。",
                suggestion="方法/装置/介质等不同类别独权应成组布局，确认是否为有意的类别布局。",
            ))

    return graph, issues
