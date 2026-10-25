---
layout: default
title: 设计系统格式规范
nav_order: 1
parent: 格式规范
permalink: /spec/open-design-system.html
---

# 设计系统格式规范（open-design-system）

设计系统是一个目录：`design-system.json`（身份）+ `tokens.json`（token 单一事实源）+ `README.md`（给 Agent 看的品牌手册）。`odk build tokens` 把它编译成 `tokens.css` 供画板与幻灯片消费。

## 文件形状

```
my-brand/
├── design-system.json   # {title, namespace, description}
├── tokens.json          # 颜色/间距/圆角/文字（见下）
├── README.md            # 品牌手册：祈使句写 token 用法规则
├── tokens.css           # build-tokens 生成，勿手改
├── fonts/               # 字体文件（tokens.json 的 type.fonts 引用）
└── assets/              # 图标与素材
```

## tokens.json 语法要点

- 颜色：`{"color": {"themes":[{"id":"light"}], "tokens":[{"name","value","usage"}]}}`
  - **必须是列表**（不是名字到值的映射）；值支持 `#rgb|#rgba|#rrggbb|#rrggbbaa` 与 `rgb()/hsl()/oklch()` 等（参数纯数字），或别名 `"{其他token}"`
  - 多主题：value 写成 `{"light": "#fff", "dark": "#111"}`；主题 ≤ 8，颜色 ≤ 600
- 间距/圆角：`{"spacing": {"tokens":[{"name","value"(px 数字或长度),"usage"}]}}`
- 文字：`{"type": {"families":{key: stack}, "groups":[{name, family, styles:[…]}], "fonts":[…]}}`
- 命名规则：`^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$`，编译为 `--name` CSS 变量

## 编译产物 tokens.css

`odk build tokens my-brand` 生成：

- `:root, [data-theme="<首主题>"] { --色值… --阴影… }`，其余主题各一个覆盖块
- `:root { --间距… --圆角… --font-<key> }`
- 每个文字样式一个 `.样式名` 类（font-size/weight/line-height/family）
- 每个 `fonts[]` 条目一条 `@font-face`

非法值、自指/幽灵别名会被**丢弃并警告**——不会悄悄混进产物。

## 消费

画板与幻灯片的 `designSystems` 字段登记本目录；产物通过 `tokens.css` 的变量取值（每个值只有一个来源）。
