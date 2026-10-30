#!/usr/bin/env python3
"""Scoped, create-once readiness evidence issuance; no new validation policy.

Native commands use current_publication_readiness.REQUIRED_COMMANDS verbatim.
Two exact previously captured executions may be imported as derived views;
their original receipts, logs, recorder, outcomes and measurements are retained.
No semantic FAIL, environment qualification or future Git SHA becomes PASS.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path('/Users/alecsculley/Documents/GitHub/SSN-to-BFO')
EXPECTED_ROOT = ROOT
DIRECTORY = ROOT / 'reports/current-publication-validation/readiness-reconciliation-20261029'
EXPECTED_HEAD = 'dc314460fe3e875ba1c8ccfcb3c6840a7181e733'
EXPECTED_INPUT_COUNT = 316
AUTHORIZATION_SHA256 = '5dc173c04f729ba984889d8ad6d421758059e92e7fe31d5a1e7b0dfab1e0bda0'
OLD_SELECTOR_SHA256 = 'c530f7e93a984e850b709e977d3b59773c5d28689addc7f3e7e06fb234d6a884'
PREDECESSORS = {
    'semantic': {'path': 'reports/current-ssn-sosa-semantic-validation.json',
                 'sha256': '9a72d4a9df6d6ebccb49fb93c9c42b8b18d43405b6ec0340d49abf1f5a2fc58a'},
    'validation': {'path': 'reports/current-publication-validation/commands.json',
                   'sha256': '656557d39e0a2e73888407924ca7bec6f56d4e0640cc0c5f5be920fb41e60ff1'},
}
SOURCE_DIRECTORY = Path('/private/var/folders/js/fx38x_5s22q9_bzsy77rykfh0000gn/T/ssn-runtime-builder-audit-20261029-2ukkg8v3')
SOURCE_RECORDER_SHA256 = 'ea6daa19bb8dd5bb46dc63f3766d1a1d303b1b16f2c9fb8b7daae7e925ebf130'
IMPORTS = {
    'full_repository_gate': {
        'source_name': 'canonical_make_check',
        'receipt_sha256': 'ff78f88b270934772b43b935a8a6f5271f90e02861b4868985c30eba7733c3d6',
        'log_sha256': '7c8fc48720745586359136683406801fb336c739b7e00b234470b239edd9552b',
    },
    'static_checks': {
        'source_name': 'separate_compile',
        'receipt_sha256': '6602c2118025447eccdf9c740999f9177ceb48ef12f6d7b041b37c95e9ebc817',
        'log_sha256': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
    },
}
sys.path.insert(0, str(ROOT / 'tools'))
import current_publication_readiness as readiness

VALIDATION_ONLY = {
    'issuance_tests': [sys.executable, '-B', str(DIRECTORY / 'test_record_commands.py'), '-v'],
    'focused_evidence': [sys.executable, '-B', '-m', 'unittest', '-f', '-v',
        'tests.test_current_publication_readiness', 'tests.test_current_evidence_freshness',
        'tests.test_current_validation_selection', 'tests.test_current_semantic_validation',
        'tests.test_current_semantic_invocation', 'tests.test_current_semantic_schema',
        'tests.test_current_semantic_retry', 'tests.test_current_portable_execution_evidence',
        'tests.test_current_retained_evidence', 'tests.test_current_retained_evidence_integration',
        'tests.test_current_checkpoint_successor'],
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def stamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def local(path: Path | str) -> Path:
    path = Path(path)
    absolute = path if path.is_absolute() else ROOT / path
    try:
        relative = absolute.relative_to(ROOT)
    except ValueError as error:
        raise ValueError('Evidence path is outside repository') from error
    if '..' in relative.parts or any((ROOT / Path(*relative.parts[:i])).is_symlink()
                                      for i in range(1, len(relative.parts) + 1)):
        raise ValueError('Evidence path uses traversal or symlink')
    if not absolute.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError('Evidence path escapes repository')
    return absolute


def relative(path: Path) -> str:
    return local(path).relative_to(ROOT).as_posix()


def read(path: Path) -> dict:
    return json.loads(local(path).read_bytes())


def ref(path: Path) -> dict:
    return {'path': relative(path), 'sha256': digest(local(path).read_bytes())}


def write_new(path: Path, value: dict | bytes) -> None:
    payload = value if isinstance(value, bytes) else (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()
    target = local(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('xb') as stream:
        stream.write(payload)


def head() -> str:
    return subprocess.check_output(['git', '--no-optional-locks', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()


def inputs() -> dict:
    result = {p: digest(local(p).read_bytes()) for p in sorted(readiness.validation_inputs(ROOT))}
    if len(result) != EXPECTED_INPUT_COUNT:
        raise ValueError('Governed input membership changed; prior canonical evidence cannot be imported')
    return result


def authorities() -> dict:
    if ROOT.resolve() != EXPECTED_ROOT.resolve() or head() != EXPECTED_HEAD:
        raise ValueError('Wrong repository root or accepted predecessor HEAD')
    authorization = DIRECTORY / 'authorized-request.txt'
    if digest(local(authorization).read_bytes()) != AUTHORIZATION_SHA256:
        raise ValueError('Current reconciliation authorization differs')
    selector = ROOT / readiness.CURRENT_EVIDENCE
    if digest(local(selector).read_bytes()) != OLD_SELECTOR_SHA256:
        raise ValueError('Prior selector changed or this selection is already active')
    old = read(selector)
    if old.get('predecessors') != PREDECESSORS:
        raise ValueError('Wrong historical predecessor identities')
    for predecessor in PREDECESSORS.values():
        if ref(ROOT / predecessor['path']) != predecessor:
            raise ValueError('Historical predecessor bytes changed')
    # Existing selection authentication also verifies the selected prior records.
    readiness.selected_evidence(ROOT)
    return old


def ensure_open() -> None:
    if (DIRECTORY / 'STOP.json').exists():
        raise ValueError('Stopped at an earlier failure; no further issuance is allowed')


def producer_artifacts() -> dict:
    return {relative(p): digest(local(p).read_bytes()) for p in
            (DIRECTORY / 'record_commands.py', DIRECTORY / 'test_record_commands.py',
             DIRECTORY / 'authorized-request.txt')}


def normalize(argv: list[str]) -> list[str]:
    if not isinstance(argv, list) or not argv or any(not isinstance(v, str) or not v for v in argv):
        raise ValueError('Missing command provenance')
    return ['python' if Path(argv[0]).name.startswith('python') else Path(argv[0]).name, *argv[1:]]


def check_times(document: dict) -> None:
    try:
        start = datetime.fromisoformat(document['started_at_utc'].replace('Z', '+00:00'))
        end = datetime.fromisoformat(document['completed_at_utc'].replace('Z', '+00:00'))
        if not start.tzinfo or not end.tzinfo or end < start:
            raise ValueError('Invalid execution chronology')
    except (KeyError, TypeError, AttributeError, ValueError) as error:
        raise ValueError('Execution is incomplete or has invalid timestamps') from error


def authenticate_import(role: str, payloads: dict[str, bytes], current: dict) -> dict:
    """Authenticate original recorded facts before any native-view derivation."""
    if role not in IMPORTS or set(payloads) != {'receipt', 'log', 'recorder'}:
        raise ValueError('Unrelated or wrong execution role')
    policy = IMPORTS[role]
    expected = {'receipt': policy['receipt_sha256'], 'log': policy['log_sha256'],
                'recorder': SOURCE_RECORDER_SHA256}
    if any(digest(payloads[key]) != value for key, value in expected.items()):
        raise ValueError('Pinned source receipt/log/recorder hash differs')
    source = json.loads(payloads['receipt'])
    check_times(source)
    if source.get('name') != policy['source_name'] or source.get('cwd') != str(EXPECTED_ROOT):
        raise ValueError('Unrelated task or wrong repository root')
    if any(source.get(key) != EXPECTED_HEAD for key in ('head_before', 'head_after')):
        raise ValueError('Wrong execution predecessor HEAD')
    if any(source.get(key) != current for key in ('input_sha256_before', 'input_sha256_after')):
        raise ValueError('Stale, incomplete or drifting source inputs')
    if source.get('input_drift') != [] or source.get('integrity_errors') != []:
        raise ValueError('Source execution records input drift or integrity failure')
    if type(source.get('returncode')) is not int or source['returncode'] != 0:
        raise ValueError('Source execution did not complete successfully')
    argv = source.get('command')
    if normalize(argv) != readiness.REQUIRED_COMMANDS[role]:
        raise ValueError('Command does not implement the required logical role')
    executable = Path(argv[0])
    identity = source.get('executable', {})
    if (not executable.is_absolute() or not executable.is_file()
            or identity != {'path': str(executable.resolve()), 'sha256': digest(executable.read_bytes())}):
        raise ValueError('Missing or changed executable identity')
    source_log = SOURCE_DIRECTORY / (policy['source_name'] + '.log')
    if source.get('log') != str(source_log) or source.get('log_sha256') != policy['log_sha256']:
        raise ValueError('Source log identity differs')
    if source.get('recorder') != {'path': str(SOURCE_DIRECTORY / 'run_validation.py'),
                                  'sha256': SOURCE_RECORDER_SHA256}:
        raise ValueError('Source recorder provenance differs')
    return source


def imported_payloads(role: str, *, retained: bool) -> dict:
    if role not in IMPORTS:
        raise ValueError('No approved import for role')
    source_name = IMPORTS[role]['source_name']
    directory = DIRECTORY / 'imported' / role if retained else SOURCE_DIRECTORY
    names = {'receipt': source_name + '.command.json', 'log': source_name + '.log', 'recorder': 'run_validation.py'}
    result = {}
    for key, name in names.items():
        path = local(directory / name) if retained else directory / name
        if path.is_symlink() or not path.is_file():
            raise ValueError('Missing or symlinked source artifact')
        result[key] = path.read_bytes()
    return result


def import_view(role: str, source: dict) -> dict:
    source_name = IMPORTS[role]['source_name']
    directory = DIRECTORY / 'imported' / role
    log = directory / (source_name + '.log')
    originals = {key: ref(directory / name) for key, name in {
        'receipt': source_name + '.command.json', 'log': source_name + '.log',
        'recorder': 'run_validation.py'}.items()}
    artifacts = producer_artifacts()
    artifacts.update({item['path']: item['sha256'] for item in originals.values()})
    return {
        'name': role, 'command': source['command'], 'cwd': source['cwd'],
        'head': source['head_before'], 'expected_head': source['head_before'], 'final_head': source['head_after'],
        'expected_input_sha256': source['input_sha256_before'], 'input_sha256': source['input_sha256_before'],
        'input_sha256_after': source['input_sha256_after'], 'input_drift': source['input_drift'],
        'tool_identity': source['executable'], 'execution_status': 'completed',
        'returncode': source['returncode'], 'started_at_utc': source['started_at_utc'],
        'completed_at_utc': source['completed_at_utc'], 'elapsed_seconds': source['elapsed_seconds'],
        'log': relative(log), 'log_sha256': source['log_sha256'], 'result_artifacts': artifacts,
        'recorder': ref(DIRECTORY / 'record_commands.py'), 'issuance_mode': 'derived_external_execution',
        'source_execution': originals, 'original_execution_name': source['name'],
        'derivation': {
            'expected_bindings': 'The recorded prelaunch HEAD/input snapshot is the derived expected snapshot; no additional historical measurement is claimed.',
            'completion': 'The exact pinned recorder writes completion only after subprocess.run returns; original timestamps and returncode are preserved.',
            'tool_measurement': 'Original executable identity was measured after subprocess completion; no prelaunch executable measurement is claimed.',
            'role': 'Exact normalized argv determines the required role; the original execution label is preserved separately.',
        },
        'scope': 'Derived custody view of one original execution; no rerun, semantic PASS, environment qualification or checkpoint approval is claimed.',
    }


def import_record(role: str) -> int:
    ensure_open()
    authorities()
    current = inputs()
    destination = DIRECTORY / (role + '.command.json')
    directory = DIRECTORY / 'imported' / role
    if destination.exists() or directory.exists():
        raise ValueError('Duplicate import or ambiguous existing role; no overwrite')
    payloads = imported_payloads(role, retained=False)
    source = authenticate_import(role, payloads, current)
    source_name = IMPORTS[role]['source_name']
    for key, name in {'receipt': source_name + '.command.json', 'log': source_name + '.log',
                      'recorder': 'run_validation.py'}.items():
        write_new(directory / name, payloads[key])
    document = import_view(role, source)
    errors = readiness.command_errors(document, EXPECTED_HEAD, current, ROOT)
    if errors or inputs() != current or head() != EXPECTED_HEAD:
        raise ValueError('Imported execution authentication failed: ' + ' | '.join(errors))
    write_new(destination, document)
    return 0


def semantic_argv() -> list[str]:
    return [sys.executable, '-B', 'tools/current_semantic_validation.py', '--output',
            relative(DIRECTORY / 'semantic.json')]


def native_argv(role: str) -> list[str]:
    if role in VALIDATION_ONLY:
        return list(VALIDATION_ONLY[role])
    if role == 'semantic_execution':
        return semantic_argv()
    command = list(readiness.REQUIRED_COMMANDS[role])
    command[0] = sys.executable if command[0] == 'python' else shutil.which(command[0])
    if not command[0]:
        raise ValueError('Required executable unavailable')
    return command


def record(role: str) -> int:
    ensure_open()
    authorities()
    destination, log = DIRECTORY / (role + '.command.json'), DIRECTORY / (role + '.log')
    if destination.exists() or log.exists():
        raise ValueError('Execution paths already used; no duplicate execution')
    if role == 'semantic_execution' and any((DIRECTORY / name).exists() for name in ('semantic.json', 'semantic.md')):
        raise ValueError('Semantic successor output already exists')
    command = native_argv(role)
    before_head, before = head(), inputs()
    if before_head != EXPECTED_HEAD:
        raise ValueError('Accepted predecessor changed before command launch')
    tool = {'path': str(Path(command[0]).resolve()), 'sha256': digest(Path(command[0]).read_bytes())}
    artifacts = producer_artifacts()
    started, timer = stamp(), time.monotonic()
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', GIT_OPTIONAL_LOCKS='0')
    environment['PATH'] = str(Path(sys.executable).parent) + os.pathsep + environment.get('PATH', '')
    status = 'completed'
    with local(log).open('xb') as stream:
        try:
            process = subprocess.run(command, cwd=ROOT, env=environment, stdout=stream, stderr=subprocess.STDOUT)
            returncode = process.returncode
        except OSError as error:
            status, returncode = 'launch_failed', 127
            stream.write(('Command launch failed: ' + str(error) + '\n').encode())
    completed = stamp()
    after_head, after = head(), inputs()
    artifacts[relative(log)] = digest(log.read_bytes())
    if role == 'semantic_execution':
        for name in ('semantic.json', 'semantic.md'):
            path = DIRECTORY / name
            if path.exists():
                artifacts[relative(path)] = digest(local(path).read_bytes())
    document = {
        'name': role, 'command': command, 'cwd': str(ROOT), 'head': before_head,
        'expected_head': before_head, 'final_head': after_head,
        'expected_input_sha256': before, 'input_sha256': before, 'input_sha256_after': after,
        'input_drift': sorted(k for k in before.keys() | after.keys() if before.get(k) != after.get(k)),
        'tool_identity': tool, 'execution_status': status, 'returncode': returncode,
        'started_at_utc': started, 'completed_at_utc': completed, 'elapsed_seconds': time.monotonic() - timer,
        'log': relative(log), 'log_sha256': artifacts[relative(log)], 'result_artifacts': artifacts,
        'recorder': ref(DIRECTORY / 'record_commands.py'), 'issuance_mode': 'native_execution',
        'scope': 'Actual named execution only; independent semantic and environment qualification outcomes remain separate.',
    }
    errors = readiness.command_errors(document, after_head, after, ROOT)
    if after_head != EXPECTED_HEAD or tool['sha256'] != digest(Path(command[0]).read_bytes()):
        errors.append('Accepted predecessor or executable changed during execution')
    document['receipt_authentication_errors'] = errors
    write_new(destination, document)
    if returncode != 0 or errors:
        write_new(DIRECTORY / 'STOP.json', {'first_failure': role, 'returncode': returncode,
                                          'receipt': ref(destination), 'authentication_errors': errors})
    return returncode or int(bool(errors))


def authenticate_receipt(role: str, current: dict) -> dict:
    path = DIRECTORY / (role + '.command.json')
    document = read(path)
    if document.get('name') != role or document.get('returncode') != 0:
        raise ValueError('Missing, wrong-role or failed command receipt')
    check_times(document)
    errors = readiness.command_errors(document, EXPECTED_HEAD, current, ROOT)
    if errors:
        raise ValueError('Command receipt is not current: ' + ' | '.join(errors))
    expected_artifacts = producer_artifacts()
    if any(document['result_artifacts'].get(k) != value for k, value in expected_artifacts.items()):
        raise ValueError('Producer/test/authorization artifact binding missing or changed')
    if document.get('recorder') != ref(DIRECTORY / 'record_commands.py'):
        raise ValueError('Issuance producer identity differs')
    if document.get('issuance_mode') == 'derived_external_execution':
        payloads = imported_payloads(role, retained=True)
        source = authenticate_import(role, payloads, current)
        if document != import_view(role, source):
            raise ValueError('Derived current record differs from immutable original execution')
    elif document.get('issuance_mode') != 'native_execution' or document.get('receipt_authentication_errors') != []:
        raise ValueError('Unknown issuance mode or failed native authentication')
    return document


def finalize() -> int:
    ensure_open()
    old = authorities()
    current = inputs()
    destination = DIRECTORY / 'commands.json'
    if destination.exists():
        raise ValueError('Successor ledger already exists')
    commands = [authenticate_receipt(role, current) for role in readiness.REQUIRED_COMMANDS]
    if head() != EXPECTED_HEAD or inputs() != current:
        raise ValueError('Candidate changed during finalization')
    document = {
        'head': EXPECTED_HEAD, 'input_sha256': current, 'commands': commands,
        'predecessor': PREDECESSORS['validation'],
        'prior_selector': {'path': relative(ROOT / readiness.CURRENT_EVIDENCE), 'sha256': OLD_SELECTOR_SHA256},
        'prior_selected_records': {'semantic': old['semantic'], 'validation': old['validation']},
        'receipt_artifacts': {relative(DIRECTORY / (role + '.command.json')):
                              digest((DIRECTORY / (role + '.command.json')).read_bytes())
                              for role in readiness.REQUIRED_COMMANDS},
        'environment': {'qualification_status': 'not_performed',
                        'historical_environment_reference': {**PREDECESSORS['validation'], 'json_pointer': '/environment'}},
        'declared_environment_match': False,
        'environment_note': 'No new Java distribution/environment qualification is claimed by this reconciliation.',
        'finalized_at_utc': stamp(),
        'classification': 'CURRENT EXECUTION LEDGER; NO SEMANTIC OR ENVIRONMENT QUALIFICATION CLAIM',
        'binding_basis': 'Eight exact required argv roles, each independently authenticated against original execution facts and current inputs.',
    }
    with_changed_root = readiness.ROOT
    if with_changed_root != ROOT:
        raise ValueError('Readiness validator root differs from issuance root')
    errors = readiness.validation_errors(document)
    if errors:
        raise ValueError('Complete ledger validation failed: ' + ' | '.join(errors))
    write_new(destination, document)
    return 0


def authenticate_semantic(current: dict) -> tuple[dict, dict, list[str]]:
    """Validate diagnostic custody without changing the actual semantic outcome."""
    driver_path = DIRECTORY / 'semantic_execution.command.json'
    driver = read(driver_path)
    if (driver.get('name') != 'semantic_execution'
            or driver.get('issuance_mode') != 'native_execution'
            or driver.get('command') != semantic_argv()
            or driver.get('cwd') != str(ROOT)
            or driver.get('recorder') != ref(DIRECTORY / 'record_commands.py')
            or driver.get('receipt_authentication_errors') != []):
        raise ValueError('Semantic driver identity, provenance or authentication differs')
    check_times(driver)
    errors = readiness.command_errors(driver, EXPECTED_HEAD, current, ROOT)
    required = producer_artifacts()
    for name in ('semantic.json', 'semantic.md'):
        path = DIRECTORY / name
        required[relative(path)] = digest(local(path).read_bytes())
    if any(driver.get('result_artifacts', {}).get(k) != value for k, value in required.items()):
        errors.append('Semantic driver does not bind exact selected report and outputs')
    report = read(DIRECTORY / 'semantic.json')
    status = report.get('status')
    expected_exit = 0 if status == 'PASS' else 1 if status == 'FAIL' else None
    if type(driver.get('returncode')) is not int or driver['returncode'] != expected_exit:
        errors.append('Semantic driver returncode contradicts its recorded outcome')
    errors += readiness.semantic.validate_stored(report, ROOT)
    publication_errors = readiness.semantic.validate_publication_execution_bindings(report, ROOT)
    allowed = set()
    for artifact in report.get('evidence_files', []):
        path = artifact.get('path', '')
        if path.endswith('.command.json'):
            command = read(ROOT / path)
            if (command.get('execution_status') == 'completed'
                    and type(command.get('returncode')) is int and command['returncode'] != 0):
                allowed.add('Semantic command did not complete successfully: ' + path)
    errors += [error for error in publication_errors if error not in allowed]
    if errors:
        raise ValueError('Current semantic custody is not valid: ' + ' | '.join(errors))
    return driver, report, publication_errors


def activate() -> int:
    ensure_open()
    authorities()
    current = inputs()
    ledger_path = DIRECTORY / 'commands.json'
    ledger = read(ledger_path)
    if ledger.get('predecessor') != PREDECESSORS['validation'] or ledger.get('prior_selector', {}).get('sha256') != OLD_SELECTOR_SHA256:
        raise ValueError('Successor ledger predecessor differs')
    expected = [authenticate_receipt(role, current) for role in readiness.REQUIRED_COMMANDS]
    if ledger.get('commands') != expected or ledger.get('receipt_artifacts') != {
        relative(DIRECTORY / (role + '.command.json')): digest((DIRECTORY / (role + '.command.json')).read_bytes())
        for role in readiness.REQUIRED_COMMANDS}:
        raise ValueError('Ledger selection is incomplete, ambiguous or differs from exact receipts')
    errors = readiness.validation_errors(ledger)
    semantic_path = DIRECTORY / 'semantic.json'
    semantic_driver, semantic, publication_errors = authenticate_semantic(current)
    if errors:
        raise ValueError('Current evidence custody is not valid: ' + ' | '.join(errors))
    # A valid FAIL is eligible for honest selection, never converted to PASS.
    if semantic.get('status') not in {'PASS', 'FAIL'}:
        raise ValueError('Semantic outcome missing')
    selector = ROOT / readiness.CURRENT_EVIDENCE
    old_bytes = local(selector).read_bytes()
    if digest(old_bytes) != OLD_SELECTOR_SHA256 or head() != EXPECTED_HEAD or inputs() != current:
        raise ValueError('Selection or inputs changed before activation')
    write_new(DIRECTORY / 'prior-selector.json', old_bytes)
    write_new(DIRECTORY / 'selection-evidence.json', {
        'prior_selector': ref(DIRECTORY / 'prior-selector.json'),
        'validation': ref(ledger_path), 'semantic': ref(semantic_path),
        'semantic_driver': ref(DIRECTORY / 'semantic_execution.command.json'),
        'recorded_semantic_status': semantic['status'],
        'recorded_semantic_driver_returncode': semantic_driver['returncode'],
        'semantic_publication_diagnostics': publication_errors,
        'scope': 'Selection custody only; recorded FAIL and independent publication blockers remain visible.',
    })
    document = {'schema_version': 1, 'semantic': ref(semantic_path), 'validation': ref(ledger_path),
                'predecessors': copy.deepcopy(PREDECESSORS)}
    temporary = DIRECTORY / 'current-evidence.next.json'
    write_new(temporary, document)
    if local(selector).read_bytes() != old_bytes:
        raise ValueError('Prior selector changed during activation')
    os.replace(temporary, selector)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='action', required=True)
    commands.add_parser('import').add_argument('role', choices=tuple(IMPORTS))
    commands.add_parser('record').add_argument('role', choices=(*readiness.REQUIRED_COMMANDS, *VALIDATION_ONLY, 'semantic_execution'))
    commands.add_parser('finalize')
    commands.add_parser('activate')
    args = parser.parse_args()
    try:
        return import_record(args.role) if args.action == 'import' else record(args.role) if args.action == 'record' else finalize() if args.action == 'finalize' else activate()
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        marker = DIRECTORY / 'STOP.json'
        if DIRECTORY.is_dir() and not marker.exists():
            write_new(marker, {'first_failure': args.action, 'role': getattr(args, 'role', None),
                               'failure_kind': 'issuance_authentication_error', 'error': str(error)})
        print('Evidence issuance stopped: ' + str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
