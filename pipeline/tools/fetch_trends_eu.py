"""EU trends. Modes: osm_all (ohsome groupBy per city), gt:<CC> (Google Trends per country, merge into city files)."""
import json, re, sys, time, requests
sys.path.insert(0,'/home/sandbox/europe/work')
from cities_eu import CITIES_EU, WAVE1
ROOT='/home/sandbox/europe/repo'
GROCERY='convenience,supermarket,greengrocer,bakery,butcher,deli,alcohol,newsagent,confectionery,health_food,seafood,cheese,coffee,pastry,wine,frozen_food'
SERVICES='hairdresser,barber,beauty,nail_salon,tanning,massage,tattoo,piercing,laundry,dry_cleaning,florist,optician,hearing_aids,mobile_phone,phone_repair,computer,electronics_repair,pet_grooming,pet,travel_agent,funeral_directors,shoe_repair,tailor,key_cutting,locksmith,photo,print_shop,copyshop,books,charity,second_hand'
YEARS=[str(y) for y in range(2017,2027)]
def ohsome_group(bbox,key):
    for a in range(4):
        try:
            r=requests.post('https://api.ohsome.org/v1/elements/count/groupBy/tag',
                data={'bboxes':bbox,'filter':f'{key}=*','groupByKey':key,'time':'2017-01-01/2026-01-01/P1Y','format':'json'},timeout=110)
            if r.status_code==200:
                return {g['groupByObject'].split('=',1)[1]:{row['timestamp'][:4]:row['value'] for row in g['result']} for g in r.json()['groupByResult']}
            print('ohsome HTTP',r.status_code,flush=True)
        except Exception as e: print('ohsome err',str(e)[:60],flush=True)
        time.sleep(4*(a+1))
    return None
GROC=GROCERY.split(','); SERV=SERVICES.split(',')
def merge(groups,*keys):
    yrs={}
    for k in keys:
        for y,v in groups.get(k,{}).items(): yrs[y]=yrs.get(y,0)+v
    return yrs
def city_osm(cid):
    b=CITIES_EU[cid]['bbox']; bbox=f'{b[1]},{b[0]},{b[3]},{b[2]}'
    am=ohsome_group(bbox,'amenity'); sh=ohsome_group(bbox,'shop'); le=ohsome_group(bbox,'leisure'); of=ohsome_group(bbox,'office')
    if not all(x is not None for x in (am,sh,le,of)): print('FAIL groups',cid); return {}
    return {
     'cafe':merge(am,'cafe'),'restaurant':merge(am,'restaurant'),'fast_food':merge(am,'fast_food'),
     'pub_bar':merge(am,'pub','bar','nightclub'),'grocery':merge(sh,*GROC),
     'fitness':merge(le,'fitness_centre'),'cowork':merge(of,'coworking'),
     'services':merge(sh,*SERV),'agents':merge(of,'estate_agent','letting_agent'),
     'pharmacy':merge(am,'pharmacy'),'vets':merge(am,'veterinary')}
def write_city(cid):
    osm=city_osm(cid)
    if not osm: print('SKIP',cid); return
    src=f"ohsome API (HeiGIT), OpenStreetMap full-history extract, {CITIES_EU[cid]['region']} bbox (same coverage as this site's map), counts at 1 Jan each year"
    T={'years':YEARS,'osm':osm,'osm_source':src,'gt_years':[],'gt':None}
    open(f'{ROOT}/{cid}/data/trends.js','w').write('const TRENDS='+json.dumps(T,separators=(',',':'))+';\n')
    print('written',cid,len(osm),'cats',flush=True)
def read_T(cid):
    t=open(f'{ROOT}/{cid}/data/trends.js').read()
    m=re.search(r'const TRENDS=(\{.*\}|null);?\s*$',t,re.S)
    return json.loads(m.group(1)) if m and m.group(1)!='null' else None
def gt_country(cc):
    from pytrends.request import TrendReq
    lt=open('/home/sandbox/london-location-lens/trends.js').read()
    T=json.loads(re.search(r'const TRENDS=(\{.*\});?\s*$',lt,re.S).group(1))
    kw=T['gt']['kw']; anchor='restaurant'
    pt=TrendReq(hl='en-GB',tz=0,timeout=(30,110),retries=1,backoff_factor=2)
    ids=list(kw); series={}; gtyears=None
    B=5
    for i in range(0,len(ids),B):
        batch=ids[i:i+B]
        kws=[anchor]+[kw[x] for x in batch]
        try:
            pt.build_payload(kws,geo=cc,timeframe='2021-01-01 2026-09-01')
            df=pt.interest_over_time()
            if df.empty: continue
            wk=df.drop(columns=['isPartial'],errors='ignore').resample('YE').mean()
            gtyears=[str(y) for y in wk.index.year]
            for x,k in zip(batch,kws[1:]):
                row={}
                for y,v,a in zip(gtyears,wk[k],wk[anchor]):
                    row[y]=round(float(v)/float(a)*10,1) if a else 0.0
                series[x]=row
        except Exception as e:
            print('gt batch err',cc,str(e)[:80],flush=True)
        time.sleep(3)
    return {'geo':cc,'anchor':anchor,'kw':kw,'series':series,
            'source':f"Google Trends, yearly mean weekly interest index per keyword, geo {cc}, 5-year window, rescaled across batches against shared anchor 'restaurant'"},gtyears
def apply_gt(cc):
    gt=gt_country(cc)
    if not gt or not gt[0] or not gt[0]['series']: print('GT EMPTY',cc); return
    for cid in WAVE1:
        if CITIES_EU[cid]['cc']!=cc: continue
        T=read_T(cid)
        if not T: continue
        T['gt']=gt[0]; T['gt_years']=gt[1]
        open(f'{ROOT}/{cid}/data/trends.js','w').write('const TRENDS='+json.dumps(T,separators=(',',':'))+';\n')
        print('gt applied',cid,flush=True)
if __name__=='__main__':
    tgt=sys.argv[1]
    if tgt=='osm_all':
        for cid in WAVE1: write_city(cid)
    elif tgt.startswith('gt:'):
        apply_gt(tgt[3:])
    else:
        write_city(tgt)
