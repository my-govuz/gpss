export type LocationKind='city'|'country'|'region'|'airport'|'coordinate'|'selected';
export interface Location { id:string; name:string; country:string; kind:LocationKind; lat:number; lon:number; aliases?:string[]; importance?:number; accuracy?:number; timestamp?:number }
export type RouteType='geodesic'|'road';
export interface RouteSegment { name:string; roadClass?:RoadClass; distanceMeters:number; durationSeconds:number }
export interface Route { points:Location[]; distanceKm:number; initialBearing:number; finalBearing:number; durationHours:number; mode:RouteType; segments?:RouteSegment[]; startSnapMeters?:number; destinationSnapMeters?:number; datasetType?:'demo'|'production' }
export type RoadClass='motorway'|'trunk'|'primary'|'secondary'|'tertiary'|'residential'|'service'|'unclassified';
export interface RoadNode { id:string; lat:number; lon:number }
export interface RoadEdge { from:string; to:string; distanceMeters:number; speedKph:number; roadClass:RoadClass; oneway?:boolean; name?:string; geometry?:[number,number][] }
export interface RoadGraph { version:string; region?:string; type?:'demo'|'production'; nodes:RoadNode[]; edges:RoadEdge[] }
export type SelectionMode='start'|'destination'|null; export type RouteStatus='idle'|'loading-road-network'|'building'|'ready'|'error';
