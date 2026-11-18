import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('local_evaluation',Path(__file__).resolve().parents[1]/'scripts/run_local_evaluation.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class LocalEvaluationTests(unittest.TestCase):
    def test_dataset_is_balanced_and_ids_unique(self):
        cases=module.build_cases()
        self.assertEqual(len(cases),40)
        self.assertEqual(len({c['id'] for c in cases}),40)
        self.assertEqual(set(module.Counter(c['category'] for c in cases).values()),{5})

    def test_correct_value_with_wrong_source_fails(self):
        case=module.build_cases()[0]
        result=module.grade({'answer':case['accepted_answers'][0],'citations':['invented']},case)
        self.assertTrue(result['strict_answer_match'])
        self.assertFalse(result['passed'])

    def test_multi_source_requires_both_references(self):
        case=next(c for c in module.build_cases() if c['category']=='multi_source')
        self.assertFalse(module.grade({'answer':case['accepted_answers'][0],'citations':case['expected_citations'][:1]},case)['passed'])
        self.assertTrue(module.grade({'answer':case['accepted_answers'][0],'citations':case['expected_citations']},case)['passed'])

    def test_abstention_must_not_cite_irrelevant_evidence(self):
        case=next(c for c in module.build_cases() if c['category']=='missing_evidence')
        self.assertTrue(module.grade({'answer':'Insufficient evidence','citations':[]},case)['passed'])
        self.assertFalse(module.grade({'answer':'Insufficient evidence','citations':['plan-0']},case)['passed'])

    def test_invalid_output_and_wrong_units_fail(self):
        case=next(c for c in module.build_cases() if c['category']=='currency_units')
        self.assertFalse(module.grade(None,case)['passed'])
        self.assertFalse(module.grade({'answer':'15 USD','citations':case['expected_citations']},case)['passed'])

    def test_strict_metric_does_not_silently_accept_verbose_answers(self):
        case=module.build_cases()[0]
        self.assertFalse(module.grade({'answer':'The trial lasts 9 days','citations':case['expected_citations']},case)['strict_answer_match'])

if __name__=='__main__':unittest.main()
