import sys,json
sys.path.insert(0,'/home/sandbox/europe/work')
from cities_eu import CITIES_EU,SHIP
UK=['london','manchester','birmingham','leeds','bristol','liverpool','sheffield','glasgow','edinburgh']
UN={'london':'London','manchester':'Manchester','birmingham':'Birmingham','leeds':'Leeds','bristol':'Bristol','liverpool':'Liverpool','sheffield':'Sheffield','glasgow':'Glasgow','edinburgh':'Edinburgh'}
entries=[dict(id='hub',name='All cities',country='Europe',url='')]
entries += [dict(id='uk-'+c,name=UN[c],country='United Kingdom',url=c+'/') for c in UK]
entries += [dict(id=c,name=CITIES_EU[c]['name'],country=CITIES_EU[c]['country_name'].title(),url=c+'/') for c in SHIP if c not in UK]
js=json.dumps(entries,ensure_ascii=False,separators=(',',':'))
out=f'''/* Location Potential Europe - searchable country-grouped city picker. */
window.LPE_BASE=(function(){{var m=location.pathname.match(/^(.*\\/location-potential-europe\\/)/);return m?m[1]:"/";}})();
window.CITIES={js};
(function(){{
 const base=window.LPE_BASE,path=location.pathname,nav=document.getElementById('citynav'); if(!nav)return;
 const cur=(CITIES.find(c=>c.url&&path.indexOf(base+c.url)===0)||CITIES[0]);
 nav.innerHTML=`<button class="citypick-btn" type="button" aria-expanded="false"><span>City</span><b>${{cur.name}}</b><i>⌄</i></button><div class="citypick-panel" hidden><label><span class="sr-only">Search cities</span><input class="citypick-search" type="search" placeholder="Search ${{CITIES.length-1}} cities or countries" autocomplete="off"></label><div class="citypick-groups"></div></div>`;
 const btn=nav.querySelector('.citypick-btn'),panel=nav.querySelector('.citypick-panel'),inp=nav.querySelector('input'),box=nav.querySelector('.citypick-groups');
 function render(q=''){{q=q.trim().toLocaleLowerCase();let groups={{}};CITIES.forEach(c=>{{if(c.id==='hub')return;if(q&&!(`${{c.name}} ${{c.country}}`.toLocaleLowerCase().includes(q)))return;(groups[c.country]??=[]).push(c)}});box.innerHTML=`<a class="citypick-all" href="${{base}}">All cities</a>`+Object.keys(groups).sort().map(k=>`<section><h3>${{k}}</h3>${{groups[k].sort((a,b)=>a.name.localeCompare(b.name)).map(c=>`<a href="${{base+c.url}}"${{c.id===cur.id?' class="on"':''}}>${{c.name}}</a>`).join('')}}</section>`).join('')+(Object.keys(groups).length?'':'<p class="citypick-empty">No matching city</p>')}}
 function open(v){{panel.hidden=!v;btn.setAttribute('aria-expanded',String(v));if(v){{render(inp.value);setTimeout(()=>inp.focus(),0)}}}} btn.onclick=()=>open(panel.hidden);inp.oninput=()=>render(inp.value);document.addEventListener('click',e=>{{if(!nav.contains(e.target))open(false)}});document.addEventListener('keydown',e=>{{if(e.key==='Escape')open(false)}});render();
}})();
'''
open('/home/sandbox/europe/repo/cities.js','w').write(out)
print('cities.js',len(entries))
