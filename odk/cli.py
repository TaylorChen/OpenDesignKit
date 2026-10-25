"""odk — unified CLI for OpenDesignKit.

Commands:
  odk init deck|canvas|system <dir>     scaffold a new artifact
  odk check <dir> [--json]              validate (auto-detects format)
  odk build player <deck-dir>           (re)generate the slide player
  odk build tokens <system-dir>         compile tokens.json -> tokens.css
  odk serve <dir> [--port N]            local preview server (enables dc-import)
  odk export-pdf <deck-dir> [--out D]   export each slide as PDF (16:9)

Legacy entry point: `python3 tools/validator.py ...` still works and maps here.
"""

import argparse
import http.server
import json
import os
import shutil
import socketserver
import subprocess
import sys
import tempfile
from pathlib import Path

from . import core
from . import __version__

SLIDE_W_IN, SLIDE_H_IN = 20, 11.25  # 1920x1080 @96dpi


def _chrome():
    """Locate a Chrome/Chromium binary (env override first)."""
    cand = [os.environ.get("CHROME_BIN"), shutil.which("google-chrome"),
            shutil.which("chromium"), shutil.which("chromium-browser")]
    if sys.platform == "darwin":
        cand.append("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
    if sys.platform.startswith("win"):
        cand.append(str(Path(os.environ.get("PROGRAMFILES", "C:/Program Files")) / "Google/Chrome/Application/chrome.exe"))
    for c in cand:
        if c and Path(c).exists():
            return c
    return None


# ------------------------------------------------------------------ init

def cmd_init(args):
    kind = {"deck": core.init_deck, "canvas": core.init_canvas, "system": core.init_design_system}[args.kind]
    kind(args.dir)
    return 0


# ------------------------------------------------------------------ check

def cmd_check(args):
    kind = core.detect_type(args.dir)
    if kind is None:
        msg = "cannot detect type: directory has no deck.json / canvas.json / design-system.json"
        if args.json:
            print(json.dumps({"type": None, "ok": False, "problems": [msg], "warnings": []}))
        else:
            core.print_err(msg)
        return 1
    fn = {"slides": core.validate_slides, "design": core.validate_design, "design-system": core.validate_design_system}[kind]

    if args.json:
        # validators print their own human banner; keep stdout pure JSON
        import contextlib, io
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            problems, warnings = fn(args.dir)
        print(json.dumps({"type": kind, "ok": not problems, "dir": str(args.dir),
                          "problems": problems, "warnings": warnings},
                         ensure_ascii=False, indent=2))
        return 0 if not problems else 1

    problems, warnings = fn(args.dir)
    print()
    for w in warnings:
        core.print_warn(w)
    if problems:
        for p in problems:
            core.print_err(p)
        print(f"\n{core.RED}{core.BOLD}Validation FAILED with {len(problems)} error(s) and {len(warnings)} warning(s).{RESET_ALL}\n")
        return 1
    core.print_ok(f"{core.BOLD}Validation PASSED with 0 error(s) ({len(warnings)} warning(s)).{RESET_ALL}\n")
    return 0


RESET_ALL = "\033[0m"


# ------------------------------------------------------------------ build

def cmd_build(args):
    if args.what == "player":
        return core.build_player(args.dir) or 0
    return core.build_tokens(args.dir) or 0


# ------------------------------------------------------------------ serve

def cmd_serve(args):
    handler = functools_partial_directory_handler(args.dir)
    port = args.port
    with socketserver.ThreadingTCPServer(("127.0.0.1", port), handler) as httpd:
        url = f"http://127.0.0.1:{port}"
        print(f"{core.BOLD}{core.CYAN}OpenDesignKit preview server{RESET_ALL}")
        print(f"  serving: {Path(args.dir).resolve()}")
        print(f"  url:     {url}  (Ctrl-C 停止)")
        print(f"  提示:    画板通过 {url}/Main.dc.html 访问时 dc-import 子组件可用")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nbye")
    return 0


def functools_partial_directory_handler(root):
    root_path = Path(root).resolve()

    class _H(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=str(root_path), **kw)

        def log_message(self, fmt, *log_args):  # quieter
            pass

    return _H


# ------------------------------------------------------------------ export-pdf

def cmd_export_pdf(args):
    chrome = _chrome()
    if not chrome:
        core.print_err("未找到 Chrome/Chromium。可设置环境变量 CHROME_BIN 指向可执行文件。")
        return 1
    deck = Path(args.dir)
    deck_json = json.loads((deck / "deck.json").read_text(encoding="utf-8"))
    order = deck_json.get("order", [])
    out_dir = Path(args.out) if args.out else deck / "export"
    out_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="odk-print-") as tmp:
        tmp_path = Path(tmp)
        for i, slide_id in enumerate(order):
            wrapper = tmp_path / f"s{i}.html"
            abs_slide = (deck / "slides" / f"{slide_id}.html").resolve()
            wrapper.write_text(
                "<!doctype html><html><head><meta charset='utf-8'><style>"
                "@page { size: 1920px 1080px; margin: 0; }"
                "html,body{margin:0;padding:0;overflow:hidden}"
                "iframe{border:0;width:1920px;height:1080px;display:block}"
                "</style></head><body>"
                f"<iframe src='file://{abs_slide}'></iframe></body></html>",
                encoding="utf-8",
            )
            pdf_path = out_dir / f"{i + 1:02d}-{slide_id}.pdf"
            r = subprocess.run([
                chrome, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                f"--print-to-pdf={pdf_path}", wrapper.resolve().as_uri(),
            ], capture_output=True, text=True, timeout=120)
            if r.returncode != 0 or not pdf_path.exists():
                core.print_err(f"导出失败 {slide_id}: {r.stderr[:200]}")
                return 1
            core.print_ok(f"已导出 {pdf_path.name}")
    print(f"\n{len(order)} 页 PDF 已输出到 {out_dir}")
    return 0


