"""Read-only authentication of the three-term transition and current evidence.

This is a retained execution helper, not a semantic decision or a relaxation of
publication readiness. It writes only its new result beside this source file.
"""
import hashlib
import json
from collections import Counter
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
import current_assessment as assessment
import current_documentary_workbook as documentary
import current_semantic_workbook as semantic
import current_decision_applicability as applicability
import current_retained_evidence as retained
import current_semantic_validation as execution
import current_publication_readiness as readiness

TRANSITION = "reports/current-semantic-workbook/transitions/58481ff2-4e56-4931-a3d4-383357b16561.json"
BASELINE_SHA256 = "fc0e627b4c8cdef24aaa743defef8c8a3e447515a292a463d127f6693ae34a26"
EXPECTED = {
    "http://www.w3.org/ns/ssn/forProperty": "no_direct_mapping",
    "http://www.w3.org/ns/ssn/systems/SystemProperty": "inheritance_sufficient",
    "http://www.w3.org/ns/ssn/systems/MeasurementRange": "inheritance_sufficient",
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    output = OUT / "scoped-authentication.json"
    if output.exists():
        raise ValueError("Authentication destination already exists; preserve prior execution")
    baseline_path = OUT / "pre-reconciliation-state.json"
    if digest(baseline_path) != BASELINE_SHA256:
        raise ValueError("Preservation comparison baseline changed before execution")
    baseline = json.loads(baseline_path.read_text())
    result = {"scope": "Transition authenticity and current execution custody; no claim of full semantic or publication PASS",
        "comparison_baseline": {"path": baseline_path.relative_to(ROOT).as_posix(), "sha256": BASELINE_SHA256}, "stages": {}}
    try:
        _, documentary_chain, _ = documentary._history(ROOT)
        result["stages"]["documentary_history"] = {"status": "PASS", "updates": len(documentary_chain)}
        history = semantic.resolve_history(ROOT)
        result["stages"]["semantic_history"] = {"status": "PASS", "tail_sha256": history["tail_sha256"],
            "chain_kinds": dict(Counter(item["kind"] for item in history["chain"]))}
        records = json.loads(assessment.ASSESSMENT.read_text())["records"]
        assessment.validate(json.loads(assessment.SCOPE.read_text()), records,
                            assessment.source_graph(), assessment.processed_rows())
        three = {r["source_iri"]: r for r in records if r["source_iri"] in EXPECTED}
        assert set(three) == set(EXPECTED)
        for iri, outcome in EXPECTED.items():
            assert three[iri]["review_state"] == "final" and three[iri]["assessment_outcome"] == outcome
        result["stages"]["human_decisions_and_current_applicability"] = {"status": "PASS", "decisions": {
            iri: {"outcome": r["assessment_outcome"], "record": r["human_decision_record"]}
            for iri, r in three.items()}}
        applicability.validate_prepared_records(ROOT)
        bound = applicability._bound_records(ROOT)
        result["stages"]["applicability_records"] = {"status": "PASS", "bound_records": len(bound)}
        stored = retained.store_paths(ROOT)
        assert len(stored) == 4
        retained_results = []
        for path in sorted((ROOT / retained.STORE / "manifests").rglob("*.json")):
            manifest = json.loads(path.read_text())
            _, snapshot = retained._snapshot(ROOT, manifest["logical_path"], manifest["sha256"])
            assert retained.resolve(ROOT, manifest["logical_path"], manifest["sha256"]) == snapshot
            retained_results.append({"manifest": path.relative_to(ROOT).as_posix(),
                "snapshot": snapshot.relative_to(ROOT).as_posix(), "sha256": digest(snapshot)})
        result["stages"]["retained_evidence"] = {"status": "PASS", "bindings": retained_results}
        transition = semantic.validate_transition(ROOT, ROOT / TRANSITION)
        delta = transition["generation_expectations"]["logical_axiom_delta"]
        assert len(delta["removed"]) == 3 and not delta["added"]
        assert {a["authorization_type"] for a in transition["authorities"].values()} == {"EXPLICIT_NEW_HUMAN_DECISION"}
        result["stages"]["semantic_transition"] = {"status": "PASS", "path": TRANSITION,
            "sha256": digest(ROOT / TRANSITION), "removed": delta["removed"], "added": delta["added"]}
        prefixes = ("reports/current-human-decisions/", "reports/current-documentary-workbook/",
                    "reports/current-semantic-workbook/", "reports/current-decision-applicability/")
        custody = {p: sha for p, sha in baseline["repository_sha256"].items() if p.startswith(prefixes)}
        prior_retained = {p: sha for p, sha in baseline["repository_sha256"].items() if p.startswith("reports/retained-evidence/")}
        assert len(custody) == 135 and len(prior_retained) == 4
        assert all(digest(ROOT / p) == sha for p, sha in {**custody, **prior_retained}.items())
        result["stages"]["historical_preservation"] = {"status": "PASS", "custody_files": 135, "retained_files": 4}
        report = json.loads((OUT / "semantic.json").read_text())
        errors = execution.validate_stored(report)
        assert not errors, errors
        publication_errors = execution.validate_publication_execution_bindings(report)
        # Successful publication is a separate gate. Accept only intact custody;
        # honest nonzero profile/tool outcomes remain visible publication blockers.
        assert all(error.startswith("Semantic command did not complete successfully: ")
                   for error in publication_errors), publication_errors
        result["stages"]["current_semantic_execution_custody"] = {"status": "PASS",
            "semantic_gate_status": report["status"], "publication_execution_errors": publication_errors,
            "report": {"path": (OUT / "semantic.json").relative_to(ROOT).as_posix(), "sha256": digest(OUT / "semantic.json")}}
        inputs = {p: readiness.fingerprint(ROOT / p)["sha256"] for p in sorted(readiness.validation_inputs(ROOT))}
        head = readiness.git(ROOT, "rev-parse", "HEAD")
        receipts = []
        for name in ("assessment", "source_identity", "generation_freshness", "sosa_source_version", "sosa_products", "static_checks"):
            path = OUT / (name + ".command.json")
            receipt = json.loads(path.read_text())
            errors = readiness.command_errors(receipt, head, inputs, ROOT)
            assert not errors and receipt["returncode"] == 0, errors
            receipts.append({"path": path.relative_to(ROOT).as_posix(), "sha256": digest(path)})
        result["stages"]["current_command_execution_custody"] = {"status": "PASS", "receipts": receipts}
        assert digest(baseline_path) == BASELINE_SHA256
        result["status"] = "PASS"
    except Exception as error:
        result["status"] = "FAIL"
        result["error"] = f"{type(error).__name__}: {error}"
    with output.open("x") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    print(json.dumps(result, indent=2), flush=True)
    return int(result["status"] != "PASS")


if __name__ == "__main__":
    raise SystemExit(main())
