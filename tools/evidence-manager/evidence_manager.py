#!/usr/bin/env python3
"""Local evidence manifest and SHA-256 integrity checker."""

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record_evidence(file_path, evidence_id, finding_id):
    path = Path(file_path).expanduser().resolve(strict=True)

    if not path.is_file():
        raise ValueError("Evidence path must point to a regular file.")

    if not evidence_id.strip() or not finding_id.strip():
        raise ValueError("Evidence ID and finding ID are required.")

    return {
        "evidence_id": evidence_id.strip(),
        "finding_id": finding_id.strip(),
        "filename": path.name,
        "sha256": sha256_file(path),
        "size_bytes": path.stat().st_size,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }


def write_manifest(record, output_path):
    output = Path(output_path).expanduser()
    output.parent.mkdir(parents=True, exist_ok=True)

    # Do not silently overwrite an existing manifest.
    with output.open("x", encoding="utf-8") as handle:
        json.dump(record, handle, indent=2)
        handle.write("\n")

    return output


def verify_manifest(manifest_path, evidence_path):
    with Path(manifest_path).expanduser().open(
        "r", encoding="utf-8"
    ) as handle:
        record = json.load(handle)

    path = Path(evidence_path).expanduser().resolve(strict=True)
    if not path.is_file():
        raise ValueError("Evidence path must point to a regular file.")

    actual_hash = sha256_file(path)
    expected_hash = record.get("sha256", "")
    matches = actual_hash == expected_hash

    return {
        "evidence_id": record.get("evidence_id"),
        "expected_sha256": expected_hash,
        "actual_sha256": actual_hash,
        "matches": matches,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Record and verify local evidence file integrity."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    record_parser = subparsers.add_parser(
        "record", help="Hash an evidence file and write a JSON manifest."
    )
    record_parser.add_argument("--file", required=True)
    record_parser.add_argument("--evidence-id", required=True)
    record_parser.add_argument("--finding-id", required=True)
    record_parser.add_argument("--output", required=True)

    verify_parser = subparsers.add_parser(
        "verify", help="Compare an evidence file against its manifest hash."
    )
    verify_parser.add_argument("--manifest", required=True)
    verify_parser.add_argument("--file", required=True)

    args = parser.parse_args()

    try:
        if args.command == "record":
            record = record_evidence(
                args.file, args.evidence_id, args.finding_id
            )
            output = write_manifest(record, args.output)
            print("Evidence recorded successfully.")
            print(f"Manifest: {output}")
            print(f"SHA-256:  {record['sha256']}")
        else:
            result = verify_manifest(args.manifest, args.file)
            print(json.dumps(result, indent=2))
            if not result["matches"]:
                return 1
            print("Integrity check passed.")

    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
