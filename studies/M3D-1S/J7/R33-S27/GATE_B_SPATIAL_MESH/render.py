import bpy,pathlib,sys,json,hashlib
R=pathlib.Path(__file__).parent;args=sys.argv[sys.argv.index('--')+1:];rev=args[0]
bpy.ops.wm.open_mainfile(filepath=str(R/('SPATIAL_'+rev+'.blend')),load_ui=False,use_scripts=False)
S=bpy.context.scene;S.render.threads_mode='FIXED';S.render.threads=2
out=R/rev;out.mkdir(exist_ok=True);names=args[1:] or ['E11_NAVE_HUMAN','E11_H1_HUMAN','E11_URBAN_AERIAL']
for name in names:
    S.camera=bpy.data.objects[name];S.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);print('REAL_IMAGE_SAVED',name,flush=True)
(out/'render.json').write_text(json.dumps({'blend_sha256':hashlib.sha256((R/('SPATIAL_'+rev+'.blend')).read_bytes()).hexdigest(),'cameras':names,'full_scene':True,'cutaway':False},indent=2),encoding='utf8',newline='\n')
