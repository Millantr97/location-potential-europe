import json, math, re, os, sys, collections
sys.path.insert(0,'/home/sandbox/europe/work')
from cities_eu import CITIES_EU
from transit_eu import TRANSIT, PER_STOP_M
from rents_eu import RENTS
from students_eu import STUDENTS
cid=sys.argv[1]; C=CITIES_EU[cid]
ROOT='/home/sandbox/europe/repo'
P=f'{ROOT}/pipeline/eu/{cid}'
os.makedirs(P,exist_ok=True)
DAYPROF=json.load(open(f'{ROOT}/pipeline/eu/nr_day_profile.json'))
FX={'EUR':1.0,'CHF':0.95,'CZK':25.0,'PLN':4.3,'HUF':400.0,'SEK':11.2,'DKK':7.46,'NOK':11.9,'GBP':0.86,'BGN':1.96,'RON':4.98}
if C['cur']=='kr': CURCODE={'SE':'SEK','DK':'DKK','NO':'NOK'}[C['country']]
else: CURCODE={'€':'EUR','CHF ':'CHF','Kč':'CZK','zł':'PLN','Ft':'HUF','lei':'RON','лв':'BGN','£':'GBP'}[C['cur']]
fx=FX[CURCODE]
WEEKS=52.14
pool=json.load(open(f'{P}/pool.json'))
UNITCATS=["cafe","restaurant","fast_food","pub_bar","grocery","shops","fitness","cowork","services","agents","pharmacy","vets"]
SERVICES_SHOPS={'hairdresser','barber','beauty','nail_salon','tanning','massage','tattoo','piercing','laundry','dry_cleaning','florist','optician','hearing_aids','mobile_phone','phone_repair','computer','electronics_repair','pet_grooming','pet','travel_agent','funeral_directors','shoe_repair','tailor','key_cutting','locksmith','photo','print_shop','copyshop','books','charity','second_hand'}
GROCERY_SHOPS={'convenience','supermarket','greengrocer','bakery','butcher','deli','alcohol','newsagent','confectionery','health_food','seafood','cheese','coffee','pastry','wine','frozen_food'}
CHAINS=['costa','starbucks','pret a manger','mcdonald','kfc','subway','pizza hut','domino','popeyes','taco bell','burger king','five guys','vapiano','vips','100 montaditos','rodilla','pans & company','pans and company','telepizza','la tagliatella','foster hollywood','hard rock','paul','brioche doree','la mie caline','hippopotamus','buffalo grill','courtepaille','del arte','nordsee','febo','hema','etos','jumbo','albert heijn','ah to go','kruidvat','lidl','aldi','rewe','edeka','penny','netto','kaufland','rossmann','müller','mueller','spar','billa','merkur','hofer','migros','coop','denner','manor','carrefour','auchan','leclerc','intermarché','intermarche','monoprix','franprix','casino','mercadona','alcampo','eroski','consum','hipercor','el corte inglés','el corte ingles','esselunga','conad','autogrill','bershka','zara','h&m','mango','primark','uniqlo','decathlon','foot locker','snipes','sephora','douglas','rituals','kiko','flying tiger','normal','ikea','mediamarkt','media markt','saturn','fnac','darty','wework','regus','spaces','puregym','basic-fit','basic fit','mcfit','fit star','john reed','clever fit','anytime fitness','fitness park','keepcool','bodystreet','synergym','vivagym','viva gym','altafit','holmes place','go fit','dreamfit','smart fit']
CHAIN_RE=re.compile('|'.join(re.escape(c) for c in sorted(set(CHAINS),key=len,reverse=True)))
def is_chain(t):
    s=((t.get('name') or '')+' '+(t.get('brand') or '')+' '+(t.get('operator') or '')).lower()
    return bool(CHAIN_RE.search(s))
def classify(el):
    t=el.get('tags',{})
    am=t.get('amenity',''); sh=t.get('shop',''); le=t.get('leisure',''); to=t.get('tourism',''); of=t.get('office','')
    if am in ('cafe','restaurant','fast_food'): return am
    if am in ('pub','bar','nightclub'): return 'pub_bar'
    if am=='pharmacy': return 'pharmacy'
    if am=='veterinary': return 'vets'
    if of in ('estate_agent','letting_agent'): return 'agents'
    if of=='coworking': return 'cowork'
    if sh: return 'grocery' if sh in GROCERY_SHOPS else ('services' if sh in SERVICES_SHOPS else ('shops' if sh!='vacant' else None))
    if le=='fitness_centre': return 'fitness'
    if to in ('museum','gallery','attraction') or am in ('theatre','cinema','arts_centre'): return 'culture'
    if le in ('park','garden','common'): return 'park'
    return None
