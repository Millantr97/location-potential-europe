import json,csv,re,unicodedata,math,sys
from difflib import SequenceMatcher
sys.path.insert(0,'work');from cities_eu import CITIES_EU
T=[r for r in json.load(open('work/eurostat250.json'))['cities'] if not r['code'].startswith('UK')]
def norm(s):
 s=re.sub(r'\s*\(greater city\)','',s,flags=re.I).replace('/',' ');s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower();return re.sub('[^a-z0-9]+','',s)
alias={'bruxellesbrussel':'brussels','antwerpen':'antwerp','praha':'prague','munchen':'munich','koln':'cologne','frankfurtammain':'frankfurt','nurnberg':'nuremberg','hannover':'hanover','sevilla':'seville','palmasdegrancanarialas':'laspalmasdegrancanaria','pamplonairuna':'pamplona','alicantealacant':'alicante','sansebastiandonostia':'sansebastian','roma':'rome','milano':'milan','napoli':'naples','torino':'turin','genova':'genoa','firenze':'florence','sgravenhage':'thehague','warszawa':'warsaw','bucuresti':'bucharest','helsinkihelsingfors':'helsinki','tampere tammerfors':'tampere','espooesbo':'espoo','goteborg':'gothenburg','lisboa':'lisbon','greatervalletta':'valletta'}
def key(s):n=norm(s);return alias.get(n,n)
G=[]
for x in csv.reader(open('/tmp/cities500.txt'),delimiter='\t'):
 if len(x)>14 and x[6]=='P':G.append(dict(name=x[1],ascii=x[2],alts=x[3].split(',')[:40],lat=float(x[4]),lon=float(x[5]),cc=x[8],pop=int(x[14] or 0),feature=x[7]))
existing={key(v['name']):cid for cid,v in CITIES_EU.items()}
# Treat already-shipped page slugs as established destinations even if older config source omitted them.
import os
for cid in os.listdir('repo'):
 if os.path.isfile(f'repo/{cid}/index.html'): existing.setdefault(key(cid.replace('-', ' ')),cid)
