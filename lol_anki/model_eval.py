"""Isolated author-model experiments on retained evidence; never imports cards."""
import copy
from collections import Counter
from pathlib import Path
import time
import tomllib
from .io import atomic,canonical,digest,inside,read_json,write_json
from .generation.ai import AIClient,ModelError
from .generation.contracts import check_draft,check_verification,support_check_passed
from .generation.kit_contracts import validate_text,validate_support,supported


def evaluate_author(root,archive,model,verifier_model,output):
    root=Path(root).resolve(); archive=inside(root,archive); output=inside(root,output)
    if not output.is_relative_to(root/'data/model-evaluations') and not output.is_relative_to(root/'build'):
        raise ValueError('Keep experiments under data/model-evaluations or build; never overwrite drafts/content')
    if archive==output or output.is_relative_to(archive): raise ValueError('Experiments cannot modify source archives')
    manifest=read_json(archive/'archive.json')
    for rel,sha in manifest['files'].items():
        if digest(inside(archive,rel).read_bytes())!=sha: raise ValueError('Experiment source archive changed')
    config=tomllib.loads((root/'generation.toml').read_text('utf-8'))['ai']
    config={**config,'attempts':2}
    author_request=read_json(archive/'ai/author-pass-1/request.json')
    verifier_request=read_json(archive/'ai/verifier-pass-1/request.json')
    packet=read_json(archive/'source-packet.json'); adaptive=packet['schema_version']>1
    if (output/'report.json').exists():
        saved=read_json(output/'report.json')
        if (saved['candidate_model'],saved['verifier_model'],saved['source_packet_sha256'])!=(model,verifier_model,digest((archive/'source-packet.json').read_bytes())):
            raise ValueError('Evaluation output already belongs to a different experiment; choose a new output folder')
        return {**saved,'reused_report':True,'new_execution_model_attempts':0}
    inventory=read_json(archive/('card-inventory.json' if adaptive else 'mechanics-inventory.json'))
    images_by_sha={digest(p.read_bytes()):p for p in archive.rglob('*.png')}
    images=[images_by_sha[sha] for sha in author_request['images_sha256']]
    verify_images=[images_by_sha[sha] for sha in verifier_request['images_sha256']]
    cache=root/'.cache/model-evaluation'/digest(output.relative_to(root).as_posix().encode())[:20]/'ai'
    existing={p for p in cache.glob('*/attempt-*') if p.is_dir()}; started=time.monotonic()
    result={'schema_version':1,'champion':packet['champion']['name'],'candidate_model':model,
            'verifier_model':verifier_model,'source_archive':archive.relative_to(root).as_posix(),
            'source_packet_sha256':digest((archive/'source-packet.json').read_bytes()),
            'human_approved':False,'editorial_imports':0,'production_configuration_changed':False,
            'limitation':'Controlled source-packet comparison; model cross-check is fallible and is not human factual QA.'}
    receipts={}
    try:
        candidate=AIClient({**config,'model':model},cache)
        draft,receipt=candidate.generate(author_request['task'],author_request['instructions'],author_request['data'],
            author_request['schema'],lambda v:validate_text(v,packet,inventory) if adaptive else check_draft(v,packet),images)
        receipts['candidate']=receipt; write_json(output/'candidate-draft.json',draft)
        payload=copy.deepcopy(verifier_request['data']); payload['draft']=draft
        verifier=AIClient({**config,'model':verifier_model},cache)
        verification,receipt=verifier.generate(verifier_request['task'],verifier_request['instructions'],payload,
            verifier_request['schema'],lambda v:validate_support(v,packet,inventory,draft) if adaptive else check_verification(v,packet,inventory,draft),verify_images)
        receipts['verifier']=receipt; write_json(output/'verification.json',verification)
        failures=[c for c in verification['checks'] if not (supported(c) if adaptive else support_check_passed(c,inventory))]
        result.update(status='evaluated',cards=len(draft['cards']),schema_and_citations_passed=True,
            semantic_failed_checks=len(failures),failed_checks=failures,
            missing_core_ids=[c['mechanic_id'] for check in verification['checks'] for c in check['core_coverage'] if not c['covered']],
            kit_complete=verification.get('kit_complete',True),omitted_topics=verification.get('omitted_topics',[]),
            candidate_suitable_for_controlled_trial=not failures and verification.get('kit_complete',True) and not verification.get('omitted_topics'))
    except (ValueError,OSError,RuntimeError) as ex:
        result.update(status='failed',error_type=type(ex).__name__,error=str(ex),candidate_suitable_for_controlled_trial=False)
    attempts={p for p in cache.glob('*/attempt-*') if p.is_dir()}-existing
    result['new_model_attempts']=len(attempts); result['elapsed_seconds']=round(time.monotonic()-started,2)
    totals={}; missing=0
    # Retain exact public requests/responses/diagnostics without model reasoning events.
    requests={p.parent for p in attempts}|{cache/r['request_sha256'] for r in receipts.values()}
    allowed={'request.json','receipt.json','accepted.json','response.json','metadata.json','error.json','schema.json','model-output.json','prompt.txt','stderr.txt'}
    for request in requests:
        for file in request.rglob('*'):
            if file.is_file() and file.name in allowed:
                atomic(output/'requests'/request.name/file.relative_to(request),file.read_bytes())
    for attempt in attempts:
        request=read_json(attempt.parent/'request.json'); key=request['model']
        if not (attempt/'metadata.json').exists(): missing+=1; continue
        values=read_json(attempt/'metadata.json').get('usage',[])
        for value in values if isinstance(values,list) else [values]:
            if isinstance(value,dict):
                sums=totals.setdefault(key,Counter()); sums.update({k:v for k,v in value.items() if isinstance(v,int)})
    result.update(receipts=receipts,available_new_attempt_usage={k:dict(v) for k,v in totals.items()},attempts_without_usage=missing)
    write_json(output/'report.json',result)
    atomic(output/'REPORT.md',('# Author-model evaluation: '+packet['champion']['name']+'\n\n'+
        f'Candidate: {model}. Independent model checker: {verifier_model}. Status: {result["status"]}.\n\n'+
        'No review records, production configuration or approved content were changed.\n\n'+
        '```json\n'+canonical(result).decode()+'```\n').encode())
    return result
