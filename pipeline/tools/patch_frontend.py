"""Patch repo/app.js + repo/report.js for EU cities. All replacements keep UK behaviour as default."""
import io
def patch(path, subs):
    s=open(path,encoding='utf-8').read()
    for old,new in subs:
        assert old in s, f"NOT FOUND in {path}: {old[:90]}"
        assert s.count(old)==1, f"MULTIPLE in {path}: {old[:60]}"
        s=s.replace(old,new)
    open(path,'w',encoding='utf-8').write(s)
    print(path,'patched:',len(subs),'subs')

APP='/home/sandbox/europe/repo/app.js'
patch(APP,[
 ('const money=n=>"£"+Math.round(n).toLocaleString("en-GB");',
  'const CUR=(window.CITY&&CITY.cur)||"£";const money=n=>CUR+Math.round(n).toLocaleString("en-GB");'),
 ('sliderField("Rent tolerance (rateable-value proxy, £/m²/yr)","rent"',
  'sliderField(CITY.eu?"Rent tolerance (typical rent, "+CUR+"/m²/yr)":"Rent tolerance (rateable-value proxy, £/m²/yr)","rent"'),
 ('<span class="lv">Aged 20-39</span>','<span class="lv">${CITY.texts.ageYoung||"Aged 20-39"}</span>'),
 ('<span class="lv">Students (16+)</span>','<span class="lv">${CITY.texts.studentsLbl||"Students (16+)"}</span>'),
 ('<span class="lv">Professional / managerial jobs</span>','<span class="lv">${CITY.texts.profLbl||"Professional / managerial jobs"}</span>'),
 ('<span class="lv">Born outside the UK</span>','<span class="lv">${CITY.texts.bornAbroad||"Born outside the UK"}</span>'),
 ('${s.rent.basis==="SAA"',
  '${s.rent.basis==="modelled"?`<div class="ev-line"><span class="lv">Typical retail rent / m² / yr (city-level MODELLED)${chipFor("mod")}</span><span class="rv">${money(s.rent.retail_rv_m2)}</span></div>\\n      <div class="ev-line"><span class="lv">Typical office rent / m² / yr (city-level MODELLED)${chipFor("mod")}</span><span class="rv">${money(s.rent.office_rv_m2)}</span></div>`:s.rent.basis==="SAA"'),
 ('      <div class="ev-line"><span class="lv">Est. business rates after small-biz relief${chipFor("mod")}</span><span class="rv">${money(estRates(s,concept)/12)}/mo</span></div>',
  '      ${CITY.eu?"":`<div class="ev-line"><span class="lv">Est. business rates after small-biz relief${chipFor("mod")}</span><span class="rv">${money(estRates(s,concept)/12)}/mo</span></div>`}'),
 ('<span class="lv">Rule: borough rateable value x segment-type factor x footfall factor, uplifted to 2026. Rates = unit RV proxy x 49.9p multiplier with Small Business Rate Relief below £15k RV. Get agent quotes before committing.</span>',
  '<span class="lv">${CITY.texts.rentRule||"Rule: borough rateable value x segment-type factor x footfall factor, uplifted to 2026. Rates = unit RV proxy x 49.9p multiplier with Small Business Rate Relief below £15k RV. Get agent quotes before committing."}</span>'),
 ('x your £${concept.ticket} ticket','x your ${CUR}${concept.ticket} ticket'),
 ('<p>The estimated passing rent per m² is MODELLED: borough retail rateable value x a segment-type factor (prime/managed retail 1.35-1.45, high street 1.15, side street 0.95, market 1.0) x a footfall factor (up to +30% for the busiest flows) x 1.08 uplift to 2026. Business rates proxy: unit rateable value x the 49.9p small-business multiplier, with 100% relief under £12,000 RV tapering to £15,000. Always get agent quotes.</p>',
  '${CITY.texts.rentMethod||`<p>The estimated passing rent per m² is MODELLED: borough retail rateable value x a segment-type factor (prime/managed retail 1.35-1.45, high street 1.15, side street 0.95, market 1.0) x a footfall factor (up to +30% for the busiest flows) x 1.08 uplift to 2026. Business rates proxy: unit rateable value x the 49.9p small-business multiplier, with 100% relief under £12,000 RV tapering to £15,000. Always get agent quotes.</p>`}'),
 ('each concept, United Kingdom, rescaled','each concept, ${CITY.country_name||"United Kingdom"}, rescaled'),
 ('const vt=verdictText(r),shareTxt="The best location for my new business is: https://locationpotential.com/"+(CITY.id==="london"?"":CITY.id+"/")+"#expert";',
  'const vt=verdictText(r),shareTxt="The best location for my new business is: "+(CITY.site||"https://locationpotential.com/")+(CITY.id==="london"?"":CITY.id+"/")+"#expert";'),
 ('const basis=(CITY.id==="glasgow"||CITY.id==="edinburgh")?"SAA-derived retail RV proxy":"VOA retail rateable value";',
  'const basis=CITY.eu?"city-level modelled typical rent":((CITY.id==="glasgow"||CITY.id==="edinburgh")?"SAA-derived retail RV proxy":"VOA retail rateable value");'),
])

