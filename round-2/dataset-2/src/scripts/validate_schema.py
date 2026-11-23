"""Validate a JSON file against an aii-json schema with jsonschema (same schema file and validate() call the aii-json validator uses)."""
import json
import sys
from pathlib import Path

from jsonschema import Draft7Validator

import os
schema_path = Path(os.environ["AII_JSON_SCHEMA"]) if os.environ.get("AII_JSON_SCHEMA") else Path(__file__).resolve().parent / "exp_sel_data_out.json"
schema = json.loads(schema_path.read_text(encoding="utf-8"))
doc = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
errors = sorted(Draft7Validator(schema).iter_errors(doc), key=lambda e: list(e.path))
print(f"{sys.argv[1]}: {len(errors)} schema errors")
for e in errors[:10]:
    print(" path:", list(e.absolute_path), "|", e.message)
sys.exit(1 if errors else 0)
