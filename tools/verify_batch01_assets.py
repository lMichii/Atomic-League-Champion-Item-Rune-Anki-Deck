"""Decode genuine production images/GIF frames and record source-stream diagnostics."""
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from lol_anki.io import read_json,write_json
from PIL import Image

records=[]
for asset in read_json(ROOT/'data/sources/production.json')['batch01_media_provenance']:
    path=ROOT/'data/batch01'/asset['path']
    record={'path':asset['path'],'sha256':asset['sha256']}
    if path.suffix in ('.gif','.png','.jpg'):
        with Image.open(path) as image:
            record['size']=list(image.size)
            frames=getattr(image,'n_frames',1)
            for n in range(frames): image.seek(n); image.load()
            record['decoded_frames']=frames
            record['status']='decoded'
    else:
        probe=subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=codec_name,width,height','-of','json',str(path)],capture_output=True,text=True)
        if probe.returncode: raise RuntimeError(probe.stderr)
        record['video_stream']=__import__('json').loads(probe.stdout)['streams'][0]
        record['probe_diagnostic']=probe.stderr.strip() or None
        record['status']='video_stream_identified'
    records.append(record)
report={'files':len(records),'image_files_fully_decoded':sum('decoded_frames' in r for r in records),
        'gif_files_fully_decoded':sum(r['path'].endswith('.gif') for r in records),
        'source_video_files':sum('video_stream' in r for r in records),'records':records,
        'audio_note':'Some original WebMs emit Opus header diagnostics. GIFs contain video only; every emitted GIF frame was decoded successfully.'}
write_json(ROOT/'data/batch01/qa/asset_validation.json',report)
print({k:v for k,v in report.items() if k!='records'})
