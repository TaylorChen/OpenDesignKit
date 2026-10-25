---
layout: default
title: 设计稿格式规范
nav_order: 2
parent: 格式规范
permalink: /spec/open-design.html
---

# 设计稿格式规范（open-design）

一份设计稿是工作目录里的一个目录：`canvas.json` 索引 + 每块画板一个 `.dc.html`。画板是**自成一体的 HTML 组件**（`<x-dc>` 模板 + DCLogic 状态类），支持交互。

## 文件形状

```
my-canvas/
├── canvas.json        # 索引：画板布局、顺序、便签、引用的设计系统
├── Main.dc.html       # 每块画板一个文件
├── Card.dc.html       # 子组件画板（可被 dc-import 引用）
└── support.js         # 预览运行时（odk init canvas 自动附带）
```

## canvas.json 关键字段

| 字段 | 说明 |
|---|---|
| `v` | 固定 `3` |
| `boards` | `{文件名: {x, y, w, h, title, is_interactive}}`；尺寸 40–8000 |
| `order` | 画板顺序 |
| `notes` | 画布便签 `{id: {x, y, text, kind}}` |
| `launch` | `{"view": "canvas"}` 或聚焦单画板 `{"view":"focused","file":"Main.dc.html"}` |

## 画板（.dc.html）结构

```html
<script src="./support.js"></script>          <!-- 预览运行时（编辑器存在时用编辑器的） -->
<x-dc>                                        <!-- 模板块 -->
  <helmet><style>…</style></helmet>           <!-- 注入页头 -->
  …布局 + {{ holes }} + <sc-for>/<sc-if>…     <!-- 声明式模板 -->
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{…}'>
class Component extends DCLogic {             <!-- 状态与事件 -->
  renderVals() { return { … }; }
}
</script>
```

- **hole**：`{{ 路径 }}`（点号取值，不写表达式）；字面量 `true/false/null/数字` 可用
- **控制流**：`<sc-for list="{{items}}" as="item">` 重复；`<sc-if value="{{cond}}">` 分支
- **事件**：`onClick="{{ fn }}"`（renderVals 返回的函数）
- **子组件**：`<dc-import name="Card" title="…" hint-size="300px,120px">` 挂载同级 `Card.dc.html`
- **画板间链接**：`<a href="Other.dc.html">` 原生跳转
- `data-props`：声明可编辑属性（单引号包裹的 JSON）；`$preview` 应与 canvas.json 画框一致

## 校验与预览

```bash
odk check my-canvas          # <x-dc>/DCLogic/data-props/禁用标签/尺寸/notes/guides
odk serve my-canvas          # 浏览器打开；dc-import 子组件需要 http 服务
```
