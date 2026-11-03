import copy
import unittest
from helpers import sandbox_project
from lol_anki.io import canonical, digest, read_json, write_json
from lol_anki.review import propose, apply_review
from lol_anki.validation import validate


class ReviewTests(unittest.TestCase):
    def make_proposal(self,project):
        candidate = copy.deepcopy(project.content())
        candidate['cards'][0]['row']['answer'] += ' Editorial test.'
        path = project.root/'candidate.json'; write_json(path,candidate)
        result = propose(project,path,project.root/'proposal')
        return result,project.root/'proposal/proposal.json'

    def test_hash_bound_apply_changes_only_reviewed_card_and_advances_mod(self):
        with sandbox_project() as project:
            original = project.content()
            result,path = self.make_proposal(project)
            apply_review(project,path,result['accept_token'],'Test reviewer')
            after = project.content()
            self.assertEqual(original['cards'][1:],after['cards'][1:])
            self.assertGreater(after['cards'][0]['revision'],original['build_epoch'])
            self.assertEqual(validate(project)['errors'],0)
            receipt = read_json(project.root/'data/reviews'/result['accept_token']/'receipt.json')
            self.assertEqual(receipt['after_sha256'],digest(canonical(after)))
            self.assertEqual(digest(canonical(read_json(project.root/'data/reviews'/result['accept_token']/'proposal.json'))),result['accept_token'])
            with self.assertRaises(ValueError):
                apply_review(project,path,result['accept_token'],'Test reviewer')

    def test_tampered_or_unaccepted_proposal_fails(self):
        with sandbox_project() as project:
            result,path = self.make_proposal(project)
            before = project.path('content').read_bytes()
            with self.assertRaises(ValueError):
                apply_review(project,path,'wrong hash','Test reviewer')
            proposal = read_json(path); proposal['candidate']['cards'][0]['row']['answer']='tampered'
            write_json(path,proposal)
            with self.assertRaises(ValueError):
                apply_review(project,path,result['accept_token'],'Test reviewer')
            self.assertEqual(before,project.path('content').read_bytes())

    def test_stale_base_or_sources_fails(self):
        with sandbox_project() as project:
            result,path = self.make_proposal(project)
            current = project.content(); current['cards'][0]['row']['answer']='independent edit'
            write_json(project.path('content'),current)
            with self.assertRaisesRegex(ValueError,'Stale'):
                apply_review(project,path,result['accept_token'],'Test reviewer')
