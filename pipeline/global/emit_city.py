#!/usr/bin/env python3
import json,sys,collections,math,re,os,datetime
from cities import CITIES
cid,osmfile,censusfile=sys.argv[1:4];C=CITIES[cid];obs=json.load(open(osmfile));cells=json.load(open(censusfile));
def hav(a,b,c,d):
 R=6371000;p1,p2=math.radians(a),math.radians(c);dp=math.radians(c-a);dl=math.radians(d-b);return 2*R*math.asin(math.sqrt(math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2))
def slug(s):return re.sub('-+','-',re.sub('[^a-z0-9]+','-',s.lower())).strip('-')
def cat(t):
 a=t.get('amenity','');q=t.get('shop','');o=t.get('office','');l=t.get('leisure','')
 if a in ('cafe','restaurant','fast_food'):return a
 if a in ('pub','bar','nightclub'):return 'pub_bar'
 if a=='pharmacy':return 'pharmacy'
 if a=='veterinary':return 'vets'
 if o=='estate_agent':return 'agents'
 if o=='coworking':return 'cowork'
 if l=='fitness_centre':return 'fitness'
 if q in ('convenience','supermarket','greengrocer','bakery','butcher','deli','alcohol'):return 'grocery'
 if q:return 'shops'
 return None
def demo(la,lo):
 c=min(cells,key=lambda x:(x['lat']-la)**2+(x['lng']-lo)**2); p=max(1,c['residents']); foreign=c['foreign_born']/p;deg=c['degree_plus']/max(1,c['degree_den']);
 return {'code':c['geoid'],'name':'ACS 2024 5-year census tract','residents':p,'pct20_39':round(100*(p-c['under18'])/p,1),'pct_under20':round(100*c['under18']/p,1),'pct_students':8,'pct_prof':round(100*deg,1),'pct_nonuk':round(100*foreign,1),'diversity':round(2*foreign*(1-foreign),3),'top_eth':[['US-born',round(100*(1-foreign),1)],['Foreign-born',round(100*foreign,1)]]}
units=[];stations=[]
for x in obs:
 t=x['tags']; rw=t.get('railway');
 if (rw in ('station','halt') or t.get('station')=='subway') and t.get('name'):stations.append(x);continue
 c=cat(t)
 if c:units.append({'lat':x['lat'],'lng':x['lng'],'cat':c,'name':t.get('name',''),'street':t.get('addr:street',''),'cuisine':t.get('cuisine','')})
by=collections.defaultdict(list)
for u in units:
 if u['street']:by[u['street']].append(u)
clusters=[(n,u) for n,u in by.items() if len(u)>=8]
# local density lookups
G=collections.defaultdict(list)
for u in units:G[(round(u['lat'],3),round(u['lng'],3))].append(u)
def nearby(la,lo,rad=350):
 out=[]
 for x in range(-4,5):
  for y in range(-4,5):
   for u in G.get((round(la,3)+x*.001,round(lo,3)+y*.001),[]):
    if hav(la,lo,u['lat'],u['lng'])<=rad:out.append(u)
 return out
