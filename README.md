# RoadRakshak — Control Room Demo

Showcase build: recorded clips from six Greater Noida cameras, sample violation
records, and a GIS vehicle-journey view. No AI, database or backend — it runs
from a laptop or from GitHub Pages.

```bash
.venv/bin/python demo/build_demo.py     # one-time: transcode clips, seed images
.venv/bin/python demo/serve.py          # http://localhost:8090
```

Live copy: https://devloper-404.github.io/RoadRakshak-Repo/

## Feature preview

On the first visit a short guided preview walks through the features one at a
time — the page it describes opens blurred behind it. **Next →** / **Skip
preview**, the dots underneath jump to any step and show how many remain, and
the arrow keys and Esc work too. It shows once per browser; reopen it with the
**▶ Tour** button in the header, or add `?tour` to the URL.

## Pages

| Page | What it does |
|---|---|
| **Camera Wall** | Four feed panels, any of the six cameras (Round-about, KP2 – Metro, Metro Merger, Metro Lane, Pari Chowk, Expo Mart) via the per-panel dropdown. Monitoring only — **no alerts here**. |
| **Detections** | Latest capture with the vehicle ringed, plate, camera, location; feed of everything prior. Fills as the clips play. |
| **Violations** | Records table with filters and search. **Re-enter plate** on any row. Click a row for evidence and actions. |
| **Analytics** | Worst location, totals, fine value, ranked bars by location and violation type. |
| **GIS · Journey** | Search a vehicle by plate / date / time / camera → its photo, its route across cameras on a real map, and each camera's footage at the moment it passed. **Replay** walks the route camera by camera. |

## Where the data comes from

- **Violations** — images in `demo/violation/`, named by plate:
  `<PLATE>__<VIOLATION>__<CAMERA>__<VEHICLE>.jpg`. Rename a file, reload.
- **Journeys** — `demo/journeys.json`: camera coordinates, vehicles, and their
  camera-to-camera hops (clip + the second the vehicle appears). Edit, reload.
- **Cameras** — `demo/demo_data.json`.

## Challans are generated, not sent

**Generate Challan** opens `challan.html` with the record filled in — a
printable A4 document an officer reviews and prints or saves as PDF. Nothing is
dispatched; the record moves to `CHALLAN GENERATED`.

## Violations covered

No Helmet · Triple Riding · Wrong Direction · Over Speeding.

## Publishing

The static site in `roadrakshak-demo/` is built from this folder:
`python build_site.py` there, commit, `git push site gh-pages`.

## For developers

**[DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)** — every file, camera settings,
adding videos, the violation and journey data formats, the GIS tab, publishing.

---

## This copy (GitHub Pages)

Served at https://devloper-404.github.io/RoadRakshak-Repo/ from the `gh-pages`
branch. It is generated from the `demo/` folder of the SIH repository — edit
there, then here:

```bash
python build_site.py          # copies files, patches index.html, writes violations.json
git add -A && git commit -m "update demo" && git push site gh-pages
```
