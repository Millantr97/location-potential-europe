#!/usr/bin/env python3
"""Fetch ACS 2024 five-year tract context from the official Census API."""
import json,urllib.request,sys
# population; under 18; working age 18-64; employed; foreign-born; bachelor's+
V='NAME,B01003_001E,B09001_001E,B23025_004E,B23025_005E,B05002_013E,B15003_022E,B15003_023E,B15003_024E,B15003_025E'
def fetch(state,county,out):
 u=f'https://api.census.gov/data/2024/acs/acs5?get={V}&for=tract:*&in=state:{state}%20county:{county}'
 # Environments without a Census API key can use the official table-based files below.
 # https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/
 req=urllib.request.Request(u,headers={'User-Agent':'LocationPotential/1.0 public-data research'})
 rows=json.load(urllib.request.urlopen(req,timeout=60)); hdr=rows[0]
 json.dump([dict(zip(hdr,r)) for r in rows[1:]],open(out,'w'),separators=(',',':'))
 print(out,len(rows)-1,'tracts',u)
if __name__=='__main__':fetch(*sys.argv[1:])
