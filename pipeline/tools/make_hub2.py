import os
SITE=os.environ.get("LP_SITE_BASE","https://millantr97.github.io/location-potential-europe/").rstrip("/")+"/"
"""Generate the scope-first hub index.html from cities.js data.
Run from repo root after make_frontend_data.py."""
import json, re, collections

s = open('cities.js', encoding='utf-8').read()
CITIES = json.loads(re.search(r'window\.CITIES=(\[.*\]);', s).group(1))[1:]
total_seg = sum(c['n'] for c in CITIES)

groups = collections.defaultdict(list)
for c in CITIES:
    groups[c['country']].append(c)

directory = []
for country in sorted(groups):
    cards = ''.join(
        f'<a class="city-card" href="{c["url"]}"><b>{c["name"]}</b><span>{c["n"]:,} segments</span></a>'
        for c in sorted(groups[country], key=lambda x: x['name']))
    directory.append(f'<div class="hub-country"><h3>{country}</h3><div class="city-grid">{cards}</div></div>')

html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Location Potential Europe - site selection across {len(CITIES)} cities</title><meta name="description" content="Compare {total_seg:,} street and area segments across {len(CITIES)} European cities. Choose your scope - all Europe, a macro-region, countries or single cities - pick a concept, and see the best zones. Observed competition, area context and modelled estimates are clearly labelled."><link rel="canonical" href="{SITE}"><meta property="og:title" content="Location Potential Europe - where should your business open?"><meta property="og:description" content="Pick your scope, pick your concept, see the best zones across {len(CITIES)} European cities."><meta property="og:url" content="{SITE}"><meta property="og:type" content="website"><meta property="og:image" content="{SITE}assets/og.png"><link rel="manifest" href="manifest.webmanifest"><link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="styles.css?v=37"></head><body><header class="top"><div class="top-row"><div class="brand">Location <span>Potential</span><i class="brand-city">Europe</i></div><nav class="citynav" id="citynav" aria-label="Choose a city"></nav></div></header><main class="hub-wrap"><section class="hero on"><div><div class="eyebrow">Street-level site selection · {len(CITIES)} cities across Europe</div><h1>Where should your business open?</h1><p>Choose where you could open, pick your concept, and compare <b>{total_seg:,} street and area segments</b>. Every figure is labelled observed, area context or modelled.</p><aside class="truth"><strong>Read the labels, not just the score</strong><p><b class="c-obs">OBSERVED</b> recorded at the street. <b class="c-ctx">AREA CONTEXT</b> nearby residents and demographics. <b class="c-mod">MODELLED</b> transparent estimates. Verify any shortlist locally before signing.</p></aside></div></section>
<section id="compare-app"><h2>Find the best zone in your scope</h2>
<div class="step-h" id="step-scope"><span class="step-n">1</span> Where could you open? <span class="step-hint">start broad, pick a featured city, or draw an area</span></div>
<div id="scope-chips" class="chip-row scope-primary" role="group" aria-label="Europe and macro-regions"></div>
<div class="featured-block"><div class="scope-label">Featured cities</div><div id="featured-cities" class="featured-cities" role="group" aria-label="Featured cities"></div><button id="other-cities-toggle" class="text-toggle" type="button" aria-expanded="false" aria-controls="other-cities-panel">Select other cities</button><div id="other-cities-panel" class="other-cities-panel" hidden><label><span class="sr-only">Search all cities</span><input id="scope-city-search" type="search" placeholder="Search 136 cities - e.g. Vienna, Málaga, Prague" autocomplete="off"></label><div id="scope-cities-results" class="city-hits"></div><details class="country-scope"><summary>Select countries</summary><div id="country-chips" class="chip-row" role="group" aria-label="Countries"></div></details></div><div id="scope-cities-picked" class="chip-row picked-cities" aria-live="polite"></div></div>
<div class="map-tools"><button id="draw-area" class="draw-area" type="button" aria-pressed="false">Draw an area</button><button id="clear-area" class="text-toggle" type="button" hidden>Clear area</button><span>Draw any shape around the part of Europe you want to compare.</span></div>
<div id="scope-map" class="scope-map"></div>
<div class="step-h"><span class="step-n">2</span> What are you opening? <span class="step-hint">68 concepts - the most compact up front, the rest behind "See more concepts"</span></div>
<div id="concept-chips" class="preset-row" role="group" aria-label="Concepts"></div>
<div class="step-h"><span class="step-n">3</span> Best zones in your scope</div>
<div id="compare-results" aria-live="polite"></div>
<div id="result-actions" class="result-actions" hidden><button id="share-results" class="action" type="button">Copy shareable result link</button><button id="pdf-results" class="action primary" type="button">Open one-page PDF report</button><span id="share-status" role="status" aria-live="polite"></span></div>
</section>
<section id="cities"><details class="all-city-directory"><summary>Browse all {len(CITIES)} cities</summary><div class="directory-inner">{''.join(directory)}</div></details></section>
<div class="freshness">Data updated 17 September 2026 · interface updated 19 September 2026</div>
<section id="method"><h2>How the numbers are built</h2><p>Venues, units and station locations come from OpenStreetMap (ODbL). Residents and demographics come from the Eurostat Census 2021 1 km grid (UK cities: Census 2021 LSOA). Comparable street-level crime is not shown. Station flow and rents are modelled and labelled. Cross-city rankings convert modelled local-currency revenue to EUR at ECB reference rates for comparability only. This is a shortlisting tool, not a valuation.</p></section></main><footer class="hub-wrap"><div>Location Potential · Europe · verify shortlists with on-street counts, agent enquiries and licensing checks.</div><a href="privacy.html">Privacy Notice</a></footer><script src="cities.js?v=9"></script><script src="assets/compare-index.js"></script><script src="assets/europe-land.js?v=1"></script><script src="compare.js?v=5"></script><script src="pwa.js?v=1"></script></body></html>'''
open('index.html','w',encoding='utf-8').write(html)
print('hub written:', len(html), 'bytes,', len(CITIES), 'cities,', total_seg, 'segments')
