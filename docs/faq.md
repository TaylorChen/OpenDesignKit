---
layout: default
title: FAQ
nav_order: 4
permalink: /faq.html
---

# 常见问题

### 和 Claude Design / Claude Slides 什么关系？
三个 Skill 源自 [JimLiu/baocut](https://github.com/JimLiu/baocut) commit `7aa049e8` 的内置 Skill，经通用化改造（去除宿主专有依赖）。`skills/` 部分遵循 BaoCut Community License，其余为 MIT。本仓库与 Anthropic 无隶属关系。

### 需要装什么环境？
纯 Python 3 标准库（`odk` CLI），浏览器看产物。无 Node、无数据库、无服务端。

### 产物能在 PowerPoint 里打开吗？
幻灯片是 HTML 不是 PPTX。需要 PPT 交付时用 `odk export-pdf` 导出 16:9 PDF（任何 Office 软件可插入）。

### dc-import 子组件在本地双击打不开？
`file://` 下浏览器禁止 fetch。用 `odk serve my-canvas` 起本地服务（http://127.0.0.1:8620）即可。

### support.js 是什么？会跟宿主编辑器冲突吗？
它是独立实现的轻量预览运行时，让没有专有编辑器的环境也能渲染/交互画板。`<script src="./support.js">` 是格式标准钩子：若宿主有自己的运行时会优先使用宿主的。

### 校验通过了但看起来不好看？
`odk check` 管"格式合法与完整性"；美学靠 skill 的设计规范（排版/对比/层级）。两者互补：先 0 错误，再谈好看。

### 商业使用受限吗？
`skills/` 目录（BCL）允许非商业使用与免费分享；商业化（含托管该 Skill 的服务）需上游书面许可。`tools/`、`odk/`、`examples/`（MIT）无此限制。详见 [NOTICE](https://github.com/TaylorChen/OpenDesignKit/blob/main/NOTICE.md)。
