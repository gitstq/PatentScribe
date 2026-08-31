"""交底书形式审查规则引擎（L 系列规则）。

规则参考《专利法》《专利法实施细则》《专利审查指南》中对发明名称、
摘要、权利要求书、说明书与附图标记的形式要求，做**确定性**的自动检查；
无法形式化判断的内容（如创造性高度）不在此列。
"""

from __future__ import annotations

import re
from typing import Dict, List, Set, Tuple

from .claim_parser import analyze_claims, parse_claims
from .miner import _bigrams
from .models import CheckReport, Claim, Disclosure, Issue, Severity

# 发明名称长度上限（审查指南：一般不超过 25 个字）
TITLE_MAX_LEN = 25
# 摘要字数上限（审查指南：一般不超过 300 字）
ABSTRACT_MAX_LEN = 300

# 权利要求中不宜出现的模糊/宣传性用语
VAGUE_WORDS = {
    "最好": "最高级限定，保护范围不确定",
    "最佳": "最高级限定，保护范围不确定",
    "最优": "最高级限定，保护范围不确定",
    "大约": "约数用语导致范围不清",
    "大概": "约数用语导致范围不清",
    "左右": "约数用语导致范围不清",
    "例如": "权项中举例会被解读为限定，建议删除或放入说明书",
    "等": "开放式列举可能导致范围不清，确认是否必要",
    "高效": "效果性形容词不构成技术特征",
    "低成本": "效果性形容词不构成技术特征",
    "先进": "宣传性用语，不构成技术特征",
    "新型": "宣传性用语，不构成技术特征",
    "现代化": "宣传性用语，不构成技术特征",
}
# 摘要中不宜出现的商业宣传语
ABSTRACT_BAD = (
    "性能优异", "业界领先", "世界领先", "填补空白", "巨大效益",
    "商业价值", "深受好评", "颠覆性", "革命性",
)
# 附图标记：2~4 位数字（避免把“步骤101”之类误判？步骤编号也允许出现，
# 这里只统计 2 位以上数字，用于交叉一致性提示）
_NUM_TOKEN = re.compile(r"(?<!\d)(\d{2,4})(?!\d)")
_CN_CHAR = re.compile(r"[\u4e00-\u9fff]")


def _cn_len(text: str) -> int:
    """按“汉字数 + 英文单词数”计字数，贴近中文写作习惯。"""
    han = len(_CN_CHAR.findall(text))
    words = len(re.findall(r"[A-Za-z][A-Za-z0-9_+\-]*", text))
    digits = len(re.findall(r"\d+(?:\.\d+)?", text))
    return han + words + digits


