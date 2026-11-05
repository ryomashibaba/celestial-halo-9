"""HALO-9 / LCS1 — occupied civic rift: a NEW research intervention.

Loads the verified E12 COPY, strips its rejected polygonal replacements,
keeps the useful E11 civic interiors, and AUTHORS ONE CONNECTED SECTION:
NAVE (station/library/ceremony) -> accessible lift/terraces -> H1 inhabited
school/street/shops -> W0 tiered estuary port. No authoritative world coords.
No artistic adoption, Minecraft writes, use of paid services, or master writes.
"""
import bpy, math, sys, json, hashlib, time
from pathlib import Path
from mathutils import Vector
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
out = Path(argv[argv.index('--output') + 1]) if '--output' in argv else Path('/tmp/halo9_lcs1')
out.mkdir(parents=True, exist_ok=True)
(out / 'renders').mkdir(exist_ok=True)
source = Path(bpy.data.filepath)
assert source.name == 'LCS1_E12_SOURCE.blend', source
assert hashlib.sha256(source.read_bytes()).hexdigest() == 'ba3363c0908bbf0b4d61afb1d4497af8696364c60b97eac754f351249ccb3c19'
S = bpy.context.scene
assert S['CONSTRUCTION'] == 'HOLD' and S['FORMAL_ART_ACCEPTED'] == 0 and (S['COMPLETED_TARGETS'] == 0)
cameras = {n: bpy.data.objects[n].matrix_world.copy() for n in ('E11_NAVE_HUMAN', 'E11_H1_HUMAN', 'E11_URBAN_AERIAL')}
deleted = []
for o in tuple(S.objects):
    if any((c.name == 'E12_SUBTRACTIVE_CIVIC_MASTER_UNAPPROVED' for c in o.users_collection)) or o.name.startswith('H1_SOUTH_HABITABLE_CLIFF'):
        deleted.append(o.name)
        bpy.data.objects.remove(o, do_unlink=True)
assert len(deleted) >= 7, len(deleted)
C = bpy.data.collections.new('LCS1_FUNCTION_FIRST_OCCUPIED_RIFT_RESEARCH')
S.collection.children.link(C)

def mat(name, rgb, metal=0.0, rough=0.5, emit=0.0):
    m = bpy.data.materials.new('LCS1_' + name)
    m.diffuse_color = (*rgb, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*rgb, 1)
    p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metal
    if emit:
        p.inputs['Emission Color'].default_value = (*rgb, 1)
        p.inputs['Emission Strength'].default_value = emit
    return m
M = {'chalk': mat('chalk_formed_civic_concrete', (0.62, 0.72, 0.71), 0.1, 0.57), 'bone': mat('warm_public_limestone', (0.78, 0.7, 0.54), 0.04, 0.7), 'slate': mat('rift_shadow_basalt', (0.06, 0.12, 0.16), 0.28, 0.49), 'steel': mat('aged_champagne_titanium', (0.35, 0.41, 0.39), 0.6, 0.32), 'copper': mat('patinated_copper', (0.43, 0.3, 0.15), 0.6, 0.35), 'glass': mat('deep_teal_reflecting_glass', (0.035, 0.27, 0.32), 0.31, 0.18), 'water': mat('tidal_pools', (0.025, 0.17, 0.2), 0.3, 0.22), 'light': mat('inhabited_warm_light', (0.95, 0.56, 0.24), 0.12, 0.29, 1.25), 'way': mat('wayfinding_glow', (0.23, 0.78, 0.83), 0.2, 0.29, 1.8), 'green': mat('gardens', (0.11, 0.29, 0.17), 0, 0.89), 'street': mat('warm_paving', (0.39, 0.47, 0.44), 0.08, 0.75), 'roof': mat('titanium_roof', (0.3, 0.39, 0.42), 0.48, 0.35)}

def mesh(name, vs, fs, key):
    me = bpy.data.meshes.new(name)
    me.from_pydata(vs, [], fs)
    me.update()
    o = bpy.data.objects.new('LCS1_' + name, me)
    C.objects.link(o)
    me.materials.append(M[key])
    return o

