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
