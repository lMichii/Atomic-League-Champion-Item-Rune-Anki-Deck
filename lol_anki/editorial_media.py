"""Identity-bound, immutable media overrides. Approval is always an explicit action."""
import copy
import json
from pathlib import Path
import subprocess
import math
import datetime as dt
from .io import atomic,canonical,digest,inside,read_json,write_json
from .media import gif,gif_info
from .cache import Cache
from .operations import serialized

def immutable(path,blob):
    path=Path(path)
    if path.exists() and path.read_bytes()!=blob: raise ValueError('Immutable media/source object was modified: '+str(path))
    atomic(path,blob)


def inspect_media(path):
    path=Path(path)
    if path.suffix.lower() not in ('.png','.jpg','.gif','.mp4','.webm'): raise ValueError('Supported media: PNG, GIF, MP4, WebM (source JPEG portraits also supported)')
    if path.suffix.lower() in ('.png','.jpg','.gif','.webm'): Cache.validate(path.read_bytes(),path.suffix.lower()[1:])
    probe=_run(['ffprobe','-v','error','-select_streams','v:0','-show_entries',
        'stream=width,height,codec_name:format=duration','-of','json',str(path)],capture_output=True,text=True,timeout=30)
    if probe.returncode: raise ValueError('Media could not be probed or decoded: '+probe.stderr[:300])
    data=json.loads(probe.stdout); stream=next(iter(data.get('streams',[])),None)
    if not stream or not 16<=stream['width']<=4096 or not 16<=stream['height']<=4096: raise ValueError('Missing video/image stream or dimensions outside 16..4096 pixels')
    duration=float(data.get('format',{}).get('duration',0))
    if not math.isfinite(duration) or not 0<=duration<=120: raise ValueError('Select a short ability clip (at most 120 seconds) before importing')
    result=_run(['ffmpeg','-hide_banner','-v','error','-xerror','-i',str(path),'-map','0:v:0','-f','null','-'],capture_output=True,timeout=60)
    if result.returncode or result.stderr.strip(): raise ValueError('Media failed full decoding: '+result.stderr.decode(errors='replace')[:300])
    info={'width':stream['width'],'height':stream['height'],'codec':stream['codec_name'],'duration_seconds':duration,'full_decode':'passed'}
    if path.suffix.lower()=='.gif':
        info.update(gif_info(path.read_bytes()))
        if info['frames']<2 or info['loop']!=0: raise ValueError('GIF overrides must animate and loop indefinitely')
    return info


def _run(command,**options):
    try: return subprocess.run(command,**options)
    except subprocess.SubprocessError as ex: raise ValueError('Media inspection/decoding timed out or failed') from ex


def variant_identity(card):
    unit=card.get('learning_unit')
    if not unit or not unit.get('context_id'): return None
    return {'entity_id':card['entity_id'],'subject_id':unit['subject_id'],
            'context_id':unit['context_id'],'slot':unit['slot']}


def matches(target,card):
    if target.get('role','front') not in ('front','icon','cue'): return False
    fields=set(target)-{'role'}
    if target.get('kind')=='card': return fields=={'kind','card_id'} and target['card_id']==card['id']
    if target.get('kind')=='variant': return variant_identity(card) is not None and fields=={'kind','identity'} and target['identity']==variant_identity(card)
    return False


