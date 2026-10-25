"""OpenDesignKit engine: validators, scaffolds, builders (imported by odk.cli)."""
#!/usr/bin/env python3
"""
OpenDesignKit - Lightweight Validator CLI
Validates Open Design canvases, Open Slides decks, and Open Design Systems.
Zero external dependencies (Pure Python 3 standard library).
"""

import sys
import os
import json
import re
from pathlib import Path

# --- ANSI Colors ---
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_err(msg):
    print(f"{RED}✖ {msg}{RESET}")

def print_warn(msg):
    print(f"{YELLOW}⚠ {msg}{RESET}")

def print_ok(msg):
    print(f"{GREEN}✔ {msg}{RESET}")

# ==============================================================================
# 1. Slides Validator
# ==============================================================================

DISALLOWED_SLIDE_TAGS = {
    'html', 'head', 'body', 'script', 'style', 'title', 'link',
    'h4', 'h5', 'h6', 'blockquote', 'figure', 'pre', 'header',
    'footer', 'nav', 'main', 'article', 'iframe', 'video', 'embed'
}

def validate_slides(deck_dir):
    deck_path = Path(deck_dir)
    problems = []
    warnings = []

    print(f"\n{BOLD}{CYAN}Validating Slides Deck:{RESET} {deck_path}")

    # Check deck.json
    deck_json_path = deck_path / "deck.json"
    if not deck_json_path.exists():
        problems.append("deck.json not found in deck directory.")
        return problems, warnings

    try:
        with open(deck_json_path, 'r', encoding='utf-8') as f:
            deck_meta = json.load(f)
    except Exception as e:
        problems.append(f"deck.json contains invalid JSON: {e}")
        return problems, warnings

    # Validate deck metadata
    v = deck_meta.get("v")
    if v != 4:
        warnings.append(f"deck.json 'v' is {v}, expected 4.")

    title = deck_meta.get("title")
    if not title:
        problems.append("deck.json missing required 'title'.")

    order = deck_meta.get("order")
    if not isinstance(order, list) or len(order) == 0:
        problems.append("deck.json 'order' must be a non-empty array of slide IDs.")
        order = []

    cover = deck_meta.get("cover")
    if cover and cover not in order:
        problems.append(f"deck.json 'cover' ('{cover}') does not match any slide ID in 'order'.")

    sections = deck_meta.get("sections", {})
    if isinstance(sections, dict):
        for s_id, s_data in sections.items():
            start_id = s_data.get("start")
            if start_id and start_id not in order:
                problems.append(f"Section '{s_id}' start slide '{start_id}' not found in 'order'.")

    faces = deck_meta.get("faces", {})
    if not isinstance(faces, dict):
        problems.append("deck.json 'faces' must be an object.")
    else:
        for f_key, f_data in faces.items():
            if not isinstance(f_data, dict) or not f_data.get("family") or not f_data.get("href"):
                warnings.append(f"deck.json faces['{f_key}'] should declare both 'family' and 'href'.")

    # Check slides directory
    slides_dir = deck_path / "slides"
    if not slides_dir.exists():
        problems.append("Directory 'slides/' does not exist in deck.")
        return problems, warnings

    # Check each slide in order
    disk_slides = {f.stem: f for f in slides_dir.glob("*.html")}
    for slide_id in order:
        slide_file = slides_dir / f"{slide_id}.html"
        if not slide_file.exists():
            problems.append(f"Slide '{slide_id}' in order not found at slides/{slide_id}.html")
            continue

        try:
            with open(slide_file, 'r', encoding='utf-8') as sf:
                content = sf.read()
        except Exception as e:
            problems.append(f"Could not read {slide_file.name}: {e}")
            continue

        # Syntax checks
        # Check root <section>
        section_match = re.search(r'<\s*section\b([^>]*)>', content, re.IGNORECASE)
        if not section_match:
            problems.append(f"Slide '{slide_id}.html' must have a root <section> element.")
        else:
            attrs = section_match.group(1)
            # check id
            id_match = re.search(r'\bid\s*=\s*["\']([^"\']+)["\']', attrs)
            if not id_match or id_match.group(1) != slide_id:
                problems.append(f"Slide '{slide_id}.html' <section> id must match filename stem ('{slide_id}').")
            # check inline style
            if 'style=' not in attrs:
                warnings.append(f"Slide '{slide_id}.html' <section> should declare inline layout styles.")
            else:
                style_match = re.search(r'style\s*=\s*("([^"]*)"|\'([^\']*)\')', attrs)
                style_val = (style_match.group(2) or style_match.group(3) or "") if style_match else ""
                if '1920px' not in style_val:
                    warnings.append(f"Slide '{slide_id}.html' should set width:1920px (16:9 stage).")
                if '1080px' not in style_val:
                    warnings.append(f"Slide '{slide_id}.html' should set height:1080px (16:9 stage).")
            # speech notes
            if not re.search(r'<aside[^>]*>[\s\S]*?</aside>', content, re.IGNORECASE):
                warnings.append(f"Slide '{slide_id}.html' has no <aside> speech notes.")

        # Check for disallowed tags
        for tag in DISALLOWED_SLIDE_TAGS:
            if re.search(rf'<\s*{tag}\b', content, re.IGNORECASE):
                problems.append(f"Slide '{slide_id}.html' contains disallowed tag <{tag}>.")

    # Check orphans
    for stem, f in disk_slides.items():
        if stem not in order:
            warnings.append(f"Orphan slide file: {f.name} is on disk but not listed in deck.json 'order'.")

    return problems, warnings

