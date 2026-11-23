#!/usr/bin/env bash
# Full pipeline: digitize the source figures, score the drawn curves, fit and test the candidates,
# render figures, and write results/method_out.json. Runs on CPU in a few minutes.
set -euo pipefail
cd "$(dirname "$0")"
PY=.venv/bin/python
mkdir -p logs results figures data/digitized
$PY -W ignore src/digitize_figures.py
$PY -W ignore src/paper_curves.py
$PY -W ignore src/analysis.py
$PY -W ignore src/run_tests.py
$PY -W ignore src/make_figures.py
$PY -W ignore src/write_method_out.py
$PY -W ignore src/format_outputs.py
$PY -W ignore src/audit_headline_numbers.py
