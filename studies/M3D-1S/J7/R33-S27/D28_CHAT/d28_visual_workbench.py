#!/usr/bin/env python3
"""D28 research workbench: visual pick -> bounded real-GLB vertex edit -> six-camera review.

Usage:
  python d28_visual_workbench.py --output ./D28_WORK --port 8768 [--source path.glb]
  python d28_visual_workbench.py --output ./D28_WORK --self-test

Isolated study tool only. No Minecraft, Blender, protected masters or formal adoption.
Does not edit source GLB. All edits are recipe-based rebuilds from a copied base.
"""
from __future__ import annotations
import argparse, hashlib, io, json, math, threading, time
from pathlib import Path
from dataclasses import dataclass
from typing import Any
import numpy as np
import vtk  # Register VTK OpenGL rendering factories before offscreen windows
import trimesh
from PIL import Image, ImageDraw
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import vtkCellArray, vtkTriangle, vtkPolyData
from vtkmodules.vtkRenderingCore import (vtkActor, vtkRenderer, vtkRenderWindow, vtkPolyDataMapper,
    vtkCellPicker, vtkWindowToImageFilter)
from vtkmodules.vtkIOImage import vtkPNGWriter
from vtkmodules.util.numpy_support import numpy_to_vtk, vtk_to_numpy
from fastapi import FastAPI, Body, HTTPException, Request
from fastapi.responses import HTMLResponse, Response, JSONResponse
import uvicorn

WIDTH, HEIGHT = 560, 350
VIEWS = ['front','rear','east','west','aerial','oblique']
MAX_MESHES = 120
MAX_TRIANGLES = 350_000
MAX_MESH_VERTICES = 300_000
MAX_UPLOAD_BYTES = 16_000_000
PROTECTED_TECHNICAL_MESHES = {"civic_spine", "civic_plaza"}  # D27 local route fixture only

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()

def load_scene(raw:bytes)->trimesh.Scene:
    try: s=trimesh.load(io.BytesIO(raw),file_type='glb',force='scene',process=False)
    except Exception as exc:raise ValueError(f'Invalid GLB: {exc}') from exc
    if not 1<=len(s.geometry)<=MAX_MESHES:raise ValueError('unsupported mesh count')
    if sum(len(g.faces) for g in s.geometry.values())>MAX_TRIANGLES:raise ValueError('GLB exceeds triangle cap')
    if any(len(g.vertices)>MAX_MESH_VERTICES for g in s.geometry.values()):raise ValueError('GLB exceeds vertex cap')
    if not all(np.isfinite(g.vertices).all() for g in s.geometry.values()):raise ValueError('non-finite vertices')
    nodes=list(s.graph.nodes_geometry)
    if len(nodes)!=len(s.geometry):raise ValueError('instanced or unreferenced geometries unsupported')
    for node in nodes:
        transform,name=s.graph.get(node)
        if not np.allclose(transform,np.eye(4),atol=1e-8):raise ValueError('nonidentity transforms unsupported')
        if name not in s.geometry:raise ValueError('missing scene geometry')
    return s

def demo_glb()->bytes:
    """Neutral two-body technique fixture; not a design concept or accepted city mass."""
    a=trimesh.creation.icosphere(subdivisions=3,radius=205.0)
    a.apply_scale([1.1,.90,1.34]);a.apply_translation([-225,0,175]);a.visual.vertex_colors=[196,208,223,255]
    b=trimesh.creation.icosphere(subdivisions=3,radius=135.0)
    b.apply_scale([.94,1.3,.83]);b.apply_translation([205,25,265]);b.visual.vertex_colors=[215,182,153,255]
    s=trimesh.Scene();s.add_geometry(a,geom_name='NEUTRAL_A',node_name='NEUTRAL_A');s.add_geometry(b,geom_name='NEUTRAL_B',node_name='NEUTRAL_B')
    return trimesh.exchange.gltf.export_glb(s)

