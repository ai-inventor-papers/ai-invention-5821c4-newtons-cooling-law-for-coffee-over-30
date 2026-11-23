#!/usr/bin/env bash
# Restore the Python environment and the source PDF used by this workspace.
set -euo pipefail
cd "$(dirname "$0")"
uv venv .venv --python=3.12
uv pip install --python .venv/bin/python -r requirements.txt
mkdir -p data/source
curl -sSLk -o data/source/sedlacek_dolejsi.pdf "https://ipnp-web.troja.mff.cuni.cz/~dolejsi/outreach/sedlacek_ajp.pdf"