def slab(name, p, z, depth, key):
    assert len(p) >= 3
    n = len(p)
    v = [(x, y, z - depth) for x, y in p] + [(x, y, z) for x, y in p]
    f = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))]
    f += [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)]
    return mesh(name, v, f, key)

def block(name, ctr, dim, key):
    x, y, z = ctr
    dx, dy, dz = [v / 2 for v in dim]
    v = [(x + u * dx, y + v * dy, z + w * dz) for w in (-1, 1) for u, v in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    return mesh(name, v, [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)], key)

def beam(name, a, b, width, height, key):
    a, b = (Vector(a), Vector(b))
    d = b - a
    assert d.length > 0.01
    q = d.to_track_quat('Z', 'Y')
    v = []
    for t in (0, 1):
        for xx, yy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            v.append(tuple(a + q @ Vector((xx * width / 2, yy * height / 2, t * d.length))))
    return mesh(name, v, [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)], key)

def route(name, pts, width, depth, key):
    vs = []
    n = len(pts)
    assert n > 1
    for i, (x, y, z) in enumerate(pts):
        d = Vector(pts[min(i + 1, n - 1)]) - Vector(pts[max(0, i - 1)])
        L = math.hypot(d.x, d.y)
        ux, uy = (-d.y / L, d.x / L) if L > 0.01 else (1, 0)
        vs.extend([(x + sign * ux * width / 2, y + sign * uy * width / 2, z - dz) for dz in (0, depth) for sign in (-1, 1)])
    fs = []
    for i in range(n - 1):
        a = 4 * i
        b = 4 * (i + 1)
        fs.extend([(a, b, b + 1, a + 1), (a + 2, a + 3, b + 3, b + 2), (a, a + 2, b + 2, b), (a + 1, b + 1, b + 3, a + 3)])
    fs.extend([(0, 1, 3, 2), (4 * n - 4, 4 * n - 2, 4 * n - 1, 4 * n - 3)])
    return mesh(name, vs, fs, key)

def stair(name, a, b, n, width, key):
    for j in range(n):
        t0 = j / n
        t1 = (j + 1) / n
        x = a[0] + (b[0] - a[0]) * t0
        y = a[1] + (b[1] - a[1]) * t0
        x2 = a[0] + (b[0] - a[0]) * t1
        y2 = a[1] + (b[1] - a[1]) * t1
        d = Vector((x2 - x, y2 - y))
        d.normalize()
        nx, ny = (-d.y * width / 2, d.x * width / 2)
        slab(name + '_tread_' + str(j), [(x + nx, y + ny), (x - nx, y - ny), (x2 - nx, y2 - ny), (x2 + nx, y2 + ny)], a[2] + (b[2] - a[2]) * t1, 1.6, key)

def rail(name, pts, raise_z, key='steel'):
    elevated = [(x, y, z + raise_z) for x, y, z in pts]
    for i in range(len(elevated) - 1):
        beam(name + '_r' + str(i), elevated[i], elevated[i + 1], 1.6, 1.8, key)
    for i in range(len(elevated)):
        beam(name + '_p' + str(i), pts[i], elevated[i], 1.1, 1.1, key)
slab('nave_confluence_station', [(35, -335), (176, -326), (245, -210), (232, -75), (120, -29), (55, -112)], 115, 9, 'street')
slab('nave_station_upper_concourse', [(82, -290), (165, -305), (230, -212), (220, -119), (140, -81), (90, -170)], 143, 6, 'bone')
for i, (x, y) in enumerate([(74, -290), (180, -298), (229, -157), (122, -75)]):
    beam('station_open_truss_' + str(i), (x, y, 111), (x + (i - 2) * 7, y + 6, 185), 7, 6, 'steel')
slab('station_north_canopy', [(70, -310), (159, -326), (194, -225), (140, -160), (90, -184)], 188, 5, 'roof')
slab('station_south_canopy', [(210, -213), (247, -166), (241, -89), (154, -59), (166, -155)], 194, 5, 'chalk')
for i in range(5):
    beam('train_platform_edge_' + str(i), (48 + i * 15, -340, 117), (48 + i * 15, -310, 117), 0.8, 1.0, 'way')
