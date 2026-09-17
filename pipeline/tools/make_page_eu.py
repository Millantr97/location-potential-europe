"""Generate repo/<city>/index.html + repo/<city>/city.js for an EU city. Run after emit_eu.py."""
import json, re, sys, os
sys.path.insert(0,'/home/sandbox/europe/work')
from cities_eu import CITIES_EU
from transit_eu import TRANSIT
cid=sys.argv[1]; C=CITIES_EU[cid]
ROOT='/home/sandbox/europe/repo'
TPL='/home/sandbox/london-location-lens/index.html'
SITE='https://millantr97.github.io/location-potential-europe/'
segs=json.load(open(f'{ROOT}/pipeline/eu/{cid}/segments_full2.json'))
nseg=len(segs); narea=len([s for s in segs if s.get('lvl')!='street']); nstreet=nseg-narea
t=TRANSIT.get(cid)
if t and t[3]=='wiki': flowsrc=f"{C['name']} urban rail annual ridership (published system total); stop-level split MODELLED"
elif t: flowsrc=f"{C['name']} urban rail annual ridership (modelled system total); stop-level split MODELLED"
else: flowsrc="no urban rail system - all flow MODELLED from commercial density"
movement=(f"<p>Typical-day station entries and exits by day type (Mon / Tue-Thu / Fri / Sat / Sun) and annual totals are MODELLED for {C['name']}: "
 f"the city's published annual urban-rail ridership is divided across the station locations recorded in OpenStreetMap and scaled by each catchment's recorded commercial density, "
 f"then split across the week on a standard rail-week profile. No stop-level counts are published on a comparable open basis here, so every flow figure on this page is MODELLED - a demand anchor, not a count taken on that pavement. "
 f"Stations within 900 m from OpenStreetMap. Street-level pitches inherit their parent catchment's flow scaled to the street's share of recorded commercial units; streets beyond 900 m of any station show no flow at all and say so.</p>")
voa_method=("<p>Typical retail and office rents per m² for "+C['name']+" are MODELLED at city level: anchored to Cushman & Wakefield 'Main Streets Across the World 2025' prime-street rents, scaled down to typical trading streets, cross-checked against local market reports, and shown in local currency. No comparable per-property valuation roll is published across Europe. Always get agent quotes.</p>")
city_js=f"""window.CITY={{id:"{cid}",name:"{C['name']}",region:"{C['region']}",mapCenter:[{C['center'][0]},{C['center'][1]}],mapZoom:12,
cur:"{C['cur']}",cc:"{C['cc']}",country_name:"{C['country_name']}",eu:1,
site:"{SITE}",siteHost:"millantr97.github.io/location-potential-europe",
texts:{{
 flowCredit:"{flowsrc}",
 police:"",
 voaYear:"modelled 2026",
 voaMethod:`{voa_method}`,
 crimeNote:"",
 crimeMethod:"",
 crimeDropped:"No comparable open street-level crime feed is published for {C['country_name']}, so this site does not estimate business crime here.",
 movement:`{movement}`,
 resNote:"A 1 km census grid cell describes residents, not the people walking this street.",
 resMethod:`<p>Census 2021 statistics from the Eurostat 1 km population grid for the cell containing the segment anchor: total residents, broad age bands, employed residents and country-of-birth groups (born in {C['country_name']} / another EU country / outside the EU). The grid does not report employment for France and Germany; there the employment share is a city-level MODELLED figure. The student share is a city-level MODELLED estimate.</p>`,
 resResolution:"Resolution: 1 km census grid cell (Eurostat Census 2021).",
 resCensus:"Census 2021 (1 km grid)",
 resRmini:"A 1 km census grid cell describes residents, not the people walking this street. Census 2021, Eurostat grid.",
 bornAbroad:"Born abroad",
 ageYoung:"Working age (15-64)",
 ageUnder:"Under 15",
 studentsLbl:"Students (city-level est.)",
 profLbl:"Employed residents (share)",
 rentRule:"Rule: city-level typical rent x segment-type factor x footfall factor. City-level MODELLED figure in local currency - always get agent quotes before committing.",
 rentMethod:`<p>The estimated passing rent per m² is MODELLED: a city-level typical high-street rent for {C['name']} (anchored to Cushman &amp; Wakefield 'Main Streets Across the World 2025' prime-street rents, scaled to typical trading streets) x a segment-type factor (prime/managed retail 1.35-1.45, high street 1.15, side street 0.95, market 1.0) x a footfall factor (up to +30% for the busiest flows). No comparable per-property valuation roll is published across Europe, so this stays a city-level estimate in local currency. Always get agent quotes.</p>`,
 coverage:(SEGS,UNITS)=>`<p>${{SEGS.length.toLocaleString("en-GB")}} segments covering {C['region']} at street level: ${{SEGS.filter(s=>s.lvl!=="street").length}} area pitches (curated commercial areas plus urban rail station catchments - flow MODELLED from published system ridership, no minimum flow) and ${{SEGS.filter(s=>s.lvl==="street").length.toLocaleString("en-GB")}} street pitches - every named retail street and parade with 8 or more recorded commercial units, long streets split into roughly 400 m stretches. ${{UNITS.length.toLocaleString("en-GB")}} individual commercial units recorded across them from OpenStreetMap. A street pitch inside a station catchment carries that catchment's flow MODELLED down to the street's share of recorded units; a street more than 900 m from any station has no flow anchor and says so on its panel.</p>`,
}}}};"""
open(f'{ROOT}/{cid}/city.js','w',encoding='utf-8').write(city_js)
# ---- stub trends.js until fetch_trends_eu.py runs ----
tdir=f'{ROOT}/{cid}/data'; os.makedirs(tdir,exist_ok=True)
if not os.path.exists(f'{tdir}/trends.js'):
    open(f'{tdir}/trends.js','w').write('const TRENDS=null;\n')
