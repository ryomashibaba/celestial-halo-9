// R33-S27-D10. Pure ECMAScript; no imports, IO, network, Blender, or local automation.
// runD10() returns actual OBJ strings and verification data; caller controls saving.
// A method coupon, not a city/architecture generator or an artistic acceptance test.

function d10Experiment() {
  // Method coupon only. Explicit authored vertices; no city/form generator.
  // Coordinates: arbitrary local metres, Z up. Open surface, NOT a room/hull.
  const vertices = [
    [-48,-120,0],[-19,-58,8],[4,10,-4],[-12,84,5],[31,156,0],
    [-65,-108,74],[9,-45,96],[54,18,68],[18,93,114],[59,167,81],
    [-29,-126,166],[37,-60,201],[96,2,179],[67,87,226],[81,158,193],
    [-8,-94,251],[64,-24,303],[119,40,286],[82,122,334],[143,192,279]
  ];
  const faces=[];
  for(let r=0;r<3;r++) for(let c=0;c<4;c++) {
    const a=r*5+c,b=a+1,d=a+5,e=d+1;
    if((r+c)%2===0) faces.push([a,b,e],[a,e,d]); else faces.push([a,b,d],[b,e,d]);
  }
  const edgeSet=new Set();
  faces.forEach(f=>f.forEach((a,i)=>edgeSet.add([a,f[(i+1)%3]].sort((a,b)=>a-b).join(","))));
  const edges=[...edgeSet].map(s=>s.split(",").map(Number));
  const n=vertices.length, H=Array.from({length:n},()=>Array(n).fill(0));
  edges.forEach(([i,j])=>{H[i][i]++;H[j][j]++;H[i][j]--;H[j][i]--;});
  // Small displacement penalty makes the linear objective strictly convex.
  for(let i=0;i<n;i++) H[i][i]+=0.05;
  const unit=i=>Array.from({length:n},(_,j)=>+(i===j));
  // Two virtual attachment samples on authored patch, not a collision/volume model.
  const wA=Array(n).fill(0),wB=Array(n).fill(0);
  wA[6]=0.35;wA[7]=0.65;wB[11]=0.4;wB[12]=0.6;
  const dot=(a,b)=>a.reduce((s,x,i)=>s+x*b[i],0);
  const pins=[0,1,2,3,4,9,14,19];
  function linear(A,b) {
    const m=A.map((row,i)=>[...row,b[i]]),size=A.length;
    for(let k=0;k<size;k++){
      let pivot=k;for(let i=k+1;i<size;i++) if(Math.abs(m[i][k])>Math.abs(m[pivot][k]))pivot=i;
      if(Math.abs(m[pivot][k])<1e-10) throw Error("infeasible_or_redundant_constraints");
      [m[k],m[pivot]]=[m[pivot],m[k]];
      const d=m[k][k];for(let j=k;j<=size;j++)m[k][j]/=d;
      for(let i=0;i<size;i++)if(i!==k){const f=m[i][k];for(let j=k;j<=size;j++)m[i][j]-=f*m[k][j];}
    } return m.map(row=>row[size]);
  }
  function solve(extra){
    const constraints=[...pins.map(i=>({a:unit(i),b:0})),...extra],m=n+constraints.length;
    const K=Array.from({length:m},()=>Array(m).fill(0)),rhs=Array(m).fill(0);
    for(let i=0;i<n;i++)for(let j=0;j<n;j++)K[i][j]=H[i][j];
    constraints.forEach((q,k)=>{rhs[n+k]=q.b;q.a.forEach((v,i)=>{K[i][n+k]=v;K[n+k][i]=v;});});
    const d=linear(K,rhs).slice(0,n);
    const residual=Math.max(...constraints.map(q=>Math.abs(dot(q.a,d)-q.b)));
    if(residual>1e-7)throw Error("constraint_residual");
    return {d,residual};
  }
  const base=vertices.map(v=>[...v]);
  const zero=Array(n).fill(0);
  const semantic=solve([{a:wA,b:24},{a:wB,b:12}]);
  const direct=solve([{a:unit(12),b:32}]);
  function state(d){return vertices.map((v,i)=>[v[0]+d[i],v[1],v[2]]);}
  function floor(v) {
    const xA=dot(wA,v.map(p=>p[0]))-12,xB=dot(wB,v.map(p=>p[0]))-12;
    return [[-120,0,88],[xA,0,88],[xA,30,88],[-120,30,88],
            [-105,-15,184],[xB,-15,184],[xB,15,184],[-105,15,184]];
  }
  const pointOnly=zero.slice();pointOnly[12]=32;
  const globalFactor=1+24/dot(wA,vertices.map(v=>v[0]));
  const globalScale=vertices.map(v=>[v[0]*globalFactor,v[1],v[2]]);
  const scenarios={
    BASE:{cage:base,floor:floor(base)},
    CAGE_ONLY_DRAG:{cage:state(pointOnly),floor:floor(base)},
    GLOBAL_SCALE:{cage:globalScale,floor:floor(globalScale)},
    SEMANTIC_EDIT:{cage:state(semantic.d),floor:floor(state(semantic.d))},
    DIRECT_EDIT:{cage:state(direct.d),floor:floor(state(direct.d))}
  };
  let conflictDetected=false;
  try{solve([{a:unit(12),b:32},{a:unit(12),b:-16}]);}
  catch(e){conflictDetected=e.message==="infeasible_or_redundant_constraints";}
  const reverse=solve([{a:wA,b:-24},{a:wB,b:-12}]);
  const roundTrip=semantic.d.map((x,i)=>x+reverse.d[i]);
  // Independent verification below reads serialized OBJ coordinates, not solve residuals.
  function obj(s){
    let out="# D10 editable open-surface METHOD COUPON. NOT architecture, ART not evaluated.\n# local metres; Z up; no canonical city coordinates\no authored_patch\n";
    out+=s.cage.map(v=>"v "+v.map(x=>x.toFixed(9)).join(" ")).join("\n")+"\n";
    out+=s.floor.map(v=>"v "+v.map(x=>x.toFixed(9)).join(" ")).join("\n")+"\n";
    out+=faces.map(f=>"f "+f.map(i=>i+1).join(" ")).join("\n")+"\n";
    out+="g civic_floor_samples\nf 21 22 23\nf 21 23 24\nf 25 26 27\nf 25 27 28\n";
    return out;
  }
  const objs=Object.fromEntries(Object.entries(scenarios).map(([k,s])=>[k,obj(s)]));
  return {vertices,faces,edges,pins,weights:{A:wA,B:wB},objs,
    solver:{semantic_residual_m:semantic.residual,direct_residual_m:direct.residual,
      conflictDetected,conflict_classification:"singular KKT; contradictions and redundancy not distinguished",
      max_round_trip_m:Math.max(...roundTrip.map(Math.abs))}};
}

