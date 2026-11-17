import os,tempfile
os.environ['DATA_DIR']=tempfile.mkdtemp(prefix='eval-test-')
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app import app
from evaluator import CASES,grade,evaluate


class EvaluationTests(unittest.TestCase):
    def setUp(self):self.client=TestClient(app)
    def test_grader_rejects_unknown_citation(self):
        result=grade({'answer':'14 days','citations':['invented']},CASES[0]);self.assertFalse(result['passed']);self.assertEqual(result['unsupported_reference_count'],1)
    def test_negation_catches_yes(self):self.assertFalse(grade({'answer':'Yes','citations':['shipping-1']},CASES[4])['passed'])
    def test_fixture_results_are_explicit(self):
        report=evaluate(False,3);self.assertEqual(report['mode'],'fixture');self.assertEqual(report['summary']['grounded']['pass_rate'],1)
        self.assertTrue(report['mlflow_run_id']);self.assertEqual(len(report['dataset_sha256']),64)
    def test_live_limit(self):
        with self.assertRaises(ValueError):evaluate(True,5)
    def test_live_requires_operator(self):self.assertEqual(self.client.post('/api/evaluate',json={'live':True,'limit':2}).status_code,403)
    @patch('evaluator.provider',side_effect=RuntimeError('do not leak provider data'))
    def test_provider_failures_are_measured(self,mock):
        report=evaluate(True,1);self.assertEqual(report['summary']['baseline']['errors'],1);self.assertEqual(report['summary']['baseline']['pass_rate'],0)
        self.assertNotIn('do not leak',str(report))
    def test_owned_record_access(self):
        run=self.client.post('/api/evaluate',json={'limit':1}).json()
        self.assertEqual(self.client.get('/api/runs/'+run['id']).status_code,404)
        self.assertEqual(self.client.get('/api/runs/'+run['id'],headers={'X-Run-Token':run['token']}).status_code,200)
    def test_compare_rejects_different_datasets(self):
        left=self.client.post('/api/evaluate',json={'limit':1}).json();right=self.client.post('/api/evaluate',json={'limit':2}).json()
        result=self.client.post('/api/compare',json={'left_id':left['id'],'left_token':left['token'],'right_id':right['id'],'right_token':right['token']})
        self.assertEqual(result.status_code,422)


if __name__=='__main__':unittest.main()
