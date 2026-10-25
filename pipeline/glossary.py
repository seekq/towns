"""Read the official XLSX without requiring Excel or third-party libraries."""
import zipfile, xml.etree.ElementTree as ET

def read_glossary(path):
 ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
 with zipfile.ZipFile(path) as z:
  strings=[''.join(si.itertext()) for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',ns)]
  result={}
  for row in ET.fromstring(z.read('xl/worksheets/sheet1.xml')).findall('.//m:row',ns):
   cells=[]
   for c in row.findall('m:c',ns):
    v=c.find('m:v',ns)
    cells.append(strings[int(v.text)] if v is not None and c.get('t')=='s' else (v.text if v is not None else ''))
   if len(cells)>=4 and cells[2].startswith('T'):
    result[cells[2]]={'description':cells[3],'table':cells[1]}
  return result