function d10Verify(objs, meta) {
  function check(ok,msg){if(!ok)throw Error(msg);}
  function parse(text){
    const v=[],f=[];
    for(const line of text.split(/\r?\n/)){
      const t=line.trim().split(/\s+/);
      if(t[0]==="v"){check(t.length===4,"vertex_arity");const p=t.slice(1).map(Number);check(p.every(Number.isFinite),"nonfinite");v.push(p);}
      if(t[0]==="f"){const a=t.slice(1).map(Number);check(a.length===3&&a.every(Number.isInteger),"triangle_indices");f.push(a.map(x=>x-1));}
    }
    check(v.length===28&&f.length===28,"counts");
    f.forEach(a=>check(a.every(i=>i>=0&&i<v.length),"index_bounds"));
    return {v,f};
  }
  const sub=(a,b)=>a.map((x,i)=>x-b[i]),norm=a=>Math.hypot(...a);
  const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
  const dot=(a,b)=>a.reduce((s,x,i)=>s+x*b[i],0);
  const states=Object.fromEntries(Object.entries(objs).map(([k,t])=>[k,parse(t)])),base=states.BASE;
  const sample=(s,w)=>w.reduce((a,w,i)=>a+w*s.v[i][0],0)-12;
  const rows={};
  for(const [name,s] of Object.entries(states)){
    check(JSON.stringify(s.f)===JSON.stringify(base.f),"connectivity_changed");
    let bad=0,minAlignment=1;
    s.f.forEach((f,i)=>{
      const normal=x=>cross(sub(x.v[f[1]],x.v[f[0]]),sub(x.v[f[2]],x.v[f[0]]));
      const a=normal(base),b=normal(s),na=norm(a),nb=norm(b);
      check(na>1e-6&&nb>1e-6,"degenerate_triangle");
      const align=dot(a,b)/(na*nb);minAlignment=Math.min(minAlignment,align);if(align<=0)bad++;
    });
    const pinDrift=Math.max(...meta.pins.map(i=>norm(sub(s.v[i],base.v[i]))));
    const gapA=Math.abs(s.v[21][0]-sample(s,meta.weights.A));
    const gapB=Math.abs(s.v[25][0]-sample(s,meta.weights.B));
    const widthA=s.v[21][0]-s.v[20][0],widthB=s.v[25][0]-s.v[24][0];
    const zSpread=Math.max(
      Math.max(...s.v.slice(20,24).map(p=>p[2]))-Math.min(...s.v.slice(20,24).map(p=>p[2])),
      Math.max(...s.v.slice(24,28).map(p=>p[2]))-Math.min(...s.v.slice(24,28).map(p=>p[2])));
    rows[name]={pin_drift_m:pinDrift,attachment_gap_m:Math.max(gapA,gapB),
      floor_A_width_m:widthA,floor_B_width_m:widthB,
      floor_A_delta_m:widthA-(base.v[21][0]-base.v[20][0]),
      floor_B_delta_m:widthB-(base.v[25][0]-base.v[24][0]),
      direct_handle_delta_m:s.v[12][0]-base.v[12][0],floor_z_spread_m:zSpread,
      reversed_triangle_normals:bad,min_normal_alignment:minAlignment};
  }
  check(Math.abs(rows.SEMANTIC_EDIT.floor_A_delta_m-24)<1e-7,"semantic_A_target");
  check(Math.abs(rows.SEMANTIC_EDIT.floor_B_delta_m-12)<1e-7,"semantic_B_target");
  check(Math.abs(rows.DIRECT_EDIT.direct_handle_delta_m-32)<1e-7,"direct_target");
  for(const key of ["SEMANTIC_EDIT","DIRECT_EDIT"]){
    const q=rows[key];check(q.pin_drift_m<1e-7&&q.attachment_gap_m<1e-7&&q.floor_z_spread_m<1e-7,"invariant_failed");
    check(q.reversed_triangle_normals===0,"local_orientation_failed");
    check(q.floor_A_width_m>20&&q.floor_B_width_m>20,"sample_width_failed");
  }
  // Negative controls: exact same direct drag, without floor update, and a global x scaling.
  check(rows.CAGE_ONLY_DRAG.attachment_gap_m>1,"negative_detached_floor_not_detected");
  check(rows.GLOBAL_SCALE.pin_drift_m>1,"negative_pin_drift_not_detected");
  return {scope:"serialized OBJ coordinate/connectivity coupon only; NOT collisions or art",rows};
}

