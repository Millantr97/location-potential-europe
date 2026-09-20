#!/usr/bin/env python3
"""Join official ACS 2024 five-year tract context to TIGER centroids."""
import geopandas as gpd,pandas as pd,json,sys,functools
state=sys.argv[1]; counties=sys.argv[2].split(','); out=sys.argv[3]; base=sys.argv[4] if len(sys.argv)>4 else '/tmp/usacs'; tractzip=sys.argv[5] if len(sys.argv)>5 else f'{base}/nytract.zip'
def tab(n):
 x=pd.read_csv(f'{base}/{n}.dat',sep='|',dtype={'GEO_ID':str});return x[x.GEO_ID.str.startswith('1400000US'+state)].set_index('GEO_ID')
x=functools.reduce(lambda a,b:a.join(b,how='outer'),[tab(t) for t in ('b01003','b09001','b23025','b05002','b15003')])
g=gpd.read_file('zip://'+tractzip).to_crs(4326);g=g[g.COUNTYFP.isin(counties)].copy();g['GEO_ID']='1400000US'+g.GEOID
c=g.geometry.representative_point(); outrows=[]
for _,r in g.iterrows():
 q=x.loc[r.GEO_ID] if r.GEO_ID in x.index else None
 if q is None:continue
 pop=max(0,int(q.B01003_E001)); under=max(0,int(q.B09001_E001)); emp=max(0,int(q.B23025_E004)); foreign=max(0,int(q.B05002_E013)); edu=sum(max(0,int(q.get(f'B15003_E{i:03d}',0))) for i in range(22,26)); adult=max(1,int(q.B15003_E001));
 pt=r.geometry.representative_point();outrows.append({'geoid':r.GEOID,'lat':round(pt.y,6),'lng':round(pt.x,6),'residents':pop,'under18':under,'employed':emp,'foreign_born':foreign,'degree_plus':edu,'degree_den':adult})
json.dump(outrows,open(out,'w'),separators=(',',':'));print(out,len(outrows),'tracts',sum(r['residents'] for r in outrows),'residents')
