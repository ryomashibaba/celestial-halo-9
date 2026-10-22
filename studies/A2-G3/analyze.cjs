const fs=require('fs'),path=require('path');
const root=__dirname,data=JSON.parse(fs.readFileSync(path.join(root,'spatial-models.json'),'utf8'));
const add=(a,b)=>a.map((v,i)=>v+b[i]),sub=(a,b)=>a.map((v,i)=>v-b[i]),mul=(a,s)=>a.map(v=>v*s),dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0),len=a=>Math.sqrt(dot(a,a)),unit=a=>mul(a,1/len(a)),cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
function sdf(s,p){
 if(s.type==='ellipsoid')return (len(p.map((v,i)=>(v-s.c[i])/s.r[i]))-1)*Math.min(...s.r);
 if(s.type==='capsule'){let v=sub(s.b,s.a),q=sub(p,s.a),h=Math.max(0,Math.min(1,dot(q,v)/dot(v,v)));return len(sub(q,mul(v,h)))-s.r;}
 let c=s.min.map((v,i)=>(v+s.max[i])/2),r=s.min.map((v,i)=>(s.max[i]-v)/2),q=p.map((v,i)=>Math.abs(v-c[i])-r[i]);return len(q.map(v=>Math.max(0,v)))+Math.min(Math.max(...q),0);
}
function field(m,p){let o=Math.min(...m.solids.map(s=>sdf(s,p))),v=Math.min(...m.voids.map(s=>sdf(s,p)));return Math.max(o,-v,-p[2]);}
function occupied(m,p){return field(m,p)<0;}
function segment(m,a,b){let d=sub(b,a),L=len(d),n=Math.ceil(L/.02),first=null;for(let i=1;i<n;i++){let t=i/n,p=add(a,mul(d,t));if(occupied(m,p)){first={distance_from_eye_km:L*t,point_km:p};break;}}return {clear:first===null,first_obstruction:first};}
function bounds(m){let lo=[Infinity,Infinity,Infinity],hi=[-Infinity,-Infinity,-Infinity];for(const s of m.solids){let a=s.min||sub(s.c,s.r),b=s.max||add(s.c,s.r);a.forEach((v,i)=>lo[i]=Math.min(lo[i],v));b.forEach((v,i)=>hi[i]=Math.max(hi[i],v));}lo[2]=Math.max(0,lo[2]);return {min:lo,max:hi};}
function grid(m,h=.2){const b=bounds(m),dims=b.min.map((v,i)=>Math.ceil((b.max[i]-v)/h));let total=dims.reduce((a,b)=>a*b,1),cells=new Uint8Array(total),vol=0,zUpper=0;
const index=(x,y,z)=>x+dims[0]*(y+dims[1]*z),pos=(x,y,z)=>[x,y,z].map((v,i)=>b.min[i]+(v+.5)*h);
for(let z=0;z<dims[2];z++)for(let y=0;y<dims[1];y++)for(let x=0;x<dims[0];x++){let p=pos(x,y,z);if(occupied(m,p)){cells[index(x,y,z)]=1;vol++;if(p[2]>=4)zUpper++;}}
let components=[];for(let idx=0;idx<total;idx++){if(cells[idx]!==1)continue;let q=[idx],n=0;cells[idx]=2;for(let at=0;at<q.length;at++){let i=q[at],x=i%dims[0],y=Math.floor(i/dims[0])%dims[1],z=Math.floor(i/(dims[0]*dims[1]));n++;for(let [dx,dy,dz] of [[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]]){let X=x+dx,Y=y+dy,Z=z+dz;if(X<0||Y<0||Z<0||X>=dims[0]||Y>=dims[1]||Z>=dims[2])continue;let k=index(X,Y,Z);if(cells[k]===1){cells[k]=2;q.push(k);}}}components.push(n);}
return {sample_spacing_m:h*1000,solid_connected_components_6_neighbor:components.sort((a,b)=>b-a),sampled_material_volume_km3:vol*h**3,sampled_material_above_4km_km3:zUpper*h**3,warning:'Voxel connectivity and occupied volume only; no structural, living-area, or art-quality validation.'};}
const external=[
 {id:'front_ground',label:'地上正面',eye:[0,-10,.05],look:[0,0,3.0],up:[0,0,1],fov:58},
 {id:'oblique',label:'南東斜視',eye:[10,-11,8],look:[0,0,3.0],up:[0,0,1],ortho:10},
 {id:'side',label:'東側面',eye:[12,0,3.2],look:[0,0,3.2],up:[0,0,1],ortho:10},
 {id:'rear',label:'北・背面',eye:[0,12,3.2],look:[0,0,3.2],up:[0,0,1],ortho:10},
 {id:'top',label:'俯瞰',eye:[0,0,14],look:[0,0,3],up:[0,1,0],ortho:10}
];
function trace(m,eye,dir){let t=0;for(let i=0;i<300&&t<30;i++){let p=add(eye,mul(dir,t)),d=field(m,p);if(d<.0002){let e=.0005,n=unit([0,1,2].map(k=>{let a=[...p],b=[...p];a[k]+=e;b[k]-=e;return field(m,a)-field(m,b)}));return {p,n,t};}t+=Math.max(.0002,d*.8);}return null;}
const escape=s=>s.replaceAll('&','&amp;').replaceAll('<','&lt;');
function renderSheet(m){let arr=[`<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="1050" viewBox="0 0 1500 1050"><style>text{font-family:'Yu Gothic','Meiryo',sans-serif;fill:#223a45}.t{font-size:25px;font-weight:bold}.s{font-size:15px}</style><rect width="1500" height="1050" fill="#f2f1ea"/><text x="35" y="42" class="t">A2-G3 / ${m.id} — ${escape(m.name)}</text><text x="35" y="72" class="s">同一の数式的空間モデルからの低解像度占有面描画。都市建築・美術品質の実証画像ではありません。</text>`];
 let cameras=[...external,{id:'inside',label:'内部・検証視点',eye:m.eye,look:m.look,up:[0,0,1],fov:82}];
 cameras.forEach((cam,idx)=>{let ox=35+(idx%3)*490,oy=105+Math.floor(idx/3)*455,w=100,h=80,scale=4.5;
 arr.push(`<text x="${ox}" y="${oy+22}" class="t">${cam.label}</text><rect x="${ox}" y="${oy+40}" width="450" height="360" fill="#dce5e6"/>`);
 let f=unit(sub(cam.look,cam.eye)),r=unit(cross(f,cam.up)),u=unit(cross(r,f)),light=unit([-.6,-.7,1]);
 for(let y=0;y<h;y++){let colors=[];for(let x=0;x<w;x++){let px=((x+.5)/w-.5)*2,py=(.5-(y+.5)/h)*2,origin=cam.eye,dir;
 if(cam.ortho){origin=add(cam.eye,add(mul(r,px*cam.ortho/2),mul(u,py*cam.ortho/2*h/w)));dir=f;}else{let k=Math.tan(cam.fov*Math.PI/360);dir=unit(add(f,add(mul(r,px*k),mul(u,py*k*h/w))));}
 let hit=trace(m,origin,dir);if(!hit){colors.push(null);continue;}let shade=.30+.7*Math.max(0,dot(hit.n,light)),base=hit.p[2]>4?[166,191,182]:[203,205,188];colors.push('#'+base.map(c=>Math.round(c*shade).toString(16).padStart(2,'0')).join(''));}
 for(let x=0;x<w;){let c=colors[x],k=x+1;while(k<w&&colors[k]===c)k++;if(c)arr.push(`<rect x="${ox+x*scale}" y="${oy+40+y*scale}" width="${(k-x)*scale+.05}" height="${scale+.05}" fill="${c}"/>`);x=k;}}
 if(cam.id==='inside')for(const city of m.city_targets){let d=sub(city.p,cam.eye),z=dot(d,f),k=Math.tan(cam.fov*Math.PI/360),px=dot(d,r)/z/k,py=dot(d,u)/z/(k*h/w);if(z>0&&Math.abs(px)<1&&Math.abs(py)<1&&segment(m,cam.eye,city.p).clear&&occupied(m,add(city.p,mul(city.g,.12)))){let X=ox+(px+1)/2*w*scale,Y=oy+40+(1-py)/2*h*scale;arr.push(`<circle cx="${X}" cy="${Y}" r="5" fill="#f4c56b"/><text x="${X+7}" y="${Y-7}" style="font-size:13px;fill:#f4c56b">${city.id}</text>`);}}
 arr.push(`<text x="${ox}" y="${oy+425}" class="s">${cam.id==='inside'?'金点＝遮蔽なし・背面占有ありの都市予定点':cam.ortho?'平行投影・水平幅10km':`透視・水平画角${cam.fov}°`}</text>`);
 });
 arr.push('<text x="35" y="1030" class="s">無装飾・単純曲面の占有モデル。外形と空洞の矛盾を見る診断図。美術採択／構造安全／居住床の実証を意味しません。</text></svg>');
 fs.writeFileSync(path.join(root,m.id+'-six-views.svg'),arr.join('\n'));return cameras;
}
function sections(m){let arr=[`<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="650"><style>text{font-family:'Yu Gothic','Meiryo',sans-serif;fill:#223a45;font-size:18px}</style><rect width="1500" height="650" fill="#f2f1ea"/><text x="30" y="38">A2-G3 / ${m.id} — 同じ占有モデルの断面 / 単位km</text>`];
 const views=m.id==='C3'?[{label:'三施設共有断面 y=0.5',p:(a,b)=>[a,.5,b],xmin:-2,xmax:2,ymin:0,ymax:4},{label:'A/C縦断面 x=-0.8',p:(a,b)=>[-.8,a,b],xmin:-2,xmax:2,ymin:0,ymax:4},{label:'共有床水平断面 z=1.2',p:(a,b)=>[a,b,1.2],xmin:-2,xmax:2,ymin:-2,ymax:2}]:[{label:'東西断面 y=0',p:(a,b)=>[a,0,b],xmin:-4,xmax:4,ymin:0,ymax:7},{label:'南北断面 x=0',p:(a,b)=>[0,a,b],xmin:-4,xmax:4,ymin:0,ymax:7},{label:'高所水平断面 z=4.5',p:(a,b)=>[a,b,4.5],xmin:-4,xmax:4,ymin:-4,ymax:4}];
 views.forEach((v,i)=>{let x0=30+i*490,y0=105,s=416/(v.xmax-v.xmin);arr.push(`<text x="${x0}" y="80">${v.label}</text><rect x="${x0}" y="${y0}" width="416" height="416" fill="#dce5e6"/>`);let h=.05;for(let y=v.ymin;y<v.ymax;y+=h)for(let x=v.xmin;x<v.xmax;x+=h){let p=v.p(x+h/2,y+h/2);if(occupied(m,p))arr.push(`<rect x="${x0+(x-v.xmin)*s}" y="${y0+(v.ymax-y-h)*s}" width="${h*s+.05}" height="${h*s+.05}" fill="#818e80"/>`);}arr.push(`<text x="${x0}" y="555">横軸 ${v.xmin}〜${v.xmax} / 縦軸 ${v.ymin}〜${v.ymax}</text>`);});arr.push('<text x="30" y="610">緑灰＝建築の占有域、淡青＝空。内部施設・生活街区は未配置。図の実線形状を完成外観としない。</text></svg>');fs.writeFileSync(path.join(root,m.id+'-sections.svg'),arr.join('\n'));}
