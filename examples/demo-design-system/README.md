# OpenDesignKit Default System

默认设计系统：暖调中性色 + 橙色强调 + Source Sans 3。为 Open Design 画板、Open Slides 幻灯片与任何 HTML 产物提供统一的视觉语言。

## 使用方式

- **画板 / 幻灯片**：把颜色写成行内样式时直接取下表的 hex 值（单一来源原则：不要在 `<style>` 里粘贴原始值以外的变体）。
- **字体**：在 `deck.json` 的 `faces` 或页面 `<head>` 里引入 `https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700&display=swap`，`font-family` 写 `'Source Sans 3', system-ui, sans-serif`。
- **自定义**：以 `tokens.json` 为模板替换色板与字号，保留列表形状（`{"tokens":[{"name","value","usage"}]}`），不要改成名字到值的映射。

## 色板

| Token | 值 | 用途 |
|---|---|---|
| bg-000 | `#faf9f5` | 页面默认背景（暖调纸感白） |
| bg-100 | `#ffffff` | 卡片与浮层 |
| bg-dark | `#141413` | 深色节背景 |
| ink-000 | `#141413` | 主文字 |
| ink-100 | `#475467` | 次级文字 |
| ink-200 | `#98a2b3` | 辅助文字 |
| accent | `#c2410c` | 强调：序号、按钮、链接 |
| accent-hover | `#92400e` | 强调悬停态 |
| border | `#eaecf0` | 描边与分隔线 |

## 字号刻度

| 样式 | 字号/行高 | 用途 |
|---|---|---|
| display-xl | 96 / 1.05 · 700 | 封面主标题 |
| display-lg | 64 / 1.1 · 700 | 章节大标题 |
| heading | 32 / 1.25 · 600 | 卡片标题 |
| body | 22 / 1.5 · 400 | 正文 |
| caption | 17 / 1.5 · 400 | 注释 |
| eyebrow | 20 / 1.2 · 600 · 0.08em | 栏首小标 |

## 间距与圆角

8pt 刻度：8 / 16 / 24 / 40 / 64 / 128。圆角：8（控件）、16（卡片）、999（圆形）。
