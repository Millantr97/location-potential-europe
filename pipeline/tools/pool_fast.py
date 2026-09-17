"""Fast pool extract: pyosmium FileProcessor, C++ tag filter + location handling, one pass."""
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
    hits=[(cid,c) for cid,c in CITY_OF if c['bbox'][0]<=la<=c['bbox'][2] and c['bbox'][1]<=lo<=c['bbox'][3]]
    if not hits:return None
    return min(hits,key=lambda x:(la-x[1]['center'][0])**2+(lo-x[1]['center'][1])**2)[0]
out={cid:[] for cid,_ in CITY_OF}
fp=osmium.FileProcessor(PBF, osmium.osm.osm_entity_bits.NODE | osmium.osm.osm_entity_bits.WAY)
fp.with_locations('sparse_file_array,/tmp/pool_locations.dat')
fp.with_filter(osmium.filter.KeyFilter('amenity','shop','leisure','tourism','office','railway','station'))
n=0
for o in fp:
    n+=1
    t=o.tags
    am=t.get('amenity',''); sh=t.get('shop',''); le=t.get('leisure',''); to=t.get('tourism',''); of=t.get('office',''); rw=t.get('railway',''); st=t.get('station','')
    is_node = o.type_str()=='n'
    if not (am in AMEN or sh or le in LEIS or to in TOUR or of in ('coworking','estate_agent','letting_agent') or (is_node and (rw in ('station','halt') or st=='subway'))): continue
    if is_node:
        try: la,lo=o.location.lat,o.location.lon
        except Exception: continue
        cid=city_of(la,lo)
        if not cid: continue
        out[cid].append({'type':'node','id':o.id,'lat':round(la,6),'lon':round(lo,6),'tags':{k:v for k,v in t}})
    else:
        try:
            las=[nd.location.lat for nd in o.nodes if nd.location.valid()]
            los=[nd.location.lon for nd in o.nodes if nd.location.valid()]
        except Exception: continue
        if not las: continue
        la=sum(las)/len(las); lo=sum(los)/len(los)
        cid=city_of(la,lo)
        if not cid: continue
        out[cid].append({'type':'way','id':o.id,'center':{'lat':round(la,6),'lon':round(lo,6)},'tags':{k:v for k,v in t}})
print('objects seen:',n,flush=True)
for cid,_ in CITY_OF:
    d=f'/home/sandbox/europe/repo/pipeline/eu/{cid}'
    os.makedirs(d,exist_ok=True)
    json.dump(out[cid],open(f'{d}/pool.json','w'))
    print(cid,'pool:',len(out[cid]),flush=True)
