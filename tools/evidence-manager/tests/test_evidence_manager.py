import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from evidence_manager import record_evidence, write_manifest, verify_manifest


class EvidenceManagerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.evidence = self.root / "evidence.txt"
        self.evidence.write_text("authorised test evidence\n", encoding="utf-8")
        self.manifest = self.root / "manifest.json"

    def test_records_correct_sha256(self):
        record = record_evidence(self.evidence, "EVD-001", "FIND-001")
        expected = hashlib.sha256(self.evidence.read_bytes()).hexdigest()
        self.assertEqual(record["sha256"], expected)
        self.assertEqual(record["evidence_id"], "EVD-001")

    def test_writes_valid_json_manifest(self):
        record = record_evidence(self.evidence, "EVD-001", "FIND-001")
        write_manifest(record, self.manifest)
        loaded = json.loads(self.manifest.read_text(encoding="utf-8"))
        self.assertEqual(loaded["finding_id"], "FIND-001")

    def test_verifies_unchanged_evidence(self):
        record = record_evidence(self.evidence, "EVD-001", "FIND-001")
        write_manifest(record, self.manifest)
        result = verify_manifest(self.manifest, self.evidence)
        self.assertTrue(result["matches"])

    def test_detects_modified_evidence(self):
        record = record_evidence(self.evidence, "EVD-001", "FIND-001")
        write_manifest(record, self.manifest)
        self.evidence.write_text("modified evidence\n", encoding="utf-8")
        result = verify_manifest(self.manifest, self.evidence)
        self.assertFalse(result["matches"])

    def test_refuses_to_overwrite_manifest(self):
        record = record_evidence(self.evidence, "EVD-001", "FIND-001")
        write_manifest(record, self.manifest)
        with self.assertRaises(FileExistsError):
            write_manifest(record, self.manifest)

    def test_rejects_empty_ids(self):
        with self.assertRaises(ValueError):
            record_evidence(self.evidence, " ", "FIND-001")


if __name__ == "__main__":
    unittest.main()
