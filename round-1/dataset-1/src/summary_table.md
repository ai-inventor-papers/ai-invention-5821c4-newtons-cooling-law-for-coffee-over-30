# Summary table: published hot-liquid cooling curves (one row per source)

| source_id | source type | curves | liquid | cup / geometry | time span (min) | sampling | room T | humidity | lid / fat | measurement error |
|---|---|---|---|---|---|---|---|---|---|---|
| SEDLACEK2010 | article (venue unverified) | 1 (Fig. 1) | coffee | china pot on a table; volume not reported | 0 to 138.5 | about 5 min (marker times) | not reported | not reported | open; no measured fat-layer series | 0.3 C (stated) |
| MANITOBA_WORKSHOP | course workshop handout (not peer reviewed) | 1 (table) | coffee | cup not reported | 0 to 48 | 1, 1, 1, then 5 min | 71 F = 21.7 C (stated) | not reported | not reported | not stated; F-to-C quantization about 0.28 C |
| LANGER2018 | peer-reviewed article (DLR 114, 2018; Zenodo 10.5281/zenodo.1402983, CC-BY-4.0) | 6 kept of 10 digitized (Abb. 2, styles 01-06) | hot water at 88 C (not coffee) | single-use cups, 237 mL; material class per legend, per-curve mapping not established | 1 to 33 | not reported | not reported | not reported | not mapped per curve | about 3% of reading (logger spec) |

**Counts for the decision rule**

- Sources: 3 (meets the minimum of 3 independent sources, but each has a different measurement method).
- Curves: 8 (target 5 to 10). Langer styles 07-10 were digitized but left out to stay at 8 curves; they remain in temp/datasets/langer_abb2_raw.json.
- Sources that explicitly record relative humidity: **0 of 3**. The humidity term has no testable source in this set.
- Sources that record cup geometry (volume or surface area): 1 of 3 explicitly (Langer, 237 mL); surface area is not given in any source.
- Sources that record lid or fat-layer condition for a measured series: 0 of 3 (Sedlacek's fat-layer condition appears only in fitted Table I).
- Coffee curves: 2 (Sedlacek Fig. 1, Manitoba). Non-coffee: 6 (Langer, hot water).

**Data checks and exclusions**

- Sedlacek Fig. 2, Fig. 4 and Fig. 5 repeat the same measured run as Fig. 1 (mean absolute difference 0.02 to 0.16 C); they are not counted as extra curves.
- Sedlacek Fig. 3 is a different trace with irregular marker times (mean absolute difference 0.84 C, max 5.2 C from Fig. 1); excluded pending a check.
- Langer Abb. 2: digitized 65 C crossing times are 18 to 32 min. The text of the same paper quotes 11 to 22 min for the same cup classes. This disagreement is not resolved; the curves are kept but flagged.
- Langer Abb. 3 (reusable cups) is not included in this set.
- Manitoba table is in whole degrees F; the conversion is recorded per row.
