#!/usr/bin/env python3
"""M120 actual-old-city tile evidence + proposed B city geometry comparison images.
Non-construction. Route is centerline-only with unbuilt lifts; do not mistake visuals for gameplay.
"""
from __future__ import annotations
import json, math, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from m119_city_model import ROOT,produce,SITES,ATLAS,PROGRAM,MATERIALS
from m120_city_model import produce_m120,M120_MATERIALS
MATERIALS.update(M120_MATERIALS)
BG='#0b131b'; INK='#eef0e8'; MUTED='#9babb5'; AQUA='#78cbd1'; GOLD='#e1b47b'; RED='#f69a78'
plt.rcParams.update({'font.family':'DejaVu Sans','savefig.facecolor':BG,'figure.facecolor':BG,'axes.facecolor':BG,'text.color':INK})

def t(pt):return (pt[0]-3703.5,pt[1]+2184.5,pt[2]+1840)

def old_tiles(ax,site=None):
    tiles=[];clr=[]
    for s in ATLAS['sites']:
        if site and s['site']!=site:continue
        for q in s['tiles']:
            x,z,yy=q['x'],q['z'],q['max_y']
            tiles.append([t((x,z,yy)),t((x+8,z,yy)),t((x+8,z+8,yy)),t((x,z+8,yy))])
            clr.append((.20,.27,.31,.60))
    ax.add_collection3d(Poly3DCollection(tiles,facecolors=clr,edgecolors='none',zsort='min'))

def draw(ax,meshes,sites=None):
    groups={}
    for obj in meshes:
        if sites and obj['site'] not in sites:continue
        color=obj['material']
        pts=[t(v) for v in obj['v']]
        for f in obj['f']:
            if len(f)<3:continue
            groups.setdefault(color,[]).append([pts[j] for j in f])
    ordered=['structure','obsidian','shadow','court','garden','forest','sandstone','copper','glass','opal','lagoon','pearl','ivory','cyan','gold']
    for color in ordered:
        if color not in groups:continue
        alpha= .88 if color in ('structure','obsidian','shadow') else (.77 if color in ('glass','opal','forest','garden') else .95)
        ax.add_collection3d(Poly3DCollection(groups[color],facecolor=MATERIALS.get(color,INK),
             alpha=alpha,edgecolors='#2e4651',linewidth=.08,zsort='average'))

def config(ax,angle=(-67,26),center=(0,0,115),span=(820,520,520),zoom=2.65):
    (az,el)=angle;(x,z,y)=center;(sx,sz,sy)=span
    ax.set_xlim(x-sx,x+sx);ax.set_ylim(z-sz,z+sz);ax.set_zlim(y-sy/2,y+sy/2)
    ax.set_box_aspect((1.6,1.14,.60),zoom=zoom)
    ax.view_init(elev=el,azim=az);ax.set_axis_off();ax.grid(False)
    try: ax.dist=5
    except Exception:pass

def titlebar(fig,title,subtitle):
    fig.text(.027,.966,'CELESTIAL HALO-9 / M120 / ARCHITECTURAL REGENERATION LAB',fontsize=12,color=GOLD,weight='bold')
    fig.text(.027,.933,title,fontsize=23,weight='bold',color=INK)
    fig.text(.028,.905,subtitle,fontsize=10.2,color=MUTED)
    fig.text(.028,.025,'OBSERVED grey tiles: M117 saved blocks / WHITE-COPPER-TEAL: unapproved research mesh / NO world writes / NO protected clearance',fontsize=8.7,color=MUTED)

