/* Location Potential Europe - scope-first cross-city comparison.
   Start with broad regions or featured cities; search all cities only on demand.
   The schematic map also supports drawing a rectangular area to select cities. */
(function(){
const root=document.getElementById('compare-app'); if(!root)return;
const ALL=window.CITIES.slice(1);
const REGIONS=["Southern","Western","Northern","Eastern"];
const RCOL={Southern:"#c0563f",Western:"#2c6e59",Northern:"#3a5a8c",Eastern:"#8a6d3b"};
const COUNTRIES=[...new Set(ALL.map(c=>c.country))].sort();
const FEATURED=['uk-london','madrid','paris','rome','berlin','barcelona','vienna','amsterdam','lisbon'];
const norm=s=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase();
const scope={regions:new Set(),countries:new Set(),cities:new Set(),all:true};
let conceptId=null,zonesCache={},drawMode=false,drawStart=null,drawRect=null;

function inScope(c){return scope.all||scope.regions.has(c.region)||scope.countries.has(c.country)||scope.cities.has(c.id);}
function scopeList(){return ALL.filter(inScope);}
function ensureScope(){if(!scope.regions.size&&!scope.countries.size&&!scope.cities.size)scope.all=true;}
function scopeLabel(){
  if(scope.all)return "all Europe";
  const parts=[...[...scope.regions].map(r=>r+" Europe"),...scope.countries,...[...scope.cities].map(id=>{const c=ALL.find(x=>x.id===id);return c?c.name:id;})];
  return parts.join(" + ")||"all Europe";
}
const eurFmt=n=>"€"+Math.round(n).toLocaleString("en-GB");
function toggleCity(id){scope.all=false;scope.cities.has(id)?scope.cities.delete(id):scope.cities.add(id);ensureScope();renderAll();}

function renderScope(){
  const box=document.getElementById('scope-chips');
  box.innerHTML=`<button class="chip-scope ${scope.all?'on':''}" data-all="1" aria-pressed="${scope.all}">All Europe (${ALL.length} cities)</button>`
    +REGIONS.map(r=>`<button class="chip-scope ${scope.regions.has(r)?'on':''}" data-region="${r}" aria-pressed="${scope.regions.has(r)}" style="--rc:${RCOL[r]}">${r} Europe</button>`).join('');
  box.querySelectorAll('button').forEach(b=>b.onclick=()=>{
    if(b.dataset.all){scope.all=true;scope.regions.clear();scope.countries.clear();scope.cities.clear();drawRect=null;}
    else{scope.all=false;scope.regions.has(b.dataset.region)?scope.regions.delete(b.dataset.region):scope.regions.add(b.dataset.region);ensureScope();}
    renderAll();
  });
  const countryBox=document.getElementById('country-chips');
  countryBox.innerHTML=COUNTRIES.map(c=>`<button class="chip-scope ${scope.countries.has(c)?'on':''}" data-country="${c}" aria-pressed="${scope.countries.has(c)}">${c}</button>`).join('');
  countryBox.querySelectorAll('button').forEach(b=>b.onclick=()=>{scope.all=false;scope.countries.has(b.dataset.country)?scope.countries.delete(b.dataset.country):scope.countries.add(b.dataset.country);ensureScope();renderAll();});
  const featured=document.getElementById('featured-cities');
  featured.innerHTML=FEATURED.map(id=>{const c=ALL.find(x=>x.id===id);return `<button class="featured-city ${scope.cities.has(id)?'on':''}" data-city="${id}" aria-pressed="${scope.cities.has(id)}"><b>${c.name}</b><span>${c.country}</span></button>`;}).join('');
  featured.querySelectorAll('button').forEach(b=>b.onclick=()=>toggleCity(b.dataset.city));
  const picked=document.getElementById('scope-cities-picked');
  picked.innerHTML=[...scope.cities].filter(id=>!FEATURED.includes(id)).map(id=>{const c=ALL.find(x=>x.id===id);return `<button class="chip-scope on" data-city="${id}" aria-pressed="true">${c?c.name:id} ×</button>`;}).join('');
  picked.querySelectorAll('button').forEach(b=>b.onclick=()=>toggleCity(b.dataset.city));
}
function renderCitySearch(q){
  const res=document.getElementById('scope-cities-results');
  q=norm(q||'').trim(); if(!q){res.innerHTML='';return;}
  const hits=ALL.filter(c=>norm(c.name+' '+c.country).includes(q)).slice(0,10);
  res.innerHTML=hits.map(c=>`<button class="city-hit ${scope.cities.has(c.id)?'on':''}" data-add="${c.id}">${c.name} <span>${c.country}</span></button>`).join('')||'<div class="hub-note">No matching city</div>';
  res.querySelectorAll('button').forEach(b=>b.onclick=()=>{toggleCity(b.dataset.add);document.getElementById('scope-city-search').value='';renderCitySearch('');});
}
function renderMap(){
  const sel=new Set(scopeList().map(c=>c.id));
  const dots=ALL.map(c=>{const r=Math.max(5,Math.min(14,4+Math.sqrt(c.n)/4.2)),dim=!sel.has(c.id);return `<g class="area-city" role="button" tabindex="0" data-city="${c.id}" aria-label="${c.name}, ${c.country}${dim?' - not selected':' - selected'}" aria-pressed="${!dim}"><circle class="mapdot${dim?' dim':''}" cx="${c.x}" cy="${c.y}" r="${r}" fill="${RCOL[c.region]}"><title>${c.name}, ${c.country} - ${c.n} segments</title></circle></g>`;}).join('');
  const rect=drawRect?`<rect class="area-selection" x="${drawRect.x}" y="${drawRect.y}" width="${drawRect.w}" height="${drawRect.h}"/>`:'';
  document.getElementById('scope-map').innerHTML=`<svg class="eumap area-map${drawMode?' drawing':''}" viewBox="95 274 730 830" role="img" aria-label="Schematic map of Europe. Select city dots or use Draw an area.">${dots}${rect}<rect class="area-drag" x="0" y="0" width="0" height="0" hidden/></svg><div class="mapkey">Schematic map - dot position approximate, size = scored segments, colour = macro-region. ${scope.all?'All cities in scope.':sel.size+' cities in scope.'}</div>`;
  bindMap();
  document.getElementById('draw-area').classList.toggle('on',drawMode);
  document.getElementById('draw-area').setAttribute('aria-pressed',drawMode);
  document.getElementById('draw-area').textContent=drawMode?'Drawing: drag on map':'Draw an area';
  document.getElementById('clear-area').hidden=!drawRect;
}
function pointInSvg(svg,e){const p=svg.createSVGPoint();p.x=e.clientX;p.y=e.clientY;return p.matrixTransform(svg.getScreenCTM().inverse());}
function bindMap(){
  const svg=document.querySelector('#scope-map svg');
  svg.querySelectorAll('.area-city').forEach(g=>{g.onclick=e=>{if(drawMode)return;e.preventDefault();toggleCity(g.dataset.city);};g.onkeydown=e=>{if(!drawMode&&(e.key==='Enter'||e.key===' ')){e.preventDefault();toggleCity(g.dataset.city);}};});
  if(!drawMode)return;
  const live=svg.querySelector('.area-drag');
  svg.onpointerdown=e=>{drawStart=pointInSvg(svg,e);svg.setPointerCapture(e.pointerId);live.hidden=false;live.setAttribute('x',drawStart.x);live.setAttribute('y',drawStart.y);live.setAttribute('width',0);live.setAttribute('height',0);};
  svg.onpointermove=e=>{if(!drawStart)return;const p=pointInSvg(svg,e),x=Math.min(drawStart.x,p.x),y=Math.min(drawStart.y,p.y),w=Math.abs(p.x-drawStart.x),h=Math.abs(p.y-drawStart.y);live.setAttribute('x',x);live.setAttribute('y',y);live.setAttribute('width',w);live.setAttribute('height',h);};
  svg.onpointerup=e=>{if(!drawStart)return;const p=pointInSvg(svg,e),r={x:Math.min(drawStart.x,p.x),y:Math.min(drawStart.y,p.y),w:Math.abs(p.x-drawStart.x),h:Math.abs(p.y-drawStart.y)};drawStart=null;if(r.w<12||r.h<12)return;drawRect=r;scope.all=false;scope.regions.clear();scope.countries.clear();scope.cities=new Set(ALL.filter(c=>c.x>=r.x&&c.x<=r.x+r.w&&c.y>=r.y&&c.y<=r.y+r.h).map(c=>c.id));ensureScope();drawMode=false;renderAll();};
}
function renderConcepts(q){
  const box=document.getElementById('concept-chips');
  const list=window.COMPARE_CONCEPTS.filter(p=>!q||norm(p.name).includes(norm(q)));
  box.innerHTML=list.map(p=>`<button class="chip-scope concept ${p.id===conceptId?'on':''}" data-c="${p.id}" aria-pressed="${p.id===conceptId}">${p.name}</button>`).join('');
  box.querySelectorAll('button').forEach(b=>b.onclick=()=>{conceptId=b.dataset.c;renderAll();loadResults();});
}
function loadResults(){
  const out=document.getElementById('compare-results');
  if(!conceptId){out.innerHTML='<div class="hub-note">Pick a concept above to rank every zone in your scope.</div>';return;}
  if(zonesCache[conceptId])return renderResults();
  out.innerHTML='<div class="hub-note">Scoring '+scopeList().length+' cities…</div>';
  const sc=document.createElement('script');sc.src=window.LPE_BASE+'assets/compare/'+conceptId+'.js';sc.onload=()=>{zonesCache[conceptId]=window.COMPARE_ZONES;renderResults();};sc.onerror=()=>{out.innerHTML='<div class="hub-note">Comparison data missing for this concept.</div>';};document.head.appendChild(sc);
}
function renderResults(){
  const out=document.getElementById('compare-results');
  const cities=new Set(scopeList().map(c=>c.url.replace(/\/$/,'')));const zones=(zonesCache[conceptId]||[]).filter(z=>cities.has(z.c));const p=window.COMPARE_CONCEPTS.find(x=>x.id===conceptId);
  if(!zones.length){out.innerHTML='<div class="hub-note">No zones in this scope.</div>';return;}
  const ranked=zones.slice().sort((a,b)=>b.e-a.e).slice(0,20),meta=id=>ALL.find(c=>c.url===id+'/');
  out.innerHTML=`<h3>Best zones for “${p.name}” across ${scopeLabel()}</h3><div class="hub-note">Ranked by modelled monthly revenue converted to EUR at ECB reference rates (${window.FX_DATE}) for comparability only - local currency is shown too and stays canonical. Every figure MODELLED; open the city page for the full input breakdown. Fit score is computed within each city.</div><div class="cmp-list" role="list">${ranked.map((z,i)=>{const c=meta(z.c);return `<a role="listitem" class="cmp-row" href="${window.LPE_BASE}${z.c}/?concept=${conceptId}"><span class="cmp-rank">${i+1}</span><span class="cmp-main"><b>${z.n}</b><span class="cmp-city">${c.name}, ${c.country} · fit ${z.s}/100</span></span><span class="cmp-rev"><b>${eurFmt(z.e)}/mo</b><span class="cmp-local">${c.cur}${z.r.toLocaleString("en-GB")} local · range ${c.cur}${z.lo.toLocaleString("en-GB")}-${c.cur}${z.hi.toLocaleString("en-GB")}</span></span></a>`;}).join('')}</div>`;
}
function renderAll(){renderScope();renderMap();renderConcepts(document.getElementById('concept-search').value);if(conceptId&&zonesCache[conceptId])renderResults();}
const otherToggle=document.getElementById('other-cities-toggle'),otherPanel=document.getElementById('other-cities-panel');
otherToggle.onclick=()=>{const open=otherPanel.hidden;otherPanel.hidden=!open;otherToggle.setAttribute('aria-expanded',open);otherToggle.textContent=open?'Hide other cities':'Select other cities';if(open)setTimeout(()=>document.getElementById('scope-city-search').focus(),0);};
document.getElementById('scope-city-search').oninput=e=>renderCitySearch(e.target.value);
document.getElementById('concept-search').oninput=e=>renderConcepts(e.target.value);
document.getElementById('draw-area').onclick=()=>{drawMode=!drawMode;renderMap();};
document.getElementById('clear-area').onclick=()=>{drawRect=null;scope.all=true;scope.regions.clear();scope.countries.clear();scope.cities.clear();renderAll();};
renderScope();renderMap();renderConcepts('');loadResults();
})();
