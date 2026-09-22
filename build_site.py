#!/usr/bin/env python3
"""Build the static copy of the RoadRakshak demo control room for GitHub Pages.

Reads ~/SIH/SIH/demo (never writes there), copies what the page needs into
this folder, and replaces the one thing that needed a server — the live
listing of violation/ — with a static violations.json.

    python build_site.py                 # source: ../SIH/demo
    python build_site.py --src /path/to/demo

Then: git add -A && git commit && git push
"""
import argparse, json, shutil, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
IMG_EXT = {".jpg", ".jpeg", ".png", ".webp"}          # same set serve.py lists
FILE_LIMIT = 100 * 1024 * 1024                        # GitHub hard limit per file
SITE_LIMIT = 1024 * 1024 * 1024                       # GitHub Pages soft limit

PATCHES = [
    # the only server call -> a static file written by this script
    ("fetch('api/violations')", "fetch('violations.json')"),
    # status messages must not point a visitor at build scripts
    ("'no images in demo/violation/ — run demo/build_demo.py'", "'no violation images on this site'"),
    ("'demo_data.json missing — run: python demo/build_demo.py'", "'site data missing'"),
    # public page says what it is
    ('<span class=sub id=camSub>4 of 8 feeds active</span></div>',
     '<span class=sub id=camSub>4 of 8 feeds active</span>\n'
     '      <span class=sub style="margin-left:auto">Demo · recorded footage · sample records</span></div>'),
]

NOTE_README = """# RoadRakshak — demo control room (static site)

A showcase copy of the RoadRakshak traffic control room, served by GitHub
Pages. Recorded footage from six camera positions in Greater Noida and a set of
sample violation records; nothing here is live detection.

Pages: Camera Wall · Detections · Violations (with plate re-entry and a
printable challan) · Analytics.

## Refreshing the site

The source is the `demo/` folder of the SIH repository. To change what shows:

1. Rename or add images in `demo/violation/` — the filename is the record:
   `<PLATE>__<VIOLATION>__<CAMERA>__<VEHICLE>.jpg`
2. `python build_site.py` here (copies files, rewrites `violations.json`)
3. `git add -A && git commit -m "update demo" && git push`

The GIS · Journey tab reads `journeys.json` (cameras with lat/lng, vehicles with
their camera hops, clip + time offset). Edit it in `demo/`, rebuild, push.
"""


def fourcc(path: Path) -> str:
    try:
        import cv2
        v = int(cv2.VideoCapture(str(path)).get(cv2.CAP_PROP_FOURCC))
        return "".join(chr((v >> (8 * i)) & 255) for i in range(4)).strip().lower()
    except Exception:
        return "?"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=str(HERE.parent / "SIH" / "demo"))
    a = ap.parse_args()
    src = Path(a.src).expanduser().resolve()
    if not (src / "index.html").exists():
        sys.exit(f"no demo at {src}")

    data = json.loads((src / "demo_data.json").read_text())
    videos = [src / c["video"] for c in data["cameras"] if c.get("video")]
    problems = []
    for v in videos:
        if not v.exists():
            problems.append(f"missing video {v.relative_to(src)}"); continue
        if fourcc(v) not in ("h264", "avc1"):
            problems.append(f"{v.name}: codec {fourcc(v)!r} — browsers need H.264")
        if v.stat().st_size > FILE_LIMIT:
            problems.append(f"{v.name}: {v.stat().st_size/1e6:.0f} MB exceeds GitHub's 100 MB file limit")
    if problems:
        sys.exit("\n".join(problems))

    # page files, patched
    html = (src / "index.html").read_text()
    for old, new in PATCHES:
        if old not in html:
            sys.exit(f"index.html no longer contains: {old[:50]!r}")
        html = html.replace(old, new, 1)
    (HERE / "index.html").write_text(html)
    shutil.copy2(src / "challan.html", HERE / "challan.html")
    shutil.copy2(src / "demo_data.json", HERE / "demo_data.json")

    # media
    (HERE / "media" / "videos").mkdir(parents=True, exist_ok=True)
    for v in videos:
        shutil.copy2(v, HERE / "media" / "videos" / v.name)
    vdir = HERE / "violation"
    vdir.mkdir(exist_ok=True)
    for old in vdir.iterdir():
        if old.suffix.lower() in IMG_EXT:
            old.unlink()
    names = sorted(p.name for p in (src / "violation").iterdir()
                   if p.is_file() and p.suffix.lower() in IMG_EXT)
    for n in names:
        shutil.copy2(src / "violation" / n, vdir / n)
    (HERE / "violations.json").write_text(json.dumps({"files": names}, indent=2))

    # GIS · journey: hand-edited json, vehicle photos, and any extra clips it references
    jpath = src / "journeys.json"
    if jpath.exists():
        shutil.copy2(jpath, HERE / "journeys.json")
        j = json.loads(jpath.read_text())
        jdir = HERE / "journeys"; jdir.mkdir(exist_ok=True)
        for old in jdir.glob("*"):
            if old.suffix.lower() in IMG_EXT: old.unlink()
        for v in j.get("vehicles", []):
            photo = src / v.get("photo", "")
            if v.get("photo") and photo.exists():
                (HERE / v["photo"]).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(photo, HERE / v["photo"])
            for h in v.get("hops", []):
                clip = src / h.get("video", "")
                if h.get("video") and clip.exists() and not (HERE / h["video"]).exists():
                    if clip.stat().st_size > FILE_LIMIT:
                        sys.exit(f"{clip.name}: exceeds GitHub's 100 MB file limit")
                    (HERE / h["video"]).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(clip, HERE / h["video"])

    (HERE / ".nojekyll").write_text("")
    (HERE / "README.md").write_text(NOTE_README)
    (HERE / ".gitignore").write_text(".DS_Store\n")

    total = 0
    for p in sorted(HERE.rglob("*")):
        if p.is_file() and ".git" not in p.parts:
            total += p.stat().st_size
            print(f"  {p.stat().st_size/1e6:6.1f} MB  {p.relative_to(HERE)}")
    print(f"\n{len(names)} violation image(s), {len(videos)} clip(s), {total/1e6:.0f} MB total")
    if total > SITE_LIMIT:
        sys.exit("site exceeds GitHub Pages' 1 GB limit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