slab('nave_library_reading_floor', [(-356, -312), (-217, -295), (-194, -155), (-230, -16), (-320, 39), (-390, -92)], 162, 7, 'bone')
slab('nave_library_mezzanine', [(-365, -225), (-278, -216), (-255, -103), (-315, -38), (-370, -97)], 204, 5, 'chalk')
for i, (x, y) in enumerate([(-362, -175), (-342, -115), (-310, -63), (-260, -137)]):
    beam('library_tree_column_trunk_' + str(i), (x, y, 135), (x, y, 217), 3.4, 4, 'steel')
    for j, (dx, dy) in enumerate([(18, 12), (-15, 17)]):
        beam('library_tree_branch_%d_%d' % (i, j), (x, y, 190), (x + dx, y + dy, 226), 2.3, 2.4, 'steel')
for j, (x, y) in enumerate([(-345, -209), (-330, -155), (-310, -107), (-285, -86), (-260, -180)]):
    block('reading_room_bookshelf_' + str(j), (x, y, 179), (4, 26, 33), 'copper')
slab('nave_ceremony_hanging_choir', [(-132, 100), (-43, 60), (107, 92), (148, 199), (32, 230), (-101, 199)], 270, 8, 'chalk')
for j in range(6):
    beam('choir_daylight_fin_' + str(j), (-115 + j * 42, 174, 273), (-90 + j * 36, 220, 335), 4, 8, 'steel')
route('station_to_forum', [(92, -312, 114), (74, -229, 108), (12, -161, 89), (-21, -80, 75)], 18, 5, 'street')
route('forum_to_library', [(-95, -222, 78), (-155, -192, 91), (-213, -166, 131), (-255, -133, 162)], 14, 4, 'street')
stair('library_entrance_stair', (-171, -179, 93), (-230, -140, 162), 12, 10, 'bone')
route('forum_to_ceremony', [(-55, 17, 76), (-86, 81, 110), (-72, 146, 183), (-50, 174, 268)], 18, 6, 'chalk')
for i, (x, y, z, xx, yy, zz) in enumerate([(-385, 65, 84, -315, 365, 550), (-240, 195, 170, -135, 430, 750), (320, -20, 90, 260, 420, 710), (405, 135, 180, 355, 575, 910)]):
    beam('inhabited_rift_nonparallel_strut_' + str(i), (x, y, z), (xx, yy, zz), 13 + i * 2, 16, 'slate')
route('water_nave_access', [(-165, -612, 35), (-90, -540, 57), (-34, -453, 71), (20, -383, 74)], 24, 7, 'bone')
route('nave_h1_public_route', [(220, 55, 190), (312, 135, 225), (387, 201, 300), (450, 236, 365), (520, 276, 430), (592, 300, 437)], 24, 7, 'street')
rail('nave_h1_route_guard', [(220, 75, 190), (312, 155, 225), (387, 221, 300), (450, 256, 365), (520, 296, 430), (592, 320, 437)], 6)
for i, ((x, y, z), (xx, yy, zz)) in enumerate([((292, 137, 222), (292, 137, 88)), ((410, 219, 340), (411, 218, 125)), ((520, 276, 424), (520, 276, 228))]):
    beam('public_transfer_structure_' + str(i), (x, y, z), (xx, yy, zz), 9, 10, 'slate')
for i, (x, y) in enumerate([(443, 180), (467, 200)]):
    beam('lift_track_' + str(i), (x, y, 75), (x, y, 444), 3, 5, 'steel')
