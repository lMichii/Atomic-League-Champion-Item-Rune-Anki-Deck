#!/usr/bin/env python3
"""Create short looping GIFs from the MP4 source clips in cards.csv.
Requires FFmpeg in PATH; safe to run repeatedly.
"""
import csv, subprocess, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parent
if not shutil.which('ffmpeg'):
    raise SystemExit('FFmpeg fehlt im PATH. Existing GIFs remain usable for deck generation.')
rows=list(csv.DictReader((ROOT/'cards.csv').open(encoding='utf-8-sig', newline='')))
count=0
for r in rows:
    if r['media_type']!='gif' or not r.get('source_video_path'): continue
    src=ROOT/r['source_video_path']; dest=ROOT/r['media_path']; dest.parent.mkdir(parents=True,exist_ok=True)
    if not src.is_file(): raise FileNotFoundError(src)
    if dest.exists() and dest.stat().st_mtime>=src.stat().st_mtime: continue
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(src),'-filter_complex',
      '[0:v]fps=8,scale=420:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=96:stats_mode=diff[p];[s1][p]paletteuse=dither=bayer:bayer_scale=4',
      '-loop','0',str(dest)]
    subprocess.run(cmd,check=True);count+=1
print(f'{count} GIFs erzeugt/aktualisiert.')