# ==============================================================================
# 2. Design Canvas Validator
# ==============================================================================

def validate_design(canvas_dir):
    canvas_path = Path(canvas_dir)
    problems = []
    warnings = []

    print(f"\n{BOLD}{CYAN}Validating Design Canvas:{RESET} {canvas_path}")

    canvas_json_path = canvas_path / "canvas.json"
    if not canvas_json_path.exists():
        problems.append("canvas.json not found in canvas directory.")
        return problems, warnings

    try:
        with open(canvas_json_path, 'r', encoding='utf-8') as f:
            canvas_meta = json.load(f)
    except Exception as e:
        problems.append(f"canvas.json contains invalid JSON: {e}")
        return problems, warnings

    v = canvas_meta.get("v")
    if v != 3:
        warnings.append(f"canvas.json 'v' is {v}, expected 3.")

    title = canvas_meta.get("title")
    if not title:
        problems.append("canvas.json missing required 'title'.")

    boards = canvas_meta.get("boards", {})
    if not isinstance(boards, dict) or len(boards) == 0:
        problems.append("canvas.json 'boards' must be a non-empty object mapping filenames to frames.")

    order = canvas_meta.get("order", [])
    if not isinstance(order, list):
        problems.append("canvas.json 'order' must be an array.")

    # Check boards in canvas.json
    for board_file_rel, frame in boards.items():
        # Validate frame dimensions
        w = frame.get("w", 0)
        h = frame.get("h", 0)
        if not (40 <= w <= 8000 and 40 <= h <= 8000):
            problems.append(f"Board '{board_file_rel}' dimensions out of range (40..8000): {w}x{h}")

        board_path = canvas_path / board_file_rel
        if not board_path.exists():
            problems.append(f"Board file declared in canvas.json missing: {board_file_rel}")
            continue

        try:
            with open(board_path, 'r', encoding='utf-8') as bf:
                content = bf.read()
        except Exception as e:
            problems.append(f"Could not read board file {board_file_rel}: {e}")
            continue

        # Check support.js line
        if '<script src="./support.js"></script>' not in content:
            warnings.append(f"Board '{board_file_rel}' missing recommended '<script src=\"./support.js\"></script>'.")

        # Check <x-dc> root tag
        if '<x-dc>' not in content or '</x-dc>' not in content:
            problems.append(f"Board '{board_file_rel}' must contain <x-dc> template block.")

        # Check DCLogic script
        if 'data-dc-script' not in content:
            problems.append(f"Board '{board_file_rel}' missing <script type=\"text/x-dc\" data-dc-script> block.")

        if 'class Component extends DCLogic' not in content:
            problems.append(f"Board '{board_file_rel}' script must define 'class Component extends DCLogic'.")

        # Check $preview matches canvas.json
        props_match = re.search(r"data-props='([^']+)'", content)
        if props_match:
            try:
                props_data = json.loads(props_match.group(1))
                preview = props_data.get("$preview", {})
                if preview:
                    pw = preview.get("width")
                    ph = preview.get("height")
                    if pw and pw != w:
                        warnings.append(f"Board '{board_file_rel}' $preview.width ({pw}) != canvas.json width ({w}).")
                    if ph and ph != h:
                        warnings.append(f"Board '{board_file_rel}' $preview.height ({ph}) != canvas.json height ({h}).")
            except Exception as e:
                problems.append(f"Board '{board_file_rel}' data-props is not valid single-quoted JSON: {e}")
        else:
            warnings.append(f"Board '{board_file_rel}' data-props attribute missing or not single-quoted.")

        # Check for disallowed tags
        for dis_tag in ['iframe', 'object', 'embed']:
            if re.search(rf'<\s*{dis_tag}\b', content, re.IGNORECASE):
                problems.append(f"Board '{board_file_rel}' contains disallowed tag <{dis_tag}>.")

        # Check data URI
        if 'src="data:' in content:
            problems.append(f"Board '{board_file_rel}' contains forbidden data: URI.")

    # Check order completeness
    for b in boards.keys():
        if b not in order:
            warnings.append(f"Board '{b}' in 'boards' is not listed in 'order'.")

    # launch view
    launch = canvas_meta.get("launch")
    if launch is not None:
        view = launch.get("view") if isinstance(launch, dict) else None
        if view not in ("canvas", "focused"):
            warnings.append(f"canvas.json launch.view '{view}' should be 'canvas' or 'focused'.")
        if view == "focused" and not launch.get("file"):
            problems.append("canvas.json launch.view 'focused' requires a 'file' entry.")

    # pages must be a list
    if "pages" in canvas_meta and not isinstance(canvas_meta["pages"], list):
        problems.append("canvas.json 'pages' must be an array.")

    # notes shape
    notes = canvas_meta.get("notes", {})
    if not isinstance(notes, dict):
        problems.append("canvas.json 'notes' must be an object.")
    else:
        for n_id, n_data in notes.items():
            if not isinstance(n_data, dict):
                problems.append(f"canvas.json note '{n_id}' must be an object.")
                continue
            if not isinstance(n_data.get("x"), (int, float)) or not isinstance(n_data.get("y"), (int, float)):
                warnings.append(f"canvas.json note '{n_id}' should declare numeric x/y.")
            if not isinstance(n_data.get("text"), str) or not n_data.get("text"):
                warnings.append(f"canvas.json note '{n_id}' should declare non-empty 'text'.")

    # guides shape
    for b_file, frame in boards.items():
        if not isinstance(frame, dict):
            continue
        guides = frame.get("guides")
        if guides is None:
            continue
        if not isinstance(guides, list):
            problems.append(f"Board '{b_file}' guides must be an array.")
            continue
        if len(guides) > 6:
            warnings.append(f"Board '{b_file}' has more than 6 guides; extra ones are ignored by editors.")
        for g in guides[:6]:
            if not isinstance(g, dict) or g.get("kind") not in ("columns", "rows", "grid"):
                problems.append(f"Board '{b_file}' has an invalid guide entry (kind must be columns/rows/grid).")

    return problems, warnings

