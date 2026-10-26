"""Render both saved variants under matched, recorded conditions."""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry as g
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
preview='preview' in args
folder='process/revision2' if preview else 'renders'
(g.R/folder).mkdir(exist_ok=True)
for v in ['A','B']:
    g.render(v,'clay',preview,names=['01_CITY','02_CENTRAL','03_PUBLIC','04_HUMAN','05_REAR','06_UNDERSIDE','07_SKY_STREET'],folder=folder)
    g.render(v,'art',preview,names=['02_CENTRAL','03_PUBLIC','04_HUMAN','07_SKY_STREET'],folder=folder)
