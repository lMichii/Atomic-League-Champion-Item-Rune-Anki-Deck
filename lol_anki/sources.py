"""Retrieve source snapshots/assets into staging. Never author or replace cards."""
import json
import re
import urllib.parse
from .cache import Cache
from .io import write_json

DD = 'https://ddragon.leagueoflegends.com'
CD = 'https://raw.communitydragon.org'
VIDEO = 'https://d28xe8vt774jo5.cloudfront.net/'


def fetch(project, champions, patch, cdragon_version=None, offline=False, assets=False, refresh=False):
    if not re.fullmatch(r'\d+\.\d+\.\d+',patch):
        raise ValueError('Explicit Data Dragon version required (no latest)')
    if cdragon_version and not re.fullmatch(r'\d+\.\d+(?:\.\d+)?',cdragon_version):
        raise ValueError('Explicit immutable CDragon release required (no latest)')
    if not champions or len(champions)>6 or any(c.lower()=='all' for c in champions):
        raise ValueError('Foundational runs accept 1–6 explicitly selected champions; no mass generation')
    cache = Cache(project.root/'.cache/http',offline=offline)
    report = {'patch':patch,'cdragon_version':cdragon_version,'entities':[],'resources':[],'errors':[]}
    def resource(url, kind='json'):
        blob, meta = cache.get(url,kind,refresh)
        report['resources'].append(meta)
        return json.loads(blob) if kind=='json' else blob
    try:
        index = resource(f'{DD}/cdn/{patch}/data/en_US/champion.json')['data']
    except (OSError,ValueError,KeyError) as ex:
        report['errors'].append({'resource':'index','error':str(ex)})
        write_json(project.root/'build/retrieval.json',report)
        return report
    for name in champions:
        try:
            found = [c for c in index.values() if name.casefold() in (c['id'].casefold(),c['name'].casefold())]
            if len(found)!=1:
                raise ValueError(f'Champion not uniquely resolved in Riot index: {name}')
            champ = found[0]; key = champ['id']; cid = int(champ['key'])
            data_url = f'{DD}/cdn/{patch}/data/en_US/champion/{key}.json'
            detail = resource(data_url)['data'][key]
            abilities = []
            if len(detail.get('spells',[]))!=4:
                raise ValueError('Expected four primary active spells; inspect complex form data manually')
            for slot, ability in zip('PQWER',[detail['passive'],*detail['spells']]):
                filename = ability.get('image',{}).get('full')
                url = f'{DD}/cdn/{patch}/img/'+('passive/' if slot=='P' else 'spell/')+urllib.parse.quote(filename or '')
                abilities.append({'slot':slot,'name':ability['name'], 'riot_description':ability.get('description'),
                                  'cooldown_raw':ability.get('cooldown'),'cost_raw':ability.get('cost'),
                                  'icon_url':url if filename else None,'source_url':data_url,
                                  'qa_status':'unverified_source','patch':patch})
                if assets and filename:
                    try:
                        resource(url,'png')
                    except (OSError,ValueError) as ex:
                        report['errors'].append({'resource':url,'error':str(ex)})
            entity = {'entity_id':f'champ:{cid}','riot_id':cid,'ddragon_id':key,'name':detail['name'],
                      'stats_raw':detail.get('stats'), 'abilities':abilities,'source_url':data_url}
            report['entities'].append(entity)
            if assets:
                resource(f'{DD}/cdn/{patch}/img/champion/{key}.png','png')
            if cdragon_version:
                cd = resource(f'{CD}/{cdragon_version}/plugins/rcp-be-lol-game-data/global/default/v1/champions/{cid}.json')
                for spell in cd.get('spells',[]):
                    rel = spell.get('abilityVideoPath','').lstrip('/')
                    if not rel:
                        report['errors'].append({'resource':key+':'+spell.get('spellKey','?'),'error':'No official clip path; manual review needed'})
                        continue
                    if not re.fullmatch(r'champion-abilities/[A-Za-z0-9_/-]+\.webm',rel) or '..' in rel:
                        raise ValueError('Unsafe video path in discovery metadata')
                    if assets:
                        try:
                            resource(VIDEO+rel,'webm')
                        except (OSError,ValueError) as ex:
                            report['errors'].append({'resource':VIDEO+rel,'error':str(ex)})
        except (OSError,ValueError,KeyError) as ex:
            report['errors'].append({'resource':name,'error':str(ex)})
    report['qa_status'] = 'needs_review'
    write_json(project.root/'build/retrieval.json',report)
    return report


def archive_wiki(project, url, revision, patch, offline=False):
    """Record supplied revision-specific Wiki evidence; never mark claims verified."""
    parsed = urllib.parse.urlsplit(url)
    if parsed.hostname!='wiki.leagueoflegends.com' or not revision.isdigit():
        raise ValueError('League Wiki URL and numeric revision required')
    query = dict(urllib.parse.parse_qsl(parsed.query)); query['oldid'] = revision
    versioned = urllib.parse.urlunsplit(parsed._replace(query=urllib.parse.urlencode(query)))
    blob, meta = Cache(project.root/'.cache/http',offline=offline).get(versioned,'html')
    evidence = {'url':versioned,'wiki_revision':revision,'game_patch':patch,'snapshot_sha256':meta['sha256'],
                'retrieved_at':meta['retrieved_at'],'qa_status':'needs_review','claims':[]}
    write_json(project.root/'build/wiki'/f'{meta["sha256"]}.json',evidence)
    return evidence
