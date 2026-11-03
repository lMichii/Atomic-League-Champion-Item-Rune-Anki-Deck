"""Hash-bound, inspectable editorial proposals. No automatic source-to-prose writes."""
import difflib
import copy
import time
from .identity import guid, stable_id
from .io import atomic, canonical, digest, read_json, write_json
from .validation import validate
from .project import Project
from .operations import serialized

def source_extension(old,new):
    for field in ('snapshots','entities'):
        if new.get(field,[])[:len(old[field])]!=old[field]: raise ValueError('Source promotion must preserve existing '+field)
    if any(new.get('media_sha256',{}).get(k)!=v for k,v in old['media_sha256'].items()): raise ValueError('Existing media provenance cannot change during additive promotion')
    for field,value in old.items():
        if field not in ('snapshots','entities','media_sha256','editorial_catalog') and new.get(field)!=value:
            raise ValueError('Source promotion changed frozen source metadata: '+field)


@serialized
def propose(project, candidate_path, folder, source_candidate_path=None,editorial_inputs=None):
    base = project.content()
    candidate = read_json(candidate_path)
    candidate_sources=read_json(source_candidate_path) if source_candidate_path else None
    if candidate_sources is not None and not project.config.get('editorial_profile'): raise ValueError('Coupled source promotion requires the editorial profile')
    if candidate_sources is not None: source_extension(project.sources(),candidate_sources)
    report = validate(project, candidate, check_lock=False,sources=candidate_sources,check_source_lock=candidate_sources is None)
    if report['errors']:
        raise ValueError('Candidate fails structural validation: '+str([f for f in report['findings'] if f['severity']=='error']))
    old = {c['id']:c for c in base['cards']}
    new = {c['id']:c for c in candidate['cards']}
    changed = sorted(k for k in old.keys()|new.keys() if old.get(k)!=new.get(k))
    proposal = {'schema_version':1, 'base_sha256':digest(canonical(base)),
                'candidate_sha256':digest(canonical(candidate)),
                'sources_sha256':digest(project.path('sources').read_bytes()),
                'changed_ids':changed, 'candidate':candidate}
    if candidate_sources is not None:
        baseline=Project(project.root,profile='batch01').content()['cards']
        if candidate['cards'][:len(baseline)]!=baseline: raise ValueError('Reviewed additions cannot modify the frozen approved baseline')
        proposal.update(kind='reviewed_additions',candidate_sources=candidate_sources,
                        candidate_sources_sha256=digest(canonical(candidate_sources)),editorial_inputs=editorial_inputs or {})
    token = digest(canonical(proposal))
    folder.mkdir(parents=True,exist_ok=True)
    write_json(folder/'proposal.json',proposal)
    diff = ''.join(difflib.unified_diff(canonical(base).decode().splitlines(True),canonical(candidate).decode().splitlines(True),fromfile='current',tofile='proposed'))
    atomic(folder/'changes.diff',diff.encode())
    if candidate_sources is not None:
        atomic(folder/'sources.diff',''.join(difflib.unified_diff(canonical(project.sources()).decode().splitlines(True),
            canonical(candidate_sources).decode().splitlines(True),fromfile='current-sources',tofile='proposed-sources')).encode())
    atomic(folder/'REVIEW.md',(f'# Editorial change review\n\nProposal SHA-256: `{token}`\n\nChanged IDs: {len(changed)}\n\n'+
                             '\n'.join('- `'+k+'`' for k in changed)+'\n\nInspect changes.diff and proposal.json before explicit apply-review.\n').encode())
    return {'proposal':str(folder/'proposal.json'), 'accept_token':token,'changed_ids':changed}


