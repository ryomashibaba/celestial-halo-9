import sys, time, json, numpy as np
import c55a_city as C, c55a_render as R, views

if __name__ == '__main__':
    W = int(sys.argv[1]); H = int(sys.argv[2]); SS = int(sys.argv[3]); outdir = sys.argv[4]; only = sys.argv[5:]
    t0 = time.time()
    S = C.build_scene()
    A = R.assemble(S, False)
    hf = R.make_heightfield(S)
    lit = R.compute_lighting(A, hf)
    Ai = R.assemble(S, True)
    liti = R.compute_lighting_interior(Ai)
    print('prep', round(time.time() - t0, 1), 'ext faces', len(A['mid']), 'int faces', len(Ai['mid']), flush=True)
    stats = []
    for name, cam, ex, interior in views.get_views(S, W, H):
        if only and not any(o in name for o in only): continue
        if interior:
            img, st = R.render(Ai, liti, cam, exposure=ex, SS=SS, interior=True, label=name)
        else:
            img, st = R.render(A, lit, cam, exposure=ex, SS=SS, label=name)
        img.save(f'{outdir}/{name}.png')
        st['camera_pos'] = [round(float(x), 1) for x in cam.pos]
        stats.append(st)
        print(st, flush=True)
    json.dump(stats, open(f'{outdir}/_render_stats.json', 'w'), indent=1)
