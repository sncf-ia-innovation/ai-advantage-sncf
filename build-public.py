#!/usr/bin/env python3
"""Build the public GitHub Pages version (docs/) from the full local page.

The full page (index.html, kept only on Alex's Mac) has the to-do list, contacts and
site logistics. The public page keeps the programme, the planning, the venue and the 3D.
Run: python3 build-public.py
"""
import re
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "index.html"
OUT = HERE / "docs"
# Venue published on Alex's decision (29/10): drawn textures only, no photos or names inside.
MODELS = ["kit-google.glb", "lieu-574.glb", "mobilier-574.glb", "disposition-574.json", "disposition-validee.json"]
# The only e-mail address allowed online: where visitors send their 3D layout.
ALLOWED_EMAILS = {"alexandre.cormeraie@sncf.fr"}


def drop(html, pattern, what):
    new, n = re.subn(pattern, "", html, flags=re.S)
    if n == 0:
        raise SystemExit(f"build-public: could not find {what}; check index.html")
    return new


def main():
    html = SRC.read_text(encoding="utf-8")
    # To-do section and its script (tasks name people and site security steps).
    html = drop(html, r'<section id="etapes">.*?</section>\s*', "the to-do section")
    html = drop(html, r'<section id="google-qa">.*?</section>\s*', "the Google Q&A section")
    html = drop(html, r'<script>\s*// ── Google Q&A.*?</script>\s*', "the Google Q&A script")
    html = drop(html, r'<script>\s*// ── To-do.*?</script>\s*', "the to-do script")
    # Logistics card: delivery dock, service lift, overnight storage.
    html = drop(html, r'\s*<div class="card"><span class="tag" data-i18n="e4_tag">.*?</div>(?=\s*</div>\s*</div>\s*</section>)',
                "the logistics card")
    # Public page = 3D + calendar only (Alex, 29/10): drop the content themes and the on-site cards,
    # then order the sections 3D, planning, principle, right under the header.
    html = drop(html, r'<section id="axes">.*?</section>\s*', "the content themes section")
    html = drop(html, r'<section id="espaces">.*?</section>\s*', "the on-site section")
    blocks = {}
    for sid in ("plan3d", "planning", "principe"):
        m = re.search(r'<section id="%s">.*?</section>\s*' % sid, html, flags=re.S)
        if not m:
            raise SystemExit(f"build-public: section {sid} not found")
        blocks[sid] = m.group(0)
        html = html.replace(m.group(0), "", 1)
    html = html.replace("<main>", "<main>\n" + blocks["plan3d"] + blocks["planning"] + blocks["principe"], 1)
    # Lets the page show the "not connected / send your changes" notices.
    html = html.replace('<html lang="fr">', '<html lang="fr" data-public="1">', 1)
    # Their texts in the FR/EN tables too: hidden, but readable in the page source.
    html = re.sub(r'\b(?:t_\w+|g_(?:google|site|guests|other)|e4_\w+|todo_\w+|contacts):"(?:[^"\\]|\\.)*",?[ \t]*', "", html)
    for word in ("Sylvie", "quai", "Laurent", "Damien"):
        if word in html:
            raise SystemExit(f"build-public: '{word}' is still in the page; stopping")
    # Safety net: nothing that looks like an e-mail address may go online.
    emails = set(re.findall(r"[\w.+-]+@[A-Za-z][\w-]*\.[A-Za-z]{2,}", html)) - ALLOWED_EMAILS
    if emails:
        raise SystemExit(f"build-public: e-mail address(es) still in the page: {sorted(emails)}; stopping")

    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "3d").mkdir(parents=True)
    (OUT / "index.html").write_text(html, encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    for name in MODELS:
        src = HERE / "3d" / name
        if src.exists():
            shutil.copy2(src, OUT / "3d" / name)
    print("docs/ built:", sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file()))


if __name__ == "__main__":
    main()
