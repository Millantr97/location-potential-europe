/* Shared scoring harness: loads a baked city (city.js + data/segments.js) and the
   pure computation prefix of app.js (everything before the DOM section), so the
   site's exact scoring/revenue logic can run offline in Node. */
const fs = require('fs'), path = require('path');

function appPrefix(repoRoot) {
  const src = fs.readFileSync(path.join(repoRoot, 'app.js'), 'utf8');
  const cut = src.indexOf('/* ---------- concept UI ----------');
  if (cut < 0) throw new Error('concept UI marker not found in app.js');
  return src.slice(0, cut);
}

function loadCity(repoRoot, dir) {
  const window = {};
  const cityFile = path.join(repoRoot, dir, 'city.js');
  const parts = [
    fs.existsSync(cityFile) ? fs.readFileSync(cityFile, 'utf8') : '/* no city.js: app.js default city (London) */',
    fs.readFileSync(path.join(repoRoot, dir, 'data', 'segments.js'), 'utf8'),
    appPrefix(repoRoot),
    '\n;return {CITY, META, SEGMENTS, PRESETS, SCRATCH, normalizeConcept, computeAll, revenueFor, COMPR, REV};'
  ];
  const fn = new Function('window', 'document', parts.join('\n'));
  return fn(window, undefined);
}

module.exports = { loadCity, appPrefix };
