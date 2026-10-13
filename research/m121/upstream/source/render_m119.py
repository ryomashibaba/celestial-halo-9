#!/usr/bin/env python3
"""Offline review-quality comparison of actual 8x8 saved-block evidence versus
nonconstruction proposal meshes. Does not read or write any Minecraft world.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from m119_city_model import ATLAS,SITES,ROOT,produce,MATERIALS,HERO,CIVIC
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection,Line3DCollection
from matplotlib.patches import Patch
BG='#0d151b';INK='#e2e9eb';DIM='#96a5ab';GOLD='#d5ab79';CYN='#70c9d2';BLUE='#394c55'
plt.rcParams.update({'font.family':'DejaVu Sans','figure.facecolor':BG,'axes.facecolor':BG,'savefig.facecolor':BG})

def t(p):return (p[0]-3703.5,p[1]+2184.5,p[2]+1840)

def axes(ax,elev,azim,full=True):
 ax.set_facecolor(BG)
 ax.set_axis_off();ax.grid(False)
 if full:
  ax.set_xlim(-840,840);ax.set_ylim(-570,570);ax.set_zlim(-38,430);ax.set_box_aspect((15,9.2,5.3),zoom=1.75)
 ax.view_init(elev=elev,azim=azim)
 ax.dist=3.7

# draw actual 8x8 occupied bins only with minimum solidity; low contrast graphite
# coordinates are OBSERVED, model volume is proposed

def show_old(ax,short=False,limits=None):
 polys=[];intens=[]
 for s in ATLAS['sites']:
  for tile in s['tiles']:
   x=tile['x'];z=tile['z'];y=tile['max_y'];c=tile['count']
   if short and c<340:continue
   if limits and not(limits[0]<=x<=limits[1] and limits[2]<=z<=limits[3]):continue
   verts=[t((x,z,y)),t((x+8,z,y)),t((x+8,z+8,y)),t((x,z+8,y))]
   polys.append(verts);intens.append(min(1,c/900))
 colors=[(0.18+.14*c,0.24+.12*c,0.29+.11*c,.88) for c in intens]
 if polys:ax.add_collection3d(Poly3DCollection(polys,facecolors=colors,edgecolors='none',zsort='min'))

def show_concept(ax,data,rangebox=None):
 bycolor={}
 for m in data['meshes']:
  site=m['site'];mat=m['material']
  if rangebox and site not in rangebox and site!='MACRO':continue
  v=m['v'];p=[t(v0) for v0 in v]
  for f in m['f']:
   if len(f)<3:continue
   bycolor.setdefault(mat,[]).append([p[i] for i in f])
 # the auto painter depth sorter operates per Poly3DCollection — draw dark first
 for k in ('structure','sandstone','court','garden','glass','pearl','cyan','gold'):
  if not bycolor.get(k):continue
  clr=MATERIALS[k]
  alpha={'structure':.86,'pearl':.94,'glass':.66,'cyan':.91,'gold':.85,'sandstone':.9,'garden':.78,'court':.6}[k]
  coll=Poly3DCollection(bycolor[k],facecolor=clr,edgecolors=(.13,.21,.22,.17),linewidths=.15,alpha=alpha,zsort='average')
  ax.add_collection3d(coll)

def decorate(fig,heading,subtitle):
 fig.text(.035,.952,'CELESTIAL HALO-9   /   M119   /   CITY ARCHITECTURE LAB',color=GOLD,fontsize=15,weight='medium')
 fig.text(.035,.918,heading,color=INK,fontsize=22,weight='bold')
 fig.text(.035,.89,subtitle,color=DIM,fontsize=11)
 fig.text(.04,.034,'SOURCE: M117 review-copy saved block atlas  |  NEW SHELLS = PROPOSAL ONLY  |  NO COLLISION CERTIFICATION  |  NO WORLD WRITES',color=DIM,fontsize=9)

def comparative_views():
 A=produce('A_CROWNED_MERIDIAN');B=produce('B_FRACTURED_SKY_TERRACES')
 fig=plt.figure(figsize=(20,15),facecolor=BG)
 decorate(fig,'CITYWIDE VOLUMETRIC DESIGN / TWO COMPOSITIONS',
 'M101 concept is NOT constructed  /  Grey: observed 8x8 highest blocks  /  Light: candidate architectural envelopes')
 specs=[('01  CROWNED MERIDIAN  /  AXONOMETRIC',A,28,-70),
  ('02  FRACTURED SKY TERRACES  /  AXONOMETRIC',B,28,-70),
  ('03  CROWNED MERIDIAN  /  OPPOSITE SKYLINE',A,19,122),
  ('04  FRACTURED SKY TERRACES  /  OPPOSITE SKYLINE',B,19,122)]
 for i,(title,model,elev,azim) in enumerate(specs):
  ax=fig.add_axes([.02+(i%2)*.493,.468-(i//2)*.394,.483,.38],projection='3d',facecolor=BG)
  axes(ax,elev,azim);show_old(ax,short=True);show_concept(ax,model)
  fig.text(.056+(i%2)*.493,.855-(i//2)*.395,title,color=GOLD if i%2==0 else CYN,fontsize=11,weight='bold')
 p=ROOT/'images/M119_01_MATCHED_4_CAMERA_MACRO_SCULPTURES.png';fig.savefig(p,dpi=140,facecolor=BG,bbox_inches='tight',pad_inches=.1);plt.close(fig)
 print(p,p.stat().st_size)

def hero_details():
 B=produce('B_FRACTURED_SKY_TERRACES')
 fig=plt.figure(figsize=(20,14),facecolor=BG)
 decorate(fig,'HERO4 / INDIVIDUAL MONUMENTAL BUILDINGS','Same Minecraft X/Z absolute Y proposals  /  Interiors defined as void volumes, NOT proven navigable')
 for i,(sid,name) in enumerate([('SB05','FOLDED SKY-SAIL CITADEL'),('SB08','TWIN AURORA VAULTS'),('SB09','GREAT CEREMONIAL GATE'),('SB12','MOUNTAIN HALO SANCTUARY')]):
  ax=fig.add_axes([.025+(i%2)*.495,.48-(i//2)*.39,.47,.37],projection='3d',facecolor=BG)
  axes(ax,32,-63,False)
  s=SITES[sid];x,z=s['center'];x,z=x-3703.5,z+2184.5
  ax.set_xlim(x-165,x+165);ax.set_ylim(z-125,z+125)
  y0=s['observed_y_min']+1840
  ax.set_zlim(y0-15,y0+330);ax.set_box_aspect((8,6.5,7.3),zoom=1.95);ax.dist=3.85
  show_old(ax,short=False,limits=(s['tile_box'][0]-12,s['tile_box'][2]+12,s['tile_box'][1]-12,s['tile_box'][3]+12))
  # render only this site's proposed masses to reveal scale and open central atrium
  proposal=dict(B);proposal['meshes']=[m for m in B['meshes'] if m['site']==sid]
  show_concept(ax,proposal)
  fig.text(.059+(i%2)*.495,.855-(i//2)*.385,f'{sid}  /  {name}',color=GOLD if sid in ('SB05','SB09') else CYN,fontsize=12,weight='bold')
  fig.text(.059+(i%2)*.495,.834-(i//2)*.385,f'actual saved material Y: {s["observed_y_min"]} to {s["observed_y_max"]}',color=DIM,fontsize=9)
 p=ROOT/'images/M119_02_FOUR_HERO_MONUMENTAL_SECTIONS.png';fig.savefig(p,dpi=140,facecolor=BG,bbox_inches='tight',pad_inches=.1);plt.close(fig)
 print(p,p.stat().st_size)

def programs():
 B=produce('B_FRACTURED_SKY_TERRACES')
 fig=plt.figure(figsize=(17,12),facecolor=BG)
 decorate(fig,'SIXTEEN FACILITIES / INTERIORS AND UNBUILT TRANSFERS',
 'Actual old city measurements + nonconstruction internal spatial ambitions / Routes below are UNCONNECTED intentions')
 gs=fig.add_gridspec(2,2,left=.05,right=.96,bottom=.13,top=.855,hspace=.18,wspace=.15)
 ax=fig.add_subplot(gs[:,0]);ax.set_facecolor('#121e24');ax.set_aspect('equal');ax.set_xlim(3180,4250);ax.set_ylim(-2460,-1870)
 for s in ATLAS['sites']:
  id=s['site'];cc='#ddb57d' if id in HERO else ('#7bd0d5' if id in CIVIC else '#c8d6d4')
  for tile in s['tiles']:
   ax.add_patch(plt.Rectangle((tile['x'],tile['z']),8,8,facecolor='#50616b',alpha=min(.65,.20+.38*tile['count']/1000),linewidth=0))
  x,z=SITES[id]['center'];ax.scatter([x],[z],s=115 if id in HERO else 56,color=cc,edgecolor=BG,linewidth=.7,zorder=3)
  ax.text(x,z+20,id,color=INK,fontsize=8,ha='center',fontweight='bold')
 cx,cz=3703.5,-2184.5
 for r,linetype in [(320,'-'),(406,'--')]:
  t=np.linspace(0,2*np.pi,100);ax.plot(cx+r*1.76*np.cos(t),cz+r*np.sin(t),color=CYN,linewidth=2,linestyle=linetype,alpha=.35)
 for a,b in [('SB13','SB09'),('SB09','SB10'),('SB10','SB06'),('SB06','SB07'),('SB07','SB08'),('SB07','SB11'),('SB11','SB12'),('SB05','SB06')]:
  x1,z1=SITES[a]['center'];x2,z2=SITES[b]['center'];ax.plot([x1,x2],[z1,z2],color=GOLD,linestyle=':',lw=1.8,alpha=.74)
 ax.set_title('01  PUBLIC REALM / URBAN WAYFINDING INTENT',loc='left',color=INK,pad=12,fontsize=12)
 ax.grid(alpha=.07,color=INK);ax.tick_params(colors=DIM,labelsize=8)
 for i,(category,ids) in enumerate([('HERO4  /  MONUMENTAL', ['SB05','SB08','SB09','SB12']),('CIVIC4  /  PUBLIC VOID', ['SB06','SB07','SB10','SB11'])]):
  a=fig.add_subplot(gs[i,1]);a.set_facecolor('#121e24');a.axis('off')
  a.text(.02,.96,category,transform=a.transAxes,color=GOLD if i==0 else CYN,fontsize=14,fontweight='bold')
  for j,sid in enumerate(ids):
   name,interior,kind=__import__('m119_city_model').PROGRAM[sid]
   a.text(.025,.78-j*.185,f'{sid}  {name}',transform=a.transAxes,color=INK,fontsize=10.7,fontweight='bold')
   a.text(.05,.70-j*.185,interior,transform=a.transAxes,color=DIM,fontsize=9.3)
 fig.text(.555,.11,'FRAME8 = differentiated workshops, gardens, observatories and market halls',color=INK,fontsize=11)
 fig.text(.555,.083,'8 tentative district links and 16 site internal entries / NOT built, traversable, or verified',color=GOLD,fontsize=9)
 p=ROOT/'images/M119_03_16_SITE_INTERIOR_AND_PUBLIC_ROUTE_BOARD.png';fig.savefig(p,dpi=155,facecolor=BG,bbox_inches='tight',pad_inches=.14);plt.close(fig);print(p,p.stat().st_size)

if __name__=='__main__':
 comparative_views();hero_details();programs()
