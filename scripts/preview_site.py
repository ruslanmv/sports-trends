#!/usr/bin/env python3
"""Zero-dependency local preview of the /sports/ dashboard (no Ruby/Jekyll).

Resolves the Liquid {% include %} tags in sports/index.md against the real
includes, wraps them in the sports layout, and serves the page at /sports/ with
the real CSS/JS/JSON assets. Also supports a headless screenshot for QA.

    python scripts/preview_site.py                 # serve at http://127.0.0.1:4000/sports/
    python scripts/preview_site.py --screenshot    # write a full-page PNG
"""

from __future__ import annotations

import argparse
import re
import sys
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INCLUDES = ROOT / "_includes"
_INCLUDE_RE = re.compile(r"\{%\s*include\s+([\w./-]+)\s*%\}")
_FRONTMATTER_RE = re.compile(r"^---\n.*?\n---\n", re.DOTALL)


def resolve_includes(text: str, depth: int = 0) -> str:
    if depth > 10:
        return text
    def repl(m):
        inc = INCLUDES / m.group(1)
        return resolve_includes(inc.read_text(encoding="utf-8"), depth + 1) if inc.exists() else ""
    new = _INCLUDE_RE.sub(repl, text)
    return new if new == text else resolve_includes(new, depth + 1)


def render_page() -> str:
    body = _FRONTMATTER_RE.sub("", (ROOT / "sports" / "index.md").read_text(encoding="utf-8"))
    body = resolve_includes(body)
    nav = resolve_includes((INCLUDES / "sports" / "sports-nav.html").read_text(encoding="utf-8"))
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ruslan Magana Sports Intelligence</title>
<meta name="description" content="AI predictions, live results, and trending games updated every 30 minutes.">
<link rel="stylesheet" href="/assets/css/sports.css">
<link rel="stylesheet" href="/assets/css/sports-cards.css">
<link rel="stylesheet" href="/assets/css/sports-mobile.css">
</head>
<body class="sports-page">
{nav}
<main class="sports-shell">
{body}
</main>
<script src="/assets/js/sports-app.js" defer></script>
<script src="/assets/js/sports-live.js" defer></script>
<script src="/assets/js/sports-share.js" defer></script>
</body>
</html>"""


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/sports", "/sports/", "/sports/index.html"):
            html = render_page().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.end_headers()
            self.wfile.write(html)
            return
        return super().do_GET()

    def log_message(self, *args):  # quiet
        pass


def serve(host: str, port: int):
    handler = partial(Handler, directory=str(ROOT))
    httpd = ThreadingHTTPServer((host, port), handler)
    print(f"Serving sports dashboard at http://{host}:{port}/sports/  (Ctrl+C to stop)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.shutdown()


def screenshot(host: str, port: int, out: str):
    handler = partial(Handler, directory=str(ROOT))
    httpd = ThreadingHTTPServer((host, port), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    from playwright.sync_api import sync_playwright
    chromium = next(Path("/opt/pw-browsers").glob("chromium-*/chrome-linux/chrome"), None)
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=str(chromium) if chromium else None)
        pg = b.new_page(viewport={"width": 1440, "height": 1000}, device_scale_factor=2)
        pg.goto(f"http://{host}:{port}/sports/", wait_until="networkidle")
        pg.wait_for_timeout(600)
        pg.screenshot(path=out, full_page=True)
        b.close()
    httpd.shutdown()
    print("Wrote", out)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=4000)
    ap.add_argument("--screenshot", nargs="?", const="sports_preview.png", default=None)
    args = ap.parse_args()
    if args.screenshot:
        screenshot(args.host, args.port, args.screenshot)
    else:
        serve(args.host, args.port)


if __name__ == "__main__":
    main()