cats=['cafe','restaurant','fast_food','pub_bar','grocery','shops','fitness','cowork','services','agents','pharmacy','vets']
def build(i,name,la,lo,lvl,us):
 co={k:0 for k in cats}
 for u in us:co[u['cat']]=co.get(u['cat'],0)+1
 co.update(cafe_chain=0,restaurant_chain=0,fast_food_chain=0,grocery_chain=0,fitness_chain=0,terrace_share=0,culture=0,parks_600=0)
 annual=round(150000+len(us)*85000) if lvl=='area' else round(len(us)*45000)
 days={'mon':round(annual/365), 'mid':round(annual/350), 'fri':round(annual/330),'sat':round(annual/300),'sun':round(annual/500)}
 d=demo(la,lo); stype='transport_hub' if lvl=='area' else ('high_street' if len(us)>=40 else 'side_street');
 rm={'new-york':1450,'los-angeles':850,'chicago':600,'san-francisco':950,'boston':700,'washington-dc':650,'seattle':650,'miami':700,'sydney':1450,'melbourne':1050,'brisbane':750,'perth':700,'adelaide':600}.get(cid,700); office=round(rm*.62); est=round(rm*(1.18 if stype=='transport_hub' else 1.1 if stype=='high_street' else .92))
 return {'id':slug(name)+'-'+str(i),'name':name,'borough':C['name'],'zone':'city','lat':round(la,5),'lng':round(lo,5),'stype':stype,'lvl':lvl,'weak':False if lvl=='area' else True,'anchors':([{'station':name.replace(' station area',''),'mode':'MODELLED','annual':annual,'src':'modelled','days_modelled':True}] if lvl=='area' else []),'flow':{'annual_total':annual,'days':days,'modelled_from':name if lvl=='area' else None,'share':None,'weekend_share':.25,'weekend_ratio_norm':.5,'fri_sat_norm':.5,'day_rel':{'mon':.95,'mid':1,'fri':1.06,'sat':1.12,'sun':.68}},'transport':{'stations_900m':1 if lvl=='area' else 0,'names':[name.replace(' station area','')] if lvl=='area' else []},'osm':co,'lsoa':d,'crime':None,'crime_per1000':None,'rent':{'retail_rv_m2':rm,'office_rv_m2':office,'basis':'modelled','est_rent_m2':est},'model':{'spend_est':round(42+22*d['pct_prof']/100),'office_skew':round(.25+.5*d['pct_prof']/100,2),'rhythm':{'early':.12,'midday':.28,'afternoon':.23,'evening':.28,'late':.09}},'_units':us}
segs=[]
for i,x in enumerate(stations):segs.append(build(i,x['tags']['name']+' station area',x['lat'],x['lng'],'area',nearby(x['lat'],x['lng'],300)))
for i,(n,us) in enumerate(clusters,len(segs)):
 la=sorted(u['lat'] for u in us)[len(us)//2];lo=sorted(u['lng'] for u in us)[len(us)//2];segs.append(build(i,n+' (New York)',la,lo,'street',us))
# verify join distance < 3 km
joined=sum(1 for s in segs if min(hav(s['lat'],s['lng'],c['lat'],c['lng']) for c in cells)<3000);print('census join',joined,'/',len(segs))
UNITCATS=cats;un=[];comps={};seen=set()
for si,s in enumerate(segs):
 cc=collections.defaultdict(list)
 for u in s.pop('_units'):
  k=(u['lat'],u['lng'],u['cat']);
  if k not in seen:un.append([u['lat'],u['lng'],UNITCATS.index(u['cat']),0,si,0,u['name'][:60],u['street'][:48],u['cuisine'][:30]]);seen.add(k)
  if u['name']:cc[u['cat']].append([u['name'][:44],u['cuisine'][:26],0,0])
 if cc:comps[s['id']]={k:v[:12] for k,v in cc.items()}
out=f'{cid}/data';os.makedirs(out,exist_ok=True);today=datetime.date.today().strftime('%-d %b %Y');meta={'built':today,'osm_date':today,'crime_window':'','census':'ACS 2024 five-year census tract','numbat':'Station presence OBSERVED; stop-level flow MODELLED from local commercial density','sources':{}}
open(out+'/segments.js','w').write('const SEGMENTS='+json.dumps(segs,separators=(',',':'))+';\nconst META='+json.dumps(meta,separators=(',',':'))+';\n');open(out+'/units.js','w').write('const UNITCATS='+json.dumps(UNITCATS)+';\nconst UNITS='+json.dumps(un,separators=(',',':'))+';\n');open(out+'/competitors.js','w').write('const COMPETITORS='+json.dumps(comps,separators=(',',':'))+';\n');open(out+'/trends.js','w').write('const TRENDS=null;\n')
json.dump({'segments':len(segs),'observed_units':len(un),'census_join_rate':joined/len(segs)},open('/tmp/'+cid+'-quality.json','w'));print(cid,len(segs),'segments',len(un),'units')
