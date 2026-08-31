"""发明点挖掘：从原始技术笔记中抽取“问题—方案—效果”线索。

纯规则实现（提示词 + 句式模式 + 中文二元特征），不依赖任何模型或网络，
输出可直接喂给 ``builder`` 的交底书骨架。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

# 各类线索的引导词
PROBLEM_CUES = (
    "现有技术", "目前", "当前", "传统", "已有", "原有的", "普通的",
    "缺陷", "不足", "问题", "瓶颈", "难以", "无法", "不能", "缺点",
    "为了解决", "针对", "受制于", "效率低", "成本高",
)
# 句级分类只使用强方案引导词；“采用/通过/利用”等弱引导词仅用于
# 方案句内部的技术手段抽取，避免把问题描述误判为方案
SOLUTION_CUES = (
    "本发明", "本方案", "本实用新型", "本设计", "提出", "设计了",
    "步骤如下", "本实施例提供",
)
EFFECT_CUES = (
    "从而", "使得", "因此", "进而", "提高了", "提升了", "降低了",
    "减少了", "缩短了", "节省了", "实现了", "达到", "优点", "有益效果",
    "相比", "相较于", "优势在于", "保证了", "增强了",
)
# 方案句中用于切出“技术手段片段”的动词；
# “利用率”中的“利用”需要负向前瞻排除，避免把效果描述误判为手段
_MEANS_PAT = re.compile(
    r"(?:通过|采用|利用(?!率)|引入|构建|设计了?|提出了?)([^，。；！？,;!?]{2,40})"
)
_SENT_SPLIT = re.compile(r"[。！？!?\n；;]+")
# 中文停用词（二元特征过滤用，精简表，确定性维护）
STOP_BIGRAMS = {
    "一种", "上述", "所述", "本发", "发明", "本实", "用新", "新型",
    "可以", "能够", "进行", "通过", "采用", "利用", "使得", "从而",
    "以及", "或者", "并且", "包括", "包含", "具有", "其中", "其他",
    "步骤", "装置", "模块", "单元", "系统", "设备", "方法", "数据",
    "技术", "方案", "实现", "得到", "进行", "对应", "相关", "具体",
    # 常见跨词边界噪声二元片段
    "本方", "发流", "源利", "用率", "态权", "率不", "率极", "差控",
    "的问", "问题", "在高", "场景", "下的", "下存", "且难", "即可",
    "下一", "一窗", "量下", "口的", "点的",
    "下尾", "不均", "不需", "要人", "工介", "介入",
}


@dataclass
class MiningResult:
    """挖掘结果。"""

    problems: List[str] = field(default_factory=list)
    solutions: List[str] = field(default_factory=list)
    effects: List[str] = field(default_factory=list)
    means: List[str] = field(default_factory=list)
    inventive_points: List[Dict[str, str]] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    skeleton: Dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        return {
            "problems": self.problems,
            "solutions": self.solutions,
            "effects": self.effects,
            "technical_means": self.means,
            "inventive_points": self.inventive_points,
            "keywords": self.keywords,
            "skeleton": self.skeleton,
        }


def split_sentences(text: str) -> List[str]:
    """按中英文句读切句，去空白与过短片段。"""
    parts = _SENT_SPLIT.split(text.replace("\r", ""))
    return [p.strip(" 　\t，,") for p in parts if len(p.strip(" 　\t，,")) >= 4]


def _hit(sentence: str, cues: Tuple[str, ...]) -> bool:
    return any(cue in sentence for cue in cues)


def _bigrams(text: str) -> List[str]:
    """抽取中文二元词项；英文/数字按单词保留。"""
    tokens: List[str] = []
    tokens.extend(re.findall(r"[A-Za-z][A-Za-z0-9_+\-]{1,}", text))
    han = re.findall(r"[\u4e00-\u9fff]+", text)
    for run in han:
        for i in range(len(run) - 1):
            bg = run[i:i + 2]
            if bg not in STOP_BIGRAMS:
                tokens.append(bg)
    return tokens


def extract_keywords(text: str, top_k: int = 15) -> List[str]:
    """基于二元词项词频提取关键词（确定性、可复现）。

    排序口径：先按词频降序，同频按词项字典序，保证跨运行、跨平台结果一致。
    """
    freq: Dict[str, int] = {}
    for tok in _bigrams(text):
        freq[tok] = freq.get(tok, 0) + 1
    ordered = sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))
    words = [w for w, _ in ordered]
    # 高频词（出现 2 次及以上）优先；不足 top_k 时再用单次词补齐
    repeated = [w for w in words if freq[w] >= 2]
    if len(repeated) >= top_k:
        return repeated[:top_k]
    rest = [w for w in words if freq[w] == 1]
    return (repeated + rest)[:top_k]


def mine_text(text: str, patent_type: str = "发明") -> MiningResult:
    """从自由文本技术描述中挖掘问题/方案/效果与候选发明点。

    Parameters
    ----------
    text:
        原始技术笔记（可以是会议纪要、设计文档片段、聊天记录整理稿）。
    patent_type:
        目标专利类型，写入生成的骨架。
    """
    result = MiningResult()
    sentences = split_sentences(text)

    for sent in sentences:
        is_problem = _hit(sent, PROBLEM_CUES)
        is_solution = _hit(sent, SOLUTION_CUES)
        is_effect = _hit(sent, EFFECT_CUES)
        if is_problem and not is_solution:
            result.problems.append(sent)
        # 技术手段只从“方案句”中抽取，避免把问题描述误判为发明点
        if is_solution:
            result.solutions.append(sent)
            for m in _MEANS_PAT.finditer(sent):
                means = m.group(1).strip("的了一种")
                if 2 <= len(means) <= 40 and means not in result.means:
                    result.means.append(means)
        if is_effect and not is_solution:
            result.effects.append(sent)

    # 组装候选发明点：技术手段 × 最近的问题/效果
    for idx, means in enumerate(result.means, start=1):
        problem = result.problems[min(idx - 1, len(result.problems) - 1)] \
            if result.problems else ""
        effect = result.effects[min(idx - 1, len(result.effects) - 1)] \
            if result.effects else ""
        result.inventive_points.append({
            "id": f"IP{idx:02d}",
            "technical_means": means,
            "solves": problem,
            "benefit": effect,
        })

    result.keywords = extract_keywords(text)

    result.skeleton = {
        "title": "",
        "patent_type": patent_type,
        "inventors": [],
        "field": result.solutions[0] if result.solutions else "",
        "background": "\n".join(result.problems),
        "problems": result.problems,
        "solution": "\n".join(result.solutions),
        "effects": result.effects,
        "embodiments": "",
        "drawings": [],
        "abstract": "",
        "claims_text": "",
        "keywords": result.keywords,
    }
    return result
