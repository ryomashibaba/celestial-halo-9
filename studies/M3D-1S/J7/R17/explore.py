import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import atelier as a
args=sys.argv[sys.argv.index('--')+1:];which=args[0]
a.setup()
if which=='A':a.build_A()
else:a.build_B()
a.cameras();folder=a.ROOT/('exploration_'+which)
a.export(folder,'R17_'+which)
a.render(folder,args[1:] or ['01_FRONT','02_OBLIQUE','03_SIDE','04_REAR','05_AERIAL','06_UNDERSIDE','07_GROUND_UP'])
