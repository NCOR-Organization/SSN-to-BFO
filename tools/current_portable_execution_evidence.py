#!/usr/bin/env python3
"""Retain exact execution inputs and authenticate location-independent custody.

This is an additive custody adapter, not an execution, freshness or PASS waiver.
Original reports, tickets, commands, captures and envelopes are never rewritten.
Recorded graph roots and executable locations are normalized; the hash-bound
wrapper receipt identifies a governed logical role independently of its old
physical path. Content, slots, arguments, inputs, seals and outcomes stay bound.
"""
from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil

import current_retained_evidence as retained
import current_semantic_invocation as invocation


PROFILE = "current-ssn-sosa-portable-execution-v1"
MANIFESTS = retained.STORE + "/execution/manifests"
POLICY = "Exact historical execution custody only; original outcomes, HEAD/input freshness and environment qualification are not changed."
WRAPPER_ROLE = "tools/current_semantic_invocation.py"
JAVA_SOURCE_ROLE = "tools/java/CurrentSemanticReasoner.java"
TOOLCHAIN_ROLE = "config/validation-toolchain.env"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def report_identity(report: dict) -> str:
    return digest(retained._canonical(report))


def manifest_path(report: dict) -> str:
    return f"{MANIFESTS}/{report_identity(report)}.json"


def bound_file(root: Path, ref: dict) -> Path:
    path = retained._local(root, ref["path"])
    if not path.is_file():
        raise ValueError("missing portable execution source: " + ref["path"])
    data = path.read_bytes()
    if digest(data) != ref["sha256"] or ("bytes" in ref and len(data) != ref["bytes"]):
        raise ValueError("portable execution source hash or size mismatch: " + ref["path"])
    return path


def logical_path(value: str, origin: Path, root: Path) -> str:
    """Accept only canonical project paths under either authenticated root."""
    path = Path(value)
    if path.is_absolute():
        for prefix in (origin, root):
            if path.is_relative_to(prefix):
                path = path.relative_to(prefix)
                break
        else:
            raise ValueError("execution path is outside the recorded/current checkout")
    relative = path.as_posix()
    retained._local(root, relative)
    return relative


def normalized_command(command: list[str], origin: Path, root: Path) -> list[str]:
    if not isinstance(command, list) or not command or not all(isinstance(x, str) and x for x in command):
        raise ValueError("invalid portable execution command")
    result = [Path(command[0]).name]
    if result[0] not in {"java", "javac"}:
        raise ValueError("unsupported portable semantic executable")
    for index, value in enumerate(command[1:], 1):
        if command[index - 1] in {"-cp", "-classpath"}:
            result.append(":".join("repo:" + logical_path(part, origin, root) for part in value.split(":")))
        elif Path(value).is_absolute():
            result.append("repo:" + logical_path(value, origin, root))
        else:
            result.append(value)
    return result


