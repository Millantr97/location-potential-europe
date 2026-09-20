"""Regenerate cities.js with coordinates, currency, region and segment counts,
so the picker and the hub can render a visual map and scope filtering.
Run from repo root. Region follows a UN-geoscheme-style grouping."""
import json, os, re, math

UK_ORDER = ["london","manchester","birmingham","leeds","bristol","liverpool","sheffield","glasgow","edinburgh"]
UK_NAMES = {"london":"London","manchester":"Manchester","birmingham":"Birmingham","leeds":"Leeds","bristol":"Bristol","liverpool":"Liverpool","sheffield":"Sheffield","glasgow":"Glasgow","edinburgh":"Edinburgh"}
REGION = {
 "United Kingdom":"Northern","Ireland":"Northern","Sweden":"Northern","Norway":"Northern","Finland":"Northern","Denmark":"Northern","Estonia":"Northern","Latvia":"Northern","Lithuania":"Northern",
 "France":"Western","Germany":"Western","The Netherlands":"Western","Belgium":"Western","Austria":"Western","Switzerland":"Western","Luxembourg":"Western",
 "Spain":"Southern","Portugal":"Southern","Italy":"Southern","Greece":"Southern","Croatia":"Southern","Slovenia":"Southern","Malta":"Southern",
 "United States":"Americas","Australia":"Oceania",
 "Poland":"Eastern","Czechia":"Eastern","Slovakia":"Eastern","Hungary":"Eastern","Romania":"Eastern","Bulgaria":"Eastern",
}
# country display normalisation: single label for the Dutch group
def norm_country(c): return "The Netherlands" if c in ("Netherlands","the Netherlands") else c

def city_meta(d):
    if d in UK_NAMES and not os.path.exists(f"{d}/city.js"):
        return {"name": UK_NAMES[d], "country": "United Kingdom", "lat": 51.515, "lng": -0.11, "cur": "£"}
    src = open(f"{d}/city.js", encoding="utf-8").read()
    g = lambda p, dflt=None: (re.search(p, src).group(1) if re.search(p, src) else dflt)
    mc = re.search(r'mapCenter:\[(-?[\d.]+),(-?[\d.]+)\]', src)
    return {"name": g(r'name:"([^"]+)"'), "country": norm_country(g(r'country_name:"([^"]+)"', "United Kingdom")),
            "lat": float(mc.group(1)), "lng": float(mc.group(2)), "cur": g(r'cur:"([^"]+)"', "\u00a3")}

def seg_count(d):
    n = 0
    with open(f"{d}/data/segments.js", encoding="utf-8") as f:
        for line in f:
            n += line.count('{"id"')
    return n