existing.update({'dortmund':'dortmund','essen':'essen','duisburg':'duisburg','dresden':'dresden','bremen':'bremen','hannover':'hanover','palermo':'palermo','genova':'genoa','wroclaw':'wroclaw','lodz':'lodz','poznan':'poznan','nurnberg':'nuremberg'})
DISPLAY={'Palmas de Gran Canaria, Las':'Las Palmas de Gran Canaria','Pamplona/Iruña':'Pamplona','Alicante/Alacant':'Alicante','San Sebastián/Donostia':'San Sebastián','Frankfurt am Main':'Frankfurt','Espoo/Esbo':'Espoo','Tampere/Tammerfors':'Tampere','Greater Valletta':'Valletta','Warszawa':'Warsaw'}
COUNTRY={'BE':('Belgium','€'),'BG':('Bulgaria','лв'),'CH':('Switzerland','CHF '),'CZ':('Czechia','Kč'),'DE':('Germany','€'),'EE':('Estonia','€'),'ES':('Spain','€'),'FI':('Finland','€'),'FR':('France','€'),'HR':('Croatia','€'),'IT':('Italy','€'),'LV':('Latvia','€'),'LT':('Lithuania','€'),'HU':('Hungary','Ft'),'MT':('Malta','€'),'NL':('Netherlands','€'),'NO':('Norway','kr'),'PL':('Poland','zł'),'PT':('Portugal','€'),'RO':('Romania','lei'),'SI':('Slovenia','€'),'SK':('Slovakia','€'),'SE':('Sweden','kr')}
# explicit smallest Geofabrik region from known point mapping. Canary is Africa path special.
REG={
'BE':'belgium','BG':'bulgaria','CH':'switzerland','EE':'estonia','FI':'finland','HR':'croatia','LT':'lithuania','LV':'latvia','HU':'hungary','MT':'malta','NO':'norway','PT':'portugal','RO':'romania','SE':'sweden','SI':'slovenia','SK':'slovakia'}
REGNAME={'brno':'czech-republic/jihomoravsky','ostrava':'czech-republic/moravskoslezky','bochum':'germany/nordrhein-westfalen','wuppertal':'germany/nordrhein-westfalen','bielefeld':'germany/nordrhein-westfalen','bonn':'germany/nordrhein-westfalen','munster':'germany/nordrhein-westfalen','gelsenkirchen':'germany/nordrhein-westfalen','monchengladbach':'germany/nordrhein-westfalen','aachen':'germany/nordrhein-westfalen','mannheim':'germany/baden-wuerttemberg','karlsruhe':'germany/baden-wuerttemberg','augsburg':'germany/bayern','wiesbaden':'germany/hessen','braunschweig':'germany/niedersachsen','kiel':'germany/schleswig-holstein','alicante':'spain/valencia','murcia':'spain/murcia','palma-de-mallorca':'spain/islas-baleares','sabadell':'spain/cataluna','las-palmas-de-gran-canaria':'africa/canary-islands','santa-cruz-de-tenerife':'africa/canary-islands','pamplona':'spain/navarra','granada':'spain/andalucia','cordoba':'spain/andalucia','valladolid':'spain/castilla-y-leon','a-coruna':'spain/galicia','vigo':'spain/galicia','gijon':'spain/asturias','vitoria-gasteiz':'spain/pais-vasco','san-sebastian':'spain/pais-vasco','montpellier':'france/languedoc-roussillon','grenoble':'france/rhone-alpes','rouen':'france/haute-normandie','rennes':'france/bretagne','catania':'italy/isole','bari':'italy/sud','verona':'italy/nord-est','bergamo':'italy/nord-ovest','eindhoven':'netherlands/noord-brabant','haarlem':'netherlands/noord-holland','leiden':'netherlands/zuid-holland','gdansk':'poland/pomorskie','szczecin':'poland/zachodniopomorskie','lublin':'poland/lubelskie','bydgoszcz':'poland/kujawsko-pomorskie','bialystok':'poland/podlaskie','katowice':'poland/slaskie'}
def slug(n):s=unicodedata.normalize('NFKD',n).encode('ascii','ignore').decode().lower();return re.sub('[^a-z0-9]+','-',s).strip('-')
rows=[]
for r in T:
 q=key(r['name']); cid=existing.get(q)
 if cid:continue
 cc=r['code'][:2];cand=[]
 for g in G:
  if g['cc']!=cc:continue
  score=max(SequenceMatcher(None,q,key(g[z])).ratio() for z in ('name','ascii'))
  if key(g['name'])==q or key(g['ascii'])==q or any(key(a)==q for a in g['alts']):score=1
  if g['feature']=='PPLX':score-=.15
  score+=min(.07,math.log10(max(1,g['pop']))/100)
  cand.append((score,g))
 score,g=max(cand,key=lambda x:x[0]);raw=re.sub(r'\s*\(greater city\)','',r['name']); name=DISPLAY.get(raw,raw);cid=slug(name).replace('biaystok','bialystok')
 country,cur=COUNTRY[cc];dlon=min(.30,.19/max(.45,math.cos(math.radians(g['lat']))));gf=REGNAME.get(cid,REG.get(cc));assert gf,(cid,cc)
 rows.append({**r,'cid':cid,'name':name,'cc':cc,'country_name':country,'cur':cur,'lat':g['lat'],'lon':g['lon'],'bbox':[round(g['lat']-.16,3),round(g['lon']-dlon,3),round(g['lat']+.16,3),round(g['lon']+dlon,3)],'geofabrik':gf,'match':g['name'],'score':round(score,3)})
print('new target configs',len(rows))
# Manual quality gate on matches
bad=[x for x in rows if x['score']<.6];assert not bad,bad
p='work/cities_eu.py';s=open(p).read();marker='}\n# Build order: most important markets first';assert marker in s
lines=[' # ---- 250k expansion: Eurostat urb_cpop1 latest available ----']
for x in rows:lines.append(" %r: dict(name=%r, region=%r, country=%r, country_name=%r, cc=%r, cur=%r, center=(%.5f,%.5f), bbox=(%.3f,%.3f,%.3f,%.3f), geofabrik=%r, population=%d, population_year=%d),"%(x['cid'],x['name'],'the '+x['name']+' urban area',x['cc'],x['country_name'],x['cc'],x['cur'],x['lat'],x['lon'],*x['bbox'],x['geofabrik'],x['population'],x['year']))
s=s.replace(marker,'\n'.join(lines)+'\n'+marker);open(p,'w').write(s)
json.dump(rows,open('work/new250.json','w'),ensure_ascii=False,indent=2)
print('added',len(rows));print('\n'.join(f"{x['cid']}\t{x['name']}\t{x['geofabrik']}\t{x['score']}" for x in rows))
