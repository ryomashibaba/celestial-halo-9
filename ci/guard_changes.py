#!/usr/bin/env python3
"""Reject changes to protected governance/CI/frozen/reference paths."""
import subprocess,sys
PREFIXES=('governance/','.github/','deployment/','source/baselines/','source/frozen/','manifests/')
EXACT={'.gitattributes','.gitignore'}
def check_paths(paths):
    return [p for p in paths if p.startswith(PREFIXES) or p in EXACT or '..' in p.split('/') or p.startswith('/')]
if __name__=='__main__':
    if len(sys.argv)!=3:raise SystemExit('Usage: guard_changes.py BASE HEAD')
    raw=subprocess.check_output(['git','diff','--name-only','--no-renames',sys.argv[1]+'...'+sys.argv[2]],text=True)
    bad=check_paths(raw.splitlines())
    if bad:raise SystemExit('LOCKED PATH CHANGES: '+str(bad))
    print('LOCKED PATH GUARD PASS')