def camera_setup(scene:trimesh.Scene, view:str):
    bounds=np.asarray(scene.bounds); center=np.mean(bounds,axis=0)
    span=np.max(bounds[1]-bounds[0]);span=max(float(span),10.0)
    d={
      'front':(0,-2.55,.65),'rear':(0,2.55,.65),
      'east':(2.55,0,.65),'west':(-2.55,0,.65),
      'aerial':(1.25,-1.15,2.8),'oblique':(1.7,-2.2,1.25)
    }[view]
    return center+span*np.asarray(d),center,span

def vtk_poly(mesh:trimesh.Trimesh)->vtkPolyData:
    points=vtkPoints(); points.SetData(numpy_to_vtk(np.asarray(mesh.vertices,dtype=np.float64),deep=True))
    faces=vtkCellArray()
    for tri in mesh.faces:
        cell=vtkTriangle()
        for j,n in enumerate(tri):cell.GetPointIds().SetId(j,int(n))
        faces.InsertNextCell(cell)
    p=vtkPolyData();p.SetPoints(points);p.SetPolys(faces)
    return p

@dataclass
class ViewResult:
    png:bytes
    selection:dict|None=None

def render(scene:trimesh.Scene,view:str,pick:tuple[float,float]|None=None)->ViewResult:
    if view not in VIEWS:raise ValueError('unknown view')
    ren=vtkRenderer();ren.SetBackground(.10,.14,.19)
    actor_map={}
    for name,g in scene.geometry.items():
        m=vtkPolyDataMapper();m.SetInputData(vtk_poly(g))
        a=vtkActor();a.SetMapper(m)
        # Consistent non-photo technical material, no cinematic beauty claims.
        v=np.asarray(g.visual.vertex_colors)
        rgb=v[0,:3]/255. if len(v) else np.array([.76,.79,.85])
        a.GetProperty().SetColor(*rgb);a.GetProperty().SetAmbient(.27);a.GetProperty().SetDiffuse(.73)
        a.GetProperty().SetSpecular(.18);a.GetProperty().SetSpecularPower(24)
        ren.AddActor(a);actor_map[a.GetAddressAsString('')]=name
    pos,target,span=camera_setup(scene,view)
    c=ren.GetActiveCamera();c.SetPosition(*pos);c.SetFocalPoint(*target);c.SetViewUp(0,0,1);c.SetViewAngle(33)
    win=vtkRenderWindow();win.SetOffScreenRendering(1);win.SetMultiSamples(0);win.SetSize(WIDTH,HEIGHT);win.AddRenderer(ren)
    ren.ResetCameraClippingRange();win.Render()
    selection=None
    if pick is not None:
        u,v=pick
        picker=vtkCellPicker();picker.SetTolerance(.006)
        hit=picker.Pick(u*(WIDTH-1),(1-v)*(HEIGHT-1),0,ren)
        if hit and picker.GetActor():
            name=actor_map.get(picker.GetActor().GetAddressAsString(''))
            if name:
                hit_xyz=np.asarray(picker.GetPickPosition(),dtype=float)
                vertices=np.asarray(scene.geometry[name].vertices)
                index=int(np.argmin(np.einsum('ij,ij->i',vertices-hit_xyz,vertices-hit_xyz)))
                selection={'geometry':name,'vertex_id':index,'hit_xyz_m':hit_xyz.tolist(),
                           'vertex_xyz_m':vertices[index].tolist(),'view':view,'pixel_uv':[u,v]}
    w2i=vtkWindowToImageFilter();w2i.SetInput(win);w2i.ReadFrontBufferOff();w2i.SetInputBufferTypeToRGB();w2i.Update()
    writer=vtkPNGWriter();writer.SetInputConnection(w2i.GetOutputPort());writer.WriteToMemoryOn();writer.Write()
    png=vtk_to_numpy(writer.GetResult()).tobytes()
    win.Finalize()
    return ViewResult(png,selection)

