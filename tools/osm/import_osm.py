#!/usr/bin/env python3
"""Offline OSM PBF -> GLOBAL NAV road graph importer. Never downloads data."""
from __future__ import annotations
import argparse,json,math,sys
from collections import Counter,defaultdict,deque
from datetime import datetime,timezone
from pathlib import Path
try:
    import osmium
except ImportError:
    osmium=None
DRIVABLE={'motorway','motorway_link','trunk','trunk_link','primary','primary_link','secondary','secondary_link','tertiary','tertiary_link','unclassified','residential','living_street','service'}
CLASS={'motorway_link':'motorway','trunk_link':'trunk','primary_link':'primary','secondary_link':'secondary','tertiary_link':'tertiary','living_street':'residential'}
DEFAULT_SPEED={'motorway':110,'trunk':90,'primary':80,'secondary':70,'tertiary':60,'unclassified':50,'residential':35,'service':20}
def road_class(highway:str)->str:return CLASS.get(highway,highway)
def parse_speed(value:object,default:int)->int:
    if value is None:return default
    text=str(value).strip().lower(); number=''.join(c for c in text if c.isdigit() or c=='.')
    if not number:return default
    speed=float(number)
    if 'mph' in text:speed*=1.609344
    return max(1,round(speed))
def distance(a:tuple[float,float],b:tuple[float,float])->float:
    lat1,lon1=map(math.radians,a);lat2,lon2=map(math.radians,b);dlat=lat2-lat1;dlon=lon2-lon1
    h=math.sin(dlat/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 6371008.8*2*math.atan2(math.sqrt(h),math.sqrt(1-h))
def oneway(value:str|None)->int:return -1 if value=='-1' else 1 if str(value).lower() in {'yes','true','1'} else 0
def validate(graph:dict)->dict:
    nodes=graph.get('nodes');edges=graph.get('edges');assert isinstance(nodes,list) and isinstance(edges,list),'nodes and edges are required lists'
    ids=set();coords={}
    for n in nodes:
        assert isinstance(n.get('id'),str) and n['id'] not in ids,'duplicate/invalid node id';assert math.isfinite(n['lat']) and -90<=n['lat']<=90,'invalid latitude';assert math.isfinite(n['lon']) and -180<=n['lon']<=180,'invalid longitude';ids.add(n['id']);coords[n['id']]=(n['lat'],n['lon'])
    adjacency=defaultdict(set);oneway_edges=0
    for e in edges:
        assert e['from'] in ids and e['to'] in ids and e['from']!=e['to'],'invalid edge reference';assert math.isfinite(e['distanceMeters']) and e['distanceMeters']>0,'invalid distance';assert math.isfinite(e['speedKph']) and e['speedKph']>0,'invalid speed';assert len(e.get('geometry',[]))>=2,'missing geometry';adjacency[e['from']].add(e['to']);oneway_edges+=1 if e.get('oneway') else 0
    seen=set();components=0
    undirected=defaultdict(set)
    for a,targets in adjacency.items():
        for b in targets:undirected[a].add(b);undirected[b].add(a)
    for node in ids:
        if node in seen:continue
        components+=1;q=deque([node]);seen.add(node)
        while q:
            for nxt in undirected[q.popleft()]:
                if nxt not in seen:seen.add(nxt);q.append(nxt)
    return {'nodes':len(nodes),'edges':len(edges),'connectedComponents':components,'onewayEdges':oneway_edges,'minSpeedKph':min((e['speedKph'] for e in edges),default=0),'maxSpeedKph':max((e['speedKph'] for e in edges),default=0)}
class Reader(osmium.SimpleHandler if osmium else object):
    def __init__(self):super().__init__();self.nodes={};self.ways=[]
    def node(self,n):
        if n.location.valid():self.nodes[n.id]=(n.location.lat,n.location.lon)
    def way(self,w):
        highway=w.tags.get('highway')
        refs=[n.ref for n in w.nodes]
        if highway in DRIVABLE and len(refs)>1:self.ways.append((refs,dict(w.tags),highway))
def build(reader:Reader,region:str)->dict:
    degree=Counter(ref for refs,_,_ in reader.ways for ref in refs)
    out_nodes={};edges=[]
    def emit(ref):
        lat,lon=reader.nodes[ref];out_nodes[str(ref)]={'id':str(ref),'lat':lat,'lon':lon}
    for refs,tags,highway in reader.ways:
        if any(ref not in reader.nodes for ref in refs):continue
        splits=[0]+[i for i in range(1,len(refs)-1) if degree[refs[i]]>1]+[len(refs)-1]
        cls=road_class(highway);speed=parse_speed(tags.get('maxspeed'),DEFAULT_SPEED[cls]);direction=oneway(tags.get('oneway'))
        for first,last in zip(splits,splits[1:]):
            part=refs[first:last+1];geometry=[[reader.nodes[r][0],reader.nodes[r][1]] for r in part];meters=sum(distance(tuple(geometry[i]),tuple(geometry[i+1])) for i in range(len(geometry)-1));emit(part[0]);emit(part[-1])
            base={'distanceMeters':round(meters,2),'speedKph':speed,'roadClass':cls,'oneway':direction!=0,'geometry':geometry}
            if tags.get('name'):base['name']=tags['name']
            pairs=[(part[0],part[-1])] if direction==1 else [(part[-1],part[0])] if direction==-1 else [(part[0],part[-1]),(part[-1],part[0])]
            for start,end in pairs:edges.append({**base,'from':str(start),'to':str(end),'geometry':geometry if start==part[0] else list(reversed(geometry))})
    graph={'version':'1','region':region,'type':'production','source':'OpenStreetMap','createdAt':datetime.now(timezone.utc).isoformat(),'nodes':list(out_nodes.values()),'edges':edges};stats=validate(graph);graph['metadata']={**stats,'datasetType':'osm','bounds':bounds(graph['nodes'])};return graph
def bounds(nodes):
    return {'minLat':min((n['lat'] for n in nodes),default=0),'minLon':min((n['lon'] for n in nodes),default=0),'maxLat':max((n['lat'] for n in nodes),default=0),'maxLon':max((n['lon'] for n in nodes),default=0)}
def main():
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path);p.add_argument('--output',type=Path);p.add_argument('--region',default='Uzbekistan');p.add_argument('--validate',type=Path);p.add_argument('--stats',type=Path);args=p.parse_args()
    if args.validate:
        graph=json.loads(args.validate.read_text(encoding='utf8'));print(json.dumps(validate(graph),indent=2));return
    if args.stats:
        graph=json.loads(args.stats.read_text(encoding='utf8'));print(json.dumps(graph.get('metadata',validate(graph)),indent=2));return
    if not args.input or not args.output:p.error('--input and --output are required unless --validate/--stats is used')
    if osmium is None:sys.exit('Missing pyosmium. Install with: pip install -r tools/osm/requirements.txt')
    reader=Reader();reader.apply_file(str(args.input));graph=build(reader,args.region);args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(graph,separators=(',',':')),encoding='utf8');print(json.dumps(graph['metadata'],indent=2))
if __name__=='__main__':main()