# ------------------------------------------------------------------ parser

def build_parser():
    p = argparse.ArgumentParser(prog="odk", description="OpenDesignKit CLI")
    p.add_argument("--version", action="version", version=f"odk {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="scaffold deck / canvas / design-system")
    p_init.add_argument("kind", choices=["deck", "canvas", "system"])
    p_init.add_argument("dir")
    p_init.set_defaults(func=cmd_init)

    p_check = sub.add_parser("check", help="validate (auto-detects format)")
    p_check.add_argument("dir")
    p_check.add_argument("--json", action="store_true", help="machine-readable output")
    p_check.set_defaults(func=cmd_check)

    for legacy, fn in (("check-slides", core.validate_slides),
                       ("check-design", core.validate_design),
                       ("check-design-system", core.validate_design_system)):
        sp = sub.add_parser(legacy, help="(legacy alias) validate one format")
        sp.add_argument("dir")
        sp.set_defaults(func=lambda a, f=fn: _legacy_check(a, f))

    p_build = sub.add_parser("build", help="build player / tokens")
    p_build.add_argument("what", choices=["player", "tokens"])
    p_build.add_argument("dir")
    p_build.set_defaults(func=cmd_build)

    p_serve = sub.add_parser("serve", help="local preview server (enables dc-import)")
    p_serve.add_argument("dir")
    p_serve.add_argument("--port", type=int, default=8620)
    p_serve.set_defaults(func=cmd_serve)

    p_pdf = sub.add_parser("export-pdf", help="export each slide as 16:9 PDF")
    p_pdf.add_argument("dir")
    p_pdf.add_argument("--out", default=None, help="output dir (default <deck>/export/)")
    p_pdf.set_defaults(func=cmd_export_pdf)

    return p


def _legacy_check(args, fn):
    problems, warnings = fn(args.dir)
    print()
    for w in warnings:
        core.print_warn(w)
    if problems:
        for p in problems:
            core.print_err(p)
        print(f"\n{core.RED}{core.BOLD}Validation FAILED with {len(problems)} error(s) and {len(warnings)} warning(s).{RESET_ALL}\n")
        return 1
    core.print_ok(f"{core.BOLD}Validation PASSED with 0 error(s) ({len(warnings)} warning(s)).{RESET_ALL}\n")
    return 0


def main(argv=None):
    args = build_parser().parse_args(argv)
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
