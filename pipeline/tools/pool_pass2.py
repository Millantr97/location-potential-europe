"""Pass 2: resolve wanted node coords, assemble way centroids, write per-city pool.json."""
import osmium, json, sys, os
sys.path.insert(0,'/home/sandbox/europe/work')
from cities_eu import CITIES_EU
region=sys.argv[1]
PBF=f'/home/sandbox/europe/dl/pbf/{region}.osm.pbf'
CITY_OF=[(cid,c) for cid,c in CITIES_EU.items() if c['geofabrik'].replace('/','_')==region]
def city_of(la,lo):
    for cid,c in CITY_OF:
        b=c['bbox']
        if b[0]<=la<=b[2] and b[1]<=lo<=b[3]: return cid
    return None
chk=json.load(open(f'/home/sandbox/europe/work/poolchk/{region}.json'))
out={cid:[dict(e) for e in lst] for cid,lst in chk['out'].items()}
ways={int(k):v for k,v in chk['ways'].items()}
WANT=set()
for wid,(tags,refs) in ways.items(): WANT.update(refs)
print('wanted nodes:',len(WANT),flush=True)
class W(osmium.SimpleHandler):
    def __init__(h2): super().__init__(); h2.coords={}; h2.n=0
    def node(h2,n):
        h2.n+=1
        if h2.n%10000000==0: print('pass2 nodes',h2.n,flush=True)
        if n.id in WANT:
            try: h2.coords[n.id]=(n.location.lon,n.location.lat)
            except Exception: pass
w=W(); w.apply_file(PBF, locations=False)
print('coords resolved:',len(w.coords),flush=True)
added={cid:0 for cid,_ in CITY_OF}
for wid,(tags,refs) in ways.items():
    pts=[w.coords[r] for r in refs if r in w.coords]
    if not pts: continue
    lo=sum(p[0] for p in pts)/len(pts); la=sum(p[1] for p in pts)/len(pts)
    cid=city_of(la,lo)
    if not cid: continue
    out[cid].append({'type':'way','id':wid,'center':{'lat':round(la,6),'lon':round(lo,6)},'tags':tags})
    added[cid]+=1
for cid,_ in CITY_OF:
    d=f'/home/sandbox/europe/repo/pipeline/eu/{cid}'
    os.makedirs(d,exist_ok=True)
    json.dump(out[cid],open(f'{d}/pool.json','w'))
    print(cid,'pool:',len(out[cid]),'(ways',added[cid],')',flush=True)
os.remove(f'/home/sandbox/europe/work/poolchk/{region}.json')
print('done',flush=True)
