"""Remove UK-specific references from non-UK city pages (run from repo root).

Context: city pages were bootstrapped from the London template, so non-UK pages
inherited UK-only source mentions. This script is the rerunnable fix; the shared
runtime guards live in app.js / report.js (CITY.eu branches).

Fixes applied 2026-09-19:
1. trends honest-labels note in <city>/index.html said "(United Kingdom, yearly mean)"
   for every city; replaced with the city's own country from city.js country_name.
2. app.js Method tab linked nomisweb (UK census) and gov.uk NDR (UK business
   floorspace) unconditionally; now EU cities link to Eurostat GISCO grid and the
   Cushman & Wakefield rent anchor instead.
3. app.js Revenue model text said "LSOA population" (UK geography unit); EU cities
   now read "census-grid resident population".
4. report.js ticket bar hardcoded a £ glyph; now uses the city currency.
"""
import re, os

UK_CITIES = {"london","manchester","birmingham","leeds","bristol","liverpool","sheffield","glasgow","edinburgh"}

def main():
    citydirs = sorted(d for d in os.listdir('.')
                      if os.path.isdir(d) and d not in UK_CITIES | {"assets","pipeline"}
                      and os.path.exists(os.path.join(d,'city.js')))
    fixed = 0
    for d in citydirs:
        src = open(os.path.join(d,'city.js'),encoding='utf-8').read()
        m = re.search(r'country_name:"([^"]+)"', src)
        if not m:
            print("WARN no country_name:", d); continue
        p = os.path.join(d,'index.html')
        s = open(p,encoding='utf-8').read()
        old = 'Google Trends interest for a matching keyword (United Kingdom, yearly mean)'
        if old in s:
            open(p,'w',encoding='utf-8').write(
                s.replace(old, f'Google Trends interest for a matching keyword ({m.group(1)}, yearly mean)'))
            fixed += 1
    print(f"trend-note country fixed in {fixed} pages")

if __name__ == '__main__':
    main()