# ==============================================================================
# 3. Design System Validator
# ==============================================================================

def validate_design_system(ds_dir):
    ds_path = Path(ds_dir)
    problems = []
    warnings = []

    print(f"\n{BOLD}{CYAN}Validating Design System:{RESET} {ds_path}")

    # Check design-system.json
    ds_json_path = ds_path / "design-system.json"
    if not ds_json_path.exists():
        problems.append("design-system.json not found in directory.")
        return problems, warnings

    try:
        with open(ds_json_path, 'r', encoding='utf-8') as f:
            ds_meta = json.load(f)
    except Exception as e:
        problems.append(f"design-system.json contains invalid JSON: {e}")
        return problems, warnings

    if not ds_meta.get("title"):
        problems.append("design-system.json missing required 'title'.")

    if not ds_meta.get("namespace"):
        warnings.append("design-system.json missing 'namespace'.")

    # Check tokens.json
    tokens_json_path = ds_path / "tokens.json"
    if not tokens_json_path.exists():
        problems.append("tokens.json not found in design system directory.")
    else:
        try:
            tokens = json.loads(tokens_json_path.read_text(encoding="utf-8"))
            color_sec = tokens.get("color", {})
            if "tokens" in color_sec:
                if not isinstance(color_sec["tokens"], list):
                    problems.append("tokens.json 'color.tokens' must be a list of token objects, not a dict/map.")
                else:
                    if len(color_sec.get("themes") or []) > 8:
                        warnings.append("tokens.json: more than 8 color themes; extras are ignored.")
                    if len(color_sec["tokens"]) > 600:
                        warnings.append("tokens.json: more than 600 color tokens; extras are ignored.")
                    by_name = {t.get("name"): t for t in color_sec["tokens"] if isinstance(t, dict)}
                    for t in color_sec["tokens"]:
                        if not isinstance(t, dict):
                            problems.append(f"tokens.json color token entry is not an object: {t}")
                            continue
                        name = t.get("name")
                        if not name:
                            problems.append(f"Color token missing 'name': {t}")
                            continue
                        if not _NAME_RE.match(str(name)):
                            problems.append(f"Color token '{name}': name violates ^[A-Za-z0-9][A-Za-z0-9_.-]{{0,63}}$")
                        values = t.get("value")
                        theme_ids = [th.get("id") for th in (color_sec.get("themes") or []) if isinstance(th, dict)] or ["light"]
                        per_theme = values if isinstance(values, dict) else {theme_ids[0]: values}
                        for tid in per_theme:
                            if tid not in theme_ids:
                                warnings.append(f"Color token '{name}': value references unknown theme '{tid}'.")
                            _color_css(per_theme[tid], by_name, warnings, f"color token '{name}' ({tid})", cur_name=str(name))
            for fam in ("spacing", "radius"):
                sec = tokens.get(fam, {})
                if "tokens" in sec and not isinstance(sec["tokens"], list):
                    problems.append(f"tokens.json '{fam}.tokens' must be a list.")
                elif isinstance(sec, dict):
                    for t in (sec.get("tokens") or []):
                        if isinstance(t, dict):
                            if not _NAME_RE.match(str(t.get("name", ""))):
                                problems.append(f"{fam} token '{t.get('name')}': name violates naming rule.")
                            _length_css(t.get("value"), warnings, f"{fam} token '{t.get('name')}'")
            type_sec = tokens.get("type", {})
            if not isinstance(type_sec, dict):
                problems.append("tokens.json 'type' must be an object.")
            else:
                for key, stack in (type_sec.get("families") or {}).items():
                    if not isinstance(stack, str) or len(stack) > 200 or any(c in stack for c in ";{}<>\\"):
                        problems.append(f"type.families['{key}'] must be a CSS font-family stack <=200 chars without ;{{}}<>\\.")
                for g in (type_sec.get("groups") or []):
                    if not isinstance(g, dict):
                        continue
                    for st in (g.get("styles") or []):
                        sname = st.get("name", "")
                        if not _NAME_RE.match(str(sname)):
                            problems.append(f"Text style '{sname}': name violates naming rule.")
                            continue
                        _length_css(st.get("fontSize"), warnings, f"style '{sname}'.fontSize")
                        if st.get("fontSize") is None:
                            problems.append(f"Text style '{sname}' missing 'fontSize'.")
                for f in (type_sec.get("fonts") or []):
                    if not isinstance(f, dict) or not f.get("family") or not f.get("file"):
                        warnings.append(f"type.fonts entry needs 'family' and 'file': {f}")
                        continue
                    ffile = f["file"]
                    fpath = ds_path / (ffile if "/" in ffile else f"fonts/{ffile}")
                    if not fpath.exists():
                        warnings.append(f"Font file declared but missing on disk: {fpath}")
        except Exception as e:
            problems.append(f"tokens.json could not be parsed: {e}")

    # Check README.md
    readme_path = ds_path / "README.md"
    if not readme_path.exists():
        problems.append("README.md (brand manual) not found in design system directory.")

    return problems, warnings

