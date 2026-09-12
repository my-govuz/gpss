# GLOBAL NAV

## Overview

GLOBAL NAV is an **offline-first 3D navigation workstation**. It runs a local React/Three.js globe with local place search, browser GPS, globe raycasting, and exact great-circle routing. It makes no runtime request to a map, geocoder, directions service, CDN, or remote font.

## Features

- WebGL Earth with procedural day/night materials, atmosphere, starfield, mouse orbit and zoom.
- Cinematic camera focus, START/DESTINATION markers, raycast point selection, and GPS error handling.
- Local, ranked autocomplete with coordinates, aliases, case-insensitive Cyrillic/Latin input, transliterations, fuzzy matching, and locally persisted recent searches.
- Uzbek cities (including Tashkent, Samarkand, Bukhara, Khiva, Fergana and more), selected global cities, regions, countries, and airports.
- Exact Haversine distance, initial/final bearing, anti-meridian-aware great-circle interpolation, and visibly labelled **GEODESIC ROUTE** fallback.
- A local A* `RoadRouter` and directed road graph format for genuine offline road routing after an appropriate graph is installed.
- PWA manifest and same-origin application-shell cache.

## Architecture

```text
Local place data → Local geocoder → Zustand navigation state → Routing engine → Three.js globe
                                      ├─ GeodesicRouter (always available)
                                      └─ RoadRouter / local road graph (optional)
```

- `src/globe`: WebGL renderer, spherical conversion, selection and route/marker visualization.
- `src/geocoding`: local parser, ranker and browser-local recents.
- `src/routing`: geodesic math, `RoutingEngine`, and A* `RoadRouter`.
- `src/data`: compact bundled gazetteer; large data belongs in `data/` rather than React components.
- `data/manifest.json`: installed-data status displayed by the application.

## Requirements

Node.js 20 LTS or newer and npm are required. A WebGL-capable browser is required for the globe. No external service account or API key is required.

## Installation

In Windows PowerShell, macOS Terminal, or Linux shell:

```text
npm install
npm run dev
```

Open the local Vite URL shown in the terminal. Dependencies are installed only during setup; application runtime uses only local assets and browser APIs.

## Development, build and testing

```text
npm run dev
npm run typecheck
npm run build
npm test
npm run preview -- --host 127.0.0.1
```

`typecheck` is the TypeScript-only gate. `build` runs typecheck then creates `dist`. No Unix-only command is required.

## Offline mode and PWA

The service worker caches same-origin app-shell resources only. It never caches or calls external APIs. The app reports **OFFLINE READY** because the shipped globe, search, selection and geodesic operations have no network dependency. It reports the road network truthfully as **NOT INSTALLED** unless a local graph is explicitly integrated.

## Local geocoder

Enter a city, airport, country, alias, transliteration, or `latitude, longitude`. Search is local and supports examples including `Ташкент`, `Tashkent`, `Toshkent`, `Toshkent shahri`, `Tash`, `Tashknet`, and `41.3111, 69.2797`. Ranking is exact name/alias, prefix, substring, then bounded edit-distance, with local importance as a tie-breaker. Arrow keys select suggestions; Enter chooses and Escape closes them. Recent choices are retained in `localStorage` on the current device.

This is a curated starter gazetteer, **not** a claim of world-complete offline geocoding.

## GPS

**LOCATE ME** uses only `navigator.geolocation`. Coordinates remain in browser memory and are never sent to a server. Permission denial, unavailable positioning, timeouts, and unsupported browsers present an in-app message; manual globe selection remains available.

## Geodesic routing

Without road data, GLOBAL NAV builds a **GEODESIC ROUTE**. Its distance is a great-circle surface distance, and the displayed bearing is calculated locally. It is not labelled as a driving route and its displayed duration is an aerial-reference estimate only.

## Road routing

`src/routing/RoadRouter.ts` is a genuine in-memory A* router. It snaps endpoints to nearest local nodes, honours directed edges and one-way restrictions, uses travel-time cost with a Haversine/max-speed admissible heuristic, reconstructs geometry, and returns `mode: 'road'` only after an actual graph returned a path. It is deliberately not wired to the starter UI because no road graph is installed.

For production-scale graphs, load chunks and execute nearest-node/A* work in a Web Worker before calling `RoutingEngine`; do not synchronously parse a worldwide graph in the renderer thread.

## Road dataset and data format

Place road data beneath `data/roads/`. The exact JSON schema, directed-edge rules, and validation requirements are in [`data/roads/README.md`](data/roads/README.md). An importer can transform local OpenStreetMap PBF extracts into that format. The repository includes a clearly labelled development/demo network and does not download OSM data. Until a validated local dataset is loaded, the only route is the clearly labelled geodesic fallback.

## PWA, performance and accessibility

The renderer creates one scene and renderer lifecycle, caps pixel ratio at 2, updates route geometry only when endpoints/route change, and releases renderer/controls on unmount. Search has semantic listbox markup, keyboard controls, visible focus styling and reduced-motion CSS handling. The layout prioritizes desktop and condenses controls at narrow widths.

## Troubleshooting

- **GPS unavailable:** grant browser location permission, use HTTPS/localhost where required by the browser, or select manually.
- **WebGL unavailable:** enable hardware acceleration or use a WebGL-capable browser.
- **No local search result:** use coordinates or select a point; the starter gazetteer is intentionally limited.
- **No road route:** install and validate a local graph; this is expected in the starter dataset.
- **Install fails with HTTP 403:** check organization proxy/registry policy. The project uses pinned, compatible npm versions and has no project-level registry override.

## Known limitations

The bundled data does not contain a worldwide road graph, raster Earth textures, or a complete global gazetteer. Consequently, road navigation is **not installed** in the starter package. All base functions remain operational offline through the local geocoder and geodesic fallback.

## Demo road network

The bundled `public/data/roads/uzbekistan-demo.json` is a **development/demo dataset and is not a complete road network**. Its synthetic corridors are anchored around Tashkent, Jizzakh and Samarkand exclusively to exercise local loading, validation, snapping, directed edges, different speeds/classes, worker A*, geometry and the ROAD ROUTE UI. It must not be used for travel.

## Production road dataset and OSM import

A production deployment replaces that local JSON path with a validated regional OSM-derived graph; no UI, globe or routing API rewrite is required. See `tools/README.md` for the offline PBF→graph pipeline and class/one-way rules. For large graphs, retain the worker protocol and use region chunks or compact binary/typed-array storage.

## Real OSM offline-road workflow

1. Obtain an Uzbekistan `.osm.pbf` from a source of your choice and keep it local; GLOBAL NAV does not download it.
2. In Windows PowerShell create/activate a virtual environment and install `tools/osm/requirements.txt`.
3. Run `python tools/osm/import_osm.py --input .\uzbekistan-latest.osm.pbf --output .\public\data\roads\uzbekistan.osm.json --region Uzbekistan`.
4. Run `python tools/osm/import_osm.py --validate .\public\data\roads\uzbekistan.osm.json`; it reports nodes, edges, components, one-way edges and speed limits.
5. Set the local road entry in both manifests to the generated file and mark its dataset type `osm`. Rebuild and run normally; the worker/loader/router API remains unchanged.

The importer is strictly local, filters automobile-appropriate highway types, retains geometry, calculates segment distances on that geometry, preserves one-way direction (including `-1`), and uses OSM `maxspeed` before documented class defaults. No production OSM dataset is shipped in this repository.
