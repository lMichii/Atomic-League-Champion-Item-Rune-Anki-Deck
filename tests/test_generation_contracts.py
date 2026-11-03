import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from lol_anki.generation.ai import AIClient,ModelError
from lol_anki.generation.contracts import obj,string,schema_check,numeric_tokens
from lol_anki.generation.evidence import resolve,wiki_sections
from lol_anki.generation.workflow import stable_key
from lol_anki.io import read_json,write_json,canonical,digest
from lol_anki.project import ROOT,Project
from lol_anki.review import apply_review


class GenerationContractTests(unittest.TestCase):
    def test_resumed_schema_repair_uses_prior_validation_feedback(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as tmp:
            client=AIClient({'provider':'codex','attempts':1,'model':''},Path(tmp))
            schema=obj({'text':string(3,20)})
            with patch.object(client,'_codex',return_value=({'text':'x'},{})):
                with self.assertRaises(ModelError): client.generate('test','generic',{},schema)
            with patch.object(client,'_codex',return_value=({'text':'valid'},{})):
                _,receipt=client.generate('test','generic',{},schema)
            prompt=(Path(tmp)/receipt['request_sha256']/'attempt-2/prompt.txt').read_text('utf-8')
            self.assertIn('validation_errors',prompt)
            self.assertIn('invalid string length',prompt)

    def test_resuming_a_failed_request_preserves_prior_attempts_and_error_history(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as tmp:
            cfg={'provider':'codex','attempts':1,'model':'','timeout_seconds':5}
            client=AIClient(cfg,Path(tmp)); schema=obj({'text':string(3,20)})
            with patch.object(client,'_codex',side_effect=ModelError('temporary usage limit')):
                with self.assertRaises(ModelError): client.generate('test','generic',{},schema)
            error=next(Path(tmp).glob('*/attempt-1/error.json')); before=error.read_bytes()
            with patch.object(client,'_codex',return_value=({'text':'valid'},{'usage':[{'input_tokens':20,'output_tokens':4}]})):
                _,receipt=client.generate('test','generic',{},schema)
            self.assertEqual(error.read_bytes(),before)
            self.assertEqual(receipt['attempts'],2)
            self.assertEqual(receipt['execution_attempts'],1)
            self.assertIn('temporary usage limit',receipt['prior_errors'])
            folder=Path(tmp)/receipt['request_sha256']
            self.assertTrue((folder/'attempt-2/metadata.json').exists())
            self.assertNotIn('validation_errors',(folder/'attempt-2/prompt.txt').read_text('utf-8'))

    def test_provider_schema_retries_records_repair_and_replays_without_model(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as tmp:
            cfg={'provider':'codex','attempts':2,'model':'','timeout_seconds':5}
            client=AIClient(cfg,Path(tmp))
            schema=obj({'text':string(3,20)})
            with patch.object(client,'_codex',side_effect=[({'extra':'bad'},{}),({'text':'valid'}, {'test_transport':True})]) as call,patch('time.sleep'):
                value,receipt=client.generate('test','generic prompt',{'input':'test'},schema)
                self.assertEqual(call.call_count,2)
                self.assertEqual(receipt['attempts'],2)
                self.assertEqual(len(receipt['prior_errors']),1)
            folder=Path(tmp)/receipt['request_sha256']
            self.assertTrue((folder/'attempt-1/error.json').exists())
            self.assertIn('validation_errors',(folder/'attempt-2/prompt.txt').read_text('utf-8'))
            with patch.object(client,'_codex',side_effect=AssertionError('Unexpected live call')):
                self.assertEqual(client.generate('test','generic prompt',{'input':'test'},schema)[0],value)
            cached=read_json(folder/'accepted.json'); cached['text']='tampered'; write_json(folder/'accepted.json',cached)
            with self.assertRaisesRegex(ModelError,'hash mismatch'):
                client.generate('test','generic prompt',{'input':'test'},schema)

    def test_offline_model_miss_and_exhausted_attempts_fail_without_canned_content(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as tmp:
            cfg={'provider':'codex','attempts':2,'model':'','timeout_seconds':5}
            schema=obj({'text':string(3,20)})
            with self.assertRaisesRegex(ModelError,'Offline'):
                AIClient(cfg,Path(tmp),offline=True).generate('test','generic',{},schema)
            client=AIClient(cfg,Path(tmp))
            with patch.object(client,'_codex',side_effect=ModelError('test failure')),patch('time.sleep'):
                with self.assertRaisesRegex(ModelError,'after 2 attempts'):
                    client.generate('test','generic',{},schema)
            self.assertFalse(list(Path(tmp).glob('*/accepted.json')))

    def test_numeric_identity_resolution_is_independent_of_prose_and_patch(self):
        index={'data':{'Braum':{'id':'Braum','key':'201','name':'Braum'},'MonkeyKing':{'id':'MonkeyKing','key':'62','name':'Wukong'}}}
        for identifier in ('braum','BRAUM','201'):
            self.assertEqual(resolve(index,identifier)['key'],'201')
        self.assertEqual(resolve(index,'Wukong')['id'],'MonkeyKing')
        self.assertEqual(stable_key(201,'L1','-'),'champ:201:overview:L1')
        self.assertEqual(stable_key(201,'L2','P'),'champ:201:p:recognize:L2')
        for identifier in ('all','Braum,Ahri','../private','unknown'):
            with self.assertRaises(ValueError): resolve(index,identifier)

    def test_wiki_parser_uses_live_sections_and_rejects_missing_headings(self):
        names=['Passive One','Ability Q','Ability W','Ability E','Ability R']
        page=('<h2>Abilities[edit]</h2>'+''.join(f'<h3>{name}</h3><p>Active: Evidence for {name}.</p>' for name in names)+'<h2>Patch history</h2><p>Old unsupported history</p>').encode()
        sections=wiki_sections(page,names)
        self.assertEqual(len(sections),5)
        self.assertNotIn('unsupported history',sections[-1]['excerpt'])
        with self.assertRaises(ValueError): wiki_sections(page,['Missing']*5)

    def test_schema_rejects_extra_fields_boolean_integer_and_wrong_counts(self):
        with self.assertRaises(ValueError): schema_check({'text':'valid','extra':1},obj({'text':string()}))
        with self.assertRaises(ValueError): schema_check(True,{'type':'integer'})
        self.assertEqual(numeric_tokens('four stacks, 25% damage'),{'4','25%'})

    def test_generated_proposal_cannot_be_auto_approved_even_with_exact_hash(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as tmp:
            proposal={'kind':'champion_draft','candidate':{},'approval_required':True}
            path=Path(tmp)/'proposal.json'; write_json(path,proposal)
            before=Project(profile='batch01').path('content').read_bytes()
            with self.assertRaisesRegex(ValueError,'cannot be auto-approved'):
                apply_review(Project(profile='batch01'),path,digest(canonical(proposal)),'Test reviewer')
            self.assertEqual(before,Project(profile='batch01').path('content').read_bytes())
