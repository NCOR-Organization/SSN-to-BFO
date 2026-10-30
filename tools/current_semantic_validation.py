#!/usr/bin/env python3
"""Project-local exact-input HermiT checks; no semantic cleanup or network imports.

The hierarchy comparison is a PROV-style *approximate deductive difference*,
not model-theoretic conservativity. Every unknown/profile/tool result fails closed.
"""
from __future__ import annotations

import argparse
import copy
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time
import current_semantic_invocation as invocation
import current_portable_execution_evidence as portable_execution

from rdflib import BNode, Graph, OWL, RDF, URIRef
from rdflib.compare import to_isomorphic
from rdflib.exceptions import ParserError
from xml.sax import SAXParseException

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATHS = tuple(Path(p) for p in (
    "imports/sosa.ttl", "imports/sosa-sampling.ttl", "imports/ssn.ttl", "imports/ssn-systems.ttl"))
TARGET_PATHS = (Path("imports/cco.ttl"),)  # This artifact embeds the BFO dependency.
MAPPING_PATH = Path("SSN2BFO.ttl")
WORKBOOK_PATH = Path("mappings/SSN2BFO-COMS.xlsx")
IDENTITY_PATH = Path("config/current-ssn-sosa-identity.json")
MANIFEST_PATH = Path("config/current-semantic-expectations.json")
EXAMPLE_DIR = Path("src/current-ssn-sosa/examples/sosa-instance-data")
FIXTURE_PATH = Path("tests/fixtures/current-semantic/sample-relationship.ttl")
JAVA_SOURCE = Path("tools/java/CurrentSemanticReasoner.java")
ROBOT_JAR = Path("build/lib/robot-1.9.7/robot.jar")
REPORT_PATH = Path("reports/current-ssn-sosa-semantic-validation.json")
ROBOT_SHA256 = "91890c2e83d0f092dd08731376f154b36610544cfbe8685337a1bf7244ccaa2d"
INVOCATION_HELPER = Path("tools/current_semantic_invocation.py")
INVOCATION_TESTS = Path("tests/test_current_semantic_invocation.py")
CUSTODY_DEPENDENCIES = (Path("tools/current_portable_execution_evidence.py"),
                        Path("tools/current_retained_evidence.py"),
                        Path("tests/test_current_portable_execution_evidence.py"))
# This is a validator contract, never a regime selected by a report field.
CURRENT_EXECUTION_EVIDENCE_SCHEMA = 2
HISTORICAL_ARCHIVE_PATH = Path("reports/current-publication-validation/semantic-20261010T190914985446Z/summary.json")
HISTORICAL_ARCHIVE_SHA256 = "fef6cd505ad2e5cf29c777a33008901877735ceccc2c7faaff3384a4653f2b7f"


def current_schema_errors(report: dict) -> list[str]:
    if (type(report.get("execution_evidence_schema")) is not int
            or report["execution_evidence_schema"] != CURRENT_EXECUTION_EVIDENCE_SCHEMA):
        return ["Current semantic evidence requires execution_evidence_schema=2 and invocation tickets, envelopes and captures; no legacy fallback"]
    if report.get("reconciliation") is not None:
        return ["Historical reconciliation cannot satisfy a current semantic execution slot"]
    return []


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fingerprint(path: Path, root: Path = ROOT) -> dict:
    absolute = path if path.is_absolute() else root / path
    try:
        label = absolute.relative_to(root).as_posix()
    except ValueError:
        label = str(absolute)
    return {"path": label, "sha256": sha256(absolute), "bytes": absolute.stat().st_size}


