#!/usr/bin/env python3
"""M119 proposed HERO4 vertical PROGRAM sections, diagrammatic, NOT walkable or protected-clearance checked."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from m119_city_model import ROOT,produce,SITES,PROGRAM
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
BG='#0d151b';WHITE='#f0eee5';DARK='#1f333b';CYAN='#72bec9';GOLD='#daa866';MUTED='#99a8aa';LIGHT='#b6c8ca'
B=produce('B_FRACTURED_SKY_TERRACES');voids={v['site']:v for v in B['proposed_courts_and_voids'] if v['site'] in ['SB05','SB08','SB09','SB12']}
fig=plt.figure(figsize=(20,13),facecolor=BG)
fig.text(.035,.947,'C E L E S T I A L   H A L O - 9    /    M119    /   SPACE PLANNING',color=GOLD,fontsize=15)
fig.text(.035,.907,'HERO4 / MONUMENTAL INTERIOR SECTIONS',color=WHITE,fontsize=23,fontweight='bold')
fig.text(.035,.877,'Measured actual saved material bounds  +  proposed giant atriums  /  NOT collision-cleared, traversable or approved',color=MUTED,fontsize=11)
for index,sid in enumerate(['SB05','SB08','SB09','SB12']):
 xcol=index%2;row=index//2
 ax=fig.add_axes([.052+xcol*.49,.515-row*.382,.438,.315]);ax.set_facecolor('#14222a')
 s=SITES[sid];v=voids[sid];bas=s['observed_y_min'];top=s['observed_y_max']
 height=v['y1']-v['y0']
 # graph horizontal distance not to actual scale, section is a spatial planning diagram
 ax.add_patch(patches.Rectangle((-100,bas),200,top-bas,facecolor='#455863',alpha=.27,hatch='////',edgecolor='#657887',linewidth=.5))
 ax.add_patch(patches.Rectangle((-61,v['y0']),122,height,facecolor='#102a33',edgecolor=CYAN,linestyle='--',linewidth=2.0,alpha=.95))
 for floor in range(4):
  y=bas+18+floor*24
  if y>=v['y1']-8:break
  ax.add_patch(patches.Rectangle((-100,y),34,3,facecolor=GOLD,edgecolor='none'))
  ax.add_patch(patches.Rectangle((66,y),34,3,facecolor=GOLD,edgecolor='none'))
  ax.plot([-65,65],[y,y],color=GOLD,ls=':',alpha=.35,lw=1.5)
 ax.plot([-100,100],[top,top],color=WHITE,lw=2)
 ax.annotate('observed upper blocks',(-98,top),(-98,top+27),color=MUTED,fontsize=9,arrowprops={'arrowstyle':'-|>','color':MUTED})
 ax.text(0,(v['y0']+v['y1'])/2,'UNVERIFIED\nOPEN VOID',color=CYAN,ha='center',va='center',fontsize=14,fontweight='bold')
 ax.text(0,v['y1']+8,f'{height:.0f} block planned atrium height',color=GOLD,ha='center',fontsize=10)
 ax.set_xlim(-112,112);ax.set_ylim(bas-14,max(v['y1']+37,top+55));ax.tick_params(labelsize=9,colors=MUTED)
 ax.set_xticks([]);ax.set_ylabel('Actual Minecraft Y',color=MUTED,fontsize=9)
 ax.grid(axis='y',color=WHITE,alpha=.06)
 for sp in ax.spines.values():sp.set_visible(False)
 name,interior,kind=PROGRAM[sid]
 fig.text(.064+xcol*.49,.844-row*.383,f'{sid}  {name}',color=WHITE,fontsize=11.5,fontweight='bold')
 fig.text(.065+xcol*.49,.493-row*.383,interior+' | original frozen geometry untouched',color=MUTED,fontsize=10)
fig.text(.045,.045,'RESEARCH REPLACEMENT DESIGN: visible overlaps with the existing city are NOT cleared.  No Minecraft construction.  No functional elevators or safety-certified routes.',color=GOLD,fontsize=10)
p=ROOT/'images/M119_04_FOUR_HERO_INTERIOR_CUTAWAY_SECTIONS.png'
fig.savefig(p,facecolor=BG,dpi=150,bbox_inches='tight',pad_inches=.12);plt.close(fig);print(p,p.stat().st_size)
