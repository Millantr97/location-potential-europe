import json,csv,re,unicodedata,sys,math
from difflib import SequenceMatcher
from shapely.geometry import shape,Point
sys.path.insert(0,'work');from cities_eu import CITIES_EU,SHIP
T=json.load(open('work/eurostat250.json'))['cities']
# EU/EFTA only; UK handled as existing/copy source separately
T=[r for r in T if not r['code'].startswith('UK')]
ccmap={'BE':'BE','BG':'BG','CZ':'CZ','DE':'DE','EE':'EE','ES':'ES','FR':'FR','HR':'HR','IT':'IT','LV':'LV','LT':'LT','HU':'HU','MT':'MT','NL':'NL','PL':'PL','PT':'PT','RO':'RO','SI':'SI','SK':'SK','FI':'FI','SE':'SE','NO':'NO','CH':'CH'}
def norm(s):
 s=re.sub(r'\s*\(greater city\)','',s,flags=re.I).replace('/',' ')
 s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()
 return re.sub(r'[^a-z0-9]+','',s)
alias={'bruxellesbrussel':'brussels','antwerpen':'antwerp','praha':'prague','munchen':'munich','koln':'cologne','frankfurtammain':'frankfurt','nurnberg':'nuremberg','hannover':'hanover','sevilla':'seville','palmasdegrancanarialas':'laspalmasdegrancanaria','pamplonairuna':'pamplona','alicantealacant':'alicante','sansebastiandonostia':'sansebastian','roma':'rome','milano':'milan','napoli':'naples','torino':'turin','genova':'genoa','firenze':'florence','riga':'riga','sgravenhage':'thehague','warszawa':'warsaw','bucuresti':'bucharest','iasi':'iasi','helsinkihelsingfors':'helsinki','tampere tammerfors':'tampere','espooesbo':'espoo','goteborg':'gothenburg','zurich':'zurich'}
def key(s):
 n=norm(s);return alias.get(n,n)
# geonames populated places, choose same country exact normalized first
G=[]
for x in csv.reader(open('/tmp/cities500.txt'),delimiter='\t'):
 if len(x)<15 or x[6]!='P':continue
 G.append(dict(name=x[1],ascii=x[2],alts=x[3].split(','),lat=float(x[4]),lon=float(x[5]),cc=x[8],pop=int(x[14] or 0),feature=x[7]))
# existing names map
existing={key(v['name']):cid for cid,v in CITIES_EU.items()}
# geofabrik polygons, Europe URLs only
F=[]
for f in json.load(open('/tmp/geofabrik.json'))['features']:
 p=f['properties'];u=p.get('urls',{}).get('pbf','')
 if 'download.geofabrik.de/europe/' not in u:continue
 try:geom=shape(f['geometry'])
 except:continue
 F.append((geom.area,p['id'],u,geom))
def geo_region(lat,lon):
 hits=[x for x in F if x[3].contains(Point(lon,lat))]
 if not hits:return None
 x=min(hits,key=lambda z:z[0]); return x[2].split('/europe/',1)[1].rsplit('-latest.osm.pbf',1)[0]
rows=[]
for r in T:
 cc=ccmap[r['code'][:2]]; q=key(r['name']); cid=existing.get(q)
 cand=[]
 for g in G:
  if g['cc']!=cc:continue
  names=[g['name'],g['ascii']]+g['alts']
  score=max(SequenceMatcher(None,q,key(n)).ratio() for n in names if n)
  if key(g['name'])==q or key(g['ascii'])==q or any(key(n)==q for n in g['alts']): score=1
  # prefer real city over borough and plausible population
  score += min(0.08, math.log10(max(1,g['pop']))/100)
  if g['feature']=='PPLC':score+=.02
  if g['feature']=='PPLX':score-=.12
  cand.append((score,g))
 score,g=max(cand,key=lambda x:x[0])
 rows.append({**r,'cc':cc,'key':q,'existing':cid,'match':g['name'],'score':round(score,3),'lat':g['lat'],'lon':g['lon'],'gpop':g['pop'],'feature':g['feature'],'geofabrik':geo_region(g['lat'],g['lon'])})
json.dump(rows,open('work/target_mapped.json','w'),ensure_ascii=False,indent=2)
print('targets',len(rows),'existing',sum(bool(x['existing']) for x in rows),'new',sum(not x['existing'] for x in rows))
for x in rows:
 if not x['existing']: print(x['code'],x['name'],'=>',x['match'],x['score'],x['lat'],x['lon'],x['geofabrik'])
