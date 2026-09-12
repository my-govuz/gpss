# Offline OSM import architecture

GLOBAL NAV never downloads OSM data. Prepare an extract locally, then run an importer outside the browser:

```text
OSM PBF → road-way filter → node table → directed edges → local graph JSON → data/roads/
```

Map `motorway`, `trunk`, `primary`, `secondary`, `tertiary`, `residential`, `service`, and `unclassified` to the graph road classes. Preserve OSM `oneway`; emit both directed edges only when a way is bidirectional. Prefer an OSM `maxspeed` value when present. If absent, importer defaults must be explicit in its generated metadata, not silently guessed by the browser router. Validate the resulting JSON with `validateRoadGraph` before deployment.

For 100k+ nodes, produce regional chunks and move from JSON objects to compact typed-array/binary chunks while retaining the `RoadGraph`/worker message API. Do not commit PBF extracts or production datasets to this repository.
