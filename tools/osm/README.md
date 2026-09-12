# Offline OSM PBF importer

This optional, local-only Python tool turns a PBF that **you obtain yourself** into a GLOBAL NAV graph. It never downloads data.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r tools/osm/requirements.txt
python tools/osm/import_osm.py --input .\uzbekistan-latest.osm.pbf --output .\public\data\roads\uzbekistan.osm.json --region Uzbekistan
python tools/osm/import_osm.py --validate .\public\data\roads\uzbekistan.osm.json
```

Use a local PBF source such as a regional OSM extract provider, place it anywhere outside Git, then update `public/data/manifest.json` so the `roads` dataset path points at generated JSON and has `datasetType: "osm"`. Copy the same manifest/data into `data/` for source tracking (but do not commit a production PBF/graph unless licensing and repository size permit it).

The importer filters motor-vehicle highway classes, preserves `oneway` including `-1`, uses valid OSM `maxspeed` (`km/h` and `mph`) before documented class defaults, calculates every edge distance along geometry, splits at junctions and retains intermediate shape points in each edge geometry. `--validate` prints node/edge, connected-component, one-way, speed and bounds-derived metadata; a validation failure exits non-zero.