def apply_recipe(raw:bytes,operations:list[dict])->bytes:
    base=load_scene(raw)
    if len(operations)>40:raise ValueError('max 40 strokes per study session')
    original={name:(g.faces.copy(),g.vertices.copy(),bool(g.is_watertight)) for name,g in base.geometry.items()}
    for step in operations:
        name=step.get('geometry');idx=step.get('vertex_id')
        if name not in base.geometry:raise ValueError('unknown geometry')
        if name in PROTECTED_TECHNICAL_MESHES:raise ValueError('protected civic route/plaza cannot be edited by any recipe')
        g=base.geometry[name];v=np.asarray(g.vertices).copy()
        if type(idx)!=int or idx<0 or idx>=len(v):raise ValueError('invalid vertex id')
        radius=float(step.get('radius_m',0));delta=np.asarray(step.get('delta_xyz_m',[]),dtype=float)
        span=max(float(np.max(base.bounds[1]-base.bounds[0])),10.)
        if (not math.isfinite(radius) or not .1<=radius<=span or delta.shape!=(3,) or not np.isfinite(delta).all()
            or np.linalg.norm(delta)>min(150.,span*.25) or not np.any(delta)):
            raise ValueError('unsafe brush displacement/radius')
        anchor=v[idx].copy();r=np.linalg.norm(v-anchor,axis=1)
        t=np.clip(1-r/radius,0,1);w=t*t*(3-2*t)
        v+=w[:,None]*delta
        g.vertices=v
        if not np.isfinite(g.vertices).all():raise ValueError('nonfinite result')
        if original[name][2] and (not g.is_watertight or not g.is_winding_consistent or g.volume<=0):
            raise ValueError('mesh integrity failed')
        areas=trimesh.triangles.area(g.triangles)
        if areas.min()<1e-7:raise ValueError('degenerate triangle detected')
    for name,g in base.geometry.items():
        if not np.array_equal(g.faces,original[name][0]):raise ValueError('topology changed')
    return trimesh.exchange.gltf.export_glb(base)

