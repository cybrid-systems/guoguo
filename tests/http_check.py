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

frac_page = fetch("/fractions.html").decode("utf-8")
need("果果的分数课" in frac_page, "fraction page title")
need('data-course="fractions"' in frac_page, "fraction course id")
need('id="course-bar"' in frac_page, "fraction course bar")
need("/course-bar.js" in frac_page, "fraction course bar script")
need('id="source"' in frac_page, "fraction page missing source box")
need("双向预览" in frac_page, "fraction page missing preview")
need('id="work-block"' in frac_page, "fraction process")
need("先切成一样" in frac_page, "fraction process step")
need(any(
    c.get("id") == "fractions" and c.get("status") == "open" and c.get("href") == "/fractions.html"
    for c in listed
), catalog)

def post_to(path, cmd):
    return json.loads(fetch(path, cmd).decode("utf-8"))

frac = json.loads(fetch("/api/fractions/state").decode("utf-8"))
need(frac["ok"] is True, frac)
need(frac.get("lesson") == "fractions", frac.get("lesson"))
need(frac["num"] == 1 and frac["den"] == 2, frac)
need(frac["num2"] == 1 and frac["den2"] == 3, frac)
need(frac["quot"] == 0, frac.get("quot"))
need(frac["sumOk"] is True, frac.get("sumOk"))
need(frac["sumNum"] == 5 and frac["sumDen"] == 6, (frac.get("sumNum"), frac.get("sumDen")))
need(frac["diffOk"] is True, frac.get("diffOk"))
need(frac["diffNum"] == 1 and frac["diffDen"] == 6, (frac.get("diffNum"), frac.get("diffDen")))
need(frac["sameOk"] is True, frac.get("sameOk"))
need(frac["sameNum"] == 3 and frac["sameDen"] == 6 and frac["sameNum2"] == 2,
     (frac.get("sameNum"), frac.get("sameDen"), frac.get("sameNum2")))
need(len(frac["nodes"]) == 4, frac.get("nodes"))
frac_num = next(n for n in frac["nodes"] if n["name"] == "*num*")
need(frac_num["text"] == "1", frac_num)
need(isinstance(frac_num["literal"], int) and frac_num["literal"] >= 0, frac_num)

sub = post_to("/api/fractions", "sub")
need(sub["ok"] is True, sub.get("error"))
need(sub["num"] == 1 and sub["den"] == 2 and sub["num2"] == 1 and sub["den2"] == 3, sub)
need(sub["diffNum"] == 1 and sub["diffDen"] == 6, sub)
need(sub.get("mut", "") == "", sub.get("mut"))

too_big = post_to("/api/fractions", "take2 2")
need(too_big["ok"] is True, too_big.get("error"))
cannot = post_to("/api/fractions", "sub")
need(cannot["ok"] is False, "sub of a larger second bar should fail")
need(cannot["num"] == 1 and cannot["den"] == 2 and cannot["num2"] == 2 and cannot["den2"] == 3, cannot)
need(cannot.get("mut", "") == "", cannot.get("mut"))
need(cannot["sameOk"] is True and cannot["sameNum"] == 3 and cannot["sameNum2"] == 4, cannot)
need(cannot["diffOk"] is False, cannot.get("diffOk"))
restored = post_to("/api/fractions", "take2 1")
need(restored["ok"] is True and restored["num2"] == 1, restored)

cut = post_to("/api/fractions", "cut 4")
need(cut["ok"] is True, cut.get("error"))
need(cut["num"] == 1 and cut["den"] == 4, cut)
need(str(cut.get("mut", "")).startswith("replace-value #"), cut.get("mut"))
need(next(n for n in cut["nodes"] if n["name"] == "*num*")["literal"] == frac_num["literal"], cut["nodes"])

miss = post_to("/api/fractions", "take 9")
need(miss["ok"] is False, "take 9 should fail")
need(miss["num"] == 1 and miss["den"] == 4, miss)
need(miss.get("mut", "") == "", miss.get("mut"))

over = post_to("/api/fractions", "take 3")
need(over["ok"] is True and over["num"] == 3 and over["den"] == 4, over)
over2 = post_to("/api/fractions", "take2 2")
need(over2["num2"] == 2 and over2["den2"] == 3, over2)
added = post_to("/api/fractions", "add")
need(added["ok"] is True, added.get("error"))
need(added["num"] == 3 and added["den"] == 4 and added["num2"] == 2 and added["den2"] == 3, added)
need(added.get("mut", "") == "", added.get("mut"))
need(added["sumNum"] == 17 and added["sumDen"] == 12, added)
need(added["sumWhole"] == 1 and added["sumRest"] == 5, added)
need(added["sameNum"] == 9 and added["sameDen"] == 12 and added["sameNum2"] == 8, added)

one = post_to("/api/fractions", "take 1")
need(one["num"] == 1, one)
wide_a = post_to("/api/fractions", "cut 13")
need(wide_a["ok"] is True and wide_a["num"] == 1 and wide_a["den"] == 13, wide_a)
one2 = post_to("/api/fractions", "take2 1")
need(one2["num2"] == 1, one2)
wide_b = post_to("/api/fractions", "cut2 17")
need(wide_b["num"] == 1 and wide_b["den"] == 13 and wide_b["num2"] == 1 and wide_b["den2"] == 17, wide_b)
wide_add = post_to("/api/fractions", "add")
need(wide_add["ok"] is True, wide_add.get("error"))
need(wide_add["sumNum"] == 30 and wide_add["sumDen"] == 221, wide_add)
need(wide_add["sumWhole"] == 0 and wide_add["sumRest"] == 30, wide_add)
need(wide_add["sameOk"] is False and wide_add["sameDen"] == 221, wide_add)
need(wide_add["sameNum"] == 17 and wide_add["sameNum2"] == 13, wide_add)
need(wide_add.get("mut", "") == "", wide_add.get("mut"))
wide_same = post_to("/api/fractions", "same")
need(wide_same["ok"] is False and wide_same["den"] == 13 and wide_same["den2"] == 17, wide_same)

back = json.loads(fetch("/api/state").decode("utf-8"))
need(back["bits"] == "00000001", back.get("bits"))
need(back["dec"] == 1, back.get("dec"))
