"""Validate full, mini and preview JSON files against schemas/exp_sel_data_out.json (JSON Schema Draft 7).

Usage: .venv/bin/python scripts/validate_schema.py
"""
import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = json.loads((ROOT / "schemas" / "exp_sel_data_out.json").read_text(encoding="utf-8"))
FILES = ["full_data_out.json", "mini_data_out.json", "preview_data_out.json"]


def main() -> int:
    validator = jsonschema.Draft7Validator(SCHEMA)
    failed = False
    for name in FILES:
        data = json.loads((ROOT / name).read_text(encoding="utf-8"))
        errors = list(validator.iter_errors(data))
        n = sum(len(d["examples"]) for d in data["datasets"])
        print(f"{name}: examples={n} schema_errors={len(errors)}")
        for e in errors[:5]:
            print("  ", list(e.path)[:4], e.message[:200])
        failed = failed or bool(errors)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
