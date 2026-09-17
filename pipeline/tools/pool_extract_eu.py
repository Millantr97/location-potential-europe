"""Extract commercial POI pools for EU city bboxes from a Geofabrik PBF - SINGLE pass with
disk-backed node location index. Usage: pool_extract_eu.py <region>"""
import osmium, json, sys, os
sys.path.insert(0,'/home/sandbox/europe/work')
from cities_eu import CITIES_EU
AMEN={'cafe','restaurant','fast_food','pub','bar','nightclub','theatre','cinema','arts_centre','pharmacy','veterinary'}
LEIS={'fitness_centre','park','garden','common'}
TOUR={'museum','gallery','attraction'}
region=sys.argv[1]
PBF=f'/home/sandbox/europe/dl/pbf/{region}.osm.pbf'
CITY_OF=[(cid,c) for cid,c in CITIES_EU.items() if c['geofabrik'].replace('/','_')==region]
assert CITY_OF, region
def city_of(la,lo):
    for cid,c in CITY_OF:
        b=c['bbox']
        if b[0]<=la<=b[2] and b[1]<=lo<=b[3]: return cid
    return None
IDX= f'/tmp/locidx_{region}'
os.makedirs(IDX,exist_ok=True)
class H(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.loc=osmium.index.create_map(f'dense_file_array,{IDX}/nodes.dat')
        self.loch=osmium.NodeLocationsForWays(self.loc)
        self.loch.ignore_errors()
        self.out={cid:[] for cid,_ in CITY_OF}
    def node(self,n):
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
        las=[]; los=[]
        for nd in w.nodes:
            try:
                las.append(nd.location.lat); los.append(nd.location.lon)
            except Exception: pass
        if not las: return
        la=sum(las)/len(las); lo=sum(los)/len(los)
        cid=city_of(la,lo)
        if not cid: return
        self.out[cid].append({'type':'way','id':w.id,'center':{'lat':round(la,6),'lon':round(lo,6)},'tags':{k:v for k,v in t}})
h=H()
reader=osmium.io.Reader(PBF)
osmium.apply(reader,h,h.loch)
reader.close()
print('done:',{k:len(v) for k,v in h.out.items()},flush=True)
for cid,_ in CITY_OF:
    d=f'/home/sandbox/europe/repo/pipeline/eu/{cid}'
    os.makedirs(d,exist_ok=True)
    json.dump(h.out[cid],open(f'{d}/pool.json','w'))
    print(cid,'pool:',len(h.out[cid]),flush=True)