REP='/home/sandbox/europe/repo/report.js'
patch(REP,[
 ('${(CITY.id==="glasgow"||CITY.id==="edinburgh")?"Scottish Assessors valuation roll":"VOA "+(CITY.texts.voaYear||"2023")}',
  '${CITY.eu?"Modelled city-level rents":((CITY.id==="glasgow"||CITY.id==="edinburgh")?"Scottish Assessors valuation roll":"VOA "+(CITY.texts.voaYear||"2023"))}'),
 ('${kv("Usual residents (Census 2021)",','${kv("Usual residents ("+(CITY.texts.resCensus||"Census 2021")+")",'),
 ('${kv("Aged 20-39",s.lsoa.pct20_39.toFixed(1)+"%")}${kv("Under 20",s.lsoa.pct_under20.toFixed(1)+"%")}',
  '${kv(CITY.texts.ageYoung||"Aged 20-39",s.lsoa.pct20_39.toFixed(1)+"%")}${kv(CITY.texts.ageUnder||"Under 20",s.lsoa.pct_under20.toFixed(1)+"%")}'),
 ('${kv("Students (16+)",s.lsoa.pct_students.toFixed(1)+"%")}${kv("Professional / managerial jobs",s.lsoa.pct_prof.toFixed(1)+"%")}',
  '${kv(CITY.texts.studentsLbl||"Students (16+)",s.lsoa.pct_students.toFixed(1)+"%")}${kv(CITY.texts.profLbl||"Professional / managerial jobs",s.lsoa.pct_prof.toFixed(1)+"%")}'),
 ('${s.lsoa.pct_nonuk!=null?kv("Born outside the UK",s.lsoa.pct_nonuk.toFixed(1)+"%"):""}',
  '${s.lsoa.pct_nonuk!=null?kv(CITY.texts.bornAbroad||"Born outside the UK",s.lsoa.pct_nonuk.toFixed(1)+"%"):""}'),
 ('<div class="rmini">LSOA ≈ 1,500 residents - it describes residents, not the people walking this street. Census 2021 via Nomis.</div>',
  '<div class="rmini">${CITY.texts.resRmini||"LSOA ≈ 1,500 residents - it describes residents, not the people walking this street. Census 2021 via Nomis."}</div>'),
 ('${s.rent.basis==="SAA"',
  '${s.rent.basis==="modelled"?kv("Typical retail rent / m² / yr (city-level MODELLED)",money(s.rent.retail_rv_m2),"mod")+kv("Typical office rent / m² / yr (city-level MODELLED)",money(s.rent.office_rv_m2),"mod"):s.rent.basis==="SAA"'),
 ('      ${kv("Est. business rates after small-biz relief",money(estRates(s,c)/12)+"/mo","mod")}',
  '      ${CITY.eu?"":kv("Est. business rates after small-biz relief",money(estRates(s,c)/12)+"/mo","mod")}'),
 ('<div class="rmini">Rule: borough rateable value x segment-type factor x footfall factor, uplifted to 2026. Rates = unit RV proxy x 49.9p multiplier with Small Business Rate Relief below £15k RV. Get agent quotes before committing.</div>',
  '<div class="rmini">${CITY.texts.rentRule||"Rule: borough rateable value x segment-type factor x footfall factor, uplifted to 2026. Rates = unit RV proxy x 49.9p multiplier with Small Business Rate Relief below £15k RV. Get agent quotes before committing."}</div>'),
 ('describes the surrounding statistical area - Census LSOA, Met Police, VOA borough.',
  'describes the surrounding statistical area - ${CITY.eu?"Census 2021 1 km grid (Eurostat), city-level modelled rents":"Census LSOA, Met Police, VOA borough"}.'),
 ('<span class="rv">Census 2021 LSOA via Nomis</span>','<span class="rv">${CITY.eu?"Census 2021 1 km grid (Eurostat)":"Census 2021 LSOA via Nomis"}</span>'),
 ('<div class="rkv2"><span class="rl">Rateable values ${chip("ctx")}</span><span class="rv">VOA business floorspace, Mar 2023</span></div>',
  '<div class="rkv2"><span class="rl">Rents ${chip("mod")}</span><span class="rv">${CITY.eu?"Typical city-level retail + office rents (MODELLED)":"VOA business floorspace, Mar 2023"}</span></div>'),
 ('LSOA describes residents not visitors;','${CITY.eu?"the census grid cell describes residents not visitors":"LSOA describes residents not visitors"};'),
 ('<a href="https://locationpotential.com/#expert">','<a href="${CITY.site||"https://locationpotential.com/"}#expert">'),
 ('<div class="rclose-url">locationpotential.com ·','<div class="rclose-url">${CITY.siteHost||"locationpotential.com"} ·'),
])
print('OK')
