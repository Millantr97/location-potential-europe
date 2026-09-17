import sys, os, json, csv, re
sys.path.insert(0,'/home/sandbox/europe/work')
from cities_eu import CITIES_EU
from pyproj import Transformer
tr=Transformer.from_crs(3035,4326,always_xy=True)
CSV='/home/sandbox/europe/dl/census_grid/Eurostat_Census-GRID_2021_V3/ESTAT_Census_2021_V3.csv'
OUT='/home/sandbox/europe/work/census'
os.makedirs(OUT,exist_ok=True)
M=0.03  # bbox margin in degrees
boxes={cid:(c['bbox'][0]-M,c['bbox'][1]-M,c['bbox'][2]+M,c['bbox'][3]+M) for cid,c in CITIES_EU.items()}
out={cid:[] for cid in CITIES_EU}
pat=re.compile(r'CRS3035RES1000mN(\d+)E(\d+)')
rows=0; kept=0
with open(CSV) as f:
    rd=csv.reader(f); hdr=next(rd)
    # GRD_ID,T,M,F,Y_LT15,Y_1564,Y_GE65,EMP,NAT,EU_OTH,OTH,SAME,CHG_IN,CHG_OUT,LAND_SURFACE,POPULATED,CNTR_ID
    buf=[]; bufc=[]
    for r in rd:
        m=pat.match(r[0])
        if not m: continue
        buf.append((int(m.group(2)),int(m.group(1)),r))
        if len(buf)>=200000:
            xs=[b[0] for b in buf]; ys=[b[1] for b in buf]
            lons,lats=tr.transform(xs,ys)
            for (x,y,r2),lo,la in zip(buf,lons,lats):
                rows+=1
                for cid,(b0,b1,b2,b3) in boxes.items():
                    if b0<=la<=b2 and b1<=lo<=b3:
                        t=int(r2[1])
                        if t<=0: continue
                        out[cid].append([round(la,5),round(lo,5),t,int(r2[4]),int(r2[5]),int(r2[6]),int(r2[7]),int(r2[8]),int(r2[9]),int(r2[10])])
                        kept+=1
            buf=[]
    if buf:
        xs=[b[0] for b in buf]; ys=[b[1] for b in buf]
        lons,lats=tr.transform(xs,ys)
        for (x,y,r2),lo,la in zip(buf,lons,lats):
            rows+=1
            for cid,(b0,b1,b2,b3) in boxes.items():
                if b0<=la<=b2 and b1<=lo<=b3:
                    t=int(r2[1])
                    if t<=0: continue
                    out[cid].append([round(la,5),round(lo,5),t,int(r2[4]),int(r2[5]),int(r2[6]),int(r2[7]),int(r2[8]),int(r2[9]),int(r2[10])])
                    kept+=1
print('rows scanned:',rows,'cells kept:',kept)
counts={}
for cid,lst in out.items():
    counts[cid]=len(lst)
    if lst: json.dump(lst,open(f'{OUT}/{cid}.json','w'))
print(json.dumps(counts))
