"""Run the vendored M119-M121 tests with UTF-8 and without cache writes."""
from pathlib import Path
import argparse
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / 'research/m121/upstream'
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-tests', action='store_true', help='Also run original governance tests using repository-local temporary fixtures')
    args = parser.parse_args()
    subprocess.run([sys.executable, '-B', '-X', 'utf8', str(ROOT / 'tools/m121_verify_bundle.py'), str(BUNDLE)], check=True)
    subprocess.run([sys.executable, '-B', '-X', 'utf8', '-m', 'unittest', 'discover', '-s', 'tests', '-v'], cwd=BUNDLE, check=True)
    if args.repo_tests:
        temp = ROOT / 'artifacts/test-temp'
        temp.mkdir(parents=True, exist_ok=True)
        env = dict(os.environ, TEMP=str(temp), TMP=str(temp), TMPDIR=str(temp))
        subprocess.run([sys.executable, '-B', '-X', 'utf8', str(ROOT / 'ci/check_policy.py')], cwd=ROOT, env=env, check=True)
        subprocess.run([sys.executable, '-B', '-X', 'utf8', '-m', 'unittest', 'discover', '-s', 'tests', '-v'], cwd=ROOT, env=env, check=True)
