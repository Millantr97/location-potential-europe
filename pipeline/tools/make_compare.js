/* Bake cross-city comparison: for every published city and every concept preset,
   run the site's exact scoring (app.js prefix via lib_score) and store the top 5
   zones. Output: assets/compare/<concept>.js + assets/compare-index.js.
   Usage: node pipeline/tools/make_compare.js  (from repo root) */
const fs = require('fs'), path = require('path');
const { loadCity } = require('./lib_score.js');

const root = path.join(__dirname, '..', '..');
const citiesSrc = fs.readFileSync(path.join(root, 'cities.js'), 'utf8');
const CITIES = JSON.parse(citiesSrc.match(/window\.CITIES=(\[.*\]);/s)[1]).slice(1); // drop hub

/* FX: ECB reference rates via Frankfurter, 18 Sep 2026; BGN pegged. Ranking-only conversion. */
const FX = { EUR:1, USD:1.174, AUD:1.764, GBP:0.8588, PLN:4.3635, CZK:24.339, HUF:364.28, SEK:11.2915, NOK:10.8095, DKK:7.4754, CHF:0.9462, RON:5.2647, BGN:1.9558 };
const COUNTRY2CODE = { 'United Kingdom':'GBP', 'Poland':'PLN', 'Czechia':'CZK', 'Hungary':'HUF', 'Sweden':'SEK', 'Norway':'NOK', 'Denmark':'DKK', 'Switzerland':'CHF', 'Romania':'RON', 'Bulgaria':'BGN', 'United States':'USD', 'Australia':'AUD' }; // everything else in the set is EUR

function observedCount(s){ return Object.entries(s.osm||{}).filter(([k,v])=>typeof v==='number' && !k.endsWith('_share')).reduce((a,[,v])=>a+Math.max(0,v),0); }
function evidenceCoverage(s, concept){
  // Coverage, not predictive certainty. OBSERVED 45%, AREA CONTEXT 30%, MODELLED specification 25%.
  const osm=s.osm||{}, observedSignals=['cafe','restaurant','fast_food','pub_bar','grocery','fitness','cowork','services','shops'];
  const obsPresent=observedSignals.filter(k=>Number.isFinite(osm[k])).length/observedSignals.length;
  const depth=Math.min(1,Math.log10(1+observedCount(s))/2);
  const observed=Math.round(100*(0.55*obsPresent+0.45*depth));
  const l=s.lsoa||{}, ctxFields=['residents','pct20_39','pct_under20','pct_students','pct_prof','pct_nonuk'];
  const context=Math.round(100*ctxFields.filter(k=>Number.isFinite(l[k])).length/ctxFields.length);
  const modelChecks=[s.flow&&Number.isFinite(s.flow.annual_total),s.rent&&Number.isFinite(s.rent.retail_rv_m2),s.model&&Number.isFinite(s.model.spend_est),s.model&&s.model.rhythm&&Object.keys(s.model.rhythm).length>=5];
  const model=Math.round(100*modelChecks.filter(Boolean).length/modelChecks.length);
  return {score:Math.round(observed*.45+context*.30+model*.25),observed,context,model};
}
function weatherBasis(country){ return ['United Kingdom','Ireland','Norway','Sweden','Finland','Denmark','Iceland'].includes(country)?'weather-sensitive':['Spain','Portugal','Italy','Greece','Australia'].includes(country)?'outdoor-seasonal':'mixed-weather'; }
function seasonalityBasis(country){ return ['Spain','Portugal','Italy','Greece','Croatia','Australia'].includes(country)?'higher seasonal swing':'moderate seasonal swing'; }
let concepts = null, perConcept = {};
for (const c of CITIES) {
  const dir = c.url.replace(/\/$/, '');
  let m;
  try { m = loadCity(root, dir); } catch (e) { console.error('SKIP', dir, e.message); continue; }
  if (!concepts) {
    concepts = m.PRESETS.map(p => ({ id: p.id, name: p.name, cat: p.cat, floorspace: p.floorspace, ticket: p.ticket }));
    for (const p of concepts) perConcept[p.id] = [];
  }
  const code = COUNTRY2CODE[c.country] || 'EUR';
  for (const p of concepts) {
    const concept = m.normalizeConcept(JSON.parse(JSON.stringify(m.PRESETS.find(x => x.id === p.id))));
    const top = m.computeAll(concept).slice(0, 5);
    for (const r of top) {
      const eur = r.rev.month / (FX[code] || 1);
      perConcept[p.id].push({ c: dir, n: r.seg.name, s: Math.round(r.score), r: Math.round(r.rev.month),
        lo: Math.round(r.rev.low), hi: Math.round(r.rev.high), e: Math.round(eur),
        la: +r.seg.lat.toFixed(5), ln: +r.seg.lng.toFixed(5),
        cf: evidenceCoverage(r.seg, concept), rv: Math.round(r.seg.rent && r.seg.rent.retail_rv_m2 || 0),
        pop: Math.round(r.seg.lsoa && r.seg.lsoa.residents || 0), flow: Math.round(r.seg.flow && r.seg.flow.annual_total || 0),
        obs: observedCount(r.seg), wb: weatherBasis(c.country), season: seasonalityBasis(c.country) });
    }
  }
  process.stderr.write('.');
}
fs.mkdirSync(path.join(root, 'assets', 'compare'), { recursive: true });
for (const p of concepts) {
  fs.writeFileSync(path.join(root, 'assets', 'compare', p.id + '.js'),
    `window.COMPARE_ZONES=${JSON.stringify(perConcept[p.id])};`);
}
fs.writeFileSync(path.join(root, 'assets', 'compare-index.js'),
  '/* concept list + ranking FX (ECB reference via Frankfurter, 18 Sep 2026; BGN pegged 1.9558). Ranking conversion only - local currency stays canonical. */\n' +
  `window.COMPARE_CONCEPTS=${JSON.stringify(concepts)};\nwindow.FX_RATES=${JSON.stringify(FX)};\nwindow.FX_DATE="18 Sep 2026";\n`);
console.error('\ndone', CITIES.length, 'cities x', concepts.length, 'concepts');