def _review_candidate(project, proposal_path, accept):
    proposal = read_json(proposal_path)
    if proposal.get('kind')=='champion_draft':
        raise ValueError('Generated champion drafts require editorial/source/media review and a new ordinary proposal; they cannot be auto-approved')
    if accept != digest(canonical(proposal)):
        raise ValueError('Exact reviewed proposal hash required')
    lock = read_json(project.path('lock'))
    current = project.content()
    current_hash = digest(canonical(current))
    if current_hash != proposal['base_sha256'] or current_hash != lock['content_sha256']:
        raise ValueError('Stale proposal or unreviewed current content; restore reviewed base first')
    if digest(project.path('sources').read_bytes()) != proposal['sources_sha256']:
        raise ValueError('Sources changed after proposal review')
    candidate = copy.deepcopy(proposal['candidate'])
    candidate_sources=proposal.get('candidate_sources')
    if candidate_sources is not None:
        if proposal.get('kind')!='reviewed_additions' or not project.config.get('editorial_profile'): raise ValueError('Unsupported source promotion')
        if digest(canonical(candidate_sources))!=proposal['candidate_sources_sha256']: raise ValueError('Source candidate hash mismatch')
        source_extension(project.sources(),candidate_sources)
        baseline=Project(project.root,profile='batch01').content()['cards']
        if candidate['cards'][:len(baseline)]!=baseline: raise ValueError('Frozen baseline was modified')
        from .editorial import Editorial
        editor=Editorial(project.root); registry=editor.registry()
        for key,sha in proposal.get('editorial_inputs',{}).items():
            record=registry['cards'][key]
            if digest(canonical(record))!=sha: raise ValueError('Editorial decisions changed after proposal creation')
            expected=next(c for c in candidate['cards'] if c['id']==key)['editorial_review']['media_sha256']
            if editor.effective(record)[1]!=expected: raise ValueError('Selected media changed after proposal creation')
    if digest(canonical(candidate)) != proposal['candidate_sha256']:
        raise ValueError('Candidate hash mismatch')
    old = {c['id']:c for c in current['cards']}
    new = {c['id']:c for c in candidate['cards']}
    changed = sorted(k for k in old.keys()|new.keys() if old.get(k)!=new.get(k))
    if changed != proposal['changed_ids']:
        raise ValueError('Changed ID list is inconsistent')
    if candidate_sources is not None and any(k not in proposal['editorial_inputs'] for k in changed): raise ValueError('Every changed addition requires a bound editorial decision')
    return proposal,lock,current,candidate,candidate_sources,changed


@serialized
def inspect_review(project, proposal_path, accept):
    """Read-only inspection using the same preconditions as explicit apply."""
    proposal,lock,current,candidate,sources,changed = _review_candidate(project,proposal_path,accept)
    report=validate(project,candidate,check_lock=False,sources=sources,check_source_lock=sources is None)
    return {'proposal':proposal,'current':current,'validation':report}


@serialized
def apply_review(project, proposal_path, accept, reviewer, notes=''):
    if not reviewer.strip(): raise ValueError('Reviewer name and exact reviewed proposal hash required')
    proposal,lock,current,candidate,candidate_sources,changed = _review_candidate(project,proposal_path,accept)
    current_hash=digest(canonical(current))
    old={c['id']:c for c in current['cards']}; new={c['id']:c for c in candidate['cards']}
    if not changed:
        return {'status':'no_changes'}
    # Explicit review advances only changed note revisions; scheduling is importer-owned.
    revision = max(int(time.time()),current['build_epoch']+1)
    candidate['build_epoch'] = revision
    for card in candidate['cards']:
        key = card['id']
        if key in changed:
            card['revision'] = revision
        else:
            card['revision'] = old[key]['revision']
    report = validate(project,candidate,check_lock=False,sources=candidate_sources,check_source_lock=candidate_sources is None)
    if report['errors']:
        raise ValueError('Reviewed candidate failed validation')
    folder = project.root/'data/reviews'/accept
    folder.mkdir(parents=True,exist_ok=True)
    atomic(folder/'before.json',canonical(current))
    atomic(folder/'before-lock.json',canonical(lock))
    atomic(folder/'before-sources.json',project.path('sources').read_bytes())
    write_json(folder/'proposal.json',proposal)
    receipt = {'proposal_sha256':accept,'reviewer':reviewer,'notes':notes,'revision':revision,'changed_ids':changed,
               'before_sha256':current_hash,'after_sha256':digest(canonical(candidate))}
    write_json(folder/'receipt.json',receipt)
    lock['content_sha256'] = receipt['after_sha256']
    if candidate_sources is not None:
        receipt['sources_after_sha256']=digest(canonical(candidate_sources))
        lock['sources_sha256']=receipt['sources_after_sha256']
        write_json(folder/'receipt.json',receipt)
    lock['reviews'].append(receipt)
    for key in new:
        lock['identities'][key] = {'guid':guid(key),'nid':stable_id(key,1800000000000),'cid':stable_id(key,2300000000000)}
    # Crash between these two atomic files fails closed (lock mismatch); before/receipt enable recovery.
    write_json(project.path('content'),candidate)
    if candidate_sources is not None: write_json(project.path('sources'),candidate_sources)
    write_json(project.path('lock'),lock)
    return {'status':'applied','review':receipt}
