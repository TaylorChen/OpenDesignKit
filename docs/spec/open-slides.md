---
layout: default
title: 幻灯片格式规范
nav_order: 3
parent: 格式规范
permalink: /spec/open-slides.html
---

# 幻灯片格式规范（open-slides）

一份 deck 是工作目录里的一个目录：`deck.json` 索引 + `slides/<id>.html` 每页一个文件。产物是纯本地文件，任何现代浏览器可直接渲染。

## 文件形状

```
my-deck/
├── deck.json          # 索引：标题、页序、章节、封面、字体
├── slides/
│   ├── cover.html     # 每页一个完整 HTML
│   └── ...
├── assets/            # 本地图片，相对路径引用
└── player.html        # odk build player 生成（放映器）
```

## deck.json 关键字段

| 字段 | 必填 | 说明 |
|---|---|---|
| `v` | 是 | 固定 `4` |
| `title` | 是 | 放映器标题栏使用 |
| `order` | 是 | 页面 ID 数组，放映顺序；每个 ID 对应 `slides/<id>.html` |
| `cover` | 建议 | 封面页 ID（必须在 order 中）；播放器从这里开始 |
| `sections` | 否 | 章节导航 `{id: {description, start}}`，start 必须在 order 中 |
| `faces` | 建议 | 字体 `{key: {family, href}}`，建议 Google Fonts 并钉版本 |
| `designSystems` | 否 | 引用的设计系统 |

## 每页 HTML 的硬性规则

- 根元素是**一个** `<section id="<页id>">`，id 必须与文件名一致
- 尺寸固定 **1920×1080**，全内联样式（无外部 CSS）
- 只用 `h1–h3`、`p`、`div/span`（布局）与行内样式；**禁止** `script/style/html/body/iframe` 等标签
- **`<aside>` 写演讲备注**（放映器按 S 键显示）
- `data-transition` 可选（如 `fade`）
- 图片：本地相对路径（`assets/photo.png`）；不用网络临时链接

## 校验

```bash
odk check my-deck            # 自动识别；0 错误 0 警告才交付
```

覆盖：deck.json 结构与引用完整性、order 孤儿文件、页面尺寸、备注存在性、禁用标签、faces 形状。

## 交付

```bash
odk build player my-deck     # 生成/刷新 player.html（含最新讲稿）
```
