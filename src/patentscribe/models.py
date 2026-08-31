"""核心数据模型。

All domain objects are plain dataclasses so they can be serialised to JSON
without custom encoders and remain easy to embed in other programs.
"""

from __future__ import annotations

from dataclasses import dataclass, field as dc_field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional


class Severity(str, Enum):
    """问题严重级别。"""

    ERROR = "error"   # 必须修复：会导致形式缺陷或权要逻辑错误
    WARN = "warn"     # 建议修复：存在保护范围/撰写质量风险
    INFO = "info"     # 提示：最佳实践层面的优化建议

    @property
    def label_cn(self) -> str:
        return {
            Severity.ERROR: "错误",
            Severity.WARN: "警告",
            Severity.INFO: "提示",
        }[self]


# 受支持的专利类型（中国国家知识产权局口径）
PATENT_TYPES = ("发明", "实用新型", "外观设计")


@dataclass
class Issue:
    """单条校验问题。"""

    code: str                         # 规则编号，例如 C003 / L101
    severity: Severity                # 严重级别
    location: str                     # 所在位置（章节/权利要求编号）
    message: str                      # 问题描述
    suggestion: str = ""              # 修改建议

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["severity"] = self.severity.value
        return d


@dataclass
class Claim:
    """单条权利要求。"""

    number: int                                   # 权项序号
    text: str                                     # 归一化后的完整文本
    kind: str = "independent"                     # independent / dependent
    subject: str = ""                             # 主题名称，如“一种数据处理方法”
    refs: List[int] = dc_field(default_factory=list)  # 引用的在先权项编号
    features: List[str] = dc_field(default_factory=list)  # 按分号切分的技术特征片段

    @property
    def is_independent(self) -> bool:
        return self.kind == "independent"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Disclosure:
    """专利技术交底书结构化模型。"""

    title: str = ""                                  # 发明名称
    patent_type: str = "发明"                        # 发明 / 实用新型 / 外观设计
    inventors: List[str] = dc_field(default_factory=list)      # 发明人
    field: str = ""                                  # 技术领域
    background: str = ""                             # 背景技术
    problems: List[str] = dc_field(default_factory=list)       # 现有技术存在的问题
    solution: str = ""                               # 技术方案（发明内容）
    effects: List[str] = dc_field(default_factory=list)        # 有益效果
    embodiments: str = ""                            # 具体实施方式
    drawings: List[Dict[str, str]] = dc_field(default_factory=list)  # 附图说明 [{figure,desc,marks}]
    abstract: str = ""                               # 摘要
    claims_text: str = ""                            # 权利要求书原文
    keywords: List[str] = dc_field(default_factory=list)       # 核心技术关键词
    extras: Dict[str, Any] = dc_field(default_factory=dict)    # 扩展字段，向前兼容

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    # ------------------------------------------------------------------
    # 便捷构造
    # ------------------------------------------------------------------
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Disclosure":
        """从普通字典构造，忽略未知字段（向前兼容模板扩展）。"""
        known = {f for f in cls.__dataclass_fields__}  # type: ignore[attr-defined]
        clean: Dict[str, Any] = {}
        extras: Dict[str, Any] = {}
        for key, value in data.items():
            if key in known:
                clean[key] = value
            else:
                extras[key] = value
        obj = cls(**clean)
        obj.extras = extras
        return obj

    def required_sections(self) -> Dict[str, str]:
        """章节名 → 文本，用于完整性检查。"""
        return {
            "发明名称": self.title,
            "技术领域": self.field,
            "背景技术": self.background,
            "技术方案": self.solution,
            "具体实施方式": self.embodiments,
            "摘要": self.abstract,
            "权利要求书": self.claims_text,
        }


@dataclass
class CheckReport:
    """一次完整校验的结果。"""

    issues: List[Issue] = dc_field(default_factory=list)
    claims: List[Claim] = dc_field(default_factory=list)

    @property
    def errors(self) -> List[Issue]:
        return [i for i in self.issues if i.severity == Severity.ERROR]

    @property
    def warnings(self) -> List[Issue]:
        return [i for i in self.issues if i.severity == Severity.WARN]

    @property
    def infos(self) -> List[Issue]:
        return [i for i in self.issues if i.severity == Severity.INFO]

    @property
    def passed(self) -> bool:
        """没有错误级问题即视为通过（警告不阻断）。"""
        return not self.errors

    def add(self, issue: Issue) -> None:
        self.issues.append(issue)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "error_count": len(self.errors),
            "warn_count": len(self.warnings),
            "info_count": len(self.infos),
            "issues": [i.to_dict() for i in self.issues],
            "claims": [c.to_dict() for c in self.claims],
        }
