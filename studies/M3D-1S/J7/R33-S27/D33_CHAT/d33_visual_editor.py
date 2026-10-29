#!/usr/bin/env python3
"""D33 isolated art-direction workbench: real GLB <-> 7x7 surface control cages.
Browser: interactive rotating 3D projection, selectable cage handles, edit/export/undo.
No Blender native file, no Minecraft world, no formal architectural certification.
"""
import copy, json, math, hashlib, threading, argparse, base64, io
from pathlib import Path
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import plotly.offline
from d33_sculpt import sculpt_mesh, build, initial_guides
from d33_render import render as render_real_glb, VIEWS
from PIL import Image

ROOT=Path(__file__).resolve().parent
EXPORTS=ROOT/'runtime_exports'
BASE_CAGE=ROOT/'D33_BASE_CAGE.json'
BASE_GLB=ROOT/'D33_BASE_ART_STUDY.glb'
COLORS={'MAIN_SHEAR':'#B7AFA0','HANGING_CROWN':'#8BAFC4','LOWER_BUTTRESS':'#73869B'}

class EditPoint(BaseModel):
    revision:int
    object:str
    i:int
    j:int
    x:float
    y:float
    z:float

class Reversion(BaseModel):
    revision:int

class Editor:
    def __init__(self,root=ROOT):
        self.root=root
        self.export=root/'runtime_exports'
        self.export.mkdir(parents=True,exist_ok=True)
        self.base=json.loads((root/'D33_BASE_CAGE.json').read_text(encoding='utf-8'))
        self.current=copy.deepcopy(self.base)
        self.history=[]
        self.revision=0
        self.lock=threading.Lock()
        self.base_sha=hashlib.sha256((root/'D33_BASE_ART_STUDY.glb').read_bytes()).hexdigest()
        self.export_file=root/'D33_BASE_ART_STUDY.glb'

    def mesh(self,plan):
        res={}
        for name,spec in plan['objects'].items():
            m=sculpt_mesh(spec,tile=16)
            v=np.asarray(m.vertices,dtype=float).round(3).tolist()
            faces=np.asarray(m.faces).tolist()
            res[name]={'vertices':v,'faces':faces,'color':COLORS[name]}
        return res

    def state(self,full=False):
        state={'revision':self.revision,'names':list(self.current['objects']),
            'controls':{n:self.current['objects'][n]['cage'] for n in self.current['objects']},
            'undo_available':bool(self.history),'export_url':'/api/export',
            'cage_url':'/api/cage','source_sha256':self.base_sha}
        if full:
            state['meshes']=self.mesh(self.current)
            state['base_meshes']=self.mesh(self.base)
        return state

    def _save(self):
        fn=self.export/f'D33_EDIT_r{self.revision:04d}.glb'
        result=build(self.current,fn)
        if not all(o['watertight'] for o in result['geometry'].values()):
            fn.unlink(missing_ok=True)
            raise ValueError('Mesh failed watertightness test')
        planfile=self.export/f'D33_EDIT_r{self.revision:04d}_CAGE.json'
        planfile.write_text(json.dumps(self.current,ensure_ascii=False,indent=2),encoding='utf-8')
        self.export_file=fn
        return result

    def edit(self,p):
        with self.lock:
            if p.revision!=self.revision:raise ValueError('Stale editor revision: refresh')
            if p.object not in self.current['objects']:raise ValueError('Unknown object')
            if isinstance(p.i,bool) or isinstance(p.j,bool) or not (0<=p.i<7 and 0<=p.j<7):raise ValueError('Invalid cage index')
            xyz=np.asarray([p.x,p.y,p.z],dtype=float)
            if not np.isfinite(xyz).all():raise ValueError('Non-finite point coordinate')
            old=np.array(self.current['objects'][p.object]['cage'][p.i][p.j],dtype=float)
            if np.linalg.norm(xyz-old)>400 or np.linalg.norm(xyz)>6000:raise ValueError('Edit exceeds safe cage bounds')
            backup=copy.deepcopy(self.current)
            self.current['objects'][p.object]['cage'][p.i][p.j]=xyz.round(5).tolist()
            try:
                new_rev=self.revision+1
                self.revision=new_rev
                result=self._save()
            except Exception:
                self.current=backup
                self.revision-=1
                raise
            self.history.append(backup)
            # Immutable original: ensure source still matches expected hash
            assert hashlib.sha256((self.root/'D33_BASE_ART_STUDY.glb').read_bytes()).hexdigest()==self.base_sha
            return {'revision':self.revision,'model':result,'state':self.state(full=True)}

    def undo(self,revision):
        with self.lock:
            if revision!=self.revision:raise ValueError('Stale revision')
            if not self.history:raise ValueError('No history')
            self.current=self.history.pop()
            self.revision+=1
            result=self._save()
            return {'revision':self.revision,'model':result,'state':self.state(full=True)}


def create_app(root=ROOT):
    ed=Editor(root)
    app=FastAPI(title='HALO-9 D33 Isolated Sculpt Research',docs_url=None,redoc_url=None)
    app.state.ed=ed
    @app.get('/',response_class=HTMLResponse)
    def index():return (root/'D33_EDITOR.html').read_text(encoding='utf-8')
    @app.get('/vendor/plotly.min.js')
    def plotlyjs():
        return FileResponse(root/'plotly.min.js',media_type='text/javascript')
    @app.get('/api/state')
    def get_state():return ed.state(full=True)
    @app.post('/api/edit')
    def edit(p:EditPoint):
        try:return ed.edit(p)
        except ValueError as e:raise HTTPException(status_code=400,detail=str(e))
    @app.post('/api/undo')
    def undo(p:Reversion):
        try:return ed.undo(p.revision)
        except ValueError as e:raise HTTPException(status_code=400,detail=str(e))
    @app.get('/api/previews')
    def previews():
        if ed.revision:
            folder=ed.export/f'D33_EDIT_r{ed.revision:04d}_VIEWS'
        else:
            folder=root/'D33_BASE_VIEWS'
        if not all((folder/(name+'.png')).exists() for name in VIEWS):
            render_real_glb(ed.export_file,folder)
        imgs=[]
        for name in VIEWS:
            with Image.open(folder/(name+'.png')) as im:
                im=im.convert('RGB');im.thumbnail((520,350))
                buf=io.BytesIO();im.save(buf,format='JPEG',quality=81)
                data=base64.b64encode(buf.getvalue()).decode('ascii')
                imgs.append({'view':name,'data_uri':'data:image/jpeg;base64,'+data})
        return {'revision':ed.revision,'renderer':'VTK / actual saved GLB','images':imgs}
    @app.get('/api/export')
    def export():return FileResponse(ed.export_file,filename=ed.export_file.name,media_type='model/gltf-binary')
    @app.get('/api/cage')
    def cage():return FileResponse(ed.export/f'D33_EDIT_r{ed.revision:04d}_CAGE.json',filename='D33_EDIT_CAGE.json') if ed.revision else FileResponse(root/'D33_BASE_CAGE.json',filename='D33_BASE_CAGE.json')
    return app

if __name__=='__main__':
    import uvicorn
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8843);args=parser.parse_args()
    uvicorn.run(create_app(),host='127.0.0.1',port=args.port,log_level='warning')
