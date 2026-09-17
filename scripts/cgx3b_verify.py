"""Capture exact UTF-8 subprocess evidence for this lane, offline."""
import os
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.stdout.reconfigure(encoding='utf-8')
env = dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONUTF8='1',
           PYTHONPATH=str(root / 'scripts/cgx3b_offline') + os.pathsep + str(root))
result = subprocess.run([sys.executable, *sys.argv[2:]], cwd=root, env=env,
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
(root / sys.argv[1]).write_bytes(result.stdout)
print(result.stdout.decode('utf-8', errors='replace'))
raise SystemExit(result.returncode)
