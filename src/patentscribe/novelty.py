"""三性辅助比对：本申请与对比文件之间的术语重合度分析。

注意：本模块只做**词面重合度**的确定性统计，用于辅助判断新颖性/创造性
的检索方向，不能替代专利检索与审查意见。输出指标：

* Jaccard 相似度 = 交集 / 并集
* 包含度 containment = 交集 / 本申请术语数（本申请有多少术语已被对比文件覆盖）
* 重合高频词表
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Tuple

from .miner import _bigrams
from .models import Disclosure

# 重合度分档阈值（containment 口径）
HIGH_THRESHOLD = 0.60
MID_THRESHOLD = 0.30


@dataclass
class PriorArtMatch:
    """单篇对比文件的比对结果。"""

    name: str
    jaccard: float
    containment: float
    overlap_size: int
    shared_terms: List[Tuple[str, int]] = field(default_factory=list)
    level: str = "低"  # 高 / 中 / 低

    def to_dict(self) -> Dict[str, object]:
        return {
            "name": self.name,
            "jaccard": round(self.jaccard, 4),
            "containment": round(self.containment, 4),
            "overlap_term_count": self.overlap_size,
            "level": self.level,
            "shared_terms": [
                {"term": t, "count": c} for t, c in self.shared_terms
            ],
        }


@dataclass
class NoveltyResult:
    matches: List[PriorArtMatch] = field(default_factory=list)

    @property
    def riskiest(self) -> PriorArtMatch | None:
        if not self.matches:
            return None
        return max(self.matches, key=lambda m: m.containment)

    def to_dict(self) -> Dict[str, object]:
        return {
            "matches": [m.to_dict() for m in self.matches],
            "riskiest": self.riskiest.name if self.riskiest else None,
            "note": (
                "本结果为词面重合度统计，仅用于辅助确定检索与差异化方向，"
                "不构成新颖性/创造性的法律结论。"
            ),
        }


def _term_bag(text: str) -> Dict[str, int]:
    freq: Dict[str, int] = {}
    for tok in _bigrams(text):
        freq[tok] = freq.get(tok, 0) + 1
    return freq


def disclosure_corpus(disclosure: Disclosure) -> str:
    parts = [
        disclosure.title,
        disclosure.field,
        disclosure.solution,
        disclosure.embodiments,
        disclosure.claims_text,
        " ".join(disclosure.keywords),
    ]
    return "\n".join(p for p in parts if p)


def _level(containment: float) -> str:
    if containment >= HIGH_THRESHOLD:
        return "高"
    if containment >= MID_THRESHOLD:
        return "中"
    return "低"


def compare_prior_art(
    disclosure: Disclosure,
    prior_arts: Sequence[Tuple[str, str]],
    top_terms: int = 20,
) -> NoveltyResult:
    """把交底书与若干对比文件逐一比对。

    Parameters
    ----------
    disclosure:
        本申请的结构化交底书。
    prior_arts:
        ``(文件名, 对比文件全文)`` 序列，纯文本即可（PDF/Word 请先转文本）。
    top_terms:
        每篇对比文件最多返回多少个重合高频词。
    """
    result = NoveltyResult()
    own = _term_bag(disclosure_corpus(disclosure))
    own_set = set(own)
    if not own_set:
        raise ValueError("交底书的技术方案/权要内容为空，无法进行比对。")

    for name, text in prior_arts:
        other = _term_bag(text)
        other_set = set(other)
        shared = own_set & other_set
        union = own_set | other_set
        jaccard = len(shared) / len(union) if union else 0.0
        containment = len(shared) / len(own_set)
        shared_freq = sorted(
            ((t, min(own[t], other[t])) for t in shared),
            key=lambda kv: (-kv[1], kv[0]),
        )[:top_terms]
        result.matches.append(PriorArtMatch(
            name=name,
            jaccard=jaccard,
            containment=containment,
            overlap_size=len(shared),
            shared_terms=shared_freq,
            level=_level(containment),
        ))
    result.matches.sort(key=lambda m: -m.containment)
    return result