class Workspace:
    def __init__(self,root:Path,source:Path|None=None):
        self.root=root.resolve();self.root.mkdir(parents=True,exist_ok=True)
        self.base_path=self.root/'BASE.glb';self.current_path=self.root/'EDIT.glb'
        self.recipe_path=self.root/'EDIT_PLAN.json'
        self.lock=threading.RLock();self.selected=None
        if not self.base_path.exists():
            if source:
                source=source.resolve()
                if self.root==source.parent or self.root in source.parents:raise ValueError('source must not be inside workspace')
                raw=source.read_bytes();load_scene(raw)
            else:raw=demo_glb()
            self.base_path.write_bytes(raw)
        self.raw=self.base_path.read_bytes();load_scene(self.raw)
        self.protected=sorted(PROTECTED_TECHNICAL_MESHES.intersection(load_scene(self.raw).geometry))
        self.base_images={v:render(load_scene(self.raw),v).png for v in VIEWS}
        if self.recipe_path.exists():
            data=json.loads(self.recipe_path.read_text('utf-8'))
            if data.get('base_sha256')!=sha(self.raw):raise ValueError('baseline sha does not match recipe')
            self.ops=data['operations']
        else:self.ops=[]
        self._rebuild()
    def _rebuild(self):
        self.edited=apply_recipe(self.raw,self.ops) if self.ops else self.raw
        scene=load_scene(self.edited)
        self.current_path.write_bytes(self.edited)
        self.recipe_path.write_text(json.dumps({'study':'D28', 'base_sha256':sha(self.raw),
            'operations':self.ops,'limitations':'manual technical sculpt, not city approval'},indent=2)+'\n',encoding='utf-8')
        self.images={v:render(scene,v).png for v in VIEWS}
        self.diff_images={};self.pixel_changes={}
        for key in VIEWS:
            base=np.asarray(Image.open(io.BytesIO(self.base_images[key])).convert('RGB'),dtype=np.int16)
            edited=np.asarray(Image.open(io.BytesIO(self.images[key])).convert('RGB'),dtype=np.int16)
            changed=np.max(np.abs(base-edited),axis=2)>20
            self.pixel_changes[key]=round(100*float(changed.mean()),3)
            overlay=edited.astype(np.uint8).copy()
            overlay[changed]=(0.35*overlay[changed]+0.65*np.array([250,112,90])).astype(np.uint8)
            out=io.BytesIO();Image.fromarray(overlay).save(out,format='PNG')
            self.diff_images[key]=out.getvalue()
        self.revision=sha(self.edited)
    def state(self):
        scene=load_scene(self.edited)
        return {'revision':self.revision,'base_sha256':sha(self.raw),'operations':len(self.ops),
                'geometry':[{ 'name':k,'vertices':len(g.vertices),'triangles':len(g.faces)} for k,g in scene.geometry.items()],
                'selected':self.selected,'views':VIEWS,'size_px':[WIDTH,HEIGHT],
                'protected_geometry':self.protected,
                'image_diff_percent_not_art_score':self.pixel_changes,
                'art':'NOT SUBMITTED','minecraft':'HOLD'}
    def select(self,view,u,v):
        if view not in VIEWS or not all(math.isfinite(z) and 0<=z<=1 for z in (u,v)):
            raise ValueError('invalid view or coordinates')
        self.selected=render(load_scene(self.edited),view,(u,v)).selection
        return self.selected
    def commit_edit(self,request):
        if self.selected and self.selected['geometry'] in self.protected:raise ValueError('protected civic route / plaza geometry')
        if request.get('revision')!=self.revision:raise ValueError('stale edit revision')
        if not self.selected:raise ValueError('select a vertex first')
        step={'geometry':self.selected['geometry'],'vertex_id':self.selected['vertex_id'],
              'radius_m':request.get('radius_m'),'delta_xyz_m':request.get('delta_xyz_m')}
        # Fail closed: validate entire proposal before altering files or history
        candidate=self.ops+[step]
        result=apply_recipe(self.raw,candidate)
        self.ops=candidate;self._rebuild();self.selected=None
        assert self.edited==result
        return self.state()
    def import_glb(self,blob:bytes):
        if len(blob)>MAX_UPLOAD_BYTES:raise ValueError('GLB upload exceeds 16MB')
        s=load_scene(blob)  # validate before touching the existing working files
        if self.ops:raise ValueError('Save and undo current edits before importing another GLB')
        if blob==self.raw:return self.state()
        archive=self.root/'archived_sources';archive.mkdir(exist_ok=True)
        old=archive/(sha(self.raw)+'.glb')
        if not old.exists():old.write_bytes(self.raw)
        self.base_path.write_bytes(blob)
        self.raw=blob;self.selected=None
        self.protected=sorted(PROTECTED_TECHNICAL_MESHES.intersection(s.geometry))
        self.base_images={v:render(s,v).png for v in VIEWS}
        self._rebuild()
        return self.state()
    def undo(self,revision):
        if revision!=self.revision:raise ValueError('stale revision')
        if not self.ops:raise ValueError('nothing to undo')
        self.ops.pop();self._rebuild();self.selected=None
        return self.state()