block('open_public_lift_car', (455, 190, 265), (22, 28, 14), 'glass')
slab('lift_public_lower_landing', [(422, 165), (486, 184), (471, 222), (423, 207)], 82, 6, 'bone')
slab('lift_public_upper_landing', [(419, 171), (488, 191), (477, 231), (422, 209)], 438, 8, 'bone')
slab('h1_public_street', [(739, 270), (806, 270), (820, 716), (746, 720)], 439, 7, 'street')
slab('h1_sky_lane_west', [(578, 325), (654, 300), (724, 329), (722, 686), (631, 707), (590, 642)], 443, 11, 'bone')
slab('h1_school_and_civic_east_quarter', [(827, 302), (949, 274), (1030, 351), (1013, 594), (922, 678), (845, 622)], 441, 14, 'chalk')
route('h1_braided_upper_street', [(610, 372, 457), (666, 409, 473), (715, 456, 491), (776, 535, 505), (848, 576, 517), (929, 609, 525)], 19, 5, 'chalk')
route('h1_upper_lane_feeder', [(708, 460, 439), (726, 485, 461), (748, 518, 488), (777, 531, 505)], 12, 4, 'bone')
rail('h1_sky_lane_railing', [(610, 384, 457), (665, 421, 473), (714, 467, 491), (777, 547, 505), (848, 587, 517), (929, 622, 525)], 5)
slab('h1_library_ground', [(586, 360), (711, 345), (731, 424), (703, 521), (600, 531), (575, 456)], 447, 7, 'bone')
slab('h1_library_upper_reading', [(589, 385), (675, 369), (695, 421), (672, 490), (596, 498)], 474, 6, 'chalk')
for j, (x, y) in enumerate([(592, 384), (684, 368), (700, 464), (596, 488)]):
    beam('h1_library_fork_column_' + str(j), (x, y, 447), (x + 5, y + 9, 521), 4.5, 7, 'steel')
slab('h1_library_west_roof', [(575, 373), (642, 357), (651, 487), (582, 512)], 520, 5, 'roof')
slab('h1_library_east_roof', [(663, 349), (711, 363), (735, 478), (684, 500)], 537, 5, 'roof')
for i in range(4):
    block('h1_library_shelf_' + str(i), (613 + i * 15, 420, 460), (3, 43, 23), 'copper')
slab('h1_school_play_court', [(855, 405), (981, 407), (997, 553), (868, 571)], 442, 6, 'green')
for i, (x0, y0, z0, dx, dy, h) in enumerate([(847, 339, 443, 48, 93, 44), (953, 359, 443, 62, 80, 59), (915, 574, 445, 93, 53, 50)]):
    slab('h1_school_wing_floor_' + str(i), [(x0, y0), (x0 + dx, y0 + 8), (x0 + dx - 9, y0 + dy), (x0 + 12, y0 + dy + 7)], z0 + 2, 4, 'chalk')
    for j, (x, y) in enumerate([(x0 + 8, y0 + 12), (x0 + dx - 13, y0 + dy - 6)]):
        beam('h1_school_wing_strut_%d_%d' % (i, j), (x, y, z0 + 3), (x + 4, y + 9, z0 + h), 3.1, 5, 'steel')
    slab('h1_school_wing_roof_' + str(i), [(x0 - 7, y0 - 10), (x0 + dx + 8, y0 + 12), (x0 + dx - 8, y0 + dy + 13), (x0, y0 + dy + 15)], z0 + h, 5, 'roof')
    slab('h1_school_civic_mezzanine_' + str(i), [(x0 + 5, y0 + 12), (x0 + dx - 3, y0 + 19), (x0 + dx - 14, y0 + dy - 12), (x0 + 15, y0 + dy - 5)], z0 + h * 0.54, 4, 'bone')
