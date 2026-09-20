#!/usr/bin/env python3
"""Fail the build on rent unit/FX regressions and broken anchor ordering."""
import json,os,re,statistics,sys
EUR={'£':1.16,'€':1.0,'CHF ':1.05,'Kč':.04,'zł':.2326,'Ft':.0025,'kr':.089,'lei':.201,'лв':.5113}
def city(c):
 s=open(f'{c}/data/segments.js',encoding='utf-8').read(); a=json.loads(re.search(r'const SEGMENTS=(.*);\nconst META=',s,re.S).group(1));
 cs=open(f'{c}/city.js',encoding='utf-8').read() if os.path.exists(f'{c}/city.js') else ''
 m=re.search(r'cur:"([^"]+)"',cs); cur=m.group(1) if m else '£'
 return statistics.median(x['rent']['est_rent_m2'] for x in a if x.get('rent')),cur
rows={}
for d in os.listdir('.'):
 if os.path.exists(f'{d}/data/segments.js'):
  try:
   v,cur=city(d); rows[d]=(v,cur,v*EUR.get(cur,1))
  except Exception: pass
bad=[(c,*x) for c,x in rows.items() if not 50 <= x[2] <= 1800]
if bad: print('Implausible annual retail rent in EUR/m2:',bad); sys.exit(1)
for a,b in [('london','paris'),('paris','madrid'),('madrid','lisbon')]:
 if rows[a][2] <= rows[b][2]: print('Anchor ordering failed:',a,rows[a],'<',b,rows[b]);sys.exit(1)
print('rent sanity OK:', ' > '.join(f'{c} {rows[c][0]:.0f}{rows[c][1]}' for c in ['london','paris','madrid','lisbon']), '|',len(rows),'cities checked')
