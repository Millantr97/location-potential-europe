"""Two-phase named-highway extraction for big PBFs. mode=ways|nodes <region>"""
import osmium, json, sys, os, math
sys.path.insert(0,'/home/sandbox/europe/work')
from cities_eu import CITIES_EU
mode,region=sys.argv[1],sys.argv[2]
PBF=f'/home/sandbox/europe/dl/pbf/{region}.osm.pbf'
CITY_OF=[(cid,c) for cid,c in CITIES_EU.items() if c['geofabrik'].replace('/','_')==region]
assert CITY_OF, region
TMP=f'/tmp/hw_{region}.json'
SKIP={'footway','path','cycleway','steps','track','service','construction','proposed','corridor','elevator','rest_area','services'}
if mode=='ways':
    ways=[]
    for o in osmium.FileProcessor(PBF, osmium.osm.osm_entity_bits.WAY):
        name=o.tags.get('name')
        if not name: continue
        hw=o.tags.get('highway','')
        if hw in SKIP: continue
        ways.append([o.id,name,hw,[nd.ref for nd in o.nodes]])
    json.dump(ways,open(TMP,'w'))
    ids=set()
    for w in ways: ids.update(w[3])
    json.dump(sorted(ids),open(TMP+'.ids','w'))
    print('ways kept:',len(ways),'node ids:',len(ids))
else:
    ways=json.load(open(TMP)); ids=set(json.load(open(TMP+'.ids')))
    bboxes=[c['bbox'] for _,c in CITY_OF]
    pad=0.06
    def in_any(la,lo):
        for b in bboxes:
            if b[0]-pad<=la<=b[2]+pad and b[1]-pad<=lo<=b[3]+pad: return True
        return False
    coords={}
    for o in osmium.FileProcessor(PBF, osmium.osm.osm_entity_bits.NODE):
        if o.id in ids:
            la,lo=o.location.lat,o.location.lon
            if in_any(la,lo): coords[o.id]=(round(la,6),round(lo,6))
    print('coords resolved:',len(coords),'of',len(ids))
    out={cid:[] for cid,_ in CITY_OF}
    for wid,name,hw,refs in ways:
        pts=[coords[r] for r in refs if r in coords]
        if len(pts)<2: continue
        la=sum(p[0] for p in pts)/len(pts); lo=sum(p[1] for p in pts)/len(pts)
        for cid,c in CITY_OF:
            b=c['bbox']
            if b[0]<=la<=b[2] and b[1]<=lo<=b[3]:
                out[cid].append({'name':name,'hw':hw,'pts':pts}); break
    for cid,_ in CITY_OF:
        d=f'/home/sandbox/europe/repo/pipeline/eu/{cid}'
        os.makedirs(d,exist_ok=True)
        json.dump(out[cid],open(f'{d}/streets.json','w'))
        print(cid,'named streets:',len(out[cid]))
