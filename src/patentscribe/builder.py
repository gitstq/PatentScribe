"""交底书构建器：JSON 模板生成、加载与校验。

采用 JSON 作为唯一的零依赖交换格式（标准库 ``json`` 即可读写），
同时兼容 mine 子命令产出的骨架字典。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Union

from .models import PATENT_TYPES, Disclosure


class DisclosureError(ValueError):
    """交底书数据结构异常。"""


def dump_template(patent_type: str = "发明") -> Dict[str, Any]:
    """返回一份带填写说明的交底书模板。"""
    if patent_type not in PATENT_TYPES:
        raise DisclosureError(
            f"专利类型必须是 {PATENT_TYPES} 之一，收到：{patent_type!r}"
        )
    return {
        "title": "一种示例数据处理方法",
        "patent_type": patent_type,
        "inventors": ["张三", "李四"],
        "field": "本示例涉及数据处理技术领域，尤其涉及一种……的方法。",
        "background": (
            "现有方案通常采用……，在……场景下存在处理耗时长、"
            "资源占用高、准确率不足等问题。"
        ),
        "problems": [
            "问题1：现有方案在……情况下处理延迟高。",
            "问题2：现有方案无法适配……场景。",
        ],
        "solution": (
            "本方案提出一种……方法，包括：步骤 S1……；步骤 S2……；"
            "步骤 S3……，通过……实现……。"
        ),
        "effects": [
            "效果1：处理延迟降低约 40%。",
            "效果2：在……场景下适配性显著增强。",
        ],
        "embodiments": (
            "下面结合实施例详细说明。在一个实施例中，模块100用于……，"
            "模块200用于……；方法流程包括步骤 S101 至 S104……"
        ),
        "drawings": [
            {"figure": "图1", "desc": "本方案的整体架构示意图", "marks": "100,200"},
            {"figure": "图2", "desc": "方法流程示意图", "marks": "S101-S104"},
        ],
        "abstract": (
            "本方案公开了一种……方法与装置，通过……手段，解决……问题，"
            "实现……效果，可应用于……场景。"
        ),
        "claims_text": (
            "1. 一种数据处理方法，其特征在于，包括：\n"
            "获取待处理数据；\n"
            "对所述待处理数据执行第一处理，得到中间结果；\n"
            "对所述中间结果执行第二处理，得到输出结果。\n"
            "2. 根据权利要求1所述的方法，其特征在于，所述第一处理包括……。\n"
            "3. 根据权利要求1或2所述的方法，其特征在于，……。"
        ),
        "keywords": ["数据处理", "中间结果"],
    }


def load_disclosure(source: Union[str, Path, Dict[str, Any]]) -> Disclosure:
    """从 JSON 文件路径或字典加载 :class:`Disclosure`，并做结构校验。"""
    if isinstance(source, dict):
        data = source
    else:
        path = Path(source)
        if not path.exists():
            raise DisclosureError(f"文件不存在：{path}")
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise DisclosureError(f"JSON 解析失败（{path}）：{exc}") from exc
    if not isinstance(data, dict):
        raise DisclosureError("交底书根节点必须是 JSON 对象。")

    # 类型与默认值规范化
    normalized: Dict[str, Any] = {}
    list_fields = {"inventors", "problems", "effects", "keywords"}
    str_fields = {
        "title", "patent_type", "field", "background", "solution",
        "embodiments", "abstract", "claims_text",
    }
    for key in list_fields:
        value = data.get(key, [])
        if value is None:
            value = []
        if isinstance(value, str):
            value = [v.strip() for v in value.split("\n") if v.strip()]
        if not isinstance(value, list):
            raise DisclosureError(f"字段 {key} 必须是数组。")
        normalized[key] = [str(v) for v in value]
    for key in str_fields:
        normalized[key] = str(data.get(key, "") or "")
    drawings = data.get("drawings", []) or []
    if not isinstance(drawings, list):
        raise DisclosureError("字段 drawings 必须是数组。")
    clean_drawings = []
    for item in drawings:
        if isinstance(item, dict):
            clean_drawings.append({str(k): str(v) for k, v in item.items()})
    normalized["drawings"] = clean_drawings
    return Disclosure.from_dict(normalized)


def save_json(data: Dict[str, Any], path: Union[str, Path]) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return path
