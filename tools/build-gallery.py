#!/usr/bin/env python3
"""Sync examples into the GitHub Pages gallery (docs/gallery/).

Copies the three runnable examples (player/board/design-system) into
docs/gallery/<name>/ so the Pages site can serve them, then regenerates
docs/gallery.md link cards.

Usage: python3 tools/build-gallery.py
"""

import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "examples"
DST = REPO / "docs" / "gallery"

COPYSETS = {
    "demo-slides": ["deck.json", "player.html", "slides"],
    "demo-design": ["canvas.json", "Main.dc.html", "support.js"],
    "demo-design-system": ["design-system.json", "tokens.json", "tokens.css", "README.md"],
}

TITLES = {
    "demo-slides": ("幻灯片 · 放映器", "deck.json + 每页一个 HTML；← → 翻页，S 讲稿，O 目录"),
    "demo-design": ("可交互画板", "canvas.json + .dc.html；support.js 渲染，点击色板换主题色"),
    "demo-design-system": ("设计系统", "tokens.json 单一事实源 + 品牌手册 + 编译产物 tokens.css"),
}


def main() -> int:
    if not SRC.exists():
        print("examples/ 不存在", file=sys.stderr)
        return 1
    if DST.exists():
        shutil.rmtree(DST)
    DST.mkdir(parents=True)

    for name, items in COPYSETS.items():
        dest = DST / name
        dest.mkdir()
        for item in items:
            src = SRC / name / item
            if not src.exists():
                print(f"  ⚠ 跳过不存在的 {src.relative_to(REPO)}", file=sys.stderr)
                continue
            if src.is_dir():
                shutil.copytree(src, dest / item)
            else:
                shutil.copy2(src, dest / item)
        print(f"  ✔ {dest.relative_to(REPO)}")

    def link(name: str, path: str) -> str:
        return f"{{{{ site.baseurl }}}}/{path}"

    rows = []
    for name, (title, desc) in TITLES.items():
        if name == "demo-slides":
            href = "{{ site.baseurl }}/gallery/demo-slides/player.html"
            cta = "打开放映器"
        elif name == "demo-design":
            href = "{{ site.baseurl }}/gallery/demo-design/Main.dc.html"
            cta = "打开画板"
        else:
            href = "{{ site.baseurl }}/gallery/demo-design-system/README.md"
            cta = "查看品牌手册"
        rows.append(
            f"| **{title}**<br>{desc} | [`{name}`](https://github.com/TaylorChen/OpenDesignKit/tree/main/examples/{name}) | [{cta}]({href}) |"
        )

    gallery_md = f"""---
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
{chr(10).join(rows)}

## 更新画廊

示例内容变化后，在仓库根目录运行：

```bash
python3 tools/build-gallery.py
```

脚本会把 `examples/` 的最新产物复制到 `docs/gallery/` 并重新生成本页。
"""
    (REPO / "docs" / "gallery.md").write_text(gallery_md, encoding="utf-8")
    print("  ✔ docs/gallery.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
