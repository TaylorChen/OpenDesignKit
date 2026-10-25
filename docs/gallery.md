---
layout: default
title: 示例画廊
nav_order: 3
permalink: /gallery.html
---

# 示例画廊

以下示例与仓库 `examples/` 目录保持同步（由 `tools/build-gallery.py` 生成）。
点击"打开"直接在新标签页体验；仓库源码链接在中间列。

| 示例 | 源码 | 在线体验 |
|---|---|---|
| **幻灯片 · 放映器**<br>deck.json + 每页一个 HTML；← → 翻页，S 讲稿，O 目录 | [`demo-slides`](https://github.com/TaylorChen/OpenDesignKit/tree/main/examples/demo-slides) | [打开放映器]({{ site.baseurl }}/gallery/demo-slides/player.html) |
| **可交互画板**<br>canvas.json + .dc.html；support.js 渲染，点击色板换主题色 | [`demo-design`](https://github.com/TaylorChen/OpenDesignKit/tree/main/examples/demo-design) | [打开画板]({{ site.baseurl }}/gallery/demo-design/Main.dc.html) |
| **设计系统**<br>tokens.json 单一事实源 + 品牌手册 + 编译产物 tokens.css | [`demo-design-system`](https://github.com/TaylorChen/OpenDesignKit/tree/main/examples/demo-design-system) | [查看品牌手册]({{ site.baseurl }}/gallery/demo-design-system/README.md) |

## 更新画廊

示例内容变化后，在仓库根目录运行：

```bash
python3 tools/build-gallery.py
```

脚本会把 `examples/` 的最新产物复制到 `docs/gallery/` 并重新生成本页。