HTML=r'''<!doctype html><html lang="ja"><head><meta charset="utf-8"/>
<title>HALO-9 / D28 Visual Sculpt Workbench</title><meta name="viewport" content="width=device-width,initial-scale=1"/>
<style>
:root{font-family:system-ui,-apple-system,sans-serif;color:#e9eff5;background:#0a111a}
*{box-sizing:border-box}body{margin:0}header{padding:15px 24px;background:#121e2b;border-bottom:1px solid #304357;display:flex;justify-content:space-between;gap:16px;align-items:center}
h1{font-size:19px;letter-spacing:.02em;margin:0}small,.muted{color:#a7b6c6}.layout{display:grid;grid-template-columns:minmax(0,1fr) 290px;gap:14px;padding:14px;max-width:1620px;margin:auto}
.viewport-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}.viewport{border:1px solid #304558;background:#142232;border-radius:10px;overflow:hidden;position:relative;cursor:crosshair}
.viewport b{display:block;padding:8px 12px;font-size:13px;font-weight:600}.viewport img{width:100%;display:block;aspect-ratio:560/350;object-fit:contain}.viewport:hover{border-color:#7ebac8}
.marker{position:absolute;width:15px;height:15px;border:2px solid #f8b55a;border-radius:50%;box-shadow:0 0 0 2px #142232;pointer-events:none;transform:translate(-50%,-50%)}
.panel{border:1px solid #31475b;border-radius:10px;background:#142232;padding:17px;align-self:start}label{display:block;font-size:12px;color:#b1c2ce;margin:11px 0 5px}input{width:100%;background:#09131f;border:1px solid #40576d;color:#fff;border-radius:6px;padding:9px}button,.download{display:inline-block;background:#365b6e;color:white;border:0;padding:11px 14px;border-radius:7px;cursor:pointer;text-decoration:none;font:inherit;text-align:center}
button:hover,.download:hover{background:#477e91}button.secondary{background:#2a3645}button:disabled{opacity:.4;cursor:not-allowed}.pair{display:grid;grid-template-columns:1fr 1fr;gap:9px}.triple{display:grid;grid-template-columns:repeat(3,1fr);gap:7px}.triple input{min-width:0}
#selected{min-height:56px;border:1px dashed #506276;padding:12px;border-radius:6px;font-size:13px;overflow-wrap:anywhere}#message{font-size:13px;margin:13px 0;min-height:20px}footer{padding:10px 24px 22px;color:#90a2b2;font-size:12px}
@media(max-width:1050px){.layout{grid-template-columns:1fr}.viewport-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:540px){.viewport-grid{grid-template-columns:1fr}}
</style></head><body><header><div><h1>CELESTIAL HALO-9 / D28 — Visual Sculpt Workbench</h1><small>隔離した実GLBを6方向から観察し、クリック位置の頂点を編集する研究環境</small></div><small>TECH EXPERIMENT · ART NOT SUBMITTED · Minecraft HOLD</small></header>
<div class="layout"><main><div class="viewport-grid" id="views"></div><p class="muted">画像をクリックして3D表面上の頂点を選択。ブラシ移動後、6枚すべてが実GLBから再描画されます。視覚上の変化は美術合格の証拠ではありません。</p></main>
<aside class="panel"><b>GLBを開く（隔離コピー）</b>
<label for="source">手元の .glb ファイルを読み込む</label><input type="file" id="source" accept=".glb,model/gltf-binary"/>
<p class="muted" style="font-size:12px">現在の編集が0回の場合のみ、最大16MB。元ファイルは変更しません。</p>
<hr style="border:0;border-top:1px solid #30475a;margin:12px 0"/>
<b>表示対象</b><div class="triple" style="margin:12px 0 18px">
<button class="secondary mode" data-mode="base" id="mode_base">編集前</button><button class="mode" data-mode="edit" id="mode_edit">編集後</button><button class="secondary mode" data-mode="diff" id="mode_diff">差分</button></div>
<b>頂点編集</b><p id="selected">6視点の画像をクリックして選択してください。</p>
<label for="radius">影響半径（m）</label><input id="radius" type="number" value="220" min="0.1" step="10"/>
<label>移動量（m）: X / Y / Z</label><div class="triple"><input id="dx" type="number" value="35" step="5" aria-label="X"/><input id="dy" type="number" value="0" step="5" aria-label="Y"/><input id="dz" type="number" value="20" step="5" aria-label="Z"/></div>
<div class="pair" style="margin-top:13px"><button id="edit">実GLBを編集</button><button class="secondary" id="undo">1手戻す</button></div>
<div id="message"></div><div class="muted" id="status"></div><div class="muted" id="diffrates" style="font-size:12px;margin-top:6px"></div><hr style="border:0;border-top:1px solid #30475a;margin:16px 0"/>
<div class="pair"><a class="download" href="/artifact/EDIT.glb">GLB保存</a><a class="download" href="/artifact/EDIT_PLAN.json">編集履歴JSON</a></div>
<p class="muted" style="font-size:12px">原本GLBは常に保護します。自己交差・建築構造・公共経路・美術品質は認証していません。</p></aside></div>
<footer>D28 local research build | 六視点は固定カメラ。ローカル環境のみ、外部通信なし。</footer>
<script>
let state=null, displayMode='edit';const root=document.getElementById('views');const message=document.getElementById('message');
const names={front:'南側',rear:'北側',east:'東側',west:'西側',aerial:'俯瞰',oblique:'斜視'};
for(let key of ['front','rear','east','west','aerial','oblique']){let box=document.createElement('div');box.className='viewport';box.dataset.view=key;box.innerHTML='<b>'+names[key]+'</b><img alt="実3Dからレンダリングした'+names[key]+'画像"/>';root.append(box);
box.querySelector('img').addEventListener('click',async(e)=>{let rect=e.target.getBoundingClientRect(); let u=(e.clientX-rect.left)/rect.width,v=(e.clientY-rect.top)/rect.height;await call('/api/select',{view:key,u,v});});}
async function post(url,body){let r=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});let j=await r.json();if(!r.ok)throw Error(j.detail||'error');return j}
function clearMarkers(){document.querySelectorAll('.marker').forEach(n=>n.remove())}
function refresh(){for(let box of root.children){box.querySelector('img').src='/api/'+(displayMode==='base'?'baseview':displayMode==='diff'?'diffview':'view')+'/'+box.dataset.view+'?v='+encodeURIComponent(state.revision);}document.getElementById('status').textContent=`編集 ${state.operations}回 / メッシュ ${state.geometry.length}個 / SHA256 ${state.revision.slice(0,14)}…`;document.getElementById('undo').disabled=state.operations===0;document.getElementById('diffrates').textContent='編集前との差分（画素割合、非美術評価）: '+Object.entries(state.image_diff_percent_not_art_score).map(([k,v])=>names[k]+' '+v.toFixed(2)+'%').join(' / ');}
async function call(endpoint,data){try{message.textContent='処理中…';if(endpoint==='/api/select'){let s=await post(endpoint,data);clearMarkers();if(!s){document.getElementById('selected').textContent='メッシュがない場所です。再選択してください。';message.textContent='';return;}document.getElementById('selected').textContent=`${s.geometry} / vertex #${s.vertex_id}\n(${s.vertex_xyz_m.map(x=>x.toFixed(1)).join(', ')})m`;let viewbox=document.querySelector('.viewport[data-view="'+data.view+'"]');let marker=document.createElement('div');marker.className='marker';let img=viewbox.querySelector('img');marker.style.left=(img.offsetLeft+img.clientWidth*data.u)+'px';marker.style.top=(img.offsetTop+img.clientHeight*data.v)+'px';viewbox.append(marker);message.textContent='頂点を選択しました';}
else{state=await post(endpoint,data);refresh();clearMarkers();document.getElementById('selected').textContent='編集結果を確認し、次の頂点を選択してください。';message.textContent='実GLBを保存し6視点を更新しました。';}}
catch(e){message.textContent='拒否: '+e.message;}}
window.onload=async()=>{state=await (await fetch('/api/state')).json();refresh();}
document.getElementById('edit').onclick=()=>call('/api/edit',{revision:state.revision,radius_m:Number(document.getElementById('radius').value),delta_xyz_m:['dx','dy','dz'].map(k=>Number(document.getElementById(k).value))});
document.getElementById('undo').onclick=()=>call('/api/undo',{revision:state.revision});
document.getElementById('source').onchange=async event=>{
 const f=event.target.files?.[0];if(!f)return;
 if(!f.name.toLowerCase().endsWith('.glb')){message.textContent='GLBのみ対応';return;}
 try{
   message.textContent='検証して読み込み中…';const result=await fetch('/api/import',{method:'POST',headers:{'Content-Type':'model/gltf-binary'},body:await f.arrayBuffer()});
   const next=await result.json();if(!result.ok)throw Error(next.detail||'import failed');
   state=next;displayMode='edit';refresh();clearMarkers();message.textContent='読み込み成功。元ファイルは変更されません。';
 }catch(ex){message.textContent='読込拒否: '+ex.message;}
};
document.querySelectorAll('button.mode').forEach(button=>button.addEventListener('click',()=>{
 displayMode=button.dataset.mode;document.querySelectorAll('button.mode').forEach(b=>b.classList.toggle('secondary',b!==button));refresh();clearMarkers();
}));
</script></body></html>'''

