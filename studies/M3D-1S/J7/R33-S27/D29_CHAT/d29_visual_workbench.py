#!/usr/bin/env python3
"""D29 extension of D28 visual editor: local orthogonal solid carving + six real GLB views.
Local isolated research, not an editable full city/Blender replacement.
"""
import argparse,json,io,threading
from pathlib import Path
import d28_visual_workbench as d28
from d29_orthogonal_csg import fixture_glb,carve_glb,load_checked,sha,TARGET,MAX_BOXES,valid_voids
from fastapi import HTTPException,Body
import uvicorn

class D29Workspace(d28.Workspace):
    def __init__(self,root,source=None):
        root=Path(root)
        data=json.loads((root/'EDIT_PLAN.json').read_text('utf-8')) if (root/'EDIT_PLAN.json').exists() else {}
        self.cuts=list(data.get('cut_ops',[]))
        self.history=list(data.get('action_history',[]))
        super().__init__(root,source)
    def _rebuild(self):
        base=self._cut_bytes(self.cuts)
        edited=d28.apply_recipe(base,self.ops) if self.ops else base
        self.edited=edited
        self.current_path.write_bytes(edited)
        self.recipe_path.write_text(json.dumps({'study':'D29','base_sha256':sha(self.raw),
          'operations':self.ops,'cut_ops':self.cuts,'action_history':self.history,
          'limitations':'axis-aligned single box carving; not general CSG or certified construction'},indent=2)+'\n')
        scene=d28.load_scene(edited)
        self.images={v:d28.render(scene,v).png for v in d28.VIEWS}
        import numpy as np
        from PIL import Image
        self.diff_images={};self.pixel_changes={}
        for key in d28.VIEWS:
            a=np.asarray(Image.open(io.BytesIO(self.base_images[key])).convert('RGB'),dtype=np.int16)
            b=np.asarray(Image.open(io.BytesIO(self.images[key])).convert('RGB'),dtype=np.int16)
            changed=np.max(np.abs(a-b),axis=2)>20
            self.pixel_changes[key]=round(float(changed.mean()*100),3)
            overlay=b.astype(np.uint8).copy()
            overlay[changed]=(.35*overlay[changed]+.65*np.array([250,112,90])).astype(np.uint8)
            output=io.BytesIO();Image.fromarray(overlay).save(output,format='PNG')
            self.diff_images[key]=output.getvalue()
        self.revision=sha(self.edited)
    def _cut_bytes(self,cuts):
        if not cuts:return self.raw
        plan={'baseline_sha256':sha(self.raw),'target_geometry':TARGET,'voids':cuts}
        return carve_glb(self.raw,plan)
    def state(self):
        s=super().state();s['study']='D29';s['cut_count']=len(self.cuts)
        s['topology_changed']=bool(self.cuts);s['action_history']=self.history.copy()
        s['source_is_supported_box']=TARGET in d28.load_scene(self.raw).geometry
        return s
    def commit_cut(self,body):
        if body.get('revision')!=self.revision:raise ValueError('stale edit revision')
        if self.ops:raise ValueError('cut existing mass before sculpt strokes; undo existing strokes first')
        if len(self.cuts)>=MAX_BOXES:raise ValueError('maximum 3 orthogonal cuts')
        box=body.get('box')
        candidate=self.cuts+[box]
        result=self._cut_bytes(candidate) # validate and readback before mutations
        old=self.cuts; oldh=self.history
        try:
            self.cuts=candidate;self.history=oldh+['cut'];self._rebuild()
            if result!=self.edited:raise ValueError('rebuild mismatch')
        except Exception:
            self.cuts=old;self.history=oldh;self._rebuild();raise
        self.selected=None
        return self.state()
    def commit_edit(self,body):
        if body.get('revision')!=self.revision:raise ValueError('stale revision')
        if not self.selected:raise ValueError('select vertex')
        if self.selected['geometry'] in self.protected:raise ValueError('protected public route')
        step={'geometry':self.selected['geometry'],'vertex_id':self.selected['vertex_id'],
          'radius_m':body.get('radius_m'),'delta_xyz_m':body.get('delta_xyz_m')}
        candidate=self.ops+[step]
        expected=d28.apply_recipe(self._cut_bytes(self.cuts),candidate)
        old=self.ops;oldh=self.history
        try:
            self.ops=candidate;self.history=oldh+['brush'];self._rebuild()
            if self.edited!=expected:raise ValueError('rebuild mismatch')
        except Exception:
            self.ops=old;self.history=oldh;self._rebuild();raise
        self.selected=None
        return self.state()
    def undo(self,revision):
        if revision!=self.revision:raise ValueError('stale revision')
        if not self.history:raise ValueError('no edit to undo')
        k=self.history.pop()
        if k=='brush':self.ops.pop()
        elif k=='cut':self.cuts.pop()
        else:raise ValueError('corrupted action history')
        self._rebuild();self.selected=None
        return self.state()
    def import_glb(self,blob):
        if self.cuts:raise ValueError('undo all void edits before importing')
        return super().import_glb(blob)

