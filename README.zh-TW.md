<div align="center">

# 🖋️ PatentScribe · 專利交底書撰寫與權利要求自檢工具包

### 零依賴 · 離線執行 · 確定性規則引擎 —— 讓真正做研發的人，也能交出專業的技術交底書

[简体中文](./README.md) ｜ **繁體中文** ｜ [English](./README.en-US.md) ｜ [日本語](./README.ja.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Zero Dependency](https://img.shields.io/badge/dependencies-zero-success.svg)](#-快速開始)
[![Tests](https://img.shields.io/badge/tests-52%20passed-brightgreen.svg)](#-測試)
[![Version](https://img.shields.io/badge/version-v1.0.0-orange.svg)](https://github.com/gitstq/PatentScribe/releases)

</div>

---

## 🎉 專案介紹

**PatentScribe** 是一款面向中國大陸專利申請場景的**技術交底書結構化撰寫、權利要求自檢與多格式匯出工具**。它不依賴任何大模型、不聯網、不安裝任何第三方套件，僅用 Python 標準函式庫即可執行，輸出結果**確定、可重現、可稽核**。

許多研發工程師都遇過這樣的困境：方案是自己設計的、程式碼是自己寫的，可到了要申請專利時，卻卡在「發明點怎麼挖、權利要求怎麼佈局、交底書怎麼一次寫到位」。市面上的同類工具要嘛是綁定大模型的「智能體技能」（內容不可重現、資料還得傳出內網），要嘛是笨重的商業代理系統。

**PatentScribe 把其中可以被規則化的環節全部自動化：**

- 🧭 從零散技術筆記中**挖掘候選發明點**（問題 → 手段 → 效果）；
- 🧩 用一份 JSON 骨架**結構化組織交底書**，章節不遺漏；
- ⚖️ 自動解析權利要求、建構**引用依賴樹**，揪出懸空引用、多項引多項、後引錯誤等硬傷；
- 📋 依據《專利法》《專利法實施細則》《專利審查指南》的形式要求執行 **30+ 條形式審查規則**；
- 🔎 與對比文件做**術語重合度比對**，輔助判斷新穎性/創造性的檢索方向；
- 📄 一鍵匯出 **Markdown / 自包含 HTML / 可編輯 Word（.docx）** 三種交付物。

> 🌱 **靈感來源**：本專案從 GitHub Trending 上的「中國專利智能體技能」類專案獲得靈感——我們認同「降低專利撰寫門檻」的方向，但選擇了一條完全不同的技術路線：**用確定性規則引擎取代機率式生成**，讓敏感技術資料不必離開內網，讓每一條審查結論都能對應到明確的規則編號。全部程式碼為獨立自研，未複製任何專案的原始碼。

---

## ✨ 核心特性

### 🧠 發明點挖掘（`mine`）
- 基於**句式引導詞 + 中文二元特徵**的確定性擷取，自動歸類「現有技術問題 / 技術手段 / 有益效果」；
- 自動組裝 **問題→手段→效果** 三元組，形成候選發明點清單；
- 詞頻統計擷取核心關鍵詞，結果跨執行、跨平台**完全一致**。

### ⚖️ 權利要求自檢（`claims` / `lint`）
- 支援 `1.`、`1、`、`【1】`、`權利要求1.` 等多種編號寫法，支援 `1至3`、`1或2` 等**引用區間自動展開**；
- 自動識別**獨權 / 從權**、擷取主題名稱與技術特徵片段；
- 建構完整**引用依賴圖**，輸出 ASCII 依賴樹與每項權項的引用深度；
- 覆蓋中國大陸專利實務中的典型硬傷：

| 規則 | 檢查內容 |
|---|---|
| C001 | 權項編號必須從 1 連續編號，不跳號、不重號 |
| C002 | 至少存在一條獨立權利要求 |
| C003 | 禁止懸空引用（引用不存在的權項） |
| C004 | 從權只能引用在先權項，禁止後引 |
| C005 | 獨權建議使用「其特徵在於」兩段式寫法 |
| C006 | 一條權項只能在末尾使用一個句號 |
| C008 | **多項從屬權利要求不得引用另一項多項從屬權利要求** |
| C009 | 引用鏈不得成環 |
| C010 | 方法/裝置/設備/媒體獨權的類別佈局提示 |

### 📋 形式審查規則引擎（`lint`，L1xx–L7xx）
- **完整性**：必填章節缺失即回報錯誤（L101）；
- **名稱規範**：發明名稱長度、宣傳性用語檢查（L201/L202）；
- **摘要規範**：300 字上限、商業宣傳語識別（L301/L302）；
- **用語品質**：自動標記「最好/最佳/大約/左右/例如/高效」等模糊或宣傳用語（L401）；
- **支援充分性**：獨權技術特徵是否在「具體實施方式」中得到說明書支撐（L501）；
- **附圖標記一致性**：權要中的標記是否在實施方式/附圖說明中出現（L601/L602）；
- 三級問題分級（**錯誤 / 警告 / 提示**），錯誤級問題以非零結束碼阻斷流程，可直接接入 CI。

### 🔎 三性輔助比對（`novelty`）
- 基於術語集合計算 **Jaccard 相似度**與**包含度（containment）**；
- 輸出高頻重合術語與「高 / 中 / 低」風險分檔，輔助確定差異化與檢索方向；
- 明確標註：詞面統計**不構成**新穎性/創造性的法律結論。

### 📦 多格式匯出（`export`）
- **Markdown**：適合 Git 版本管理與評審；
- **HTML**：單一檔案、內聯樣式、零外鏈，雙擊即可在瀏覽器檢視；
- **DOCX**：標準函式庫直接組裝 OOXML，可用 Word / WPS / LibreOffice 開啟繼續編輯；
- 可選把自檢結果一併嵌入匯出物，交付即留痕。

### 🛡️ 工程級品質
- **零第三方依賴**：僅用 Python 標準函式庫，Python 3.9+ 全平台可用；
- **完全離線**：不發起任何網路請求，技術資料不出本機/內網；
- **52 個單元測試**覆蓋解析、校驗、挖掘、比對、匯出、CLI 全鏈路；
- 同時提供**命令列、Python 函式庫、`python -m`** 三種使用方式。

---

## 🚀 快速開始

### 📌 環境需求

| 項目 | 要求 |
|---|---|
| Python | **3.9 / 3.10 / 3.11 / 3.12**（推薦 3.10+） |
| 作業系統 | Windows / macOS / Linux 全平台 |
| 第三方依賴 | **無** |
| 網路 | **不需要**（完全離線） |

### 方式一：pip 安裝（推薦）

```bash
# 從 Release 頁下載 wheel 後本機安裝，無需聯網拉取依賴
pip install patentscribe-1.0.0-py3-none-any.whl

patentscribe --version
```

### 方式二：原始碼免安裝執行

```bash
git clone https://github.com/gitstq/PatentScribe.git
cd PatentScribe
export PYTHONPATH=src        # Windows PowerShell: $env:PYTHONPATH="src"
python -m patentscribe --version
```

### 方式三：可編輯模式（開發者）

```bash
pip install -e .
patentscribe --help
```

### ⚡ 30 秒上手

```bash
# 1. 產生一份交底書範本（帶範例填寫說明）
patentscribe init -o my_disclosure.json

# 2. 填寫 JSON 後做形式審查與權要自檢
patentscribe lint -i my_disclosure.json

# 3. 檢視權利要求依賴樹
patentscribe claims -i my_disclosure.json

# 4. 一鍵匯出 Markdown / HTML / Word（含自檢結果）
patentscribe export -i my_disclosure.json -f all -o dist --name 交底書 --with-check
```

---

## 📖 詳細使用指南

### 🧭 指令總覽

| 子指令 | 作用 | 關鍵參數 |
|---|---|---|
| `init` | 產生交底書 JSON 範本 | `-o 輸出路徑`、`--type` |
| `mine` | 從技術筆記挖掘發明點 | `-i 筆記.txt`、`--skeleton`、`--format json` |
| `lint` | 形式審查 + 權要自檢 | `-i 交底書.json`、`--json` |
| `claims` | 權要解析與依賴樹 | `-i 交底書.json` |
| `novelty` | 對比文件重合度比對 | `-i 交底書.json -p 對比文件1.txt 對比文件2.txt` |
| `export` | 匯出交付物 | `-f md/html/docx/all`、`-o 目錄`、`--with-check` |
| `report` | 完整 Markdown 自檢報告 | `-i 交底書.json -o 報告.md` |

### 1️⃣ 從零散筆記開始：`mine`

把會議紀要、設計文件片段、聊天整理稿存成純文字，PatentScribe 會自動擷取線索：

```bash
python -m patentscribe mine -i examples/example_notes.txt
```

加上 `--skeleton -o skeleton.json` 即可直接產生一份可繼續填寫的交底書骨架。完整範例見 [`examples/example_disclosure.json`](./examples/example_disclosure.json)。

### 2️⃣ 結構化交底書欄位說明

| 欄位 | 含義 | 是否必填 |
|---|---|---|
| `title` | 發明名稱（建議 ≤25 字） | ✅ |
| `patent_type` | 發明 / 實用新型 / 外觀設計 | ✅ |
| `field` | 技術領域 | ✅ |
| `background` | 背景技術 | ✅ |
| `problems` | 現有技術問題清單 | 建議 |
| `solution` | 技術方案（發明內容） | ✅ |
| `effects` | 有益效果清單 | 建議 |
| `embodiments` | 具體實施方式（須支撐獨權特徵） | ✅ |
| `drawings` | 附圖說明（圖號、說明、標記） | 有附圖時必填 |
| `abstract` | 摘要（≤300 字） | ✅ |
| `claims_text` | 權利要求書原文 | ✅ |
| `keywords` | 核心關鍵詞 | 建議 |

### 3️⃣ 權利要求自檢：`claims`

```bash
python -m patentscribe claims -i examples/example_disclosure.json
```

會輸出每條獨權/從權的 ASCII 依賴樹、引用深度與問題清單。

### 4️⃣ 對比文件比對：`novelty`

```bash
python -m patentscribe novelty \
  -i examples/example_disclosure.json \
  -p examples/example_prior_art.txt
```

### 5️⃣ 作為 Python 函式庫嵌入

```python
from patentscribe import load_disclosure, lint_disclosure, to_docx

disclosure = load_disclosure("my_disclosure.json")
report = lint_disclosure(disclosure)

print("通過" if report.passed else "未通過")
for issue in report.issues:
    print(issue.code, issue.location, issue.message)

to_docx(disclosure, "dist/技術交底書.docx")
```

### 6️⃣ 接入 CI 流水線

`lint` 在存在**錯誤級**問題時返回結束碼 `1`，可直接用於合併門禁：

```bash
patentscribe lint -i disclosure.json --json > check.json || exit 1
```

### 🖥️ 展示素材佔位

> 完整終端錄影與匯出示例將於後續版本補充到 `docs/` 目錄；目前可執行 `make demo` 一鍵重現範例中的全部指令與產物。

---

## 💡 設計思路與迭代規劃

### 🧱 為什麼是「規則引擎」而不是「大模型」？

1. **可重現**：同一份輸入永遠得到同一份結論，便於評審與回歸；
2. **可稽核**：每條結論都有規則編號（C0xx/Lxxx），能追溯到審查指南依據；
3. **零信任成本**：技術交底書屬於核心機密，規則引擎完全離線，資料不出內網；
4. **零維護成本**：不依賴任何線上服務、API Key 與第三方套件，十年後仍能執行。

### 🧩 技術選型

| 層 | 選型 | 理由 |
|---|---|---|
| 語言 | Python 3.9+ | 專利工程師與研發都易讀易改；標準函式庫足以覆蓋全部需求 |
| 解析 | 正規表示式 + 有限狀態切分 | 權要編號/引用模式明確，規則比模型更可靠 |
| 中文處理 | 自實作二元特徵 + 停用表 | 不引入 jieba 等重量依賴，保持零依賴與確定性 |
| DOCX | 標準函式庫 `zipfile` 組裝 OOXML | 無需 python-docx 即可產出 Word 可編輯檔案 |
| 打包 | 自寫零依賴建構腳本 | 無 build/setuptools 也能產出標準 wheel/sdist |

### 🗺️ 迭代路線圖

- [x] v1.0.0：交底書範本、發明點挖掘、權要依賴分析、30+ 形式規則、三格式匯出、對比文件比對
- [ ] v1.1：外觀設計專利（圖式說明、六視圖清單）專項規則
- [ ] v1.2：權利要求**修改對照**（原始/修改稿差異比對與修改依據產生）
- [ ] v1.3：批次專案模式（一個目錄下多份交底書批次自檢與彙總）
- [ ] v2.0：可選的本機大模型適配層（預設仍保持零依賴離線）

### 🙋 社群貢獻方向

補充審查規則、完善雙語術語表、增加更多真實場景範例、補充終端錄影，都非常歡迎，詳見貢獻指南。

---

## 📦 打包與部署指南

PatentScribe 屬於**工具庫 / CLI 類專案**（純 Python，跨平台），無需安裝可執行程式，按下列方式分發：

### 建構分發包

```bash
# 方式 A：零依賴標準函式庫建構（推薦，無需安裝任何建構工具）
python scripts/build.py
# 產物：
#   dist/patentscribe-1.0.0-py3-none-any.whl   （wheel，跨平台通用）
#   dist/patentscribe-1.0.0.tar.gz             （原始碼分發包）

# 方式 B：標準 PEP 517 建構
pip install build && python -m build
```

### 安裝與分發

```bash
pip install dist/patentscribe-1.0.0-py3-none-any.whl
pipx install ./dist/patentscribe-1.0.0-py3-none-any.whl
```

### 相容性說明

- 相容 CPython 3.9–3.12，Windows / macOS / Linux；
- wheel 標記為 `py3-none-any`，**無平台相關二進位檔**；
- DOCX 產物已通過標準 XML 解析器與 Word/WPS 開啟驗證；
- 內網/離線環境直接拷貝 wheel 安裝即可，無需存取 PyPI。

---

## 🧪 測試

```bash
make test
# 等價於：
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

一鍵重現完整範例流程：

```bash
make demo
```

---

## 🤝 貢獻指南

我們歡迎所有形式的貢獻，請遵循以下約定：

1. **Issue**：提交問題請附上輸入檔案片段（可脫敏）、執行指令與實際輸出；規則誤報/漏報請標註對應規則編號。
2. **Fork & PR**：
   - 提交資訊遵循 **Angular Convention**：`feat: 新功能` / `fix: 修復` / `docs: 文件` / `refactor: 重構` / `test: 測試` / `chore: 雜項`；
   - 新規則必須配套單元測試，且不引入第三方依賴；
   - 確保 `make test` 全部通過。
3. **新增審查規則**：在 `linter.py`/`claim_parser.py` 中按編號段續編（C 系列=權要，L 系列=說明書），並在 README 規則表中登記。
4. 文件四種語言版本同步更新（至少保證簡中與英文）。

---

## ❓ 常見問題

**Q：它能取代專利代理人嗎？**
A：不能。PatentScribe 負責把交底材料結構化、把形式硬傷消滅在提交前，並輔助檢索方向；創造性高度、權利要求佈局策略仍需與專業代理人協作。

**Q：會上傳我的技術資料嗎？**
A：不會。程式沒有任何網路程式碼，全部計算在本機完成，可在內網/斷網環境稽核原始碼後使用。

**Q：為什麼不直接調用大模型生成交底書？**
A：機率式生成不可重現、可能「編造」技術細節，且資料需傳出內網。PatentScribe 的定位是**確定性的品質底座**；未來會提供可選的本機模型適配層，但預設永遠離線。

**Q：支援外觀設計專利嗎？**
A：v1.0 以發明/實用新型為主，外觀設計的專項規則在路線圖中（v1.1）。

---

## 📄 開源協議

本專案基於 **[MIT License](./LICENSE)** 開源，允許自由使用、修改、分發與商用，保留版權聲明即可。

> ⚠️ 本工具輸出的所有審查與比對意見僅為撰寫輔助，不構成法律意見；專利申請的授權前景請以國家知識產權局審查結論及專業代理意見為準。

<div align="center">

如果這個專案幫你省下了熬夜寫交底書的時間，歡迎點一顆 ⭐ 支持我們！

**Made with ❤️ by PatentScribe contributors**

</div>