def coord(el):
    if el['type']=='node': return el['lat'],el['lon']
    c=el.get('center',{}); return c.get('lat'),c.get('lon')
def hav(a,b,c,d):
    R=6371000; p1,p2=math.radians(a),math.radians(c)
    dp=math.radians(c-a); dl=math.radians(d-b)
    x=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(x))
BANDS=[(1500,'City centre'),(4000,'1.5-4 km from centre'),(8000,'4-8 km from centre'),(15000,'8-15 km from centre')]
def band(la,lo):
    d=hav(la,lo,C['center'][0],C['center'][1])
    for mx,label in BANDS:
        if d<mx: return label
    return '15+ km from centre'
print('classifying pool',len(pool),flush=True)
units_all=[]; seen=set(); culture=[]; parks=[]; stations=[]; malls=[]
for e in pool:
    k=(e['type'],e['id'])
    if k in seen: continue
    seen.add(k)
    t=e.get('tags',{})
    la,lo=coord(e)
    if not la: continue
    if e['type']=='node' and (t.get('railway') in ('station','halt') or t.get('station')=='subway') and t.get('name'):
        kind='subway' if t.get('station')=='subway' else ('halt' if t.get('railway')=='halt' else 'station')
        stations.append((la,lo,t['name'],kind)); continue
    if t.get('shop')=='mall' and t.get('name'):
        malls.append((la,lo,t['name'])); continue
    cat=classify(e)
    if not cat: continue
    if cat=='park': parks.append((la,lo)); continue
    if cat=='culture': culture.append((la,lo)); continue
    st=(t.get('addr:street') or '').strip(); st=re.sub(r'\s+',' ',st)
    units_all.append({'lat':round(la,5),'lng':round(lo,5),'cat':cat,'chain':1 if is_chain(t) else 0,
        'name':t.get('name',''),'street':st,
        'cuisine':(t.get('cuisine','') or t.get('shop','')).split(';')[0],
        'terrace':1 if (t.get('outdoor_seating','')+t.get('seat:outside','')).lower()=='yes' else 0})
print('units:',len(units_all),'culture:',len(culture),'parks:',len(parks),'stations:',len(stations),'malls:',len(malls),flush=True)
# Fill missing addr:street from nearest named highway geometry point (OSM observed).
SF=f'{P}/streets.json'
if os.path.exists(SF):
    ways=json.load(open(SF)); PG={}
    for w in ways:
        for pt in w['pts'][::2]: PG.setdefault((int(pt[0]/0.002),int(pt[1]/0.002)),[]).append((pt[0],pt[1],w['name']))
    def street_at(la,lo):
        best=None;bd=40.0;ci,cj=int(la/0.002),int(lo/0.002)
        for dx in range(-1,2):
            for dy in range(-1,2):
                for x in PG.get((ci+dx,cj+dy),[]):
                    d=hav(la,lo,x[0],x[1])
                    if d<bd:bd=d;best=x[2]
        return best
    filled=0
    for u in units_all:
        if not u['street']:
            nm=street_at(u['lat'],u['lng'])
            if nm:u['street']=nm;filled+=1
    print('street names filled from nearest way:',filled,flush=True)

def gridify(lst,cell):
    g={}
    for x in lst: g.setdefault((round(x[0]/cell),round(x[1]/cell)),[]).append(x)
    return g
UNIT_G=gridify([(u['lat'],u['lng'],u) for u in units_all],0.004)
CULT_G=gridify(culture,0.004); PARK_G=gridify(parks,0.01); STN_G=gridify(stations,0.015)
def near_units(la,lo,rad):
    out=[]
    ci,cj=round(la/0.004),round(lo/0.004)
    for dx in range(-1,1+1):
        for dy in range(-1,1+1):
            for x in UNIT_G.get((ci+dx,cj+dy),[]):
                if hav(la,lo,x[0],x[1])<=rad: out.append(x[2])
    return out
