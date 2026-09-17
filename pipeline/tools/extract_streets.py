"""Extract named highway ways (polylines) per city bbox -> repo/pipeline/eu/<cid>/streets.json"""
import osmium, json, sys, os
sys.path.insert(0,'/home/sandbox/europe/work')
from cities_eu import CITIES_EU
region=sys.argv[1]
PBF=f'/home/sandbox/europe/dl/pbf/{region}.osm.pbf'
CITY_OF=[(cid,c) for cid,c in CITIES_EU.items() if c['geofabrik'].replace('/','_')==region]
assert CITY_OF, region
out={cid:[] for cid,_ in CITY_OF}
fp=osmium.FileProcessor(PBF, osmium.osm.osm_entity_bits.WAY)
fp.with_locations('sparse_file_array,/home/sandbox/europe/dl/locidx_hw.dat')
fp.with_filter(osmium.filter.KeyFilter('highway'))
n=0
for o in fp:
    n+=1
    name=o.tags.get('name')
    if not name: continue
    hw=o.tags.get('highway','')
    if hw in ('footway','path','cycleway','steps','track','service','construction','proposed','corridor','elevator','rest_area','services'): continue
    try:
        pts=[(round(nd.location.lat,6),round(nd.location.lon,6)) for nd in o.nodes if nd.location.valid()]
    except Exception: continue
    if len(pts)<2: continue
    la=sum(p[0] for p in pts)/len(pts); lo=sum(p[1] for p in pts)/len(pts)
    for cid,c in CITY_OF:
        b=c['bbox']
        if b[0]<=la<=b[2] and b[1]<=lo<=b[3]:
            out[cid].append({'name':name,'hw':hw,'pts':pts})
            break
print('ways seen:',n,flush=True)
for cid,_ in CITY_OF:
    d=f'/home/sandbox/europe/repo/pipeline/eu/{cid}'
    os.makedirs(d,exist_ok=True)
    json.dump(out[cid],open(f'{d}/streets.json','w'))
    print(cid,'named streets:',len(out[cid]),flush=True)
