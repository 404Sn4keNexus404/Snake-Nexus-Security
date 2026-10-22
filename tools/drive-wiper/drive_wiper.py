#!/usr/bin/env python3
"""Snake Nexus Drive Wiper v0.1 — read-only drive inventory prototype."""

import json
import shutil
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk


def format_bytes(value):
    """Format a byte count as a human-readable size."""
    try:
        size = float(value)
    except (TypeError, ValueError):
        return "Unknown"

    if size < 0:
        return "Unknown"
    if size == 0:
        return "0 B"

    units = ("B", "KiB", "MiB", "GiB", "TiB", "PiB")
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.1f} {unit}"
        size /= 1024
    return "Unknown"


def load_drives():
    """Read block-device information using lsblk; never write to devices."""
    if not shutil.which("lsblk"):
        raise RuntimeError("lsblk not found. Install util-linux.")

    result = subprocess.run(
        [
            "lsblk", "--json", "--bytes", "--output",
            "NAME,PATH,SIZE,TYPE,MODEL,TRAN,RM,RO,FSTYPE,MOUNTPOINTS"
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
    )
    data = json.loads(result.stdout)
    devices = []

    def visit(device, parent=""):
        item = {
            "name": device.get("name") or "Unknown",
            "path": device.get("path") or "",
            "size": device.get("size"),
            "type": device.get("type") or "Unknown",
            "model": (device.get("model") or "").strip(),
            "transport": device.get("tran") or "",
            "removable": bool(device.get("rm")),
            "readonly": bool(device.get("ro")),
            "filesystem": device.get("fstype") or "",
            "mountpoints": [
                point for point in (device.get("mountpoints") or [])
                if point
            ],
            "parent": parent,
        }
        devices.append(item)
        for child in device.get("children") or []:
            visit(child, item["name"])

    for device in data.get("blockdevices", []):
        visit(device)

    return devices


class DriveWiperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Snake Nexus Drive Wiper v0.1")
        self.root.geometry("950x520")
        self.devices = []

        ttk.Label(
            root,
            text="SNAKE NEXUS // DRIVE WIPER",
            font=("TkDefaultFont", 16, "bold"),
        ).pack(pady=(12, 4))

        ttk.Label(
            root,
            text="READ-ONLY INSPECTION PROTOTYPE — NO ERASURE FUNCTION",
        ).pack(pady=(0, 12))

        columns = (
            "name", "path", "size", "type", "model",
            "transport", "removable", "readonly", "filesystem", "mounts"
        )
        self.table = ttk.Treeview(root, columns=columns, show="headings")
        headings = {
            "name": "Device", "path": "Path", "size": "Capacity",
            "type": "Type", "model": "Model", "transport": "Transport",
            "removable": "Removable", "readonly": "Read-only",
            "filesystem": "Filesystem", "mounts": "Mount points",
        }
        for column in columns:
            self.table.heading(column, text=headings[column])
            self.table.column(column, width=105, minwidth=75)

        self.table.column("model", width=160)
        self.table.column("mounts", width=170)
        self.table.pack(fill="both", expand=True, padx=12, pady=8)

        buttons = ttk.Frame(root)
        buttons.pack(pady=8)
        ttk.Button(
            buttons, text="Refresh inventory", command=self.refresh
        ).pack(side="left", padx=5)
        ttk.Button(
            buttons, text="View details", command=self.details
        ).pack(side="left", padx=5)

        ttk.Label(
            root,
            text="Safety: this version only reads lsblk output. It cannot erase drives.",
        ).pack(pady=(0, 10))

        self.refresh()

    def refresh(self):
        try:
            self.devices = load_drives()
        except (RuntimeError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
            messagebox.showerror("Inventory error", str(exc))
            return

        self.table.delete(*self.table.get_children())
        for index, device in enumerate(self.devices):
            values = (
                device["name"],
                device["path"],
                format_bytes(device["size"]),
                device["type"],
                device["model"],
                device["transport"],
                "Yes" if device["removable"] else "No",
                "Yes" if device["readonly"] else "No",
                device["filesystem"],
                ", ".join(device["mountpoints"]),
            )
            self.table.insert("", "end", iid=str(index), values=values)

    def details(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showinfo("Select a device", "Select a device first.")
            return

        device = self.devices[int(selected[0])]
        details = (
            f"Device: {device['name']}\n"
            f"Path: {device['path']}\n"
            f"Capacity: {format_bytes(device['size'])}\n"
            f"Type: {device['type']}\n"
            f"Model: {device['model'] or 'Unknown'}\n"
            f"Transport: {device['transport'] or 'Unknown'}\n"
            f"Removable: {device['removable']}\n"
            f"Read-only: {device['readonly']}\n"
            f"Filesystem: {device['filesystem'] or 'None detected'}\n"
            f"Mount points: {', '.join(device['mountpoints']) or 'None'}\n\n"
            "This prototype performs inspection only."
        )
        messagebox.showinfo("Device details", details)


if __name__ == "__main__":
    window = tk.Tk()
    app = DriveWiperApp(window)
    window.mainloop()
