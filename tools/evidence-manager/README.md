# Snake Nexus Evidence Manager

A local Python CLI for recording evidence-file metadata and checking file
integrity with SHA-256 hashes.

## Features

- Calculate SHA-256 hashes for local evidence files.
- Record evidence IDs, finding IDs, filenames, file sizes, and UTC timestamps.
- Write JSON manifests without silently overwriting existing files.
- Verify evidence against the hash recorded in its manifest.
- Detect changes to evidence contents.

## Requirements

- Python 3.9 or newer
- No third-party packages required

## Record evidence

Run from the repository root:

    mkdir -p evidence manifests
    printf 'Illustrative authorised test evidence\n' > evidence/sample.txt

    python3 tools/evidence-manager/evidence_manager.py record \
      --file evidence/sample.txt \
      --evidence-id EVD-001 \
      --finding-id FIND-001 \
      --output manifests/EVD-001.json

## Verify evidence

    python3 tools/evidence-manager/evidence_manager.py verify \
      --manifest manifests/EVD-001.json \
      --file evidence/sample.txt

## Run tests

    cd tools/evidence-manager
    PYTHONPATH=. python3 -m unittest discover -s tests -v

## Limitations

A matching hash confirms that the file matches the recorded hash; it does
not independently prove when or how the original evidence was captured.
The manifest itself can be modified, so protect trusted manifests separately.

Use only with evidence you are authorised to handle.
