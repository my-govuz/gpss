import * as THREE from 'three'; import type { Location } from '../types';
export const RADIUS=2.35;
export function latLonToVector3(lat:number,lon:number,r=RADIUS){const phi=THREE.MathUtils.degToRad(90-lat),theta=THREE.MathUtils.degToRad(lon+180);return new THREE.Vector3(-r*Math.sin(phi)*Math.cos(theta),r*Math.cos(phi),r*Math.sin(phi)*Math.sin(theta));}
export function vector3ToLatLon(v:THREE.Vector3):{lat:number;lon:number}{const n=v.normalize();return{lat:THREE.MathUtils.radToDeg(Math.asin(n.y)),lon:((THREE.MathUtils.radToDeg(Math.atan2(n.z,-n.x))-180+540)%360)-180};}
export function locationVector(p:Location,r=RADIUS){return latLonToVector3(p.lat,p.lon,r);}
