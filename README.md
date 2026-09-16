# RoadRakshak — demo control room (static site)

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
