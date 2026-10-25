---
layout: default
title: Dogfood 验证记录
nav_order: 5
permalink: /dogfood.html
---

# Dogfood 验证记录

> 方法：把 OpenDesignKit 当作陌生用户的工具，完成三个真实任务，全程记录发现的问题。
> 每个发现当场修复并补充回归测试。这就是本项目的"轻量自证"。

## 测试 A：幻灯片——5 页产品介绍 deck

**任务**：init deck → 按 open-slides 规范写 5 页（封面/痛点/方案/工作流/CTA）→ check → build player → 全页截图走查。

**结果**：✅ 校验一次通过（0 错 0 警），放映器 5 页 + 5 段讲稿全部正常。

**发现并修复**：
- 🐛 **放映器不缩放**：`#frame` 是 flex 子项，`flex-shrink:1` 把 1920px 宽压缩到视口宽（高度不受影响）→ 水平永远裁切。
  修复：`flex: none` + 按视口 `min(w/1920, h/1080)` 等比缩放并居中；初始与讲稿面板切换时都重算。3 轮截图回归确认。

## 测试 B：交互画板——定价卡片组

**任务**：init system（tokens 消费源）→ 写 Pricing.dc.html（sc-for 三档方案、sc-if 徽章、月付/年付 onClick 切换、helmet 引用 tokens.css）+ Testimonial.dc.html 子组件（dc-import）→ check → serve → 两种状态截图对比。

**结果**：✅ 校验 0/0；tokens.css 变量生效（accent/边框/背景）；sc-if 徽章、高亮边框、dc-import 子组件全部就位；点击"月付"后价格 39/159→49/199、高亮迁移、计费后缀消失——**状态→重渲染→事件闭环完整**。

**发现并修复**：
- 🐛 **`python3 odk/cli.py serve` 直接执行崩溃**：cli 使用相对导入（`from . import core`），脱离包上下文即失败。
  修复：双模式导入（直接执行时自举 sys.path）+ 新增 `odk/__main__.py`，`python3 -m odk` 与直接执行均可用。
- ⚠ **体验洞察**：画板引用兄弟目录的 `tokens.css` 时，`odk serve` 必须服务**公共父目录**而非画板目录（否则相对路径 404、`var(--*)` 元素全部隐形）。已在文档记录；后续可在 serve 时自动向上探测。

## 测试 C：设计系统——tokens 编译与消费

**任务**：init system → build tokens → check → 由测试 B 的画板通过 `tokens.css` 变量消费。

**结果**：✅ 28 行 tokens.css 一次生成；画板消费 `--accent/--border/--ink-100/--bg-000` 渲染正确。

## 汇总

| 指标 | 结果 |
|---|---|
| 真实缺陷 | 2 个（放映器 flex 压缩、CLI 直接执行崩溃）——均已修复 |
| 体验洞察 | 1 个（跨目录 tokens 需服务父目录，已记录） |
| 校验表现 | 3 次工作流全部一次通过 0 错 0 警 |
| 覆盖能力 | sc-for / sc-if / 事件 / 状态 / dc-import / tokens 消费 / 放映器 / PDF 前置全链路 |

## 复现

```bash
odk init deck my-deck && odk init canvas my-canvas && odk init system my-brand
# 按各 SKILL.md 写内容，然后：
odk check <dir> && odk build player my-deck && odk serve my-canvas
```
