<div align="center">

# 🖋️ PatentScribe · 発明開示書作成＆クレーム自己点検ツールキット

### 依存ゼロ · 完全オフライン · 決定論的ルールエンジン —— 研究開発者が、質の高い技術開示書を自分で仕上げるために

[简体中文](./README.md) ｜ [繁體中文](./README.zh-TW.md) ｜ [English](./README.en-US.md) ｜ **日本語**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Zero Dependency](https://img.shields.io/badge/dependencies-zero-success.svg)](#-クイックスタート)
[![Tests](https://img.shields.io/badge/tests-52%20passed-brightgreen.svg)](#-テスト)
[![Version](https://img.shields.io/badge/version-v1.0.0-orange.svg)](https://github.com/gitstq/PatentScribe/releases)

</div>

---

## 🎉 プロジェクト紹介

**PatentScribe** は、中国（CNIPA）の特許出願プロセスにおける**技術交底書（発明開示書）の構造化作成、請求項（権利要求）の自己点検、複数形式での出力**を行うツールキットです。LLM 不要・ネットワーク不要・サードパーティ製パッケージ不要。Python 標準ライブラリだけで動作し、結果は常に**決定的で、再現可能で、監査可能**です。

研究開発者なら誰もが経験する困りごと——「自分で設計し自分で実装したのに、発明のポイントの洗い出しや請求項の構成、開示書の仕上げでつまずく」。既存ツールは LLM 依存の「エージェントスキル」（結果が再現できない、機密資料を社外に出す必要がある）か、重厚な商用システムばかりです。

**PatentScribe は、ルール化できる工程をすべて自動化します：**

- 🧭 荒い技術メモから**発明ポイント候補を抽出**（課題 → 手段 → 効果）;
- 🧩 ひとつの JSON 雛形で開示書を**構造化**し、章の抜けを防止;
- ⚖️ 請求項を自動解析して**従属関係ツリーを構築**し、宙ぶらりん参照・多重従属の連鎖・後方参照などの欠陥を検出;
- 📋 中国特許法・実施細則・審査指南に基づく **30 以上の形式審査ルール**;
- 🔎 先行技術文献との**用語重複度を比較**し、新規性・進歩性の調査方向を支援;
- 📄 **Markdown / 自己完結 HTML / 編集可能な Word（.docx）** をワンコマンドで出力。

> 🌱 **着想**: GitHub Trending で話題になった「中国特許エージェントスキル」から、特許作成の敷居を下げるという課題設定に共感しました。ただし技術路線は根本的に異なります——**確率的な生成ではなく決定論的ルールエンジン**を選び、機密資料を社外に出さず、すべての指摘に明示的なルール番号を付与します。ソースコードはすべて独自実装であり、他プロジェクトのコードは一切コピーしていません。

---

## ✨ 主な機能

### 🧠 発明ポイント抽出（`mine`）
- **文パターン + 中国語バイグラム特徴**による決定論的抽出。「先行技術の課題 / 技術的手段 / 有益な効果」を自動分類;
- **課題→手段→効果**の三つ組を発明ポイント候補として整理;
- 頻度ベースのキーワード抽出。実行環境・プラットフォームによらず**結果は完全に同一**。

### ⚖️ 請求項の自己点検（`claims` / `lint`）
- `1.`、`1、`、`【1】`、`権利要求1.` など多様な番号表記に対応。`1〜3`、`1または2` の**参照範囲を自動展開**;
- **独立請求項 / 従属請求項**を判定し、主題名称と特徴断片を抽出;
- 完全な**従属グラフ**を構築し、ASCII ツリーと参照深度を出力;
- 中国特許実務の代表的欠陥をカバー:

| ルール | 点検内容 |
|---|---|
| C001 | 番号は 1 から連番であること（欠番・重番なし） |
| C002 | 独立請求項が少なくとも 1 項あること |
| C003 | 存在しない請求項への宙ぶらりん参照の禁止 |
| C004 | 従属項は先行する請求項のみ参照可能（後方参照禁止） |
| C005 | 独立項は「その特徴は〜にある」二区分形式が望ましい |
| C006 | 1 請求項の終端にピリオドは 1 つだけ |
| C008 | **多重従属項が別の多重従属項を従属先にできない**（中国実務） |
| C009 | 参照グラフに循環がないこと |
| C010 | 方法/装置/デバイス/媒体の独立項カテゴリ構成の通知 |

### 📋 形式審査エンジン（`lint`、L1xx〜L7xx）
- **完全性**: 必須章の欠落をエラー表示（L101）;
- **名称ルール**: 文字数上限・宣伝的表現（L201/L202）;
- **要約ルール**: 300 字上限・宣伝文の検出（L301/L302）;
- **用語品質**: 「最良・約・例えば・高効率」など曖昧/宣伝的語を指摘（L401）;
- **サポート要件**: 独立項の各特徴が実施形態に裏付けられているか（L501）;
- **図面符号の整合性**: 請求項中の符号が実施形態/図面説明に現れるか（L601/L602）;
- 3 段階の重要度（**エラー / 警告 / 情報**）。エラー時は非ゼロ終了コードで CI ゲートに利用可能。

### 🔎 先行技術との重複度（`novelty`）
- 用語集合から **Jaccard 類似度**と**包含度（containment）**を算出;
- 高頻度共通用語と「高/中/低」リスク帯を出力し、差別化と調査の方向性を支援;
- 語彙統計は新規性・進歩性に関する**法的結論ではない**旨を明記。

### 📦 複数形式の出力（`export`）
- **Markdown**: バージョン管理・レビュー向け;
- **HTML**: 単一ファイル・スタイル内蔵・外部リンクなし。ブラウザですぐ閲覧;
- **DOCX**: 標準ライブラリで OOXML を直接組み立て。Word/WPS/LibreOffice で編集可能;
- 点検結果を成果物に埋め込み、提出物に監査証跡を残すことも可能。

### 🛡️ エンジニアリング品質
- **サードパーティ依存ゼロ**、Python 3.9+ で全 OS 対応;
- **完全オフライン**——ネットワーク呼び出しは一切なし;
- 解析・点検・抽出・比較・出力・CLI をカバーする **52 のユニットテスト**;
- **CLI / Python ライブラリ / `python -m`** の 3 通りで利用可能。

---

## 🚀 クイックスタート

### 📌 動作要件

| 項目 | 要件 |
|---|---|
| Python | **3.9 / 3.10 / 3.11 / 3.12**（3.10 以上推奨） |
| OS | Windows / macOS / Linux |
| サードパーティ | **なし** |
| ネットワーク | **不要**（完全オフライン） |

### 方法 1: pip インストール（推奨）

```bash
# Releases ページから wheel をダウンロードしてローカルインストール（PyPI アクセス不要）
pip install patentscribe-1.0.0-py3-none-any.whl

patentscribe --version
```

### 方法 2: ソースからインストール不要で実行

```bash
git clone https://github.com/gitstq/PatentScribe.git
cd PatentScribe
export PYTHONPATH=src        # Windows PowerShell: $env:PYTHONPATH="src"
python -m patentscribe --version
```

### 方法 3: 開発者向け編集可能インストール

```bash
pip install -e .
patentscribe --help
```

### ⚡ 30 秒ツアー

```bash
# 1. 記入ガイド付きの雛形を生成
patentscribe init -o my_disclosure.json

# 2. JSON を記入したら形式点検と請求項解析を実行
patentscribe lint -i my_disclosure.json

# 3. 請求項の従属ツリーを確認
patentscribe claims -i my_disclosure.json

# 4. Markdown / HTML / Word を一括出力（点検結果込み）
patentscribe export -i my_disclosure.json -f all -o dist --name disclosure --with-check
```

---

## 📖 詳細な使い方

### 🧭 コマンド一覧

| サブコマンド | 役割 | 主なオプション |
|---|---|---|
| `init` | 開示書 JSON 雛形の生成 | `-o 出力先`, `--type` |
| `mine` | メモから発明ポイントを抽出 | `-i notes.txt`, `--skeleton`, `--format json` |
| `lint` | 形式点検＋請求項解析 | `-i file.json`, `--json` |
| `claims` | 請求項解析と従属ツリー | `-i file.json` |
| `novelty` | 先行文献との重複度比較 | `-i file.json -p prior1.txt prior2.txt` |
| `export` | 成果物の出力 | `-f md/html/docx/all`, `-o dir`, `--with-check` |
| `report` | 完全な Markdown 点検レポート | `-i file.json -o report.md` |

### 1️⃣ 荒いメモから始める: `mine`

議事録や設計メモをプレーンテキストで保存してください。

```bash
python -m patentscribe mine -i examples/example_notes.txt
```

`--skeleton -o skeleton.json` を付けると、そのまま編集を続けられる開示書の雛形が生成されます。完全な記入例は [`examples/example_disclosure.json`](./examples/example_disclosure.json) を参照してください。

### 2️⃣ 開示書フィールド

| フィールド | 意味 | 必須 |
|---|---|---|
| `title` | 発明名称（25 字以内推奨） | ✅ |
| `patent_type` | 発明 / 実用新型 / 意匠 | ✅ |
| `field` | 技術分野 | ✅ |
| `background` | 背景技術 | ✅ |
| `problems` | 先行技術の課題リスト | 推奨 |
| `solution` | 技術方案（発明内容） | ✅ |
| `effects` | 有益な効果 | 推奨 |
| `embodiments` | 具体的実施形態（独立項を裏付ける） | ✅ |
| `drawings` | 図面説明（図番号・説明・符号） | 図面がある場合 |
| `abstract` | 要約（300 字以内） | ✅ |
| `claims_text` | 請求項の原文 | ✅ |
| `keywords` | コアキーワード | 推奨 |

### 3️⃣ 請求項の自己点検: `claims`

```bash
python -m patentscribe claims -i examples/example_disclosure.json
```

独立項・従属項ごとの ASCII ツリー、参照深度、問題リストが出力されます。

### 4️⃣ 先行文献との比較: `novelty`

```bash
python -m patentscribe novelty \
  -i examples/example_disclosure.json \
  -p examples/example_prior_art.txt
```

### 5️⃣ Python ライブラリとして組み込む

```python
from patentscribe import load_disclosure, lint_disclosure, to_docx

disclosure = load_disclosure("my_disclosure.json")
report = lint_disclosure(disclosure)

print("PASS" if report.passed else "FAIL")
for issue in report.issues:
    print(issue.code, issue.location, issue.message)

to_docx(disclosure, "dist/disclosure.docx")
```

### 6️⃣ CI への組み込み

`lint` は**エラーレベル**の問題があると終了コード `1` を返します。

```bash
patentscribe lint -i disclosure.json --json > check.json || exit 1
```

### 🖥️ デモ素材

> ターミナル録画と出力サンプルは今後のリリースで `docs/` に追加予定です。現時点では `make demo` を実行すれば、すべての例示コマンドと成果物を再現できます。

---

## 💡 設計思想とロードマップ

### 🧱 なぜ LLM ではなくルールエンジンか？

1. **再現可能**: 同じ入力は常に同じ結論。レビューと回帰テストが容易;
2. **監査可能**: すべての指摘にルール番号（C0xx/Lxxx）があり、審査指南へ遡及可能;
3. **機密保持**: 開示書は最重要機密。オフライン専用なので社内ネットワークから出ない;
4. **保守ゼロ**: オンラインサービス・API キー・サードパーティ不要。10 年後でも動作。

### 🧩 技術選定

| 層 | 選定 | 理由 |
|---|---|---|
| 言語 | Python 3.9+ | 開発者・特許担当者双方に読みやすく、標準ライブラリで全要件を充足 |
| 解析 | 正規表現＋有限状態分割 | 請求項の番号/参照パターンは明確で、モデルよりルールが堅実 |
| 中国語処理 | 自作バイグラム特徴＋ストップリスト | jieba 等の重い依存を排し、決定性を維持 |
| DOCX | `zipfile` による OOXML 組み立て | python-docx 不要で編集可能な Word を生成 |
| パッケージ | 自作の依存ゼロビルドスクリプト | build/setuptools なしで標準 wheel/sdist を生成 |

### 🗺️ ロードマップ

- [x] v1.0.0: 雛形、発明ポイント抽出、従属関係解析、30+ ルール、3 形式出力、先行文献比較
- [ ] v1.1: 意匠特許専用ルール（図面説明・六面図チェックリスト）
- [ ] v1.2: 請求項**補正対照**（新旧差分と補正根拠の生成）
- [ ] v1.3: バッチモード（フォルダ内の複数開示書を一括点検・集計）
- [ ] v2.0: オプションのローカルモデル適応層（既定は永遠にオフライン）

### 🙋 貢献できる領域

点検ルールの追加、二言語用語表の充実、実例の追加、ターミナル録画の提供などを歓迎します。貢献ガイドをご覧ください。

---

## 📦 ビルドと配布

PatentScribe は**ライブラリ / CLI プロジェクト**（純 Python・クロスプラットフォーム）であり、ネイティブ実行ファイルは不要です。

### 配布物のビルド

```bash
# 方法 A: 依存ゼロの標準ライブラリビルダー（ビルドツール不要）
python scripts/build.py
# 生成物:
#   dist/patentscribe-1.0.0-py3-none-any.whl
#   dist/patentscribe-1.0.0.tar.gz

# 方法 B: 標準 PEP 517 ビルド
pip install build && python -m build
```

### インストールと配布

```bash
pip install dist/patentscribe-1.0.0-py3-none-any.whl
pipx install ./dist/patentscribe-1.0.0-py3-none-any.whl
```

### 互換性

- CPython 3.9〜3.12、Windows / macOS / Linux;
- wheel は `py3-none-any` タグで**プラットフォーム固有バイナリなし**;
- DOCX は標準 XML パーサと Word/WPS で検証済み;
- 隔離ネットワークでも wheel をコピーするだけでインストール可能（PyPI 不要）。

---

## 🧪 テスト

```bash
make test
# 同等:
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

完全な例示フローの再現:

```bash
make demo
```

---

## 🤝 コントリビューション

あらゆる貢献を歓迎します:

1. **Issue**: （匿名化した）入力断片・実行コマンド・実際の出力を添付してください。誤検知/見逃しにはルール番号を明記。
2. **Pull Request**:
   - コミットメッセージは **Angular 規約**に準拠: `feat:` / `fix:` / `docs:` / `refactor:` / `test:` / `chore:`;
   - 新ルールにはユニットテストが必須。サードパーティ依存の追加は不可;
   - `make test` が全て通ることを確認。
3. **新ルール**: `linter.py` / `claim_parser.py` に既存の採番（C 系=請求項、L 系=明細書）で追加し、README のルール表に登録。
4. 多言語ドキュメントの同期（最低限 中国語・英語）。

---

## ❓ FAQ

**特許弁理士の代わりになりますか？**
いいえ。PatentScribe は資料を構造化し提出前に形式欠陥を除去し、調査方向を支援するものです。進歩性の評価や請求項戦略は資格のある弁理士との協働が必要です。

**技術資料が外部に送信されることは？**
一切ありません。ネットワークコードは存在せず、すべてローカルで完結します。隔離環境ではソース監査のうえご利用ください。

**なぜ LLM で開示書を生成しないのですか？**
確率的生成は再現不能で技術詳細を「幻覚」する恐れがあり、資料の社外持ち出しも必要です。PatentScribe は**決定論的な品質基盤**です。将来オプションとしてローカルモデル層を検討しますが、既定は永遠にオフラインです。

**意匠特許には対応しますか？**
v1.0 は発明・実用新型中心です。意匠専用ルールは v1.1 で予定しています。

---

## 📄 ライセンス

**[MIT License](./LICENSE)** のもとで公開。著作権表示を残す限り、利用・改変・再配布・商用利用が自由に行えます。

> ⚠️ 本ツールの点検・比較結果は作成支援のみを目的とし、法的助言ではありません。特許性の最終判断は CNIPA の審査結論および専門的な代理意見に従ってください。

<div align="center">

PatentScribe が深夜の作業を減らせたなら、ぜひ ⭐ をお願いします！

**Made with ❤️ by PatentScribe contributors**

</div>
