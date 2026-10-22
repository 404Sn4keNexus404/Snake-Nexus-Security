#!/usr/bin/env python3
"""Snake Nexus Bug Bounty Auto Documenter."""

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

SEVERITIES = ("Informational", "Low", "Medium", "High", "Critical")


def validate_url(value):
    """Validate an HTTP(S) URL without embedded credentials."""
    value = value.strip()
    parsed = urlsplit(value)

    if (
        parsed.scheme not in ("http", "https")
        or not parsed.hostname
        or any(char.isspace() for char in value)
        or parsed.username is not None
        or parsed.password is not None
    ):
        raise ValueError("Enter a valid HTTP(S) URL without credentials.")

    try:
        parsed.port
    except ValueError as exc:
        raise ValueError("Invalid port in URL.") from exc

    return value


def required(value, field):
    value = value.strip()
    if not value:
        raise ValueError(f"{field} cannot be empty.")
    return value


def build_finding(args):
    severity = args.severity.title()

    if severity not in SEVERITIES:
        raise ValueError(
            f"Severity must be one of: {', '.join(SEVERITIES)}"
        )

    # Remove existing list numbers so Markdown doesn't number twice.
    steps = [
        re.sub(r"^\s*\d+[.)]\s*", "", line.strip())
        for line in args.steps.splitlines()
        if line.strip()
    ]

    if not steps:
        raise ValueError("Provide at least one reproduction step.")

    evidence = [
        line.strip()
        for line in args.evidence.splitlines()
        if line.strip()
    ]

    return {
        "title": required(args.title, "Title"),
        "program": required(args.program, "Program"),
        "severity": severity,
        "affected_url": validate_url(args.url),
        "summary": required(args.summary, "Summary"),
        "steps_to_reproduce": steps,
        "impact": required(args.impact, "Impact"),
        "evidence_references": evidence,
        "remediation": required(args.remediation, "Remediation"),
        "created_at": datetime.now(timezone.utc).isoformat(
            timespec="seconds"
        ),
    }


def safe_stem(title):
    stem = re.sub(r"[^A-Za-z0-9_-]+", "-", title)
    return stem.strip("-_").lower()[:60] or "finding"


def markdown_report(finding):
    steps = "\n".join(
        f"{i}. {step}"
        for i, step in enumerate(
            finding["steps_to_reproduce"], start=1
        )
    )

    evidence = "\n".join(
        f"- {item}" for item in finding["evidence_references"]
    ) or "- No evidence references supplied."

    return f"""# {finding['title']}

- **Program:** {finding['program']}
- **Severity:** {finding['severity']}
- **Affected URL:** {finding['affected_url']}
- **Created:** {finding['created_at']}

## Summary

{finding['summary']}

## Steps to Reproduce

{steps}

## Impact

{finding['impact']}

## Evidence References

{evidence}

## Recommended Remediation

{finding['remediation']}

---
Generated locally by Snake Nexus Bug Bounty Auto Documenter.
Review all details and follow the program's disclosure rules.
"""


def write_report(finding, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    stem = safe_stem(finding["title"])
    md_path = output_dir / f"{stem}.md"
    json_path = output_dir / f"{stem}.json"

    if md_path.exists() or json_path.exists():
        raise FileExistsError(
            f"Report '{stem}' already exists in {output_dir}"
        )

    md_path.write_text(markdown_report(finding), encoding="utf-8")

    try:
        json_path.write_text(
            json.dumps(finding, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    except Exception:
        md_path.unlink(missing_ok=True)
        raise

    return md_path, json_path


def main():
    parser = argparse.ArgumentParser(
        description="Generate local Markdown and JSON bug bounty reports."
    )

    parser.add_argument("--title", required=True)
    parser.add_argument("--program", required=True)
    parser.add_argument("--severity", required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--steps", required=True)
    parser.add_argument("--impact", required=True)
    parser.add_argument("--evidence", default="")
    parser.add_argument("--remediation", required=True)
    parser.add_argument("--output", default="reports")

    args = parser.parse_args()

    try:
        finding = build_finding(args)
        md_path, json_path = write_report(finding, args.output)
    except (ValueError, OSError, FileExistsError) as exc:
        parser.error(str(exc))

    print("Reports created successfully!")
    print(f"Markdown: {md_path}")
    print(f"JSON:     {json_path}")


if __name__ == "__main__":
    main()
