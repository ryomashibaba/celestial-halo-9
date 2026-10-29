#!/usr/bin/env python3
"""VTK screenshots from each saved GLB, never made-up 2D geometry."""
from pathlib import Path
import sys,io
import trimesh
from PIL import Image, ImageDraw
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P))
from d28_visual_workbench import render,VIEWS
from d29_render import inside_render

def main():
    for key in ['BASE','ROOM','SKYLIGHT']:
        s=trimesh.load(str(P/f'D30_{key}.glb'),force='scene',process=False)
        for view in VIEWS:
            (P/f'D30_{key}_{view}.png').write_bytes(render(s,view).png)
        eyes={
            'entry_human':([10,-275,145],[70,-20,175],(0,0,1)),
            'room_human':([105,70,162],[185,155,185],(0,0,1)),
            'skylight_human':([105,70,150],[195,150,495],(0,1,0))}
        for label,(eye,look,up) in eyes.items():
            (P/f'D30_{key}_{label}.png').write_bytes(inside_render(s,eye,look,up,70))
    cols=['BASE','ROOM','SKYLIGHT'];views=['front','oblique','aerial','rear','entry_human','room_human','skylight_human']
    w,h=510,310;margin=16;gap=10;label_h=29;header=46
    output=Image.new('RGB',(margin*2+len(cols)*w+2*gap,margin*2+header+len(views)*(h+label_h+gap)),(238,241,245))
    draw=ImageDraw.Draw(output)
    for ci,c in enumerate(cols):
        x=margin+ci*(w+gap);draw.text((x,margin+8),c,fill=(10,30,42))
        for vi,v in enumerate(views):
            y=margin+header+vi*(h+label_h+gap)
            pic=Image.open(P/f'D30_{c}_{v}.png').convert('RGB');pic.thumbnail((w,h));output.paste(pic,(x,y))
            draw.text((x+7,y+h+5),v,fill=(40,50,70))
    output.save(P/'D30_7VIEW_STAGE_COMPARE.jpg',quality=88)
    print('Rendered',3*len(VIEWS)+3*3,'saved GLB photographs and stage contact sheet')
if __name__=='__main__':main()
