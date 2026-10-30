"""Outcome, historic-scope and current-acceptance boundaries for v2 evidence."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import current_publication_readiness as readiness
from tests import test_current_publication_readiness as fixtures

HISTORICAL_LEDGER = 'reports/current-publication-validation/readiness-reconciliation-20261029/commands.json'
HISTORICAL_SHA256 = 'e9acbcd2344354a777f382fb58a95f5c4d44515a216d49f76ba8272f9ddd8b7c'


class CurrentEvidenceDependencyContractTests(unittest.TestCase):
    def setUp(self):
        custody = patch.object(readiness, "native_ledger_errors", return_value=[])
        custody.start()
        self.addCleanup(custody.stop)

    def test_original_316_receipts_remain_pinned_history_without_current_applicability(self):
        path = ROOT / HISTORICAL_LEDGER
        before = path.read_bytes()
        document = json.loads(before)
        self.assertEqual(len(document['input_sha256']), 316)
        self.assertEqual(len(document['commands']), 8)
        self.assertEqual(readiness.historical_validation_errors(path, HISTORICAL_SHA256), [])
        self.assertTrue(readiness.historical_validation_errors(path, '0' * 64))
        with patch.object(readiness.scopes, 'ledger_inputs', return_value=document['input_sha256']), \
                patch.object(readiness.scopes, 'role_inputs', return_value=document['input_sha256']), \
                patch.object(readiness.scopes, 'scope_declaration', side_effect=lambda root, role: {'schema_version': 2, 'profile': readiness.scopes.PROFILE, 'role': role}):
            issues = readiness.validation_errors(document)
        self.assertTrue(any('legacy receipts are historical only' in issue for issue in issues))
        self.assertEqual(path.read_bytes(), before)

    def test_current_receipt_cannot_claim_future_inputs_or_forge_scope(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            good = fixtures.PublicationEvidenceTests().command_fixture(root)
            inputs = good['input_sha256']
            with patch.object(readiness.scopes, 'execution_tools', return_value={}), \
                    patch.object(readiness.scopes, 'execution_environment', return_value={}), \
                    patch.object(readiness.scopes, 'ledger_inputs', return_value=inputs), \
                    patch.object(readiness.scopes, 'role_inputs', return_value=inputs), \
                    patch.object(readiness.scopes, 'scope_declaration', side_effect=lambda root, role: {'schema_version': 2, 'profile': readiness.scopes.PROFILE, 'role': role}):
                self.assertEqual(readiness.validation_errors(good, root, 'candidate'), [])
                for field in ('input_sha256_after', 'expected_input_sha256', 'input_sha256'):
                    bad = copy.deepcopy(good)
                    bad['commands'][0][field]['future-retained-object'] = 'f' * 64
                    self.assertTrue(readiness.validation_errors(bad, root, 'candidate'))
                bad = copy.deepcopy(good)
                bad['commands'][0]['input_scope']['paths'] = []
                self.assertTrue(readiness.validation_errors(bad, root, 'candidate'))
                for field in ('execution_tools_before', 'execution_tools_after',
                              'expected_execution_tools', 'execution_environment_before',
                              'execution_environment_after', 'expected_execution_environment'):
                    bad = copy.deepcopy(good)
                    bad['commands'][0][field] = {'changed': True}
                    self.assertTrue(readiness.validation_errors(bad, root, 'candidate'))
                (root / 'tool.py').write_text('materially changed genuine input\n')
                self.assertTrue(readiness.validation_errors(good, root, 'candidate'))

    def test_native_custody_failure_cannot_be_hidden_by_current_scope_bindings(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            good = fixtures.PublicationEvidenceTests().command_fixture(root)
            inputs = good['input_sha256']
            with patch.object(readiness, 'native_ledger_errors', return_value=['Native validation custody: forged capture']), \
                    patch.object(readiness.scopes, 'execution_tools', return_value={}), \
                    patch.object(readiness.scopes, 'execution_environment', return_value={}), \
                    patch.object(readiness.scopes, 'ledger_inputs', return_value=inputs), \
                    patch.object(readiness.scopes, 'role_inputs', return_value=inputs), \
                    patch.object(readiness.scopes, 'scope_declaration', side_effect=lambda root, role: {'schema_version': 2, 'profile': readiness.scopes.PROFILE, 'role': role}):
                self.assertEqual(readiness.validation_errors(good, root, 'candidate'),
                                 ['Native validation custody: forged capture'])

    def command_report(self, root, *, code=2, execution='completed', payload=None):
        payload = {'status': 'profile_failure'} if payload is None else payload
        stdout = root / 'stdout.json'
        stdout.write_text(json.dumps(payload))
        command = {'command': ['java', 'CurrentSemanticReasoner'], 'returncode': code,
                   'execution_status': execution,
                   'stdout': {'path': stdout.name, 'sha256': hashlib.sha256(stdout.read_bytes()).hexdigest()}}
        path = root / 'slot.command.json'
        path.write_text(json.dumps(command))
        return {'status': 'FAIL', 'evidence_files': [
            {'path': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}]}

    def test_completed_fail_is_distinct_from_signals_timeouts_and_missing_payloads(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.assertEqual(readiness.semantic_completion_errors(self.command_report(root), root), [])
            technical = self.command_report(root, payload={
                'status': 'technical_failure', 'error': 'java.lang.IllegalArgumentException: unsupported query'})
            self.assertEqual(readiness.semantic_completion_errors(technical, root), [])
            for kwargs in ({'code': -15}, {'code': 143}, {'code': True}, {'execution': 'timeout'},
                           {'payload': {}}, {'payload': {'status': 'technical_failure'}},
                           {'code': 0}, {'code': 2, 'payload': {'status': 'consistent'}}):
                with self.subTest(kwargs=kwargs):
                    self.assertTrue(readiness.semantic_completion_errors(self.command_report(root, **kwargs), root))
            report = self.command_report(root)
            (root / 'stdout.json').unlink()
            self.assertTrue(readiness.semantic_completion_errors(report, root))
            self.assertTrue(readiness.semantic_completion_errors({'status': 'FAIL'}, root))

    def test_diagnostic_classification_preserves_all_failures_and_fails_closed(self):
        result = readiness.classify_diagnostics(
            ['profile failure', 'stale receipt', 'unknown', 'overlap', 'profile failure'],
            ['stale receipt', 'overlap'], ['profile failure', 'overlap'])
        self.assertEqual(result['class_a_count'], 3)
        self.assertEqual(result['class_b_count'], 1)
        self.assertEqual([row['message'] for row in result['diagnostics']],
                         ['profile failure', 'stale receipt', 'unknown', 'overlap'])

    def test_completed_nonzero_outcomes_require_prior_authentication(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            report = self.command_report(root)
            self.assertEqual(readiness.completed_outcome_diagnostics(report, root, []),
                             {'Semantic command did not complete successfully: slot.command.json'})
            self.assertEqual(readiness.completed_outcome_diagnostics(report, root, ['invalid custody']), set())
            for code in (0, -15, 143, True):
                self.assertEqual(readiness.completed_outcome_diagnostics(
                    self.command_report(root, code=code), root, []), set())

    def test_authenticated_completed_fail_cannot_make_publication_ready(self):
        # All nonsemantic criteria are deliberately satisfied. Authentication
        # success must still never turn an actual FAIL into publication READY.
        cov = {'summary': {'source_assessment_equality': True, 'source_term_count': 91,
                          'review_states': {'final': 91, 'deferred': 0, 'unreviewed': 0}}}
        rat = {'summary': {'human_review_required_proposals': 0}}
        report = {'status': 'FAIL', 'blockers': ['actual profile failure'], 'hierarchy_runs': {},
                  'conservativity': {side: {'status': 'PASS', 'additions_count': 0, 'losses_count': 0}
                                     for side in ('source', 'target')}}
        original_read = readiness.read
        def read(path):
            if path == ROOT / 'semantic-fixture':
                return report
            if path == ROOT / 'validation-fixture':
                return {'declared_environment_match': True}
            return original_read(path)
        with patch.object(readiness, 'read', side_effect=read), \
                patch.object(readiness, 'selected_evidence', return_value=(ROOT / 'semantic-fixture', ROOT / 'validation-fixture', {})), \
                patch.object(Path, 'exists', return_value=True), \
                patch.object(readiness, 'check_record', return_value=[]), \
                patch.object(readiness.assessment, 'build_reports', return_value=(cov, rat, {'item_count': 0}, {})), \
                patch.object(readiness.semantic, 'validate_stored', return_value=[]), \
                patch.object(readiness.semantic, 'validate_publication_execution_bindings', return_value=[]), \
                patch.object(readiness, 'semantic_completion_errors', return_value=[]), \
                patch.object(readiness, 'validation_errors', return_value=[]), \
                patch.object(readiness, 'preservation', return_value={'status': 'PASS', 'errors': []}), \
                patch.object(readiness, 'examples_pass', return_value=True), \
                patch.object(readiness, 'expectations_pass', return_value=True):
            result = readiness.evaluate()
        self.assertEqual(result['semantic']['status'], 'FAIL')
        self.assertEqual(result['verdict'], readiness.NOT_READY)
        self.assertIn('actual profile failure', result['blockers'])
        self.assertEqual(result['diagnostic_classification']['class_a_count'], 0)
        self.assertEqual(result['diagnostic_classification']['class_b_count'], 1)


if __name__ == '__main__':
    unittest.main()
