"""Newspaper comparisons are diagnostics only; never used to populate the app."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXPECTED={'total':544,'male':273,'female':271,'married':249,'single':239,'widowed':27,'divorced':16,'separated':13,'irishLanguage':205,'veryGoodHealth':295,'carers':34,'dailySmokers':59,'disability':101,'irish':462,'nonIrish':82,'catholic':397,'noReligion':92,'otherReligion':26,'atWork':253,'remoteWork':33,'unemployed':6,'retired':101,'students':26,'age0to4':39,'age20to24':27,'age50to54':46,'age75plus':49,'broadband':166,'publicMains':204,'privateWater':3,'cars3plus':23,'noCar':22,'mortgage':44,'ownedOutright':119,'holidayHomes':220,'vacant':21,'bedrooms5plus':61,'bedrooms3':207,'noRenewable':128,'noSmokeAlarm':13,'marriedNoChildren':51,'marriedWithChildren':54,'cohabiting':10,'oneParent':10,'singleOccupant':60,'coal':18,'oil':141,'gas':8,'electric':18}
def report():
 data=json.loads((ROOT/'web/data/towns.json').read_text())
 towns=[t for t in data['towns'] if t['name']=='Ballycotton' and 'Cork' in t['county']]
 lines=['# Ballycotton sanity log','','Newspaper values are checks only, never application inputs. Threshold: more than 10%.','']
 if not towns: lines.append('Ballycotton not found.')
 else:
  town=towns[0]
  lines+=['| Field | Newspaper | CSO | Result |','| --- | --- | --- | --- |']
  for key,expected in EXPECTED.items():
   value=town['stats'][key]['value']; result='n/a: not published with requested meaning' if value is None else ('DIFF >10%' if abs(value-expected)/expected>.1 else 'within 10%')
   lines.append(f'| {key} | {expected} | {value if value is not None else "n/a"} | {result} |')
  rented=sum(town['stats'][k]['value'] for k in ['rentedPrivate','rentedLocalAuthority','rentedVoluntary'])
  lines.append(f'| rented (sum of published rental types) | 28 | {rented} | {"DIFF >10%" if abs(rented-28)/28>.1 else "within 10%"} |')
 (ROOT/'data/BALLYCOTTON_SANITY.md').write_text('\n'.join(lines)+'\n')
 print('\n'.join(lines))
if __name__=='__main__': report()
