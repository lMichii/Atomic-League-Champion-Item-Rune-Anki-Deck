import argparse
import json
import logging
from pathlib import Path
from .io import inside
from .project import Project, ROOT


def main(argv=None):
    parser = argparse.ArgumentParser(description='League Anki pilot pipeline: sources, authored content, review, export')
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--profile',choices=('pilot','batch01','editorial'),default='pilot')
    commands = parser.add_subparsers(dest='command',required=True)
    items=commands.add_parser('item-prototype',help='Build only the saved five-item prototype and existing visual glossary; no AI or approvals')
    items.add_argument('--offline',action='store_true',help='Use archived sources and cached/saved icons only')
    db=commands.add_parser('build-card-index',help='Build/update the searchable card and source-pointer inventory')
    db.add_argument('--apkg',default='build/staging/League_Anki_Gesamtstand_Reparaturen_2026-11-03.apkg')
    db.add_argument('--output',default='data/database/cards.jsonl')
    sl=commands.add_parser('source-lookup',help='Retrieve stored cards and source excerpts for a champion or ability')
    sl.add_argument('champion'); sl.add_argument('--ability'); sl.add_argument('--raw',action='store_true',help='Include full stored source text')
    sb=commands.add_parser('staging-batch',help='Resume a frozen batch with author-only generation and a standalone staging APKG; no approvals')
    sb.add_argument('batch'); sb.add_argument('--offline',action='store_true')
    sb.add_argument('--recover-cached',action='store_true',help='Try saved failed responses with current deterministic checks; never calls a model')
    sb.add_argument('--repair-champion',help='Explicit single repair of one failed champion; repeated repairs require human intervention')
    se=commands.add_parser('export-saved',help='Export approved cards and saved drafts together, without generation or approvals')
    se.add_argument('--output',type=Path,required=True)
    me=commands.add_parser('evaluate-author',help='Compare an author model against retained evidence without importing/approving cards')
    me.add_argument('archive',type=Path); me.add_argument('--model',required=True); me.add_argument('--verifier-model',required=True)
    me.add_argument('--output',type=Path,required=True)
    ci=commands.add_parser('champion-inventory',help='Current Riot roster and approved/generated/editorial completion status'); ci.add_argument('--offline',action='store_true')
    bp=commands.add_parser('batch-plan',help='Freeze a bounded new-champion draft batch; never approves cards')
    bp.add_argument('batch'); bp.add_argument('--size',type=int,default=10); bp.add_argument('--champions',nargs='+'); bp.add_argument('--offline',action='store_true')
    bp.add_argument('--authorization',help='Record an explicit user request for another draft batch without inventing prior review approval')
    br=commands.add_parser('batch-run',help='Run/resume a frozen batch, retry failures and import only pending drafts')
    br.add_argument('batch'); br.add_argument('--offline',action='store_true')
    br.add_argument('--retry-qa',action='store_true',help='Regenerate only failed, unimported QA results after a processor/prompt fix; retain prior run history')
    bs=commands.add_parser('batch-status',help='Read saved per-champion checkpoints and QA report'); bs.add_argument('batch')
    ba=commands.add_parser('batch-audit',help='Revalidate completed archived drafts offline without AI, imports or approvals'); ba.add_argument('batch')
    bc=commands.add_parser('batch-review-complete',help='Explicit human batch review acknowledgment; grants no card approvals')
    bc.add_argument('batch'); bc.add_argument('--reviewer',required=True)
    generate = commands.add_parser('generate-champion',help='Retrieve a champion kit and create UNAPPROVED AI drafts, inventory and previews')
    generate.add_argument('champion',help='Exactly one name, Data Dragon ID or Riot numeric key')
    generate.add_argument('--offline',action='store_true',help='Replay cached sources and model output; never invent missing inputs')
    generate.add_argument('--sources-only',action='store_true',help='Collect sources without invoking a model')
    generate.add_argument('--cached-sources',action='store_true',help='Reuse source snapshots while allowing missing media and model calls')
    generate.add_argument('--resume-draft',type=Path,help='Resume a source-matched saved AI draft checkpoint before verification')
    archive = commands.add_parser('archive-generated-run',help='Archive a completed UNAPPROVED run for reproducibility/history')
    archive.add_argument('path',type=Path)
    replay = commands.add_parser('replay-generated-run',help='Verify an unapproved run archive and replay it offline, without a model call')
    replay.add_argument('path',type=Path)
    commands.add_parser('editorial-init',help='Initialize a frozen-baseline reviewed-additions profile; approves nothing')
    imp=commands.add_parser('editorial-import',help='Import draft history without replacing manual edits/reviews'); imp.add_argument('path',type=Path)
    commands.add_parser('editorial-status',help='Render local review previews and report per-champion blockers')
    commands.add_parser('editorial-media-tasks',help='Report researched media gaps and explicit manual capture/matching tasks')
    srv=commands.add_parser('editorial-serve',help='Open a loopback-only editorial review service'); srv.add_argument('--port',type=int,default=8765)
    edit=commands.add_parser('editorial-review',help='Apply an explicit local edit/content/media decision from JSON')
    edit.add_argument('card_id'); edit.add_argument('request',type=Path)
    mi=commands.add_parser('editorial-media-import',help='Import a local media override as pending, never auto-approved')
    mi.add_argument('card_id'); mi.add_argument('path',type=Path); mi.add_argument('--metadata',required=True,type=Path); mi.add_argument('--variant',action='store_true')
    mi.add_argument('--role',choices=('front','icon','cue'),default='front')
    ma=commands.add_parser('editorial-media-approve',help='Explicitly approve one override after inspecting ability matching')
    ma.add_argument('card_id'); ma.add_argument('--override',required=True); ma.add_argument('--reviewer',required=True); ma.add_argument('--notes',default='')
    ep=commands.add_parser('editorial-propose',help='Propose selected content+media-reviewed additions; does not apply')
    ep.add_argument('--ids',nargs='+',required=True); ep.add_argument('--output',type=Path,default=Path('build/editorial/review'))
    commands.add_parser('migrate',help='Lossless one-time migration; never overwrite existing authored content')
    commands.add_parser('validate',help='Validate content/source/media and write missing/uncertain-data report')
    run = commands.add_parser('run',help='Validate and build existing six-pilot content, entirely offline')
    run.add_argument('--output')
    build = commands.add_parser('build',help='Build reviewed content; structural errors block export')
    build.add_argument('--output')
    stage = commands.add_parser('batch01-stage',help='Stage the authorized Batch 01 sources/media and candidate, without applying content')
    stage.add_argument('--offline',action='store_true')
    inspect = commands.add_parser('inspect-apkg'); inspect.add_argument('path',type=Path)
    fetch = commands.add_parser('fetch',help='Stage sources; never edit authored cards')
    fetch.add_argument('--champions',required=True)
    fetch.add_argument('--patch',required=True)
    fetch.add_argument('--cdragon-version')
    fetch.add_argument('--offline',action='store_true')
    fetch.add_argument('--refresh',action='store_true')
    fetch.add_argument('--assets',action='store_true')
    wiki = commands.add_parser('archive-wiki')
    wiki.add_argument('--url',required=True); wiki.add_argument('--revision',required=True)
    wiki.add_argument('--patch',required=True); wiki.add_argument('--offline',action='store_true')
    media = commands.add_parser('prepare-media'); media.add_argument('--output',default='build/proposed-media')
    propose = commands.add_parser('propose'); propose.add_argument('candidate',type=Path)
    propose.add_argument('--output',default='build/review')
    apply = commands.add_parser('apply-review'); apply.add_argument('proposal',type=Path)
    apply.add_argument('--accept',required=True); apply.add_argument('--reviewer',required=True)
    apply.add_argument('--notes',default='')
    args = parser.parse_args(argv)
    project = Project(args.root,profile=args.profile)
    log_folder = project.root/'build'; log_folder.mkdir(exist_ok=True)
    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(name)s %(message)s',
                        handlers=[logging.FileHandler(log_folder/'pipeline.log',encoding='utf-8'),logging.StreamHandler()],force=True)
    try:
        if args.command=='item-prototype':
            from .items import build_prototype
            result=build_prototype(project.root,args.offline)
        elif args.command=='build-card-index':
            from .database import build_index
            result=build_index(project.root,args.apkg,args.output)
        elif args.command=='source-lookup':
            from .database import lookup
            result=lookup(project.root,args.champion,args.ability,args.raw)
        elif args.command=='export-saved':
            from .staging import export_saved
            result=export_saved(project.root,args.output)
        elif args.command=='staging-batch':
            from .staging import run_staging
            result=run_staging(project.root,args.batch,args.offline,args.recover_cached,args.repair_champion)
        elif args.command=='evaluate-author':
            from .model_eval import evaluate_author
            result=evaluate_author(project.root,args.archive,args.model,args.verifier_model,args.output)
        elif args.command.startswith('batch-') or args.command=='champion-inventory':
            from .batches import BatchRunner
            from .io import read_json,write_json
            runner=BatchRunner(project.root)
            if args.command=='champion-inventory':
                index,receipt=runner.roster(args.offline); rows=runner.inventory(index)
                write_json(project.root/'build/batches/inventory.json',{'roster':receipt,'champions':rows})
                result={'roster':receipt,'champions':rows}
            elif args.command=='batch-plan':
                state=runner.plan(args.batch,args.size,args.champions,args.offline,args.authorization)
                result={'id':state['id'],'status':state['status'],'champions':{k:v['status'] for k,v in state['champions'].items()}}
            elif args.command=='batch-run':
                state=runner.run(args.batch,args.offline,args.retry_qa); result=read_json(runner.path(args.batch)/'report.json')
            elif args.command=='batch-status':
                state=read_json(runner.path(args.batch)/'batch.json'); result=read_json(runner.path(args.batch)/'report.json')
            elif args.command=='batch-audit': result=runner.audit(args.batch)
            else: result=runner.acknowledge_review(args.batch,args.reviewer)
        elif args.command.startswith('editorial-'):
            from .editorial import Editorial
            from .editorial_media import variant_identity
            from .io import read_json,write_json
            editor=Editorial(project.root)
            if args.command=='editorial-init':
                editor.initialize(); result={'status':'initialized','baseline_cards':100,'new_approvals':0}
            elif args.command=='editorial-import': result=editor.sync(args.path)
            elif args.command=='editorial-status':
                previews=editor.render(); state=editor.state(); write_json(project.root/'build/editorial/status.json',state)
                result={'champions':state['champions'],'previews':previews,'model_calls':0}
            elif args.command=='editorial-media-tasks':
                from .editorial_research import report_tasks
                tasks=report_tasks(project.root); result={'manual_tasks':len(tasks['tasks']),'model_calls':0,'report':'data/editorial/research/aphelios-media-tasks.json'}
            elif args.command=='editorial-serve':
                from .editorial_server import serve
                serve(project.root,args.port); return 0
            elif args.command=='editorial-review':
                request=read_json(args.request); result=editor.mutate(args.card_id,request['action'],request,request.get('expected'))
                editor.render()
            elif args.command=='editorial-media-import':
                card=editor.override_card(args.card_id)
                target={'kind':'variant','identity':variant_identity(card)} if args.variant else {'kind':'card','card_id':args.card_id}
                target['role']=args.role
                result=editor.overrides.ingest(card,args.path,target,read_json(args.metadata)); editor.render()
            elif args.command=='editorial-media-approve':
                result=editor.overrides.approve(args.override,editor.override_card(args.card_id),args.reviewer,args.notes); editor.render()
            elif args.command=='editorial-propose': result=editor.propose(args.ids,inside(project.root,args.output))
            else: raise ValueError('Unknown editorial command')
        elif args.command=='migrate':
            from .migrate import migrate
            result = migrate(project)
        elif args.command=='generate-champion':
            from .generation.workflow import generate
            result = generate(project.root,args.champion,offline=args.offline,sources_only=args.sources_only,cached_sources=args.cached_sources,resume_draft=args.resume_draft)
            if result.get('output') and (project.root/'data/editorial/registry.json').exists():
                from .editorial import Editorial
                editor=Editorial(project.root)
                if any(r['champion']==result['champion']['name'] for r in editor.registry()['cards'].values()):
                    result['editorial_sync']=editor.sync(Path(result['output']))
                    result['generated_previews']=result['previews']
                    result['previews']=editor.render()[result['champion']['name'].lower()]
        elif args.command=='archive-generated-run':
            from .generation.archive import archive_run
            result = archive_run(project.root,args.path)
        elif args.command=='replay-generated-run':
            from .generation.archive import restore_inputs
            from .generation.workflow import generate
            identifier = restore_inputs(project.root,args.path)
            seed=args.path/'draft-seed.json'
            result = generate(project.root,identifier,offline=True,resume_draft=seed if seed.exists() else None)
        elif args.command=='batch01-stage':
            from .batch01 import stage
            result = stage(project,offline=args.offline)
        elif args.command in ('validate','run','build'):
            from .operations import run_pipeline
            result = run_pipeline(project,output=getattr(args,'output',None),export=args.command!='validate')
        elif args.command=='inspect-apkg':
            from .package import inspect_apkg
            result = inspect_apkg(args.path)
        elif args.command=='fetch':
            from .sources import fetch
            result = fetch(project,[n.strip() for n in args.champions.split(',') if n.strip()],args.patch,args.cdragon_version,args.offline,args.assets,args.refresh)
            print(json.dumps({'entities':len(result['entities']),'resources':len(result['resources']),
                              'errors':result['errors'],'report':'build/retrieval.json'},ensure_ascii=False,indent=2))
            return int(bool(result['errors']))
        elif args.command=='archive-wiki':
            from .sources import archive_wiki
            result = archive_wiki(project,args.url,args.revision,args.patch,args.offline)
        elif args.command=='prepare-media':
            from .media import prepare
            target = inside(project.root,args.output)
            if not target.is_relative_to(project.root/'build'):
                raise ValueError('Converted media must be staged under build/')
            result = prepare(project,target)
        elif args.command=='propose':
            from .review import propose
            target = inside(project.root,args.output)
            if not target.is_relative_to(project.root/'build'):
                raise ValueError('Proposals must be staged under build/')
            result = propose(project,args.candidate,target)
        elif args.command=='apply-review':
            from .review import apply_review
            result = apply_review(project,args.proposal,args.accept,args.reviewer,args.notes)
        logging.info('%s completed',args.command)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        if args.command=='evaluate-author': return int(result.get('status')=='failed')
        if args.command=='staging-batch': return int(bool(result.get('errors')))
        return int(bool(result.get('failed_champions') or result.get('errors'))) if args.command in ('batch-run','batch-audit') else 0
    except (OSError,ValueError,KeyError,RuntimeError) as ex:
        logging.error('%s failed: %s',args.command,ex)
        print(f'ERROR: {ex}')
        return 1