def _inventory(report: dict, root: Path) -> tuple[Path, list[dict], list[dict]]:
    """Derive roles/dependencies from hash-bound raw records, not manifest claims."""
    if report.get("execution_evidence_schema") != 2:
        raise ValueError("portable retention requires ticketed execution schema 2")
    directory = retained._local(root, report["evidence_directory"])
    bindings = {item["path"]: item for item in report["evidence_files"]}
    if len(bindings) != len(report["evidence_files"]):
        raise ValueError("duplicate portable source evidence binding")
    for ref in bindings.values():
        bound_file(root, ref)
    selected = report["selected_invocations"]
    if not selected or len(set(selected.values())) != len(selected):
        raise ValueError("missing or duplicated selected portable invocation")
    documents, commands, origins = [], {}, set()
    for slot, identifier in sorted(selected.items()):
        ticket_ref = bindings[(directory / "invocations" / (identifier + ".ticket.json")).relative_to(root).as_posix()]
        ticket = invocation.read_ticket(bound_file(root, ticket_ref))
        if ticket["slot"] != slot or ticket["invocation_id"] != identifier:
            raise ValueError("portable selected invocation/slot mismatch")
        name = ticket["execution_identity"]["id"]
        raw_ref = bindings[(directory / (name + ".result.json")).relative_to(root).as_posix()]
        command_ref = bindings[(directory / (name + ".command.json")).relative_to(root).as_posix()]
        raw = json.loads(bound_file(root, raw_ref).read_bytes())
        command = json.loads(bound_file(root, command_ref).read_bytes())
        if raw.get("attempt") != command or command.get("command") != ticket["command"]:
            raise ValueError("portable producer disagrees with ticket/raw result")
        if raw.get("selected_invocation_id") != identifier or raw.get("execution_identity") != ticket["execution_identity"]:
            raise ValueError("portable raw execution identity differs from ticket")
        graph_relative = Path(raw["input_document"]["path"])
        graph_absolute = Path(ticket["graph"]["path"])
        if graph_relative.is_absolute() or not graph_absolute.is_absolute() or not graph_relative.parts:
            raise ValueError("portable graph lacks recorded relative/absolute identity")
        origin = graph_absolute
        for _ in graph_relative.parts:
            origin = origin.parent
        if origin / graph_relative != graph_absolute:
            raise ValueError("portable graph checkout-root binding differs")
        origins.add(origin)
        dependencies = [raw_ref, command_ref, ticket_ref]
        dependencies.extend(bindings[(directory / "invocations" / (identifier + suffix)).relative_to(root).as_posix()]
                            for suffix in (".envelope.json", ".capture.json", ".stdout.log", ".stderr.log"))
        for role, key, ticket_key in (("execution_graph", "input_document", "graph"),
                                      ("execution_queries", "query_document", "query")):
            ref = raw.get(key)
            if ref is None:
                if ticket.get(ticket_key) is not None:
                    raise ValueError("portable query membership mismatch")
                continue
            recorded = ticket[ticket_key]
            label = logical_path(recorded["path"], origin, root)
            if label != ref["path"] or any(ref[k] != recorded[k] for k in ("sha256", "bytes")):
                raise ValueError("portable document binding differs from ticket")
            documents.append({"role": role, "slot": slot, "invocation_id": identifier,
                "logical_path": label, "sha256": ref["sha256"], "bytes": ref["bytes"],
                "retained_path": retained.execution_object_path(ref["sha256"]),
                "producer": command_ref, "source_inputs": ticket["governed_inputs"],
                "execution_identity": ticket["execution_identity"], "dependent_records": dependencies})
        commands[command_ref["path"]] = (command_ref, command)
    if len(origins) != 1:
        raise ValueError("portable execution records disagree on original checkout root")
    origin = origins.pop()
    for name in ("javac.command.json", "java-version.command.json"):
        label = (directory / name).relative_to(root).as_posix()
        if label in bindings:
            commands[label] = (bindings[label], json.loads(bound_file(root, bindings[label]).read_bytes()))
    tools = []
    for _, (ref, command) in sorted(commands.items()):
        tool = command["execution_binding"]["tool"]
        if tool.get("path") != command["command"][0]:
            raise ValueError("portable command tool binding differs")
        retained._sha(tool["sha256"])
        tools.append({"producer": ref, "command": normalized_command(command["command"], origin, root),
                      "executable": {"name": Path(tool["path"]).name, "sha256": tool["sha256"],
                                     "bytes": tool.get("bytes")}})
    return origin, documents, tools


def _toolchain_binding(report: dict) -> dict:
    """Keep measured version output separate from unperformed host qualification."""
    inputs = {item["path"]: item for item in report["bound_files"]}
    evidence = {item["path"]: item for item in report["evidence_files"]}
    directory = report["evidence_directory"]
    version_label = directory + "/java-version.command.json"
    version = report.get("java_version")
    return {"configured_environment": inputs.get("config/validation-toolchain.env"),
            "reasoner_jar": report.get("toolchain", {}).get("jar"),
            "reasoner_source": inputs.get("tools/java/CurrentSemanticReasoner.java"),
            "version_command": evidence.get(version_label),
            "version_outputs": [version[channel] for channel in ("stdout", "stderr")
                                if isinstance(version, dict) and channel in version],
            "environment_qualification": "NOT_CLAIMED_BY_RETENTION",
            "runtime_policy": "Historical measured version output and configured JAR identity are retained; a relocated host still requires existing environment qualification and executable/content checks."}


