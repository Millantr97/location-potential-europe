import json,re,requests
URL='https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/urb_cpop1?lang=en&indic_ur=DE1001V&sinceTimePeriod=2018'
j=requests.get(URL,timeout=60).json(); nt=j['size'][-1]; d=j['dimension']['cities']['category']; vals=j['value']; times=list(j['dimension']['time']['category']['index'])
rows=[]
for code,pos in d['index'].items():
 if not re.match(r'^[A-Z]{2}\d{3}C$',code): continue
 vv=[(int(y),vals.get(str(pos*nt+t))) for t,y in enumerate(times) if vals.get(str(pos*nt+t)) is not None]
 if vv and vv[-1][1]>=250000: rows.append(dict(code=code,name=d['label'].get(code,''),year=vv[-1][0],population=vv[-1][1]))
rows.sort(key=lambda x:(x['code'][:2],-x['population']))
json.dump({'source':URL,'threshold':250000,'count':len(rows),'cities':rows},open('work/eurostat250.json','w'),ensure_ascii=False,indent=2);print(len(rows))