def create_app(workspace:Workspace):
    app=FastAPI(title='HALO9 D28 local visual experiment')
    @app.get('/',response_class=HTMLResponse)
    def index():return HTML
    @app.get('/api/state')
    def state():return workspace.state()
    @app.get('/api/view/{view}')
    def view_png(view:str):
        with workspace.lock:
            if view not in VIEWS:raise HTTPException(404,'unknown view')
            return Response(content=workspace.images[view],media_type='image/png',headers={'Cache-Control':'no-store'})
    @app.get('/api/baseview/{view}')
    def base_view_png(view:str):
        with workspace.lock:
            if view not in VIEWS:raise HTTPException(404,'unknown view')
            return Response(content=workspace.base_images[view],media_type='image/png',headers={'Cache-Control':'no-store'})
    @app.get('/api/diffview/{view}')
    def diff_view_png(view:str):
        with workspace.lock:
            if view not in VIEWS:raise HTTPException(404,'unknown view')
            return Response(content=workspace.diff_images[view],media_type='image/png',headers={'Cache-Control':'no-store'})
    @app.post('/api/import')
    async def import_model(request:Request):
        if int(request.headers.get('content-length',0) or 0)>MAX_UPLOAD_BYTES:
            raise HTTPException(413,'GLB upload exceeds 16MB')
        raw=await request.body()
        try:
            with workspace.lock:return workspace.import_glb(raw)
        except ValueError as exc:raise HTTPException(422,str(exc))
    @app.post('/api/select')
    def select(body:dict=Body(...)):
        try:
            with workspace.lock:return workspace.select(body['view'],float(body['u']),float(body['v']))
        except (ValueError,KeyError,TypeError) as exc:raise HTTPException(422,str(exc))
    @app.post('/api/edit')
    def edit(body:dict=Body(...)):
        try:
            with workspace.lock:return workspace.commit_edit(body)
        except (ValueError,KeyError,TypeError) as exc:raise HTTPException(422,str(exc))
    @app.post('/api/undo')
    def undo(body:dict=Body(...)):
        try:
            with workspace.lock:return workspace.undo(body.get('revision'))
        except (ValueError,KeyError,TypeError) as exc:raise HTTPException(422,str(exc))
    @app.get('/artifact/{file}')
    def artifact(file:str):
        if file not in ('EDIT.glb','BASE.glb','EDIT_PLAN.json'):raise HTTPException(404)
        with workspace.lock:
            p=workspace.root/file
            return Response(content=p.read_bytes(),media_type='model/gltf-binary' if file.endswith('.glb') else 'application/json',headers={'Content-Disposition':f'attachment; filename="{file}"'})
    return app

def main():
    a=argparse.ArgumentParser();a.add_argument('--source',type=Path);a.add_argument('--output',type=Path,default=Path('D28_WORK'))
    a.add_argument('--port',type=int,default=8768);a.add_argument('--self-test',action='store_true');a.add_argument('--open',action='store_true')
    args=a.parse_args();w=Workspace(args.output,args.source)
    if args.self_test:
        print(json.dumps(w.state(),indent=2));return
    if args.open:
        import webbrowser
        threading.Timer(1.5,lambda: webbrowser.open(f'http://127.0.0.1:{args.port}')).start()
    uvicorn.run(create_app(w),host='127.0.0.1',port=args.port,log_level='warning')
if __name__=='__main__':main()