dwellings = [('garden_house', 610, 548, 447, 42, 52, 36), ('bay_house', 657, 566, 447, 48, 45, 54), ('school_caretaker', 991, 449, 443, 38, 57, 31), ('cliff_house', 1010, 529, 450, 43, 47, 68), ('market_loft', 625, 304, 446, 65, 36, 44), ('south_market', 858, 297, 446, 76, 32, 35), ('upper_studio', 625, 642, 454, 48, 44, 45), ('upper_residence', 687, 650, 448, 52, 42, 59), ('northern_courtyard', 824, 674, 447, 73, 42, 42), ('north_garden_loft', 921, 646, 451, 56, 44, 52)]
for i, (label, x, y, z, w, l, h) in enumerate(dwellings):
    slab(label + '_actual_floor', [(x, y), (x + w, y + 4), (x + w - 7, y + l), (x + 6, y + l + 5)], z, 5, 'bone')
    beam(label + '_back_wall_lower', (x + 6, y + l - 2, z), (x + 6, y + l - 2, z + h), 4, 6, 'chalk')
    beam(label + '_back_wall_upper', (x + w - 7, y + l - 2, z), (x + w - 7, y + l - 2, z + h), 4, 6, 'chalk')
    for j in (0, 1):
        fz = z + 15 + j * (h - 16) / 2
        if fz > z + h - 5:
            continue
        slab(label + '_inhabited_level_' + str(j), [(x + 2, y + 8), (x + w - 2, y + 10), (x + w - 8, y + l - 8), (x + 8, y + l - 6)], fz, 3, 'street' if j else 'chalk')
    t = 6 if i % 3 == 0 else -4 if i % 3 == 1 else 2
    slab(label + '_asymmetric_roof', [(x - 4, y - 7), (x + w + 8, y + 3), (x + w - 3, y + l + 12), (x + 10, y + l + 13)], z + h + t, 5, 'roof')
    beam(label + '_door_left', (x + w * 0.46, y + 2, z), (x + w * 0.46, y + 2, z + 11), 2.1, 2.3, 'steel')
    beam(label + '_door_right', (x + w * 0.65, y + 2, z), (x + w * 0.65, y + 2, z + 11), 2.1, 2.3, 'steel')
    beam(label + '_door_lintel', (x + w * 0.46, y + 2, z + 11), (x + w * 0.65, y + 2, z + 11), 2, 3, 'copper')
    route(label + '_balcony', [(x + 5, y + 8, z + h * 0.63), (x + w * 0.6, y + 5, z + h * 0.64), (x + w - 5, y + 10, z + h * 0.64)], 5, 2, 'bone')
    block(label + '_occupied_glazing', (x + w * 0.8, y + l - 4, z + 22), (w * 0.18, 2, h * 0.24), 'glass')
for i, (x, y) in enumerate([(703, 342), (828, 358), (710, 593), (822, 596)]):
    slab('h1_shop_covered_stall_' + str(i), [(x - 12, y), (x + 12, y), (x + 17, y + 18), (x - 15, y + 20)], 450 + i % 2 * 2, 2, 'copper')
    beam('h1_shop_canopy_' + str(i), (x - 14, y + 11, 466), (x + 16, y + 18, 470), 2, 4, 'roof')
    block('h1_shop_display_' + str(i), (x, y + 12, 454), (16, 3, 10), 'glass')
for i, (x, y) in enumerate([(750, 361), (803, 412), (743, 470), (804, 563), (762, 624), (824, 686)]):
    block('public_street_seating_' + str(i), (x, y, 443), (13, 4, 3), 'copper')
for i, (x, y) in enumerate([(720, 330), (825, 347), (731, 535), (817, 572), (742, 695)]):
    slab('public_planter_' + str(i), [(x - 8, y - 7), (x + 9, y - 7), (x + 9, y + 7), (x - 8, y + 8)], 444, 3, 'green')
    beam('habitable_tree_' + str(i), (x, y, 445), (x + 2, y, 461), 1.3, 1.5, 'slate')
slab('h1_station_public_platform', [(705, 681), (794, 674), (821, 732), (711, 760)], 441, 8, 'bone')
slab('h1_station_canopy', [(699, 683), (774, 676), (843, 735), (721, 775)], 473, 5, 'roof')
for i, (x, y) in enumerate([(716, 693), (790, 714)]):
    beam('h1_station_pillar_' + str(i), (x, y, 440), (x + 4, y + 7, 471), 4, 5, 'steel')
