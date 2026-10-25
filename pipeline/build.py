"""Rebuild static data strictly from checksummed official CSO files."""
from pathlib import Path
import csv, hashlib, json, re
from glossary import read_glossary
ROOT=Path(__file__).resolve().parents[1]

def number(cell):
 if cell is None or cell.strip() in ('','..',':','-','*','...'): return None
 try:
  value=int(cell)
 except ValueError as exc: raise ValueError(f'Unexpected count {cell!r}') from exc
 if value<0: raise ValueError('Negative count')
 return value

def sum_columns(row,columns):
 values=[number(row[c]) for c in columns]
 return sum(values) if all(v is not None for v in values) else None

def read_csv(name,encoding='utf-8-sig'):
 with (ROOT/'data/raw'/name).open(encoding=encoding,newline='') as f: return list(csv.DictReader(f))

def build():
 manifest=json.loads((ROOT/'data/raw/sources.json').read_text())
 for entry in manifest:
  if hashlib.sha256((ROOT/'data/raw'/entry['file']).read_bytes()).hexdigest()!=entry['sha256']:
   raise ValueError(f"Checksum mismatch: {entry['file']}; run pipeline/fetch.py")
 glossary=read_glossary(ROOT/'data/raw/glossary.xlsx')
 mapping=json.loads((ROOT/'data/field_map.json').read_text())['fields']
 for field in mapping:
  for c,desc in zip(field['columns'] or [],field['glossary'],strict=True):
   if glossary[c]!=desc: raise ValueError(f'Glossary changed for {c}; mapping review required')
  if field['denominator'] and glossary[field['denominator']]!=field['denominatorGlossary']:
   raise ValueError('Denominator glossary changed')
 saps=read_csv('saps.csv','cp1252'); by_guid={r['GUID'].lower():r for r in saps}
 if len(saps)!=len(by_guid): raise ValueError('Duplicate SAPS GUID')
 f1015=[r for r in read_csv('f1015.csv') if r['STATISTIC']=='F1015C01' and r['Sex']=='Both sexes' and r['Census Year']=='2022']
 national=[r for r in read_csv('fy001.csv') if r['STATISTIC']=='FY001C01' and r['CensusYear']=='2022' and r['County']=='State' and r['Sex']=='Both sexes']
 if len(national)!=1: raise ValueError('Expected exactly one official national population')
 state=number(national[0]['VALUE'])
 if not state: raise ValueError('Missing State population')
 towns=[]; exclusions=[]; unmatched=[]
 for r in f1015:
  ident=r['C04160V04929']; label=r['List of Towns']
  if ident=='IE0':
   exclusions.append(dict(id=ident,label=label,reason='Built-up-area aggregate, not a town; not the national population.'))
   continue
  row=by_guid.get(ident.lower())
  if row is None: unmatched.append(dict(id=ident,label=label)); continue
  split=label.rsplit(', ',1)
  if len(split)!=2: raise ValueError(f'Cannot extract official county label: {label}')
  name,county=split; county=re.sub(r'^Co ', 'Co. ', county); pop=number(r['VALUE'])
  if pop!=number(row['T1_1AGETT']): raise ValueError(f'Population mismatch: {label}')
  stats={}
  for field in mapping:
   value=sum_columns(row,field['columns']) if field['source'] else None
   denominator=number(row[field['denominator']]) if field['denominator'] else None
   if value is not None and denominator is not None and value>denominator: raise ValueError(f'Count exceeds base: {label} {field["key"]}')
   stats[field['key']]=dict(value=value,denominator=denominator,pct=value/denominator*100 if value is not None and denominator else None)
  towns.append(dict(id=ident,geoCode=row['GEOGID'],name=name,county=county,label=name+', '+county,population=pop,pctOfState=pop/state*100,stats=stats))
 (ROOT/'data/unmatched.json').write_text(json.dumps(unmatched,ensure_ascii=False,indent=2)+'\n')
 (ROOT/'data/exclusions.json').write_text(json.dumps(exclusions,ensure_ascii=False,indent=2)+'\n')
 if unmatched: raise ValueError(f'{len(unmatched)} towns unmatched; see data/unmatched.json')
 populations=sorted([t['population'] for t in towns],reverse=True)
 for t in towns: t['rank']=populations.index(t['population'])+1
 # Full source partitions: include not-stated and every source category, never inferred residuals.
 partitions={
 'sex':(['T1_1AGETM','T1_1AGETF'],'T1_1AGETT'),
 'marital':(['T1_2'+c+'T' for c in ['SGL','MAR','SEP','DIV','WID']],'T1_2T'),
 'religion':(['T2_4'+c for c in ['CA','OR','NR','NS']],'T2_4T'),
 'citizenship':(['T2_1'+c for c in ['IEC','UKC','PLC','INC','EUC','RWC','NSC']],'T2_1TC'),
 'irishLanguage':(['T3_1YES','T3_1NO','T3_1NS'],'T3_1T'),
 }
 # Identify complete categorical partitions from exact table prefixes in the glossary.
 for prefix,total in [('T6_3_','T6_3_TH'),('T6_5_','T6_5_T'),('T6_6_','T6_6_T'),('T6_8_','T6_8_T'),('T6_9_','T6_9_TH'),('T6_10_','T6_10_T'),('T6_11_','T6_11_T'),('T8_1_','T8_1_TT'),('T12_3_','T12_3_TT'),('T12_4_','T12_4_T'),('T15_1_','T15_1_TC'),('T15_2_','T15_2_T')]:
  cols=[c for c in glossary if c.startswith(prefix) and c!=total]
  if prefix in ['T6_3_','T6_9_']: cols=[c for c in cols if c.endswith('H')]
  if prefix in ['T8_1_','T12_3_']: cols=[c for c in cols if c.endswith('T')]
  partitions[prefix]=(cols,total)
 discrepancies=[]
 for t in towns:
  row=by_guid[t['id'].lower()]
  for category,(cols,total) in partitions.items():
   value=sum_columns(row,cols); denominator=number(row[total])
   if value is not None and denominator is not None and value!=denominator:
    discrepancies.append(dict(id=t['id'],category=category,sum=value,denominator=denominator,difference=value-denominator))
 (ROOT/'data/category_checks.json').write_text(json.dumps(dict(partitions=partitions,discrepancies=discrepancies),indent=2)+'\n')
 out=dict(censusYear=2022,statePopulation=state,downloadDate=max(e['downloaded'] for e in manifest),sources=manifest,fields=mapping,towns=towns)
 target=ROOT/'web/data/towns.json'; target.parent.mkdir(exist_ok=True,parents=True)
 target.write_text(json.dumps(out,ensure_ascii=False,separators=(',',':'))+'\n')
 print(f'Built {len(towns)} towns; State population {state:,}; unmatched {len(unmatched)}; source partition discrepancies {len(discrepancies)}')
 return out
if __name__=='__main__': build()
