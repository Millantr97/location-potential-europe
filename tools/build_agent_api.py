#!/usr/bin/env python3
"""Build static, agent-readable endpoints from the published city datasets."""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE='https://millantr97.github.io/location-potential-europe/'

def read_json_assignment(path,name):
    text=path.read_text()
    m=re.search(rf'(?:window\.)?{re.escape(name)}\s*=\s*',text)
    if not m: raise ValueError(f'Cannot parse {name} in {path}')
    value,end=json.JSONDecoder().raw_decode(text[m.end():])
    return value

def cities():
    text=(ROOT/'cities.js').read_text()
    m=re.search(r'window\.CITIES=(\[.*?\]);\n',text,re.S)
    return [c for c in json.loads(m.group(1)) if c['id']!='hub']

def zone_record(s):
    flow=s.get('flow') or {}; trans=s.get('transport') or {}; osm=s.get('osm') or {}; ctx=s.get('lsoa') or {}; rent=s.get('rent') or {}
    return {
      'id':s.get('id'),'name':s.get('name'),'area':s.get('borough'),'level':s.get('lvl'),
      'anchor_observed':{'lat':s.get('lat'),'lng':s.get('lng')},
      'observed':{'commercial_features':osm,'stations_within_900m':trans.get('stations_900m'),'station_names':trans.get('names') or []},
      'area_context':{'geography_code':ctx.get('code'),'geography_name':ctx.get('name'),'residents':ctx.get('residents'),'age_20_39_pct':ctx.get('pct20_39'),'under_20_pct':ctx.get('pct_under20'),'foreign_born_pct':ctx.get('pct_nonuk'),'degree_or_higher_pct':ctx.get('pct_prof')},
      'modelled':{'annual_station_flow_anchor':flow.get('annual_total'),'flow_source_area':flow.get('modelled_from'),'retail_rent_per_m2':rent.get('retail_rv_m2'),'office_rent_per_m2':rent.get('office_rv_m2'),'estimated_rent_per_m2':rent.get('est_rent_m2')}
    }

def main():
    out=ROOT/'api/v1/cities'; out.mkdir(parents=True,exist_ok=True)
    catalogue=[]; total=0
    for c in cities():
      p=ROOT/c['url']/'data/segments.js'
      if not p.exists(): continue
      segs=read_json_assignment(p,'SEGMENTS'); total+=len(segs)
      doc={'schema_version':'1.0','dataset_version':'2026-09-20','city':{k:c.get(k) for k in ('id','name','country','region','cur','lat','lng')},
        'labels':{'anchor_observed':'OBSERVED','observed':'OBSERVED','area_context':'AREA CONTEXT','modelled':'MODELLED'},
        'warning':'Planning and shortlisting data, not a valuation or premises-availability feed. Modelled values are estimates; verify locally before committing.',
        'score_endpoints':BASE+'api/v1/concepts/{concept}.json','zones':[zone_record(s) for s in segs]}
      dest=out/f"{c['id']}.json"; dest.write_text(json.dumps(doc,separators=(',',':'),ensure_ascii=False))
      catalogue.append({**{k:c.get(k) for k in ('id','name','country','region','cur','lat','lng')},'zone_count':len(segs),'endpoint':BASE+f"api/v1/cities/{c['id']}.json"})
    concepts=sorted(p.stem for p in (ROOT/'api/v1/concepts').glob('*.json'))
    index={'schema_version':'1.0','dataset_version':'2026-09-20','source_site':BASE,'city_count':len(catalogue),'zone_count':total,
      'labels':{'observed':'OBSERVED','area_context':'AREA CONTEXT','modelled':'MODELLED'},
      'cities':catalogue,'concepts':[{'id':x,'score_endpoint':BASE+f'api/v1/concepts/{x}.json'} for x in concepts],
      'openapi':BASE+'openapi.json','documentation':BASE+'developers/','llms':BASE+'llms.txt'}
    (ROOT/'api/v1/index.json').write_text(json.dumps(index,separators=(',',':'),ensure_ascii=False))
    print(f'Built {len(catalogue)} city endpoints with {total:,} zones; {len(concepts)} score endpoints')
if __name__=='__main__': main()
