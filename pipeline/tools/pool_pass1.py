"""Pass 1: collect matching nodes (by city) + wanted way refs + way tags. Saves checkpoint JSON."""
import osmium, json, sys, os
sys.path.insert(0,'/home/sandbox/europe/work')
from cities_eu import CITIES_EU
AMEN={'cafe','restaurant','fast_food','pub','bar','nightclub','theatre','cinema','arts_centre','pharmacy','veterinary'}
LEIS={'fitness_centre','park','garden','common'}
TOUR={'museum','gallery','attraction'}
region=sys.argv[1]
PBF=f'/home/sandbox/europe/dl/pbf/{region}.osm.pbf'
CITY_OF=[(cid,c) for cid,c in CITIES_EU.items() if c['geofabrik'].replace('/','_')==region]
def city_of(la,lo):
    for cid,c in CITY_OF:
        b=c['bbox']
        if b[0]<=la<=b[2] and b[1]<=lo<=b[3]: return cid
    return None
class H(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.out={cid:[] for cid,_ in CITY_OF}; self.ways={}; self.n=0
    def node(self,n):
        self.n+=1
        if self.n%10000000==0: print('nodes scanned',self.n,flush=True)
        t=n.tags
        am=t.get('amenity',''); sh=t.get('shop',''); le=t.get('leisure',''); to=t.get('tourism',''); of=t.get('office',''); rw=t.get('railway',''); st=t.get('station','')
        if not (am in AMEN or sh or le in LEIS or to in TOUR or of in ('coworking','estate_agent','letting_agent') or rw in ('station','halt') or st=='subway'): return
        try: la,lo=n.location.lat,n.location.lon
        except Exception: return
        cid=city_of(la,lo)
        if not cid: return
        self.out[cid].append({'type':'node','id':n.id,'lat':round(la,6),'lon':round(lo,6),'tags':{k:v for k,v in t}})
    def way(self,w):
        t=w.tags
        am=t.get('amenity',''); sh=t.get('shop',''); le=t.get('leisure',''); to=t.get('tourism',''); of=t.get('office','')
        if not (am in AMEN or sh or le in LEIS or to in TOUR or of in ('coworking','estate_agent','letting_agent')): return
        self.ways[w.id]=[{k:v for k,v in t},[nd.ref for nd in w.nodes]]
h=H(); h.apply_file(PBF, locations=False)
print('nodes kept:',{k:len(v) for k,v in h.out.items()},'ways:',len(h.ways),flush=True)
os.makedirs(f'/home/sandbox/europe/work/poolchk',exist_ok=True)
json.dump({'out':h.out,'ways':h.ways},open(f'/home/sandbox/europe/work/poolchk/{region}.json','w'))
print('checkpoint saved',flush=True)