# Legacy directories whose pages exist but were never in the published picker -
# kept out so the published city set stays exactly as shipped (136 destinations).
LEGACY_UNLISTED = {"bremen","dortmund","dresden","duisburg","essen","genoa","hanover","lodz","nuremberg","palermo","poznan","wroclaw"}
PICKER_JS = r"""
/* Shared geographic Europe map: Natural Earth land paths with city dots positioned on the same projection. */
window.lpeMapSVG=function(selId,curId){
  const RCOL={Southern:"#c0563f",Western:"#2c6e59",Northern:"#3a5a8c",Eastern:"#8a6d3b"};
  const land=(window.LPE_LAND||[]).map(d=>'<path class="land" d="'+d+'"/>').join("");
  const dots=window.CITIES.slice(1).map(c=>{
    const r=Math.max(4,Math.min(13,3+Math.sqrt(c.n)/4.2));
    const cls="mapdot"+(selId&&!(selId.has?selId.has(c.id):selId===c.id)?" dim":"")+(curId===c.id?" cur":"");
    return '<a href="'+window.LPE_BASE+c.url+'" class="mapdotlink" aria-label="'+c.name+', '+c.country+' - '+c.n+' scored segments"><circle class="'+cls+'" cx="'+c.x+'" cy="'+c.y+'" r="'+r+'" fill="'+RCOL[c.region]+'"><title>'+c.name+', '+c.country+' - '+c.n+' segments</title></circle></a>';
  }).join("");
  return '<svg class="eumap geo" viewBox="95 274 730 830" role="img" aria-label="Geographic map of Europe with one dot per city">'+land+dots+'</svg>';
};
(function(){
 const base=window.LPE_BASE,path=location.pathname,nav=document.getElementById('citynav'); if(!nav)return;
 const cur=(CITIES.find(c=>c.url&&path.indexOf(base+c.url)===0)||CITIES[0]);
 nav.innerHTML=`<button class="citypick-btn" type="button" aria-expanded="false"><span>City</span><b>${cur.name}</b><i>&#8964;</i></button><div class="citypick-panel" hidden><div class="citypick-map">${lpeMapSVG(null,cur.id)}<div class="mapkey">Natural Earth geography - a dot per city, sized by scored segments, coloured by region. Tap a dot to open the city.</div></div><label><span class="sr-only">Search cities</span><input class="citypick-search" type="search" placeholder="Search ${CITIES.length-1} cities or countries" autocomplete="off" aria-controls="citypick-results"></label><div class="citypick-status sr-only" aria-live="polite"></div><div class="citypick-groups" id="citypick-results"></div></div>`;
 const btn=nav.querySelector('.citypick-btn'),panel=nav.querySelector('.citypick-panel'),inp=nav.querySelector('input'),box=nav.querySelector('.citypick-groups'),status=nav.querySelector('.citypick-status');
 const norm=s=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase();
 function render(q=''){q=norm(q.trim());let groups={},matches=0;CITIES.forEach(c=>{if(c.id==='hub')return;if(q&&!norm(`${c.name} ${c.country}`).includes(q))return;matches++;(groups[c.country]??=[]).push(c)});box.innerHTML=`<a class="citypick-all" href="${base}">All cities</a>`+Object.keys(groups).sort().map(k=>`<section><h3>${k}</h3>${groups[k].sort((a,b)=>a.name.localeCompare(b.name)).map(c=>`<a href="${base+c.url}"${c.id===cur.id?' class="on"':''}>${c.name}</a>`).join('')}</section>`).join('')+(Object.keys(groups).length?'':'<p class="citypick-empty">No matching city</p>');status.textContent=matches+' matching '+(matches===1?'city':'cities')}
 function open(v){panel.hidden=!v;btn.setAttribute('aria-expanded',String(v));if(v){render(inp.value);setTimeout(()=>inp.focus(),0)}} btn.onclick=()=>open(panel.hidden);inp.oninput=()=>render(inp.value);document.addEventListener('click',e=>{if(!nav.contains(e.target))open(false)});document.addEventListener('keydown',e=>{if(e.key==='Escape')open(false);if(!panel.hidden&&(e.key==='ArrowDown'||e.key==='ArrowUp')){const links=[...box.querySelectorAll('.citypick-groups a')],i=links.indexOf(document.activeElement),n=e.key==='ArrowDown'?Math.min(i+1,links.length-1):Math.max(i-1,0);if(links[n]){e.preventDefault();links[n].focus()}}});render();
})();
"""


def main():
    cities = [{"id":"hub","name":"All cities","country":"Global","url":""}]
    dirs = sorted(dd for dd in os.listdir('.') if os.path.isdir(dd) and dd not in ("assets","pipeline") and os.path.exists(f"{dd}/data/segments.js") and dd not in LEGACY_UNLISTED)
    for d in dirs:
        m = city_meta(d); m.update(id=("uk-"+d if d in UK_NAMES else d), url=d+"/", n=seg_count(d), region=REGION[m["country"]])
        cities.append(m)
    # projection helpers used client-side too; bake x,y for a 1000-wide Mercator-ish canvas
    lon0, lon1, lat0, lat1 = -25.0, 45.0, 26.5, 71.5
    def merc(lat): return math.log(math.tan(math.pi/4 + math.radians(lat)/2))
    W = 1000.0
    xw = W / (lon1 - lon0)
    Hh = xw * (merc(lat1) - merc(lat0)) * 180 / math.pi
    for c in cities[1:]:
        c["x"] = round((c["lng"] - lon0) * xw, 1)
        c["y"] = round((merc(lat1) - merc(c["lat"])) * xw * 180 / math.pi, 1)
        c["lat"] = round(c["lat"], 4); c["lng"] = round(c["lng"], 4)
    out = ("/* Location Potential Europe - city picker data: name, country, macro-region, "
           "map coordinates (pre-projected x/y on a %dx%d canvas), currency, segment count. "
           "Generated by pipeline/tools/make_frontend_data.py - do not hand-edit. */\n" % (int(W), int(round(Hh))))
    out += 'window.LPE_BASE=(function(){var m=location.pathname.match(/^(.*\\/location-potential-europe\\/)/);return m?m[1]:"/";})();\n'
    out += "window.MAP_W=%d;window.MAP_H=%d;\n" % (int(W), int(round(Hh)))
    out += "window.CITIES=" + json.dumps(cities, ensure_ascii=False, separators=(",", ":")) + ";\n"
    out += PICKER_JS
    open("cities.js","w",encoding="utf-8").write(out)
    print("cities.js:", len(cities)-1, "cities,", len(out), "bytes, canvas", int(W), int(round(Hh)))

if __name__ == "__main__":
    main()
