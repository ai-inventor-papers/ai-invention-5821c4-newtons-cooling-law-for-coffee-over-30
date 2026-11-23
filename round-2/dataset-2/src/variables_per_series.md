# Variables per series

Every candidate that was read or checked in this run. "Accepted" requires per-time-point liquid temperature over at least 20 min, with a digitisation error of at most 0.5 C when read from a figure, plus provenance. Humidity or mass is required only by the Step 2 target, not for accepting a temperature series.

| # | Source | Pot or cup | Variables per time point | Points in first 30 min | Span (min) | Digitisation method and error | Decision and reason |
|---|---|---|---|---|---|---|---|
| 1 | Sedlacek & Dolejsi, Fig. 1 (AJP preprint PDF, `ipnp-web.troja.mff.cuni.cz/~dolejsi/outreach/sedlacek_ajp.pdf`) | china pot, coffee | liquid temperature only | 7 | -0.3 to 138.6 | vector markers on PDF page 1 (29 markers); y error 0.21 C (calibration residual); x error 0.06 min; overlay check passed | **ACCEPTED**: the only measured curve in the PDF. No initial temperature, room temperature, humidity, mass, geometry or lid stated. |
| 2 | Same PDF, metal-pot and vacuum-pot curves | metal pot, vacuum pot | none published | n/a | n/a | n/a | **REJECTED**: not published as curves. Table I gives fitted parameters only. |
| 3 | Same PDF, water and water-with-fat curves | water, fat-covered water | none published | n/a | n/a | n/a | **REJECTED**: not published as curves; Table I only. |
| 4 | Same PDF, Figs. 6 and 7 | evaporation test; pot photographs | raster images | n/a | n/a | not digitised | **REJECTED**: raster, not time series. |
| 5 | Sedlacek & Dolejsi, Figs. 2 to 5 | china pot | model curves, not data | n/a | n/a | n/a | **REJECTED**: model output, not measurement. |
| 6 | Langer et al. 2018, Zenodo 1402983 (CC BY 4.0) | disposable and reusable cups, 88 C hot water | none attached | n/a | n/a | n/a | **REJECTED**: only a 768.7 kB PDF attached; abstract gives only average times to 65 C (20 to 24 min disposable; 29 to 40 min reusable). The German and English abstracts disagree (29 to 42 vs 29 to 40 min). |
| 7 | Protons for Breakfast blog, "Mug Cooling: The Lid Effect" (2018) | insulated mug, lid on and off | temperature and mass in separate experiments | n/a | n/a | plotted only; no digitisation error | **REJECTED**: mass and temperature come from different runs; informal blog source; no geometry. |
| 8 | "How a soup bowl and a coffee cup cool down", IOP Physics Education, doi 10.1088/1361-6552/ad6ac9 (2024) | bowls and cups | not verifiable | n/a | n/a | full text HTTP 403; Crossref abstract only | **REJECTED**: abstract reports no per-time-point series; full text not reachable. |
| 9 | IOP paper, doi 10.1088/1361-6404/ae0dc8 (2025) | hot water, open cup | not verifiable | n/a | n/a | full text HTTP 403; Crossref abstract only | **REJECTED**: abstract reports no per-time-point series; full text not reachable. |
| 10 | ResearchGate copy of paper 8 | bowls and cups | not verifiable | n/a | n/a | HTTP 403 | **REJECTED**: not readable. |
| 11 | ScienceDirect S0735193325010334 (paper cup, hot water) | paper cup | not verifiable (snippet: ambient 25 C, RH 20 % held constant) | n/a | n/a | HTTP 403 | **REJECTED**: data not readable; humidity was held fixed, not logged. |
| 12 | arXiv 1710.00667, "Cooling jug physics" | porous clay pot-in-pot jug | ambient relative humidity as a parameter, not per time point | n/a | n/a | grep of text | **REJECTED**: porous clay jug, not a hot open cup; no per-time-point humidity. |
| 13 | Illustrative Mathematics task 382 | covered coffee cup | model f(t) = 110 e^{-0.08t} + 75 (F) | n/a | n/a | n/a | **REJECTED**: a textbook model, not measured data. |

## Summary

- Accepted series: 1 (row 1), temperature only.
- Series with humidity or cup mass per time point, accepted: 0.
- The Step 2 target of 1 to 3 humidity or mass series is not met. No such series was found; see `search_log.md` for the 14 queries and 6 sources read.
- Not re-fetched: Manitoba coffee table series and the Langer 65 C crossing-time conflict. Both were optional in the plan. The conflict is not resolved here.