def git_value(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def command_input_snapshot(root: Path = ROOT) -> list[dict]:
    paths = {*SOURCE_PATHS, *TARGET_PATHS, MAPPING_PATH, WORKBOOK_PATH, IDENTITY_PATH,
             MANIFEST_PATH, FIXTURE_PATH, JAVA_SOURCE, ROBOT_JAR,
             Path("tools/current_semantic_validation.py"), INVOCATION_HELPER, INVOCATION_TESTS,
             *CUSTODY_DEPENDENCIES,
             Path("config/validation-toolchain.env"),
             *source_examples(root)}
    manifest = json.loads((root / MANIFEST_PATH).read_text())
    paths.update(Path(p) for item in manifest["expectations"] if item.get("review_state") == "approved"
                 for p in item.get("input_files", []))
    return [fingerprint(path, root) if (root / path).is_file()
            else {"path": path.as_posix(), "sha256": None, "bytes": None}
            for path in sorted(paths)]


def command_document_snapshot(command: list[str], root: Path = ROOT) -> list[dict]:
    """Bind the actual serialized graph/query arguments as well as governed sources."""
    return [fingerprint(Path(value), root) for value in command[1:]
            if Path(value).suffix in {".rdf", ".json"}]


def source_examples(root: Path = ROOT) -> list[Path]:
    return sorted(p.relative_to(root) for p in (root / EXAMPLE_DIR).glob("*.ttl"))


def load_exact_local_graph(paths: list[Path] | tuple[Path, ...], root: Path = ROOT) -> tuple[Graph, dict]:
    """Expand explicit local inputs, audit imports, remove directives only.

    No logical axiom (including the historical simplicity blockers) is removed.
    Missing imported ontologies remain an explicit blocker, even if HermiT can
    answer a diagnostic question over the available local graph.
    """
    graph = Graph()
    identities: set[str] = set()
    imports: list[dict] = []
    inputs = []
    for path in paths:
        part = Graph().parse(root / path, format="turtle")
        inputs.append(fingerprint(path, root))
        identities.update(str(s) for s in part.subjects(RDF.type, OWL.Ontology))
        identities.update(str(o) for o in part.objects(None, OWL.versionIRI))
        imports.extend({"file": str(path), "ontology": str(s), "import": str(o)}
                       for s, o in part.subject_objects(OWL.imports))
        graph += part
    unresolved = [item for item in imports if item["import"] not in identities]
    directives = list(graph.triples((None, OWL.imports, None)))
    for triple in directives:
        graph.remove(triple)
    return graph, {
        "inputs": inputs, "import_directives": sorted(imports, key=lambda x: (x["file"], x["import"])),
        "unresolved_imports": unresolved, "removed_import_directive_count": len(directives),
        "removed_logical_axioms": 0, "triples": len(graph),
        "closure_policy": "All four current source modules for every example; CCO merged (including BFO) and integrated SSN2BFO product in aligned phase. Explicit local import expansion only; no remote resolution, no semantic cleanup.",
    }


def graph_identity(graph: Graph) -> str:
    """RDF-isomorphism identity, independent of serialized blank-node labels.

    Canonicalize each connected blank-node component with its named anchors.
    This preserves shared blank nodes without repeatedly canonicalizing the much
    larger named-only ontology. Component multiplicity is retained.
    """
    parent, anonymous, named = {}, [], []

    def representative(node):
        parent.setdefault(node, node)
        if parent[node] != node:
            parent[node] = representative(parent[node])
        return parent[node]

    for triple in graph:
        nodes = [node for node in triple if isinstance(node, BNode)]
        if not nodes:
            named.append([node.n3() for node in triple])
            continue
        for node in nodes:
            parent[representative(node)] = representative(nodes[0])
        anonymous.append(triple)
    components = {}
    for triple in anonymous:
        node = next(node for node in triple if isinstance(node, BNode))
        components.setdefault(representative(node), Graph()).add(triple)
    value = [sorted(named), sorted(str(to_isomorphic(part).graph_digest()) for part in components.values())]
    return hashlib.sha256(json.dumps(value, separators=(",", ":")).encode()).hexdigest()


def expected_execution_plan(root: Path = ROOT, only_slot: str | None = None) -> dict[str, dict]:
    """Construct required slots from governed files/configuration, never summaries."""
    manifest = json.loads((root / MANIFEST_PATH).read_text())
    approved, _ = selected_expectations(manifest)
    corpus = source_examples(root)
    plan = {}

    def add(slot, identifier, role, paths, *, side=None, phase=None, corpus_id=None, query=None, premises=None):
        if only_slot is not None and slot != only_slot:
            return
        graph, closure = load_exact_local_graph(tuple(paths), root)
        if premises:
            graph.parse(data=premises, format="turtle")
        mode = "hierarchy" if role == "hierarchy" else "consistency"
        closure_identity = hashlib.sha256(json.dumps(closure, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        identity = {
            "schema_version": 1, "id": identifier, "execution_role": role,
            "analysis_kind": "named_hierarchy" if role == "hierarchy" else "entailment" if query else "consistency",
            "comparison_side": side, "phase": phase, "corpus_id": corpus_id,
            "test_id": identifier, "query_id": query["id"] if query else None,
            "closure_identity": closure_identity, "governed_inputs": closure["inputs"],
            "graph_identity": graph_identity(graph), "queries": [query] if query else [],
            "command_identity": {"entrypoint": "CurrentSemanticReasoner", "mode": mode,
                "jvm_options": ["-Xmx4G"], "helper": fingerprint(JAVA_SOURCE, root),
                "jar": {"path": ROBOT_JAR.as_posix(), "sha256": ROBOT_SHA256}},
        }
        plan[slot] = {"identity": identity, "closure": closure, "slot": slot}

    for side, paths in (("source", SOURCE_PATHS), ("target", TARGET_PATHS),
                        ("aligned", (*SOURCE_PATHS, *TARGET_PATHS, MAPPING_PATH))):
        add("hierarchy/" + side, side + "-hierarchy", "hierarchy", paths, side=side)
    for index, path in enumerate(corpus + [FIXTURE_PATH]):
        role = "synthetic_fixture" if path == FIXTURE_PATH else "source_example"
        prefix = "fixture" if path == FIXTURE_PATH else "examples/" + path.as_posix()
        for phase in ("source", "aligned"):
            paths = (*SOURCE_PATHS, path) if phase == "source" else (*SOURCE_PATHS, *TARGET_PATHS, MAPPING_PATH, path)
            add(prefix + "/" + phase, f"example-{index:02d}-{phase}", role, paths,
                phase="source-only" if phase == "source" else "aligned", corpus_id=path.as_posix())
    for item in approved:
        query = dict(item["query"], id=item["id"], expected_entailed=item["expected_entailed"])
        add("expectations/" + item["id"], "expectation-" + item["id"], "semantic_expectation",
            (*SOURCE_PATHS, *TARGET_PATHS, MAPPING_PATH, *(Path(p) for p in item.get("input_files", []))),
            phase="aligned", corpus_id="approved-semantic-expectations", query=query, premises=item.get("premises_turtle"))
    return plan


def validate_execution_slot(raw: dict, expected: dict, report: dict, root: Path,
                            portable=None) -> None:
    """Check recorded documents/command against an independently required slot."""
    identity, closure = expected["identity"], expected["closure"]
    identifier = identity["id"]
    if raw.get("id") != identifier:
        raise ValueError("Raw execution ID differs from required slot: " + identifier)
    if raw.get("execution_identity") != identity:
        raise ValueError("Raw execution identity differs from required slot: " + identifier)
    if raw.get("closure") != closure:
        raise ValueError("Raw closure/input identity differs from required slot: " + identifier)
    document = raw.get("input_document", {})
    path = Path(document.get("path", ""))
    resolved = portable.resolve(document) if portable is not None else root / path
    if (path.name != identifier + ".rdf" or not resolved.is_file()
            or (portable is None and fingerprint(path, root) != document)):
        raise ValueError("Required execution graph document missing, changed, or belongs to another slot: " + identifier)
    if graph_identity(Graph().parse(resolved, format="xml")) != identity["graph_identity"]:
        raise ValueError("Execution graph differs from required closure/input identity: " + identifier)
    command = raw.get("attempt", {}).get("command")
    if command is None:
        if report.get("toolchain", {}).get("status") != "technical_failure":
            raise ValueError("Required execution command missing: " + identifier)
        return
    # The raw result cannot choose its build/helper directory. Current runs bind
    # it in the retained compiler command and execution freshness checks.
    build = Path(report.get("toolchain", {}).get("class_directory", ""))
    if ((portable is None and (root / path).parent != build)
            or (portable is not None and path.parent.as_posix() != portable.logical(str(build)))):
        raise ValueError("Execution graph/build directory differs from compiler provenance: " + identifier)
    expected_command = [shutil.which("java") or "java", "-Xmx4G", "-cp",
                        str(build) + ":" + str(root / ROBOT_JAR), "CurrentSemanticReasoner",
                        str(root / path), identity["command_identity"]["mode"]]
    if identity["queries"]:
        query_path = path.with_suffix(".queries.json")
        query_document = raw.get("query_document")
        resolved_query = portable.resolve(query_document) if portable is not None else root / query_path
        if ((portable is None and query_document != fingerprint(query_path, root))
                or (portable is not None and query_document.get("path") != query_path.as_posix())
                or json.loads(resolved_query.read_text()) != identity["queries"]):
            raise ValueError("Execution query/test differs from required slot: " + identifier)
        expected_command.append(str(root / query_path))
    elif raw.get("query_document") is not None:
        raise ValueError("Unexpected query document for required slot: " + identifier)
    if ((portable is None and command != expected_command)
            or (portable is not None and portable.command(command) != portable.command(expected_command))):
        raise ValueError("Execution command/tool/phase differs from required slot: " + identifier)


def record_command(command: list[str], stem: Path, timeout: int = 120) -> dict:
    stem.parent.mkdir(parents=True, exist_ok=True)
    before_head, before_inputs = git_value("rev-parse", "HEAD"), command_input_snapshot()
    before_documents = command_document_snapshot(command)
    start = time.monotonic()
    status = "completed"
    try:
        proc = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, timeout=timeout, check=False)
        code, stdout, stderr = proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as error:
        status, code = "timeout", None
        stdout = error.stdout or ""
        stderr = error.stderr or ""
        if isinstance(stdout, bytes): stdout = stdout.decode(errors="replace")
        if isinstance(stderr, bytes): stderr = stderr.decode(errors="replace")
        stderr += f"\nTimed out after {timeout} seconds."
    except OSError as error:
        status, code, stdout, stderr = "launch_failure", None, "", str(error)
    stdout_path, stderr_path = stem.with_suffix(".stdout.log"), stem.with_suffix(".stderr.log")
    stdout_path.write_text(stdout, encoding="utf-8")
    stderr_path.write_text(stderr, encoding="utf-8")
    result = {"command": command, "returncode": code, "execution_status": status,
              "elapsed_seconds": round(time.monotonic() - start, 3),
              "stdout": fingerprint(stdout_path), "stderr": fingerprint(stderr_path)}
    after_head, after_inputs = git_value("rev-parse", "HEAD"), command_input_snapshot()
    result["execution_binding"] = {
        "expected_head": before_head, "head_before": before_head, "head_after": after_head,
        "expected_inputs": before_inputs, "inputs_before": before_inputs, "inputs_after": after_inputs,
        "documents_before": before_documents, "documents_after": command_document_snapshot(command),
        "drift": before_head != after_head or before_inputs != after_inputs or before_documents != command_document_snapshot(command),
        "tool": fingerprint(Path(command[0])) if Path(command[0]).is_file() else {"path": command[0], "sha256": None},
    }
    stem.with_suffix(".command.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def record_reasoner_command(command: list[str], stem: Path, ticket_path: Path, timeout: int = 120) -> dict:
    """Run Java through the ticket-consuming helper and retain its receipt."""
    before_head, before_inputs = git_value("rev-parse", "HEAD"), command_input_snapshot()
    before_documents = command_document_snapshot(command)
    receipt = invocation.execute_ticket(ticket_path, root=ROOT, timeout=timeout)
    envelope, paths = receipt["envelope"], receipt["paths"]
    after_head, after_inputs = git_value("rev-parse", "HEAD"), command_input_snapshot()
    after_documents = command_document_snapshot(command)
    result = {"command": command, "returncode": envelope["returncode"],
              "execution_status": envelope["execution_status"],
              "elapsed_seconds": envelope["elapsed_seconds"],
              "stdout": fingerprint(paths["stdout"]), "stderr": fingerprint(paths["stderr"]),
              "selected_invocation_id": envelope["invocation_id"],
              "invocation_nonce": envelope["nonce"],
              "invocation": {kind: fingerprint(paths[kind]) for kind in ("ticket", "capture", "envelope")},
              "execution_binding": {
                  "expected_head": before_head, "head_before": before_head, "head_after": after_head,
                  "expected_inputs": before_inputs, "inputs_before": before_inputs, "inputs_after": after_inputs,
                  "documents_before": before_documents, "documents_after": after_documents,
                  "drift": before_head != after_head or before_inputs != after_inputs or before_documents != after_documents,
                  "tool": fingerprint(Path(command[0])) if Path(command[0]).is_file() else {"path": command[0], "sha256": None},
              }}
    invocation.create_once(stem.with_suffix(".command.json"), invocation.canonical_bytes(result))
    return result


def build_helper(evidence: Path, build: Path, jar: Path = ROOT / ROBOT_JAR) -> dict:
    build.mkdir(parents=True, exist_ok=True)
    if not jar.exists() or sha256(jar) != ROBOT_SHA256:
        result = {"status": "technical_failure", "error": "Pinned ROBOT 1.9.7 jar absent or SHA-256 mismatch"}
        (evidence / "toolchain-failure.json").write_text(json.dumps(result, indent=2) + "\n")
        return result
    record = record_command([shutil.which("javac") or "javac", "-cp", str(jar), "-d", str(build),
                             str(ROOT / JAVA_SOURCE)], evidence / "javac")
    return {"status": "ready" if record["returncode"] == 0 else "technical_failure", "command": record,
            "jar": fingerprint(jar), "class_directory": str(build)}


def run_graph(graph: Graph, closure: dict, name: str, evidence: Path, build: Path,
              toolchain: dict, hierarchy: bool = False, queries: list[dict] | None = None,
              timeout: int = 120, expected_execution: dict | None = None) -> dict:
    """Execute one slot once in explicitly unused build/evidence destinations.

    A retry must choose fresh destinations for this slot. Check every known
    destination before creating anything, including dangling symlinks, and
    reserve the slot before writing inputs. Exclusive writes also close races
    after the preflight; no earlier graph, query, or result can be overwritten.
    """
    input_path = build / f"{name}.rdf"
    query_path = build / f"{name}.queries.json"
    result_path = evidence / f"{name}.result.json"
    reservation_path = evidence / f"{name}.attempt.json"
    destinations = [input_path, query_path, reservation_path, result_path,
                    *(evidence / f"{name}.{suffix}" for suffix in (
                        "command.json", "stdout.log", "stderr.log", "ticket.json",
                        "capture.json", "envelope.json"))]
    occupied = [path for path in destinations if path.exists() or path.is_symlink()]
    if occupied:
        raise FileExistsError("Semantic attempt destination already exists; retry with new build/evidence "
                              "destinations: " + ", ".join(str(path) for path in occupied))
    graph_bytes = graph.serialize(format="xml", encoding="utf-8")
    query_bytes = json.dumps(queries).encode("utf-8") if queries else None
    invocation.create_once(reservation_path, invocation.canonical_bytes({
        "schema": "current-semantic-attempt-reservation-v1", "id": name,
        "slot": expected_execution.get("slot") if expected_execution else "diagnostic/" + name,
        "input_path": str(input_path.absolute()),
        "query_path": str(query_path.absolute()) if queries else None,
    }))
    invocation.create_once(input_path, graph_bytes)
    if query_bytes is not None:
        invocation.create_once(query_path, query_bytes)
    result = {"id": name, "closure": closure, "input_document": fingerprint(input_path)}
    if expected_execution is not None:
        result["execution_identity"] = copy.deepcopy(expected_execution["identity"])
        result["execution_identity_origin"] = "recorded_before_execution"
    if toolchain.get("status") != "ready":
        result.update(status="technical_failure", error="Java helper unavailable; see recorded compiler/toolchain attempt")
        invocation.create_once(result_path, invocation.canonical_bytes(result))
        return result
    command = [shutil.which("java") or "java", "-Xmx4G", "-cp",
               str(build) + ":" + str(ROOT / ROBOT_JAR), "CurrentSemanticReasoner",
               str(input_path), "hierarchy" if hierarchy else "consistency"]
    if queries:
        result["query_document"] = fingerprint(query_path)
        command.append(str(query_path))
    if expected_execution is None:
        # Unit-level reasoner diagnostics still use a ticket and wrapper, but
        # are never eligible to fill a governed publication slot.
        mode = "hierarchy" if hierarchy else "consistency"
        expected_execution = {"slot": "diagnostic/" + name, "closure": closure,
            "identity": {"id": name, "graph_identity": graph_identity(graph),
                "governed_inputs": closure.get("inputs", []),
                "command_identity": {"mode": mode}}}
    if not expected_execution.get("slot"):
        raise ValueError("Reasoner invocation requires a slot")
    ticket_path = invocation.create_ticket(root=ROOT, evidence=evidence,
        slot=expected_execution["slot"], identity=expected_execution["identity"],
        closure=expected_execution["closure"], graph_path=input_path,
        query_path=query_path if queries else None, command=command)
    attempt = record_reasoner_command(command, evidence / name, ticket_path, timeout)
    result["attempt"] = attempt
    result["selected_invocation_id"] = attempt["selected_invocation_id"]
    result["invocation_nonce"] = attempt["invocation_nonce"]
    try:
        payload = json.loads((ROOT / attempt["stdout"]["path"]).read_text())
    except (ValueError, OSError):
        payload = {"status": "technical_failure", "error": "Reasoner did not produce parseable JSON"}
    result["reasoner_result"] = payload
    if attempt["returncode"] not in (0, 2):
        result.update(status="technical_failure", error="Reasoner execution failure or timeout")
    elif closure.get("unresolved_imports"):
        result.update(status="technical_failure", error="Unresolved imported ontology; available-local-graph output is diagnostic only")
    elif payload.get("status") not in ("consistent", "inconsistent"):
        result.update(status="technical_failure", error=payload.get("error", "OWL 2 DL profile failure"))
    elif attempt["returncode"] != 0:
        result.update(status="technical_failure", error="Nonzero reasoner exit despite semantic status")
    else:
        result["status"] = payload["status"]
    invocation.create_once(result_path, invocation.canonical_bytes(result))
    return result


def relation_set(result: dict, signature: dict) -> set[tuple[str, str, str]]:
    classes, properties = set(signature["classes"]), set(signature["object_properties"])
    rows = set()
    for relation in result["reasoner_result"].get("relations", []):
        terms = classes if relation["kind"].startswith("class_") else properties
        left, right = relation["subject"], relation["object"]
        if left != right and left in terms and right in terms:
            rows.add((relation["kind"], left, right))
    return rows


def approximate_difference(baseline: dict, combined: dict) -> dict:
    if baseline.get("status") != "consistent" or combined.get("status") != "consistent":
        return {"status": "BLOCKED", "additions_count": None, "losses_count": None,
                "additions": None, "losses": None, "affected_terms": None,
                "reason": "Both complete, consistent, OWL 2 DL reasoner results are required; unavailable is not zero."}
    if "relations" not in baseline["reasoner_result"] or "relations" not in combined["reasoner_result"]:
        return {"status": "BLOCKED", "additions_count": None, "losses_count": None,
                "additions": None, "losses": None, "affected_terms": None,
                "reason": "Hierarchy materialization missing; unavailable is not an empty relation set."}
    signature = baseline["reasoner_result"]["signature"]
    before, after = relation_set(baseline, signature), relation_set(combined, signature)
    added, lost = sorted(after - before), sorted(before - after)
    def describe(rows):
        return [{"kind": k, "subject": s, "object": o,
                 "deliberate_mapping_commitment": "human_review_required",
                 "review_question": "Is this same-signature consequence intended? No automatic exception is accepted."}
                for k, s, o in rows]
    return {"status": "FAIL" if added or lost else "PASS", "signature": signature,
            "baseline_relation_count": len(before), "aligned_relation_count": len(after),
            "additions_count": len(added), "losses_count": len(lost),
            "additions": describe(added), "losses": describe(lost),
            "affected_terms": sorted({term for _, s, o in added + lost for term in (s, o)})}


def classify_example(source: dict, aligned: dict) -> str:
    if source.get("status") == "inconsistent":
        return "source-intrinsic inconsistency"
    if source.get("status") != "consistent" or aligned.get("status") not in ("consistent", "inconsistent"):
        return "technical/tool failure"
    if aligned["status"] == "inconsistent":
        return "mapping-induced inconsistency"
    return "aligned consistent"


def compact_result(result: dict) -> dict:
    compact = {key: value for key, value in result.items() if key != "reasoner_result"}
    payload = result.get("reasoner_result", {})
    compact["reasoner_result"] = {key: value for key, value in payload.items()
                                 if key not in ("relations", "profile_violations", "signature")}
    compact["reasoner_result"]["profile_violation_count"] = len(payload.get("profile_violations", []))
    compact["reasoner_result"]["profile_violation_examples"] = payload.get("profile_violations", [])[:4]
    if "signature" in payload:
        compact["reasoner_result"]["signature_counts"] = {key: len(value) for key, value in payload["signature"].items()}
    compact["reasoner_result"]["relation_count"] = len(payload["relations"]) if "relations" in payload else None
    return compact


def selected_expectations(manifest: dict) -> tuple[list[dict], list[dict]]:
    approved, proposed = [], []
    identifiers = set()
    for item in manifest["expectations"]:
        if item["id"] in identifiers: raise ValueError("Duplicate expectation ID: " + item["id"])
        identifiers.add(item["id"])
        if item.get("review_state") == "approved":
            if not item.get("approval_evidence"): raise ValueError("Approved expectation lacks human approval evidence")
            approved.append(item)
        else:
            proposed.append(item)
        if item.get("evidence_role") not in {"independent_semantic_expectation", "mapping_axiom_regression"}:
            raise ValueError("Expectation evidence role missing or invalid: " + item["id"])
        if item.get("entailment_origin") not in {"source_semantics", "mapping_induced"}:
            raise ValueError("Expectation entailment origin missing or invalid: " + item["id"])
    return approved, proposed


def expectation_counts(approved: list[dict], proposed: list[dict]) -> dict:
    counts = {"approved_count": len(approved), "proposed_count": len(proposed),
              "proposed_positive_count": sum(item["expected_entailed"] is True for item in proposed),
              "proposed_negative_count": sum(item["expected_entailed"] is False for item in proposed)}
    for label, items in (("approved", approved), ("proposed", proposed)):
        counts[label + "_independent_count"] = sum(item["evidence_role"] == "independent_semantic_expectation" for item in items)
        counts[label + "_regression_count"] = sum(item["evidence_role"] == "mapping_axiom_regression" for item in items)
    return counts


def validate_expectation_results(report: dict, manifest: dict, require_approved: bool = True) -> list[str]:
    """Require exact manifest/result membership, not just a passing summary count."""
    errors = []
    approved, proposed = selected_expectations(manifest)
    summary = report.get("expectations", {})
    expected_counts = expectation_counts(approved, proposed)
    for key, expected in expected_counts.items():
        if summary.get(key) != expected:
            errors.append("Semantic expectation count mismatch: " + key)
    if sorted(summary.get("proposed_ids", [])) != sorted(item["id"] for item in proposed):
        errors.append("Proposed semantic expectation IDs differ from manifest")
    approved_by_id = {item["id"]: item for item in approved}
    answers = []
    for run in summary.get("approved_results", []):
        run_answers = run.get("reasoner_result", {}).get("expectations", [])
        if run.get("status") != "consistent" or len(run_answers) != 1:
            errors.append("Approved semantic expectation lacks one valid complete-reasoner answer")
        for answer in run_answers:
            answers.append(answer.get("id"))
            item = approved_by_id.get(answer.get("id"))
            if item is None or answer.get("passed") is not True or answer.get("entailed") is not item["expected_entailed"]:
                errors.append("Approved semantic expectation answer failed or differs from manifest: " + str(answer.get("id")))
    if sorted(str(item) for item in answers) != sorted(approved_by_id):
        errors.append("Approved semantic expectation result IDs differ from manifest (missing, duplicate, or extra)")
    independent = [item for item in approved if item["evidence_role"] == "independent_semantic_expectation"]
    if require_approved and {item["expected_entailed"] for item in independent} != {True, False}:
        errors.append("Approved positive and negative semantic expectations are both required")
    return errors


def write_markdown(report: dict, path: Path) -> None:
    lines = ["# Current SSN/SOSA semantic validation", "", "Generated by `tools/current_semantic_validation.py`.", "",
             f"- HEAD: `{report['head']}`; branch: `{report['branch']}`.",
             f"- Executed at: `{report['executed_at_utc']}`.",
             f"- Overall semantic gate: **{report['status']}**.",
             "- All inputs, code, toolchain, commands, individual outputs and corpus hashes are bound in the adjacent JSON report.", "",
             "## Method and limitations", "",
             "A deterministic execution plan built from the governed files, sorted corpus and approved query configuration binds each required slot to its own raw result. "
             "The validator checks role, analysis, comparison side, phase, corpus/test/query, closure inputs, RDF graph identity, compiler and command arguments before deriving any classification. "
             "A summary cannot select a different raw execution. Incoming serialized graphs are checked independently of blank-node labels.", "",
             ("Fresh reasoner executions use a create-once pre-execution ticket with a random challenge. The ticket-consuming wrapper checks exact graph/query bytes and the required slot, launches Java, and creates a separate captured-output artifact and sealed result envelope. "
              "The validator checks the selected invocation ID, ticket, envelope, captured stdout/stderr and derived result. `javac` and `java -version` are toolchain setup checks governed by their existing command/input/output records; they are not semantic reasoner slots. "
              "This local custody prevents post-hoc output rebinding while tickets, envelopes and the selected-invocations record remain intact. It is not cryptographic nonrepudiation against an actor who can rewrite every local file; that stronger threat requires external or write-once custody.") if report.get("execution_evidence_schema") == 2 else
             "This retained historical execution predates invocation tickets and is ineligible for successful current publication evidence.", "",
             "PROV-style approximate deductive difference: HermiT materializes all non-reflexive named class/object-property subsumptions and equivalences, "
             "then compares baseline with aligned entailments separately inside each original logical signature. Built-in top/bottom entities are excluded; "
             "foreign names referenced in the baseline remain in its logical signature. Equivalence contributes both subclass/subproperty directions plus "
             "one canonical equivalence pair. This is not full model-theoretic conservativity. No claim of methodological novelty or equivalence to a 312-instance corpus is made.", "",
             "Every example uses all four current source modules; aligned runs add CCO merged (which embeds BFO) and `SSN2BFO.ttl`. "
             "Only import directives are removed from temporary, explicitly expanded graphs. All logical triples, including functionality and inverse functionality, "
             "are retained. Missing imports, OWL 2 DL violations, reasoner errors, timeouts and absent materializations fail closed. "
             "Consistency results on an incomplete or out-of-profile local graph are diagnostic only.", "",
             "## Approximate deductive difference", "", "| Signature | Status | Additions | Losses |", "|---|---|---:|---:|"]
    for side, result in report["conservativity"].items():
        lines.append(f"| {side} | {result['status']} | {result['additions_count'] if result['additions_count'] is not None else 'unavailable'} | {result['losses_count'] if result['losses_count'] is not None else 'unavailable'} |")
        if result.get("additions") or result.get("losses"):
            lines.extend([f"- {side}: `{row['subject']}` {row['kind']} `{row['object']}`; human review required."
                          for row in result["additions"] + result["losses"]])
    lines += ["", "No unavailable comparison is recorded as zero changes. Any addition or loss fails this gate and requires human review; no automatic waivers exist.",
              "", "## Source examples", "", f"Corpus: **{len(report['examples'])} source-example files**; **1 separate synthetic fixture**.", "",
              "| Example | Source-only | Aligned | Classification |", "|---|---|---|---|"]
    for example in report["examples"] + [report["synthetic_fixture"]]:
        lines.append(f"| `{example['file']['path']}` | {example['source']['status']} | {example['aligned']['status']} | {example['classification']} |")
    lines += ["", "Source-intrinsic inconsistency requires a valid inconsistent source result; mapping-induced inconsistency requires a valid consistent source result and inconsistent aligned result. Tool/profile failures are not semantic inconsistencies.", "",
              "## Selected expectations", "",
              f"Approved: {report['expectations']['approved_count']}; proposed, unapproved: {report['expectations']['proposed_count']}. "
              f"Proposed independent expectations: {report['expectations']['proposed_independent_count']}; "
              f"proposed mapping-axiom regressions/restatements: {report['expectations']['proposed_regression_count']}. "
              "Proposed cases are specified in `config/current-semantic-expectations.json`, are not executed as accepted commitments, and do not count as publication evidence. "
              "Negative expectations mean not entailed under open-world semantics, not an asserted negation. Selected tests do not prove global interpretability.", "",
              "## Blockers", ""]
    lines += ["- " + item for item in report["blockers"]]
    lines += ["", "## Evidence", "", f"Raw command records and complete stdout/stderr: `{report['evidence_directory']}`.", "",
              "The historical `tools/test_full_sosa_closure_hermit.py` cleanup run is not a substitute for these exact-input attempts. "
              "The source/target, corpus and product bytes are unchanged by this evaluator.", ""]
    if report.get("reconciliation"):
        lines += ["The summaries and expectation classifications were reconciled against retained raw evidence at "
                  f"`{report['reconciliation']['checked_at_utc']}`. Original execution time and bindings are preserved. "
                  "Execution identities labeled `reconstructed_from_retained_artifacts` describe current verification of retained closure, graph and command artifacts; "
                  "they are not backfilled original execution metadata. Raw artifacts remain unchanged. "
                  "This is a historical blocked execution, ineligible as successful current publication evidence; no reasoner rerun is claimed.", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def execution_status(attempt: dict, payload: dict, closure: dict) -> str:
    """Derive a usable semantic status from execution facts, never a summary."""
    if (attempt.get("execution_status") != "completed" or attempt.get("returncode") != 0
            or closure.get("unresolved_imports")
            or payload.get("owl2_dl_profile") is not True
            or payload.get("profile_violations") != []):
        return "technical_failure"
    status = payload.get("status")
    if status not in {"consistent", "inconsistent"} or payload.get("consistent") is not (status == "consistent"):
        return "technical_failure"
    return status


def verify_invocation_chain(command: dict, raw: dict, expected: dict, report: dict,
                            directory: Path, evidence: dict, root: Path, portable=None) -> None:
    """Authenticate one selected execution against its ticket and wrapper capture."""
    slot = expected["slot"]
    selected = report.get("selected_invocations", {}).get(slot)
    if not isinstance(selected, str) or not selected:
        raise ValueError("Selected invocation missing for required execution slot: " + slot)
    if command.get("selected_invocation_id") != selected or raw.get("selected_invocation_id") != selected:
        raise ValueError("Selected invocation differs from command/raw required execution slot: " + slot)
    ticket_path = directory / "invocations" / (selected + ".ticket.json")
    refs = command.get("invocation", {})
    for kind, path in invocation.invocation_paths(root / ticket_path).items():
        label = path.relative_to(root).as_posix()
        binding = fingerprint(path, root)
        if label not in evidence or evidence[label] != binding:
            raise ValueError("Invocation artifact missing or changed: " + label)
        if kind in ("ticket", "capture", "envelope") and refs.get(kind) != binding:
            raise ValueError("Command invocation artifact differs from wrapper evidence: " + label)
    if portable is None:
        receipt = invocation.verify_result(root / ticket_path, root=root, expected_slot=slot,
                                           expected_invocation_id=selected)
    else:
        portable.verify_tool(command)
        receipt = portable.verify_result(root / ticket_path, expected=expected)
        if receipt["ticket"]["invocation_id"] != selected:
            raise ValueError("Portable invocation differs from selected identity")
    envelope = receipt["envelope"]
    if command.get("invocation_nonce") != envelope["nonce"] or raw.get("invocation_nonce") != envelope["nonce"]:
        raise ValueError("Mutable invocation nonce differs from ticket and helper envelope: " + slot)
    if (command.get("returncode") != envelope["returncode"] or
            command.get("execution_status") != envelope["execution_status"] or
            command.get("command") != envelope["command"]):
        raise ValueError("Command execution state differs from helper result envelope: " + slot)
    for channel in ("stdout", "stderr"):
        if command.get(channel) != fingerprint(receipt["paths"][channel], root):
            raise ValueError("Command output differs from captured invocation: " + slot + "/" + channel)


def verify_selection_record(report: dict, directory: Path, evidence: dict, root: Path,
                            plan: dict[str, dict]) -> list[str]:
    """A create-once selection prevents a mutable report changing same-slot runs."""
    errors = []
    selection_path = directory / "selected-invocations.json"
    try:
        label = selection_path.as_posix()
        binding = fingerprint(selection_path, root)
        if report.get("selection_record") != binding or evidence.get(label) != binding:
            raise ValueError("Selected invocation record missing or changed")
        record = json.loads((root / selection_path).read_bytes())
        invocation.verify_seal(record, "selection_sha256")
        if record.get("schema") != invocation.SCHEMA or record.get("selected_invocations") != report.get("selected_invocations"):
            raise ValueError("Selected invocation record differs from report")
        if set(record["selected_invocations"]) - set(plan):
            raise ValueError("Selected invocation record contains an unknown execution slot")
        identities = list(record["selected_invocations"].values())
        if len(identities) != len(set(identities)):
            raise ValueError("An invocation ID was selected for two distinct slots")
        seen_ids, seen_nonces = set(), set()
        for path in (root / directory / "invocations").glob("*.ticket.json"):
            ticket = invocation.read_ticket(path)
            identifier, nonce = ticket["invocation_id"], ticket["nonce"]
            if path.name != identifier + ".ticket.json" or identifier in seen_ids or nonce in seen_nonces:
                raise ValueError("Invocation ID or nonce reused across distinct executions")
            seen_ids.add(identifier)
            seen_nonces.add(nonce)
            if fingerprint(path, root) != evidence.get(path.relative_to(root).as_posix()):
                raise ValueError("Invocation ticket missing from retained evidence: " + identifier)
        if any(identifier not in seen_ids for identifier in identities):
            raise ValueError("Selected invocation ticket missing")
    except (OSError, ValueError, KeyError, TypeError, SyntaxError) as error:
        errors.append("Invalid selected invocation record: " + str(error))
    return errors


def reconcile_raw_evidence(report: dict, root: Path = ROOT) -> tuple[dict, list[str]]:
    """Read retained result/command/stdout artifacts and derive every summary.

    This entry point is current-only. The validator contract requires tickets;
    a report's schema declaration is checked, never used to choose a legacy
    path. Wrapper custody establishes exit state and bytes before classification.
    """
    derived, errors = copy.deepcopy(report), current_schema_errors(report)
    if errors:
        derived["status"] = "FAIL"
        return derived, errors
    evidence = {item.get("path"): item for item in report.get("evidence_files", [])}
    directory = Path(report.get("evidence_directory", "."))
    try:
        portable = portable_execution.context(report, root)
        plan = expected_execution_plan(root)
    except (OSError, ValueError, KeyError, TypeError, SyntaxError, ParserError, SAXParseException) as error:
        return derived, ["Cannot construct required semantic execution plan: " + str(error)]
    errors.extend(verify_selection_record(report, directory, evidence, root, plan))

    def read_json(path: Path) -> dict:
        label = path.as_posix()
        if label not in evidence:
            raise ValueError("Required raw artifact lacks evidence binding: " + label)
        if not (root / path).is_file() or sha256(root / path) != evidence[label].get("sha256"):
            raise ValueError("Raw artifact hash differs or is missing: " + label)
        value = json.loads((root / path).read_text())
        if not isinstance(value, dict):
            raise ValueError("Raw artifact is not a JSON object: " + label)
        return value

    toolchain = report.get("toolchain", {})
    if toolchain.get("status") == "ready":
        try:
            compiler = read_json(directory / "javac.command.json")
            expected_command = [shutil.which("javac") or "javac", "-cp", str(root / ROBOT_JAR),
                                "-d", toolchain["class_directory"], str(root / JAVA_SOURCE)]
            if (compiler != toolchain.get("command")
                    or (portable is None and compiler.get("command") != expected_command)
                    or (portable is not None and portable.command(compiler.get("command")) != portable.command(expected_command))):
                errors.append("Compiler command/tool identity differs from required execution plan")
            if portable is not None:
                portable.verify_tool(compiler)
            if compiler.get("execution_status") != "completed" or compiler.get("returncode") != 0:
                errors.append("Ready toolchain lacks a successful retained compiler execution")
        except (OSError, ValueError, KeyError, TypeError) as error:
            errors.append("Cannot verify retained compiler execution: " + str(error))

    def derive_run(summary: dict, slot: str) -> dict:
        expected = plan[slot]
        identifier = expected["identity"]["id"]
        if summary.get("id") != identifier:
            errors.append("Stored semantic reference differs from required execution slot " + slot + ": " + str(summary.get("id")))
        try:
            # Critically, the summary never selects the raw artifact to read.
            raw = read_json(directory / (identifier + ".result.json"))
            validate_execution_slot(raw, expected, report, root, portable=portable)
            attempt = raw.get("attempt")
            if attempt is None:
                # An honest compiler/launch precondition failure has no reasoner command.
                if report.get("toolchain", {}).get("status") != "technical_failure":
                    raise ValueError("Raw reasoner command missing: " + identifier)
                payload = {}
            else:
                command = read_json(directory / (identifier + ".command.json"))
                if attempt != command:
                    errors.append("Raw result disagrees with retained command: " + identifier)
                attempt = command
                verify_invocation_chain(command, raw, expected, report, directory, evidence, root, portable=portable)
                for channel in ("stdout", "stderr"):
                    binding = command.get(channel, {})
                    label = binding.get("path")
                    selected = report.get("selected_invocations", {}).get(slot)
                    expected_label = (directory / "invocations" / (str(selected) + "." + channel + ".log")).as_posix()
                    if label != expected_label:
                        raise ValueError("Raw command output differs from required execution slot: " + identifier + "/" + channel)
                    if label not in evidence or binding != evidence[label]:
                        raise ValueError("Raw command output binding differs: " + str(label))
                    if not (root / label).is_file() or sha256(root / label) != binding.get("sha256"):
                        raise ValueError("Raw command output missing or changed: " + str(label))
                try:
                    payload = json.loads((root / command["stdout"]["path"]).read_text())
                    if not isinstance(payload, dict):
                        raise ValueError("Reasoner output is not an object")
                except ValueError:
                    payload = {"status": "technical_failure", "error": "Reasoner did not produce parseable JSON"}
                if raw.get("reasoner_result") != payload:
                    errors.append("Raw result disagrees with retained reasoner stdout: " + identifier)
            status = execution_status(attempt or {}, payload, raw.get("closure", {}))
            if raw.get("status") != status:
                errors.append("Raw result status contradicts execution evidence: " + identifier)
            result = dict(raw, status=status)
            if raw.get("execution_identity_origin") != "recorded_before_execution":
                errors.append("Raw execution identity origin invalid: " + identifier)
            if attempt is not None:
                result["attempt"] = attempt
                result["reasoner_result"] = payload
            compact = compact_result(result)
            if summary != compact:
                errors.append("Stored semantic execution summary contradicts raw evidence: " + identifier)
            return result
        except (OSError, ValueError, KeyError, TypeError, SyntaxError, ParserError, SAXParseException) as error:
            errors.append("Cannot reconcile semantic execution " + identifier + ": " + str(error))
            return {"id": identifier, "status": "technical_failure"}

    if set(report.get("hierarchy_runs", {})) != {"source", "target", "aligned"}:
        errors.append("Required hierarchy slot membership differs")
    full = {name: derive_run(report.get("hierarchy_runs", {}).get(name, {}), "hierarchy/" + name)
            for name in ("source", "target", "aligned")}
    derived["hierarchy_runs"] = {name: compact_result(run) for name, run in full.items()}
    comparisons = {}
    for side in ("source", "target"):
        try:
            comparisons[side] = approximate_difference(full.get(side, {}), full.get("aligned", {}))
        except (KeyError, TypeError, ValueError) as error:
            errors.append("Malformed raw hierarchy materialization: " + str(error))
            comparisons[side] = approximate_difference({}, {})
    derived["conservativity"] = comparisons
    if report.get("conservativity") != comparisons:
        errors.append("Stored conservativity summary contradicts raw evidence; unavailable differences are not zero")
    rows = derived.get("examples", [])
    corpus = source_examples(root)
    if [row.get("file", {}).get("path") for row in rows] != [path.as_posix() for path in corpus]:
        errors.append("Required example slot membership differs")
    for index, path in enumerate(corpus + [FIXTURE_PATH]):
        fixture = path == FIXTURE_PATH
        row = derived.get("synthetic_fixture", {}) if fixture else (rows[index] if index < len(rows) else {})
        if row.get("file") != fingerprint(path, root):
            errors.append("Example corpus/input reference differs from required slot: " + path.as_posix())
        prefix = "fixture" if fixture else "examples/" + path.as_posix()
        source = derive_run(row.get("source", {}), prefix + "/source")
        aligned = derive_run(row.get("aligned", {}), prefix + "/aligned")
        classification = classify_example(source, aligned)
        if row.get("classification") != classification:
            errors.append("Stored example classification contradicts raw evidence: " + path.as_posix())
        row.update(source=compact_result(source), aligned=compact_result(aligned), classification=classification)
    derived["example_counts"] = dict(Counter(row["classification"] for row in derived.get("examples", [])))
    if report.get("example_counts") != derived["example_counts"]:
        errors.append("Stored example counts contradict raw evidence")
    expectations = derived.setdefault("expectations", {})
    expectation_slots = [slot for slot in plan if slot.startswith("expectations/")]
    expected_results = expectations.get("approved_results", [])
    if len(expected_results) != len(expectation_slots):
        errors.append("Required expectation execution slot membership differs")
    expectations["approved_results"] = [compact_result(derive_run(
        expected_results[index] if index < len(expected_results) else {}, slot))
        for index, slot in enumerate(expectation_slots)]
    valid = (set(full) == {"source", "target", "aligned"}
             and all(run.get("status") == "consistent" for run in full.values())
             and all(item["status"] == "PASS" for item in comparisons.values())
             and bool(derived.get("examples"))
             and all(row.get("classification") == "aligned consistent"
                     for row in derived.get("examples", []) + [derived.get("synthetic_fixture", {})]))
    try:
        manifest = json.loads((root / MANIFEST_PATH).read_text())
        valid = valid and not validate_expectation_results(derived, manifest)
    except (OSError, ValueError, KeyError):
        valid = False
    derived["status"] = "PASS" if valid and not errors else "FAIL"
    if report.get("status") != derived["status"]:
        errors.append("Stored semantic gate contradicts raw execution evidence or required expectations")
    return derived, errors


def read_historical_archive(root: Path = ROOT) -> dict:
    """Read one fixed legacy archive for historical inspection, never slot evidence.

    The path and original-summary digest are pinned in validator code. The
    summary pins the retained raw artifacts. Neither a supplied report, a schema
    field, nor an eligibility assertion can select or extend this archive family.
    Current validators never call this reader or accept its result as evidence.
    """
    path = root / HISTORICAL_ARCHIVE_PATH
    if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()) or sha256(path) != HISTORICAL_ARCHIVE_SHA256:
        raise ValueError("Unrecognized or changed historical archive summary")
    original = json.loads(path.read_text())
    if (original.get("schema_version") != 1 or "execution_evidence_schema" in original
            or original.get("status") != "FAIL"
            or original.get("evidence_directory") != HISTORICAL_ARCHIVE_PATH.parent.as_posix()):
        raise ValueError("Historical archive schema/family differs from pinned legacy record")
    artifacts = original.get("evidence_files", [])
    seen = set()
    for binding in artifacts:
        relative = Path(binding["path"])
        artifact = root / relative
        if (relative.is_absolute() or not relative.is_relative_to(HISTORICAL_ARCHIVE_PATH.parent)
                or not artifact.resolve().is_relative_to((root / HISTORICAL_ARCHIVE_PATH.parent).resolve())
                or artifact.is_symlink() or relative in seen
                or fingerprint(artifact, root) != binding):
            raise ValueError("Historical archive artifact missing, changed or outside pinned family: " + str(relative))
        seen.add(relative)
    if not artifacts:
        raise ValueError("Historical archive has no retained evidence")
    return {"kind": "historical_legacy_archive", "status": "HISTORICAL_ONLY",
            "archive": fingerprint(path, root),
            "publication_evidence_eligible": False, "current_review_evidence_eligible": False,
            "original_execution_summary": original,
            "policy": "Pinned historical bytes only; no current required execution slot or semantic conclusion is validated."}


def validate_publication_execution_bindings(report: dict, root: Path = ROOT) -> list[str]:
    """Stricter freshness gate for accepting successful publication evidence."""
    # Always enforce the current contract, including when called on its own.
    errors = reconcile_raw_evidence(report, root)[1]
    try:
        portable = portable_execution.context(report, root)
        expected_head, expected_inputs = git_value("rev-parse", "HEAD"), command_input_snapshot(root)
        if any(item["sha256"] is None for item in expected_inputs):
            errors.append("Required semantic command input is missing; no successful publication evidence is possible")
        commands = [item for item in report.get("evidence_files", []) if item.get("path", "").endswith(".command.json")]
        if not commands:
            errors.append("No bound semantic command records")
        for item in commands:
            path = root / item["path"]
            if not path.is_file() or sha256(path) != item.get("sha256"):
                errors.append("Semantic command artifact missing or changed: " + item["path"])
                continue
            command = json.loads(path.read_text())
            binding = command.get("execution_binding", {})
            if any(binding.get(key) != expected_head for key in ("expected_head", "head_before", "head_after")):
                errors.append("Semantic command HEAD binding missing or stale: " + item["path"])
            if any(binding.get(key) != expected_inputs for key in ("expected_inputs", "inputs_before", "inputs_after")):
                errors.append("Semantic command input binding missing or stale: " + item["path"])
            if binding.get("drift") is not False:
                errors.append("Semantic command records missing/nonzero drift: " + item["path"])
            if command.get("execution_status") != "completed" or command.get("returncode") != 0:
                errors.append("Semantic command did not complete successfully: " + item["path"])
            tool = binding.get("tool", {})
            identity = command.get("command", [])
            documents = (portable.command_documents(identity) if portable is not None
                         else command_document_snapshot(identity, root))
            if (binding.get("documents_before") != documents or binding.get("documents_after") != documents
                    or ("CurrentSemanticReasoner" in identity and not documents)):
                errors.append("Semantic command graph/query binding missing or stale: " + item["path"])
            if not identity or tool.get("path") != identity[0] or not tool.get("sha256"):
                errors.append("Semantic command tool identity missing: " + item["path"])
            elif portable is not None:
                try:
                    portable.verify_tool(command)
                except (ValueError, OSError) as error:
                    errors.append("Semantic portable command tool identity differs: " + str(error))
            elif not (root / tool["path"]).is_file() or sha256(root / tool["path"]) != tool["sha256"]:
                errors.append("Semantic command tool changed: " + item["path"])
            evidence = {entry["path"]: entry for entry in report.get("evidence_files", [])}
            for channel in ("stdout", "stderr"):
                artifact = command.get(channel, {})
                label = artifact.get("path")
                if label not in evidence or artifact != evidence[label] or not (root / label).is_file() or sha256(root / label) != artifact.get("sha256"):
                    errors.append("Semantic command result artifact missing or changed: " + str(label))
    except (OSError, ValueError, KeyError, TypeError, SyntaxError, ParserError, SAXParseException) as error:
        errors.append("Cannot validate semantic command provenance: " + str(error))
    return errors


def validate_stored(report: dict, root: Path = ROOT) -> list[str]:
    """Validate current required execution evidence; historical inspection is separate."""
    errors = current_schema_errors(report)
    if report.get("head") != git_value("rev-parse", "HEAD"):
        errors.append("Stored semantic evidence HEAD differs from current HEAD")
    required_paths = {*SOURCE_PATHS, *TARGET_PATHS, MAPPING_PATH, WORKBOOK_PATH,
                      MANIFEST_PATH, FIXTURE_PATH, IDENTITY_PATH, JAVA_SOURCE,
                      Path("tools/current_semantic_validation.py"),
                      Path("tests/test_current_semantic_validation.py"),
                      Path("config/validation-toolchain.env"), *source_examples(root),
                      *CUSTODY_DEPENDENCIES,
                      INVOCATION_HELPER, INVOCATION_TESTS}
    try:
        manifest = json.loads((root / MANIFEST_PATH).read_text())
        approved, _ = selected_expectations(manifest)
        required_paths.update(Path(p) for item in approved for p in item.get("input_files", []))
        errors.extend(validate_expectation_results(report, manifest, require_approved=False))
    except (OSError, ValueError, KeyError) as error:
        errors.append("Cannot validate semantic expectation manifest: " + str(error))
    bound_paths = [item["path"] for item in report.get("bound_files", [])]
    if len(bound_paths) != len(set(bound_paths)):
        errors.append("Duplicate bound semantic input paths")
    for path in sorted(required_paths - {Path(p) for p in bound_paths}):
        errors.append("Required semantic evidence binding missing: " + str(path))
    for item in report.get("bound_files", []):
        path = root / item["path"]
        if not path.exists() or sha256(path) != item["sha256"]:
            errors.append("Stored semantic evidence hash differs: " + item["path"])
    expected_corpus = [item["file"]["path"] for item in report.get("examples", [])]
    if expected_corpus != [str(p) for p in source_examples(root)]:
        errors.append("Source example corpus membership changed")
    toolchain = report.get("toolchain", {})
    jar = root / ROBOT_JAR
    if toolchain.get("jar", {}).get("path") != str(ROBOT_JAR) or toolchain.get("jar", {}).get("sha256") != ROBOT_SHA256:
        errors.append("Pinned reasoner toolchain binding missing or incorrect")
    if not jar.exists() or sha256(jar) != ROBOT_SHA256:
        errors.append("Pinned reasoner jar missing or changed")
    if not report.get("evidence_files"):
        errors.append("Raw semantic evidence manifest missing or empty")
    evidence_paths = {item["path"] for item in report.get("evidence_files", [])}
    runs = list(report.get("hierarchy_runs", {}).values())
    for example in report.get("examples", []) + [report.get("synthetic_fixture", {})]:
        runs.extend(example.get(phase, {}) for phase in ("source", "aligned"))
    runs.extend(report.get("expectations", {}).get("approved_results", []))
    if set(report.get("hierarchy_runs", {})) != {"source", "target", "aligned"}:
        errors.append("Required hierarchy attempts missing")
    if report.get("synthetic_fixture", {}).get("file", {}).get("path") != str(FIXTURE_PATH):
        errors.append("Separate synthetic fixture attempt missing")
    for run in runs:
        if not run.get("id"):
            errors.append("Required semantic execution attempt missing")
        for channel in (() if not run.get("attempt") and toolchain.get("status") == "technical_failure" else ("stdout", "stderr")):
            path = run.get("attempt", {}).get(channel, {}).get("path")
            if path not in evidence_paths:
                errors.append("Execution output lacks retained evidence binding: " + str(path))
    for item in report.get("evidence_files", []):
        path = root / item["path"]
        if not path.exists() or sha256(path) != item["sha256"]:
            errors.append("Stored raw evidence hash differs: " + item["path"])
    _, reconciliation_errors = reconcile_raw_evidence(report, root)
    errors.extend(reconciliation_errors)
    return errors


def reconcile_stored_report(report: dict, root: Path = ROOT) -> dict:
    """Reject the retired route that refreshed historical metadata into current evidence."""
    raise ValueError("Historical reconciliation cannot supply current evidence; use read_historical_archive for archival inspection")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check stored evidence binding and require semantic gate PASS")
    parser.add_argument("--reconcile", action="store_true", help="Retired: historical reconciliation cannot produce current evidence")
    parser.add_argument("--read-historical", action="store_true", help="Read and verify the fixed legacy archive for ineligible historical inspection only")
    parser.add_argument("--output", type=Path, default=REPORT_PATH)
    parser.add_argument("--timeout", type=int, default=120, help="Timeout per complete-reasoner attempt")
    args = parser.parse_args(argv)
    output = ROOT / args.output
    if args.reconcile:
        parser.error("--reconcile is retired; use --read-historical for ineligible archive inspection")
    if args.read_historical:
        if args.check or args.output != REPORT_PATH:
            parser.error("--read-historical cannot select a current output or validation mode")
        try:
            archive = read_historical_archive()
        except (OSError, ValueError, KeyError, TypeError) as error:
            print("FAIL: " + str(error))
            return 1
        print(json.dumps({key: value for key, value in archive.items() if key != "original_execution_summary"}, indent=2))
        return 0
    if args.check:
        if not output.exists():
            print("FAIL: semantic report missing")
            return 1
        report = json.loads(output.read_text())
        errors = validate_stored(report)
        errors.extend(validate_publication_execution_bindings(report))
        try:
            errors.extend(validate_expectation_results(report, json.loads((ROOT / MANIFEST_PATH).read_text())))
        except (OSError, ValueError, KeyError) as error:
            errors.append("Semantic expectation validation failed: " + str(error))
        comparisons = report.get("conservativity", {})
        if set(comparisons) != {"source", "target"} or any(
                item.get("status") != "PASS" or item.get("additions_count") != 0 or item.get("losses_count") != 0
                for item in comparisons.values()):
            errors.append("Both source and target deductive-difference results must pass")
        examples = report.get("examples", []) + [report.get("synthetic_fixture", {})]
        if any(item.get("classification") != "aligned consistent" or
               any(item.get(phase, {}).get("status") != "consistent" for phase in ("source", "aligned"))
               for item in examples):
            errors.append("Every source example and the separate fixture need consistent exact-closure results")
        if report.get("status") != "PASS": errors.append("Current semantic evidence gate is " + str(report.get("status")))
        print("\n".join(errors) if errors else "PASS: current semantic evidence and hashes")
        return int(bool(errors))
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    evidence = ROOT / "reports/current-publication-validation" / ("semantic-" + stamp)
    evidence.mkdir(parents=True)
    build = ROOT / "build/current-semantic-validation" / stamp
    toolchain = build_helper(evidence, build)
    java_version = record_command([shutil.which("java") or "java", "-version"], evidence / "java-version")
    paths = (*SOURCE_PATHS, *TARGET_PATHS, MAPPING_PATH, WORKBOOK_PATH, MANIFEST_PATH,
             FIXTURE_PATH, Path(__file__).relative_to(ROOT), INVOCATION_HELPER, INVOCATION_TESTS, JAVA_SOURCE,
             *CUSTODY_DEPENDENCIES,
             Path("tests/test_current_semantic_validation.py"), Path("config/validation-toolchain.env"))
    if (ROOT / IDENTITY_PATH).exists(): paths += (IDENTITY_PATH,)
    corpus = source_examples()
    source_graph, source_closure = load_exact_local_graph(SOURCE_PATHS)
    target_graph, target_closure = load_exact_local_graph(TARGET_PATHS)
    aligned_graph, aligned_closure = load_exact_local_graph((*SOURCE_PATHS, *TARGET_PATHS, MAPPING_PATH))
    plan = expected_execution_plan()
    source = run_graph(source_graph, source_closure, "source-hierarchy", evidence, build, toolchain, True, timeout=args.timeout, expected_execution=plan["hierarchy/source"])
    target = run_graph(target_graph, target_closure, "target-hierarchy", evidence, build, toolchain, True, timeout=args.timeout, expected_execution=plan["hierarchy/target"])
    aligned = run_graph(aligned_graph, aligned_closure, "aligned-hierarchy", evidence, build, toolchain, True, timeout=args.timeout, expected_execution=plan["hierarchy/aligned"])
    print("Hierarchy attempts:", source["status"], target["status"], aligned["status"], flush=True)
    examples = []
    fixture = None
    for index, path in enumerate(corpus + [FIXTURE_PATH]):
        source_data, source_info = load_exact_local_graph((*SOURCE_PATHS, path))
        aligned_data, aligned_info = load_exact_local_graph((*SOURCE_PATHS, *TARGET_PATHS, MAPPING_PATH, path))
        prefix = "fixture" if path == FIXTURE_PATH else "examples/" + path.as_posix()
        source_result = run_graph(source_data, source_info, f"example-{index:02d}-source", evidence, build, toolchain, timeout=args.timeout, expected_execution=plan[prefix + "/source"])
        aligned_result = run_graph(aligned_data, aligned_info, f"example-{index:02d}-aligned", evidence, build, toolchain, timeout=args.timeout, expected_execution=plan[prefix + "/aligned"])
        row = {"file": fingerprint(path), "source": compact_result(source_result), "aligned": compact_result(aligned_result),
               "classification": classify_example(source_result, aligned_result)}
        print(str(path) + ": " + row["classification"], flush=True)
        if path == FIXTURE_PATH: fixture = row
        else: examples.append(row)
    manifest = json.loads((ROOT / MANIFEST_PATH).read_text())
    approved, proposed = selected_expectations(manifest)
    expectation_results = []
    for item in approved:
        query_graph, query_closure = load_exact_local_graph((*SOURCE_PATHS, *TARGET_PATHS, MAPPING_PATH,
                                                           *(Path(p) for p in item.get("input_files", []))))
        if item.get("premises_turtle"): query_graph.parse(data=item["premises_turtle"], format="turtle")
        query = dict(item["query"], id=item["id"], expected_entailed=item["expected_entailed"])
        result = run_graph(query_graph, query_closure, "expectation-" + item["id"], evidence, build, toolchain,
                           queries=[query], timeout=args.timeout, expected_execution=plan["expectations/" + item["id"]])
        expectation_results.append(compact_result(result))
    comparison = {"source": approximate_difference(source, aligned), "target": approximate_difference(target, aligned)}
    blockers = []
    unresolved = sorted({item["import"] for item in aligned_closure["unresolved_imports"]})
    if unresolved: blockers.append("No local artifact resolves imported ontology: " + ", ".join(unresolved) + ". Exact transitive import closure is unavailable; no network fetch was attempted.")
    for label, result in (("Source", source), ("Target", target), ("Aligned", aligned)):
        payload = result.get("reasoner_result", {})
        if result["status"] != "consistent":
            blockers.append(f"{label} hierarchy: {result['status']}; {result.get('error', payload.get('status', 'unknown'))}. See individual profile/reasoner outputs.")
    if any(row["classification"] != "aligned consistent" for row in examples + [fixture]):
        blockers.append("Exact-closure example success is not established for every source example and the separate fixture.")
    if any(item["status"] != "PASS" for item in comparison.values()):
        blockers.append("Source and target approximate deductive-difference comparisons do not both have a valid PASS result.")
    polarities = {item["expected_entailed"] for item in approved if item["evidence_role"] == "independent_semantic_expectation"}
    if polarities != {True, False}: blockers.append("Human approval of selected positive and negative semantic expectations is outstanding.")
    if any(item["status"] != "consistent" or len(item["reasoner_result"].get("expectations", [])) != 1
           or not all(q["passed"] for q in item["reasoner_result"].get("expectations", []))
           for item in expectation_results): blockers.append("An approved semantic expectation failed or could not execute.")
    if not (ROOT / IDENTITY_PATH).exists(): blockers.append("Current source/target identity record was unavailable at execution time.")
    extra_inputs = {Path(p) for item in approved for p in item.get("input_files", [])}
    selected = {plan_slot: run["selected_invocation_id"] for plan_slot, run in (
        [("hierarchy/source", source), ("hierarchy/target", target), ("hierarchy/aligned", aligned)] +
        [(('fixture' if row["file"]["path"] == FIXTURE_PATH.as_posix() else
           'examples/' + row["file"]["path"]) + '/' + phase,
          row[phase]) for row in examples + [fixture] for phase in ("source", "aligned")] +
        [("expectations/" + item["id"].removeprefix("expectation-"), item) for item in expectation_results]
    ) if run.get("selected_invocation_id")}
    selection_path = evidence / "selected-invocations.json"
    invocation.create_once(selection_path, invocation.canonical_bytes(invocation.sealed({
        "schema": invocation.SCHEMA, "selected_invocations": selected}, "selection_sha256")))
    report = {"schema_version": 1, "execution_evidence_schema": CURRENT_EXECUTION_EVIDENCE_SCHEMA,
              "selected_invocations": selected, "selection_record": fingerprint(selection_path),
              "track": "current-ssn-sosa", "head": git_value("rev-parse", "HEAD"),
              "branch": git_value("branch", "--show-current"), "working_tree_status": git_value("status", "--short", "--branch"),
              "executed_at_utc": datetime.now(timezone.utc).isoformat(), "status": "FAIL" if blockers else "PASS",
              "method": "HermiT complete OWL 2 DL named hierarchy/equivalence approximate deductive difference; no logical axiom removal",
              "python": sys.version, "platform": platform.platform(), "toolchain": toolchain, "java_version": java_version,
              "bound_files": [fingerprint(p) for p in sorted(set(paths) | set(corpus) | extra_inputs)],
              "hierarchy_runs": {"source": compact_result(source), "target": compact_result(target), "aligned": compact_result(aligned)},
              "conservativity": comparison, "examples": examples, "example_counts": dict(Counter(r["classification"] for r in examples)),
              "synthetic_fixture": fixture, "expectations": {**expectation_counts(approved, proposed),
                  "approved_results": expectation_results, "proposed_ids": [item["id"] for item in proposed]},
              "blockers": blockers, "evidence_directory": evidence.relative_to(ROOT).as_posix(),
              "evidence_files": [fingerprint(p) for p in sorted(evidence.rglob("*")) if p.is_file()]}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (evidence / "summary.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    write_markdown(report, output.with_suffix(".md"))
    print(f"Wrote {output.relative_to(ROOT)}; semantic gate {report['status']}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
