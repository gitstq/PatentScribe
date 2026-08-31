<div align="center">

# 🖋️ PatentScribe · 专利交底书撰写与权要自检工具包

### 零依赖 · 离线运行 · 确定性规则引擎 —— 让真正做研发的人，也能交出专业的技术交底书

**简体中文** ｜ [繁體中文](./README.zh-TW.md) ｜ [English](./README.en-US.md) ｜ [日本語](./README.ja.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Zero Dependency](https://img.shields.io/badge/dependencies-zero-success.svg)](#-快速开始)
[![Tests](https://img.shields.io/badge/tests-52%20passed-brightgreen.svg)](#-测试)
[![Version](https://img.shields.io/badge/version-v1.0.0-orange.svg)](https://github.com/gitstq/PatentScribe/releases)

</div>

---

## 🎉 项目介绍

**PatentScribe** 是一款面向中国专利申请场景的**技术交底书结构化撰写、权利要求自检与多格式导出工具**。它不依赖任何大模型、不联网、不安装任何第三方库，仅用 Python 标准库即可运行，输出结果**确定、可复现、可审计**。

很多研发工程师都遇到过这样的困境：方案是自己设计的、代码是自己写的，可到了要申请专利时，却卡在「发明点怎么挖、权利要求怎么布局、交底书怎么一次写到位」。而市面上的同类工具要么是绑定大模型的"智能体技能"（内容不可复现、数据要出内网），要么是沉重的商业代理系统。

**PatentScribe 把其中可以被规则化的环节全部自动化：**

- 🧭 从零散技术笔记中**挖掘候选发明点**（问题 → 手段 → 效果）；
- 🧩 用一份 JSON 骨架**结构化组织交底书**，章节不遗漏；
- ⚖️ 自动解析权利要求、构建**引用依赖树**，揪出悬空引用、多项引多项、前引错误等硬伤；
- 📋 按《专利法》《专利法实施细则》《专利审查指南》的形式要求执行 **30+ 条形式审查规则**；
- 🔎 与对比文件做**术语重合度比对**，辅助判断新颖性/创造性的检索方向；
- 📄 一键导出 **Markdown / 自包含 HTML / 可编辑 Word（.docx）** 三种交付物。

> 🌱 **灵感来源**：本项目从 GitHub Trending 上的"中国专利智能体技能"类项目获得灵感——我们认同"降低专利撰写门槛"的方向，但选择了一条完全不同的技术路线：**用确定性规则引擎替代概率式生成**，让敏感技术资料不必离开内网，让每一条审查结论都能对应到明确的规则编号。全部代码为独立自研，未复制任何项目的源码。

---

## ✨ 核心特性

### 🧠 发明点挖掘（`mine`）
- 基于**句式引导词 + 中文二元特征**的确定性抽取，自动归类"现有技术问题 / 技术手段 / 有益效果"；
- 自动组装 **问题→手段→效果** 三元组，形成候选发明点清单；
- 词频统计提取核心关键词，结果跨运行、跨平台**完全一致**。

### ⚖️ 权利要求自检（`claims` / `lint`）
- 支持 `1.`、`1、`、`【1】`、`权利要求1.` 等多种编号写法，支持 `1至3`、`1或2` 等**引用区间自动展开**；
- 自动识别**独权 / 从权**、提取主题名称与技术特征片段；
- 构建完整**引用依赖图**，输出 ASCII 依赖树与每项权要的引用深度；
- 覆盖中国专利实务中的典型硬伤：

| 规则 | 检查内容 |
|---|---|
| C001 | 权项编号必须从 1 连续编号，不跳号、不重号 |
| C002 | 至少存在一条独立权利要求 |
| C003 | 禁止悬空引用（引用不存在的权项） |
| C004 | 从权只能引用在先权项，禁止后引 |
| C005 | 独权建议使用"其特征在于"两段式写法 |
| C006 | 一条权项只能在末尾使用一个句号 |
| C008 | **多项从属权利要求不得引用另一项多项从属权利要求** |
| C009 | 引用链不得成环 |
| C010 | 方法/装置/设备/介质独权的类别布局提示 |

### 📋 形式审查规则引擎（`lint`，L1xx–L7xx）
- **完整性**：必填章节缺失即报错（L101）；
- **名称规范**：发明名称长度、宣传性用语检查（L201/L202）；
- **摘要规范**：300 字上限、商业宣传语识别（L301/L302）；
- **用语质量**：自动标记"最好/最佳/大约/左右/例如/高效"等模糊或宣传用语（L401）；
- **支撑充分性**：独权技术特征是否在"具体实施方式"中得到说明书支撑（L501）；
- **附图标记一致性**：权要中的标记是否在实施方式/附图说明中出现（L601/L602）；
- 三级问题分级（**错误 / 警告 / 提示**），错误级问题以非零退出码阻断流程，可直接接入 CI。

### 🔎 三性辅助比对（`novelty`）
- 基于术语集合计算 **Jaccard 相似度**与**包含度（containment）**；
- 输出高频重合术语与"高 / 中 / 低"风险分档，辅助确定差异化与检索方向；
- 明确标注：词面统计**不构成**新颖性/创造性的法律结论。

### 📦 多格式导出（`export`）
- **Markdown**：适合 Git 版本管理与评审；
- **HTML**：单文件、内联样式、零外链，双击即可在浏览器查看；
- **DOCX**：标准库直接拼装 OOXML，可用 Word / WPS / LibreOffice 打开继续编辑；
- 可选把自检结果一并嵌入导出物，交付即留痕。

### 🛡️ 工程级品质
- **零第三方依赖**：仅用 Python 标准库，Python 3.9+ 全平台可用；
- **完全离线**：不发起任何网络请求，技术资料不出本机/内网；
- **52 个单元测试**覆盖解析、校验、挖掘、比对、导出、CLI 全链路；
- 同时提供 **命令行、Python 库、`python -m`** 三种使用方式。

---

## 🚀 快速开始

### 📌 环境要求

| 项目 | 要求 |
|---|---|
| Python | **3.9 / 3.10 / 3.11 / 3.12**（推荐 3.10+） |
| 操作系统 | Windows / macOS / Linux 全平台 |
| 第三方依赖 | **无** |
| 网络 | **不需要**（完全离线） |

### 方式一：pip 安装（推荐）

```bash
# 从 Release 页下载 wheel 后本地安装，无需联网拉依赖
pip install patentscribe-1.0.0-py3-none-any.whl

# 验证安装
patentscribe --version
```

### 方式二：源码免安装运行

```bash
git clone https://github.com/gitstq/PatentScribe.git
cd PatentScribe
export PYTHONPATH=src        # Windows PowerShell: $env:PYTHONPATH="src"
python -m patentscribe --version
```

### 方式三：可编辑模式（开发者）

```bash
pip install -e .
patentscribe --help
```

### ⚡ 30 秒上手

```bash
# 1. 生成一份交底书模板（带示例填写说明）
patentscribe init -o my_disclosure.json

# 2. 填写 JSON 后做形式审查与权要自检
patentscribe lint -i my_disclosure.json

# 3. 查看权利要求依赖树
patentscribe claims -i my_disclosure.json

# 4. 一键导出 Markdown / HTML / Word（含自检结果）
patentscribe export -i my_disclosure.json -f all -o dist --name 交底书 --with-check
```

---

## 📖 详细使用指南

### 🧭 命令总览

| 子命令 | 作用 | 关键参数 |
|---|---|---|
| `init` | 生成交底书 JSON 模板 | `-o 输出路径`、`--type 发明/实用新型/外观设计` |
| `mine` | 从技术笔记挖掘发明点 | `-i 笔记.txt`、`--skeleton 直接生成骨架`、`--format json` |
| `lint` | 形式审查 + 权要自检 | `-i 交底书.json`、`--json` |
| `claims` | 权要解析与依赖树 | `-i 交底书.json` |
| `novelty` | 对比文件重合度比对 | `-i 交底书.json -p 对比文件1.txt 对比文件2.txt` |
| `export` | 导出交付物 | `-f md/html/docx/all`、`-o 目录`、`--with-check` |
| `report` | 完整 Markdown 自检报告 | `-i 交底书.json -o 报告.md` |

### 1️⃣ 从零散笔记开始：`mine`

把会议纪要、设计文档片段、聊天整理稿存成纯文本，PatentScribe 会自动抽取线索：

```bash
python -m patentscribe mine -i examples/example_notes.txt
```

输出示例：

```text
=== 候选发明点（问题 → 手段 → 效果） ===
[IP01] 手段：引入动态权重调度器
      解决：现有技术在高并发请求调度场景下，通常采用静态权重轮询策略……
      效果：从而将平均响应延迟降低约40%……
=== 提取关键词 ===
节点、权重、负载、响应、延迟、控制、流量、突发、窗口、请求……
```

加上 `--skeleton -o skeleton.json` 即可直接生成一份可继续填写的交底书骨架。

### 2️⃣ 结构化交底书字段说明

| 字段 | 含义 | 是否必填 |
|---|---|---|
| `title` | 发明名称（建议 ≤25 字） | ✅ |
| `patent_type` | 发明 / 实用新型 / 外观设计 | ✅ |
| `field` | 技术领域 | ✅ |
| `background` | 背景技术 | ✅ |
| `problems` | 现有技术问题列表 | 建议 |
| `solution` | 技术方案（发明内容） | ✅ |
| `effects` | 有益效果列表 | 建议 |
| `embodiments` | 具体实施方式（须支撑独权特征） | ✅ |
| `drawings` | 附图说明（图号、说明、标记） | 有附图时必填 |
| `abstract` | 摘要（≤300 字） | ✅ |
| `claims_text` | 权利要求书原文 | ✅ |
| `keywords` | 核心关键词 | 建议 |

完整范例见 [`examples/example_disclosure.json`](./examples/example_disclosure.json)。

### 3️⃣ 权利要求自检：`claims`

```bash
python -m patentscribe claims -i examples/example_disclosure.json
```

```text
├─ 1 [独权] 一种动态权重请求调度方法
│  ├─ 2 [从权] 根据权利要求1所述的方法
│  │  └─ 4 [从权] 根据权利要求1至3任一项所述的方法
│  │     └─ 5 [从权] 根据权利要求4所述的方法
│  ├─ 3 [从权] 根据权利要求1所述的方法
……
```

### 4️⃣ 对比文件比对：`novelty`

```bash
python -m patentscribe novelty \
  -i examples/example_disclosure.json \
  -p examples/example_prior_art.txt
```

```text
- example_prior_art.txt：包含度 4.9%，Jaccard 3.8%，重合术语 15 个，风险档：低
  高频重合：权重、负载、服务、用于、业务、分发、加权、均衡……
```

### 5️⃣ 作为 Python 库嵌入

```python
from patentscribe import load_disclosure, lint_disclosure, to_docx

disclosure = load_disclosure("my_disclosure.json")
report = lint_disclosure(disclosure)

print("通过" if report.passed else "未通过")
for issue in report.issues:
    print(issue.code, issue.location, issue.message)

to_docx(disclosure, "dist/技术交底书.docx")
```

### 6️⃣ 接入 CI 流水线

`lint` 在存在**错误级**问题时返回退出码 `1`，可直接用于合并门禁：

```bash
patentscribe lint -i disclosure.json --json > check.json || exit 1
```

### 🖥️ 运行截图 / 演示占位

> 完整终端录屏与导出示例将随后续版本补充到 `docs/` 目录；当前可运行
> `make demo` 一键复现示例中的全部命令与产物。

---

## 💡 设计思路与迭代规划

### 🧱 为什么是"规则引擎"而不是"大模型"？

1. **可复现**：同一份输入永远得到同一份结论，便于评审与回归；
2. **可审计**：每条结论都有规则编号（C0xx/Lxxx），能追溯到审查指南依据；
3. **零信任成本**：技术交底书属于核心机密，规则引擎完全离线，资料不出内网；
4. **零维护成本**：不依赖任何在线服务、API Key 与第三方包，十年后仍能运行。

### 🧩 技术选型

| 层 | 选型 | 理由 |
|---|---|---|
| 语言 | Python 3.9+ | 专利工程师与研发都易读易改；标准库足够覆盖全部需求 |
| 解析 | 正则 + 有限状态切分 | 权要编号/引用模式明确，规则比模型更可靠 |
| 中文处理 | 自实现二元特征 + 停用表 | 不引入 jieba 等重量依赖，保持零依赖与确定性 |
| DOCX | 标准库 `zipfile` 拼装 OOXML | 无需 python-docx 即可产出 Word 可编辑文件 |
| 打包 | 自写零依赖构建脚本 | 无 build/setuptools 也能产出标准 wheel/sdist |

### 🗺️ 迭代路线图

- [x] v1.0.0：交底书模板、发明点挖掘、权要依赖分析、30+ 形式规则、三格式导出、对比文件比对
- [ ] v1.1：外观设计专利（图式说明、六视图清单）专项规则
- [ ] v1.2：权利要求**修改对照**（原始/修改稿差异比对与修改依据生成）
- [ ] v1.3：批量项目模式（一个目录下多份交底书批量自检与汇总）
- [ ] v2.0：可选的本地大模型适配层（默认仍保持零依赖离线）

### 🙋 社区贡献方向

补充审查规则、完善双语术语表、增加更多真实场景示例、补充终端录屏，都非常欢迎，详见贡献指南。

---

## 📦 打包与部署指南

PatentScribe 属于**工具库 / CLI 类项目**（纯 Python，跨平台），无需安装可执行程序，按下列方式分发：

### 构建分发包

```bash
# 方式 A：零依赖标准库构建（推荐，无需安装任何构建工具）
python scripts/build.py
# 产物：
#   dist/patentscribe-1.0.0-py3-none-any.whl   （wheel，跨平台通用）
#   dist/patentscribe-1.0.0.tar.gz             （源码分发包）

# 方式 B：标准 PEP 517 构建
pip install build && python -m build
```

### 安装与分发

```bash
pip install dist/patentscribe-1.0.0-py3-none-any.whl   # 单机安装
pipx install ./dist/patentscribe-1.0.0-py3-none-any.whl  # 隔离环境安装
```

### 兼容性说明

- 兼容 CPython 3.9–3.12，Windows / macOS / Linux；
- wheel 标记为 `py3-none-any`，**无平台相关二进制**；
- DOCX 产物已通过标准 XML 解析器与 Word/WPS 打开验证；
- 内网/离线环境直接拷贝 wheel 安装即可，无需访问 PyPI。

---

## 🧪 测试

```bash
make test
# 等价于：
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

一键复现完整示例流程：

```bash
make demo
```

---

## 🤝 贡献指南

我们欢迎所有形式的贡献，请遵循以下约定：

1. **Issue**：提交问题请附上输入文件片段（可脱敏）、执行命令与实际输出；规则误报/漏报请标注对应规则编号。
2. **Fork & PR**：
   - 提交信息遵循 **Angular Convention**：`feat: 新功能` / `fix: 修复` / `docs: 文档` / `refactor: 重构` / `test: 测试` / `chore: 杂项`；
   - 新规则必须配套单元测试，且不引入第三方依赖；
   - 确保 `make test` 全部通过。
3. **新增审查规则**：在 `linter.py`/`claim_parser.py` 中按编号段续编（C 系列=权要，L 系列=说明书），并在 README 规则表中登记。
4. 文档四种语言版本同步更新（至少保证简中与英文）。

---

## ❓ 常见问题

**Q：它能替代专利代理人吗？**
A：不能。PatentScribe 负责把交底材料结构化、把形式硬伤消灭在提交前，并辅助检索方向；创造性高度、权利要求布局策略仍需与专业代理人协作。

**Q：会上传我的技术资料吗？**
A：不会。程序没有任何网络代码，全部计算在本机完成，可在内网/断网环境审计源码后使用。

**Q：为什么不直接调用大模型生成交底书？**
A：概率式生成不可复现、可能"编造"技术细节，且资料需出内网。PatentScribe 的定位是**确定性的质量底座**；未来会提供可选的本地模型适配层，但默认永远离线。

**Q：支持外观设计专利吗？**
A：v1.0 以发明/实用新型为主，外观设计的专项规则在路线图中（v1.1）。

---

## 📄 开源协议

本项目基于 **[MIT License](./LICENSE)** 开源，允许自由使用、修改、分发与商用，保留版权声明即可。

> ⚠️ 本工具输出的所有审查与比对意见仅为撰写辅助，不构成法律意见；专利申请的授权前景请以国家知识产权局审查结论及专业代理意见为准。

<div align="center">

如果这个项目帮你省下了熬夜写交底书的时间，欢迎点一颗 ⭐ 支持我们！

**Made with ❤️ by PatentScribe contributors**

</div>
