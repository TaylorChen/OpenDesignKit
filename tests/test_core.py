"""OpenDesignKit engine self-tests (stdlib unittest)."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from odk import core  # noqa: E402


def _mkdeck(title, notes=None, slides=None):
    d = Path(tempfile.mkdtemp())
    (d / "slides").mkdir()
    (d / "deck.json").write_text(json.dumps(
        {"v": 4, "title": title, "order": ["cover"], "cover": "cover"}), encoding="utf-8")
    body = '<section id="cover" style="width:1920px;height:1080px"></section>'
    if notes:
        body += f"<aside>{notes}</aside>"
    (d / "slides" / "cover.html").write_text(body, encoding="utf-8")
    for sid, html in (slides or {}).items():
        (d / "slides" / f"{sid}.html").write_text(html, encoding="utf-8")
    return d


class TestBuildPlayerInjection(unittest.TestCase):
    def test_script_close_cannot_escape(self):
        evil = '</script><img src=x onerror=alert(1)>'
        d = _mkdeck(evil)
        self.assertEqual(core.build_player(str(d)), 0)
        html = (d / "player.html").read_text(encoding="utf-8")
        tpl_count = (core.TEMPLATES / "player.html").read_text().count("</script>")
        self.assertEqual(html.count("</script>"), tpl_count, "script close count must match template")
        self.assertIn("<\\/script>", html)

    def test_html_comment_cannot_enter_escaped_state(self):
        d = _mkdeck("<!-- probe")
        self.assertEqual(core.build_player(str(d)), 0)
        html = (d / "player.html").read_text(encoding="utf-8")
        self.assertIn("<\\u0021--", html)
        self.assertNotIn("<!-- probe", html)

    def test_player_still_parses(self):
        d = _mkdeck("正常标题", notes="普通备注")
        self.assertEqual(core.build_player(str(d)), 0)
        html = (d / "player.html").read_text(encoding="utf-8")
        const = html.split("const DECK = ", 1)[1].split(";\n", 1)[0]
        data = json.loads(const)  # must be valid JSON after escapes
        self.assertEqual(data["title"], "正常标题")
        self.assertEqual(data["__notes__"]["cover"], "普通备注")


class TestDetectType(unittest.TestCase):
    def _detect(self, marker):
        d = Path(tempfile.mkdtemp())
        (d / marker).write_text("{}", encoding="utf-8")
        return core.detect_type(str(d))

    def test_all(self):
        self.assertEqual(self._detect("deck.json"), "slides")
        self.assertEqual(self._detect("canvas.json"), "design")
        self.assertEqual(self._detect("design-system.json"), "design-system")
        d = Path(tempfile.mkdtemp())
        self.assertIsNone(core.detect_type(str(d)))


class TestCompileTokens(unittest.TestCase):
    def test_self_alias_dropped(self):
        css, warns = core.compile_tokens({"color": {"tokens": [
            {"name": "a", "value": "{a}"}]}})
        self.assertNotIn("--a", css)
        self.assertTrue(any("alias" in w for w in warns))

    def test_ghost_alias_dropped(self):
        css, warns = core.compile_tokens({"color": {"tokens": [
            {"name": "a", "value": "{nope}"}]}})
        self.assertNotIn("--a", css)

    def test_valid_alias_resolves(self):
        css, _ = core.compile_tokens({"color": {"tokens": [
            {"name": "base", "value": "#faf9f5"},
            {"name": "ref", "value": "{base}"}]}})
        self.assertIn("--ref: var(--base);", css)

    def test_invalid_color_dropped(self):
        css, warns = core.compile_tokens({"color": {"tokens": [
            {"name": "bad", "value": "red"}]}})
        self.assertNotIn("--bad", css)
        self.assertTrue(warns)

    def test_themes(self):
        css, _ = core.compile_tokens({"color": {"themes": [{"id": "light"}, {"id": "dark"}],
                                                "tokens": [{"name": "bg", "value": {"light": "#ffffff", "dark": "#111111"}}]}})
        self.assertIn('[data-theme="dark"]', css)
        light_part = css.split('[data-theme="dark"]')[0]
        self.assertIn("#ffffff", light_part)
        self.assertIn("#111111", css.split('[data-theme="dark"]', 2)[1])


class TestValidatorsPositive(unittest.TestCase):
    def test_examples_still_pass(self):
        for sub, fn in (("demo-slides", core.validate_slides),
                        ("demo-design", core.validate_design),
                        ("demo-design-system", core.validate_design_system)):
            problems, _ = fn(str(REPO / "examples" / sub))
            self.assertEqual(problems, [], f"{sub} should have 0 problems")


if __name__ == "__main__":
    unittest.main()


class TestProbeServeRoot(unittest.TestCase):
    def _build(self):
        base = Path(tempfile.mkdtemp())
        (base / "pricing").mkdir()
        (base / "my-brand").mkdir()
        (base / "pricing" / "Pricing.dc.html").write_text(
            '<link rel="stylesheet" href="../my-brand/tokens.css">', encoding="utf-8")
        (base / "my-brand" / "tokens.css").write_text(":root{--a:#fff}", encoding="utf-8")
        return base

    def test_probe_finds_common_parent(self):
        base = self._build().resolve()
        root, notes = core.probe_serve_root(base / "pricing")
        self.assertEqual(root, base)
        self.assertTrue(any("向上探测" in n for n in notes))

    def test_no_refs_serves_target(self):
        base = Path(tempfile.mkdtemp()).resolve()
        (base / "solo.dc.html").write_text("<p>hi</p>", encoding="utf-8")
        root, notes = core.probe_serve_root(base)
        self.assertEqual(root, base)
        self.assertEqual(notes, [])

    def test_missing_ref_reported(self):
        base = self._build()
        (base / "pricing" / "Pricing.dc.html").write_text(
            '<link rel="stylesheet" href="../ghost/x.css">', encoding="utf-8")
        root, notes = core.probe_serve_root(base / "pricing")
        self.assertTrue(any("不存在" in n for n in notes))
