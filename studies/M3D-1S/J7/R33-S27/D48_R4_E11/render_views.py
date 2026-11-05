"""True Blender CPU renders, isolated scene, two threads, no live GUI render window."""
import bpy,sys,pathlib,json,time,hashlib
root=pathlib.Path(__file__).parent
args=sys.argv[sys.argv.index('--')+1:]
version,width,samples=args[:3]
names=args[3:] or ['E11_NAVE_HUMAN','E11_H1_HUMAN','E11_URBAN_AERIAL']
s=bpy.data.scenes['E11_INHABITED_SECTION_RESEARCH'];bpy.context.window.scene=s
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=int(samples);s.cycles.use_denoising=True
s.render.threads_mode='FIXED';s.render.threads=2
s.render.resolution_x=int(width);s.render.resolution_y=int(int(width)*.75);s.render.resolution_percentage=100
out=root/version;out.mkdir(exist_ok=True)
report=[]
for name in names:
    s.camera=bpy.data.objects[name];s.render.filepath=str(out/(name+'.png'))
    start=time.monotonic();bpy.ops.render.render(write_still=True)
    p=pathlib.Path(s.render.filepath)
    report.append({'camera':name,'location':list(s.camera.location),'matrix':[list(r) for r in s.camera.matrix_world],
                   'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'seconds':time.monotonic()-start})
    (out/'render_manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('E11_TRUE_RENDER_COMPLETE',version,len(report),flush=True)
