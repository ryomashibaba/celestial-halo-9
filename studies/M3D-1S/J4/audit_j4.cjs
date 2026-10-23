/* Reproducible J4 OBJ mesh intersection audit. Node.js 18+; no npm packages. */
"use strict";
const fs = require("node:fs");
const auditOBJ = function auditOBJ(text,design){
 const verts=[],objects=[];let current=null;
 for(const line of text.split(/\r?\n/)){
  if(line.startsWith("o ")){current={id:line.slice(2).trim(),triangles:[]};objects.push(current);}
  else if(line.startsWith("v ")){const v=line.slice(2).trim().split(/\s+/).map(Number);verts.push(v);}
  else if(line.startsWith("f ")){const ids=line.slice(2).trim().split(/\s+/).map(x=>+x.split("/")[0]);if(!current||ids.length!==3||ids.some(i=>i<1||i>verts.length))throw Error("Invalid OBJ face");current.triangles.push(ids.map(i=>verts[i-1]));}
 }
 const spec=new Map(design.objects.map(o=>[o.id,o]));
 for(const o of objects){
  const p=o.triangles.flat();
  o.min=[0,1,2].map(k=>Math.min(...p.map(v=>v[k])));o.max=[0,1,2].map(k=>Math.max(...p.map(v=>v[k])));
  o.role=spec.get(o.id)?.role||"UNKNOWN";o.type=spec.get(o.id)?.type||"UNKNOWN";
 }
 const sub=(a,b)=>[a[0]-b[0],a[1]-b[1],a[2]-b[2]];
 const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
 const dot=(a,b)=>a[0]*b[0]+a[1]*b[1]+a[2]*b[2];
 const overlap=(a,b,c,d)=>a.every((v,k)=>v<=d[k]&&b[k]>=c[k]);
 function hitBox(tri,mn,mx){
  const center=mn.map((a,i)=>(a+mx[i])/2), half=mn.map((a,i)=>(mx[i]-a)/2),vs=tri.map(v=>sub(v,center));
  const edges=[sub(vs[1],vs[0]),sub(vs[2],vs[1]),sub(vs[0],vs[2])];
  const ax=[[1,0,0],[0,1,0],[0,0,1],cross(edges[0],edges[1])];
  const bases=[[1,0,0],[0,1,0],[0,0,1]];
  for(const e of edges)for(const b of bases)ax.push(cross(e,b));
  for(const a of ax){
   if(dot(a,a)<1e-16)continue;
   const x=vs.map(v=>dot(a,v)),rad=dot(half,a.map(Math.abs));
   if(Math.min(...x)>rad+1e-7||Math.max(...x)<-rad-1e-7)return false;
  }
  return true;
 }
 function colliders(mn,mx){
  const result=[];
  for(const o of objects){
   if(!overlap(o.min,o.max,mn,mx))continue;
   let count=0;for(const tr of o.triangles)if(hitBox(tr,mn,mx))count++;
   if(count)result.push({id:o.id,role:o.role,type:o.type,intersected_triangles:count});
  }
  return result;
 }
 const rooms=[];
 for(const s of design.spaces){
  const box=(mn,mx)=>({min:mn,max:mx,intersecting:colliders(mn,mx)});
  rooms.push({space:s.id,full_room_inset_2m:box(s.min.map(v=>v+2),s.max.map(v=>v-2)),inspection_core_inset_1m:box(s.coremin.map(v=>v+1),s.coremax.map(v=>v-1))});
 }
 const nodes=new Map(design.route.nodes.map(n=>[n.id,n.p]));
 // The route body cube follows nominal station XY/Z. It is a conservative probe, not a full swept pedestrian capsule.
 const walks=[];
 for(const e of design.route.edges){
  if(e.mode!=="walk")continue;
  const a=nodes.get(e.from),b=nodes.get(e.to),visits=[];
  for(let i=0;i<=20;i++){
   const t=i/20,p=a.map((v,k)=>v+(b[k]-v)*t);
   const mn=[p[0]-1,p[1]-1,p[2]+1],mx=[p[0]+1,p[1]+1,p[2]+4];
   const hits=colliders(mn,mx).filter(h=>!["walkable_public_connection","shared_floor","public_corridor","vertical_transit_level","station_lift_car","walkway_surface"].includes(h.role));
   if(hits.length)visits.push({fraction:t,point:p.map(v=>Math.round(v*100)/100),hits:hits.slice(0,8)});
  }
  walks.push({from:e.from,to:e.to,centerline_probed:21,interfered_sample_count:visits.length,interference_witnesses:visits.slice(0,5)});
 }
 return {schema:"m3d1s.J4.mesh_sat_audit.v1",method:"OBJ triangles against inset room boxes using 13-axis SAT; 21 centerline 2x2x3m headroom boxes per declared pedestrian edge",geometry:{objects:objects.length,triangles:objects.reduce((s,o)=>s+o.triangles.length,0),vertices:verts.length,source_coverage:objects.filter(o=>spec.has(o.id)).length},rooms,route_centerline:walks,limits:["Triangle/box intersection of SURFACES only: boxes fully enclosed by solids can be misclassified clear; this is not volumetric Boolean.", "Room interiors have intended floors, seats and walls, so full-volume intersections may be legitimate; requires semantic review.", "Pedestrian probes measure nominal node coordinates, not an actual fitted walkable capsule or support geometry. No complete walkability proof.", "SAT counts do not imply manifold or full room functionality; Blender/Unreal import and human art review not done."]};
};
if (require.main === module) {
 const [obj,source,out] = process.argv.slice(2);
 if(!obj || !source || !out)throw new Error("Usage: node audit_j4.cjs model.obj junction_source.json result.json");
 const result=auditOBJ(fs.readFileSync(obj,"utf8"),JSON.parse(fs.readFileSync(source,"utf8")));
 if(fs.existsSync(out))throw Error("Refuse to overwrite existing output");
 fs.writeFileSync(out,JSON.stringify(result,null,2));
}
module.exports={auditOBJ};