route('h1_school_platform_bridge', [(806, 580, 440), (838, 592, 449), (889, 620, 452), (925, 643, 452)], 15, 4, 'chalk')
slab('w0_hewn_upper_bank', [(-510, -440), (-320, -485), (-190, -612), (15, -670), (220, -535), (480, -330), (670, -170), (555, 145), (260, 190), (-130, -90), (-450, -180)], 50, 27, 'slate')
slab('w0_public_tidal_lower_quay', [(-337, -694), (-105, -738), (130, -647), (335, -486), (488, -370), (550, -235), (418, -248), (214, -432), (-36, -594), (-294, -612)], 28, 9, 'street')
for j in range(12):
    z = 49 - j * 2.5
    y = -605 - j * 9
    slab('w0_hewn_tidal_steps_' + str(j), [(-100 - j * 5, y), (80 + j * 5, y - 12), (160 + j * 3, y + 16), (-50 - j * 5, y + 20)], z, 2, 'bone')
slab('w0_ferry_station', [(388, -365), (498, -353), (614, -269), (632, -178), (569, -118), (455, -191)], 37, 9, 'chalk')
slab('w0_ferry_lower_gate', [(482, -409), (600, -363), (676, -275), (621, -235), (509, -291)], 21, 7, 'street')
for i, (x, y) in enumerate([(409, -335), (487, -341), (603, -258)]):
    beam('w0_ferry_sloping_pier_' + str(i), (x, y, 37), (x + 13, y + 7, 102), 5, 7, 'steel')
slab('w0_ferry_slotted_roof_w', [(393, -373), (492, -355), (533, -276), (460, -207)], 106, 5, 'roof')
slab('w0_ferry_slotted_roof_e', [(546, -305), (619, -260), (644, -172), (557, -137)], 115, 6, 'chalk')
route('w0_ferry_public_access', [(450, -290, 40), (352, -360, 46), (212, -489, 55), (116, -552, 61), (10, -575, 70)], 18, 5, 'bone')
route('w0_nave_shoreline', [(10, -575, 70), (-51, -604, 61), (-170, -612, 35), (-281, -646, 29)], 17, 5, 'street')
route('w0_h1_water_link', [(544, -208, 52), (611, -105, 79), (658, 23, 155), (700, 118, 277), (747, 223, 437)], 20, 6, 'chalk')
slab('w0_west_cliff_public_overlook', [(-760, -291), (-684, -324), (-571, -219), (-587, -123), (-695, -96), (-792, -190)], 137, 10, 'slate')
route('w0_cliff_public_walk', [(-712, -150, 142), (-607, -223, 119), (-456, -333, 87), (-321, -468, 58), (-230, -581, 34)], 19, 6, 'bone')
rail('w0_cliff_guard', [(-712, -140, 142), (-607, -210, 119), (-456, -319, 87), (-321, -452, 58), (-230, -565, 34)], 6)
spine = [(-420, 240, 340), (-305, 290, 465), (-160, 355, 615), (-37, 411, 750), (115, 472, 905), (219, 501, 1025), (306, 550, 1190)]
route('transverse_civic_ascending_urban_spine', spine, 42, 12, 'steel')
rail('transverse_spine_lit_guard', [(x - 21, y, z) for x, y, z in spine], 12, 'way')
for i, (x, y, z) in enumerate(spine[1:-1]):
    s = [(x - 83, y - 35), (x + 50, y - 46), (x + 70, y + 36), (x - 68, y + 65)]
    slab('rift_occupied_terrace_' + str(i), s, z, 9, 'chalk' if i % 2 == 0 else 'slate')
    if i % 2 == 0:
        slab('rift_sky_public_pavilion_' + str(i), [(x - 48, y + 9), (x + 20, y + 11), (x + 29, y + 58), (x - 31, y + 67)], z + 49 + i * 4, 5, 'roof')
        for j, (xx, yy) in enumerate([(x - 35, y + 17), (x + 18, y + 27)]):
            beam('rift_civic_pavilion_support_%d_%d' % (i, j), (xx, yy, z), (xx + 8, yy + 5, z + 49 + i * 4), 3.2, 4.5, 'steel')
    else:
        route('rift_hanging_public_walk_' + str(i), [(x - 53, y - 24, z + 4), (x - 17, y + 8, z + 17), (x + 40, y + 31, z + 17)], 13, 4, 'bone')
