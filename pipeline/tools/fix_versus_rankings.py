#!/usr/bin/env python3
"""Fill any empty strongest-concepts table from the live scoring engine.
Uses a small Node VM runner because app.js is the canonical scoring/revenue code.
Fails if any city remains empty or a narrative winner lacks evidence."""
import subprocess,json,glob,re,os,sys,tempfile
NODE=r'''const fs=require('fs'),vm=require('vm');let seg=fs.readFileSync(process.argv[2]+'/data/segments.js','utf8').replace(/^const SEGMENTS=/,'globalThis.SEGMENTS=').replace(/\nconst META=/,'\nglobalThis.META=');let app=fs.readFileSync('app.js','utf8');app=app.slice(0,app.indexOf('/* ---------- concept UI ---------- */'));const ctx={console,window:{},document:{},Intl,Math};ctx.window.CITY=null;vm.createContext(ctx);vm.runInContext(seg+'\n'+app+'\nglobalThis.OUT=PRESETS.map(p=>{let r=computeAll(p)[0];return {name:p.name,fit:Math.round(r.score),rev:Math.round(r.rev.month),zone:r.seg.name}}).sort((a,b)=>b.rev-a.rev).slice(0,10)',ctx);console.log(JSON.stringify(ctx.OUT));'''
runner='/tmp/lp-rank-city.js';open(runner,'w').write(NODE)
FX={'london':1.16}
cache={}
def ranks(city):
 if city not in cache:cache[city]=json.loads(subprocess.check_output(['node',runner,city],text=True))
 return cache[city]
def rows(city,n=3):
 fx=FX.get(city,1);return ''.join(f'<tr><td>{i}</td><td>{x["name"]}</td><td>{x["fit"]}/100</td><td>€{round(x["rev"]*fx):,}/mo</td></tr>' for i,x in enumerate(ranks(city)[:n],1))
# Fill London top-concepts page fully.
p='london/rankings/top-concepts/index.html';s=open(p).read();s=re.sub(r'(<tbody>).*?(</tbody>)',lambda m:m.group(1)+''.join(f'<tr><td>{i}</td><td><b>{x["name"]}</b><br><span>{x["zone"]}</span></td><td>{x["fit"]}/100</td><td>€{round(x["rev"]*1.16):,}/mo</td></tr>' for i,x in enumerate(ranks('london'),1))+m.group(2),s,count=1,flags=re.S);open(p,'w').write(s)
# Repair every empty side and recompute evidence-based winner narrative.
for p in glob.glob('versus/*/index.html'):
 s=open(p).read();links=re.findall(r'href="../../([^/]+)/">Open ',s)
 if len(links)!=2:continue
 names=re.findall(r'<h2>Strongest concepts in ([^<]+)</h2>',s)
 for name,city in zip(names,links):
  pat=rf'(<h2>Strongest concepts in {re.escape(name)}</h2>\s*<table.*?<tbody>)(.*?)(</tbody>)'
  s=re.sub(pat,lambda m:m.group(1)+(rows(city) if not m.group(2).strip() else m.group(2))+m.group(3),s,count=1,flags=re.S)
 # derive winner from the maximum displayed comparable revenue on each side
 scores=[]
 for name in names:
  m=re.search(rf'<h2>Strongest concepts in {re.escape(name)}</h2>\s*<table.*?<tbody>(.*?)</tbody>',s,re.S); nums=[int(x.replace(',','')) for x in re.findall(r'€([\d,]+)/mo',m.group(1))];scores.append(max(nums))
 winner=names[0] if scores[0]>=scores[1] else names[1]
 s=re.sub(r'On the model\'s strongest-concept revenue comparison, <b>[^<]+</b> currently leads\.',f"On the model's strongest-concept revenue comparison, <b>{winner}</b> currently leads.",s)
 open(p,'w').write(s)
# guard all tables
bad=[]
for p in glob.glob('versus/*/index.html')+[ 'london/rankings/top-concepts/index.html']:
 if re.search(r'<tbody>\s*</tbody>',open(p).read()):bad.append(p)
if bad:raise SystemExit('empty ranking tables: '+','.join(bad))
print('repaired',len(cache),'city ranking sets; all versus tables populated')
