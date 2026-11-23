"""Make mini (first 3 examples) and preview (mini + strings truncated to 200 chars) from full_data_out.json."""
import copy
import json
from pathlib import Path

D = Path(__file__).resolve().parents[1] / "data"
full = json.loads((D / "full_data_out.json").read_text())
mini = copy.deepcopy(full)
for ds in mini["datasets"]:
    ds["examples"] = ds["examples"][:3]
mini["metadata"]["variant"] = "mini: first 3 examples of the single series"

def trunc(o):
    if isinstance(o, str):
        return o if len(o) <= 200 else o[:200] + "..."
    if isinstance(o, list):
        return [trunc(x) for x in o]
    if isinstance(o, dict):
        return {k: trunc(v) for k, v in o.items()}
    return o

preview = trunc(copy.deepcopy(mini))
preview["metadata"]["variant"] = "preview: mini with strings truncated to 200 chars"
(D / "mini_data_out.json").write_text(json.dumps(mini, indent=2, ensure_ascii=False))
(D / "preview_data_out.json").write_text(json.dumps(preview, indent=2, ensure_ascii=False))
print("mini examples", len(mini["datasets"][0]["examples"]), "preview examples", len(preview["datasets"][0]["examples"]))
