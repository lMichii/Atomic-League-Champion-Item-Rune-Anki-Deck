"""Generate review contact sheets from real downloaded clips; never deck placeholders."""
import importlib.util
from pathlib import Path
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from lol_anki.media import gif
from lol_anki.io import read_json, write_json


def main():
    root = ROOT/'build/batch01/downloads'
    output = ROOT/'build/batch01/contact_sheets'; output.mkdir(parents=True,exist_ok=True)
    from PIL import Image, ImageDraw
    for name in ('caitlyn','ashe','jinx','leona','lux','morgana'):
        rows=[]
        for slot in 'pqwer':
            source = root/f'cache/webm/{name}_{slot}.webm'
            if not source.exists():
                continue
            probe=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(source)],capture_output=True,text=True,check=True)
            duration=float(probe.stdout.strip())
            strip=Image.new('RGB',(4*360,230),'#101317'); d=ImageDraw.Draw(strip)
            for i,fraction in enumerate((0.1,0.35,0.6,0.85)):
                time=duration*fraction
                frame=output/f'{name}_{slot}_{i}.png'
                subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',str(time),'-i',str(source),'-frames:v','1','-vf','scale=360:-1',str(frame)],check=True)
                with Image.open(frame) as image:
                    strip.paste(image,(i*360,25))
                d.text((i*360+5,5),f'{name.upper()} {slot.upper()}  {time:.2f}s',fill='white')
            rows.append(strip)
        sheet=Image.new('RGB',(1440,len(rows)*230),'#101317')
        for i,row in enumerate(rows):
            sheet.paste(row,(0,i*230))
        sheet.save(output/f'{name}.jpg',quality=92)
        print(output/f'{name}.jpg')


if __name__=='__main__':
    main()
