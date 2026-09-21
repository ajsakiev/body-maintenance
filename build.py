#!/usr/bin/env python3
"""Bake manifest.json and every content/*.md file into index.html.

The site normally fetches its content at runtime, which browsers block when the
page is opened directly from disk (file://). This script embeds everything into
a <script id="siteData"> block so index.html works as a standalone file you can
double-click.

Run it after editing any markdown file or manifest.json:

    python3 build.py
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent
INDEX = ROOT / "index.html"
MANIFEST = ROOT / "manifest.json"

START = "<!-- BUILD:DATA:START -->"
END = "<!-- BUILD:DATA:END -->"


def collect_files(manifest):
    """Walk the manifest's three levels and return every referenced file path."""
    files = []
    for section in manifest["sections"]:
        for node in [section] + section.get("children", []):
            if node.get("file"):
                files.append(node["file"])
            for child in node.get("children", []):
                if child.get("file"):
                    files.append(child["file"])
    # dedupe, keep order
    return list(dict.fromkeys(files))


def main():
    manifest = json.loads(MANIFEST.read_text())

    pages = {}
    missing = []
    for rel in collect_files(manifest):
        path = ROOT / rel
        if path.exists():
            pages[rel] = path.read_text()
        else:
            missing.append(rel)

    orphans = sorted(
        str(p.relative_to(ROOT))
        for p in ROOT.glob("content/**/*.md")
        if str(p.relative_to(ROOT)) not in pages
    )

    payload = json.dumps({"manifest": manifest, "pages": pages}, ensure_ascii=False)
    # Keep any "</script>" inside the markdown from closing the tag early.
    payload = payload.replace("<", "\\u003c")

    block = f'{START}\n<script id="siteData" type="application/json">{payload}</script>\n{END}'

    html = INDEX.read_text()
    pattern = re.compile(re.escape(START) + ".*?" + re.escape(END), re.DOTALL)
    if not pattern.search(html):
        sys.exit(f"Could not find {START} ... {END} markers in index.html")
    INDEX.write_text(pattern.sub(lambda _: block, html))

    size_kb = INDEX.stat().st_size / 1024
    print(f"Baked {len(pages)} pages into index.html ({size_kb:.0f} KB)")
    for rel in missing:
        print(f"  MISSING (in manifest, no file): {rel}")
    for rel in orphans:
        print(f"  ORPHAN (file exists, not in manifest): {rel}")


if __name__ == "__main__":
    main()
