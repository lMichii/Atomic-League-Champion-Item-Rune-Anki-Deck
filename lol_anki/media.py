"""Content-based, resumable v4 GIF processing. Writes only proposed build assets."""
import shutil
import subprocess
import tempfile
from pathlib import Path
from .cache import Cache
from .io import digest, read_json, write_json

V4_FILTER = '[0:v]fps=8,scale=420:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=96:stats_mode=diff[p];[s1][p]paletteuse=dither=bayer:bayer_scale=4'


def gif_info(blob):
    """Parse GIF blocks (not byte-pattern counts) to check animation/loop behavior."""
    Cache.validate(blob,'gif')
    if len(blob)<13:
        raise ValueError('Truncated GIF header')
    pos = 13 + (3 * 2**((blob[10]&7)+1) if blob[10]&128 else 0)
    frames, loop = 0, None
    def blocks(offset):
        values = []
        while True:
            size = blob[offset]; offset += 1
            if not size:
                return offset,b''.join(values)
            values.append(blob[offset:offset+size]); offset += size
            if offset>len(blob):
                raise ValueError('Truncated GIF data block')
    try:
        while pos<len(blob):
            marker = blob[pos]; pos += 1
            if marker==0x3b:
                return {'frames':frames,'loop':loop}
            if marker==0x21:
                label = blob[pos]; pos += 1
                pos,data = blocks(pos)
                if label==0xff and data.startswith(b'NETSCAPE2.0\x01') and len(data)>=14:
                    loop = int.from_bytes(data[12:14],'little')
            elif marker==0x2c:
                packed = blob[pos+8]; pos += 9
                if packed&128:
                    pos += 3*2**((packed&7)+1)
                pos += 1  # LZW minimum code size
                pos,_ = blocks(pos)
                frames += 1
            else:
                raise ValueError('Invalid GIF block marker')
    except IndexError as ex:
        raise ValueError('Truncated GIF') from ex
    raise ValueError('GIF trailer missing')


def gif(source, target, ffmpeg='ffmpeg'):
    """Source, filter, and FFmpeg version are part of the conversion cache key."""
    source, target = Path(source), Path(target)
    binary = shutil.which(ffmpeg)
    if not binary:
        raise FileNotFoundError('FFmpeg required only for conversion, not pilot rebuilds')
    version = subprocess.run([binary,'-version'],check=True,capture_output=True,text=True).stdout.splitlines()[0]
    recipe = {'source_sha256':digest(source.read_bytes()),'filter':V4_FILTER,'loop':0,'ffmpeg':version}
    receipt = target.with_suffix('.gif.json')
    if receipt.is_file() and target.is_file():
        old = read_json(receipt)
        if old.get('recipe')==recipe and old.get('sha256')==digest(target.read_bytes()):
            return {**old,'status':'cached'}
    target.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=target.parent) as folder:
        temp = Path(folder)/'converted.gif'
        subprocess.run([binary,'-hide_banner','-loglevel','error','-y','-i',str(source),
                        '-filter_complex',V4_FILTER,'-loop','0',str(temp)],check=True,timeout=180)
        blob = temp.read_bytes()
        info = gif_info(blob)
        if info['frames']<2 or info['loop']!=0:
            raise ValueError('Expected animated infinitely looping v4 GIF')
        from .io import atomic
        atomic(target,blob)
    result = {'recipe':recipe,'sha256':digest(blob),'status':'converted'}
    write_json(receipt,result)
    return result


def prepare(project, output):
    result = []
    for card in project.content()['cards']:
        row = card['row']
        if row['media_type']=='gif' and row['source_video_path']:
            from .io import inside
            source = inside(project.legacy,row['source_video_path'])
            result.append({'id':card['id'],**gif(source,output/Path(row['media_path']).name)})
    return result