extra_html='''<hr style="border:0;border-top:1px solid #30475a;margin:16px 0"/>
<b>D29：実メッシュへ公共空洞を切る</b>
<p class="muted" style="font-size:12px">MASS_TESTという直方体メッシュのみ対応。入口→公開室→天窓の順に、既存三角形の位相を再構築。Minecraft施工とは無関係。</p>
<div class="pair"><button class="secondary" id="cut_entry">1. 南入口を切断</button><button class="secondary" id="cut_room">2. 公共室を切断</button></div>
<button class="secondary" id="cut_roof" style="margin-top:7px;width:100%">3. 天窓を開ける</button>
<label>任意直方体の下限 X/Y/Z（m）</label>
<div class="triple"><input id="bx0" type="number" value="-95"/><input id="by0" type="number" value="-270"/><input id="bz0" type="number" value="40"/></div>
<label>上限 X/Y/Z（m）</label><div class="triple"><input id="bx1" type="number" value="95"/><input id="by1" type="number" value="-130"/><input id="bz1" type="number" value="185"/></div>
<button class="secondary" id="cut_custom" style="margin-top:7px;width:100%">入力した直方体を切断</button>
<p class="muted" style="font-size:12px">最大3個まで。非直方体や建築安全性は未対応。選択不要、形状を事前に確認してください。</p>
'''
script='''
async function cutD29(box){try{
 message.textContent='実メッシュの位相を再構築しています…';
 state=await post('/api/cut',{revision:state.revision,box:box});
 refresh();clearMarkers();message.textContent='実GLBを再構成し6視点を更新しました。';
}catch(e){message.textContent='切断拒否: '+e.message;}}
const presets={entry:{min:[-95,-270,40],max:[95,-130,185]},room:{min:[-210,-155,40],max:[230,165,265]},roof:{min:[-60,-45,250],max:[70,90,380]}};
const previousRefresh=refresh;
refresh=function(){previousRefresh();
 document.getElementById('status').textContent=`公共空洞 ${state.cut_count}個 / ブラシ ${state.operations}回 / GLB SHA256 ${state.revision.slice(0,14)}…`;
 document.getElementById('undo').disabled=state.action_history.length===0;
};
for(const [id,box] of Object.entries(presets)){document.getElementById('cut_'+id).onclick=()=>cutD29(box);}
document.getElementById('cut_custom').onclick=()=>cutD29({min:['bx0','by0','bz0'].map(k=>Number(document.getElementById(k).value)),max:['bx1','by1','bz1'].map(k=>Number(document.getElementById(k).value))});
'''
D29_HTML=d28.HTML.replace('D28 Visual Sculpt Workbench','D29 Topology + Visual Workbench').replace('D28 — Visual Sculpt Workbench','D29 — Topology + Visual Workbench')
D29_HTML=D29_HTML.replace('<div id="message"></div>',extra_html+'<div id="message"></div>')
D29_HTML=D29_HTML.replace('</script>',script+'</script>')

def create_app(ws):
    d28.HTML=D29_HTML
    app=d28.create_app(ws)
    @app.post('/api/cut')
    def cut(box:dict=Body(...)):
        try:
            with ws.lock:return ws.commit_cut(box)
        except (ValueError,KeyError,TypeError) as e:raise HTTPException(422,str(e))
    return app

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=Path('D29_WORK'));p.add_argument('--source',type=Path)
    p.add_argument('--port',type=int,default=8769);p.add_argument('--open',action='store_true')
    args=p.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    if not args.source and not (args.output/'BASE.glb').exists():
        # Only the local, isolated demo fixture. No protected models touched.
        src=args.output.parent/(args.output.name+'_SOURCE.glb')
        if not src.exists():src.write_bytes(fixture_glb())
        args.source=src
    w=D29Workspace(args.output,args.source)
    if args.open:
        import webbrowser
        threading.Timer(1.5,lambda:webbrowser.open('http://127.0.0.1:'+str(args.port))).start()
    uvicorn.run(create_app(w),host='127.0.0.1',port=args.port,log_level='warning')
if __name__=='__main__':main()