# ==============================================================================
# 4. Type Detection & Scaffolding & Builders
# ==============================================================================

TEMPLATES = Path(__file__).resolve().parent / "templates"  # packaged: odk/templates

def detect_type(target_dir):
    p = Path(target_dir)
    if (p / "design-system.json").exists():
        return "design-system"
    if (p / "canvas.json").exists():
        return "design"
    if (p / "deck.json").exists():
        return "slides"
    return None


def _write_file(path: Path, content: str, overwrite=False):
    if path.exists() and not overwrite:
        print_warn(f"已存在，跳过：{path}")
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print_ok(f"已创建：{path}")
    return True


def _copy_template(name: str, dest: Path, overwrite=False):
    return _write_file(dest, (TEMPLATES / name).read_text(encoding="utf-8"), overwrite)


def init_canvas(target_dir):
    p = Path(target_dir)
    print(f"\n{BOLD}{CYAN}初始化 Design Canvas：{RESET}{p}")
    canvas_json = {
        "v": 3,
        "title": "新设计稿",
        "launch": {"view": "canvas"},
        "pages": [],
        "boards": {"Main.dc.html": {"x": 0, "y": 0, "w": 960, "h": 600, "title": "Main", "is_interactive": True}},
        "order": ["Main.dc.html"],
        "notes": {},
        "designSystems": [],
    }
    _write_file(p / "canvas.json", json.dumps(canvas_json, ensure_ascii=False, indent=2) + "\n")
    _copy_template("board.html", p / "Main.dc.html")
    _copy_template("support.js", p / "support.js")
    print(f"\n下一步：编辑画板后运行 {BOLD}python3 tools/validator.py check {p}{RESET}")


