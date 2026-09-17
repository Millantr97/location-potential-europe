"""Named highway polylines via Overpass 'out geom' for one city. Usage: <cid>"""
import json, sys, os, urllib.request
sys.path.insert(0,'/home/sandbox/europe/work')
from cities_eu import CITIES_EU
cid=sys.argv[1]; C=CITIES_EU[cid]
b=C['bbox']
q=f"""[out:json][timeout:110];
way["highway"]["name"]({b[0]},{b[1]},{b[2]},{b[3]});
out geom;"""
req=urllib.request.Request('https://overpass-api.de/api/interpreter',data=q.encode())
d=json.load(urllib.request.urlopen(req,timeout=115))
SKIP={'footway','path','cycleway','steps','track','service','construction','proposed','corridor','elevator','rest_area','services'}
out=[]
for el in d['elements']:
    t=el.get('tags',{})
    if t.get('highway') in SKIP: continue
    pts=[(round(g['lat'],6),round(g['lon'],6)) for g in el.get('geometry',[])]
    if len(pts)<2: continue
    out.append({'name':t['name'],'hw':t.get('highway',''),'pts':pts})
dd=f'/home/sandbox/europe/repo/pipeline/eu/{cid}'
os.makedirs(dd,exist_ok=True)
json.dump(out,open(f'{dd}/streets.json','w'))
print(cid,'named streets:',len(out))
