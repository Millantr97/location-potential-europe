/* Location Potential Europe - scope-first cross-city comparison.
   1. choose scope (macro-regions, countries, single cities - freely combinable)
   2. pick a concept
   3. ranked best zones across the chosen scope. */
(function(){
const root=document.getElementById('compare-app'); if(!root)return;
const ALL=window.CITIES.slice(1);
const REGIONS=["Southern","Western","Northern","Eastern"];
const RCOL={Southern:"#c0563f",Western:"#2c6e59",Northern:"#3a5a8c",Eastern:"#8a6d3b"};
const COUNTRIES=[...new Set(ALL.map(c=>c.country))].sort();
const norm=s=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase();
const scope={regions:new Set(),countries:new Set(),cities:new Set(),all:true};
let conceptId=null, zonesCache={};

function inScope(c){return scope.all||scope.regions.has(c.region)||scope.countries.has(c.country)||scope.cities.has(c.id);}
function scopeList(){return ALL.filter(inScope);}
function scopeLabel(){
  if(scope.all)return "all Europe";
  const parts=[...[...scope.regions].map(r=>r+" Europe"),...scope.countries,...[...scope.cities].map(id=>{const c=ALL.find(x=>x.id===id);return c?c.name:id;})];
  return parts.join(" + ")||"all Europe";
}
const eurFmt=n=>"€"+Math.round(n).toLocaleString("en-GB");

function renderScope(){
  const box=document.getElementById('scope-chips');
  box.innerHTML=`<button class="chip-scope ${scope.all?'on':''}" data-all="1" aria-pressed="${scope.all}">All Europe (${ALL.length} cities)</button>`
    +REGIONS.map(r=>`<button class="chip-scope ${scope.regions.has(r)?'on':''}" data-region="${r}" aria-pressed="${scope.regions.has(r)}" style="--rc:${RCOL[r]}">${r} Europe</button>`).join("")
    +COUNTRIES.map(c=>`<button class="chip-scope ${scope.countries.has(c)?'on':''}" data-country="${c}" aria-pressed="${scope.countries.has(c)}">${c}</button>`).join("");
  box.querySelectorAll('button').forEach(b=>b.onclick=()=>{
    if(b.dataset.all){scope.all=true;scope.regions.clear();scope.countries.clear();scope.cities.clear();}
    else{scope.all=false;
      if(b.dataset.region)scope.regions.has(b.dataset.region)?scope.regions.delete(b.dataset.region):scope.regions.add(b.dataset.region);
      if(b.dataset.country)scope.countries.has(b.dataset.country)?scope.countries.delete(b.dataset.country):scope.countries.add(b.dataset.country);
      if(!scope.regions.size&&!scope.countries.size&&!scope.cities.size)scope.all=true;}
    renderAll();
  });
  const picked=document.getElementById('scope-cities-picked');
  picked.innerHTML=[...scope.cities].map(id=>{const c=ALL.find(x=>x.id===id);return `<button class="chip-scope on" data-city="${id}" aria-pressed="true">${c?c.name:id} ×</button>`;}).join("");
  picked.querySelectorAll('button').forEach(b=>b.onclick=()=>{scope.cities.delete(b.dataset.city);if(!scope.regions.size&&!scope.countries.size&&!scope.cities.size)scope.all=true;renderAll();});
}
function renderCitySearch(q){
  const res=document.getElementById('scope-cities-results');
  q=norm(q||'').trim(); if(!q){res.innerHTML='';return;}
  const hits=ALL.filter(c=>norm(c.name+' '+c.country).includes(q)).slice(0,8);
  res.innerHTML=hits.map(c=>`<button class="city-hit" data-add="${c.id}">${c.name} <span>${c.country}</span></button>`).join('')||'<div class="hub-note">No matching city</div>';
  res.querySelectorAll('button').forEach(b=>b.onclick=()=>{scope.all=false;scope.cities.add(b.dataset.add);document.getElementById('scope-city-search').value='';renderCitySearch('');renderAll();});
}
function renderMap(){
  const sel=new Set(scopeList().map(c=>c.id));
  document.getElementById('scope-map').innerHTML=window.lpeMapSVG(sel,null)
    +`<div class="mapkey">Schematic map - dot position approximate, size = scored segments, colour = macro-region. ${scope.all?'All cities in scope.':sel.size+' cities in scope.'}</div>`;
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
  const finish=()=>{renderResults();};
  if(zonesCache[conceptId])return finish();
  out.innerHTML='<div class="hub-note">Scoring '+scopeList().length+' cities…</div>';
  const sc=document.createElement('script');
  sc.src=(window.LPE_BASE)+'assets/compare/'+conceptId+'.js';
  sc.onload=()=>{zonesCache[conceptId]=window.COMPARE_ZONES;finish();};
  sc.onerror=()=>{out.innerHTML='<div class="hub-note">Comparison data missing for this concept.</div>';};
  document.head.appendChild(sc);
}
function renderResults(){
  const out=document.getElementById('compare-results');
  const cities=new Set(scopeList().map(c=>c.url.replace(/\/$/,'')));
  const zones=(zonesCache[conceptId]||[]).filter(z=>cities.has(z.c));
  const p=window.COMPARE_CONCEPTS.find(x=>x.id===conceptId);
  if(!zones.length){out.innerHTML='<div class="hub-note">No zones in this scope.</div>';return;}
  const ranked=zones.slice().sort((a,b)=>b.e-a.e).slice(0,20);
  const meta=id=>ALL.find(c=>c.url===id+'/');
  out.innerHTML=`<h3>Best zones for “${p.name}” across ${scopeLabel()}</h3>
   <div class="hub-note">Ranked by modelled monthly revenue converted to EUR at ECB reference rates (${window.FX_DATE}) for comparability only - local currency is shown too and stays canonical. Every figure MODELLED; open the city page for the full input breakdown. Fit score is computed within each city.</div>
   <div class="cmp-list" role="list">${ranked.map((z,i)=>{const c=meta(z.c);return `
    <a role="listitem" class="cmp-row" href="${window.LPE_BASE}${z.c}/?concept=${conceptId}">
      <span class="cmp-rank">${i+1}</span>
      <span class="cmp-main"><b>${z.n}</b><span class="cmp-city">${c.name}, ${c.country} · fit ${z.s}/100</span></span>
      <span class="cmp-rev"><b>${eurFmt(z.e)}/mo</b><span class="cmp-local">${c.cur}${z.r.toLocaleString("en-GB")} local · range ${c.cur}${z.lo.toLocaleString("en-GB")}-${c.cur}${z.hi.toLocaleString("en-GB")}</span></span>
    </a>`;}).join('')}</div>`;
}
function renderAll(){renderScope();renderMap();renderConcepts(document.getElementById('concept-search').value);renderResults&&conceptId&&zonesCache[conceptId]&&renderResults();}
document.getElementById('scope-city-search').oninput=e=>renderCitySearch(e.target.value);
document.getElementById('concept-search').oninput=e=>renderConcepts(e.target.value);
renderScope();renderMap();renderConcepts('');
loadResults();
})();
