"""Real-media acquisition/conversion and technical checks; no content authoring."""
from pathlib import Path
import subprocess
from ..io import atomic,digest,write_json
from ..media import gif,gif_info
import json


def collect_assets(retriever,packet,folder):
    folder=Path(folder)
    slug=packet['champion']['ddragon_id'].lower()
    records=[]; findings=[]
    def download(url,name,kind):
        if not url:
            findings.append({'code':'media_url_missing','name':name})
            return None
        blob,meta=retriever.get(url,kind,optional=True)
        if blob is None:
            findings.append({'code':'media_unavailable','name':name,'url':url})
            return None
        path=folder/'media'/name; atomic(path,blob)
        record={'path':path.relative_to(folder).as_posix(),'sha256':digest(blob),
                'source_url':url,'source_sha256':meta['sha256'],'retrieved_at':meta['retrieved_at'],'kind':kind}
        records.append(record)
        return record
    portrait=download(packet['portrait_url'],slug+'_portrait.jpg','jpg')
    if not portrait:
        portrait=download(f"https://ddragon.leagueoflegends.com/cdn/{packet['versions']['ddragon']}/img/champion/{packet['champion']['ddragon_id']}.png",slug+'_portrait.png','png')
    abilities={}
    for ability in packet['abilities']:
        slot=ability['slot']; prefix=slug+'_'+slot.lower()
        icon=download(ability['icon_url'],prefix+'_icon.png','png')
        video=download(ability['video_url'],prefix+'.webm','webm')
        animation=None
        if video:
            try:
                target=folder/'media'/(prefix+'.gif')
                receipt=gif(folder/video['path'],target)
                info=gif_info(target.read_bytes())
                animation={'path':target.relative_to(folder).as_posix(),'sha256':digest(target.read_bytes()),
                           'source_url':ability['video_url'],'source_sha256':video['sha256'],'kind':'gif',
                           'recipe':receipt['recipe'],'frames':info['frames'],'loop':info['loop']}
                records.append(animation)
            except (OSError,ValueError,RuntimeError,subprocess.SubprocessError) as ex:
                findings.append({'code':'gif_conversion_failed','slot':slot,'message':str(ex)})
        if slot!='P' and not animation:
            findings.append({'code':'active_icon_fallback','slot':slot,'message':'No working GIF; draft icon fallback needs review'})
        if not icon: findings.append({'code':'required_icon_missing','slot':slot})
        abilities[slot]={'icon':icon,'video':video,'gif':animation}
    manifest={'portrait':portrait,'abilities':abilities,'files':records,'findings':findings,
              'visual_qa':'unreviewed','current_client_verified':False}
    write_json(folder/'assets.json',manifest)
    return manifest


def passive_frames(folder,assets):
    """Extract genuine review frames; these are model inputs, not verified cues."""
    folder=Path(folder)
    passive=assets['abilities']['P']['video']
    if not passive: return [],[]
    source=folder/passive['path']
    probe=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','json',str(source)],check=True,capture_output=True,text=True)
    duration=float(json.loads(probe.stdout)['format']['duration'])
    paths=[]; metadata=[]
    for i,fraction in enumerate((0.15,0.4,0.65,0.9)):
        target=folder/'visual-inputs'/f'passive-{i+1}.png'; target.parent.mkdir(exist_ok=True)
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',str(duration*fraction),'-i',str(source),
                        '-frames:v','1','-vf','scale=640:-1',str(target)],check=True,capture_output=True)
        paths.append(target)
        metadata.append({'path':target.relative_to(folder).as_posix(),'sha256':digest(target.read_bytes()),
                         'timestamp_seconds':round(duration*fraction,4),'source_sha256':passive['sha256'],
                         'source_url':passive['source_url'],'status':'unverified_visual_evidence'})
    write_json(folder/'visual-inputs/manifest.json',metadata)
    return paths,metadata