def init_deck(target_dir):
    p = Path(target_dir)
    print(f"\n{BOLD}{CYAN}初始化 Slides Deck：{RESET}{p}")
    deck_json = {
        "v": 4,
        "lists": "css",
        "title": "新演示文稿",
        "order": ["cover"],
        "cover": "cover",
        "sections": {},
        "faces": {
            "source-sans-3": {
                "family": "Source Sans 3",
                "href": "https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700&display=swap",
            }
        },
        "designSystems": [],
    }
    _write_file(p / "deck.json", json.dumps(deck_json, ensure_ascii=False, indent=2) + "\n")
    _copy_template("cover.html", p / "slides" / "cover.html")
    build_player(p)
    print(f"\n下一步：写完各页后运行 {BOLD}python3 tools/validator.py check {p}{RESET}，再 {BOLD}build-player{RESET} 刷新播放器")


def init_design_system(target_dir):
    p = Path(target_dir)
    print(f"\n{BOLD}{CYAN}初始化 Design System：{RESET}{p}")
    ds_json = {"title": "新设计系统", "namespace": "ods", "description": "一句话说明这套系统的定位。"}
    _write_file(p / "design-system.json", json.dumps(ds_json, ensure_ascii=False, indent=2) + "\n")
    tokens_json = {
        "color": {
            "themes": [{"id": "light"}],
            "tokens": [
                {"name": "bg-000", "value": "#faf9f5", "usage": "页面背景"},
                {"name": "ink-000", "value": "#141413", "usage": "主文字"},
                {"name": "accent", "value": "#c2410c", "usage": "强调色"},
                {"name": "border", "value": "#eaecf0", "usage": "描边与分隔线"},
            ],
        },
        "spacing": {"tokens": [
            {"name": "space-1", "value": 8, "usage": "最小间距"},
            {"name": "space-2", "value": 16, "usage": "元素内间距"},
            {"name": "space-3", "value": 24, "usage": "卡片间距"},
        ]},
        "radius": {"tokens": [{"name": "radius-md", "value": 16, "usage": "卡片圆角"}]},
        "type": {
            "families": {"sans": "'Source Sans 3', system-ui, sans-serif"},
            "groups": [
                {"name": "Text", "family": "sans", "styles": [
                    {"name": "heading", "fontSize": 32, "fontWeight": 600, "lineHeight": 1.25, "usage": "标题"},
                    {"name": "body", "fontSize": 22, "fontWeight": 400, "lineHeight": 1.5, "usage": "正文"},
                ]}
            ],
        },
    }
    _write_file(p / "tokens.json", json.dumps(tokens_json, ensure_ascii=False, indent=2) + "\n")
    _write_file(p / "README.md", "# 新设计系统\n\n品牌手册：用祈使句写 token 用法规则（例如「正文用 `body`；强调色只用 `accent`」）。\n")
    build_tokens(p)
    print(f"\n下一步：扩充 tokens 后运行 {BOLD}python3 tools/validator.py check {p}{RESET}，再 {BOLD}build-tokens{RESET} 重新编译")


