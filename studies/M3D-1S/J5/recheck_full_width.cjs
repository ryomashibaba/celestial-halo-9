#!/usr/bin/env node
"use strict";
// M3D-1S/J5: conservative BOX-based full-deck-width overhead probe, not a full mobility simulation.
// Node.js 18+. Runs offline with built-in fs only; no install, network, or destructive writes.
// Usage: node recheck_full_width.cjs ../junction/junction_source.json junction_J5_source.json out.json
const fs = require("node:fs");
function audit(src) {
  const excluded = new Set([
    "walkable_public_connection", "shared_floor", "public_corridor",
    "vertical_transit_level", "station_lift_car", "walkway_surface",
    "walkable_node_landing", "transport_platform", "pedestrian_approach",
    "public_street", "public_plaza"
  ]);
  const blocks=src.objects.filter(o=>o.type==="box"&&!excluded.has(o.role));
  const results={};
  for(const edge of src.route.edges.filter(e=>e.mode==="walk")){
    const key=edge.from+"__"+edge.to,prefix="WALK_DECK_"+key+"_";
    const beams=src.objects.filter(o=>o.type==="beam"&&o.id.startsWith(prefix))
      .sort((a,b)=>Number(a.id.slice(prefix.length))-Number(b.id.slice(prefix.length)));
    const sections=[];
    for(const seg of beams){
      const a=seg.from,b=seg.to,dx=b[0]-a[0],dy=b[1]-a[1];
      const length=Math.hypot(dx,dy)||1,ux=dx/length,uy=dy/length,vx=-uy,vy=ux;
      const pathLen=Math.hypot(...a.map((x,i)=>b[i]-x));
      const samples=Math.max(1,Math.ceil(pathLen/2)),collisions=[];
      for(let i=0;i<=samples;i++){
        const t=i/samples,pt=a.map((x,k)=>x+(b[k]-x)*t);
        const heightMin=pt[2]+6.25,heightMax=heightMin+3;
        const rect=[];
        for(const sign of [-1,1])for(const along of [-1,1]){
          rect.push([pt[0]+vx*sign*(seg.width/2+.5)+ux*along,
                     pt[1]+vy*sign*(seg.width/2+.5)+uy*along]);
        }
        for(const o of blocks){
          if(o.c[2]-o.size[2]/2>heightMax||o.c[2]+o.size[2]/2<heightMin)continue;
          const corners=[
            [o.c[0]-o.size[0]/2,o.c[1]-o.size[1]/2],
            [o.c[0]-o.size[0]/2,o.c[1]+o.size[1]/2],
            [o.c[0]+o.size[0]/2,o.c[1]-o.size[1]/2],
            [o.c[0]+o.size[0]/2,o.c[1]+o.size[1]/2]
          ];
          const intersects=[[1,0],[0,1],[ux,uy],[vx,vy]].every(axis=>{
            const p=rect.map(v=>v[0]*axis[0]+v[1]*axis[1]);
            const q=corners.map(v=>v[0]*axis[0]+v[1]*axis[1]);
            return Math.max(...p)>=Math.min(...q)&&Math.max(...q)>=Math.min(...p);
          });
          if(intersects)collisions.push({t:+t.toFixed(4),object_id:o.id});
        }
      }
      sections.push({name:seg.id,length_m:+pathLen.toFixed(2),width_m:seg.width,
        headroom_violations:collisions.length,
        colliding_parts:[...new Set(collisions.map(c=>c.object_id))],
        examples:collisions.slice(0,5)});
    }
    results[key]={segment_count:sections.length,
      collision_event_count:sections.reduce((a,s)=>a+s.headroom_violations,0),
      segments:sections};
  }
  return results;
}
if(require.main===module){
  const [before,after,out]=process.argv.slice(2);
  if(!before||!after||!out)throw Error("usage: node recheck_full_width.cjs before.json after.json result.json");
  if(fs.existsSync(out))throw Error("Refuses to overwrite existing file");
  const a=audit(JSON.parse(fs.readFileSync(before,"utf8")));
  const b=audit(JSON.parse(fs.readFileSync(after,"utf8")));
  const result={schema:"m3d1s.j5.full_width_box_clearance.v1",
    method:"Actual deck segments, <=2m sample spacing; each cross section uses 20-25m full width + 0.5m margin, 1m longitudinal margin and 3m headroom starting 0.25m above deck top (beam centre+6m)",
    before:a,after:b,
    limitations:["BOX obstacles only; excludes other segment beams, taper volumes and floors/plazas",
      "Surface clearances do not prove supported continuous walking path or accessibility",
      "No visual aesthetics, Blender reimport, canonical coordinates, public building completion"]};
  fs.writeFileSync(out,JSON.stringify(result,null,2));
  console.log("Saved local headroom audit. Surface clearance is NOT a whole-city or walkability PASS.");
}
module.exports={audit};
