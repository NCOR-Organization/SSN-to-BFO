import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import current_retained_evidence as retained


HISTORICAL = b"Historical report\r\nExact bytes: \xc3\xa9\n"
CURRENT = b"Current regenerated report\n"
LOGICAL = "reports/example-current-report.md"
HASH = hashlib.sha256(HISTORICAL).hexdigest()
COMMIT = "1" * 40
CREATED = "2026-10-26T12:00:00+00:00"


def canonical(document):
    return (json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def portable_fixture(root, logical=LOGICAL):
    key = hashlib.sha256(logical.encode()).hexdigest()
    manifest = root / retained.STORE / "manifests" / key / (HASH + ".json")
    snapshot = root / retained.STORE / "sha256" / HASH / Path(logical).name
    document = {"schema_version": 1, "profile": retained.PROFILE, "logical_path": logical,
                "snapshot_path": snapshot.relative_to(root).as_posix(), "sha256": HASH,
                "bytes": len(HISTORICAL), "source_git_commit": COMMIT,
                "source_git_blob": hashlib.sha1(b"blob " + str(len(HISTORICAL)).encode()
                                                + b"\0" + HISTORICAL).hexdigest(),
                "reason": "Historical evidence path later became a regenerable report",
                "creation_date": CREATED, "custody_classification": retained.CLASSIFICATION}
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    snapshot.write_bytes(HISTORICAL)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_bytes(canonical(document))
    return manifest, snapshot, document


class PortableEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.live = self.root / LOGICAL
        self.live.parent.mkdir(parents=True)
        self.live.write_bytes(CURRENT)

    def test_unchanged_live_path_authenticates_without_retention(self):
        self.live.write_bytes(HISTORICAL)
        self.assertEqual(retained.resolve(self.root, LOGICAL, HASH), self.live)
        self.assertEqual(retained.evidence_paths(self.root, LOGICAL, HASH), [LOGICAL])
        self.assertEqual(retained.store_paths(self.root), [])

    def test_changed_live_path_uses_exact_historical_bytes_without_mutating_either(self):
        manifest, snapshot, _ = portable_fixture(self.root)
        historical_record = canonical({"path": LOGICAL, "sha256": HASH})
        record = self.root / "historical-record.json"
        record.write_bytes(historical_record)
        self.assertEqual(retained.resolve(self.root, LOGICAL, HASH), snapshot)
        self.assertEqual(snapshot.read_bytes(), HISTORICAL)
        self.assertEqual(self.live.read_bytes(), CURRENT)
        self.assertEqual(record.read_bytes(), historical_record)
        self.assertEqual(retained.evidence_paths(self.root, LOGICAL, HASH),
                         sorted([LOGICAL, manifest.relative_to(self.root).as_posix(),
                                 snapshot.relative_to(self.root).as_posix()]))
        self.assertEqual(retained.store_paths(self.root),
                         sorted([manifest.relative_to(self.root).as_posix(),
                                 snapshot.relative_to(self.root).as_posix()]))

    def test_missing_live_path_can_resolve_retained_binding(self):
        _, snapshot, _ = portable_fixture(self.root)
        self.live.unlink()
        self.assertEqual(retained.resolve(self.root, LOGICAL, HASH), snapshot)

    def test_immutable_mode_rejects_changed_or_missing_live_path_despite_snapshot(self):
        portable_fixture(self.root)
        for missing in (False, True):
            with self.subTest(missing=missing):
                if missing:
                    self.live.unlink()
                message = "missing retained evidence" if missing else "retained evidence hash mismatch"
                with self.assertRaisesRegex(ValueError, "^" + message):
                    retained.resolve(self.root, LOGICAL, HASH, allow_retained=False)

    def test_changed_live_path_without_snapshot_fails(self):
        with self.assertRaisesRegex(ValueError, "^retained evidence hash mismatch"):
            retained.resolve(self.root, LOGICAL, HASH)

    def test_missing_live_path_without_snapshot_preserves_missing_error_contract(self):
        self.live.unlink()
        with self.assertRaisesRegex(ValueError, "^missing retained evidence"):
            retained.resolve(self.root, LOGICAL, HASH)

    def test_corrupt_or_missing_snapshot_fails(self):
        _, snapshot, _ = portable_fixture(self.root)
        snapshot.write_bytes(b"corrupt snapshot")
        with self.assertRaisesRegex(ValueError, "hash or size mismatch"):
            retained.resolve(self.root, LOGICAL, HASH)
        snapshot.unlink()
        with self.assertRaisesRegex(ValueError, "missing retained evidence snapshot"):
            retained.resolve(self.root, LOGICAL, HASH)

    def test_same_hash_does_not_authorize_an_unbound_logical_path(self):
        portable_fixture(self.root)
        with self.assertRaisesRegex(ValueError, "missing retained evidence snapshot manifest"):
            retained.resolve(self.root, "reports/another-report.md", HASH)

    def test_wrong_manifest_bindings_and_metadata_fail(self):
        manifest, _, document = portable_fixture(self.root)
        wrong = {"logical_path": "reports/unrelated.md", "sha256": "0" * 64,
                 "snapshot_path": "reports/outside-store.md", "bytes": len(HISTORICAL) + 1,
                 "source_git_blob": "0" * 40, "source_git_commit": "short-ref",
                 "custody_classification": "current output", "creation_date": "not-a-date",
                 "reason": "", "profile": "different-profile", "schema_version": True}
        for key, value in wrong.items():
            with self.subTest(key=key):
                manifest.write_bytes(canonical({**document, key: value}))
                with self.assertRaises(ValueError):
                    retained.resolve(self.root, LOGICAL, HASH)

    def test_manifest_rejects_duplicate_keys_noncanonical_json_and_extra_fields(self):
        manifest, _, document = portable_fixture(self.root)
        candidates = [b'{"schema_version":1,"schema_version":1}',
                      json.dumps(document).encode(), canonical({**document, "override": True})]
        for data in candidates:
            with self.subTest(data=data[:50]):
                manifest.write_bytes(data)
                with self.assertRaises(ValueError):
                    retained.resolve(self.root, LOGICAL, HASH)

    def test_noncanonical_or_escaping_logical_paths_and_hashes_fail(self):
        for logical in ("../outside", "/tmp/outside", "reports/./example.md",
                        "reports//example.md", "reports/../example.md", "reports\\example.md"):
            with self.subTest(logical=logical), self.assertRaises(ValueError):
                retained.resolve(self.root, logical, HASH)
        for value in (None, "A" * 64, "x", "0" * 63):
            with self.subTest(hash=value), self.assertRaises(ValueError):
                retained.resolve(self.root, LOGICAL, value)

    def test_live_symlink_is_not_hidden_by_valid_snapshot(self):
        portable_fixture(self.root)
        target = self.root / "other.md"
        target.write_bytes(HISTORICAL)
        self.live.unlink()
        self.live.symlink_to(target)
        with self.assertRaisesRegex(ValueError, "noncanonical"):
            retained.resolve(self.root, LOGICAL, HASH)

    def test_live_directory_is_not_hidden_by_valid_snapshot(self):
        portable_fixture(self.root)
        self.live.unlink()
        self.live.mkdir()
        with self.assertRaisesRegex(ValueError, "regular file"):
            retained.resolve(self.root, LOGICAL, HASH)

    def test_manifest_and_snapshot_symlinks_fail(self):
        manifest, snapshot, _ = portable_fixture(self.root)
        for path in (manifest, snapshot):
            data = path.read_bytes()
            target = self.root / "other"
            target.write_bytes(data)
            path.unlink()
            path.symlink_to(target)
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "noncanonical"):
                retained.resolve(self.root, LOGICAL, HASH)
            path.unlink()
            path.write_bytes(data)

    def test_store_discovery_rejects_symlinks_including_directory_links(self):
        portable_fixture(self.root)
        link = self.root / retained.STORE / "linked-directory"
        link.symlink_to(self.root / "reports", target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "noncanonical"):
            retained.store_paths(self.root)

    def test_store_parent_symlink_cannot_redirect_snapshot_resolution(self):
        directory = self.root / "elsewhere"
        directory.mkdir()
        (self.root / retained.STORE).symlink_to(directory, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "noncanonical"):
            retained.resolve(self.root, LOGICAL, HASH)


class GitRetentionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.git("init", "--quiet")
        self.live = self.root / LOGICAL
        self.live.parent.mkdir(parents=True)
        self.live.write_bytes(HISTORICAL)
        self.commit = self.commit_files()
        self.live.write_bytes(CURRENT)

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args], stderr=subprocess.PIPE).decode().strip()

    def commit_files(self):
        self.git("add", "--all")
        self.git("-c", "user.name=Custody test", "-c", "user.email=custody@example.invalid",
                 "commit", "--quiet", "-m", "Fixture historical evidence")
        return self.git("rev-parse", "HEAD")

    def retain(self, logical=LOGICAL, expected=HASH, commit=None):
        return retained.retain_git(self.root, logical, expected, commit or self.commit,
                                   creation_date=CREATED, reason="Historical generated report")

    def test_retention_recovers_exact_git_bytes_and_preserves_current_report(self):
        manifest = self.retain()
        document = json.loads(manifest.read_text())
        self.assertEqual(document["source_git_commit"], self.commit)
        self.assertEqual(document["source_git_blob"], self.git("rev-parse", self.commit + ":" + LOGICAL))
        self.assertEqual(retained.resolve(self.root, LOGICAL, HASH).read_bytes(), HISTORICAL)
        self.assertEqual(self.live.read_bytes(), CURRENT)

    def test_existing_manifest_is_never_rewritten(self):
        manifest = self.retain()
        before = {p: (self.root / p).read_bytes() for p in retained.store_paths(self.root)}
        with self.assertRaisesRegex(ValueError, "already exists"):
            self.retain()
        self.assertEqual({p: (self.root / p).read_bytes() for p in retained.store_paths(self.root)}, before)
        self.assertTrue(manifest.is_file())

    def test_wrong_hash_or_missing_git_source_creates_no_custody_files(self):
        for expected, commit in (("0" * 64, self.commit), (HASH, "0" * 40)):
            with self.subTest(expected=expected, commit=commit), self.assertRaises(ValueError):
                self.retain(expected=expected, commit=commit)
            self.assertEqual(retained.store_paths(self.root), [])
        self.assertEqual(self.live.read_bytes(), CURRENT)

    def test_symbolic_git_references_are_not_immutable_commit_identities(self):
        with self.assertRaisesRegex(ValueError, "full object ID"):
            self.retain(commit="HEAD")
        self.assertEqual(retained.store_paths(self.root), [])

    def test_git_symlink_blob_cannot_supply_regular_historical_evidence(self):
        logical = "reports/historical-link.md"
        link = self.root / logical
        link.symlink_to(Path(LOGICAL).name)
        commit = self.commit_files()
        # Removing the live link isolates rejection of the historical Git mode.
        link.unlink()
        link_hash = hashlib.sha256(Path(LOGICAL).name.encode()).hexdigest()
        with self.assertRaisesRegex(ValueError, "regular Git file"):
            self.retain(logical=logical, expected=link_hash, commit=commit)
        self.assertEqual(retained.store_paths(self.root), [])

    def test_git_commit_path_binding_is_verified_when_repository_is_available(self):
        manifest = self.retain()
        later = self.commit_files()
        document = json.loads(manifest.read_text())
        document["source_git_commit"] = later
        manifest.write_bytes(canonical(document))
        with self.assertRaisesRegex(ValueError, "source commit/path binding mismatch"):
            retained.resolve(self.root, LOGICAL, HASH)

    def test_existing_snapshot_corruption_is_not_overwritten(self):
        _, snapshot, _ = portable_fixture(self.root)
        for path in (self.root / retained.STORE / "manifests").rglob("*.json"):
            path.unlink()
        snapshot.write_bytes(b"corrupt")
        with self.assertRaisesRegex(ValueError, "existing immutable retained snapshot differs"):
            self.retain()
        self.assertEqual(snapshot.read_bytes(), b"corrupt")

    def test_two_logical_paths_can_explicitly_bind_identical_shared_snapshot(self):
        other = "reports/other/example-current-report.md"
        path = self.root / other
        path.parent.mkdir(parents=True)
        path.write_bytes(HISTORICAL)
        commit = self.commit_files()
        self.retain()
        path.write_bytes(CURRENT)
        with self.assertRaisesRegex(ValueError, "missing retained evidence snapshot manifest"):
            retained.resolve(self.root, other, HASH)
        self.retain(logical=other, commit=commit)
        self.assertEqual(retained.resolve(self.root, LOGICAL, HASH), retained.resolve(self.root, other, HASH))


if __name__ == "__main__":
    unittest.main()
