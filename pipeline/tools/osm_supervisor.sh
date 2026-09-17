cd /home/sandbox/europe
for i in 1 2 3 4 5 6 7 8; do
  while pgrep -f 'osm_missing.py' >/dev/null; do sleep 60; done
  left=$(python3 - <<'PY'
import sys,os
sys.path.insert(0,'/home/sandbox/europe/work')
from fetch_trends_eu import read_T
from cities_eu import SHIP
n=0
for cid in SHIP:
    p=f'/home/sandbox/europe/repo/{cid}/data/trends.js'
    if not (os.path.exists(p) and read_T(cid)): n+=1
print(n)
PY
)
  echo "round $i: $left cities missing" >> /tmp/osm_sup.log
  [ "$left" = "0" ] && break
  sleep 300
  nohup python3 work/osm_missing.py >> /tmp/osm_missing.log 2>&1 &
done
echo SUPERVISOR-EXIT >> /tmp/osm_sup.log