def lint_disclosure(disclosure: Disclosure) -> CheckReport:
    """执行全部规则，返回 :class:`CheckReport`。"""
    report = CheckReport()
    issues = report.issues

    # ------------------------------------------------------------ L1 完整性
    for sec_name, content in disclosure.required_sections().items():
        if not content or not str(content).strip():
            issues.append(Issue(
                code="L101", severity=Severity.ERROR, location=sec_name,
                message=f"必填章节“{sec_name}”为空。",
                suggestion="补全该章节后再导出/提交。",
            ))

    if not disclosure.problems:
        issues.append(Issue(
            code="L102", severity=Severity.WARN, location="现有技术问题",
            message="未列出现有技术存在的问题（problems 为空）。",
            suggestion="用 2~4 条说明现有技术的具体缺陷，为差异化提供锚点。",
        ))
    if not disclosure.effects:
        issues.append(Issue(
            code="L103", severity=Severity.WARN, location="有益效果",
            message="未列出有益效果（effects 为空）。",
            suggestion="效果应与技术手段一一对应，尽量可量化。",
        ))

    if disclosure.patent_type not in ("发明", "实用新型", "外观设计"):
        issues.append(Issue(
            code="L104", severity=Severity.ERROR, location="专利类型",
            message=f"不支持的专利类型：{disclosure.patent_type!r}。",
            suggestion="取值必须为 发明 / 实用新型 / 外观设计。",
        ))

    # ------------------------------------------------------------ L2 名称
    title = disclosure.title.strip()
    if title:
        tlen = _cn_len(title)
        if tlen > TITLE_MAX_LEN:
            issues.append(Issue(
                code="L201", severity=Severity.WARN, location="发明名称",
                message=f"名称约 {tlen} 字，超过审查指南建议的 {TITLE_MAX_LEN} 字上限。",
                suggestion="压缩为“一种+核心技术主题+方法/装置/系统”的短名称。",
            ))
        for bad in ("最好", "最佳", "最优", "高效", "先进"):
            if bad in title:
                issues.append(Issue(
                    code="L202", severity=Severity.ERROR, location="发明名称",
                    message=f"名称含宣传性/效果性用语“{bad}”。",
                    suggestion="名称只写技术主题，不写效果与商业评价。",
                ))

    # ------------------------------------------------------------ L3 摘要
    abstract = disclosure.abstract.strip()
    if abstract:
        alen = _cn_len(abstract)
        if alen > ABSTRACT_MAX_LEN:
            issues.append(Issue(
                code="L301", severity=Severity.WARN, location="摘要",
                message=f"摘要约 {alen} 字，超过 {ABSTRACT_MAX_LEN} 字上限。",
                suggestion="摘要控制在 300 字以内，写明技术领域、方案要点与主要用途。",
            ))
        for bad in ABSTRACT_BAD:
            if bad in abstract:
                issues.append(Issue(
                    code="L302", severity=Severity.WARN, location="摘要",
                    message=f"摘要含商业宣传语“{bad}”。",
                    suggestion="摘要只陈述技术内容，删除商业评价。",
                ))

    # ------------------------------------------------------------ L4 权要
    claims: List[Claim] = parse_claims(disclosure.claims_text)
    report.claims = claims
    if disclosure.claims_text.strip():
        _, claim_issues = analyze_claims(claims)
        issues.extend(claim_issues)

        for claim in claims:
            for word, reason in VAGUE_WORDS.items():
                if word in claim.text:
                    sev = Severity.ERROR if word in ("最好", "最佳", "最优") else Severity.WARN
                    issues.append(Issue(
                        code="L401", severity=sev,
                        location=f"权利要求{claim.number}",
                        message=f"含用语“{word}”：{reason}。",
                        suggestion="替换为可界定的结构/步骤/数值范围。",
                    ))

        # L402 独权主题与发明名称的核心主题应对齐；
        # 电子设备/存储介质/程序产品等法定类别独权允许与名称不共享术语
        STATUTORY = ("电子设备", "存储介质", "计算机程序产品", "程序产品", "可读介质")
        if title and claims:
            indep = [c for c in claims if c.is_independent]
            title_core = re.sub(r"^一种|^一种用于", "", title)
            for c in indep:
                if any(k in c.subject for k in STATUTORY):
                    continue
                if c.subject and title_core:
                    # 主题关键词（去“一种”）至少有一个二元片段重合
                    t_bigrams = set(_bigrams(title_core))
                    s_bigrams = set(_bigrams(c.subject))
                    if t_bigrams and s_bigrams and not (t_bigrams & s_bigrams):
                        issues.append(Issue(
                            code="L402", severity=Severity.INFO,
                            location=f"权利要求{c.number}",
                            message="独权主题名称与发明名称缺少共同术语。",
                            suggestion="独权主题应与发明名称保持同一技术主题，避免名称与权要脱节。",
                        ))

        # L403 仅一条权项时提示布局纵深
        if len(claims) == 1:
            issues.append(Issue(
                code="L403", severity=Severity.INFO, location="权利要求书",
                message="目前只有 1 项权利要求，缺少从属权利要求形成的保护纵深。",
                suggestion="围绕优选实施方式补充从权，构建梯度保护。",
            ))

    # ------------------------------------------------------------ L5 特征覆盖
    if claims and disclosure.embodiments.strip():
        emb = disclosure.embodiments
        for claim in claims:
            if not claim.is_independent:
                continue
            missing = _uncovered_features(claim, emb)
            if missing:
                issues.append(Issue(
                    code="L501", severity=Severity.WARN,
                    location=f"权利要求{claim.number}",
                    message="独权中有技术特征未在“具体实施方式”中得到支撑："
                            + "；".join(missing[:3])
                            + ("……" if len(missing) > 3 else ""),
                    suggestion="说明书具体实施方式必须支撑独权的每一个特征，否则可能被认定公开不充分。",
                ))

    # ------------------------------------------------------------ L6 附图标记
    _check_drawing_marks(disclosure, claims, issues)

    # ------------------------------------------------------------ L7 关键词
    if not disclosure.keywords:
        issues.append(Issue(
            code="L701", severity=Severity.INFO, location="关键词",
            message="未填写核心技术关键词。",
            suggestion="填写 3~8 个关键词，便于检索与分类（可用 mine 子命令自动提取）。",
        ))

    # 按 错误→警告→提示、再按位置 排序，输出稳定
    order = {Severity.ERROR: 0, Severity.WARN: 1, Severity.INFO: 2}
    issues.sort(key=lambda i: (order[i.severity], i.code, i.location))
    return report


def _uncovered_features(claim: Claim, embodiments: str) -> List[str]:
    """检查独权特征片段是否在具体实施方式中有词面支撑。"""
    missing: List[str] = []
    for feat in claim.features:
        terms = [t for t in _bigrams(feat)]
        # 特征片段至少应有 2 个二元术语落在实施方式中
        hit = sum(1 for t in terms if t in embodiments)
        if terms and hit == 0:
            missing.append(feat[:24])
    return missing


def _check_drawing_marks(
    disclosure: Disclosure, claims: List[Claim], issues: List[Issue]
) -> None:
    """附图标记一致性：权要中出现的标记应在实施方式/附图说明中出现。"""
    claim_marks: Set[str] = set()
    for claim in claims:
        claim_marks.update(_NUM_TOKEN.findall(claim.text))
    emb_marks = set(_NUM_TOKEN.findall(disclosure.embodiments))
    drawing_marks: Set[str] = set()
    for fig in disclosure.drawings:
        drawing_marks.update(_NUM_TOKEN.findall(str(fig)))

    if not claim_marks:
        return

    # 步骤编号常见为 1xx，结构标记常见 2~4 位；统一按“是否在实施方式出现”判断
    absent_in_emb = sorted(m for m in claim_marks if m not in emb_marks)
    if absent_in_emb:
        issues.append(Issue(
            code="L601", severity=Severity.WARN, location="附图标记",
            message=f"权要中的标记 {absent_in_emb[:10]} 未在具体实施方式中出现。",
            suggestion="权利要求中的附图标记必须在说明书中解释，且括号标注规范一致。",
        ))
    if disclosure.drawings:
        absent_in_fig = sorted(m for m in claim_marks if m not in drawing_marks and m not in emb_marks)
        if absent_in_fig:
            issues.append(Issue(
                code="L602", severity=Severity.INFO, location="附图标记",
                message=f"标记 {absent_in_fig[:10]} 未在附图说明中登记。",
                suggestion="确认每个标记是否需要在附图说明中体现，避免漏标。",
            ))
