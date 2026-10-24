#!/usr/bin/env python3
"""
OpenClaudeDesign - Lightweight Validator CLI
Validates Claude Design canvases, Claude Slides decks, and Claude Design Systems.
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
            with open(tokens_json_path, 'r', encoding='utf-8') as f:
                tokens = json.load(f)
            # Check color tokens format
            color_sec = tokens.get("color", {})
            if "tokens" in color_sec:
                if not isinstance(color_sec["tokens"], list):
                    problems.append("tokens.json 'color.tokens' must be a list of token objects, not a dict/map.")
                else:
                    for t in color_sec["tokens"]:
                        if not t.get("name"):
                            problems.append(f"Color token missing 'name': {t}")
                        if not t.get("value"):
                            problems.append(f"Color token '{t.get('name')}' missing 'value'.")
        except Exception as e:
            problems.append(f"tokens.json contains invalid JSON: {e}")

    # Check README.md
    readme_path = ds_path / "README.md"
    if not readme_path.exists():
        problems.append("README.md (brand manual) not found in design system directory.")

    return problems, warnings

# ==============================================================================
# CLI Entrypoint
# ==============================================================================

def main():
    if len(sys.argv) < 3:
        print(f"{BOLD}OpenClaudeDesign Validator CLI{RESET}")
        print("Usage:")
        print("  python tools/validator.py check-slides <deck-dir>")
        print("  python tools/validator.py check-design <canvas-dir>")
        print("  python tools/validator.py check-design-system <system-dir>")
        sys.exit(1)

    cmd = sys.argv[1]
    target_dir = sys.argv[2]

    if not os.path.isdir(target_dir):
        print_err(f"Directory not found: {target_dir}")
        sys.exit(1)

    if cmd == "check-slides":
        problems, warnings = validate_slides(target_dir)
    elif cmd == "check-design":
        problems, warnings = validate_design(target_dir)
    elif cmd == "check-design-system":
        problems, warnings = validate_design_system(target_dir)
    else:
        print_err(f"Unknown command: {cmd}")
        sys.exit(1)

    # Output Summary
    print()
    if warnings:
        for w in warnings:
            print_warn(w)

    if problems:
        for p in problems:
            print_err(p)
        print(f"\n{RED}{BOLD}Validation FAILED with {len(problems)} error(s) and {len(warnings)} warning(s).{RESET}\n")
        sys.exit(1)
    else:
        print_ok(f"{BOLD}Validation PASSED with 0 error(s) ({len(warnings)} warning(s)).{RESET}\n")
        sys.exit(0)

if __name__ == "__main__":
    main()
