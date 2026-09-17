"""Extract POI pool and named highway geometry from one city PBF. Usage: cid pbf"""
import osmium,json,sys,os
sys.path.insert(0,'/home/sandbox/europe/work');from cities_eu import CITIES_EU
cid,pbf=sys.argv[1:];c=CITIES_EU[cid];b=c['bbox']
AMEN={'cafe','restaurant','fast_food','pub','bar','nightclub','theatre','cinema','arts_centre','pharmacy','veterinary'};LEIS={'fitness_centre','park','garden','common'};TOUR={'museum','gallery','attraction'}
def inside(a,o):return b[0]<=a<=b[2] and b[1]<=o<=b[3]
pool=[];streets=[];SKIP={'footway','path','cycleway','steps','track','service','construction','proposed','corridor','elevator','rest_area','services'}
fp=osmium.FileProcessor(pbf,osmium.osm.osm_entity_bits.NODE|osmium.osm.osm_entity_bits.WAY);fp.with_locations('sparse_file_array,/tmp/city_locations.dat')
for o in fp:
 t=o.tags;typ=o.type_str();isn=typ=='n'
 if isn:
  try:a,z=o.location.lat,o.location.lon
  except:continue
 else:
  try: pts0=[(n.location.lat,n.location.lon) for n in o.nodes if n.location.valid()]
  except:continue
  if not pts0:continue
  a=sum(x for x,_ in pts0)/len(pts0);z=sum(y for _,y in pts0)/len(pts0)
 if not inside(a,z):continue
 am=t.get('amenity','');sh=t.get('shop','');le=t.get('leisure','');to=t.get('tourism','');of=t.get('office','');rw=t.get('railway','');st=t.get('station','')
 if am in AMEN or sh or le in LEIS or to in TOUR or of in ('coworking','estate_agent','letting_agent') or (isn and (rw in ('station','halt') or st=='subway')):
  q={'type':'node' if isn else 'way','id':o.id,'tags':{k:v for k,v in t}}
  if isn:q.update(lat=round(a,6),lon=round(z,6))
  else:q['center']={'lat':round(a,6),'lon':round(z,6)}
  pool.append(q)
 if not isn and t.get('name') and t.get('highway','') not in SKIP:
  pts=[(round(x,6),round(y,6)) for x,y in pts0]
  if len(pts)>=2:streets.append({'name':t['name'],'hw':t.get('highway',''),'pts':pts})
d=f'/home/sandbox/europe/repo/pipeline/eu/{cid}';os.makedirs(d,exist_ok=True);json.dump(pool,open(d+'/pool.json','w'));json.dump(streets,open(d+'/streets.json','w'));print(cid,'pool',len(pool),'streets',len(streets))