def retain(root: Path, report_path: str, *, created_at: str | None = None) -> Path:
    """Retain exact inputs of an existing run; create no execution or success claim."""
    root = Path(root).resolve()
    source = retained._local(root, report_path)
    data = source.read_bytes()
    report = json.loads(data)
    origin, documents, tools = _inventory(report, root)
    relative = manifest_path(report)
    target = retained._local(root, relative)
    if target.exists():
        raise ValueError("portable execution manifest already exists; preserve historical custody")
    timestamp = created_at or datetime.now(timezone.utc).isoformat()
    retained._creation_date(timestamp)
    # Read and authenticate every graph before adding any retained objects.
    payloads = []
    for ref in documents:
        path = retained._local(root, ref["logical_path"])
        payload = path.read_bytes()
        if digest(payload) != ref["sha256"] or len(payload) != ref["bytes"]:
            raise ValueError("execution input no longer matches recorded bytes")
        payloads.append((ref, payload))
    document = {"schema_version": 1, "profile": PROFILE, "created_at": timestamp,
        "source_report": {"path": report_path, "sha256": digest(data), "bytes": len(data)},
        "report_identity": report_identity(report), "origin_repository_root": origin.as_posix(),
        "recorded_semantic_status": report["status"], "documents": documents, "tools": tools,
        "toolchain": _toolchain_binding(report), "policy": POLICY}
    for ref, payload in payloads:
        retained.retain_execution_object(root, payload, ref["sha256"])
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("xb") as stream:
        stream.write(retained._canonical(document))
    return target


