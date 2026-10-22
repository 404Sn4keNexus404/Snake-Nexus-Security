# Snake Nexus Bug Bounty Auto Documenter

A Python tool that creates professional bug bounty finding reports in Markdown and JSON formats.

## Features

- Records vulnerability titles and affected URLs.
- Supports Informational, Low, Medium, High, and Critical severity.
- Documents reproduction steps and security impact.
- Records evidence references and recommended remediation.
- Generates Markdown and JSON reports locally.
- Validates required fields and URLs.
- Prevents accidental overwriting of existing reports.

## Requirements

- Python 3.10 or newer recommended.
- No third-party Python packages required.

## Usage

Run the command from the Snake-Nexus-Security repository root.

Example:

```bash
python3 tools/bug-bounty-documenter/bug_bounty_documenter.py \
  --title "Missing security header" \
  --program "Example Authorized Program" \
  --severity Low \
  --url "https://example.com/" \
  --summary "A security response header was missing." \
  --steps $'1. Visit the authorized test page.\n2. Inspect the response headers.' \
  --impact "Describe the verified security impact." \
  --evidence "evidence/response-headers.txt" \
  --remediation "Configure the appropriate security header." \
  --output reports
