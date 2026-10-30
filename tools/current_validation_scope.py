"""Versioned, code-owned inputs for the eight current validation roles.

These are declared dependency closures, not observations of one successful run.
Conditional local imports and maintained data families are conservative inputs;
new test discovery and compile-glob members therefore invalidate old evidence.
Execution logs and selectors are not implicitly inputs. The unit/full suites
are later consumers of the complete retained store through the existing release
guard, so those two roles deliberately bind its inventory. Other roles bind
only their authenticated authority closure.

Version 1's universal inventory and its original receipts are unchanged. This
module never converts a historical receipt, approves an outcome, or executes a
validator. Version 2 evidence must be issued with this contract at execution.
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tomllib


PROFILE = "current-validation-inputs-v2"
SCHEMA_VERSION = 2
POLICY_PATH = "tools/current_validation_scope.py"
CUSTODY_POLICY_PATH = "tools/current_custody_dependencies.py"
_LOADED_POLICY_SHA256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
REQUIRED_COMMANDS = {
    "unit_tests": ["python", "-B", "-m", "unittest", "discover", "-s", "tests"],
    "assessment": ["python", "-B", "tools/current_assessment.py"],
    "source_identity": ["python", "-B", "tools/current_source_identity.py"],
    "generation_freshness": ["python", "-B", "tools/check_coms_mapping.py", "--check-only"],
    "sosa_source_version": ["python", "-B", "tools/check_sosa_source_version.py"],
    "sosa_products": ["python", "-B", "tools/check_sosa_next_products.py"],
    "static_checks": ["make", "compile"],
    "full_repository_gate": ["make", "check"],
}
ASSESSMENT_DIRECTORY = "reports/current-assessment/v2"
ASSESSMENT_NAMES = tuple("current-ssn-sosa-" + name + extension
                         for name in ("coverage", "rationale-proposals", "human-review")
                         for extension in (".json", ".md"))
GENERATION_REPORTS = {
    "reports/coms-generation-validation.md", "reports/coms-product-dispositions.json",
    "reports/coms-source-term-coverage.md", "reports/coms-vs-pre-coms-legacy-diff.md",
}
HISTORICAL_TEST_REPORT = "reports/current-publication-validation/semantic-20261010T190914985446Z/summary.json"
HISTORICAL_TEST_SHA256 = "fef6cd505ad2e5cf29c777a33008901877735ceccc2c7faaff3384a4653f2b7f"
HISTORICAL_LEDGER = "reports/current-publication-validation/readiness-reconciliation-20261029/commands.json"
HISTORICAL_LEDGER_SHA256 = "e9acbcd2344354a777f382fb58a95f5c4d44515a216d49f76ba8272f9ddd8b7c"
MIGRATION_REPORT_CHECKPOINT = "dc314460fe3e875ba1c8ccfcb3c6840a7181e733"
REASONER_JAR = "build/lib/robot-1.9.7/robot.jar"
REASONER_JAR_SHA256 = "91890c2e83d0f092dd08731376f154b36610544cfbe8685337a1bf7244ccaa2d"
REASONING_ROLES = frozenset({"unit_tests", "generation_freshness", "sosa_products", "full_repository_gate"})
WHOLE_SUITE_ROLES = frozenset({"unit_tests", "full_repository_gate"})
# The absence of these retired artifacts is an actual regression-test input.
RETIRED_PATHS = (
    "imports/catalog-v001.xml",
    "releases/current-ssn-sosa/ssn-sosa-bfo-directmappings.ttl",
    "releases/current-ssn-sosa/ssn-sosa-cco-directmappings.ttl",
    "releases/sosa-next/sosa-bfo-directmappings.ttl",
    "releases/sosa-next/sosa-cco-directmappings.ttl",
    "src/current-ssn-sosa/catalog-v001.xml",
    "src/current-ssn-sosa/ssn-sosa-mappings-edit.ttl",
    "src/current-ssn-sosa/sparql/artifact-metadata.rq",
    "src/current-ssn-sosa/sparql/construct/README.md",
    "src/current-ssn-sosa/sparql/construct/derive-bfo-from-cco.rq",
    "src/current-ssn-sosa/sparql/report/unprojectable-cco-targets.rq",
    "src/current-ssn-sosa/build/artifacts/current-ssn-sosa-bfo-only-generated.ttl",
    "src/current-ssn-sosa/build/artifacts/current-ssn-sosa-bfo-only-skipped-cco-targets.csv",
    "src/current-ssn-sosa/build/artifacts/current-ssn-sosa-projection-catalog.xml",
)


def _role(role: str) -> None:
    if role not in REQUIRED_COMMANDS:
        raise ValueError("unknown current validation role: " + str(role))


def _path(root: Path, relative: str, *, required: bool = True) -> Path:
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise ValueError("invalid validation input path")
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != relative:
        raise ValueError("validation input must be canonical and repository-relative: " + relative)
    root = Path(root).resolve()
    actual = root / path
    if any((root / Path(*path.parts[:i])).is_symlink() for i in range(1, len(path.parts) + 1)):
        raise ValueError("validation input may not use a symlink: " + relative)
    if not actual.resolve().is_relative_to(root):
        raise ValueError("validation input escapes repository: " + relative)
    if required and not actual.is_file():
        raise ValueError("missing regular validation input: " + relative)
    return actual


def _sha(root: Path, relative: str) -> str:
    return hashlib.sha256(_path(root, relative).read_bytes()).hexdigest()


def _tree(root: Path, relative: str) -> set[str]:
    """A code-selected maintained family, including its discovered membership."""
    directory = _path(root, relative, required=False)
    if not directory.is_dir():
        raise ValueError("missing validation input directory: " + relative)
    paths = set()
    for path in directory.rglob("*"):
        logical = path.relative_to(Path(root).resolve()).as_posix()
        if any(part in {"__pycache__", "build"} for part in path.relative_to(directory).parts):
            continue
        if path.suffix in {".pyc", ".pyo"}:
            continue
        _path(root, logical, required=False)
        if path.is_file():
            paths.add(logical)
        elif not path.is_dir():
            raise ValueError("unsupported validation input entry: " + logical)
    return paths


def _python_closure(root: Path, entries: set[str]) -> set[str]:
    """All syntactic local imports, including guarded and function-local imports."""
    pending, result = list(entries), set()
    while pending:
        relative = pending.pop()
        if relative in result:
            continue
        source = _path(root, relative)
        result.add(relative)
        try:
            tree = ast.parse(source.read_text(), filename=relative)
        except (SyntaxError, UnicodeError) as exc:
            raise ValueError("cannot derive local Python dependency closure: " + relative) from exc
        modules = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules.append(node.module)
        for module in modules:
            candidates = ("tools/" + module.replace(".", "/") + ".py",
                          module.replace(".", "/") + ".py")
            for candidate in candidates:
                path = _path(root, candidate, required=False)
                if path.exists():
                    _path(root, candidate)
                    pending.append(candidate)
    return result


def compile_paths(root: Path) -> set[str]:
    """Resolve the actual py_compile operands of the maintained Makefile target."""
    lines = _path(root, "Makefile").read_text().splitlines()
    starts = [i for i, line in enumerate(lines) if line == "compile:"]
    if len(starts) != 1:
        raise ValueError("compile scope requires exactly one Makefile compile target")
    recipe = []
    for line in lines[starts[0] + 1:]:
        if line and not line.startswith("\t"):
            break
        if line:
            recipe.append(line.strip())
    tokens = shlex.split(" ".join(recipe).replace("\\", " "))
    positions = [i for i in range(len(tokens) - 1) if tokens[i:i + 2] == ["-m", "py_compile"]]
    if len(positions) != 1:
        raise ValueError("compile scope requires one explicit py_compile invocation")
    operands = tokens[positions[0] + 2:]
    if not operands or any(not p.endswith(".py") or "$" in p for p in operands):
        raise ValueError("unsupported compile operands; update the scope contract explicitly")
    result = {"Makefile"}
    root = Path(root).resolve()
    for pattern in operands:
        _path(root, pattern, required=False)
        if any(character in pattern for character in "*?["):
            matches = sorted(root.glob(pattern))
            if not matches:
                raise ValueError("compile operand matched no inputs: " + pattern)
            for path in matches:
                logical = path.relative_to(root).as_posix()
                _path(root, logical)
                result.add(logical)
        else:
            _path(root, pattern)
            result.add(pattern)
    return result


def _source_version_paths(root: Path) -> set[str]:
    config = "config/sosa-source-version.toml"
    document = tomllib.loads(_path(root, config).read_text())
    try:
        paths = {config, document["local_overlay"]["path"],
                 *(item["local_path"] for item in document["source_files"])}
    except (KeyError, TypeError) as exc:
        raise ValueError("source-version scope requires its configured source paths") from exc
    for relative in paths:
        _path(root, relative)
    return paths


def historical_test_paths(root: Path) -> set[str]:
    """The existing schema-boundary test's immutable archive, never a selector."""
    if _sha(root, HISTORICAL_TEST_REPORT) != HISTORICAL_TEST_SHA256:
        raise ValueError("historical test archive identity differs")
    report = json.loads(_path(root, HISTORICAL_TEST_REPORT).read_bytes())
    directory = Path(HISTORICAL_TEST_REPORT).parent
    paths = {HISTORICAL_TEST_REPORT}
    bindings = report.get("evidence_files")
    if not isinstance(bindings, list) or not bindings:
        raise ValueError("historical test archive has no bound evidence")
    for ref in bindings:
        relative = ref["path"]
        if not Path(relative).is_relative_to(directory) or relative in paths:
            raise ValueError("historical test artifact outside family or duplicated")
        data = _path(root, relative).read_bytes()
        if hashlib.sha256(data).hexdigest() != ref["sha256"] or len(data) != ref["bytes"]:
            raise ValueError("historical test artifact differs: " + relative)
        paths.add(relative)
    # copytree in the historical test reads every member. Unknown additions may
    # not silently extend a code-pinned fixture family.
    if _tree(root, directory.as_posix()) != paths:
        raise ValueError("historical test archive membership differs")
    return paths