route('floating_east_tidal_strata', [(315, 225, 380), (466, 309, 515), (576, 386, 637), (657, 450, 728), (710, 534, 825)], 36, 9, 'roof')
slab('floating_east_public_archive', [(538, 361), (613, 376), (674, 445), (640, 508), (563, 487)], 653, 12, 'bone')
for i, (x, y) in enumerate([(548, 382), (633, 440)]):
    beam('floating_east_reading_strut_' + str(i), (x, y, 652), (x + 12, y + 9, 700), 4, 4, 'steel')
slab('floating_east_archive_open_roof', [(528, 376), (618, 370), (676, 464), (627, 509)], 713, 7, 'chalk')
assert S['FORMAL_ART_ACCEPTED'] == 0 and S['COMPLETED_TARGETS'] == 0 and (S['CONSTRUCTION'] == 'HOLD')
for n, m in cameras.items():
    bpy.context.view_layer.update()
    assert max((abs(bpy.data.objects[n].matrix_world[r][c] - m[r][c]) for r in range(4) for c in range(4))) < 1e-05
S['LCS1_SOURCE_E12_SHA256'] = 'ba3363c0908bbf0b4d61afb1d4497af8696364c60b97eac754f351249ccb3c19'
S['LCS1_OLD_E12_SCULPTURES_REMOVED'] = len(deleted)
S['LCS1_DESIGN_METHOD'] = 'FUNCTION_FIRST_CONNECTED_NAVE_H1_W0_NOT_BOXY_MASS_REPLACEMENT'
S['LCS1_ART_JURY'] = 'UNREVIEWED_UNADOPTED'
S['LCS1_WORLD_COORDS'] = 'ISOLATED_RESEARCH_METRES_NOT_AUTHENTICATED'
S['CONSTRUCTION'] = 'HOLD'
S['COMPLETED_TARGETS'] = 0
S['FORMAL_ART_ACCEPTED'] = 0
S.render.engine = 'CYCLES'
S.cycles.device = 'CPU'
S.cycles.samples = 12
S.cycles.use_denoising = True
S.render.threads_mode = 'FIXED'
S.render.threads = 2
S.render.resolution_x = 1100
S.render.resolution_y = 825
S.render.resolution_percentage = 100
S.render.image_settings.file_format = 'PNG'
S.render.film_transparent = False
result = out / 'LCS1_OCCUPIED_CIVIC_SECTION_WORKING.blend'
S.camera = bpy.data.objects['E11_URBAN_AERIAL']
bpy.ops.wm.save_as_mainfile(filepath=str(result), compress=True)
images = {}
for name in ['E11_NAVE_HUMAN', 'E11_H1_HUMAN', 'E11_URBAN_AERIAL']:
    S.camera = bpy.data.objects[name]
    f = out / 'renders' / (name + '.png')
    S.render.filepath = str(f)
    bpy.ops.render.render(write_still=True)
    assert f.stat().st_size > 5000, name
    images[name] = hashlib.sha256(f.read_bytes()).hexdigest()
    print('LCS1_TRUE_RENDER', name, f.stat().st_size, flush=True)
S.camera = bpy.data.objects['E11_URBAN_AERIAL']
bpy.ops.wm.save_as_mainfile(filepath=str(result), compress=True)
report = {'schema': 'halo9-lcs1-real-occupied-section-v1', 'engine': bpy.app.version_string, 'source_e12_sha256': S['LCS1_SOURCE_E12_SHA256'], 'edited_blend_sha256': hashlib.sha256(result.read_bytes()).hexdigest(), 'native_blend_bytes': result.stat().st_size, 'deleted_e12_rejected_meshes': len(deleted), 'new_authored_meshes': sum((1 for o in C.objects if o.type == 'MESH')), 'scenes': list(bpy.data.scenes.keys()), 'render_png_sha256': images, 'formal_art_adopted': 0, 'targets_completed': 0, 'minecraft_construction': 'HOLD', 'art_gate': 'PENDING_DIRECT_IMAGE_REVIEW', 'source_edited': False, 'main_edited': False}
(out / 'LCS1_AUTHOR_REPORT.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
print('LCS1_REAL_NATIVE_COMPLETE', json.dumps(report), flush=True)