# ---- page ----
s=open(TPL,encoding='utf-8').read()
s=s.replace('<title>London Location Potential - Street-level revenue and site selection for London</title>',
            f'<title>{C["name"]} Location Potential - Street-level revenue and site selection for {C["name"]}</title>')
s=s.replace('<meta name="description" content="Compare London street segments and individual commercial units for your exact business concept: real station flows, competition, residents, crime, rents and estimated monthly revenue.">',
            f'<meta name="description" content="Compare {C["name"]} street segments and individual commercial units for your exact business concept: modelled station flows, competition, residents, rents and estimated monthly revenue.">')
s=re.sub(r'<link rel="canonical" href="[^"]*">',f'<link rel="canonical" href="{SITE}{cid}/">',s,count=1)
s=s.replace('<meta property="og:title" content="Location Potential - London: where should your business open?">',
            f'<meta property="og:title" content="Location Potential - {C["name"]}: where should your business open?">')
s=s.replace('<meta property="og:url" content="https://locationpotential.com/">',f'<meta property="og:url" content="{SITE}{cid}/">')
s=s.replace('London <span>Location Potential</span>',f'{C["name"]} <span>Location Potential</span>')
s=s.replace('Street-level site selection · all of London',f'Street-level site selection · all of {C["region"]}')
s=re.sub(r'<span id="seg-count">[\d,]+</span> London street segments',f'<span id="seg-count">{nseg:,}</span> {C["name"]} street segments',s)
s=s.replace('<h2>London, ranked by the model</h2>',f'<h2>{C["name"]}, ranked by the model</h2>')
s=re.sub(r'<div class="article-grid" id="article-grid">.*?</div>\s*<div class="trend-note">',
         f'<div class="article-grid" id="article-grid"></div>\n  <p style="color:var(--muted);font-size:13px;margin:4px 0 14px">City-specific rankings for {C["name"]} are being prepared - <a href="../#rankings">the hub rankings</a> show the format.</p>\n  <div class="trend-note">',s,flags=re.S)
s=s.replace('residents, rents and crime are AREA CONTEXT','residents and rents are AREA CONTEXT')
s=re.sub(r'Each ranking is one fixed concept run through the published model over [\d,]+ London street segments\.',
         f'Each ranking is one fixed concept run through the published model over {nseg:,} {C["name"]} street segments.',s)
s=s.replace('<div>London Location Potential ·',f'<div>{C["name"]} Location Potential ·')
s=s.replace('href="privacy.html"','href="../privacy.html"')
s=s.replace('value="London Location Potential expert brief"',f'value="{C["name"]} Location Potential expert brief"')
s=s.replace('<link rel="manifest" href="/manifest.webmanifest">','<link rel="manifest" href="../manifest.webmanifest">')
s=s.replace('<link rel="apple-touch-icon" sizes="180x180" href="/assets/icons/apple-touch-icon.png">','<link rel="apple-touch-icon" sizes="180x180" href="../assets/icons/apple-touch-icon.png">')
s=re.sub(r'<script data-goatcounter="[^"]*" async src="//gc\.zgo\.at/count\.js"></script>\s*','',s)
s=s.replace('<script src="/pwa.js?v=1"></script>','<script src="../pwa.js?v=1"></script>')
s=re.sub(r'<script src="cities\.js\?v=\d+"></script>\s*<script src="segments\.js\?v=\d+"></script>\s*<script src="units\.js\?v=\d+"></script>\s*<script src="competitors\.js\?v=\d+"></script>\s*<script src="app\.js\?v=\d+"></script>\s*<script src="report\.js\?v=\d+"></script>\s*<script src="trends\.js\?v=\d+"></script>',
 '<script src="../cities.js?v=5"></script>\n<script src="city.js?v=1"></script>\n<script src="data/segments.js?v=1"></script>\n<script src="data/units.js?v=1"></script>\n<script src="data/competitors.js?v=1"></script>\n<script src="../app.js?v=32"></script>\n<script src="../report.js?v=20"></script>\n<script src="data/trends.js?v=1"></script>',s)
s=s.replace('<script src="extras.js?v=20"></script>','<script src="../extras.js?v=20"></script>')
s=s.replace('<script src="tabs.js?v=22"></script>','<script src="../tabs.js?v=22"></script>')
s=s.replace('<script src="leads.js?v=20"></script>','<script src="../leads.js?v=20"></script>')
s=s.replace('href="styles.css?v=23"','href="../styles.css?v=23"')
open(f'{ROOT}/{cid}/index.html','w',encoding='utf-8').write(s)
expected_canonical=f'<link rel="canonical" href="{SITE}{cid}/">'
assert s.count(expected_canonical)==1, f'{cid}: homepage canonical is not uniquely self-referencing'
print(cid,'page written:',nseg,'segments (',narea,'areas +',nstreet,'streets )')