def near_count(g,la,lo,cell,rad,span):
    n=0
    ci,cj=round(la/cell),round(lo/cell)
    for dx in range(-span,span+1):
        for dy in range(-span,span+1):
            for x in g.get((ci+dx,cj+dy),[]):
                if hav(la,lo,x[0],x[1])<=rad: n+=1
    return n
def near_stations(la,lo):
    ci,cj=round(la/0.015),round(lo/0.015)
    out=[]
    for dx in (-1,0,1):
        for dy in (-1,0,1):
            for x in STN_G.get((ci+dx,cj+dy),[]):
                out.append((hav(la,lo,x[0],x[1]),x[2]))
    return sorted(set((round(d),n) for d,n in out))[:8]
def osm_counts(us):
    counts={c:0 for c in UNITCATS}
    chain={c:0 for c in ('cafe','restaurant','fast_food')}
    food_tot=0; food_ter=0
    for u in us:
        counts[u['cat']]+=1
        if u['cat'] in ('cafe','restaurant','fast_food','pub_bar'):
            food_tot+=1; food_ter+=u.get('terrace',0)
            if u['cat'] in chain and u['chain']: chain[u['cat']]+=1
    return {'cafe':counts['cafe'],'cafe_chain':chain['cafe'],'restaurant':counts['restaurant'],'restaurant_chain':chain['restaurant'],
            'fast_food':counts['fast_food'],'fast_food_chain':chain['fast_food'],'pub_bar':counts['pub_bar'],
            'grocery':counts['grocery'],'grocery_chain':0,'fitness':counts['fitness'],'fitness_chain':0,'cowork':counts['cowork'],
            'services':counts['services'],'agents':counts['agents'],'pharmacy':counts['pharmacy'],'vets':counts['vets'],
            'shops':counts['shops'],'terrace_share':round(food_ter/food_tot,3) if food_tot else 0}
# ---------- census grid ----------
cells=json.load(open(f'/home/sandbox/europe/work/census/{cid}.json'))
CELL_G={}
for c in cells: CELL_G.setdefault((round(c[0]/0.01),round(c[1]/0.01)),[]).append(c)
valid=[c for c in cells if c[2]>0]
CT=[sum(c[i] for c in valid if c[i]>=0) for i in range(2,10)]
EMP_CITY=(CT[5]/CT[0]) if CT[0]>0 and CT[5]>0 else 0.48
def cell_demo(la,lo):
    best=None; bd=1e9
    ci,cj=round(la/0.01),round(lo/0.01)
    for dx in range(-1,2):
        for dy in range(-1,2):
            for c in CELL_G.get((ci+dx,cj+dy),[]):
                d=hav(la,lo,c[0],c[1])
                if d<bd: bd=d; best=c
    return best,bd
def demo_at(la,lo):
    c,d=cell_demo(la,lo)
    if c is None or d>2200: return None,None
    T=c[2]
    if T<=0: return None,d
    if any(v<0 for v in c[2:10]):
        p=dict(residents=T,pct15=100*CT[1]/CT[0],pct1564=100*CT[2]/CT[0],emp=100*EMP_CITY,
               nat=CT[5]/CT[0],eu=CT[6]/CT[0],oth=CT[7]/CT[0])
    else:
        p=dict(residents=T,pct15=100*c[3]/T,pct1564=100*c[4]/T,emp=100*c[6]/T,
               nat=c[7]/T,eu=c[8]/T,oth=c[9]/T)
    nat,eu,oth=p['nat'],p['eu'],p['oth']
    lsoa={'code':'grid1km','name':'Census 2021 grid cell (1 km)','residents':p['residents'],
          'pct20_39':round(p['pct1564'],1),'pct_under20':round(p['pct15'],1),
          'pct_students':STUDENTS.get(cid,7.0),'pct_prof':round(p['emp'],1),
          'pct_nonuk':round(100*(eu+oth),1),
          'diversity':round(1-(nat*nat+eu*eu+oth*oth),3),
          'top_eth':[[f"Born in {C['country_name']}",round(100*nat,1)],['Born in another EU country',round(100*eu,1)],['Born outside the EU',round(100*oth,1)]]}
    return lsoa,d
# ---------- transit flow (MODELLED, calibrated) ----------
rid_m,nst_cfg,mode,tsrc=TRANSIT.get(cid,(None,None,'rail','modelled'))
byname={}
for la,lo,nm,kind in stations:
    key=' '.join(nm.lower().split())
    if key not in byname: byname[key]=[la,lo,nm,kind]