def _assessment_outputs() -> set[str]:
    return {ASSESSMENT_DIRECTORY + "/" + name for name in ASSESSMENT_NAMES}


def _git_paths(root: Path, *arguments: str) -> set[str]:
    try:
        raw = subprocess.check_output(["git", "-C", str(Path(root).resolve()), *arguments], stderr=subprocess.PIPE)
        return {value.decode("utf-8") for value in raw.split(b"\0") if value}
    except (subprocess.CalledProcessError, UnicodeDecodeError) as exc:
        raise ValueError("cannot resolve governed migration file inventory") from exc


def migration_guard_paths(root: Path) -> set[str]:
    """The exact shared input family for retired-artifact reference checks.

    Report membership is frozen to accepted Git authority. Their live bytes are
    still checked. Active non-report files include both tracked and untracked
    regular files, so staging/committing an unchanged member is immaterial.
    Later receipts/selectors cannot enter through the mutable Git index.
    """
    root = Path(root).resolve()
    reports = _git_paths(root, "ls-tree", "-r", "--name-only", "-z", MIGRATION_REPORT_CHECKPOINT, "--", "reports")
    if any(not path.startswith("reports/") for path in reports):
        raise ValueError("checkpoint report inventory contains a non-report path")
    paths = set()
    for relative in reports:
        _path(root, relative)
        paths.add(relative)
    candidates = _git_paths(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z")
    for relative in candidates:
        if relative.startswith("reports/"):
            continue
        actual = _path(root, relative, required=False)
        if actual.exists():
            _path(root, relative)
            paths.add(relative)
    return paths


def historical_ledger_paths(root: Path) -> set[str]:
    """The fixed v1 compatibility regression and its exact original results.

    The old input map remains descriptive historical execution provenance; it
    is deliberately not followed to current files or relabeled as this scope.
    """
    if _sha(root, HISTORICAL_LEDGER) != HISTORICAL_LEDGER_SHA256:
        raise ValueError("historical validation fixture identity differs")
    ledger = json.loads(_path(root, HISTORICAL_LEDGER).read_bytes())
    bindings = dict(ledger.get("receipt_artifacts", {}))
    commands = ledger.get("commands")
    if not isinstance(commands, list) or not commands:
        raise ValueError("historical validation fixture has no command records")
    for command in commands:
        results = dict(command["result_artifacts"])
        if results.get(command["log"]) != command["log_sha256"]:
            raise ValueError("historical validation log binding differs")
        for relative, expected in results.items():
            if relative in bindings and bindings[relative] != expected:
                raise ValueError("historical validation artifact has conflicting identities")
            bindings[relative] = expected
    for relative, expected in bindings.items():
        if _sha(root, relative) != expected:
            raise ValueError("historical validation artifact differs: " + relative)
    return {HISTORICAL_LEDGER, *bindings}


def role_paths(root: Path, role: str) -> set[str]:
    """Derive the entire role scope; no caller may supply a path subset."""
    _role(role)
    root = Path(root).resolve()
    paths = {POLICY_PATH, CUSTODY_POLICY_PATH}
    if role == "static_checks":
        paths.update(compile_paths(root))
    elif role == "sosa_source_version":
        paths.update(_source_version_paths(root))
        paths.update(_python_closure(root, {"tools/check_sosa_source_version.py"}))
        paths.update(_tree(root, "requirements"))
    else:
        import current_custody_dependencies as custody
        if role == "assessment":
            paths.update(custody.assessment_paths(root))
            paths.update(_assessment_outputs())
            paths.update(_python_closure(root, {"tools/current_assessment.py"}))
        else:
            paths.update(custody.authority_paths(root, publication=role in WHOLE_SUITE_ROLES))
            if role in WHOLE_SUITE_ROLES:
                # These suites execute all maintained test/tool families,
                # package/catalog regressions, documentation and Git guards.
                for directory in ("tools", "tests", "config", "mappings", "imports", "rules", "queries",
                                  "releases", "src", "requirements", "legacy", "docs", ".github"):
                    paths.update(_tree(root, directory))
                paths.update({"Makefile", "README.md", ".gitignore", "SSN2BFO.ttl"})
                paths.update(GENERATION_REPORTS)
                paths.update(_assessment_outputs())
                paths.update(historical_test_paths(root))
                paths.update(historical_ledger_paths(root))
                paths.update(migration_guard_paths(root))
                # release_context._release_input_signature actually hashes
                # every retained file and compares the signature after builds.
                # Preserve that existing contract, including added membership.
                # Retain outputs before these later consumers execute; their
                # own execution receipts must remain outside the store.
                import current_retained_evidence as retained
                paths.update(retained.store_paths(root))
                for relative in RETIRED_PATHS:
                    path = _path(root, relative, required=False)
                    if path.exists():
                        _path(root, relative)
                        paths.add(relative)
            else:
                entry = REQUIRED_COMMANDS[role][2]
                paths.update(_python_closure(root, {entry}))
                # Current deterministic generation/authentication uses these
                # governed families and their conditional resolver branches.
                for directory in ("config", "mappings", "imports", "rules", "queries", "requirements"):
                    paths.update(_tree(root, directory))
                paths.update(_tree(root, "releases/current-ssn-sosa"))
                paths.add("SSN2BFO.ttl")
                if role == "generation_freshness":
                    paths.update(GENERATION_REPORTS)
                    paths.add("legacy/SSN2BFO-pre-COMS.ttl")
                    paths.update(_python_closure(root, {"tools/generate_mapping_from_coms.py"}))
                elif role == "sosa_products":
                    paths.update(_tree(root, "src/sosa-next"))
                    paths.update(_tree(root, "releases/sosa-next"))
        paths.update(_tree(root, "requirements"))
    if role in REASONING_ROLES:
        paths.update({"tools/install_validation_robot.sh", "config/validation-toolchain.env"})
    for relative in paths:
        _path(root, relative)
    return paths


def role_inputs(root: Path, role: str) -> dict[str, str]:
    return {path: _sha(root, path) for path in sorted(role_paths(root, role))}


def scope_declaration(root: Path, role: str) -> dict:
    _role(role)
    policy = _sha(root, POLICY_PATH)
    if policy != _LOADED_POLICY_SHA256:
        raise ValueError("on-disk scope policy differs from the loaded implementation")
    return {"schema_version": SCHEMA_VERSION, "profile": PROFILE, "role": role,
            "policy": {"path": POLICY_PATH, "sha256": policy},
            "custody_policy": {"path": CUSTODY_POLICY_PATH, "sha256": _sha(root, CUSTODY_POLICY_PATH)},
            "migration_report_checkpoint": MIGRATION_REPORT_CHECKPOINT if role in WHOLE_SUITE_ROLES else None,
            "absent_paths": [path for path in RETIRED_PATHS
                             if role in WHOLE_SUITE_ROLES and not _path(root, path, required=False).exists()]}


def validate_declaration(declaration: dict, root: Path, role: str) -> None:
    if (not isinstance(declaration, dict)
            or type(declaration.get("schema_version")) is not int
            or declaration != scope_declaration(root, role)):
        raise ValueError("missing, forged or incompatible validation input scope")


def ledger_inputs(root: Path) -> dict[str, str]:
    paths = set().union(*(role_paths(root, role) for role in REQUIRED_COMMANDS))
    return {path: _sha(root, path) for path in sorted(paths)}


def required_executables(role: str) -> tuple[str, ...]:
    """Actual executable families; a recorder must resolve/hash, never infer PASS."""
    _role(role)
    if role == "static_checks":
        return ("make", "python", "sh", "mktemp", "rm")
    if role == "sosa_source_version":
        return ("python",)
    if role in REASONING_ROLES:
        # The installer reuses a preexisting hash-bound JAR, so a download is
        # not an allowed hidden input to this execution contract.
        tools = ("python", "git", "java", "javac", "robot", "sh", "bash",
                 "dirname", "mkdir", "awk", "chmod", "mv", "mktemp", "rm")
        return (*tools, "make") if role in WHOLE_SUITE_ROLES else tools
    return ("python", "git")


def execution_tools(root: Path, role: str) -> dict[str, dict[str, str | int]]:
    """Read actual executable identities without running/version-probing them.

    Call in the same environment as the recorded child, before and after it.
    The native recorder must expose its Python directory on PATH for Makefile
    and installer children; disagreement fails rather than silently substituting
    a different interpreter. Executable identity is not environment qualification.
    """
    names = list(required_executables(role))
    result = {}
    if role in REASONING_ROLES:
        # An ignored runtime JAR is a tool identity, not a source file to stage
        # in a prepared Git checkpoint. Its exact bytes remain mandatory and
        # pinned before any executable discovery or validation can proceed.
        jar = _path(root, REASONER_JAR)
        data = jar.read_bytes()
        actual = hashlib.sha256(data).hexdigest()
        if actual != REASONER_JAR_SHA256:
            raise ValueError("reasoner JAR differs from the governed byte identity")
        result["robot_jar"] = {"path": jar.as_posix(), "sha256": actual, "bytes": len(data)}
        checksum = "sha256sum" if shutil.which("sha256sum") else "shasum"
        names.append(checksum)
    for name in names:
        # Make's default recipe shell is /bin/sh, independent of PATH/SHELL.
        # The governed installer/wrapper starts with the fixed /usr/bin/env
        # shebang and subsequently resolves bash and Java through PATH.
        resolved = "/bin/sh" if name == "sh" else shutil.which(name)
        if not resolved:
            raise ValueError("missing required validation executable: " + name)
        actual = Path(resolved).resolve()
        if name == "python" and actual != Path(sys.executable).resolve():
            raise ValueError("PATH Python differs from the recording interpreter")
        if not actual.is_file():
            raise ValueError("validation executable is not a regular file: " + name)
        data = actual.read_bytes()
        result[name] = {"path": actual.as_posix(), "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
    if role in REASONING_ROLES:
        env = Path("/usr/bin/env").resolve()
        if not env.is_file():
            raise ValueError("missing fixed installer shebang executable: /usr/bin/env")
        env_data = env.read_bytes()
        result["installer_env"] = {"path": env.as_posix(), "sha256": hashlib.sha256(env_data).hexdigest(), "bytes": len(env_data)}
        installed = _path(root, "build/lib/robot-1.9.7/bin/robot")
        data = installed.read_bytes()
        result["installed_robot"] = {"path": installed.as_posix(), "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
    return result


def execution_environment() -> dict[str, str | None]:
    """Settings that select subprocess tools, imports, locale and Make behavior."""
    return {name: os.environ.get(name) for name in (
        "PATH", "PYTHONPATH", "PYTHONHOME", "JAVA_HOME", "JAVA_TOOL_OPTIONS", "JDK_JAVA_OPTIONS",
        "ROBOT_JAVA_ARGS", "MAKEFLAGS", "MFLAGS", "SHELL", "LANG", "LC_ALL", "LC_CTYPE", "TZ")}
