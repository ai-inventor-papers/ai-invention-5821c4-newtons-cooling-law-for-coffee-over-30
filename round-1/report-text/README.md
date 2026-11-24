# Internal research report: Newton's law of cooling for an open cup of coffee

Chronological internal report for the run. It records what the literature screen,
the held-out curve dataset and the china-pot analysis established in iteration 1.

## Layout

| Path | Contents |
|---|---|
| `paper_draft.md` | the report (framing, iteration 1, dead ends, what we have learned) |
| `references.bib` | BibTeX for cited works the citation tool could resolve (Vollmer 2009) |
| `references.json` | citation-tool record for each entry in `references.bib` |
| `figures/fig1_spec.json` | chart spec for Figure 1 (residuals of three models, first 30 min) |
| `figures/fig1_v0.png`, `figures/fig1_v0.pdf` | rendered Figure 1 |
| `.aii/manifest.yaml` | storage decisions for heavy paths (none in this workspace) |

## Sources of the numbers

Every number in the report was read from the output files of the artifacts it cites:
`gen_art_experiment_1/results/analysis_tables.csv`, `analysis_results.json` and
`tests.json`, and `gen_art_dataset_1/summary_table.md`. The literature-screen figures
are narrative; the screen reports no numbers it verified.

## Not done in this iteration

- Style exemplars, domain vocabulary and field-extras steps were not run.
- The Sedlacek and Dolejsi reference was not resolved by the citation tool (rate-limited, then no match), so it has no BibTeX entry.

## Restoring removed files

No heavy paths are marked for deletion, so nothing needs restoring.
