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

let concepts = null, perConcept = {};
for (const c of CITIES) {
  const dir = c.url.replace(/\/$/, '');
  let m;
  try { m = loadCity(root, dir); } catch (e) { console.error('SKIP', dir, e.message); continue; }
  if (!concepts) {
    concepts = m.PRESETS.map(p => ({ id: p.id, name: p.name, cat: p.cat }));
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
        la: +r.seg.lat.toFixed(5), ln: +r.seg.lng.toFixed(5) });
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
