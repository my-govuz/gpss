# Local road graph format

GLOBAL NAV does **not** ship a road network. A road graph is optional local data and must be installed deliberately. `RoadRouter` accepts JSON in this form:

```json
{"version":"1","nodes":[{"id":"n1","lat":41.3,"lon":69.2}],"edges":[{"from":"n1","to":"n2","distanceMeters":1200,"speedKph":50,"roadClass":"primary","oneway":true,"name":"Example road"}]}
```

Edges are directed. Add the reverse edge for bidirectional roads. `distanceMeters` and `speedKph` must be positive. A production importer may pre-process OSM PBF data into this format or a chunked equivalent; it must stay local and should run A* in a Web Worker. The application intentionally falls back to **GEODESIC ROUTE** until an installed graph is loaded; it never claims that fallback is a driving route.
