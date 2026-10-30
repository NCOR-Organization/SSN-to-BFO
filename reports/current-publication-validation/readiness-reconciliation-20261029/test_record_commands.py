#!/usr/bin/env python3
"""Report-local issuance regressions; no production policy or reasoner execution.

Temporary fixtures execute short Python children. Required role names remain
unchanged; only their argv are mocked locally so tests never launch full gates.
"""
from __future__ import annotations

import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import record_commands as issuance


def encoded(document):
    return (json.dumps(document, sort_keys=True) + '\n').encode()


class ReadinessIssuanceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='readiness-issuance-fixture-')
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name).resolve()
        self.root = self.base / 'repository'
        self.root.mkdir()
        self.directory = self.root / 'reports/current-publication-validation/readiness-reconciliation-20261029'
        self.directory.mkdir(parents=True)
        self.source = self.base / 'original-executions'
        self.source.mkdir()
        self.put('fixture.py', b'# governed fixture\n')
        self.inputs = {'fixture.py': issuance.digest((self.root / 'fixture.py').read_bytes())}
        self.head = 'a' * 40
        self.authorization = b'Explicit synthetic authorization for this isolated fixture.\n'
        (self.directory / 'authorized-request.txt').write_bytes(self.authorization)
        for name in ('record_commands.py', 'test_record_commands.py'):
            (self.directory / name).write_bytes(Path(__file__).with_name(name).read_bytes())
        original_semantic = 'reports/current-ssn-sosa-semantic-validation.json'
        original_validation = 'reports/current-publication-validation/commands.json'
        self.put(original_semantic, encoded({'status': 'FAIL', 'historical': True}))
        self.put(original_validation, encoded({'commands': [], 'historical': True}))
        old_semantic = 'reports/current-publication-validation/old/semantic.json'
        old_validation = 'reports/current-publication-validation/old/commands.json'
        self.put(old_semantic, encoded({'execution_evidence_schema': 2, 'status': 'FAIL'}))
        self.put(old_validation, encoded({'commands': [], 'head': 'older'}))
        self.predecessors = {'semantic': self.reference(original_semantic),
                             'validation': self.reference(original_validation)}
        self.old_selector = {'schema_version': 1, 'semantic': self.reference(old_semantic),
                             'validation': self.reference(old_validation),
                             'predecessors': self.predecessors}
        self.selector_path = self.root / issuance.readiness.CURRENT_EVIDENCE
        self.selector_path.write_bytes(encoded(self.old_selector))
        self.old_selector_bytes = self.selector_path.read_bytes()
        self.old_files = {path: (self.root / path).read_bytes() for path in
                          (original_semantic, original_validation, old_semantic, old_validation)}
        self.required = {name: ['python', '-B', '-c', 'print(' + repr(name) + ')']
                         for name in issuance.readiness.REQUIRED_COMMANDS}
        recorder = b'# Exact synthetic external recorder fixture.\n'
        (self.source / 'run_validation.py').write_bytes(recorder)
        self.policies = {}
        for role, name in [('full_repository_gate', 'canonical_make_check'), ('static_checks', 'separate_compile')]:
            argv = [sys.executable, *self.required[role][1:]]
            started = datetime.now(timezone.utc).isoformat()
            child = subprocess.run(argv, cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.assertEqual(child.returncode, 0)
            log = self.source / (name + '.log')
            log.write_bytes(child.stdout)
            document = {
                'name': name, 'command': argv, 'cwd': str(self.root),
                'head_before': self.head, 'head_after': self.head,
                'input_sha256_before': self.inputs, 'input_sha256_after': self.inputs,
                'input_drift': [], 'integrity_errors': [], 'returncode': child.returncode,
                'started_at_utc': started, 'completed_at_utc': datetime.now(timezone.utc).isoformat(),
                'elapsed_seconds': 0.1, 'log': str(log), 'log_sha256': issuance.digest(child.stdout),
                'executable': {'path': str(Path(sys.executable).resolve()),
                               'sha256': issuance.digest(Path(sys.executable).read_bytes())},
                'recorder': {'path': str(self.source / 'run_validation.py'), 'sha256': issuance.digest(recorder)},
                'scope': 'Actual short fixture execution; no real repository validation.',
            }
            payload = encoded(document)
            (self.source / (name + '.command.json')).write_bytes(payload)
            self.policies[role] = {'source_name': name, 'receipt_sha256': issuance.digest(payload),
                                   'log_sha256': issuance.digest(child.stdout)}
        self.patch(issuance, 'ROOT', self.root)
        self.patch(issuance, 'EXPECTED_ROOT', self.root)
        self.patch(issuance, 'DIRECTORY', self.directory)
        self.patch(issuance, 'EXPECTED_HEAD', self.head)
        self.patch(issuance, 'EXPECTED_INPUT_COUNT', 1)
        self.patch(issuance, 'AUTHORIZATION_SHA256', issuance.digest(self.authorization))
        self.patch(issuance, 'OLD_SELECTOR_SHA256', issuance.digest(self.old_selector_bytes))
        self.patch(issuance, 'PREDECESSORS', copy.deepcopy(self.predecessors))
        self.patch(issuance, 'SOURCE_DIRECTORY', self.source)
        self.patch(issuance, 'SOURCE_RECORDER_SHA256', issuance.digest(recorder))
        self.patch(issuance, 'IMPORTS', self.policies)
        self.patch(issuance, 'head', lambda: self.head)
        self.patch(issuance.readiness, 'ROOT', self.root)
        self.patch(issuance.readiness, 'git', lambda *args: self.head)
        self.patch(issuance.readiness, 'REQUIRED_COMMANDS', self.required)
        self.patch(issuance.readiness, 'validation_inputs', lambda root: {'fixture.py'})

    def patch(self, target, name, value):
        patcher = mock.patch.object(target, name, value)
        patcher.start()
        self.addCleanup(patcher.stop)

    def put(self, relative, payload):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)

    def reference(self, relative):
        return {'path': relative, 'sha256': issuance.digest((self.root / relative).read_bytes())}

    def complete_ledger(self):
        for role in self.required:
            result = issuance.import_record(role) if role in self.policies else issuance.record(role)
            self.assertEqual(result, 0)
        self.assertEqual(issuance.finalize(), 0)
        return issuance.read(self.directory / 'commands.json')

    def semantic_driver_fixture(self, status='PASS', evidence_files=None):
        report = self.directory / 'semantic.json'
        markdown = self.directory / 'semantic.md'
        code = ('from pathlib import Path; '
                + 'Path(' + repr(str(report)) + ').write_text(' + repr(json.dumps({
                    'execution_evidence_schema': 2, 'status': status, 'evidence_files': evidence_files or []})) + '); '
                + 'Path(' + repr(str(markdown)) + ').write_text(' + repr('Recorded outcome: ' + status) + '); '
                + 'raise SystemExit(' + str(0 if status == 'PASS' else 1) + ')')
        command = [sys.executable, '-B', '-c', code]
        self.patch(issuance, 'semantic_argv', lambda: command.copy())
        self.assertEqual(issuance.record('semantic_execution'), 0 if status == 'PASS' else 1)

    def test_real_short_execution_import_preserves_originals_and_complete_eight_roles(self):
        before = {p.name: p.read_bytes() for p in self.source.iterdir()}
        ledger = self.complete_ledger()
        self.assertEqual(len(ledger['commands']), 8)
        self.assertEqual(set(c['name'] for c in ledger['commands']), set(self.required))
        self.assertEqual(issuance.readiness.validation_errors(ledger), [])
        self.assertEqual({p.name: p.read_bytes() for p in self.source.iterdir()}, before)
        self.assertFalse(ledger['declared_environment_match'])
        for role in self.policies:
            view = issuance.read(self.directory / (role + '.command.json'))
            original = json.loads((self.source / (self.policies[role]['source_name'] + '.command.json')).read_bytes())
            self.assertEqual(view['returncode'], original['returncode'])
            self.assertEqual(view['started_at_utc'], original['started_at_utc'])
            self.assertEqual(view['expected_input_sha256'], original['input_sha256_before'])

    def test_pinned_source_bytes_prevent_forged_pass_and_log_or_recorder_substitution(self):
        good = issuance.imported_payloads('full_repository_gate', retained=False)
        for key in good:
            with self.subTest(artifact=key):
                bad = dict(good)
                bad[key] += b' '
                with self.assertRaisesRegex(ValueError, 'Pinned source'):
                    issuance.authenticate_import('full_repository_gate', bad, self.inputs)

    def test_source_contract_negatives_even_when_outer_fixture_hash_is_resealed(self):
        good = issuance.imported_payloads('full_repository_gate', retained=False)
        attacks = {
            'wrong root': lambda d: d.update(cwd=str(self.base / 'unrelated')),
            'wrong predecessor': lambda d: d.update(head_before='b' * 40),
            'unauthorized descendant': lambda d: d.update(head_after='c' * 40),
            'wrong logical role': lambda d: d.update(command=[sys.executable, '-B', '-c', 'print("wrong")']),
            'unrelated task': lambda d: d.update(name='another_task'),
            'missing command provenance': lambda d: d.pop('command'),
            'incomplete execution': lambda d: d.pop('completed_at_utc'),
            'reversed execution times': lambda d: d.update(completed_at_utc='2000-01-01T00:00:00+00:00'),
            'failed execution': lambda d: d.update(returncode=1),
            'boolean result': lambda d: d.update(returncode=False),
            'wrong input hash': lambda d: d.update(input_sha256_before={'fixture.py': '0' * 64}),
            'stale post inputs': lambda d: d.update(input_sha256_after={}),
            'input drift': lambda d: d.update(input_drift=['fixture.py']),
            'integrity failure': lambda d: d.update(integrity_errors=['failure']),
            'wrong executable bytes': lambda d: d['executable'].update(sha256='0' * 64),
            'wrong output reference': lambda d: d.update(log='/unrelated/log'),
            'missing producer provenance': lambda d: d.pop('recorder'),
        }
        for name, attack in attacks.items():
            with self.subTest(attack=name):
                document = json.loads(good['receipt'])
                attack(document)
                payloads = {**good, 'receipt': encoded(document)}
                policies = copy.deepcopy(self.policies)
                policies['full_repository_gate']['receipt_sha256'] = issuance.digest(payloads['receipt'])
                with mock.patch.object(issuance, 'IMPORTS', policies):
                    with self.assertRaises((ValueError, KeyError)):
                        issuance.authenticate_import('full_repository_gate', payloads, self.inputs)

    def test_current_input_mutation_rejects_stale_historical_pass(self):
        (self.root / 'fixture.py').write_bytes(b'# changed current implementation\n')
        with self.assertRaisesRegex(ValueError, 'inputs'):
            issuance.import_record('full_repository_gate')
        self.assertFalse((self.directory / 'full_repository_gate.command.json').exists())

    def test_authorization_and_historical_predecessor_changes_fail_closed(self):
        paths = [self.directory / 'authorized-request.txt',
                 self.root / self.predecessors['semantic']['path'],
                 self.root / self.predecessors['validation']['path'], self.selector_path]
        for path in paths:
            with self.subTest(path=path.name):
                original = path.read_bytes()
                path.write_bytes(original + b' ')
                try:
                    with self.assertRaises(ValueError):
                        issuance.authorities()
                finally:
                    path.write_bytes(original)

    def test_missing_receipt_or_required_role_cannot_finalize(self):
        issuance.import_record('full_repository_gate')
        with self.assertRaises(FileNotFoundError):
            issuance.finalize()
        self.assertFalse((self.directory / 'commands.json').exists())

    def test_duplicate_import_and_duplicate_selected_role_are_rejected(self):
        issuance.import_record('full_repository_gate')
        before = (self.directory / 'full_repository_gate.command.json').read_bytes()
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            issuance.import_record('full_repository_gate')
        self.assertEqual((self.directory / 'full_repository_gate.command.json').read_bytes(), before)
        document = issuance.read(self.directory / 'full_repository_gate.command.json')
        document['name'] = 'static_checks'
        (self.directory / 'full_repository_gate.command.json').write_bytes(encoded(document))
        with self.assertRaisesRegex(ValueError, 'wrong-role'):
            issuance.authenticate_receipt('full_repository_gate', self.inputs)

    def test_derived_view_cannot_change_outcome_or_source_reference(self):
        issuance.import_record('full_repository_gate')
        path = self.directory / 'full_repository_gate.command.json'
        original = path.read_bytes()
        for mutation in ('returncode', 'completed_at_utc', 'source_execution'):
            with self.subTest(field=mutation):
                document = json.loads(original)
                document[mutation] = 1 if mutation == 'returncode' else 'forged'
                path.write_bytes(encoded(document))
                with self.assertRaises((ValueError, TypeError)):
                    issuance.authenticate_receipt('full_repository_gate', self.inputs)
        path.write_bytes(original)

    def test_native_failure_stops_later_calls_without_fabricated_success(self):
        with mock.patch.dict(self.required, {'unit_tests': ['python', '-B', '-c', 'raise SystemExit(7)']}):
            self.assertEqual(issuance.record('unit_tests'), 7)
        receipt = issuance.read(self.directory / 'unit_tests.command.json')
        self.assertEqual(receipt['returncode'], 7)
        self.assertEqual(receipt['execution_status'], 'completed')
        self.assertTrue((self.directory / 'STOP.json').is_file())
        with self.assertRaisesRegex(ValueError, 'Stopped'):
            issuance.record('assessment')
        self.assertFalse((self.directory / 'assessment.log').exists())

    def test_semantic_failure_is_preserved_and_not_blanket_exempted(self):
        self.semantic_driver_fixture('FAIL')
        receipt = issuance.read(self.directory / 'semantic_execution.command.json')
        self.assertEqual(receipt['returncode'], 1)
        with mock.patch.object(issuance.readiness.semantic, 'validate_stored', return_value=[]), \
             mock.patch.object(issuance.readiness.semantic, 'validate_publication_execution_bindings', return_value=[]):
            _, report, _ = issuance.authenticate_semantic(self.inputs)
        self.assertEqual(report['status'], 'FAIL')
        with self.assertRaisesRegex(ValueError, 'Stopped'):
            issuance.finalize()

    def test_valid_current_pass_supersedes_historical_fail_without_rewriting_it(self):
        self.complete_ledger()
        self.semantic_driver_fixture()
        # This test exercises issuance/selection; raw semantic validation has its own focused suite.
        with mock.patch.object(issuance.readiness.semantic, 'validate_stored', return_value=[]), \
             mock.patch.object(issuance.readiness.semantic, 'validate_publication_execution_bindings', return_value=[]):
            self.assertEqual(issuance.activate(), 0)
        selected, _, metadata = issuance.readiness.selected_evidence(self.root)
        self.assertEqual(json.loads(selected.read_bytes())['status'], 'PASS')
        self.assertEqual(metadata['mode'], 'successor_records')
        self.assertEqual((self.directory / 'prior-selector.json').read_bytes(), self.old_selector_bytes)
        for path, payload in self.old_files.items():
            self.assertEqual((self.root / path).read_bytes(), payload)

    def test_semantic_report_or_current_command_custody_errors_block_activation(self):
        self.complete_ledger()
        self.semantic_driver_fixture()
        for stored, commands in [(['stale artifact'], []), ([], ['Semantic command input binding missing or stale: fixture'])]:
            with self.subTest(errors=stored + commands), \
                 mock.patch.object(issuance.readiness.semantic, 'validate_stored', return_value=stored), \
                 mock.patch.object(issuance.readiness.semantic, 'validate_publication_execution_bindings', return_value=commands):
                with self.assertRaisesRegex(ValueError, 'custody'):
                    issuance.activate()
            self.assertEqual(self.selector_path.read_bytes(), self.old_selector_bytes)

    def test_semantic_outer_receipt_missing_incomplete_wrong_role_or_wrong_output_is_rejected(self):
        self.semantic_driver_fixture()
        path = self.directory / 'semantic_execution.command.json'
        original = path.read_bytes()
        attacks = {
            'wrong role': lambda d: d.update(name='other'),
            'wrong driver': lambda d: d.update(command=[sys.executable, '-B', '-c', 'print("unrelated")']),
            'incomplete': lambda d: d.pop('completed_at_utc'),
            'wrong report hash': lambda d: d['result_artifacts'].update({issuance.relative(self.directory / 'semantic.json'): '0' * 64}),
            'wrong outcome': lambda d: d.update(returncode=1),
            'stale command map': lambda d: d.update(input_sha256={}),
        }
        with mock.patch.object(issuance.readiness.semantic, 'validate_stored', return_value=[]), \
             mock.patch.object(issuance.readiness.semantic, 'validate_publication_execution_bindings', return_value=[]):
            for name, attack in attacks.items():
                with self.subTest(attack=name):
                    document = json.loads(original)
                    attack(document)
                    path.write_bytes(encoded(document))
                    with self.assertRaises(ValueError):
                        issuance.authenticate_semantic(self.inputs)
            path.unlink()
            with self.assertRaises(FileNotFoundError):
                issuance.authenticate_semantic(self.inputs)

    def test_completed_nonzero_diagnostic_never_hides_stale_provenance(self):
        child = subprocess.run([sys.executable, '-B', '-c', 'raise SystemExit(2)'],
                               cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.assertEqual(child.returncode, 2)
        path = self.directory / 'raw-fixture.command.json'
        path.write_bytes(encoded({'execution_status': 'completed', 'returncode': child.returncode}))
        logical = issuance.relative(path)
        self.semantic_driver_fixture('FAIL', [issuance.ref(path)])
        outcome = 'Semantic command did not complete successfully: ' + logical
        with mock.patch.object(issuance.readiness.semantic, 'validate_stored', return_value=[]):
            for problem in ('Semantic command input binding missing or stale: ' + logical,
                            'Semantic command tool changed: ' + logical):
                with self.subTest(problem=problem), mock.patch.object(
                    issuance.readiness.semantic, 'validate_publication_execution_bindings',
                    return_value=[outcome, problem]):
                    with self.assertRaisesRegex(ValueError, 'custody'):
                        issuance.authenticate_semantic(self.inputs)
            with mock.patch.object(issuance.readiness.semantic, 'validate_publication_execution_bindings',
                                   return_value=[outcome]):
                _, report, diagnostics = issuance.authenticate_semantic(self.inputs)
                self.assertEqual(report['status'], 'FAIL')
                self.assertEqual(diagnostics, [outcome])
                path.write_bytes(encoded({'execution_status': 'incomplete', 'returncode': 2}))
                with self.assertRaisesRegex(ValueError, 'custody'):
                    issuance.authenticate_semantic(self.inputs)

    def test_ledger_ambiguity_and_missing_bound_receipt_are_rejected(self):
        ledger = self.complete_ledger()
        path = self.directory / 'commands.json'
        ledger['commands'].append(copy.deepcopy(ledger['commands'][0]))
        path.write_bytes(encoded(ledger))
        with self.assertRaisesRegex(ValueError, 'ambiguous'):
            issuance.activate()
        ledger['commands'].pop()
        path.write_bytes(encoded(ledger))
        (self.directory / 'assessment.command.json').unlink()
        with self.assertRaises(FileNotFoundError):
            issuance.activate()

    def test_symlink_and_missing_producer_artifacts_are_rejected(self):
        path = self.directory / 'authorized-request.txt'
        path.unlink()
        target = self.base / 'authorization-copy.txt'
        target.write_bytes(self.authorization)
        path.symlink_to(target)
        with self.assertRaisesRegex(ValueError, 'symlink'):
            issuance.authorities()
        path.unlink()
        path.write_bytes(self.authorization)
        (self.directory / 'test_record_commands.py').unlink()
        with self.assertRaises(FileNotFoundError):
            issuance.producer_artifacts()


if __name__ == '__main__':
    unittest.main(failfast=True)
