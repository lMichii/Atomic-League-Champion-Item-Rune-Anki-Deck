"""Fetch optional real passive clips through the existing fetcher/cache."""
import importlib.util
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from lol_anki.io import read_json,write_json
path=ROOT/'LoL_Anki_Riot_Medien_Fetcher/lol_anki_media_fetcher/media_fetcher.py'
spec=importlib.util.spec_from_file_location('legacy_fetcher',path)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
root=ROOT/'build/batch01/downloads'
client=m.Client(root/'cache',offline='--offline' in sys.argv,timeout=15)
records=read_json(root/'manifest.json')['ability_assets']
status=[]
for record in records:
    if record['slot']!='P': continue
    name=record['champion'].lower()
    source=root/f'cache/webm/{name}_p.webm'
    ok,note=client.get_asset(record['video_source_url'],source,('webm',))
    if ok:
        ok,note=m.convert_video(source,root/f'media/videos/{name}_p.mp4','mp4')
    status.append({'champion':record['champion'],'url':record['video_source_url'],'downloaded':ok,'note':note})
    print(status[-1])
write_json(ROOT/'build/batch01/passive_downloads.json',status)