class MediaOverrides:
    def __init__(self,root):
        self.root=Path(root); self.folder=self.root/'data/editorial'; self.path=self.folder/'overrides.json'

    def records(self):
        return read_json(self.path) if self.path.exists() else {'schema_version':1,'records':[]}

    @serialized
    def ingest(self,card,source,target,provenance):
        target={**target,'role':target.get('role','front')}
        if card['row']['slot']=='P' and target['role']=='front' and (Path(source).suffix.lower()!='.png' or provenance.get('display_role') in ('screenshot','supplemental')):
            target['role']='cue'
        if not matches(target,card): raise ValueError('Media target does not exactly match this stable card/variant identity')
        if target['role']=='cue' and card['row']['slot']!='P': raise ValueError('Supplementary cue media is reserved for passive cards')
        if target['role']=='icon' and Path(source).suffix.lower()!='.png': raise ValueError('Answer icon replacements must be PNG')
        if not all(isinstance(provenance.get(k),str) and provenance[k].strip() for k in ('origin','source','rights_holder','license_reference','asset_version','distribution_status')):
            raise ValueError('Origin, source, rights holder, license reference, asset version and distribution status are required')
        if provenance['distribution_status'] not in ('pending','personal_only','cleared','restricted'): raise ValueError('Invalid distribution review status')
        source=Path(source).resolve()
        if source.suffix.lower() not in ('.gif','.png','.mp4','.webm'): raise ValueError('Overrides accept GIF, PNG, MP4 and WebM')
        if source.stat().st_size>100*1024*1024: raise ValueError('Media exceeds 100 MiB; select a shorter clip')
        source_info=inspect_media(source); source_sha=digest(source.read_bytes())
        if source_sha in card.get('ambiguous_media_sha256',[]): raise ValueError('Generic slot media cannot be assigned to this ability variant, regardless of filename')
        original=self.folder/'originals'/(source_sha+source.suffix.lower()); immutable(original,source.read_bytes())
        recipe=None
        if source.suffix.lower() in ('.mp4','.webm'):
            converted=self.root/'build/editorial/conversions'/(source_sha+'.gif')
            try: recipe=gif(original,converted)['recipe']
            except subprocess.SubprocessError as ex: raise ValueError('Source video conversion failed') from ex
            blob=converted.read_bytes(); extension='.gif'
        else: blob=source.read_bytes(); extension=source.suffix.lower()
        asset=self.folder/'media'/('override-'+digest(blob)+extension); immutable(asset,blob)
        info=inspect_media(asset)
        identity={'target':target,'source_sha256':source_sha,'sha256':digest(blob),'provenance':provenance,'recipe':recipe}
        key=digest(canonical(identity)); data=self.records()
        existing=next((r for r in data['records'] if r['id']==key),None)
        if existing: return existing  # Ingestion never downgrades or overwrites an approved record.
        record={**identity,'id':key,'path':asset.relative_to(self.root).as_posix(),
                'original_path':original.relative_to(self.root).as_posix(),'source_info':source_info,'output_info':info,
                'created_at':dt.datetime.now(dt.timezone.utc).isoformat(),
                'review':{'status':'pending','reviewer':'','matching_notes':''}}
        data['records'].append(record); write_json(self.path,data)
        return record

    @serialized
    def approve(self,key,card,reviewer,notes=''):
        if not reviewer.strip(): raise ValueError('Named reviewer required')
        data=self.records(); record=next(r for r in data['records'] if r['id']==key)
        if not matches(record['target'],card): raise ValueError('Override belongs to another card/weapon/form')
        path=inside(self.root,record['path'])
        if digest(path.read_bytes())!=record['sha256']: raise ValueError('Override bytes changed')
        inspect_media(path)
        if record['source_sha256'] in card.get('ambiguous_media_sha256',[]): raise ValueError('Generic slot media cannot be approved for this variant')
        if record['review']['status']!='approved': record['review']={'status':'approved','reviewer':reviewer,'matching_notes':notes,'at':dt.datetime.now(dt.timezone.utc).isoformat()}
        target_key=digest(canonical(record['target']))
        if data.setdefault('selected',{}).get(target_key)!=key:
            data.setdefault('selection_history',[]).append({'target':record['target'],'override_id':key,'reviewer':reviewer,'notes':notes,'at':dt.datetime.now(dt.timezone.utc).isoformat()})
        data['selected'][target_key]=key
        write_json(self.path,data)
        return record

    def select(self,card,role='front'):
        records=[r for r in self.records()['records'] if r['review']['status']=='approved' and matches(r['target'],card) and r['target'].get('role','front')==role]
        for kind in ('card','variant'):
            choices=[r for r in records if r['target']['kind']==kind]
            if len(choices)>1:
                selected=self.records().get('selected',{}).get(digest(canonical(choices[0]['target'])))
                choices=[r for r in choices if r['id']==selected]
                if not choices: raise ValueError('Multiple approved overrides match this identity; select explicitly')
            if choices:
                r=choices[0]
                if digest(inside(self.root,r['path']).read_bytes())!=r['sha256']: raise ValueError('Approved override integrity failure')
                return copy.deepcopy(r)
        return None
