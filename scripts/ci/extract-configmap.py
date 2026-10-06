#!/usr/bin/env python3
"""Write every key under `data` of a ConfigMap manifest to its own file.

Prometheus config and rules live inside ConfigMaps, but promtool only reads
plain files, so CI unpacks them first.

Usage: extract-configmap.py <configmap.yaml> <output-dir>
"""
import pathlib
import sys

import yaml


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2

    manifest = pathlib.Path(sys.argv[1])
    out_dir = pathlib.Path(sys.argv[2])

    doc = yaml.safe_load(manifest.read_text())
    if doc.get("kind") != "ConfigMap" or not doc.get("data"):
        print(f"{manifest}: not a ConfigMap with a non-empty data section", file=sys.stderr)
        return 1

    out_dir.mkdir(parents=True, exist_ok=True)
    for name, content in doc["data"].items():
        target = out_dir / name
        target.write_text(content)
        print(f"{manifest}: wrote {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
