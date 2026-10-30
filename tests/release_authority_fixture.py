"""Test-only release implementation evidence; no production authority grants.

Historical Git identities and retained approval evidence remain independent of
live HEAD, timestamps, and local task-entry hashes. Runtime producer receipts
keep their own authority and are never repurposed as implementation approval.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))
import current_retained_evidence as retained

CURRENT_AUTHORITY_HASHES = {
    "tools/release_manifest.py":
        "89105d96dac5fb4d79128b85a5becfa3faec6ac9586507286f0c97e18f0259c5",
    "config/release-manifest-schema-v2.json":
        "b0162fb89fe2872f47b13cae9ad1a15aa2b225c6a69b4152a9c894183822191c",
    "tests/test_release_manifest.py":
        "6f25af9a9760ed644bd2b4edf36fb3110f9368eba9337ad1f310fa281499ce51",
    "tools/build_release.py":
        "3969aa59159dc5caf1c3f69b2ccef5ca9c9bd28d317b97dcb332e5a04fa2eb76",
    "tools/check_release.py":
        "3b839dbdb31142eba720a25801eb4f2f28c46a7623e60dd868024d661dfe8d6a",
    "tools/release_archive.py":
        "8928d921ac7b850f5ff52449c12013fa2c394b6d1acaff83972134b81741c974",
    "tools/rehearse_release.py":
        "737f880da62c0b33de00877404469e98b0cc6634340bbd8bab0f128676d3263d",
}


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


# The original seven historical pins above remain immutable. This fixture binds
# only the separately authorized release-contract implementation; it grants no
# production checkpoint, semantic approval, or publication-readiness status.
HISTORICAL_AUTHORITY_COMMIT = "dc314460fe3e875ba1c8ccfcb3c6840a7181e733"
CURRENT_AUTHORITY_FIXTURE = "tests/fixtures/current-release-authority/release-contract-20261028/authority.json"
CURRENT_AUTHORITY_FIXTURE_SHA256 = "beb40db1e9fca6734fc9af521ea7c91fcd01287b033c9b4e202e3fad106b78bd"


def historical_release_authority(root: Path) -> dict[str, str]:
    """Authenticate the unchanged historical pins against immutable Git blobs."""
    for relative, expected in CURRENT_AUTHORITY_HASHES.items():
        _, data = retained._git_source(root, relative, HISTORICAL_AUTHORITY_COMMIT)
        if sha256(data) != expected:
            raise ValueError("historical release-authority hash mismatch: " + relative)
    return dict(CURRENT_AUTHORITY_HASHES)


def approved_current_release_authority(root: Path) -> dict[str, str]:
    """Read reviewed test evidence, never infer approval from task-entry bytes."""
    fixture = retained.resolve(root, CURRENT_AUTHORITY_FIXTURE,
                               CURRENT_AUTHORITY_FIXTURE_SHA256, allow_retained=False)
    record = retained._json(fixture.read_bytes())
    if (set(record) != {"schema_version", "profile", "scope", "historical_predecessor",
                       "historical_sha256", "current_sha256", "authorization", "provenance"}
            or type(record["schema_version"]) is not int or record["schema_version"] != 1
            or record["profile"] != "approved-release-implementation-test-fixture-v1"
            or record["scope"] != "Test-only regression evidence; not an accepted checkpoint, semantic decision, or readiness certificate."
            or record["historical_predecessor"] != HISTORICAL_AUTHORITY_COMMIT
            or record["historical_sha256"] != CURRENT_AUTHORITY_HASHES
            or set(record["current_sha256"]) != set(CURRENT_AUTHORITY_HASHES)):
        raise ValueError("release-authority fixture policy mismatch")
    evidence = {}
    for key in ("authorization", "provenance"):
        reference = record[key]
        if set(reference) != {"path", "sha256", "bytes"}:
            raise ValueError("release-authority evidence binding mismatch")
        path = retained.resolve(root, reference["path"], reference["sha256"], allow_retained=False)
        evidence[key] = path.read_bytes()
        if type(reference["bytes"]) is not int or len(evidence[key]) != reference["bytes"]:
            raise ValueError("release-authority evidence size mismatch")
    # This exact earlier record binds implementation bytes, not a successful
    # canonical run. Its prior incomplete validation status remains unchanged.
    prior = json.loads(evidence["provenance"])
    if (prior["git_HEAD"] != HISTORICAL_AUTHORITY_COMMIT
            or not set(CURRENT_AUTHORITY_HASHES).issubset(prior["changed_this_continuation"])
            or {p: prior["repository_hashes"][p] for p in CURRENT_AUTHORITY_HASHES}
            != record["current_sha256"]):
        raise ValueError("release-authority prior implementation evidence mismatch")
    return dict(record["current_sha256"])


def current_release_authority(root: Path) -> dict[str, str]:
    expected = approved_current_release_authority(root)
    for relative, digest in expected.items():
        retained.resolve(root, relative, digest, allow_retained=False)
    return expected


# Logical roles are fixed in reviewed test policy, not supplied by mutable
# task metadata. Existing seven-file evidence remains byte-for-byte unchanged.
RELEASE_ROLES = {
    "current_release_builder": "tools/build_release.py",
    "current_release_archiver": "tools/release_archive.py",
    "current_release_rehearsal": "tools/rehearse_release.py",
    "current_release_rehearsal_regressions": "tests/test_release_rehearsal.py",
}
REHEARSAL_TEST_HISTORICAL_SHA256 = "f8c21ceabd0043e882f1cb217e8debf91e5c24b431d9ca0db55070cfc8e488fb"
REHEARSAL_TEST_PREDECESSOR_SHA256 = "f0b8877f1669b66ec4aabbc485ffe81c90e317e6752510a681489f384c2a2472"
FOLLOWUP_REQUEST = {
    "path": "tests/fixtures/current-release-authority/rehearsal-followup-20261029/authorized-request.txt",
    "sha256": "3d707055778c1911a3d4e4a04609e4e13c7295bdf4cb78f70a6ccf7a9e3ab428",
    "bytes": 12900,
}
FOLLOWUP_RESULT = {
    "path": "tests/fixtures/current-release-authority/rehearsal-followup-20261029/prior-final-state.json",
    "sha256": "3237a68d3cbd73d323f1f20a5415e15f41e90f9812970335e01f3ea38e1247ae",
    "bytes": 155072,
}


def _bound_bytes(root: Path, reference: dict) -> bytes:
    path = retained.resolve(root, reference["path"], reference["sha256"], allow_retained=False)
    data = path.read_bytes()
    if len(data) != reference["bytes"]:
        raise ValueError("release implementation evidence size mismatch")
    return data


def _role_path(role: str, logical_path: str) -> str:
    if role not in RELEASE_ROLES or logical_path != RELEASE_ROLES[role]:
        raise ValueError("release implementation role/path mismatch")
    return logical_path


def historical_role_authority(root: Path, role: str, logical_path: str) -> str:
    relative = _role_path(role, logical_path)
    expected = (REHEARSAL_TEST_HISTORICAL_SHA256 if role == "current_release_rehearsal_regressions"
                else CURRENT_AUTHORITY_HASHES[relative])
    _, data = retained._git_source(root, relative, HISTORICAL_AUTHORITY_COMMIT)
    if sha256(data) != expected:
        raise ValueError("historical release role hash mismatch")
    return expected


def current_role_authority(root: Path, role: str, logical_path: str) -> str:
    relative = _role_path(role, logical_path)
    approved = approved_current_release_authority(root)
    if role == "current_release_rehearsal_regressions":
        # The original receipt approves the first signature fix; the separate
        # follow-up approves the remaining subprocess stub. Authenticate both
        # endpoints without rewriting the original seven-file fixture.
        fixture = retained.resolve(root, CURRENT_AUTHORITY_FIXTURE,
                                   CURRENT_AUTHORITY_FIXTURE_SHA256, allow_retained=False)
        record = retained._json(fixture.read_bytes())
        predecessor = json.loads(_bound_bytes(root, record["provenance"]))
        _bound_bytes(root, FOLLOWUP_REQUEST)
        successor = json.loads(_bound_bytes(root, FOLLOWUP_RESULT))
        if (predecessor["repository_hashes"][relative] != REHEARSAL_TEST_PREDECESSOR_SHA256
                or relative not in predecessor["changed_this_continuation"]
                or successor["git_HEAD"] != HISTORICAL_AUTHORITY_COMMIT
                or successor["changed_this_continuation"] != [relative]
                or successor["added_this_continuation"] or successor["removed_this_continuation"]):
            raise ValueError("rehearsal implementation predecessor or follow-up mismatch")
        expected = successor["repository_hashes"][relative]
    else:
        expected = approved[relative]
    retained.resolve(root, relative, expected, allow_retained=False)
    return expected


def authenticate_role(root: Path, role: str, logical_path: str) -> dict[str, str]:
    return {"historical": historical_role_authority(root, role, logical_path),
            "current": current_role_authority(root, role, logical_path)}
