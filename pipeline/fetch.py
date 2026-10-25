"""Download official inputs; never substitute samples. Python 3.11+."""
from pathlib import Path
import datetime, hashlib, json, urllib.request
ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
 'saps.csv': 'https://www.cso.ie/en/media/csoie/census/census2022/SAPS_2022_BUA_270923.csv',
 'glossary.xlsx': 'https://www.cso.ie/en/media/csoie/census/census2022/Glossary_Saps_2022_REVISED_21102024.xlsx',
 'f1015.csv': 'https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/F1015/CSV/1.0/en',
 'fy001.csv': 'https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/FY001/CSV/1.0/en',
}
def fetch():
 raw = ROOT / 'data/raw'; raw.mkdir(parents=True, exist_ok=True)
 # Download and validate all files before replacing any tracked input.
 downloads = {}
 for name, url in SOURCES.items():
  try:
   with urllib.request.urlopen(url, timeout=90) as response: body = response.read()
   if not body or body.lstrip().startswith((b'<', b'{')): raise ValueError('Unexpected response format')
   downloads[name] = body
  except Exception as exc: raise SystemExit(f'CSO download failed: {url}: {exc}') from exc
 manifest = []
 for name, body in downloads.items():
  (raw/name).write_bytes(body)
  manifest.append(dict(file=name,url=SOURCES[name],downloaded=datetime.datetime.now(datetime.timezone.utc).isoformat(),sha256=hashlib.sha256(body).hexdigest()))
 (raw/'sources.json').write_text(json.dumps(manifest,indent=2)+'\n')
 (raw/'SOURCES.md').write_text('# Official CSO downloads\n\n'+'\n\n'.join(f"## {s['file']}\n{s['url']}\n\nDownloaded: {s['downloaded']}\n\nSHA-256: `{s['sha256']}`" for s in manifest)+'\n')
if __name__ == '__main__': fetch()