stn=list(byname.values())
n_stn=len(stn)
if rid_m is None:
    per=PER_STOP_M.get(mode,0.5)
    city_total=(nst_cfg or n_stn or 10)*per*1e6
else:
    city_total=rid_m*1e6
dens=[max(1,len(near_units(la,lo,400))) for la,lo,nm,kind in stn]
med_dens=sorted(dens)[len(dens)//2] if dens else 1
TW={'station':1.2,'subway':1.0,'halt':0.3}
weights=[]
for (la,lo,nm,kind),dn in zip(stn,dens):
    df=min(3.0,max(0.25,dn/max(1,med_dens)))
    weights.append(TW.get(kind,1.0)*df)
wsum=sum(weights) or 1.0
stn_annual={nm:city_total*w/wsum for (la,lo,nm,kind),w in zip(stn,weights)}
def anchors_for(nm):
    a=stn_annual.get(nm,0)
    days={k:a/WEEKS*DAYPROF[k] for k in ('mon','mid','fri','sat','sun')}
    return {'station':nm,'mode':'MODELLED','annual':a,'_days':days,'src':'modelled'}
# ---------- area segments ----------
areas=[]; used_ids=set()
def slug(n): return re.sub(r'-+','-',re.sub(r'[^a-z0-9]+','-',n.lower())).strip('-')
for la,lo,nm,kind in stn:
    sid='st-'+slug(nm); base=sid; k=2
    while sid in used_ids: sid=f'{base}-{k}'; k+=1
    used_ids.add(sid)
    areas.append(dict(id=sid,name=f'{nm} station area',lat=round(la,5),lng=round(lo,5),
                      stype='transport_hub',anchors=[(nm,'MODELLED')]))
for la,lo,nm in malls:
    sid='mall-'+slug(nm); base=sid; k=2
    while sid in used_ids: sid=f'{base}-{k}'; k+=1
    used_ids.add(sid)
    areas.append(dict(id=sid,name=nm,lat=round(la,5),lng=round(lo,5),stype='managed_estate',anchors=[]))
print('area segments:',len(areas),flush=True)
RENT={'retail_rv_m2':round(RENTS[cid][0]*fx),'office_rv_m2':round(RENTS[cid][1]*fx),'basis':'modelled'}
A=[]
for s in areas:
    sid=s['id']
    anch=[anchors_for(nm) for nm,tag in s['anchors']]
    us=near_units(s['lat'],s['lng'],250)
    osm=osm_counts(us)
    osm['culture']=near_count(CULT_G,s['lat'],s['lng'],0.004,250,1)
    osm['parks_600']=near_count(PARK_G,s['lat'],s['lng'],0.01,600,1)
    near9=[x for x in near_stations(s['lat'],s['lng']) if x[0]<=900]
    lsoa,ddist=demo_at(s['lat'],s['lng'])
    if lsoa is None: print('WARN no census cell for',sid)
    A.append({'id':sid,'name':s['name'],'borough':C['name'],'zone':band(s['lat'],s['lng']),
        'lat':s['lat'],'lng':s['lng'],'stype':s['stype'],'lvl':'area','weak':False,
        'anchors':[{'station':a['station'],'mode':'MODELLED','annual':round(a['annual']),'src':'modelled','days_modelled':True} for a in anch],
        '_days':{k:sum(a['_days'][k] for a in anch) for k in ('mon','mid','fri','sat','sun')},
        '_annual':sum(a['annual'] for a in anch),
        'transport':{'stations_900m':len(near9),'names':[n for _,n in near9]},
        'osm':osm,'lsoa':lsoa,'crime':None,'rent':dict(RENT),'_units':us})
print('areas built:',len(A),flush=True)
# ---------- street clustering ----------
bystreet=collections.defaultdict(list)
for i,u in enumerate(units_all):
    if u['street']: bystreet[u['street']].append(i)
CELL=0.0032
clusters=[]
for st,idxs in bystreet.items():
    if len(idxs)<6: continue
    cells2=collections.defaultdict(list)
    for i in idxs:
        u=units_all[i]; cells2[(int(u['lat']/CELL),int(u['lng']/(CELL/math.cos(math.radians(u['lat'])))))].append(i)
    occ=set(cells2); comp_id={}; comps=[]
    for c in occ:
        if c in comp_id: continue
        q=[c]; comp=[]; comp_id[c]=1
        while q:
            cur=q.pop(); comp.append(cur)
            for dx in (-1,0,1):
                for dy in (-1,0,1):
                    nb=(cur[0]+dx,cur[1]+dy)
                    if nb in occ and nb not in comp_id: comp_id[nb]=1; q.append(nb)
        comps.append(comp)
    for comp in comps:
        allidx=[i for c in comp for i in cells2[c]]
        if len(allidx)<8: continue
        lats=[units_all[i]['lat'] for i in allidx]; lngs=[units_all[i]['lng'] for i in allidx]
        span_lat=(max(lats)-min(lats))*111000; span_lng=(max(lngs)-min(lngs))*111000*math.cos(math.radians(sum(lats)/len(lats)))
        span=max(span_lat,span_lng)
        if span<=420: clusters.append((st,allidx)); continue
        nparts=max(2,round(span/380))
        horiz=span_lng>=span_lat
        key=lambda i:(units_all[i]['lng'] if horiz else units_all[i]['lat'])
        sidx=sorted(allidx,key=key); per=len(sidx)/nparts
        for p in range(nparts):
            part=sidx[round(p*per):round((p+1)*per)]
            if len(part)>=8: clusters.append((st,part))
            elif clusters and clusters[-1][0]==st: clusters[-1][1].extend(part)
print('raw clusters >=8:',len(clusters),flush=True)
cent=[]
for st,idxs in clusters:
    la=sorted(units_all[i]['lat'] for i in idxs)[len(idxs)//2]
    lo=sorted(units_all[i]['lng'] for i in idxs)[len(idxs)//2]
    cent.append((la,lo))
CG={}
for ci2,(la,lo) in enumerate(cent): CG.setdefault((round(la,3),round(lo,3)),[]).append(ci2)
attached=0; claimed=set(i for _,idxs in clusters for i in idxs)
for i,u in enumerate(units_all):
    if u['street'] or i in claimed: continue
    best=None; bd=80
    for dla in (-0.002,-0.001,0,0.001,0.002):
        for dlo in (-0.002,-0.001,0,0.001,0.002):
            for ci2 in CG.get((round(u['lat']+dla,3),round(u['lng']+dlo,3)),[]):
                d=hav(u['lat'],u['lng'],cent[ci2][0],cent[ci2][1])
                if d<bd: bd=d; best=ci2
    if best is not None: clusters[best][1].append(i); claimed.add(i); attached+=1
print('untagged attached:',attached,flush=True)
AG={}
for i,a in enumerate(A): AG.setdefault((round(a['lat'],2),round(a['lng'],2)),[]).append(i)
def nearest_anchor(la,lo,maxd=1e9):
    best=None; bd=maxd
    for dla in (-0.02,-0.01,0,0.01,0.02):
        for dlo in (-0.03,-0.015,0,0.015,0.03):
            for i in AG.get((round(la+dla,2),round(lo+dlo,2)),[]):
                d=hav(la,lo,A[i]['lat'],A[i]['lng'])
                if d<bd: bd=d; best=i
    return best,bd
streets=[]
for st,idxs in clusters:
    us=[units_all[i] for i in idxs]
    la=sorted(u['lat'] for u in us)[len(us)//2]
    lo=sorted(u['lng'] for u in us)[len(us)//2]
    ai,dist=nearest_anchor(la,lo)
    streets.append({'street':st,'lat':round(la,5),'lng':round(lo,5),'units':us,
                    'parent':A[ai]['id'] if ai is not None else None,'parent_dist':round(dist),
                    'parent_name':A[ai]['name'] if ai is not None else None})
print('streets:',len(streets),'| units inside:',sum(len(s['units']) for s in streets),flush=True)
par_by_id={p['id']:p for p in A}
used_names={p['name'].lower() for p in A}
used_ids2={p['id'] for p in A}
new=[]
for i,st in enumerate(streets):
    par=par_by_id.get(st['parent']); pdist=st['parent_dist']; sub=pdist<=900
    area_nm=(st['parent_name'].replace(' station area','') if sub and st['parent_name'] else '') or C['name']
    nm=f"{st['street']} ({area_nm})"
    if nm.lower() in used_names: nm=f"{st['street']} ({area_nm} {(i%9)+2})"
    used_names.add(nm.lower())
    sid=slug(nm); base=sid; k=2
    while sid in used_ids2: sid=f'{base}-{k}'; k+=1
    used_ids2.add(sid)
    us=st['units']; n=len(us)
    osm=osm_counts(us)
    if sub:
        osm['culture']=par['osm']['culture']; osm['parks_600']=par['osm']['parks_600']
        transport=dict(par['transport']); lsoa=dict(par['lsoa']) if par['lsoa'] else None
        anchors=[dict(a) for a in par['anchors']]
        within=sum(1 for u in us if hav(par['lat'],par['lng'],u['lat'],u['lng'])<=250)
        share=max(0.03,min(0.7, within/max(1,len(par['_units']))))
        annual=round(par['_annual']*share)
        days={k:round(par['_days'][k]*share,1) for k in par['_days']}
        mfrom=par['name']
    else:
        la,lo=st['lat'],st['lng']
        osm['culture']=near_count(CULT_G,la,lo,0.004,250,1)
        osm['parks_600']=near_count(PARK_G,la,lo,0.01,600,1)
        near9=[x for x in near_stations(la,lo) if x[0]<=900]
        transport={'stations_900m':len(near9),'names':[x[1] for x in near9]}
        lsoa,_=demo_at(la,lo)
        if lsoa is None and par and par['lsoa']: lsoa=dict(par['lsoa'])
        anchors=[]; share=None; annual=0; days={k:0.0 for k in ('mon','mid','fri','sat','sun')}; mfrom=None
    stype='high_street' if n>=40 else 'side_street'
    s={'id':sid,'name':nm,'borough':C['name'],'zone':band(st['lat'],st['lng']),
       'lat':st['lat'],'lng':st['lng'],'stype':stype,'lvl':'street','weak':True,
       'anchors':anchors,
       'flow':{'annual_total':annual,'days':days,'modelled_from':mfrom,'share':round(share,3) if share else None},
       'transport':transport,'osm':osm,'lsoa':lsoa,'crime':None,'rent':dict(RENT),
       '_units':us}
    new.append(s)
print('streets enriched:',len(new),flush=True)
for p in A:
    days={k:round(v,1) for k,v in p.pop('_days').items()}
    annual=p.pop('_annual')
    p['flow']={'annual_total':annual,'days':days}
    p['crime_per1000']=None
claimed=set()
for s in new:
    for u in s['_units']: claimed.add((round(u['lat'],4),round(u['lng'],4),u['cat']))
dropped=0
for p in A:
    keep=[]
    for u in p['_units']:
        k=(round(u['lat'],4),round(u['lng'],4),u['cat'])
        if k in claimed: dropped+=1; continue
        keep.append(u)
    if len(keep)!=len(p['_units']):
        p['_units']=keep
        oc=osm_counts(keep)
        for c in UNITCATS: p['osm'][c]=oc[c]
        for c in ('cafe','restaurant','fast_food'): p['osm'][c+'_chain']=oc[c+'_chain']
        p['osm']['terrace_share']=oc['terrace_share']
print('parent units moved to streets:',dropped,flush=True)
segs=A+new
# lsoa None -> city median
withlsoa=[s for s in segs if s['lsoa']]
med_res=sorted(s['lsoa']['residents'] for s in withlsoa)[len(withlsoa)//2]
med1564=sorted(s['lsoa']['pct20_39'] for s in withlsoa)[len(withlsoa)//2]
med15=sorted(s['lsoa']['pct_under20'] for s in withlsoa)[len(withlsoa)//2]
medemp=sorted(s['lsoa']['pct_prof'] for s in withlsoa)[len(withlsoa)//2]
medab=sorted(s['lsoa']['pct_nonuk'] for s in withlsoa)[len(withlsoa)//2]
for s in segs:
    if not s['lsoa']:
        s['lsoa']={'code':'','name':f"({C['name']} median)",'residents':med_res,'pct20_39':med1564,'pct_under20':med15,
                   'pct_students':STUDENTS.get(cid,7.0),'pct_prof':medemp,'pct_nonuk':medab,'diversity':0.5,'top_eth':[]}
        s['weak']=True
    s['crime']=None
    f=s['flow']
    days=f['days']; weekly=days['mon']+3*days['mid']+days['fri']+days['sat']+days['sun']
    ws=(days['sat']+days['sun'])/weekly if weekly else 0
    f['weekend_share']=round(ws,3); f['weekend_ratio_norm']=0; f['fri_sat_norm']=0
    f['day_rel']={k:round(days[k]/days['mid'],3) if days['mid'] else 0 for k in days}
med_dayrel={k:sorted(s['flow']['day_rel'][k] for s in segs)[len(segs)//2] for k in ('mon','mid','fri','sat','sun')}
med_ws=sorted(s['flow']['weekend_share'] for s in segs)[len(segs)//2]
for s in segs:
    if s['lvl']=='street' and not s['anchors']:
        s['flow']['day_rel']=dict(med_dayrel); s['flow']['weekend_share']=round(med_ws,3)
# ---------- norms + model (within city only) ----------
def normf(vals):
    lo,hi=min(vals),max(vals)
    return lambda v:(v-lo)/(hi-lo) if hi>lo else 0.5
nWk=normf([s['flow']['weekend_share'] for s in segs])
nFS=normf([(s['flow']['days']['fri']+s['flow']['days']['sat'])/max(1,sum(s['flow']['days'].values())) for s in segs])
logn=normf([math.log10(1+s['flow']['annual_total']) for s in segs])
nCowork=normf([math.log10(1+s['osm']['cowork']) for s in segs])
nOffice=normf([s['rent']['office_rv_m2']/fx for s in segs])
STYPE_MULT={'major_retail':1.45,'transport_hub':1.10,'high_street':1.15,'side_street':0.95,'market':1.00,'managed_estate':1.35}
retail_eur=RENTS[cid][0]; office_eur=RENTS[cid][1]
for s in segs:
    f=s['flow']
    f['weekend_ratio_norm']=round(nWk(f['weekend_share']),3)
    f['fri_sat_norm']=round(nFS((f['days']['fri']+f['days']['sat'])/max(1,sum(f['days'].values()))),3)
    o=s['osm']; fl=logn(math.log10(1+f['annual_total']))
    totv=max(1,o['cafe']+o['restaurant']+o['fast_food']+o['pub_bar']+o['grocery']+o['shops']+o['culture']+o['cowork'])
    mix={k:o[k]/totv for k in ('cafe','restaurant','fast_food','pub_bar','grocery','shops','culture','cowork')}
    w={'early':0.10+0.25*mix['cafe']+0.10*mix['grocery']+0.15*mix['cowork'],
       'midday':0.28+0.15*mix['cafe']+0.15*mix['restaurant']+0.25*mix['shops']+0.10*mix['fast_food'],
       'afternoon':0.22+0.20*mix['shops']+0.25*mix['culture']+0.10*mix['grocery'],
       'evening':0.28+0.40*mix['restaurant']+0.45*mix['pub_bar']+0.10*mix['culture'],
       'late':0.12+0.55*mix['pub_bar']+0.20*mix['fast_food']}
    w['early']*=0.65+0.55*(1-f['weekend_share'])
    w['late']*=0.55+0.8*f['fri_sat_norm']
    tw=sum(w.values())
    rhythm={k:round(v/tw,3) for k,v in w.items()}
    food_chain_share=(o['cafe_chain']+o['restaurant_chain']+o['fast_food_chain'])/max(1,o['cafe']+o['restaurant']+o['fast_food'])
    spend_eur=min(95,max(6,5+0.055*retail_eur+0.20*s['lsoa']['pct_prof']+8*food_chain_share+4*fl))
    spend=round(spend_eur*fx)
    office=round(min(1,max(0,0.45*nCowork(math.log10(1+o['cowork']))+0.35*(1-f['weekend_share'])+0.20*nOffice(s['rent']['office_rv_m2']/fx))),2)
    rent_est=round(s['rent']['retail_rv_m2']*STYPE_MULT.get(s['stype'],1.0)*(1+0.30*fl))
    s['model']={'spend_est':spend,'office_skew':office,'rhythm':rhythm}
    s['rent']['est_rent_m2']=rent_est
json.dump(segs,open(f'{P}/segments_full2.json','w'))
print('TOTAL segments:',len(segs),'(areas',len(A),'+ streets',len(new),')')
zero=[s['id'] for s in A if s['flow']['annual_total']<=0]
print('ZERO-FLOW areas:',len(zero))
nolsoa=[s['id'] for s in segs if s['lsoa']['code']=='']
print('median-filled lsoa:',len(nolsoa))