def skyline_comp():
    prev=produce('B_FRACTURED_SKY_TERRACES');new=produce_m120()
    fig=plt.figure(figsize=(19,12),facecolor=BG)
    titlebar(fig,'THE CITY MUST FEEL MONUMENTAL — 3D BEFORE / AFTER','Matching camera and measured old-building reference. M119 vs added M120 sculptural ribs, pavilion canopies and skycourt decks.')
    specs=[('M119 / RESEARCH BASELINE',prev,(-68,25)),('M120 / ARCHITECTURAL SPINES',new,(-68,25)),
            ('M119 / OPPOSITE HORIZON',prev,(116,18)),('M120 / OPPOSITE HORIZON',new,(116,18))]
    for i,(label,m,view) in enumerate(specs):
        x=.03+(i%2)*.495;y=.49-(i//2)*.41
        ax=fig.add_axes([x,y,.465,.38],projection='3d',facecolor=BG)
        config(ax,view,zoom=2.55);old_tiles(ax);draw(ax,m['meshes'])
        fig.text(x+.01,y+.373,label,color=AQUA if i%2 else GOLD,fontsize=12,weight='bold')
        fig.text(x+.01,y+.02,f'{len(m["meshes"]):,} unapproved 3D meshes',color=MUTED,fontsize=9)
    dest=ROOT/'images/M120_01_BEFORE_AFTER_MONUMENTAL_SKYLINE.png'
    fig.savefig(dest,dpi=145,pad_inches=.08);plt.close(fig);return dest

def hero_comp():
    m=produce_m120();fig=plt.figure(figsize=(18.5,12),facecolor=BG)
    titlebar(fig,'HERO4 / FOUR DIFFERENT MEGA-ARCHITECTURES','Sculptural cathedral sail, aurora arch, gateway, ridge sanctuary / actual saved building tiles stay behind the proposal.')
    for i,sid in enumerate(('SB05','SB08','SB09','SB12')):
        x=.03+(i%2)*.495;y=.49-(i//2)*.41
        ax=fig.add_axes([x,y,.465,.37],projection='3d',facecolor=BG)
        s=SITES[sid];wx=s['tile_box'][2]-s['tile_box'][0];wz=s['tile_box'][3]-s['tile_box'][1]
        xx,zz=s['center'];ycenter=s['observed_y_max']+114+1840
        config(ax,(-58,23),center=(xx-3703.5,zz+2184.5,ycenter),span=(max(155,wx*.8),max(128,wz*1.2),370),zoom=2.35)
        old_tiles(ax,sid);draw(ax,m['meshes'],{sid})
        fig.text(x+.015,y+.367,sid+' / '+PROGRAM[sid][0],color=GOLD if i%2==0 else AQUA,fontsize=12,weight='bold')
        fig.text(x+.015,y+.025,'Observed Y '+str(s['observed_y_min'])+'..'+str(s['observed_y_max']),color=MUTED,fontsize=9)
    dest=ROOT/'images/M120_02_HERO4_ARCHITECTURAL_STUDIES.png';fig.savefig(dest,dpi=150,pad_inches=.08);plt.close(fig);return dest

def route_board():
    new=produce_m120();route=new['public_route_concept'];stations=route['stations'];segs=route['segments']
    fig=plt.figure(figsize=(18,10.5),facecolor=BG)
    titlebar(fig,'PUBLIC EXPERIENCE / ONE CENTERLINE, MANY UNRESOLVED CONNECTIONS',
      'Geometric segment continuity PASS. Building doors, functional elevators, protected voids & actual walkability NOT VERIFIED.')
    gs=fig.add_gridspec(1,2,left=.055,right=.965,top=.85,bottom=.14,wspace=.19,width_ratios=[1.2,1])
    ax=fig.add_subplot(gs[0]);ax.set_facecolor('#17242c')
    for s in ATLAS['sites']:
        for q in s['tiles']:
            ax.add_patch(plt.Rectangle((q['x'],q['z']),8,8,color='#455865',alpha=.55,lw=0))
    xs=[q['xyz'][0] for q in stations];zs=[q['xyz'][1] for q in stations]
    ax.plot(xs,zs,'-',color=AQUA,lw=4,zorder=8)
    for i,q in enumerate(stations):
        ax.scatter(q['xyz'][0],q['xyz'][1],s=63,color=GOLD if i in (0,3,8,9) else AQUA,zorder=10)
        ax.text(q['xyz'][0]+12,q['xyz'][1]+(-22 if i%2 else 16),q['name'].replace('_',' '),fontsize=7.5,color=INK,zorder=11)
    ax.set_xlim(3430,4180);ax.set_ylim(-2440,-1785);ax.set_aspect('equal');ax.tick_params(colors=MUTED)
    ax.set_title('01 / ACTUAL CONSTRUCTED MATERIAL FOOTPRINT + PROPOSED ROUTE',loc='left',fontsize=12,color=INK,pad=14)
    ax.grid(color=INK,alpha=.07)
    ax2=fig.add_subplot(gs[1]);ax2.set_facecolor('#16252c')
    dd=[0];yy=[stations[0]['xyz'][2]]
    for sg in segs:dd.append(dd[-1]+sg['length_m']);yy.append(sg['end'][2])
    ax2.plot(dd,yy,color=AQUA,lw=3.4)
    ax2.scatter(dd,yy,s=40,color=GOLD,zorder=5)
    for i,sg in enumerate(segs):
        mx=(dd[i]+dd[i+1])/2;my=(yy[i]+yy[i+1])/2
        risk=sg['observed_material_tile_AABB_risks']
        if risk:
            ax2.text(mx,my+15,f'S{i:02d} {risk} OLD-TILE RISKS',ha='center',fontsize=8,color=RED,rotation=0)
    ax2.set_ylim(-1830,-1625);ax2.set_ylabel('Proposed Minecraft absolute Y / NOT certified',color=MUTED)
    ax2.set_xlabel('Concept centerline distance / m',color=MUTED)
    ax2.tick_params(colors=MUTED);ax2.grid(alpha=.11,color=INK)
    ax2.set_title('02 / PROPOSED HEIGHT TRANSITIONS + MATERIAL-TILE BROADPHASE',loc='left',fontsize=11.5,pad=15)
    fig.text(.055,.088,'IMPORTANT: Segment S00 has 13 conservative old-material tile hits and lift S01 has 8. Zero-hit elevated paths are NOT protected-void clearance.',fontsize=11,color=RED)
    fig.text(.055,.061,'SB13 true protected entrance XYZ UNKNOWN • all skybridges/lifts UNBUILT • ring docking merely sampled • route is NOT traversable',fontsize=10,color=GOLD)
    dest=ROOT/'images/M120_03_ROUTE_GEOMETRY_AND_RISKS.png';fig.savefig(dest,dpi=150,pad_inches=.1);plt.close(fig);return dest

def civic_approach():
    m=produce_m120();fig=plt.figure(figsize=(16,9),facecolor=BG)
    titlebar(fig,'A CENTER WITH SCALE / CIVIC MULTI-LEVEL SPATIAL STUDY','Close aerial and mid-level architectural volumes. Huge public void is still an uncut REPLACEMENT proposal.')
    specs=[('LOW SKYCOURT / CANTILEVERS',(-62,23)),('OPPOSITE ATRIUM / MONUMENTAL DIAGONALS',(120,16))]
    for i,(label,cam) in enumerate(specs):
        x=.03+i*.49
        ax=fig.add_axes([x,.20,.46,.64],projection='3d',facecolor=BG)
        config(ax,cam,center=(0,0,190),span=(335,255,310),zoom=2.4)
        old_tiles(ax)
        draw(ax,m['meshes'],{'CIVIC_CORE','SB06','SB07','SB10','SB11','PUBLIC_ROUTE'})
        fig.text(x+.01,.826,label,color=GOLD if i==0 else AQUA,fontsize=12,weight='bold')
    dest=ROOT/'images/M120_04_CIVIC_CORE_HUMAN_SCALE_STUDY.png';fig.savefig(dest,dpi=155,pad_inches=.08);plt.close(fig);return dest

if __name__=='__main__':
    for fn in (skyline_comp,hero_comp,route_board,civic_approach):
        p=fn();print(p.name,p.stat().st_size)
