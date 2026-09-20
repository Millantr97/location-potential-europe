#!/usr/bin/env python3
"""Apply one canonical base to all generated/static V2 output and link city logos home.
Usage: python3 pipeline/tools/apply_site_config.py [https://locationpotential.com/]
The default keeps the GitHub Pages preview. The production cutover is one command.
"""
import pathlib,re,sys,html
ROOT=pathlib.Path(__file__).resolve().parents[2]
PREVIEW='https://millantr97.github.io/location-potential-europe/'
base=(sys.argv[1] if len(sys.argv)>1 else PREVIEW).rstrip('/')+'/'
old_bases=(PREVIEW,'https://locationpotential.com/')
changed=0
for p in list(ROOT.rglob('*.html'))+list(ROOT.rglob('*.js')):
 if '.git' in p.parts or 'pipeline' in p.parts or p.name=='site-config.js':continue
 s=p.read_text(errors='ignore');o=s
 for old in old_bases:s=s.replace(old,base)
 if p.name=='index.html' and p.parent!=ROOT:
  depth=len(p.parent.relative_to(ROOT).parts); home='../'*depth
  s=re.sub(r'<div class="brand">(Location\s*<span>Potential</span>.*?</div>)',rf'<a class="brand" href="{home}" aria-label="Location Potential home">\1</a>',s,count=1,flags=re.S)
  # Existing brand links should always resolve to the V2 hub by a relative path.
  s=re.sub(r'<a class="brand" href="[^"]*">',f'<a class="brand" href="{home}" aria-label="Location Potential home">',s,count=1)
 if s!=o:p.write_text(s);changed+=1
# XML/text outputs
for name in ('sitemap.xml','robots.txt'):
 p=ROOT/name
 if p.exists():
  s=p.read_text();o=s
  for old in old_bases:s=s.replace(old,base)
  if s!=o:p.write_text(s);changed+=1
# runtime city config is generated but also used for share links
for p in ROOT.glob('*/city.js'):
 s=p.read_text();o=s
 s=re.sub(r'site:"[^"]+"',f'site:"{base}"',s,count=1);s=re.sub(r'siteHost:"[^"]+"',f'siteHost:"{base.removeprefix("https://").rstrip("/")}"',s,count=1)
 if s!=o:p.write_text(s);changed+=1
print('site base',base,'applied to',changed,'files')
