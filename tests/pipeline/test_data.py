import csv, hashlib, json, sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'pipeline'))
from build import number, sum_columns, build

@pytest.fixture(scope='module')
def data(): return build()

def test_complete_and_exact_population(data):
 rows=list(csv.DictReader(open(ROOT/'data/raw/f1015.csv',encoding='utf-8-sig')))
 source={r['C04160V04929']:int(r['VALUE']) for r in rows if r['STATISTIC']=='F1015C01' and r['Sex']=='Both sexes' and r['Census Year']=='2022'}
 towns={t['id']:t['population'] for t in data['towns']}
 excluded={x['id'] for x in json.loads((ROOT/'data/exclusions.json').read_text())}
 assert set(source)==set(towns)|excluded
 assert all(pop==source[ident] for ident,pop in towns.items())
 assert json.loads((ROOT/'data/unmatched.json').read_text())==[]

def test_nonnegative_and_percentages(data):
 def check(value):
  if isinstance(value,dict):
   for v in value.values(): check(v)
  elif isinstance(value,list):
   for v in value: check(v)
  elif isinstance(value,(int,float)): assert value>=0
 check(data)
 for t in data['towns']:
  assert t['pctOfState']==pytest.approx(t['population']/data['statePopulation']*100)
  for s in t['stats'].values():
   if s['value'] is not None and s['denominator']:
    assert 0<=s['pct']<=100
    assert abs(s['pct']-s['value']/s['denominator']*100)<.05
   else: assert s['pct'] is None

def test_ranks_and_unique_ids(data):
 towns=data['towns']; assert len({t['id'] for t in towns})==len(towns)
 ranks={}
 for t in towns:
  assert t['rank']==1+sum(o['population']>t['population'] for o in towns)
  if t['rank'] in ranks: assert ranks[t['rank']]==t['population']
  ranks[t['rank']]=t['population']

def test_full_partitions(data):
 checks=json.loads((ROOT/'data/category_checks.json').read_text())
 assert not checks['discrepancies'], 'CSO category discrepancies must be investigated and documented'
 rows=csv.DictReader(open(ROOT/'data/raw/saps.csv',encoding='cp1252'))
 for row in rows:
  for columns,total in checks['partitions'].values():
   values=sum_columns(row,columns); base=number(row[total])
   if values is not None and base is not None: assert values==base

def test_mapping_coverage_and_glossary(data):
 required={'total','male','female','single','married','separated','divorced','widowed','irishLanguage','irish','nonIrish','catholic','noReligion','otherReligion','veryGoodHealth','carers','dailySmokers','disability','atWork','unemployed','retired','students','remoteWork','age0to4','age20to24','age50to54','age75plus','marriedNoChildren','marriedWithChildren','cohabiting','oneParent','singleOccupant','mortgage','ownedOutright','rentedPrivate','rentedLocalAuthority','rentedVoluntary','vacant','holidayHomes','bedrooms3','bedrooms5plus','publicMains','privateWater','oil','gas','electric','coal','noRenewable','noSmokeAlarm','broadband','noCar','cars3plus'}
 assert {f['key'] for f in data['fields']}==required
 for f in data['fields']:
  assert f['source'] is None or f['columns'] and f['denominator'] and f['glossary']
  if f['source'] is None:
   assert f['note']
   assert all(t['stats'][f['key']]['value'] is None for t in data['towns'])

def test_nulls_are_not_zero():
 for cell in [None,'','..',':','-','*','...']: assert number(cell) is None
 assert number('0')==0
 assert sum_columns({'a':'3','b':''},['a','b']) is None
 with pytest.raises(ValueError): number('-1')
 with pytest.raises(ValueError): number('unexpected')

def test_reproducible(data):
 target=ROOT/'web/data/towns.json'; before=target.read_bytes(); build(); assert before==target.read_bytes()

def test_sanity_log(data):
 from sanity import report
 report(); assert (ROOT/'data/BALLYCOTTON_SANITY.md').exists()
