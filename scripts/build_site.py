#!/usr/bin/env python3
"""Build the Cousin Times static site from the daily newspaper HTML.

Source editions live in ~/clawd/newspaper/mic-times-YYYY-MM-DD.html.
Public output:
- index.html                         404-style placeholder at the domain root (no links)
- ct-6f30fc5c/index.html             latest edition at the private path
- ct-6f30fc5c/editions/YYYY-MM-DD.html permanent dated copy
- ct-6f30fc5c/archive.html           linked archive of all dated editions

Privacy: robots.txt disallows all crawlers, no sitemap is generated, every HTML page is forced to carry a noindex/nofollow/noarchive robots meta tag, and the paper lives behind an unguessable path. This is obscurity, not access control.
"""
from __future__ import annotations

import html
import re
import shutil
import sys
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path("/home/adrian/cousin-times")
SRC_DIR = Path("/home/adrian/clawd/newspaper")
PRIVATE_PREFIX = "ct-6f30fc5c"
PRIVATE_DIR = ROOT / PRIVATE_PREFIX
EDITIONS = PRIVATE_DIR / "editions"
NOINDEX_META = '<meta name="robots" content="noindex, nofollow, noarchive">'
FORBIDDEN = (
    "Irish Getaways",
    "Trails and Tales",
    "Feel Better Therapy",
    "IMAGE_PLACEHOLDER",
)
URL_RE = re.compile(r"https?://[^\s\"'<>]+")


def dublin_today() -> str:
    return datetime.now(ZoneInfo("Europe/Dublin")).strftime("%Y-%m-%d")


def clean_url(url: str) -> str:
    return url.rstrip(".,;:!?)]}")


def ensure_noindex(text: str) -> str:
    if 'name="robots"' in text:
        return re.sub(
            r'<meta name="robots" content="[^"]*">',
            NOINDEX_META,
            text,
            count=1,
        )
    viewport = '<meta name="viewport" content="width=device-width, initial-scale=1">'
    if viewport in text:
        return text.replace(viewport, viewport + "\n" + NOINDEX_META, 1)
    raise SystemExit("Refusing to publish: viewport meta tag not found for noindex insertion")


def validate_edition(text: str) -> None:
    for token in FORBIDDEN:
        if token in text:
            raise SystemExit(f"Refusing to publish: forbidden token present: {token}")
    if 'class="masthead"' not in text or "The Cousin Times" not in text:
        raise SystemExit("Refusing to publish: masthead/title check failed")

    urls = sorted({clean_url(u) for u in URL_RE.findall(text)})
    failures: list[str] = []
    for url in urls:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (CousinTimesBot)"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                if resp.status >= 400:
                    failures.append(f"{resp.status} {url}")
        except Exception as exc:  # noqa: BLE001 - publish gate should report any fetch failure
            failures.append(f"ERR {url} :: {exc}")
    if failures:
        raise SystemExit("Refusing to publish: external URL check failed\n" + "\n".join(failures))


def edition_title(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"<title>(.*?)</title>", text, flags=re.S | re.I)
    if match:
        return html.unescape(re.sub(r"\s+", " ", match.group(1))).strip()
    return f"The Cousin Times — {path.stem}"


def write_placeholder() -> None:
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{NOINDEX_META}
<title>404 — Not Found</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; min-height: 100vh; display: grid; place-items: center; background: #f4f4f4; color: #333; font-family: Georgia, serif; }}
  main {{ text-align: center; padding: 40px 24px; }}
  h1 {{ font-size: clamp(42px, 10vw, 84px); margin: 0 0 8px; }}
  p {{ margin: 0; color: #666; }}
</style>
</head>
<body>
<main>
  <h1>404</h1>
  <p>Nothing to see here.</p>
</main>
</body>
</html>
"""
    (ROOT / "index.html").write_text(page, encoding="utf-8")


def build_archive(entries: list[tuple[str, str]]) -> None:
    items = "\n".join(
        f'    <li><a href="editions/{date}.html"><span>{date}</span><strong>{html.escape(title)}</strong></a></li>'
        for date, title in entries
    )
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{NOINDEX_META}
<title>The Cousin Times — Archive</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Pirata+One&family=Playfair+Display:ital,wght@0,700;0,900&family=Lora:ital,wght@0,400;0,600&display=swap');
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: #e9e4d8; color: #191713; font-family: 'Lora', Georgia, serif; padding: 28px 18px 60px; }}
  main {{ width: min(920px, 100%); margin: 0 auto; background: #fbf8f1; border: 1px solid #cfc7b4; box-shadow: 0 2px 4px rgba(0,0,0,.12), 0 18px 50px rgba(0,0,0,.18); padding: 26px clamp(18px, 4vw, 42px) 34px; }}
  h1 {{ font-family: 'Pirata One', serif; font-weight: 400; text-align: center; font-size: clamp(38px, 9vw, 68px); line-height: 1; margin: 8px 0 6px; }}
  p.sub {{ text-align: center; text-transform: uppercase; letter-spacing: .22em; font-size: 12px; color: #4a453b; margin: 0 0 22px; }}
  hr {{ border: 0; border-top: 1px solid #191713; border-bottom: 3px double #191713; height: 4px; margin: 0 0 22px; }}
  ul {{ list-style: none; margin: 0; padding: 0; display: grid; gap: 12px; }}
  a {{ display: grid; gap: 3px; padding: 14px 16px; border: 1px solid #cfc7b4; background: #fffdf8; color: inherit; text-decoration: none; }}
  a:hover {{ border-color: #191713; }}
  span {{ font-size: 11px; letter-spacing: .18em; text-transform: uppercase; color: #7a2e1d; font-weight: 600; }}
  strong {{ font-family: 'Playfair Display', Georgia, serif; font-size: 20px; line-height: 1.25; }}
  .latest {{ margin: 0 0 18px; text-align: center; }}
  .latest a {{ display: inline-block; padding: 10px 14px; font-weight: 600; }}
</style>
</head>
<body>
<main>
  <h1>The Cousin Times</h1>
  <p class="sub">Daily Edition Archive</p>
  <hr>
  <p class="latest"><a href="./">Read the latest edition</a></p>
  <ul>
{items}
  </ul>
</main>
</body>
</html>
"""
    (PRIVATE_DIR / "archive.html").write_text(page, encoding="utf-8")


def remove_stale_public_paths() -> None:
    stale_archive = ROOT / "archive.html"
    if stale_archive.exists():
        stale_archive.unlink()
    stale_editions = ROOT / "editions"
    if stale_editions.exists():
        shutil.rmtree(stale_editions)


def main() -> None:
    date = sys.argv[1] if len(sys.argv) > 1 else dublin_today()
    src = SRC_DIR / f"mic-times-{date}.html"
    if not src.exists():
        raise SystemExit(f"Missing source edition: {src}")

    EDITIONS.mkdir(parents=True, exist_ok=True)
    text = ensure_noindex(src.read_text(encoding="utf-8"))
    validate_edition(text)

    dated = EDITIONS / f"{date}.html"
    dated.write_text(text, encoding="utf-8")
    (PRIVATE_DIR / "index.html").write_text(text, encoding="utf-8")

    entries = []
    for path in sorted(EDITIONS.glob("????-??-??.html"), reverse=True):
        entries.append((path.stem, edition_title(path)))
    build_archive(entries)
    remove_stale_public_paths()
    write_placeholder()
    print(f"Built Cousin Times site for {date}: {len(entries)} edition(s) archived at /{PRIVATE_PREFIX}/")


if __name__ == "__main__":
    main()
