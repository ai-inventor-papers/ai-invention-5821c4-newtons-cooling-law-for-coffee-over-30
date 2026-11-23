# Newton's law vs coffee-cup cooling data: literature screen

This folder holds a literature screen (web research only, no code or experiments). It checks whether published open-cup studies report ambient humidity or cup mass loss alongside cooling curves, and how well Newton's law of cooling matches published coffee-cup measurements.

## Layout
- `research_report.md`: source table, answers, verified vs unverified claims, follow-up questions.
- `reproducibility.md`: the queries run, the pages fetched and their outcome, and how to retrace the work.
- `research_out.json` / `.terminal_claude_agent_struct_out.json`: structured answer with numbered citations.
- `.aii/manifest.yaml`: heavy-path manifest (empty; no large files were produced).

## How to run
No code is run. Retrace the search and fetch steps listed in `reproducibility.md`.

## Restoring removed files
Nothing is marked for deletion. No restore steps are needed.

## Caveats
Several key sources returned HTTP 403 or TLS certificate errors and were not read. Their claims are recorded as unverified.
