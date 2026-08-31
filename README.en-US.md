<div align="center">

# 🖋️ PatentScribe — Invention Disclosure & Patent Claims Toolkit

### Zero-dependency · Fully offline · Deterministic rule engine — turn raw engineering notes into a submission-ready patent disclosure

[简体中文](./README.md) ｜ [繁體中文](./README.zh-TW.md) ｜ **English** ｜ [日本語](./README.ja.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Zero Dependency](https://img.shields.io/badge/dependencies-zero-success.svg)](#-quick-start)
[![Tests](https://img.shields.io/badge/tests-52%20passed-brightgreen.svg)](#-testing)
[![Version](https://img.shields.io/badge/version-v1.0.0-orange.svg)](https://github.com/gitstq/PatentScribe/releases)

</div>

---

### ⬇️ Latest release: [**v1.0.0 (Release page)**](https://github.com/gitstq/PatentScribe/releases/tag/v1.0.0) — wheel / sdist assets with SHA256 checksums, fully offline install

---

## 🎉 Introduction

**PatentScribe** is a toolkit for **Chinese patent (CNIPA-style) invention disclosures**: it helps you structure a disclosure document (`技术交底书`), self-check claims against formal requirements, and export deliverables in multiple formats. It requires **no LLM, no network access, and no third-party packages** — it runs on the Python standard library alone, so every result is **deterministic, reproducible, and auditable**.

Engineers often design the solution and write the code themselves, only to get stuck when a patent filing is due: *Which points are actually inventive? How should claims be laid out? How do I produce a complete disclosure in one pass?* Existing tools are either LLM-bound "agent skills" (non-reproducible, and your technical notes must leave the intranet) or heavyweight commercial agency systems.

**PatentScribe automates everything that can be reduced to rules:**

- 🧭 **Mine candidate inventive points** from messy notes (problem → means → effect);
- 🧩 **Structure the disclosure** with one JSON skeleton so no section is forgotten;
- ⚖️ **Parse claims and build their dependency graph**, catching dangling references, illegal multi-dependency chains, forward references and more;
- 📋 Run **30+ formal-compliance rules** grounded in the Chinese *Patent Law*, its Implementing Regulations and the *Guidelines for Patent Examination*;
- 🔎 **Compare terminology overlap** with prior-art documents to guide novelty/inventiveness searches;
- 📄 Export **Markdown / self-contained HTML / editable Word (.docx)** in one command.

> 🌱 **Inspiration**: trending "Chinese patent agent skill" projects convinced us that lowering the barrier to patent writing is a real need — but we take a fundamentally different route: a **deterministic rule engine instead of probabilistic generation**, so sensitive material never leaves your network and every finding maps to an explicit rule ID. All code was written from scratch; no source code was copied.

---

## ✨ Features

### 🧠 Inventive-point mining (`mine`)
- Deterministic extraction with cue-phrase patterns and Chinese bigram features; classifies sentences into *prior-art problems / technical means / beneficial effects*;
- Assembles **problem→means→effect** triples as a candidate inventive-point list;
- Frequency-based keyword extraction with **identical output on every run and platform**.

### ⚖️ Claims self-check (`claims` / `lint`)
- Accepts `1.`, `1、`, `【1】`, `权利要求1.` numbering styles and expands reference ranges such as `1 to 3` or `1 or 2`;
- Detects **independent vs dependent claims**, extracts subject names and feature segments;
- Builds the full **dependency graph** with an ASCII tree and per-claim depth;
- Covers classic defects in Chinese patent practice:

| Rule | What it checks |
|---|---|
| C001 | Claims numbered consecutively from 1 — no gaps or duplicates |
| C002 | At least one independent claim exists |
| C003 | No dangling reference to a non-existent claim |
| C004 | Dependent claims may only reference earlier claims |
| C005 | Independent claims should use the standard two-part form ("characterized in that") |
| C006 | Exactly one trailing period per claim |
| C008 | A multiple-dependent claim must not refer to another multiple-dependent claim |
| C009 | No cycles in the reference graph |
| C010 | Category layout of method/apparatus/device/medium independent claims |

### 📋 Formal-compliance engine (`lint`, L1xx–L7xx)
- **Completeness**: errors on missing mandatory sections (L101);
- **Title rules**: length limit and promotional wording (L201/L202);
- **Abstract rules**: 300-character cap and marketing-language detection (L301/L302);
- **Wording quality**: flags vague/promotional terms such as "best", "about", "for example", "efficient" (L401);
- **Sufficiency of disclosure**: checks whether every independent-claim feature is supported in the detailed embodiments (L501);
- **Reference-numeral consistency**: numerals in claims must appear in the embodiments/drawings (L601/L602);
- Three severity levels (**error / warning / info**); errors produce a non-zero exit code for CI gating.

### 🔎 Prior-art overlap (`novelty`)
- Computes **Jaccard similarity** and **containment** over term sets;
- Reports high-frequency shared terms and a High / Medium / Low risk band;
- Explicitly states that lexical statistics are **not** a legal novelty/inventiveness conclusion.

### 📦 Multi-format export (`export`)
- **Markdown** for version control and review;
- **HTML** as a single self-contained file with inlined styles — no external requests;
- **DOCX** assembled directly as OOXML via the standard library, editable in Word / WPS / LibreOffice;
- Optionally embeds the check results so every export carries its audit trail.

### 🛡️ Engineering-grade quality
- **Zero third-party dependencies**, Python 3.9+ on every platform;
- **Fully offline** — not a single network call;
- **52 unit tests** covering parsing, linting, mining, comparison, export and CLI;
- Three usage modes: **CLI, Python library, `python -m`**.

---

## 🚀 Quick Start

### 📌 Requirements

| Item | Requirement |
|---|---|
| Python | **3.9 / 3.10 / 3.11 / 3.12** (3.10+ recommended) |
| OS | Windows / macOS / Linux |
| Third-party packages | **None** |
| Network | **Not required** (fully offline) |

### Option 1: pip install (recommended)

```bash
# Download the wheel from the Releases page and install locally — no PyPI access needed
pip install patentscribe-1.0.0-py3-none-any.whl

patentscribe --version
```

### Option 2: Run from source, no install

```bash
git clone https://github.com/gitstq/PatentScribe.git
cd PatentScribe
export PYTHONPATH=src        # Windows PowerShell: $env:PYTHONPATH="src"
python -m patentscribe --version
```

### Option 3: Editable install (for contributors)

```bash
pip install -e .
patentscribe --help
```

### ⚡ 30-second tour

```bash
# 1. Scaffold a disclosure template with guidance text
patentscribe init -o my_disclosure.json

# 2. Fill it in, then run formal checks and claims analysis
patentscribe lint -i my_disclosure.json

# 3. Inspect the claims dependency tree
patentscribe claims -i my_disclosure.json

# 4. Export Markdown / HTML / Word in one shot (with check results)
patentscribe export -i my_disclosure.json -f all -o dist --name disclosure --with-check
```

---

## 📖 User Guide

### 🧭 Command reference

| Command | Purpose | Key options |
|---|---|---|
| `init` | Scaffold a disclosure JSON template | `-o path`, `--type` |
| `mine` | Mine inventive points from notes | `-i notes.txt`, `--skeleton`, `--format json` |
| `lint` | Formal checks + claims analysis | `-i file.json`, `--json` |
| `claims` | Claim parsing & dependency tree | `-i file.json` |
| `novelty` | Overlap comparison vs prior art | `-i file.json -p prior1.txt prior2.txt` |
| `export` | Produce deliverables | `-f md/html/docx/all`, `-o dir`, `--with-check` |
| `report` | Full Markdown audit report | `-i file.json -o report.md` |

### 1️⃣ Start from raw notes: `mine`

Save meeting minutes or design fragments as plain text:

```bash
python -m patentscribe mine -i examples/example_notes.txt
```

```text
=== Candidate inventive points (problem → means → effect) ===
[IP01] Means: a dynamic-weight scheduler
      Solves: static weighted round-robin causes hot-node queuing ...
      Benefit: average latency reduced by ~40% ...
=== Keywords ===
node, weight, load, response, latency, control, traffic, burst, window, request
```

Add `--skeleton -o skeleton.json` to produce a disclosure skeleton you can continue editing.

### 2️⃣ Disclosure schema

| Field | Meaning | Required |
|---|---|---|
| `title` | Title (recommended ≤25 Chinese chars) | ✅ |
| `patent_type` | 发明 (invention) / 实用新型 (utility model) / 外观设计 (design) | ✅ |
| `field` | Technical field | ✅ |
| `background` | Background art | ✅ |
| `problems` | List of prior-art problems | recommended |
| `solution` | Technical solution / summary of invention | ✅ |
| `effects` | Beneficial effects | recommended |
| `embodiments` | Detailed embodiments (must support independent claims) | ✅ |
| `drawings` | Drawing descriptions (figure, description, numerals) | when drawings exist |
| `abstract` | Abstract (≤300 chars) | ✅ |
| `claims_text` | Raw claims text | ✅ |
| `keywords` | Core keywords | recommended |

See [`examples/example_disclosure.json`](./examples/example_disclosure.json) for a complete worked example.

### 3️⃣ Claims self-check: `claims`

```bash
python -m patentscribe claims -i examples/example_disclosure.json
```

```text
├─ 1 [independent] A dynamic-weight request scheduling method
│  ├─ 2 [dependent] The method of claim 1 ...
│  │  └─ 4 [dependent] The method of any one of claims 1 to 3 ...
│  │     └─ 5 [dependent] The method of claim 4 ...
```

### 4️⃣ Prior-art comparison: `novelty`

```bash
python -m patentscribe novelty \
  -i examples/example_disclosure.json \
  -p examples/example_prior_art.txt
```

### 5️⃣ Embed as a Python library

```python
from patentscribe import load_disclosure, lint_disclosure, to_docx

disclosure = load_disclosure("my_disclosure.json")
report = lint_disclosure(disclosure)

print("PASS" if report.passed else "FAIL")
for issue in report.issues:
    print(issue.code, issue.location, issue.message)

to_docx(disclosure, "dist/disclosure.docx")
```

### 6️⃣ CI gating

`lint` exits with code `1` when **error-level** problems exist:

```bash
patentscribe lint -i disclosure.json --json > check.json || exit 1
```

### 🖥️ Demo assets

> Terminal recordings and exported samples will be added under `docs/` in follow-up releases. Run `make demo` today to reproduce every example command and artifact.

---

## 💡 Design Notes & Roadmap

### 🧱 Why a rule engine instead of an LLM?

1. **Reproducible** — the same input always yields the same verdict;
2. **Auditable** — every finding has a rule ID (C0xx/Lxxx) traceable to examination guidance;
3. **Confidential by design** — disclosures are crown-jewel material; an offline engine keeps them inside the intranet;
4. **Maintenance-free** — no online services, API keys or third-party packages; it will still run a decade from now.

### 🧩 Technology choices

| Layer | Choice | Rationale |
|---|---|---|
| Language | Python 3.9+ | Readable by engineers and patent staff; stdlib covers everything |
| Parsing | Regex + finite-state splitting | Claim numbering/reference patterns are well defined — rules beat models here |
| Chinese NLP | Custom bigram features + stoplist | Avoids heavy deps like jieba; stays deterministic |
| DOCX | OOXML assembled via `zipfile` | Editable Word files without python-docx |
| Packaging | Custom zero-dep build script | Standard wheel/sdist without build/setuptools |

### 🗺️ Roadmap

- [x] v1.0.0: templates, inventive-point mining, claim dependency analysis, 30+ rules, three export formats, prior-art comparison
- [ ] v1.1: design-patent rules (view drawings, six-view checklist)
- [ ] v1.2: claim **revision comparison** (before/after diff with amendment basis)
- [ ] v1.3: batch mode for a directory of disclosures with a summary report
- [ ] v2.0: optional local-model adapter (offline by default forever)

### 🙋 How to contribute

New rules, bilingual term tables, real-world examples and terminal recordings are all welcome — see the contributing guide.

---

## 📦 Build & Distribution

PatentScribe is a **library / CLI project** (pure Python, cross-platform); no native executables are needed.

### Build the distributions

```bash
# Option A: zero-dependency stdlib builder (no build tooling required)
python scripts/build.py
# Produces:
#   dist/patentscribe-1.0.0-py3-none-any.whl
#   dist/patentscribe-1.0.0.tar.gz

# Option B: standard PEP 517 build
pip install build && python -m build
```

### Install & distribute

```bash
pip install dist/patentscribe-1.0.0-py3-none-any.whl
pipx install ./dist/patentscribe-1.0.0-py3-none-any.whl
```

### Compatibility

- CPython 3.9–3.12 on Windows / macOS / Linux;
- Wheel tagged `py3-none-any` — **no platform-specific binaries**;
- DOCX output verified with a standard XML parser and Word/WPS;
- Air-gapped intranets can copy the wheel and install without PyPI access.

---

## 🧪 Testing

```bash
make test
# equivalent to:
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Reproduce the full worked example:

```bash
make demo
```

---

## 🤝 Contributing

Contributions of all kinds are welcome:

1. **Issues**: attach a (redacted) input snippet, the command run, and actual output; for false positives/negatives, cite the rule ID.
2. **Pull requests**:
   - Commit messages follow the **Angular convention**: `feat:` / `fix:` / `docs:` / `refactor:` / `test:` / `chore:`;
   - Every new rule needs unit tests and must not add third-party dependencies;
   - Make sure `make test` stays green.
3. **New rules**: extend `linter.py` / `claim_parser.py` using the existing numbering scheme (C-series = claims, L-series = specification) and register them in the rule tables.
4. Keep the multilingual docs in sync (at minimum Chinese and English).

---

## ❓ FAQ

**Does it replace a patent attorney?**
No. It structures your material and eliminates formal defects before submission; inventiveness and claim strategy still require a qualified attorney.

**Will my technical material be uploaded anywhere?**
Never. The program contains no networking code at all; everything runs locally, and you can audit the source for use on air-gapped networks.

**Why not use an LLM to generate the disclosure?**
Probabilistic generation is non-reproducible, can hallucinate technical details, and requires sending notes off-site. PatentScribe is a **deterministic quality baseline**. An optional local-model layer may come later; the default will always stay offline.

**Are design patents supported?**
v1.0 focuses on inventions and utility models; design-patent-specific rules are on the v1.1 roadmap.

---

## 📄 License

Released under the **[MIT License](./LICENSE)** — free to use, modify, distribute and commercialize, with the copyright notice retained.

> ⚠️ All check and comparison output is writing assistance only, not legal advice. Patentability is determined by the CNIPA examination and qualified professional counsel.

<div align="center">

If PatentScribe saved you a late night, consider leaving a ⭐!

**Made with ❤️ by PatentScribe contributors**

</div>
