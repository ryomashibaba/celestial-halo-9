"""Minimal GLB (glTF 2.0 binary) writer + independent verifier. Z-up scene data -> glTF Y-up ((x,y,z)->(x,z,-y))."""
import json, struct, numpy as np
import c55a_city as C

COLL_ORDER = ['NAVE_MASSIF_NORTH', 'NAVE_MASSIF_SOUTH', 'APSE_SACRED_FACE', 'NAVE_FLOOR_CANAL', 'SEVEN_HALOS', 'SANCTUM_LENS',
              'FLOATING_DISTRICTS', 'OBSIDIAN_BLADES', 'BRIDGES_VEILS_BEAMS', 'PLAZA_DISTRICTS', 'LIGHT_DECALS',
              'GREAT_HALL_INTERIOR', 'TERRAIN_CONTEXT']


def write_glb(S, path):
    mats, mat_idx = [], {}
    for name, m in C.MATERIALS.items():
        base = list(m.get('base', (0, 0, 0))) + [m.get('alpha', 1.0)]
        emit = np.array(m.get('emit', (0, 0, 0)), float)
        spec = m.get('spec', 0.0)
        d = dict(name=name, pbrMetallicRoughness=dict(baseColorFactor=[float(x) for x in base], metallicFactor=0.85 if spec >= 0.5 else 0.0,
                                                      roughnessFactor=0.28 if spec >= 0.5 else (0.55 if spec > 0 else 0.85)))
        if emit.max() > 0:
            d['emissiveFactor'] = [float(x) for x in emit / emit.max()]
            d['extensions'] = {'KHR_materials_emissive_strength': {'emissiveStrength': float(emit.max())}}
        if m.get('alpha', 1.0) < 1.0:
            d['alphaMode'] = 'BLEND'
        d['doubleSided'] = True
        mat_idx[name] = len(mats)
        mats.append(d)
    binb = bytearray()
    bvs, accs, meshes, nodes = [], [], [], []
    coll_nodes = {}

    def pad():
        while len(binb) % 4:
            binb.append(0)

    for p in S.parts:
        V = p['V'].astype(np.float32)
        Vg = np.stack([V[:, 0], V[:, 2], -V[:, 1]], 1).astype(np.float32)
        F = p['F'].astype(np.uint32)
        pad(); o = len(binb); binb += Vg.tobytes()
        bvs.append(dict(buffer=0, byteOffset=o, byteLength=Vg.nbytes, target=34962))
        accs.append(dict(bufferView=len(bvs) - 1, componentType=5126, count=len(Vg), type='VEC3',
                         min=[float(x) for x in Vg.min(0)], max=[float(x) for x in Vg.max(0)]))
        pa = len(accs) - 1
        pad(); o = len(binb); binb += F.tobytes()
        bvs.append(dict(buffer=0, byteOffset=o, byteLength=F.nbytes, target=34963))
        accs.append(dict(bufferView=len(bvs) - 1, componentType=5125, count=int(F.size), type='SCALAR'))
        ia = len(accs) - 1
        meshes.append(dict(name=p['name'], primitives=[dict(attributes={'POSITION': pa}, indices=ia, material=mat_idx[p['mat']], mode=4)]))
        nodes.append(dict(name=p['name'], mesh=len(meshes) - 1,
                          extras=dict(collection=p['coll'], material=p['mat'], interior=bool(p['interior']), context=bool(p['context']))))
        coll_nodes.setdefault(p['coll'], []).append(len(nodes) - 1)
    roots = []
    for cname in COLL_ORDER + [c for c in coll_nodes if c not in COLL_ORDER]:
        if cname in coll_nodes:
            nodes.append(dict(name=cname, children=coll_nodes[cname]))
            roots.append(len(nodes) - 1)
    pad()
    gltf = dict(asset=dict(version='2.0', generator='C55-A Claude Sonnet 5.5 procedural generator (no Blender)',
                           extras=dict(project='CELESTIAL HALO-9 independent research C55-A', concept='七環天裂都 / Sevenfold Halo Rift',
                                       units='metres', source_axes='Z-up (converted to glTF Y-up on export)')),
                extensionsUsed=['KHR_materials_emissive_strength'], scene=0, scenes=[dict(name='C55A', nodes=roots)],
                nodes=nodes, meshes=meshes, materials=mats, accessors=accs, bufferViews=bvs, buffers=[dict(byteLength=len(binb))])
    js = json.dumps(gltf, separators=(',', ':')).encode()
    while len(js) % 4:
        js += b' '
    total = 12 + 8 + len(js) + 8 + len(binb)
    with open(path, 'wb') as f:
        f.write(struct.pack('<III', 0x46546C67, 2, total))
        f.write(struct.pack('<II', len(js), 0x4E4F534A)); f.write(js)
        f.write(struct.pack('<II', len(binb), 0x004E4942)); f.write(binb)
    return total


def verify_glb(path):
    """Independent re-read: header, JSON, accessor bounds, index ranges, finiteness, triangle/vertex totals."""
    raw = open(path, 'rb').read()
    magic, ver, total = struct.unpack('<III', raw[:12])
    assert magic == 0x46546C67 and ver == 2 and total == len(raw), 'bad header'
    jl, jt = struct.unpack('<II', raw[12:20]); assert jt == 0x4E4F534A
    gl = json.loads(raw[20:20 + jl])
    off = 20 + jl
    bl, bt = struct.unpack('<II', raw[off:off + 8]); assert bt == 0x004E4942
    binb = memoryview(raw)[off + 8:off + 8 + bl]
    tris = verts = bad_idx = nonfinite = degenerate = 0
    mn = np.full(3, np.inf); mx = np.full(3, -np.inf)
    for m in gl['meshes']:
        pr = m['primitives'][0]
        pa = gl['accessors'][pr['attributes']['POSITION']]; ia = gl['accessors'][pr['indices']]
        pv = gl['bufferViews'][pa['bufferView']]; iv = gl['bufferViews'][ia['bufferView']]
        P = np.frombuffer(binb[pv['byteOffset']:pv['byteOffset'] + pv['byteLength']], np.float32).reshape(-1, 3)
        I = np.frombuffer(binb[iv['byteOffset']:iv['byteOffset'] + iv['byteLength']], np.uint32)
        assert len(P) == pa['count'] and len(I) == ia['count']
        if I.max() >= len(P): bad_idx += 1
        if not np.isfinite(P).all(): nonfinite += 1
        T = P[I.reshape(-1, 3)].astype(np.float64)
        ar = np.linalg.norm(np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]), axis=1)
        degenerate += int((ar < 1e-9).sum())
        tris += len(I) // 3; verts += len(P)
        mn = np.minimum(mn, P.min(0)); mx = np.maximum(mx, P.max(0))
    return dict(file_bytes=len(raw), meshes=len(gl['meshes']), nodes=len(gl['nodes']), materials=len(gl['materials']),
                triangles=tris, vertices=verts, meshes_with_bad_indices=bad_idx, meshes_with_nonfinite=nonfinite,
                degenerate_triangles=degenerate, bbox_gltf_yup_min=[float(x) for x in mn], bbox_gltf_yup_max=[float(x) for x in mx])
