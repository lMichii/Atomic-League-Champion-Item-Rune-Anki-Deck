"""Author comparisons stay separate from production, using retained real fixtures."""
from pathlib import Path
import tempfile
import shutil
import unittest
from unittest.mock import patch
from lol_anki.io import read_json,digest,write_json
from lol_anki.model_eval import evaluate_author
from lol_anki.project import ROOT


class ModelEvaluationTests(unittest.TestCase):
    def test_evaluation_preserves_reviews_configuration_and_source_archive(self):
        index=read_json(ROOT/'data/drafts/annie/index.json')
        archive=ROOT/'data/drafts/annie'/index['current_run']
        draft=read_json(archive/'ai-draft.json'); verification=read_json(archive/'ai-verification.json')
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as tmp:
            root=Path(tmp); shutil.copy2(ROOT/'generation.toml',root/'generation.toml')
            target=root/'data/drafts/annie'/archive.name; shutil.copytree(archive,target)
            write_json(root/'data/editorial/registry.json',{'cards':{},'events':[]})
            write_json(root/'data/content/editorial.json',{'cards':[]})
            protected=[root/'generation.toml',root/'data/editorial/registry.json',root/'data/content/editorial.json',target/'cards.json']
            before={p:digest(p.read_bytes()) for p in protected}
            with patch('lol_anki.generation.ai.AIClient._codex',side_effect=[(draft,{'usage':[{'input_tokens':100,'output_tokens':20}]}),(verification,{'usage':[{'input_tokens':200,'output_tokens':30}]})]) as call:
                result=evaluate_author(root,target,'fixture-author','fixture-verifier',root/'build/evaluation')
            self.assertEqual(call.call_count,2)
            self.assertEqual(result['status'],'evaluated')
            self.assertTrue(result['schema_and_citations_passed'])
            self.assertEqual(result['editorial_imports'],0)
            self.assertFalse(result['human_approved'])
            self.assertEqual(result['available_new_attempt_usage']['fixture-author']['input_tokens'],100)
            with patch('lol_anki.generation.ai.AIClient._codex',side_effect=AssertionError('Unexpected repeated model call')):
                replay=evaluate_author(root,target,'fixture-author','fixture-verifier',root/'build/evaluation')
            self.assertTrue(replay['reused_report']); self.assertEqual(replay['new_execution_model_attempts'],0)
            self.assertEqual(before,{p:digest(p.read_bytes()) for p in protected})

    def test_experiment_output_cannot_overwrite_an_archive(self):
        index=read_json(ROOT/'data/drafts/annie/index.json'); archive=ROOT/'data/drafts/annie'/index['current_run']
        with self.assertRaisesRegex(ValueError,'Keep experiments'):
            evaluate_author(ROOT,archive,'fixture','fixture',archive)