class PortableEvidence:
    """Authenticated, explicit resolver; never substitutes different graph bytes."""

    def __init__(self, root: Path, report: dict, manifest: dict):
        # Preserve the caller's checkout spelling for argv normalization; _local
        # independently resolves paths when enforcing the filesystem boundary.
        self.root = Path(root)
        origin, documents, tools = _inventory(report, self.root)
        if (set(manifest) != {"schema_version", "profile", "created_at", "source_report", "report_identity",
                            "origin_repository_root", "recorded_semantic_status", "documents", "tools", "toolchain", "policy"}
                or type(manifest["schema_version"]) is not int or manifest["schema_version"] != 1
                or manifest["profile"] != PROFILE or manifest["report_identity"] != report_identity(report)
                or manifest["origin_repository_root"] != origin.as_posix()
                or manifest["recorded_semantic_status"] != report["status"]
                or manifest["documents"] != documents or manifest["tools"] != tools
                or manifest["toolchain"] != _toolchain_binding(report) or manifest["policy"] != POLICY):
            raise ValueError("portable execution manifest metadata/binding differs")
        retained._creation_date(manifest["created_at"])
        original = json.loads(bound_file(self.root, manifest["source_report"]).read_bytes())
        if original != report:
            raise ValueError("portable manifest source report differs")
        self.origin, self.manifest = origin, manifest
        self.report = original
        self.evidence = {ref["path"]: ref for ref in original["evidence_files"]}
        self.inputs = {ref["path"]: ref for ref in original["bound_files"]}
        if len(self.inputs) != len(original["bound_files"]):
            raise ValueError("duplicate portable governed input binding")
        manifest_bytes = retained._canonical(manifest)
        self.manifest_reference = {"path": manifest_path(original),
                                   "sha256": digest(manifest_bytes), "bytes": len(manifest_bytes)}
        self.documents = {ref["logical_path"]: ref for ref in documents}
        if len(self.documents) != len(documents):
            raise ValueError("duplicate portable execution document path")
        for ref in documents:
            retained.resolve_execution_object(self.root, ref["sha256"], ref["bytes"])
        self._verify_governed_dependencies()

    def _required_input(self, role: str) -> dict:
        ref = self.inputs.get(role)
        if ref is None:
            raise ValueError("portable required governed binding missing: " + role)
        bound_file(self.root, ref)
        return ref

    def _verify_governed_dependencies(self) -> None:
        """Check portable semantic/tool dependencies, not whole-run freshness.

        Historical implementation hashes remain historical. Their comparison
        with today's complete code/input map belongs to the freshness gate.
        """
        self._required_input(WRAPPER_ROLE)
        self._required_input(TOOLCHAIN_ROLE)
        java_source = self._required_input(JAVA_SOURCE_ROLE)
        jar = self.report.get("toolchain", {}).get("jar")
        if not isinstance(jar, dict):
            raise ValueError("portable required governed binding missing: reasoner JAR")
        bound_file(self.root, jar)
        for document in self.documents.values():
            for ref in document["source_inputs"]:
                bound_file(self.root, ref)
            command_identity = document["execution_identity"]["command_identity"]
            if (command_identity.get("helper") != java_source
                    or command_identity.get("jar") != {"path": jar["path"], "sha256": jar["sha256"]}):
                raise ValueError("portable governed reasoner source/JAR binding differs")
        for tool in self.manifest["tools"]:
            command = json.loads(bound_file(self.root, tool["producer"]).read_bytes())
            self.verify_tool(command)
        # A measured version is optional only when the original run has none.
        # Partial or altered measurements cannot become portable qualification.
        version = self.report.get("java_version")
        version_ref = self.manifest["toolchain"]["version_command"]
        if version is not None or version_ref is not None:
            if not isinstance(version, dict) or not isinstance(version_ref, dict):
                raise ValueError("portable recorded Java version binding missing")
            recorded = json.loads(bound_file(self.root, version_ref).read_bytes())
            if recorded != version or self.command(recorded["command"]) != ["java", "-version"]:
                raise ValueError("portable recorded Java version command differs")
            for channel in ("stdout", "stderr"):
                ref = version.get(channel)
                if not isinstance(ref, dict) or self.evidence.get(ref.get("path")) != ref:
                    raise ValueError("portable recorded Java version output binding missing")
                bound_file(self.root, ref)

    def _selected_ticket(self, ticket_path: Path, slot: str) -> dict:
        """Reauthenticate immutable custody before using its physical-path fact."""
        bound_file(self.root, self.manifest_reference)
        bound_file(self.root, self.manifest["source_report"])
        selected = self.report["selected_invocations"].get(slot)
        label = (Path(self.report["evidence_directory"]) / "invocations"
                 / (str(selected) + ".ticket.json")).as_posix()
        ref = self.evidence.get(label)
        if selected is None or ref is None or ticket_path != retained._local(self.root, label):
            raise ValueError("portable selected ticket path differs")
        documents = [document for document in self.documents.values()
                     if document["slot"] == slot and document["invocation_id"] == selected]
        if not documents:
            raise ValueError("portable selected invocation lacks governed documents")
        for document in documents:
            for dependency in document["dependent_records"]:
                bound_file(self.root, dependency)
        self._verify_governed_dependencies()
        return invocation.read_ticket(bound_file(self.root, ref))

    def logical(self, value: str) -> str:
        return logical_path(value, self.origin, self.root)

    def resolve(self, binding: dict) -> Path:
        label = self.logical(binding["path"])
        ref = self.documents.get(label)
        if ref is None or any(binding.get(k) != ref[k] for k in ("sha256", "bytes")):
            raise ValueError("execution document lacks exact portable retention binding")
        return retained.resolve_execution_object(self.root, ref["sha256"], ref["bytes"])

    def command(self, command: list[str]) -> list[str]:
        return normalized_command(command, self.origin, self.root)

    def verify_tool(self, command: dict) -> None:
        recorded = command["execution_binding"]["tool"]
        name = Path(command["command"][0]).name
        if Path(recorded["path"]).name != name or name not in {"java", "javac"}:
            raise ValueError("portable executable name differs")
        resolved = shutil.which(name)
        if not resolved or digest(Path(resolved).read_bytes()) != recorded["sha256"]:
            raise ValueError("portable executable identity is missing or changed")
        if recorded.get("bytes") is not None and Path(resolved).stat().st_size != recorded["bytes"]:
            raise ValueError("portable executable byte size differs")

    def command_documents(self, command: list[str]) -> list[dict]:
        values = []
        for value in command[1:]:
            if Path(value).suffix in {".rdf", ".json"}:
                label = self.logical(value)
                ref = self.documents.get(label)
                if ref is None:
                    raise ValueError("command input lacks portable retained evidence")
                self.resolve({"path": label, "sha256": ref["sha256"], "bytes": ref["bytes"]})
                values.append({"path": label, "sha256": ref["sha256"], "bytes": ref["bytes"]})
        return values

    def verify_result(self, ticket_path: Path, *, expected: dict) -> dict:
        """Verify original seals and invocation roles, never relaunch Java.

        The semantic caller additionally checks RDF graph identity and the full
        compiler/command plan through validate_execution_slot before this call.
        Basic launch/graph/query/helper roles remain enforced here as well.
        """
        ticket = self._selected_ticket(ticket_path, expected["slot"])
        paths = invocation.invocation_paths(ticket_path)
        identifier = ticket["invocation_id"]
        if (ticket["slot"] != expected["slot"] or paths["ticket"].name != identifier + ".ticket.json"
                or ticket["execution_identity"] != expected["identity"] or ticket["closure"] != expected["closure"]
                or ticket["governed_inputs"] != expected["identity"]["governed_inputs"]):
            raise ValueError("portable invocation differs from independently required slot")
        graph = self.resolve(ticket["graph"])
        query = self.resolve(ticket["query"]) if ticket.get("query") else None
        # The ticket's absolute wrapper path is an immutable historical fact,
        # not a live file to open or an alias to infer on the relocated host.
        # Its exact ticket bytes were checked above. The report supplies the
        # fixed logical role; both that role and the ticket bind the same bytes.
        helper = ticket.get("helper", {})
        governed_helper = self._required_input(WRAPPER_ROLE)
        if (not isinstance(helper.get("path"), str) or not Path(helper["path"]).is_absolute()
                or helper.get("sha256") != governed_helper["sha256"]):
            raise ValueError("portable invocation wrapper governed identity differs")
        arguments = ticket["command"]
        if (len(arguments) != (8 if query is not None else 7)
                or arguments[1:3] != ["-Xmx4G", "-cp"] or arguments[4] != "CurrentSemanticReasoner"):
            raise ValueError("portable invocation command is not the governed Java launch")
        graph_arg, mode_arg = (arguments[-3], arguments[-2]) if query is not None else (arguments[-2], arguments[-1])
        if (self.logical(graph_arg) != self.logical(ticket["graph"]["path"])
                or mode_arg != expected["identity"]["command_identity"]["mode"]
                or (query is not None and self.logical(arguments[-1]) != self.logical(ticket["query"]["path"]))):
            raise ValueError("portable invocation command does not consume the ticketed role")
        capture = json.loads(paths["capture"].read_bytes())
        envelope = json.loads(paths["envelope"].read_bytes())
        invocation.verify_seal(capture, "capture_sha256")
        invocation.verify_seal(envelope, "envelope_sha256")
        if capture.get("schema") != invocation.SCHEMA or envelope.get("schema") != invocation.SCHEMA:
            raise ValueError("portable invocation capture/envelope schema invalid")
        if envelope["capture_sha256"] != digest(paths["capture"].read_bytes()):
            raise ValueError("portable captured result differs from envelope")
        common = ("invocation_id", "nonce", "ticket_sha256", "slot")
        if any(capture.get(key) != ticket[key] or envelope.get(key) != ticket[key] for key in common):
            raise ValueError("portable invocation challenge/slot differs")
        if capture.get("begin") != invocation.BEGIN or capture.get("end") != invocation.END:
            raise ValueError("portable invocation capture markers invalid")
        if (envelope.get("execution_identity") != ticket["execution_identity"]
                or envelope.get("command") != ticket["command"] or envelope.get("helper") != ticket["helper"]
                or envelope.get("command_sha256") != digest(invocation.canonical_bytes({"command": ticket["command"]}))):
            raise ValueError("portable invocation execution identity differs from ticket")
        if (envelope.get("graph_sha256") != digest(graph.read_bytes())
                or envelope.get("query_sha256") != (digest(query.read_bytes()) if query else None)):
            raise ValueError("portable consumed input differs from ticket")
        if any(capture.get(key) != envelope.get(key) for key in ("returncode", "execution_status")):
            raise ValueError("portable invocation exit state differs")
        outputs = {}
        for channel in ("stdout", "stderr"):
            raw = base64.b64decode(capture[channel + "_base64"], validate=True)
            if (raw != paths[channel].read_bytes() or digest(raw) != envelope[channel + "_sha256"]
                    or len(raw) != envelope[channel + "_bytes"]):
                raise ValueError("portable invocation captured output differs")
            outputs[channel] = raw
        return {"ticket": ticket, "capture": capture, "envelope": envelope, "paths": paths, **outputs}


def context(report: dict, root: Path) -> PortableEvidence | None:
    path = retained._local(Path(root), manifest_path(report))
    if not path.exists():
        return None
    return PortableEvidence(root, report, retained._json(path.read_bytes()))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True, help="Existing repository-relative semantic report")
    parser.add_argument("--retain", action="store_true", help="Exclusively retain recorded inputs; do not execute a gate")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if args.retain:
        print(retain(root, args.report).relative_to(root).as_posix())
    else:
        report = json.loads(retained._local(root, args.report).read_bytes())
        selected = context(report, root)
        if selected is None:
            raise ValueError("portable execution manifest missing")
        print(json.dumps({"retention": "VERIFIED", "execution_acceptance": "NOT_CLAIMED", "documents": len(selected.documents),
                          "recorded_semantic_status": report["status"], "fresh_execution": False}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
