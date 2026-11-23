# Reproducibility log: Newton's law vs published coffee-cup cooling measurements

Tool used: WebSearch and WebFetch (built-in), plus the aii-web-tools skill scripts
(`aii_fast_web_fetch.py fetch` and `grep`) through the skill's interpreter. Date of work: 2026-11-23.
No API keys or environment variables were needed beyond the skill's default setup.

## Search queries, in order run

1. `evaporation rate hot water relative humidity cooling experiment open container mass loss` (WebSearch)
2. `coffee cup cooling humidity vapour pressure deficit evaporative heat loss` (WebSearch)
3. `Vollmer 2009 Newton's law of cooling European Journal of Physics validity` (WebSearch)
4. `Newton's law of cooling coffee cup experiment measured curve comparison evaporation convection radiation` (WebSearch)
5. `open cup hot water cooling ambient humidity recorded evaporation mass loss balance Newton cooling study` (WebSearch)
6. `small cup cooling 2025 evaporation omitted underpredicts cooling rate Newton law` (WebSearch)

## Pages and PDFs fetched, and outcome

| Target | Method | Outcome |
|---|---|---|
| ucjf.troja.mff.cuni.cz/~dolejsi/outreach/sedlacek_ajp.pdf | WebFetch; then skill `grep` | TLS certificate failure on both. NOT read. |
| ipnp-web.troja.mff.cuni.cz/~dolejsi/outreach/sedlacek_ajp.pdf | WebFetch | TLS certificate failure. NOT read. |
| researchgate.net/publication/383334549 (soup bowl) | WebFetch | HTTP 403. NOT read. |
| ciencia.ucp.pt/ws/files/116791893/116791417.pdf | WebFetch | Binary PDF, not text-extractable by the fetch tool. NOT read. |
| sciencedirect.com/.../S0735193325010334 | WebFetch; skill fetch | HTTP 403. NOT read. |
| ui.adsabs.harvard.edu/abs/2009EJPh...30.1063V/abstract | WebFetch; skill fetch | Read. Full abstract obtained. |
| eric.ed.gov/?id=EJ851827 | WebFetch | Read. Same abstract (corroboration). |
| ui.adsabs.harvard.edu/abs/2025PhyEd..60a5011F/abstract | WebFetch; skill fetch | HTTP 202 / empty. NOT read. |
| iopscience.iop.org/article/10.1088/0143-0807/30/5/014/pdf | WebFetch | HTTP 403 / certificate issue. NOT read. |
| iopscience.iop.org/article/10.1088/1361-6404/ae0dc8 | WebFetch; skill grep | HTTP 403. NOT read. |
| emergent-scientist.edp-open.org/.../emsci170007.pdf | Skill `grep` (regex: humidity, evaporat, mass, runs) | Read via regex grep. Used. |
| emergent-scientist.edp-open.org/.../emsci170007.html | WebFetch | HTTP 403. (PDF used instead.) |

## Retracing the conclusion

1. Rerun the six queries above in order. Results drift; expect different ranks.
2. Re-fetch the ADS Vollmer abstract and the EDP PDF and grep for the quoted sentences in `research_out.json`.
3. Attempt the 403/TLS sources with institutional access or a corrected certificate store. Until then, claims that rest on them are recorded as unverified.
4. The hypothesis-text numbers for Sedláček and Dolejší (chi2/NDF 32.1 and 2.4; coefficients 15.8 and 1.94; z = 3.73; x = 1.34) were NOT checked against the PDF. They appear only as search-snippet content.