function sha256(text) {
  const raw=unescape(encodeURIComponent(text)), bytes=Array.from(raw,c=>c.charCodeAt(0));
  const bits=bytes.length*8;bytes.push(128);while(bytes.length%64!==56)bytes.push(0);
  const high=Math.floor(bits/4294967296),low=bits>>>0;
  for(let j=3;j>=0;j--)bytes.push((high>>>(j*8))&255);
  for(let j=3;j>=0;j--)bytes.push((low>>>(j*8))&255);
  const K=[0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
  const R=(x,n)=>(x>>>n)|(x<<(32-n));
  let h=[0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];
  for(let offset=0;offset<bytes.length;offset+=64){
    const w=[];for(let i=0;i<16;i++){const p=offset+i*4;w[i]=(bytes[p]<<24)|(bytes[p+1]<<16)|(bytes[p+2]<<8)|bytes[p+3];}
    for(let i=16;i<64;i++){const a=w[i-15],b=w[i-2];w[i]=(w[i-16]+(R(a,7)^R(a,18)^(a>>>3))+w[i-7]+(R(b,17)^R(b,19)^(b>>>10)))|0;}
    let [a,b,c,d,e,f,g,z]=h;
    for(let i=0;i<64;i++){const t1=(z+(R(e,6)^R(e,11)^R(e,25))+((e&f)^((~e)&g))+K[i]+w[i])|0;
      const t2=((R(a,2)^R(a,13)^R(a,22))+((a&b)^(a&c)^(b&c)))|0;
      z=g;g=f;f=e;e=(d+t1)|0;d=c;c=b;b=a;a=(t1+t2)|0;}
    h=h.map((v,i)=>(v+[a,b,c,d,e,f,g,z][i])|0);
  }
  return h.map(x=>(x>>>0).toString(16).padStart(8,"0")).join("");
}

function runD10() {
  const experiment=d10Experiment();
  const verification=d10Verify(experiment.objs,experiment);
  const mutationTests={};
  const cases={
    nonfinite:{key:"BASE",text:experiment.objs.BASE.replace("v -48.000000000","v NaN")},
    connectivity:{key:"SEMANTIC_EDIT",text:experiment.objs.SEMANTIC_EDIT.replace("f 1 2 7","f 1 3 7")}
  };
  for(const [name,test] of Object.entries(cases)){
    try {d10Verify({...experiment.objs,[test.key]:test.text},experiment);throw Error("mutation_missed");}
    catch(e){if(e.message==="mutation_missed")throw e;mutationTests[name]=e.message;}
  }
  if(!experiment.solver.conflictDetected)throw Error("conflict_missed");
  const hashes=Object.fromEntries(Object.entries(experiment.objs).map(([k,v])=>[k,sha256(v)]));
  return {experiment,verification,mutationTests,hashes};
}

export { d10Experiment, d10Verify, runD10 };
