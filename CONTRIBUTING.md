# 贡献指南 / Contributing to PatentScribe

感谢你对 PatentScribe 的兴趣！本项目坚持**零第三方依赖、完全离线、结果确定可复现**，贡献时请共同维护这三条底线。

## 🐛 提交 Issue

- 规则误报 / 漏报：请标注规则编号（如 `C008` / `L401`），并附上**可脱敏的输入片段**、执行命令与实际输出；
- 缺陷报告：注明 Python 版本、操作系统、PatentScribe 版本（`patentscribe --version`）；
- 功能建议：描述使用场景与期望输出，最好附一份示例输入。

## 🔀 提交 Pull Request

1. Fork 仓库并从 `main` 切出特性分支：`feat/xxx`、`fix/xxx`、`docs/xxx`；
2. 提交信息遵循 **Angular Convention**：
   - `feat: 新增……`
   - `fix: 修复……`
   - `docs: 文档……`
   - `refactor: 重构……`
   - `test: 测试……`
   - `chore: 工程杂项……`
3. **不允许引入任何第三方运行时依赖**（标准库之外的 import 需要在 PR 中说明必要性，原则上不接受）；
4. 新功能必须配套单元测试，保证 `make test` 全部通过；
5. 如新增审查规则：
   - 权利要求规则使用 `Cxxx` 编号段，说明书规则使用 `Lxxx` 编号段；
   - 在 README（至少简中与英文）的规则表中登记；
   - 给出规则依据（专利法/实施细则/审查指南的对应口径）。

## 🧪 本地验证清单

```bash
make test          # 全部单元测试通过
python scripts/build.py   # 能正常产出 wheel 与 sdist
make demo          # 示例全流程可复现
```

## 🌐 多语言文档

- `README.md` 为简体中文主文档；`README.en-US.md`（英文）、`README.zh-TW.md`（繁中）、`README.ja.md`（日文）为译本；
- 修改文档结构时，四种语言保持同步（至少保证简中与英文同时更新）；
- 翻译追求母语表达，禁止机翻式生硬直译。

## 📏 代码风格

- 兼容 Python 3.9 语法（避免 3.10+ 独占语法在运行路径上的使用，类型注解可用 `from __future__ import annotations`）；
- 公共函数与类写清晰 docstring，复杂规则注明依据；
- 确定性优先：相同输入必须得到相同输出，禁止依赖随机数、网络与本地时区敏感逻辑。

再次感谢你的贡献！
