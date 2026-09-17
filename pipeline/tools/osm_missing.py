import sys, os, json
sys.path.insert(0,'/home/sandbox/europe/work')
from fetch_trends_eu import write_city, read_T
from cities_eu import SHIP
for cid in SHIP:
    p=f'/home/sandbox/europe/repo/{cid}/data/trends.js'
    if os.path.exists(p) and read_T(cid): continue
    write_city(cid)
print('OSM MISSING DONE')
