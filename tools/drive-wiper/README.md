# Snake Nexus Drive Wiper

**Version:** 0.1 — read-only prototype

## Current functionality

- Graphical Tkinter interface.
- Lists block devices and partitions using `lsblk`.
- Shows capacity, model, transport, filesystem, mount points,
  removable status, and read-only status.
- Refreshes inventory and displays device details.

## Safety limits

This version is an inspection tool only. It contains no drive-erasure
implementation, raw-device writes, or privileged command execution.
Do not treat inventory information as proof that a drive is safe to erase.

## Requirements (Kali Linux)

```bash
sudo apt update
sudo apt install python3 python3-tk util-linux
```

## Run

From this directory:

```bash
python3 drive_wiper.py
```

Do not run this GUI with `sudo`.

## Tests

```bash
PYTHONPATH=. python3 -m unittest discover -s tests -v
```

The tests exercise formatting logic. They do not test physical drives
or authorize destructive operations.
