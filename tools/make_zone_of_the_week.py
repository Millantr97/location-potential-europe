#!/usr/bin/env python3
"""Generate zone-of-the-week/index.html from the site's own published data.

Picks the featured city by ISO week rotation, takes its #1 concept and leading
zone from the published top-concepts ranking, enriches with the zone's segment
record (observed residents, modelled rent and day flow), and writes the page.
Run weekly:  python3 tools/make_zone_of_the_week.py
Archives the previous issue to zone-of-the-week/archive/<ISO-year>-W<week>.html.
"""
import json,re,os,html,datetime,statistics
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE='https://millantr97.github.io/location-potential-europe'
FEAT=['london','madrid','paris','rome','berlin','barcelona','vienna','amsterdam','lisbon']
def load_json_js(path,const):
    s=open(path).read().strip()
    return json.loads(s[s.index('['):s.rindex(']')+1])
def main():
    today=datetime.date.today()
    y,week,wd=today.isocalendar()
    monday=today-datetime.timedelta(days=wd-1)
    sunday=monday+datetime.timedelta(days=6)
    city=FEAT[week%len(FEAT)]
    t=open(os.path.join(ROOT,city,'rankings','top-concepts','index.html')).read()
    rows=re.findall(r'<td>\d+</td><td><a href="([^"]*)"><b>(.*?)</b></a><small>(.*?)</small></td><td>(\d+)/100</td><td>(.*?)</td>',t)
    link,concept,zone,fit,eur=rows[0]
    concept=html.unescape(concept)
    segs=load_json_js(os.path.join(ROOT,city,'data','segments.js'),'SEGMENTS')
    seg=next((x for x in segs if x['name']==zone),None)
    cities=json.loads(re.search(r'window\.CITIES=(\[.*?\]);',open(os.path.join(ROOT,'cities.js')).read(),re.S).group(1))
    cur=next(c['cur'] for c in cities[1:] if c['url'].rstrip('/')==city)
    cname=next(c['name'] for c in cities[1:] if c['url'].rstrip('/')==city)
    # archive previous issue
    outdir=os.path.join(ROOT,'zone-of-the-week')
    os.makedirs(os.path.join(outdir,'archive'),exist_ok=True)
    idx=os.path.join(outdir,'index.html')
    if os.path.exists(idx):
        m=re.search(r'archive of week (\d{4}-W\d{2})',open(idx).read())
        tag=m.group(1) if m else 'previous'
        os.replace(idx,os.path.join(outdir,'archive','%s.html'%tag))
    days=seg['flow']['days'] if seg else {}
    maxd=max(days.values()) if days else 1
    bars=''.join('<rect x="%d" y="%d" width="52" height="%d" rx="4" fill="#16382c"/><text x="%d" y="176" font-size="13" text-anchor="middle" fill="#5c6b62">%s</text><text x="%d" y="%d" font-size="12" text-anchor="middle" fill="#5c6b62">%s</text>'
        %(70+i*90, 150-int(130*v/maxd), int(130*v/maxd), 96+i*90, lab, 96+i*90, 144-int(130*v/maxd), format(int(v),','))
        for i,(lab,v) in enumerate([('Mon',days.get('mon',0)),('Tue-Thu',days.get('mid',0)),('Fri',days.get('fri',0)),('Sat',days.get('sat',0)),('Sun',days.get('sun',0))]))
    chart='<svg viewBox="0 0 520 190" style="max-width:560px;width:100%%" role="img" aria-label="Modelled daily footfall for %s">%s</svg>'%(zone,bars)
    residents = seg['lsoa']['residents'] if seg and seg.get('lsoa') else None
    rent = seg['rent']['est_rent_m2'] if seg and seg.get('rent') else None
    facts=''
    if residents: facts+='<tr><td>Residents in the surrounding grid cell</td><td>%s</td><td><b class="c-obs">OBSERVED</b> · Census 2021 1 km grid</td></tr>'%format(int(residents),',')
    if rent: facts+='<tr><td>Modelled rent</td><td>%s%s per m2/year</td><td><b class="c-mod">MODELLED</b></td></tr>'%(cur,format(rent,','))
    if days: facts+='<tr><td>Peak day (modelled flow)</td><td>%s visits/day</td><td><b class="c-mod">MODELLED</b></td></tr>'%format(int(maxd),',')
    concept_slug=re.search(r'concept=([a-z0-9-]+)',link)
    clink='%s/?concept=%s'%(city,concept_slug.group(1)) if concept_slug else city+'/'
    page='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Zone of the week: %s, %s - Location Potential Europe</title>
<meta name="description" content="This week's zone: %s in %s, the strongest modelled zone for %s. Observed residents, modelled rent and day flow, honestly labelled.">
<link rel="canonical" href="%s/zone-of-the-week/">
<link rel="manifest" href="../manifest.webmanifest"><link rel="icon" href="../assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="../styles.css?v=38"></head><body>
<header class="top"><div class="top-row"><a class="brand" href="../">Location <span>Potential</span><i class="brand-city">Europe</i></a></div></header>
<main class="docs">
<div class="eyebrow">Zone of the week · week of %s - %s %d · auto-generated from published data</div>
<h1>%s, %s</h1>
<p>The strongest modelled zone in %s this week: <b>%s</b> for <b>%s</b>, fit %s/100, EUR comparison %s. <!-- archive of week %d-W%02d --></p>
<table class="api-table"><thead><tr><th>Fact</th><th>Value</th><th>Label</th></tr></thead><tbody>
<tr><td>Leading concept</td><td>%s</td><td><b class="c-mod">MODELLED</b> fit %s/100</td></tr>
<tr><td>EUR revenue comparison</td><td>%s</td><td><b class="c-mod">MODELLED</b> monthly, EUR for comparison only</td></tr>
%s
</tbody></table>
<h2>Modelled flow by day</h2>
%s
<h2>Open it in the tool</h2>
<p><a class="action primary" href="../%s">See %s with the %s concept &rarr;</a></p>
<p class="honesty">This page is generated by tools/make_zone_of_the_week.py from the published dataset - the same model and labels as the city pages. It is a shortlist signal, not a valuation or proof of premises availability. Past issues live in the <a href="archive/">archive</a>.</p>
</main>
<footer class="foot hub-wrap"><div>Location Potential · Europe · verify shortlists with on-street counts, agent enquiries and licensing checks.</div>
<div class="foot-links"><a href="../">Home</a><a href="../report/">Market entry report</a><a href="../privacy.html">Privacy Notice</a></div></footer>
<div class="freshness">Generated %s from data updated 17 September 2026</div>
<script src="../pwa.js?v=2"></script></body></html>'''%(
      zone,cname,zone,cname,concept.lower(),SITE,
      monday.strftime('%-d %B'),sunday.strftime('%-d %B'),sunday.year,
      zone,cname,cname,zone,concept.lower(),fit,eur,y,week,
      concept,fit,eur,facts,chart,clink,zone,concept.lower(),today.isoformat())
    open(idx,'w').write(page)
    print('zone of the week:',city,zone,concept)
if __name__=='__main__': main()
