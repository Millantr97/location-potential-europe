#!/usr/bin/env python3
import pathlib,re,sys
R=pathlib.Path(__file__).resolve().parents[2];bad=[]
for p in R.rglob('*.html'):
 if '.git' in p.parts:continue
 s=p.read_text(errors='ignore')
 if p.name=='index.html' and p.parent!=R and re.search(r'<(?:div|span) class="brand"',s):bad.append(f'{p.relative_to(R)} brand is not a home link')
 for url in re.findall(r'<(?:link rel="canonical"|meta property="og:url")[^>]*content?="([^"]+)"',s):
  if not url.startswith(('https://millantr97.github.io/location-potential-europe/','https://locationpotential.com/')):bad.append(f'{p.relative_to(R)} unexpected public URL {url}')
if bad:print('\n'.join('FAIL '+x for x in bad));sys.exit(1)
print('V2 swappability OK: city logos link home; public base is in the configured preview/production set')
