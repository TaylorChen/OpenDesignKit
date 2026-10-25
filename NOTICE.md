# NOTICE — 第三方材料与许可归属

本仓库包含源自 [JimLiu/baocut](https://github.com/JimLiu/baocut) commit
[`7aa049e8`](https://github.com/JimLiu/baocut/commit/7aa049e8) 的改编材料。

## 许可证分区

| 路径 | 许可证 | 说明 |
|---|---|---|
| `skills/**` | **BaoCut Community License v1.0**（完整文本见 [`licenses/baocut-community-license.txt`](licenses/baocut-community-license.txt)） | 改编自上游 `skills/baocut/built-in-skills/{design,design-system,slides}`，属上游许可证定义的 Software 修改版。依据其 §2 以非商业目的免费共享本修改版，并按 §5 要求标注修改与出处。**不得移除或替换该许可证对这部分材料的条件。** |
| `odk/**`（含 `odk/templates/`）、`tools/**`、`examples/**`（含 `support.js` 预览运行时）、`README.md`、`NOTICE.md` | **MIT**（见 [`LICENSE`](LICENSE)） | 本项目独立编写/创作（validator、odk CLI 与 support.js 为基于公开文件格式规范的独立实现，不含上游代码；examples 属于用上述 Skill 产出的 Content）。 |

## 修改声明（上游许可证 §5）

`skills/` 内的全部文件均为**修改版**：相对上游 commit `7aa049e8`，本项目做了通用化改造——
移除 BaoCut 宿主专有工具引用（`skills_read`、`design_import_asset`、`slides_import_asset`、
`design_check` 等专有工具名改为通用描述或可选适配）、重命名 skill、
调整产物查看/校验说明以面向任意 Agent 宿主，并补充独立编写的校验器与示例。
它们**不是** BaoCut 官方发布物，亦与其无关联。

## 与 Anthropic 的关系

本仓库与 Anthropic 无隶属或背书关系。（若项目沿用含 "Claude" 的名称，
此声明用于澄清无关联；项目名称本身不构成对任何商标的权利主张。）

## 商业化

对 `skills/` 部分的商业性分发、收费打包或商业托管，需上游权利人
（Jim Liu, junminliu@gmail.com）的书面许可。本项目的非商业开源分发不受影响。
