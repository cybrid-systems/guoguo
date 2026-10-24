#!/usr/bin/env python3
"""Exercise the Aura ↔ HTML preview without a browser."""

import json
import sys
import urllib.error
import urllib.request

base = sys.argv[1]
live = sys.argv[2]


def fetch(path, data=None):
    req = urllib.request.Request(
        base + path,
        data=None if data is None else data.encode("utf-8"),
        method="GET" if data is None else "POST",
    )
    if data is not None:
        req.add_header("Content-Type", "text/plain; charset=utf-8")
    with urllib.request.urlopen(req, timeout=20) as res:
        body = res.read()
        claimed = res.headers.get("Content-Length")
        if claimed is not None and int(claimed) != len(body):
            raise SystemExit(f"{path}: Content-Length {claimed} but body is {len(body)} bytes")
        return body


def post(cmd):
    return json.loads(fetch("/api", cmd).decode("utf-8"))


def need(cond, msg):
    if not cond:
        raise SystemExit(msg)


page = fetch("/").decode("utf-8")
need("果果的开关课" in page, "page missing title")
need("计算机只懂开和关" in page, "page lost Chinese text")
need('id="source"' in page, "page missing Aura source box")
need("双向预览" in page, "page missing preview heading")
need("replace-value" in page, "page missing mutation wording")
need('id="nodes"' in page, "page missing node strip")
need('data-course="switches"' in page, "page missing course id")
need('id="course-bar"' in page, "page missing course bar")

catalog = json.loads(fetch("/catalog.json").decode("utf-8"))
listed = catalog.get("courses") or []
need(any(c.get("id") == "switches" and c.get("href") == "/" for c in listed), catalog)
courses_page = fetch("/courses.html").decode("utf-8")
need('id="catalog"' in courses_page, "courses page missing catalog mount")
bar = fetch("/course-bar.js")
need(b"/catalog.json" in bar, "course bar script")
try:
    urllib.request.urlopen(base + "/no-such-course.html", timeout=10)
    raise SystemExit("missing course page should 404")
except urllib.error.HTTPError as err:
    need(err.code == 404, f"missing course page status {err.code}")
try:
    urllib.request.urlopen(base + "/nested/secret.html", timeout=10)
    raise SystemExit("nested path should 404")
except urllib.error.HTTPError as err:
    need(err.code == 404, f"nested path status {err.code}")

try:
    urllib.request.urlopen(base + "/nope", timeout=10)
    raise SystemExit("expected 404")
except urllib.error.HTTPError as err:
    need(err.code == 404, f"expected 404, got {err.code}")

state = json.loads(fetch("/api/state").decode("utf-8"))
need(state["ok"] is True, "state not ok")
need(state["bits"] == "01011", state["bits"])
need(state["dec"] == 11, state)
need(state["hex"] == "0B", state["hex"])
need(state["oct"] == "13", state["oct"])
need(state["hexGrouped"] == "0 1011", state["hexGrouped"])
need(state["octGrouped"] == "01 011", state["octGrouped"])
need(state["color"] == "#FF0000", state["color"])
need(state["width"] == 5, state["width"])
need('(define *bits* "01011")' in state["source"], state["source"])
need(state["hexChunks"][1]["digit"] == "B", state["hexChunks"])
need(len(state["nodes"]) == 7, state.get("nodes"))
bits0 = next(n for n in state["nodes"] if n["name"] == "*bits*")
need(bits0["text"] == "01011", bits0)
need(bits0["changed"] is False, bits0)
need(isinstance(bits0["literal"], int) and bits0["literal"] >= 0, bits0)
need(isinstance(bits0["define"], int) and bits0["define"] >= 0, bits0)
lit = bits0["literal"]
defn = bits0["define"]

age = post("set dec 65")
need(age["ok"] is True, age.get("error"))
need(age["bits"] == "01000001", age["bits"])
need(age["dec"] == 65, age["dec"])
need(age["width"] == 8, age["width"])
need(age["hex"] == "41", age["hex"])
need(age["oct"] == "101", age["oct"])
need(age["letter"] == "A", age["letter"])
need(age["hexGrouped"] == "0100 0001", age["hexGrouped"])
need(age["octGrouped"] == "01 000 001", age["octGrouped"])
need(age["color"] == "#FF0000", age["color"])
need(str(age.get("mut", "")).startswith("replace-value #"), age.get("mut"))
need("*bits*" in age["mut"] and "*width*" in age["mut"], age["mut"])
need('(define *bits* "01000001")' in age["workspace"], age["workspace"])
age_bits = next(n for n in age["nodes"] if n["name"] == "*bits*")
age_width = next(n for n in age["nodes"] if n["name"] == "*width*")
age_lamp = next(n for n in age["nodes"] if n["name"] == "*lamp*")
need(age_bits["literal"] == lit and age_bits["define"] == defn, age_bits)
need(age_bits["text"] == "01000001" and age_bits["changed"] is True, age_bits)
need(age_width["text"] == "8" and age_width["changed"] is True, age_width)
need(age_lamp["changed"] is False, age_lamp)

saved = open(live, encoding="utf-8").read()
need('(define *bits* "01000001")' in saved, saved)

refused = post("set dec 999")
need(refused["ok"] is False, "999 should fail")
need(refused["dec"] == 65, refused["dec"])
need(refused.get("mut", "") == "", refused.get("mut"))
need(all(n["changed"] is False for n in refused["nodes"]), refused.get("nodes"))
need(next(n for n in refused["nodes"] if n["name"] == "*bits*")["literal"] == lit, refused["nodes"])
need("255" in refused["error"], refused["error"])

narrow = post("width 4")
need(narrow["ok"] is False, "65 should not fit in 4 cards")
need(narrow["dec"] == 65, narrow["dec"])

flipped = post("flip 0")
need(flipped["bits"] == "11000001", flipped["bits"])
need(flipped["dec"] == 193, flipped["dec"])

paint = post("color 00ff00")
need(paint["color"] == "#00FF00", paint["color"])
need(paint["dec"] == 193, "color must not change the number byte")
need(paint["green"] == 255, paint["green"])

heart = post("stamp heart")
need(heart["rows"][0] == "01100110", heart["rows"][0])
need(heart["rowHex"][0] == "66", heart["rowHex"])

back = post(heart["source"])
need(back["ok"] is True, back.get("error"))
need(back["dec"] == 193, back["dec"])
need(back["color"] == "#00FF00", back["color"])
need(back["rows"][0] == "01100110", back["rows"][0])

edited = back["source"].replace('(define *bits* "11000001")', '(define *bits* "00000001")', 1)
open(live, "w", encoding="utf-8").write(edited)
loaded = post("reload")
need(loaded["ok"] is True, loaded.get("error"))
need(loaded["bits"] == "00000001", loaded["bits"])
need(loaded["dec"] == 1, loaded["dec"])
loaded_bits = next(n for n in loaded["nodes"] if n["name"] == "*bits*")
need(loaded_bits["literal"] == lit, loaded_bits)
need(loaded_bits["text"] == "00000001" and loaded_bits["changed"] is True, loaded_bits)
