"""Lossless, one-time ingestion. Never merges or overwrites authored content."""
import csv
import sqlite3
import zipfile
from .identity import guid, stable_id
from .io import atomic, canonical, digest, write_json


def migrate(project):
    destinations = [project.path(k) for k in ('content', 'sources', 'lock')]
    if any(p.exists() for p in destinations):
        if all(p.exists() for p in destinations):
            return {'status': 'already_migrated'}
        raise ValueError('Partial migration found; inspect existing files before recovery')
    with (project.legacy/'cards.csv').open(encoding='utf-8-sig', newline='') as stream:
        rows = list(csv.DictReader(stream))
    with (project.legacy/'manifest.csv').open(encoding='utf-8-sig', newline='') as stream:
        manifest = list(csv.DictReader(stream, delimiter=';'))
    champ_ids = {r['champion']: int(r['champion_id']) for r in manifest}
    con = sqlite3.connect(':memory:')
    with zipfile.ZipFile(project.legacy/'LoL_Anki_Pilot_6_Champions_v4_English.apkg') as z:
        con.deserialize(z.read('collection.anki2'))
    epoch = con.execute('select max(mod) from notes').fetchone()[0]
    con.close()
    snapshots = []
    for path in sorted((project.fetcher/'cache').rglob('*.json')):
        rel = path.relative_to(project.fetcher/'cache').as_posix()
        sha = digest(path.read_bytes())
        dest = project.root/'data/sources/raw'/f'{sha}.json'
        atomic(dest, path.read_bytes())
        if rel.startswith('ddragon/'):
            parts = rel.split('/')
            suffix = 'champion/'+parts[-1] if 'details' in parts else 'champion.json'
            url = f'https://ddragon.leagueoflegends.com/cdn/{parts[1]}/data/en_US/{suffix}'
            version = parts[1]
            provider = 'riot_ddragon'
        else:
            url = 'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champions/'+path.name
            provider, version = 'communitydragon', 'unknown_legacy_latest'
        snapshots.append({'provider': provider, 'source_url': url, 'upstream_version': version,
                          'snapshot_id': sha, 'sha256': sha, 'retrieved_at': None,
                          'retrieval_status': 'inherited_cache_timestamp_unknown',
                          'path': dest.relative_to(project.root).as_posix(), 'legacy_path': rel})
    media = {}
    for p in sorted((project.legacy/'media').rglob('*')):
        if p.is_file():
            media[p.relative_to(project.legacy).as_posix()] = digest(p.read_bytes())
    cards = []
    for row in rows:
        is_term = row['level'] == 'L0'
        entity = 'term:'+row['id'].split(':')[1] if is_term else 'champ:'+str(champ_ids[row['champion']])
        evidence = {'riot_url': row['source_riot'], 'wiki_url': row['source_wiki'],
                    'wiki_revision': None, 'wiki_snapshot': None, 'verified_patch': None,
                    'claims': []}
        cards.append({'id': row['id'], 'entity_id': entity, 'entity_kind': 'term' if is_term else 'champion',
                      'content_status': 'curated_legacy', 'qa_status': 'needs_review',
                      'revision': epoch, 'evidence': evidence, 'row': row})
    content = {'schema_version': 1, 'build_epoch': epoch, 'cards': cards}
    sources = {'schema_version': 1, 'game_patch': project.config['game_patch'],
               'ddragon_patch': project.config['ddragon_patch'], 'snapshots': snapshots,
               'entities': [{'id': 'champ:'+str(n), 'riot_id': n, 'name': c} for c, n in sorted(champ_ids.items())],
               'ability_assets': manifest, 'media_sha256': media}
    lock = {'schema_version': 1, 'content_sha256': digest(canonical(content)),
            'sources_sha256': digest(canonical(sources)),
            'baseline_sha256': digest(canonical(content)),
            'identities': {r['id']: {'guid': guid(r['id']), 'nid': stable_id(r['id'], 1800000000000),
                                     'cid': stable_id(r['id'], 2300000000000)} for r in rows},
            'reviews': []}
    # Sources first; never clobber a partial editorial store on rerun.
    write_json(project.path('sources'), sources)
    write_json(project.path('content'), content)
    write_json(project.path('lock'), lock)
    return {'status': 'migrated', 'cards': len(cards), 'snapshots': len(snapshots)}
