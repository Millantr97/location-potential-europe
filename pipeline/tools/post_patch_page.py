"""Post-build page patches for EU city pages. Usage: <cid> [<cid>...]"""
import sys, pathlib
sys.path.insert(0,'/home/sandbox/europe/work')
from cities_eu import CITIES_EU
BUDGET = {
 "EUR": ["Under \u20ac60,000","\u20ac60,000-\u20ac120,000","\u20ac120,000-\u20ac300,000","\u20ac300,000-\u20ac600,000","\u20ac600,000+"],
 "PLN": ["Under z\u0142250,000","z\u0142250,000-z\u0142500,000","z\u0142500,000-z\u01421,250,000","z\u01421,250,000-z\u01422,500,000","z\u01422,500,000+"],
 "CZK": ["Under K\u010d1,500,000","K\u010d1,500,000-K\u010d3,000,000","K\u010d3,000,000-K\u010d7,500,000","K\u010d7,500,000-K\u010d15,000,000","K\u010d15,000,000+"],
 "SEK": ["Under 650,000 kr","650,000-1,300,000 kr","1,300,000-3,200,000 kr","3,200,000-6,500,000 kr","6,500,000 kr+"],
 "DKK": ["Under 450,000 kr","450,000-900,000 kr","900,000-2,200,000 kr","2,200,000-4,400,000 kr","4,400,000 kr+"],
 "NOK": ["Under 700,000 kr","700,000-1,400,000 kr","1,400,000-3,500,000 kr","3,500,000-7,000,000 kr","7,000,000 kr+"],
 "HUF": ["Under 24M Ft","24M-48M Ft","48M-120M Ft","120M-240M Ft","240M Ft+"],
 "RON": ["Under 300,000 lei","300,000-600,000 lei","600,000-1,500,000 lei","1,500,000-3,000,000 lei","3,000,000 lei+"],
 "BGN": ["Under 120,000 \u043b\u0432","120,000-240,000 \u043b\u0432","240,000-600,000 \u043b\u0432","600,000-1,200,000 \u043b\u0432","1,200,000 \u043b\u0432+"],
}
OLD = ["Under \u00a350,000","\u00a350,000-\u00a3100,000","\u00a3100,000-\u00a3250,000","\u00a3250,000-\u00a3500,000","\u00a3500,000+"]
RENT = {
 "EUR": ('value="600" min="50" step="10"', '\u20ac/m\u00b2'),
 "PLN": ('value="3000" min="250" step="50"', 'z\u0142/m\u00b2'),
 "CZK": ('value="17500" min="1500" step="250"', 'K\u010d/m\u00b2'),
 "SEK": ('value="7800" min="650" step="100"', 'kr/m\u00b2'),
 "DKK": ('value="5200" min="450" step="50"', 'kr/m\u00b2'),
 "NOK": ('value="8300" min="700" step="100"', 'kr/m\u00b2'),
 "HUF": ('value="280000" min="20000" step="5000"', 'Ft/m\u00b2'),
 "RON": ('value="3500" min="250" step="50"', 'lei/m\u00b2'),
 "BGN": ('value="1400" min="100" step="25"', '\u043b\u0432/m\u00b2'),
}
CCY = {'\u20ac':'EUR','z\u0142':'PLN','K\u010d':'CZK','Ft':'HUF','lei':'RON','\u043b\u0432':'BGN','\u00a3':'GBP'}
for cid in sys.argv[1:]:
    C=CITIES_EU[cid]; name=C['name']
    ccy = CCY.get(C['cur']) or {'SE':'SEK','DK':'DKK','NO':'NOK'}.get(C['country'],'EUR')
    p = pathlib.Path(f'/home/sandbox/europe/repo/{cid}/index.html')
    s = p.read_text()
    s = s.replace('Street-level site selection · 9 UK cities · this page: London', f'Street-level site selection · {name}, {C["country_name"]}')
    s = s.replace('href="styles.css?v=32"','href="../styles.css?v=32"')
    s = s.replace('src="extras.js?v=21"','src="../extras.js?v=21"')
    s = s.replace('href="assets/favicon.svg"','href="../assets/favicon.svg"')
    s = s.replace('Google Trends, UK, 2021-2026', f"Google Trends, {C['cc']}, 2021-2026")
    s = s.replace('https://locationpotential.com/assets/og.png','https://millantr97.github.io/location-potential-europe/assets/og.png')
    s = s.replace('"url":"https://locationpotential.com/"','"url":"https://millantr97.github.io/location-potential-europe/"')
    s = s.replace('Street-level site selection across 9 UK cities: real station flows, recorded competition, residents, rents and modelled monthly revenue, honestly labelled.',
                  f'Street-level site selection in {name}: station flows, recorded competition, residents, rents and modelled monthly revenue, honestly labelled.')
    s = s.replace('"description":"Street-level site selection and modelled revenue for new business locations across 9 UK cities."',
                  f'"description":"Street-level site selection and modelled revenue for new business locations in {name}, honestly labelled."')
    for o,n in zip(OLD, BUDGET[ccy]): s = s.replace(o,n)
    attrs, sym = RENT[ccy]
    s = s.replace('<input id="inv-rent" class="prem-input" type="number" value="600" min="50" step="10"><i>\u00a3/m\u00b2</i>',
                  f'<input id="inv-rent" class="prem-input" type="number" {attrs}><i>{sym}</i>')
    p.write_text(s)
    assert 'locationpotential.com' not in s and '\u00a3' not in s and '9 UK cities' not in s and 'Google Trends, UK' not in s, cid
    print('patched', cid, ccy)
