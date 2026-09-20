#!/usr/bin/env python3
"""Build-time coherence checks for published numbers, internal links and locale metadata."""
from pathlib import Path
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup
import json,re,statistics,sys
ROOT=Path(__file__).resolve().parents[1]
BASE='https://millantr97.github.io/location-potential-europe/'
issues=[]
def const(path,name):
 t=(ROOT/path).read_text();m=re.search(rf'const {name}=(\[.*?\]);',t,re.S)
 if not m: raise ValueError(f'{name} missing in {path}')
 return json.loads(m.group(1))
cost={x['id']:x for x in const(Path('cost-calculator/cost-data.js'),'COST_CITIES')}
if len(cost)!=136: issues.append(f'cost calculator has {len(cost)} cities, expected 136')
if sum(x['n'] for x in cost.values())!=56147: issues.append(f"segment total is {sum(x['n'] for x in cost.values()):,}, expected 56,147")
for slug in cost:
 p=Path(slug)/'data/segments.js'
 if not (ROOT/p).exists(): issues.append(f'{slug}: missing {p}');continue
 seg=const(p,'SEGMENTS');r=[x['rent']['est_rent_m2'] for x in seg if x.get('rent') and x['rent'].get('est_rent_m2') is not None]
 if len(seg)!=cost[slug]['n']: issues.append(f'{slug}: {len(seg)} segments but calculator says {cost[slug]["n"]}')
 if r:
  r=sorted(r); got=[round(r[int((len(r)-1)*q)]) for q in (.25,.5,.75)]
  if got!=cost[slug]['rent']: issues.append(f'{slug}: rent p25/median/p75 {got}, calculator has {cost[slug]["rent"]}')
# Versus copy is static, so verify the named lower displayed rent matches the refreshed row.
for page in (ROOT/'versus').glob('*/index.html'):
 s=BeautifulSoup(page.read_text(errors='ignore'),'html.parser'); table=s.find('table')
 if not table: continue
 rows=table.find_all('tr'); names=[x.get_text(strip=True) for x in rows[0].find_all(['th','td'])][1:3]
 rentrow=next((r for r in rows if r.get_text(' ',strip=True).startswith('Median modelled rent')),None)
 if not rentrow or len(names)!=2: continue
 cells=[x.get_text(' ',strip=True) for x in rentrow.find_all(['th','td'])][1:3]
 vals=[float(re.sub(r'[^0-9.]','',x)) for x in cells]; lower=names[0] if vals[0]<vals[1] else names[1]
 narrative=next((x.get_text(' ',strip=True) for x in s.find_all('p') if 'shows the lower median modelled rent' in x.get_text()),'')
 if f'{lower} shows the lower median modelled rent' not in narrative: issues.append(f'{page.relative_to(ROOT)}: lower-rent narrative disagrees with row')
html=list(ROOT.rglob('*.html'));broken=[];hreflang=[]
sm=BeautifulSoup((ROOT/'sitemap.xml').read_text(),'xml');urls=[x.text for x in sm.find_all('loc')]
published=set()
for v in urls:
 if v.startswith(BASE):
  u=urlparse(v); rel=unquote(u.path.split('/location-potential-europe/',1)[-1]); target=ROOT/rel
  if u.path.endswith('/'): target/='index.html'
  published.add(target.resolve())
for page in html:
 if page.resolve() not in published: continue
 s=BeautifulSoup(page.read_text(errors='ignore'),'html.parser')
 for tag,attr in [('a','href'),('script','src'),('link','href'),('img','src'),('source','src')]:
  for node in s.find_all(tag):
   v=node.get(attr)
   if not v or v.startswith(('#','mailto:','tel:','javascript:','data:','blob:','//')) or '{{' in v: continue
   u=urlparse(v)
   if u.scheme in ('http','https'):
    if not v.startswith(BASE): continue
    rel=unquote(u.path.split('/location-potential-europe/',1)[-1])
   elif u.scheme: continue
   elif u.path.startswith('/'): rel=unquote(u.path).lstrip('/')
   else: rel=str((page.parent/unquote(u.path)).resolve().relative_to(ROOT))
   target=ROOT/rel
   if u.path.endswith('/') or (not target.suffix and not target.exists()): target/= 'index.html'
   if not target.exists(): broken.append((page.relative_to(ROOT),v,target.relative_to(ROOT)))
 for node in s.find_all('link',hreflang=True):
  v=node.get('href','');u=urlparse(v)
  if v.startswith(BASE):
   target=ROOT/unquote(u.path.split('/location-potential-europe/',1)[-1])
   if u.path.endswith('/'): target/='index.html'
   if not target.exists(): hreflang.append((page.relative_to(ROOT),node.get('hreflang'),v))
if broken: issues.extend(f'{p}: dead internal reference {v} -> {t}' for p,v,t in broken)
if hreflang: issues.extend(f'{p}: dead hreflang {lang} -> {v}' for p,lang,v in hreflang)
if len(urls)!=len(set(urls)): issues.append(f'sitemap contains {len(urls)-len(set(urls))} duplicate URLs')
for v in urls:
 if not v.startswith(BASE): continue
 u=urlparse(v);target=ROOT/unquote(u.path.split('/location-potential-europe/',1)[-1])
 if u.path.endswith('/'):target/='index.html'
 if not target.exists():issues.append(f'sitemap URL has no file: {v}')
if issues:
 print('\n'.join('FAIL: '+x for x in issues));sys.exit(1)
print(f'coherence OK: {len(cost)} cities, 56,147 segments, {len(html):,} HTML files, {len(urls):,} sitemap URLs; internal links and hreflang targets resolve')
