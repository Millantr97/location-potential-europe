"""Emit repo/<city>/data/{segments,units,competitors}.js from segments_full2.json. EU version."""
import json, math, datetime, os, sys
sys.path.insert(0,'/home/sandbox/europe/work')
from cities_eu import CITIES_EU
from transit_eu import TRANSIT
cid=sys.argv[1]; C=CITIES_EU[cid]
ROOT='/home/sandbox/europe/repo'
P=f'{ROOT}/pipeline/eu/{cid}'
segs=json.load(open(f'{P}/segments_full2.json'))
UNITCATS=["cafe","restaurant","fast_food","pub_bar","grocery","shops","fitness","cowork","services","agents","pharmacy","vets"]
def hav(a,b,c,d):
    R=6371000; p1,p2=math.radians(a),math.radians(c)
    dp=math.radians(c-a); dl=math.radians(d-b)
    x=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(x))
UNITS=[]; seen=set(); COMPS={}
for si,s in enumerate(segs):
    per={}
    for u in s.get('_units',[]):
        key=(round(u['lat'],4),round(u['lng'],4),u['cat'])
        if key in seen: continue
        seen.add(key)
        dist=round(hav(s['lat'],s['lng'],u['lat'],u['lng']))
        UNITS.append([u['lat'],u['lng'],UNITCATS.index(u['cat']),u['chain'],si,dist,
                      (u['name'] or '')[:60],(u.get('street') or '')[:48],(u.get('cuisine') or '')[:30]])
        if u['name']: per.setdefault(u['cat'],[]).append((dist,u))
    cc={}
    for cat,us in per.items():
        us.sort(key=lambda x:x[0])
        cc[cat]=[[u['name'][:44],(u.get('cuisine') or '')[:26],u['chain'],d] for d,u in us[:12]]
    if cc: COMPS[s['id']]=cc
today=datetime.date.today().strftime('%-d %b %Y')
t=TRANSIT.get(cid)
if t and t[3]=='wiki':
    flowsrc=f"{C['name']} urban rail ridership (annual, published system figure); stop-level flow MODELLED"
elif t:
    flowsrc=f"{C['name']} urban rail ridership (annual, modelled at system level); stop-level flow MODELLED"
else:
    flowsrc="No urban rail system - flow is MODELLED from commercial density only"
META={"built":today,"osm_date":today,"crime_window":"","census":"Census 2021 (1 km grid, Eurostat)",
      "numbat":flowsrc,"sources":{}}
for s in segs: s.pop('_units',None)
outdir=f'{ROOT}/{cid}/data'
os.makedirs(outdir,exist_ok=True)
with open(f'{outdir}/segments.js','w') as f:
    f.write("const SEGMENTS="+json.dumps(segs,separators=(',',':'),ensure_ascii=False)+";\nconst META="+json.dumps(META,separators=(',',':'),ensure_ascii=False)+";\n")
with open(f'{outdir}/units.js','w') as f:
    f.write("const UNITCATS="+json.dumps(UNITCATS)+";\nconst UNITS="+json.dumps(UNITS,separators=(',',':'),ensure_ascii=False)+";\n")
with open(f'{outdir}/competitors.js','w') as f:
    f.write("const COMPETITORS="+json.dumps(COMPS,separators=(',',':'),ensure_ascii=False)+";\n")
print(cid,'segments:',len(segs),'| units:',len(UNITS),'| competitors segs:',len(COMPS))
for f in ('segments.js','units.js','competitors.js'):
    print(f,os.path.getsize(f'{outdir}/{f}')//1024,'KB')
