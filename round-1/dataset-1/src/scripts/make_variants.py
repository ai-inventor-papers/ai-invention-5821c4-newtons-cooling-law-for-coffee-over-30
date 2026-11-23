"""Write mini (3 examples) and preview (up to 10 examples, strings cut to 200 characters) variants of full_data_out.json.

Grouping is kept: examples are taken in dataset order. Usage: .venv/bin/python scripts/make_variants.py
"""
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FULL = ROOT / "full_data_out.json"
MINI = ROOT / "mini_data_out.json"
PREVIEW = ROOT / "preview_data_out.json"


def take(obj: dict, n: int) -> dict:
    out = copy.deepcopy(obj)
    left = n
    for d in out["datasets"]:
        d["examples"] = d["examples"][:left]
        left -= len(d["examples"])
    out["datasets"] = [d for d in out["datasets"] if d["examples"]]
    return out


def truncate(o):
    if isinstance(o, str):
        return o[:200]
    if isinstance(o, list):
        return [truncate(x) for x in o]
    if isinstance(o, dict):
        return {k: truncate(v) for k, v in o.items()}
    return o


def main() -> None:
    full = json.loads(FULL.read_text(encoding="utf-8"))
    MINI.write_text(json.dumps(take(full, 3), indent=2, ensure_ascii=False), encoding="utf-8")
    PREVIEW.write_text(json.dumps(truncate(take(full, 10)), indent=2, ensure_ascii=False), encoding="utf-8")
    print("wrote", MINI.name, PREVIEW.name)


if __name__ == "__main__":
    main()
