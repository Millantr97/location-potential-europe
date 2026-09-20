#!/usr/bin/env python3
import osmium,json,collections,sys,math
from cities import CITIES
cid,pbf,out=sys.argv[1:4]; C=CITIES[cid]; B=C['bbox']
AMEN={'cafe','restaurant','fast_food','pub','bar','nightclub','theatre','cinema','arts_centre','pharmacy','veterinary'};LEIS={'fitness_centre','park','garden','common'};TOUR={'museum','gallery','attraction'}
items=[]; fp=osmium.FileProcessor(pbf,osmium.osm.osm_entity_bits.NODE);fp.with_filter(osmium.filter.KeyFilter('amenity','shop','leisure','tourism','office','railway','station'))
for n in fp:
 try:la,lo=n.location.lat,n.location.lon
 except:continue
 if not(B[0]<=la<=B[2] and B[1]<=lo<=B[3]):continue
 t=n.tags;am=t.get('amenity','');sh=t.get('shop','');le=t.get('leisure','');to=t.get('tourism','');of=t.get('office','');rw=t.get('railway','');st=t.get('station','')
 if am in AMEN or sh or le in LEIS or to in TOUR or of in ('coworking','estate_agent','letting_agent') or rw in ('station','halt') or st=='subway':items.append({'lat':round(la,6),'lng':round(lo,6),'tags':{k:v for k,v in t}})
json.dump(items,open(out,'w'),separators=(',',':'));print(cid,len(items),'observed objects')
