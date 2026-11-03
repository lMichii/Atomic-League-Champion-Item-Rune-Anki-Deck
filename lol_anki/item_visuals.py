"""Hash-bound visual overlays for existing glossary identities, prototype only."""
import copy
from .io import atomic, canonical, digest, inside, read_json
from .editorial_media import inspect_media

VISUALS='data/sources/items-glossary-visuals.json'
EXISTING_TERMS={'term:charm:L0','term:stun:L0','term:root_snare:L0','term:knock_up:L0','term:silence:L0'}


def visual_glossary(root, content, folder):
    manifest=read_json(root/VISUALS)
    baseline={c['id']:c for c in read_json(root/'data/content/pilot.json')['cards']}
    cards=copy.deepcopy(content['cards']); by_key={c['id']:c for c in cards}
    examples=manifest['examples']; keys=[e['card_id'] for e in examples]
    if set(keys)!=EXISTING_TERMS|{'term:stasis:L0'} or len(keys)!=6:
        raise ValueError('Visual prototype scope or duplicate glossary identity changed')
    report=[]
    for example in examples:
        key=example['card_id']; original=by_key.get(key,baseline.get(key))
        if original is None or digest(canonical(original))!=example['baseline_sha256']:
            raise ValueError('Visual glossary baseline changed: '+key)
        for record in example['source_records']:
            if digest(inside(root,record['path']).read_bytes())!=record['sha256']:
                raise ValueError('Glossary media provenance changed: '+key)
        path=inside(root,example['media_path']); blob=path.read_bytes()
        if digest(blob)!=example['sha256']: raise ValueError('Glossary example media changed: '+key)
        info=inspect_media(path)
        if path.suffix.lower()!='.gif': raise ValueError('Glossary example must be an inspected looping GIF')
        atomic(folder/'media'/path.name,blob)
        card=by_key.get(key)
        if card is None:
            card=copy.deepcopy(original); card['entity_kind']='term'; cards.append(card)
        card['revision']=manifest['revision']
        card['row'].update(learning_style=True,media_type='gif',media_path='media/'+path.name,
                           mechanic_example=example['caption'])
        # Keep the definition's source links; add example attribution on the back.
        card['row']['example_source_riot']=example['source_riot']
        card['row']['example_source_wiki']=example['source_wiki']
        report.append({**example,**info})
    if len({c['id'] for c in cards})!=len(cards): raise ValueError('Duplicate glossary export')
    return {**content,'cards':cards}, {'visual_examples':report,'text_only':manifest['text_only'],
                                      'not_added':manifest['not_added']}