# ------------------------------------------------------------------ build-tokens

_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$")
_LENGTH_RE = re.compile(r"^(?:\d*\.?\d+)(?:px|rem|em|%)$")

def _clean_var_name(name):
    n = name.lstrip("-").lstrip(".")
    return n.replace(".", "\\.")

def _length_css(value, warn, ctx):
    if isinstance(value, (int, float)):
        return f"{value}px"
    if isinstance(value, str):
        v = value.strip()
        if _LENGTH_RE.match(v) or v == "0":
            return v
        try:
            f = float(v)
            return f"{f}px"
        except ValueError:
            pass
    warn.append(f"{ctx}：非法长度值 {value!r}，已丢弃")
    return None

def _color_css(value, by_name, warn, ctx, cur_name=None):
    if not isinstance(value, str):
        warn.append(f"{ctx}：颜色值必须是字符串，已丢弃 {value!r}")
        return None
    v = value.strip()
    if re.match(r"^\{[A-Za-z0-9_.-]+\}$", v):
        target = v[1:-1]
        if cur_name is not None and target == cur_name:
            warn.append(f"{ctx}：alias 指向自己，已丢弃")
            return None
        if target not in by_name:
            warn.append(f"{ctx}：alias 指向不存在的 token '{target}'，已丢弃")
            return None
        return f"var(--{_clean_var_name(target)})"
    if re.match(r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$", v):
        return v.lower()
    if re.match(r"^(rgb|rgba|hsl|hsla|oklch|oklab|lab|lch|color)\([0-9a-zA-Z%.#, \\t-]+\)$", v):
        return v
    warn.append(f"{ctx}：非法颜色值 {v!r}，已丢弃")
    return None

def compile_tokens(tokens):
    """tokens.json -> tokens.css per OpenDesignKit format spec. Returns (css, warnings)."""
    warn = []
    out = []
    if not isinstance(tokens, dict):
        return None, ["tokens.json 根必须是对象"]

    color_sec = tokens.get("color", {})
    themes = color_sec.get("themes") or [{"id": "light"}]
    theme_ids = [t.get("id") for t in themes if isinstance(t, dict) and t.get("id")]
    if not theme_ids:
        theme_ids = ["light"]
    first = theme_ids[0]

    by_name = {}
    for t in color_sec.get("tokens", []) or []:
        if isinstance(t, dict) and t.get("name"):
            by_name[t["name"]] = t

    def token_css(t, theme_id):
        name = t.get("name", "")
        ctx = f"color token '{name}'"
        if not _NAME_RE.match(name):
            warn.append(f"{ctx}：名字不符合规范，已丢弃")
            return None
        raw = t.get("value")
        if isinstance(raw, dict):
            val = raw.get(theme_id, raw.get(first))
        else:
            val = raw
        if val is None:
            return None
        return _color_css(val, by_name, warn, ctx, cur_name=name)

    # first theme block
    lines = [f":root, [data-theme=\"{first}\"] {{"]
    for name, t in by_name.items():
        css = token_css(t, first)
        if css:
            lines.append(f"  --{_clean_var_name(name)}: {css};")
    shadow_sec = tokens.get("shadow", {})
    for t in (shadow_sec.get("tokens") or []):
        name, ctx = t.get("name", ""), "shadow token"
        if isinstance(name, str) and _NAME_RE.match(name):
            val = t.get("value")
            val = val.get(first) if isinstance(val, dict) else val
            if isinstance(val, str) and len(val) <= 400 and "url(" not in val and "var(" not in val:
                lines.append(f"  --{_clean_var_name(name)}: {val};")
            else:
                warn.append(f"shadow token '{name}'：非法值，已丢弃")
    lines.append("}")
    out.append("\n".join(lines))

    # other themes
    for tid in theme_ids[1:]:
        lines = [f"[data-theme=\"{tid}\"] {{"]
        for name, t in by_name.items():
            css = token_css(t, tid)
            if css:
                lines.append(f"  --{_clean_var_name(name)}: {css};")
        lines.append("}")
        out.append("\n".join(lines))

    # spacing / radius / other families
    root_vars = []
    for fam in ("spacing", "radius"):
        for t in (tokens.get(fam, {}).get("tokens") or []):
            name = t.get("name", "")
            if not (isinstance(name, str) and _NAME_RE.match(name)):
                warn.append(f"{fam} token '{name}'：名字不符合规范，已丢弃")
                continue
            css = _length_css(t.get("value"), warn, f"{fam} token '{name}'")
            if css:
                root_vars.append(f"  --{_clean_var_name(name)}: {css};")
    for fam_key, fam in tokens.items():
        if fam_key in ("color", "spacing", "radius", "shadow", "type") or not isinstance(fam, dict):
            continue
        for t in (fam.get("tokens") or [])[:60]:
            name = t.get("name", "")
            if isinstance(name, str) and _NAME_RE.match(name) and isinstance(t.get("value"), str) and len(t["value"]) <= 200:
                root_vars.append(f"  --{_clean_var_name(name)}: {t['value']};")

    type_sec = tokens.get("type", {})
    for key, stack in (type_sec.get("families") or {}).items():
        if isinstance(stack, str) and len(stack) <= 200:
            root_vars.append(f"  --font-{key}: {stack};")
    if root_vars:
        out.append(":root {\n" + "\n".join(root_vars) + "\n}")

    # text styles
    for group in (type_sec.get("groups") or []):
        g_family = group.get("family")
        for st in (group.get("styles") or []):
            name = st.get("name", "")
            if not (isinstance(name, str) and _NAME_RE.match(name)):
                warn.append(f"文字样式 '{name}'：名字不符合规范，已丢弃")
                continue
            fs = _length_css(st.get("fontSize"), warn, f"样式 '{name}'.fontSize")
            if not fs:
                continue
            decls = [f"  font-size: {fs};"]
            if st.get("fontWeight") is not None:
                decls.append(f"  font-weight: {st['fontWeight']};")
            lh = st.get("lineHeight")
            if lh is not None:
                lh_css = lh if isinstance(lh, (int, float)) and lh < 10 else _length_css(lh, warn, f"样式 '{name}'.lineHeight")
                if lh_css:
                    decls.append(f"  line-height: {lh_css};")
            if st.get("letterSpacing") is not None:
                ls = _length_css(st["letterSpacing"], warn, f"样式 '{name}'.letterSpacing")
                if ls:
                    decls.append(f"  letter-spacing: {ls};")
            fam = st.get("family") or g_family
            if fam:
                stack = (type_sec.get("families") or {}).get(fam)
                if stack:
                    decls.append(f"  font-family: {stack};")
            out.append(f".{name} {{\n" + "\n".join(decls) + "\n}")

    # @font-face
    for f in (type_sec.get("fonts") or []):
        fam, file = f.get("family"), f.get("file")
        if not (fam and file):
            warn.append("type.fonts entry 缺少 family/file，已跳过")
            continue
        src = file if "/" in file else f"fonts/{file}"
        decls = [f"  font-family: {fam};", f'  src: url("{src}");']
        if f.get("weight") is not None:
            decls.append(f"  font-weight: {f['weight']};")
        if f.get("style") is not None:
            decls.append(f"  font-style: {f['style']};")
        out.append("@font-face {\n" + "\n".join(decls) + "\n}")

    return "\n\n".join(out) + "\n", list(dict.fromkeys(warn))


def build_tokens(target_dir):
    p = Path(target_dir)
    print(f"\n{BOLD}{CYAN}编译 Design System tokens：{RESET}{p}")
    tokens_path = p / "tokens.json"
    if not tokens_path.exists():
        print_err("tokens.json 不存在")
        return 1
    try:
        tokens = json.loads(tokens_path.read_text(encoding="utf-8"))
    except Exception as e:
        print_err(f"tokens.json JSON 解析失败：{e}")
        return 1
    css, warns = compile_tokens(tokens)
    if css is None:
        for w in warns:
            print_err(w)
        return 1
    out_path = p / "tokens.css"
    out_path.write_text(css, encoding="utf-8")
    for w in warns:
        print_warn(w)
    print_ok(f"已生成：{out_path}（{len(css.splitlines())} 行）")
    return 0


# ------------------------------------------------------------------ build-player

def _json_for_inline_script(obj):
    """JSON safe for embedding inside a classic <script> block:
    - `</` is escaped to `<\\/` (valid JSON escape) so the payload can never
      close the script tag early;
    - `<!--` would push the HTML parser into script-data-escaped state, so
      `!` is rewritten to the unicode escape `\\u0021` (also valid JSON).
    """
    s = json.dumps(obj, ensure_ascii=False)
    s = s.replace("</", "<\\/")
    s = s.replace("<!--", "<\\u0021--")
    return s


def build_player(target_dir):
    p = Path(target_dir)
    print(f"\n{BOLD}{CYAN}生成 Slides 播放器：{RESET}{p}")
    deck_path = p / "deck.json"
    if not deck_path.exists():
        print_err("deck.json 不存在")
        return 1
    try:
        deck = json.loads(deck_path.read_text(encoding="utf-8"))
    except Exception as e:
        print_err(f"deck.json JSON 解析失败：{e}")
        return 1
    notes = {}
    for slide_id in deck.get("order", []):
        sf = p / "slides" / f"{slide_id}.html"
        if not sf.exists():
            continue
        m = re.search(r"<aside[^>]*>([\s\S]*?)</aside>", sf.read_text(encoding="utf-8"), re.IGNORECASE)
        if m:
            text = re.sub(r"<[^>]+>", " ", m.group(1))
            text = re.sub(r"\s+", " ", text).strip()
            if text:
                notes[slide_id] = text
    payload = dict(deck)
    payload["__notes__"] = notes
    tpl = (TEMPLATES / "player.html").read_text(encoding="utf-8")
    html = tpl.replace("__DECK_JSON__", _json_for_inline_script(payload))
    out_path = p / "player.html"
    out_path.write_text(html, encoding="utf-8")
    print_ok(f"已生成：{out_path}（含 {len(notes)} 页备注；浏览器直接打开，←→ 翻页，S 讲稿，O 目录）")
    return 0


