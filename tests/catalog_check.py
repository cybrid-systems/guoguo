#!/usr/bin/env python3
"""Course catalog stays aligned with the pages it points at. No Aura required."""

import json
import re
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
catalog_path = root / "courses" / "catalog.json"
id_re = re.compile(r"^[a-z][a-z0-9-]{0,31}$")
href_re = re.compile(r"^/[a-z0-9][a-z0-9-]*\.html$")
doc_re = re.compile(r"^docs/[a-z0-9][a-z0-9.-]*\.md$")
required = ("id", "title", "summary", "href", "doc", "status")


def fail(msg):
    raise SystemExit(msg)


def main():
    try:
        data = json.loads(catalog_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as err:
        fail(f"courses/catalog.json: {err}")
    courses = data.get("courses") if isinstance(data, dict) else None
    if not isinstance(courses, list) or not courses:
        fail("courses/catalog.json needs a non-empty courses list")
    seen = set()
    for course in courses:
        if not isinstance(course, dict):
            fail(f"course entry is not an object: {course!r}")
        missing = [key for key in required if key not in course]
        if missing:
            fail(f"{course.get('id', '?')} missing {missing}")
        cid = course["id"]
        if not isinstance(cid, str) or not id_re.match(cid):
            fail(f"bad id: {cid!r}")
        if cid in seen:
            fail(f"duplicate id: {cid}")
        seen.add(cid)
        for key in ("title", "summary"):
            text = course[key]
            if not isinstance(text, str) or not text.strip():
                fail(f"{cid} needs a {key}")
        if len(course["summary"]) > 200:
            fail(f"{cid} summary is too long")
        if course["status"] not in ("open", "soon"):
            fail(f"{cid} status must be open or soon")
        href = course["href"]
        if href != "/" and (not isinstance(href, str) or not href_re.match(href)):
            fail(f"{cid} href must be / or /name.html, got {href!r}")
        doc = course["doc"]
        if not isinstance(doc, str) or not doc_re.match(doc) or not (root / doc).is_file():
            fail(f"{cid} doc is missing: {doc}")
        if course["status"] != "open":
            if href == "/":
                fail(f"{cid} is not open but owns /")
            continue
        if href == "/":
            page = root / "web" / "index.html"
        else:
            page = root / "web" / href[1:]
        if not page.is_file():
            fail(f"{cid} page is missing: {page.relative_to(root)}")
        html = page.read_text(encoding="utf-8")
        needle = f'data-course="{cid}"'
        if needle not in html:
            fail(f"{page.relative_to(root)} must mark {needle}")
        if 'id="course-bar"' not in html or "/course-bar.js" not in html:
            fail(f"{page.relative_to(root)} needs the course bar")
    listing = (root / "web" / "courses.html").read_text(encoding="utf-8")
    if 'id="catalog"' not in listing or "/catalog.js" not in listing:
        fail("web/courses.html must render the catalog")
    bar = (root / "web" / "course-bar.js").read_text(encoding="utf-8")
    if "/catalog.json" not in bar:
        fail("web/course-bar.js must read /catalog.json")
    serve = (root / "aura" / "serve.aura").read_text(encoding="utf-8")
    if '"/catalog.json"' not in serve or "serve:static" not in serve:
        fail("aura/serve.aura must serve the catalog and web files")
    print("CATALOG_OK")


if __name__ == "__main__":
    sys.exit(main())
