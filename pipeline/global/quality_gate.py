#!/usr/bin/env python3
"""A geography ships only with reliable census joins and enough OSM street depth."""
import json,sys
p=json.load(open(sys.argv[1])); census=json.load(open(sys.argv[2]))
segments=int(p['segments']); observed=int(p['observed_units']); joined=float(p['census_join_rate'])
errors=[]
if segments<100: errors.append(f'only {segments} segments (<100)')
if observed<500: errors.append(f'only {observed} observed commercial/transit objects (<500)')
if joined<.90: errors.append(f'official census join {joined:.1%} (<90%)')
if not census: errors.append('official small-area census dataset empty')
if errors: print('EXCLUDED:',*errors,sep='\n- ');sys.exit(1)
print('PASS:',segments,'segments,',observed,'observed objects,',f'{joined:.1%} census join')
