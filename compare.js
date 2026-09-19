/* Location Potential Europe - scope-first cross-city comparison.
   Start with broad regions or featured cities; search all cities only on demand.
   The map is real geography (Natural Earth land outline) with city dots on top,
   and supports free-form area drawing (lasso) to select cities. */
(function(){
const root=document.getElementById('compare-app'); if(!root)return;
const ALL=window.CITIES.slice(1);
const REGIONS=["Southern","Western","Northern","Eastern"];
const RCOL={Southern:"#c0563f",Western:"#2c6e59",Northern:"#3a5a8c",Eastern:"#8a6d3b"};
const COUNTRIES=[...new Set(ALL.map(c=>c.country))].sort();
const FEATURED=['uk-london','madrid','paris','rome','berlin','barcelona','vienna','amsterdam','lisbon'];
const norm=s=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase();
const scope={regions:new Set(),countries:new Set(),cities:new Set(),all:true};
let conceptId=null,zonesCache={},drawMode=false,drawPoly=null,lasso=null;

/* concept picker mirrors the city pages: 9 most compact presets up front, the rest behind "See more concepts" */
const CONCEPTS=window.COMPARE_CONCEPTS;
const CATLABEL={cafe:"Café & coffee",restaurant:"Restaurants",pub_bar:"Pubs & bars",fast_food:"Fast food",grocery:"Grocery & food retail",fitness:"Fitness & gyms",cowork:"Workspace",services:"Services",agents:"Estate agents",pharmacy:"Pharmacy",vets:"Vets"};
const PRESETS_VISIBLE=9;
let conceptsExpanded=false,conceptFilter="all";

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
    if(b.dataset.all){scope.all=true;scope.regions.clear();scope.countries.clear();scope.cities.clear();drawPoly=null;}
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
function polyPath(pts,close){return 'M'+pts.map(p=>p.x.toFixed(1)+','+p.y.toFixed(1)).join('L')+(close?'Z':'');}
function renderMap(){
  const sel=new Set(scopeList().map(c=>c.id));
  const land=(window.LPE_LAND||[]).map(d=>`<path class="land" d="${d}"/>`).join('');
  const dots=ALL.map(c=>{const r=Math.max(5,Math.min(14,4+Math.sqrt(c.n)/4.2)),dim=!sel.has(c.id);return `<g class="area-city" role="button" tabindex="0" data-city="${c.id}" aria-label="${c.name}, ${c.country}${dim?' - not selected':' - selected'}" aria-pressed="${!dim}"><circle class="mapdot${dim?' dim':''}" cx="${c.x}" cy="${c.y}" r="${r}" fill="${RCOL[c.region]}"><title>${c.name}, ${c.country} - ${c.n} segments</title></circle></g>`;}).join('');
  const area=drawPoly?`<path class="area-selection" d="${polyPath(drawPoly,true)}"/>`:'';
  document.getElementById('scope-map').innerHTML=`<svg class="eumap area-map geo${drawMode?' drawing':''}" viewBox="95 274 730 830" role="img" aria-label="Map of Europe. Select city dots or draw a free-form area.">${land}${dots}${area}<path class="area-drag" hidden/></svg><div class="mapkey">Real map outline (Natural Earth, public domain) - dot size = scored segments, colour = macro-region. ${scope.all?'All cities in scope.':sel.size+' cities in scope.'}</div>`;
  bindMap();
  document.getElementById('draw-area').classList.toggle('on',drawMode);
  document.getElementById('draw-area').setAttribute('aria-pressed',drawMode);
  document.getElementById('draw-area').textContent=drawMode?'Drawing: draw any shape':'Draw an area';
  document.getElementById('clear-area').hidden=!drawPoly;
}
function pointInSvg(svg,e){const p=svg.createSVGPoint();p.x=e.clientX;p.y=e.clientY;return p.matrixTransform(svg.getScreenCTM().inverse());}
function insidePoly(c,pts){
  let inside=false;
  for(let i=0,j=pts.length-1;i<pts.length;j=i++){
    const xi=pts[i].x,yi=pts[i].y,xj=pts[j].x,yj=pts[j].y;
    if((yi>c.y)!==(yj>c.y)&&c.x<(xj-xi)*(c.y-yi)/(yj-yi)+xi)inside=!inside;
  }
  return inside;
}
function bindMap(){
  const svg=document.querySelector('#scope-map svg');
  svg.querySelectorAll('.area-city').forEach(g=>{g.onclick=e=>{if(drawMode)return;e.preventDefault();toggleCity(g.dataset.city);};g.onkeydown=e=>{if(!drawMode&&(e.key==='Enter'||e.key===' ')){e.preventDefault();toggleCity(g.dataset.city);}};});
  if(!drawMode)return;
  const live=svg.querySelector('.area-drag');
  svg.onpointerdown=e=>{lasso=[pointInSvg(svg,e)];svg.setPointerCapture(e.pointerId);live.hidden=false;live.setAttribute('d',polyPath(lasso,false));};
  svg.onpointermove=e=>{if(!lasso)return;const p=pointInSvg(svg,e),last=lasso[lasso.length-1];if(Math.hypot(p.x-last.x,p.y-last.y)>=3){lasso.push(p);live.setAttribute('d',polyPath(lasso,false));}};
  svg.onpointerup=e=>{
    if(!lasso)return;const pts=lasso;lasso=null;
    const xs=pts.map(p=>p.x),ys=pts.map(p=>p.y),bw=Math.max(...xs)-Math.min(...xs),bh=Math.max(...ys)-Math.min(...ys);
    if(pts.length<8||bw<12||bh<12){live.hidden=true;return;} /* accidental tap: stay in draw mode */
    drawPoly=pts;scope.all=false;scope.regions.clear();scope.countries.clear();scope.cities=new Set(ALL.filter(c=>insidePoly(c,pts)).map(c=>c.id));ensureScope();drawMode=false;renderAll();
  };
}
function renderConcepts(){
  const box=document.getElementById('concept-chips');
  const pool=conceptFilter==="all"?CONCEPTS:CONCEPTS.filter(p=>p.cat===conceptFilter);
  let visible=conceptsExpanded?pool.slice():[...CONCEPTS].sort((a,b)=>a.name.length-b.name.length||a.name.localeCompare(b.name)).slice(0,PRESETS_VISIBLE); /* default set: shortest names so the chips stay compact */
  if(conceptId&&!visible.some(p=>p.id===conceptId)){const sel=CONCEPTS.find(p=>p.id===conceptId);if(sel)visible.push(sel);} /* keep the active concept on screen */
  const filterRow=conceptsExpanded
    ? `<div class="preset-filters"><span class="pf-label">Filter by category:</span><button class="preset filter ${conceptFilter==="all"?"active":""}" data-f="all">All</button>`
      +Object.keys(CATLABEL).filter(c=>CONCEPTS.some(p=>p.cat===c)).map(c=>`<button class="preset filter ${conceptFilter===c?"active":""}" data-f="${c}">${CATLABEL[c]}</button>`).join("")+`</div>`:"";
  const moreBtn=`<button class="preset more" data-p="__more">${conceptsExpanded?'See fewer concepts':'See more concepts ('+(CONCEPTS.length-PRESETS_VISIBLE)+' more)'}</button>`;
  box.innerHTML=(conceptsExpanded?moreBtn:"")+filterRow+visible.map(p=>`<button class="preset ${p.id===conceptId?'active':''}" data-c="${p.id}" aria-pressed="${p.id===conceptId}">${p.name}</button>`).join('')+(conceptsExpanded?"":moreBtn); /* expanded list: collapse control first, not buried at the bottom */
  box.querySelectorAll('button').forEach(b=>b.onclick=()=>{
    if(b.dataset.f){conceptFilter=b.dataset.f;renderConcepts();return;}
    if(b.dataset.p==='__more'){conceptsExpanded=!conceptsExpanded;if(!conceptsExpanded)conceptFilter="all";renderConcepts();return;}
    conceptId=b.dataset.c;renderAll();loadResults();
  });
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
function renderAll(){renderScope();renderMap();renderConcepts();if(conceptId&&zonesCache[conceptId])renderResults();}
const otherToggle=document.getElementById('other-cities-toggle'),otherPanel=document.getElementById('other-cities-panel');
otherToggle.onclick=()=>{const open=otherPanel.hidden;otherPanel.hidden=!open;otherToggle.setAttribute('aria-expanded',open);otherToggle.textContent=open?'Hide other cities':'Select other cities';if(open)setTimeout(()=>document.getElementById('scope-city-search').focus(),0);};
document.getElementById('scope-city-search').oninput=e=>renderCitySearch(e.target.value);
document.getElementById('draw-area').onclick=()=>{drawMode=!drawMode;renderMap();};
document.getElementById('clear-area').onclick=()=>{drawPoly=null;scope.all=true;scope.regions.clear();scope.countries.clear();scope.cities.clear();renderAll();};
renderScope();renderMap();renderConcepts();loadResults();
})();
