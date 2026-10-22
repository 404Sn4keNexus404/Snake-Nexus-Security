import argparse
import tempfile
import unittest
from pathlib import Path

from bug_bounty_documenter import (
    build_finding,
    markdown_report,
    safe_stem,
    validate_url,
    write_report,
)


def sample_args(**overrides):
    values = {
        "title": "Missing Header",
        "program": "Authorized Test",
        "severity": "medium",
        "url": "https://example.com/path",
        "summary": "A security header was absent.",
        "steps": "Open the authorized page.\nInspect response headers.",
        "impact": "Describe the verified impact.",
        "evidence": "evidence/headers.txt",
        "remediation": "Configure the appropriate header.",
    }
    values.update(overrides)
    return argparse.Namespace(**values)


class DocumenterTests(unittest.TestCase):

    def test_valid_url(self):
        self.assertEqual(
            validate_url("https://example.com/path"),
            "https://example.com/path",
        )

    def test_rejects_file_url(self):
        with self.assertRaises(ValueError):
            validate_url("file:///etc/passwd")

    def test_rejects_url_credentials(self):
        with self.assertRaises(ValueError):
            validate_url("https://user:pass@example.com/")

    def test_rejects_invalid_severity(self):
        with self.assertRaises(ValueError):
            build_finding(sample_args(severity="extreme"))

    def test_requires_reproduction_steps(self):
        with self.assertRaises(ValueError):
            build_finding(sample_args(steps="  \n "))

    def test_builds_markdown(self):
        report = markdown_report(build_finding(sample_args()))
        self.assertIn("# Missing Header", report)
        self.assertIn("## Steps to Reproduce", report)
        self.assertIn("## Recommended Remediation", report)

    def test_safe_filename(self):
        self.assertEqual(
            safe_stem("../../Bad title!"),
            "bad-title",
        )

    def test_writes_markdown_and_json(self):
        finding = build_finding(sample_args())

        with tempfile.TemporaryDirectory() as temp:
            md_path, json_path = write_report(finding, Path(temp))

            self.assertTrue(md_path.is_file())
            self.assertTrue(json_path.is_file())
            self.assertIn(
                '"severity": "Medium"',
                json_path.read_text(encoding="utf-8"),
            )

    def test_prevents_overwriting_reports(self):
        finding = build_finding(sample_args())

        with tempfile.TemporaryDirectory() as temp:
            write_report(finding, Path(temp))

            with self.assertRaises(FileExistsError):
                write_report(finding, Path(temp))


if __name__ == "__main__":
    unittest.main()
