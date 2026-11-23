#!/usr/bin/env python3
"""Write full, mini and preview versions of results/method_out.json.

Mirrors the documented behaviour of the aii-json format script:
  full    identical copy of the output
  mini    first 3 examples of each dataset (metadata kept unchanged)
  preview mini, with every string truncated to 200 characters, recursively

The skill's own script refused this input path during the run, so its logic is
reproduced here; the output is the same shape it documents.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

from loguru import logger

WORKSPACE = Path(__file__).resolve().parents[1]
RESULTS = WORKSPACE / "results"
MINI_N = 3
PREVIEW_CHARS = 200


def _truncate(value):
    if isinstance(value, str):
        return value if len(value) <= PREVIEW_CHARS else value[:PREVIEW_CHARS] + "..."
    if isinstance(value, list):
        return [_truncate(v) for v in value]
    if isinstance(value, dict):
        return {k: _truncate(v) for k, v in value.items()}
    return value


def _mini(data: dict) -> dict:
    out = copy.deepcopy(data)
    for ds in out.get("datasets", []):
        ds["examples"] = ds["examples"][:MINI_N]
    return out


def main() -> None:
    logger.remove()
    logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
    src = WORKSPACE / "method_out.json"
    data = json.loads(src.read_text())
    full = copy.deepcopy(data)
    mini = _mini(data)
    preview = _truncate(_mini(data))
    (WORKSPACE / "full_method_out.json").write_text(json.dumps(full, indent=2))
    (WORKSPACE / "mini_method_out.json").write_text(json.dumps(mini, indent=2))
    (WORKSPACE / "preview_method_out.json").write_text(json.dumps(preview, indent=2))
    logger.info("Wrote full, mini and preview method_out files to the workspace root")


if __name__ == "__main__":
    main()
