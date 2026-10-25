# 安全政策

## 支持版本
最新一个 minor 版本（当前 0.1.x）。

## 报告漏洞
本项目产物包含**会在浏览器执行的 HTML/JS**（幻灯片、画板、播放器），注入类问题视为高危。
请不要公开 issue：使用 GitHub 的 **"Report a vulnerability"**（仓库 Security 标签页）私密报告，
或邮件联系维护者。72 小时内确认，修复后随 patch 版本发布并在 CHANGELOG 致谢。

## 已知安全设计
- `build-player` 对内联 JSON 做 `</script>` 与 `<!--` 转义（tests/test_core.py 覆盖）
- 画板/幻灯片内容应视为不可信输入：请勿在不信任来源的产物上点开外部链接
