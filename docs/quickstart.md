---
layout: default
title: 60 秒上手
nav_order: 2
parent: 指南
permalink: /quickstart.html
---

# 60 秒上手

## 0. 安装（一次性）

```bash
git clone https://github.com/TaylorChen/OpenDesignKit.git
cd OpenDesignKit && pipx install .
```

## 1. 生成第一份幻灯片（30 秒）

```bash
odk init deck my-deck
```

得到：`deck.json`（索引）+ `slides/cover.html`（封面页）+ `player.html`（放映器）。

## 2. 让 Agent 写内容

把 `skills/open-slides/` 放进你的 Agent 宿主（如 `~/.claude/skills/`），然后对它说：

> 按 open-slides 规范，把 my-deck 写成一份 5 页的产品发布 deck

Agent 的工作流是固定的：**写文件 → `odk check` 到 0 错误 → 交付**。

## 3. 自己看效果

```bash
odk build player my-deck      # 讲稿变化后刷新放映器
open my-deck/player.html      # ← → 翻页，S 讲稿，O 目录
```

## 设计稿（可交互画板）

```bash
odk init canvas my-canvas
open my-canvas/Main.dc.html   # support.js 让浏览器直接渲染 + 交互
odk serve my-canvas           # 需要用 dc-import 子组件时启动本地服务
```

## 设计系统

```bash
odk init system my-brand      # tokens.json + 品牌手册 + tokens.css
odk build tokens my-brand     # tokens 变更后重新编译
```

## 下一步

- 三个格式的[格式规范](spec/open-slides.html)
- 常见问题看 [FAQ](faq.html)
- 出问题先跑 `odk check`——它告诉你哪里不对、怎么修
