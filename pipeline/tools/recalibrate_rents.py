#!/usr/bin/env python3
"""Make modelled rent comparable across every published city.

The European builder stores each city's rent in local currency. Older UK pages
carried VOA rateable values instead, which are a tax-assessment proxy rather
than passing rent. Convert those nine cities to the same typical-city-rent
model. Also repair a September 2026 pipeline error where later non-EUR city
baselines, already expressed in local currency, were multiplied by FX again.
"""
import json, os, re, statistics

UK = {
 'london': (1050, 780), 'manchester': (380, 310), 'birmingham': (330, 290),
 'leeds': (290, 250), 'bristol': (320, 270), 'liverpool': (240, 210),
 'sheffield': (220, 195), 'glasgow': (250, 220), 'edinburgh': (300, 280),
}
# These September 17 additions were entered as local-currency baselines but the
# builder's legacy FX multiplication treated them as EUR baselines.
DOUBLE_FX = {
 'brno':25.0,'ostrava':25.0,'gdansk':4.3,'szczecin':4.3,'lublin':4.3,
 'bydgoszcz':4.3,'bialystok':4.3,'katowice':4.3,
 'iasi':4.98,'timisoara':4.98,'cluj-napoca':4.98,'constanta':4.98,
 'craiova':4.98,'brasov':4.98,'malmo':11.2,'trondheim':11.9,
}

def load(path):
 s=open(path,encoding='utf-8').read(); m=re.search(r'const SEGMENTS=(.*);\nconst META=(.*);\n?$',s,re.S)
 return json.loads(m.group(1)),json.loads(m.group(2))
def save(path,a,meta):
 open(path,'w',encoding='utf-8').write('const SEGMENTS='+json.dumps(a,separators=(',',':'),ensure_ascii=False)+';\nconst META='+json.dumps(meta,separators=(',',':'),ensure_ascii=False)+';\n')
def patch(city, retail, office, reason):
 p=f'{city}/data/segments.js'; a,meta=load(p)
 old=[]
 for s in a:
  r=s.get('rent') or {}; oldbase=float(r.get('retail_rv_m2') or 0)
  if oldbase<=0: continue
  factor=float(r.get('est_rent_m2') or oldbase)/oldbase
  old.append(r.get('est_rent_m2') or oldbase)
  r.update(retail_rv_m2=round(retail),office_rv_m2=round(office),est_rent_m2=round(retail*factor),basis='modelled')
 save(p,a,meta)
 med=statistics.median(s['rent']['est_rent_m2'] for s in a if s.get('rent'))
 print(city,reason,'old median',round(statistics.median(old)),'new median',round(med))
 return med

for city,(retail,office) in UK.items(): patch(city,retail,office,'VOA proxy -> comparable passing-rent model')
for city,fx in DOUBLE_FX.items():
 p=f'{city}/data/segments.js'; a,_=load(p); r=a[0]['rent']
 patch(city,r['retail_rv_m2']/fx,r['office_rv_m2']/fx,'removed duplicate FX multiplication')

# Keep derived products in step with city data.
p='cost-calculator/cost-data.js'; src=open(p,encoding='utf-8').read(); m=re.search(r'const COST_CITIES=(\[.*?\]);\nconst CONCEPT_SIZES=',src,re.S); costs=json.loads(m.group(1))
for c in costs:
 q=f"{c['id']}/data/segments.js"
 if not os.path.exists(q): continue
 a,_=load(q); vals=sorted(s['rent']['est_rent_m2'] for s in a if s.get('rent'))
 c['rent']=[round(vals[int((len(vals)-1)*p)]) for p in (.25,.5,.75)]
src=src[:m.start(1)]+json.dumps(costs,ensure_ascii=False)+src[m.end(1):];open(p,'w',encoding='utf-8').write(src)

# Versus pages are static and intentionally show local currency.
for root,ds,fs in os.walk('versus'):
 if 'index.html' not in fs or root=='versus': continue
 p=os.path.join(root,'index.html'); text=open(p,encoding='utf-8').read()
 links=re.findall(r'href="../../([^/]+)/">Open ',text)
 if len(links)<2: continue
 vals=[]
 for city in links[:2]:
  a,_=load(f'{city}/data/segments.js'); v=round(statistics.median(x['rent']['est_rent_m2'] for x in a if x.get('rent')))
  cur='£' if city in UK else re.search(r'cur:"([^\"]+)"',open(f'{city}/city.js',encoding='utf-8').read()).group(1)
  vals.append((v,cur))
 text=re.sub(r'(<tr><td>Median modelled rent \(per m2/year, local\)</td><td>).*?(</td><td>).*?(</td></tr>)',lambda m:m.group(1)+vals[0][1]+f'{vals[0][0]:,}'+m.group(2)+vals[1][1]+f'{vals[1][0]:,}'+m.group(3),text)
 open(p,'w',encoding='utf-8').write(text)
