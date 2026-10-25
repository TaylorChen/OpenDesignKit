---
layout: default
title: OpenDesignKit
nav_order: 1
permalink: /
---

# OpenDesignKit

> 面向全 Agent 的工业级设计套件 —— 设计稿 / 幻灯片 / 设计系统，纯文件格式，任何 AI Agent 都能产出。

{: .fs-6 .fw-300 }
源自 [JimLiu/baocut@7aa049e8](https://github.com/JimLiu/baocut/commit/7aa049e8)，通用化改造，MIT + BCL 双许可。

**[快速上手](quickstart.html){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }**
**[在线画廊](gallery.html){: .btn .fs-5 .mb-4 .mb-md-0 }**

## 它长什么样

**幻灯片放映器**（← → 翻页 · S 讲稿 · O 目录 · F 全屏）：

![幻灯片播放器]({{ site.baseurl }}/screenshots/player-demo.gif)

**可交互画板**（support.js 预览运行时；点击色板实时切换主题色）：

![可交互画板]({{ site.baseurl }}/screenshots/board-interactive.gif)

## 三个 Skill

| Skill | 产物格式 | 用途 |
|---|---|---|
| [open-design](spec/open-design.html) | `canvas.json` + `.dc.html` 画板 | 界面 / 海报 / 信息图 / 原型（支持交互） |
| [open-slides](spec/open-slides.html) | `deck.json` + 每页一个 HTML | 幻灯片 / 演示 / 讲稿 |
| [open-design-system](spec/open-design-system.html) | `design-system.json` + `tokens.json` | 品牌 tokens 单一事实源 |

## 安装

```bash
git clone https://github.com/TaylorChen/OpenDesignKit.git
cd OpenDesignKit && pipx install .
odk --version
```

无需安装也可以：克隆后直接 `python3 tools/validator.py ...`（同一引擎，零依赖）。

## 工具链

```bash
odk check my-deck --json      # 校验（自动识别格式，可机器读）
odk init deck my-deck         # 脚手架（开箱即过校验）
odk build player my-deck      # 生成放映器
odk serve my-canvas           # 本地预览（启用 dc-import）
odk export-pdf my-deck        # 每页 16:9 PDF
```
