import bpy, pathlib, sys, json, hashlib
ROOT=pathlib.Path(__file__).parent
args=sys.argv[sys.argv.index('--')+1:];rev=args[0]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/('GATE_B_'+rev+'.blend')),load_ui=False,use_scripts=False)
S=bpy.context.scene;S.render.threads_mode='FIXED';S.render.threads=2
out=ROOT/rev;out.mkdir(exist_ok=True)
done=[]
for name in ['E11_NAVE_HUMAN','E11_H1_HUMAN','E11_URBAN_AERIAL']:
    S.camera=bpy.data.objects[name];S.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
    done.append(name);print('FIXED_VIEW_DONE',name,flush=True)
(out/'render_complete.json').write_text(json.dumps({'source_sha256':hashlib.sha256((ROOT/('GATE_B_'+rev+'.blend')).read_bytes()).hexdigest(),'cameras':done,'full_scene':True,'cutaway':False},indent=2))
