#!/usr/bin/env python3
"""Fail if any city homepage canonical does not self-reference its city URL."""
from pathlib import Path
import re, sys
BASE='https://millantr97.github.io/location-potential-europe/'
errors=[]; checked=0
for page in sorted(Path(__file__).resolve().parents[2].glob('*/index.html')):
    slug=page.parent.name
    text=page.read_text(encoding='utf-8',errors='replace')
    tags=re.findall(r'<link rel="canonical" href="([^"]+)">',text)
    if not tags: continue
    checked+=1
    expected=BASE+slug+'/'
    if tags != [expected]: errors.append(f'{page}: expected one {expected}, found {tags}')
if errors:
    print('\n'.join(errors),file=sys.stderr);sys.exit(1)
print(f'OK: {checked} homepages have one self-referencing canonical')