const results={method:{units:'km',model:'Union of analytic solids minus union of analytic voids, clipped at z=0',line_of_sight_sample_m:20,gravity_support_probe_m:120,scope:'Geometric occupancy only. No load-bearing, physiological, usable-floor-area or artistic acceptance checks.'},models:[]};
for(const m of data.models){const sight=m.city_targets.map(t=>{let f=unit(sub(m.look,m.eye)),r=unit(cross(f,[0,0,1])),u=unit(cross(r,f)),d=sub(t.p,m.eye),forward=dot(d,f),h=Math.tan(82*Math.PI/360),frame=forward>0&&Math.abs(dot(d,r)/forward)<=h&&Math.abs(dot(d,u)/forward)<=h*.8;return {target:t.id,...segment(m,m.eye,t.p),inside_internal_camera_frame:frame,target_in_empty_domain:!occupied(m,t.p),backing_at_120m:occupied(m,add(t.p,mul(t.g,.12)))};});
 const row={id:m.id,eye_km:m.eye,proposed_primitive_envelope_km:bounds(m),occupancy:grid(m),sightlines:sight,cameras:renderSheet(m)};sections(m);
 if(m.id==='N2')row.connectivity_finer_grid=grid(m,.1);
 if(m.id==='N3'){row.upper_separation_probe={x_km:0,y_km:0,lower_inward_surface_z_km:4.5,upper_basin_surface_z_km:5.4,vertical_material_gap_km:.9,warning:'One section probe only, not a global minimum thickness.'};
 row.urban_connection_waypoints=[[[0,0,.95],[-2,0,.95]],[[-2,0,.95],[-2,0,5.55]],[[-2,0,5.55],[0,0,5.55]],[[-2,0,2.25],[-2,1.6,2.25]],[[-2,1.6,2.25],[1.8,1.6,2.25]],[[1.8,1.6,2.35],[1.8,.2,2.35]],[[1.8,.2,2.35],[1.16,.2,2.35]],[[0,1.6,2.3],[0,1,2.3]]].map(([a,b])=>({a,b,...segment(m,a,b)}));
 row.urban_patch_probes=m.city_targets.slice(0,4).map(t=>{let axes=t.id==='west'||t.id==='east'?[[0,1,0],[0,0,1]]:t.id==='north_low'?[[1,0,0],[0,0,1]]:[[1,0,0],[0,1,0]],counts={clear:0,backed:0,in_frame:0,combined:0},f=unit(sub(m.look,m.eye)),r=unit(cross(f,[0,0,1])),u=unit(cross(r,f)),k=Math.tan(82*Math.PI/360);for(let i=0;i<7;i++)for(let j=0;j<3;j++){let p=add(t.p,add(mul(axes[0],(i/6-.5)*.6),mul(axes[1],(j/2-.5)*.24))),d=sub(p,m.eye),z=dot(d,f),clear=!occupied(m,p)&&segment(m,m.eye,p).clear,backed=occupied(m,add(p,mul(t.g,.12))),frame=z>0&&Math.abs(dot(d,r)/z)<=k&&Math.abs(dot(d,u)/z)<=k*.8;counts.clear+=+clear;counts.backed+=+backed;counts.in_frame+=+frame;counts.combined+=+(clear&&backed&&frame);}return {target:t.id,nominal_patch_m:[600,240],sample_count:21,...counts,warning:'Sparse probes on a proposed surface only, not a modeled building facade or a usable city floor.'};});}
 if(m.id==='N1'){row.upper_separation_probe={x_km:0,y_km:0,lower_inward_surface_z_km:2.65+1.95*Math.sqrt(1-(.2/2)**2),upper_basin_surface_z_km:6.5-1.1*Math.sqrt(1-(.25/1.25)**2-(.55/1.25)**2)};row.upper_separation_probe.vertical_material_gap_km=row.upper_separation_probe.upper_basin_surface_z_km-row.upper_separation_probe.lower_inward_surface_z_km;}
 if(m.id==='C3'){row.shared_material_probes=[{id:'AB shared roof-floor',point:[0,0,1.2]},{id:'BC shared inhabited wall',point:[-.45,.2,1.8]},{id:'ABC junction',point:[-.45,.1,1.2]}].map(q=>({...q,inside_facility_envelopes:m.solids.filter(s=>sdf(s,q.point)<0).map(s=>s.name),inside_final_material:occupied(m,q.point)}));
 row.removal_tests=[{id:'remove_AB_shared_slab',cut:{type:'box',min:[-.2,-.4,1],max:[.1,.3,1.4]},a:[0,0,.85],b:[0,0,1.55]},{id:'remove_BC_shared_wall',cut:{type:'box',min:[-.6,.1,1.55],max:[-.25,.3,1.95]},a:[-.8,.2,1.75],b:[0,.2,1.75]}].map(t=>({id:t.id,before:segment(m,t.a,t.b),after:segment({...m,voids:[...m.voids,t.cut]},t.a,t.b)}));
 row.shared_street_waypoint_segments=[[[0,0,.8],[-.3,.5,.8]],[[-.3,.5,.8],[-.475,.5,.8]],[[-.475,.5,.8],[-.475,.5,1.65]],[[-.475,.5,1.65],[0,.5,1.65]],[[-.475,.5,1.65],[-.475,.5,2.7]],[[-.475,.5,2.7],[-.8,.5,2.7]]].map(([a,b])=>({a,b,...segment(m,a,b)}));}
 results.models.push(row);
}
fs.writeFileSync(path.join(root,'geometric-checks.json'),JSON.stringify(results,null,2)+'\n');
console.log(JSON.stringify(results.models.map(m=>({id:m.id,components:m.occupancy.solid_connected_components_6_neighbor.length,sight:m.sightlines.map(s=>({id:s.target,clear:s.clear,backed:s.backing_at_120m,empty:s.target_in_empty_domain})),upper_gap:m.upper_separation_probe,shared:m.shared_material_probes})),null,2));
