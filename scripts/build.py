#!/usr/bin/env python3
"""零依赖分发包构建脚本：生成 sdist(.tar.gz) 与 wheel(.whl)。

即使环境中没有 pip / build / setuptools，也能用标准库完成打包，
产物符合 wheel 与 sdist 的基本规范，可直接 pip install。

用法：
    python scripts/build.py              # 同时生成 wheel 与 sdist
    python scripts/build.py --wheel      # 仅 wheel
    python scripts/build.py --sdist      # 仅 sdist
"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import io
import tarfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "patentscribe"
DIST = ROOT / "dist"
NAME = "patentscribe"
VERSION = "1.0.0"

METADATA = """\
Metadata-Version: 2.1
Name: patentscribe
Version: 1.0.0
Summary: 中国专利交底书与权利要求结构化撰写、自检与多格式导出工具（零依赖、离线）
Author: PatentScribe contributors
License: MIT
License-File: LICENSE
Keywords: patent,china-patent,cnipa,disclosure,claims,专利,技术交底书,权利要求
Classifier: Programming Language :: Python :: 3
Classifier: Programming Language :: Python :: 3.9
Classifier: License :: OSI Approved :: MIT License
Classifier: Operating System :: OS Independent
Classifier: Environment :: Console
Requires-Python: >=3.9
Project-URL: Homepage, https://github.com/gitstq/PatentScribe
Project-URL: Repository, https://github.com/gitstq/PatentScribe

"""

WHEEL_META = """\
Wheel-Version: 1.0
Generator: patentscribe-stdlib-builder (1.0.0)
Root-Is-Purelib: true
Tag: py3-none-any
"""

ENTRY_POINTS = """\
[console_scripts]
patentscribe = patentscribe.cli:main
"""


def _sha256_b64(data: bytes) -> str:
    digest = hashlib.sha256(data).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


def _record_line(path: str, data: bytes) -> str:
    return f"{path},sha256={_sha256_b64(data)},{len(data)}"


def build_wheel() -> Path:
    DIST.mkdir(exist_ok=True)
    wheel_path = DIST / f"{NAME}-{VERSION}-py3-none-any.whl"
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    metadata = METADATA + readme
    records: list[tuple[str, bytes]] = []

    package_files = []
    for py in sorted(SRC.rglob("*.py")):
        arc = f"{NAME}/{py.relative_to(SRC).as_posix()}"
        package_files.append((arc, py.read_bytes()))
    dist_info = f"{NAME}-{VERSION}.dist-info"

    with zipfile.ZipFile(wheel_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for arc, data in package_files:
            zf.writestr(arc, data)
            records.append((arc, data))
        license_data = (ROOT / "LICENSE").read_bytes()
        zf.writestr(f"{dist_info}/LICENSE", license_data)
        records.append((f"{dist_info}/LICENSE", license_data))
        zf.writestr(f"{dist_info}/METADATA", metadata.encode("utf-8"))
        records.append((f"{dist_info}/METADATA", metadata.encode("utf-8")))
        zf.writestr(f"{dist_info}/WHEEL", WHEEL_META.encode("utf-8"))
        records.append((f"{dist_info}/WHEEL", WHEEL_META.encode("utf-8")))
        zf.writestr(f"{dist_info}/entry_points.txt", ENTRY_POINTS.encode("utf-8"))
        records.append((f"{dist_info}/entry_points.txt", ENTRY_POINTS.encode("utf-8")))

        buf = io.StringIO()
        writer = csv.writer(buf, lineterminator="\n")
        for arc, data in records:
            writer.writerow([arc, f"sha256={_sha256_b64(data)}", len(data)])
        writer.writerow([f"{dist_info}/RECORD", "", ""])
        zf.writestr(f"{dist_info}/RECORD", buf.getvalue())
    return wheel_path


def build_sdist() -> Path:
    DIST.mkdir(exist_ok=True)
    sdist_path = DIST / f"{NAME}-{VERSION}.tar.gz"
    include_dirs = ["src", "tests", "examples", "docs", "scripts"]
    include_files = [
        "pyproject.toml", "requirements.txt", "README.md", "README.en-US.md",
        "README.zh-TW.md", "README.ja.md", "LICENSE", "CONTRIBUTING.md",
        "CHANGELOG.md", "Makefile", ".gitignore",
    ]
    with tarfile.open(sdist_path, "w:gz") as tf:
        for rel in include_files:
            p = ROOT / rel
            if p.exists():
                tf.add(p, arcname=f"{NAME}-{VERSION}/{rel}")
        for d in include_dirs:
            base = ROOT / d
            if not base.exists():
                continue
            for p in sorted(base.rglob("*")):
                if p.is_file() and "__pycache__" not in p.parts:
                    tf.add(p, arcname=f"{NAME}-{VERSION}/{p.relative_to(ROOT).as_posix()}")
    return sdist_path


def main() -> int:
    parser = argparse.ArgumentParser(description="PatentScribe 零依赖打包脚本")
    parser.add_argument("--wheel", action="store_true")
    parser.add_argument("--sdist", action="store_true")
    args = parser.parse_args()
    do_all = not args.wheel and not args.sdist

    made = []
    if do_all or args.wheel:
        made.append(build_wheel())
    if do_all or args.sdist:
        made.append(build_sdist())
    for p in made:
        print(f"built: {p.relative_to(ROOT)}  ({p.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
