"""Local proposal inspection/apply/export coordinator; core checks stay shared."""
from pathlib import Path
import secrets
from .editorial import EDITABLE
from .io import canonical, digest, inside, read_json, write_json
from .operations import serialized, run_pipeline
from .project import Project
from .review import inspect_review, apply_review


class EditorialExport:
    def __init__(self, editor):
        self.editor = editor
        self.root = editor.root
        self.project = Project(self.root, profile='editorial')
        self.folder = self.root/'build/editorial/workflow'
        self.inspections = {}  # Session-scoped; a restart requires fresh inspection.

    def record_path(self, key):
        if len(key) != 32 or any(c not in '0123456789abcdef' for c in key):
            raise ValueError('Unknown proposal')
        return self.folder/(key+'.json')

    def record(self, key):
        return read_json(self.record_path(key))

    def list(self):
        return [self.public(read_json(p)) for p in sorted(self.folder.glob('*.json'), reverse=True)]

    def public(self, record):
        return {k: v for k, v in record.items() if k != 'proposal_path'}

    def store_hashes(self):
        return {k: digest(self.project.path(k).read_bytes()) for k in ('content','sources','lock')}

    @serialized
    def create(self, ids):
        if not ids or len(ids) != len(set(ids)):
            raise ValueError('Select distinct reviewed cards to propose')
        key = secrets.token_hex(16)
        folder = self.root/'build/editorial/reviews'/key
        proposed = self.editor.propose(ids, folder)
        record = {'id': key, 'status': 'proposed', 'accept_token': proposed['accept_token'],
                  'proposal_path': Path(proposed['proposal']).relative_to(self.root).as_posix(),
                  'changed_ids': proposed['changed_ids']}
        write_json(self.record_path(key), record)
        return self.public(record)

    @serialized
    def inspect(self, key):
        record = self.record(key)
        if record['status'] != 'proposed':
            return self.public(record)
        checked = inspect_review(self.project, inside(self.root, record['proposal_path']), record['accept_token'])
        proposal = checked['proposal']; current = checked['current']
        old = {c['id']: c for c in current['cards']}
        new = {c['id']: c for c in proposal['candidate']['cards']}
        groups = {'added': sorted(new.keys()-old.keys()), 'removed': sorted(old.keys()-new.keys()),
                  'modified': sorted(k for k in old.keys() & new.keys() if old[k] != new[k])}
        cards = []
        for card_id in proposal['changed_ids']:
            before = old.get(card_id); after = new.get(card_id)
            card = after or before
            columns = sorted(EDITABLE | {'media_path','icon_path','visual_cue_media_path','patch','ability'})
            diffs = [{'field': f, 'before': before['row'].get(f) if before else None,
                      'after': after['row'].get(f) if after else None}
                     for f in columns if (before['row'].get(f) if before else None) != (after['row'].get(f) if after else None)]
            cards.append({'id': card_id, 'champion': card['row']['champion'], 'level': card['row']['level'],
                          'ability': card['row']['ability'], 'diffs': diffs,
                          'change': next(k for k, ids in groups.items() if card_id in ids)})
        report = checked['validation']
        inspection = secrets.token_urlsafe(32)
        self.inspections[key] = {'token': inspection, 'accept': record['accept_token']}
        return {**self.public(record), 'inspection_token': inspection, 'groups': groups, 'cards': cards,
                'before_count': len(old), 'after_count': len(new), 'validation': report,
                'can_apply': bool(proposal['changed_ids']) and not report['errors'],
                'diff_url': f'/api/proposal-file?id={key}&file=changes.diff',
                'source_diff_url': f'/api/proposal-file?id={key}&file=sources.diff'}

    @serialized
    def apply(self, key, accept, inspection, reviewer, confirmed, notes=''):
        if not reviewer.strip(): raise ValueError('Reviewer name is required')
        if confirmed is not True: raise ValueError('Confirm that you inspected the proposed changes and warnings')
        record = self.record(key)
        if record['status'] != 'proposed': raise ValueError('Proposal has already been applied; reload its result')
        seen = self.inspections.get(key)
        if not seen or not secrets.compare_digest(str(inspection), seen['token']) or accept != seen['accept'] or accept != record['accept_token']:
            raise ValueError('Inspect this exact proposal in the current session before applying it')
        result = apply_review(self.project, inside(self.root, record['proposal_path']), accept, reviewer.strip(), notes)
        if result['status'] != 'applied': raise ValueError('Proposal contains no changes to apply')
        record.update(status='applied', apply_result=result, approved_store=self.store_hashes())
        write_json(self.record_path(key), record)
        self.inspections.pop(key, None)
        return self.public(record)

    @serialized
    def build(self, key, reviewer, notes=''):
        if not reviewer.strip(): raise ValueError('Reviewer name is required')
        record = self.record(key)
        if record['status'] != 'applied': raise ValueError('Apply this reviewed proposal before building; a completed export cannot be resubmitted')
        if record['approved_store'] != self.store_hashes(): raise ValueError('Approved store changed after applying this proposal; inspect and apply a fresh proposal before exporting')
        # Dedicated, proposal-addressed output; never overwrite production packages.
        count = len(self.project.content()['cards'])
        output = self.root/'build/editorial/exports'/record['accept_token']/f'LoL_Reviewed_{count}.apkg'
        result = run_pipeline(self.project, output=output)
        record.update(status='built', build_result=result, export_review={'reviewer': reviewer.strip(), 'notes': notes},
                      download_url=f'/api/download?id={key}')
        write_json(self.record_path(key), record)
        return self.public(record)

    @serialized
    def download(self, key):
        record = self.record(key)
        if record['status'] != 'built': raise ValueError('No completed export for this proposal')
        path = inside(self.root/'build/editorial/exports', record['build_result']['output'])
        blob = path.read_bytes()
        if digest(blob) != record['build_result']['package']['sha256']: raise ValueError('Export file changed; download blocked')
        return path.name, blob

    def proposal_file(self, key, name):
        if name not in ('changes.diff', 'sources.diff'): raise ValueError('Unknown proposal file')
        record = self.record(key)
        return (inside(self.root, record['proposal_path']).parent/name).read_bytes()
