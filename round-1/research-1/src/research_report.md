# Newton's law vs published coffee-cup cooling data

## Summary

Web-only literature screen of how accurately Newton's law of cooling predicts hot-coffee temperature over time, and whether open-cup studies record ambient humidity or cup mass loss alongside cooling curves. Verified: the Vollmer (2009) abstract states that simple exponential (Newton) cooling is mostly valid below a temperature-difference threshold that depends on experimental conditions, and that larger differences show appreciable deviations because radiation is not linear in temperature difference; that study uses solid objects up to 300 K, not coffee. Verified: Luniachek et al. (2017) use ambient humidity only as an input to a theoretical evaporation model, not as a measured cooling-curve variable. Not verified: the Sedláček and Dolejší pot study (search snippet: chi-squared per degree of freedom falling from 32.1 to 2.4 with an evaporation term), a 2025 CFD small-cup paper (snippet: omitting evaporation significantly underpredicts cooling), a 2025 radiation paper, a soup-bowl humidity study (snippet: evaporation higher by day than at night), and an IOP paper on evaporative and convective mechanisms. These were blocked (HTTP 403, TLS error or no text), so their claims rest on snippets only, and no number from a snippet is used. Conclusion: no verified source gives a measured 30-minute accuracy figure for a coffee cup, and no verified source records humidity or cup mass loss alongside curves. This is an absence in what could be read, not proof that no such study exists. Confidence is low; the answer would change with full text of the blocked sources.

## Research Findings

Bottom line: from the sources I could read, no published measured accuracy figure for a 30-minute coffee-cup curve could be verified, so no accuracy number is given here. What is verified is the validity range of Newton's law and two points about humidity and evaporation.

Verified points. Vollmer's analysis states that Newton's law of cooling, i.e. simple exponential behaviour, "is mostly valid if temperature differences are below a certain threshold which depends on the experimental conditions"; for larger differences "appreciable deviations occur which need the complete nonlinear treatment" [1, 2]. The radiation term is named as the cause, since radiation "does not vary linearly with temperature difference" [1]. The study uses IR imaging of solid objects with temperature differences up to 300 K, not coffee [1]. In the cooling-jug model of Luniachek et al., humidity enters the evaporation term, which is checked against a psychrometric table; the authors state that "the cooling DT is larger when the ambient temperature is high, and the humidity low" [6]. This is a theoretical prediction, not a measured cooling curve with recorded humidity [6].

Unverified points (search snippets only, or sources that could not be read). The Sedláček and Dolejší pot study is reported in a search snippet as showing the chi-squared per degree of freedom falling from 32.1 to 2.4 when an evaporation term is added [3]. The PDF could not be read (TLS certificate failure on both hosts), so the coefficients (15.8 and 1.94), the measurement error, the free exponent and evaporation power, and whether humidity was recorded are all unverified. A 2025 ScienceDirect CFD study of a 105 mm paper cup is reported in a snippet as finding that omitting evaporation significantly underpredicts the cooling rate [4]; the page returned HTTP 403. A 2025 Physics Education paper on radiation in a coffee cup is reported in a snippet as producing cooling curves that can be modelled with Newton's law [5]; no text was returned. A ResearchGate study of a soup bowl and coffee cup in a humidity-controlled box is reported in a snippet as showing evaporation much higher by day than at night [7]; the page returned HTTP 403. An IOP paper on evaporative and convective mechanisms in hot aqueous media is reported in a snippet as modelling the two losses separately [9]; HTTP 403. A Czech weighing study of cooling hot water is described in a snippet [10]; it was not read and its rate figures are not used. An informal mug experiment reports evaporation accounting for roughly a third of the extra cooling when the lid is removed [11]; this is a single informal run.

Answers to the three questions. (i) Ambient humidity measured alongside cooling curves: no verified source. Source 6 uses humidity only in its model. The snippets for sources 7 and 9 suggest humidity-controlled runs, but these are unverified. (ii) Cup mass loss measured alongside curves: no verified source; sources 10 and 11 mention weighing but were not read in full, and 11 is informal. (iii) Evaporation share reported as varying with humidity or vapour-pressure deficit, with the source's own numbers: no verified source. No number in this answer is taken from a search snippet.

Testability verdict. No verified published test of the humidity term or of the mass-loss alternate was found. Because several candidate sources were blocked, this is an absence in what could be read, not evidence that no test exists.

Confidence: low for the field-level answer. It would change with full text of sources 3, 4, 5, 7, 9 and 10.

## Sources

[1] [Newton's law of cooling revisited](https://ui.adsabs.harvard.edu/abs/2009EJPh...30.1063V/abstract) (M. Vollmer; 2009) — Full abstract read. Theoretical analysis of cooling of objects with small Biot number; Newton's law mostly valid below a temperature-difference threshold depending on experimental conditions; radiation causes nonlinear deviations; IR-imaging experiments of solid objects with differences up to 300 K.

> is mostly valid if temperature differences are below a certain threshold which depends on the experimental conditions

Locator: Abstract

> The latter does not vary linearly with temperature difference, which leads to deviations from Newton's law.

Locator: Abstract

[2] [Newton's Law of Cooling Revisited (ERIC record EJ851827)](https://eric.ed.gov/?id=EJ851827) (M. Vollmer; 2009) — Corroborates source 1: the same abstract text is given in the ERIC record for European Journal of Physics 30(5), 1063-1084.

> For any larger temperature differences appreciable deviations occur which need the complete nonlinear treatment.

Locator: Abstract

[3] [A physical description of coffee cooling in a pot](https://www-ucjf.troja.mff.cuni.cz/~dolejsi/outreach/sedlacek_ajp.pdf) (Sedláček, Dolejší) — NOT READ: the PDF returned a TLS certificate error on both the ucjf and ipnp-web hosts. Claims about chi2/NDF 32.1 and 2.4, evaporation coefficients 15.8 and 1.94, free exponent and power, error and humidity recording come from a search snippet only and are unverified.

[4] [The influence of evaporation on the cooling small cup of hot water](https://www.sciencedirect.com/science/article/pii/S0735193325010334) — NOT READ: HTTP 403. Search snippet reports a 3D CFD study (105 mm paper cup, LES, International Communications in Heat and Mass Transfer 169B) finding that omitting evaporation significantly underpredicts the cooling rate. Unverified; no humidity or mass data checked.

[5] [Radiation in the coffee cup](https://ui.adsabs.harvard.edu/abs/2025PhyEd..60a5011F/abstract) (2025) — NOT READ: HTTP 202, no text returned. Search snippet says cooling curves can be modelled with Newton's law and heat-transfer coefficients estimated; radiation deviations noted. Unverified.

[6] [Cooling jug physics](https://emergent-scientist.edp-open.org/articles/emsci/pdf/2017/01/emsci170007.pdf) (O. Luniachek et al.; 2017) — Full PDF read via regex grep. Theoretical model of a wet pot-in-pot jug; ambient humidity is an input to the evaporation model, checked against a psychrometric table. Predicts larger temperature difference at high ambient temperature and low humidity. No measured cooling curve with recorded humidity.

> As expected, the cooling DT is larger when the ambient temperature is high, and the humidity low.

Locator: Results, cooling-jug prediction (Fig. 5)

[7] [How a soup bowl and a coffee cup cool down](https://www.researchgate.net/publication/383334549_How_a_soup_bowl_and_a_coffee_cup_cool_down) — NOT READ: HTTP 403. Search snippet says the study ran in a humidity-controlled box and found evaporation much higher during the day than at night. Unverified; no numbers used.

[8] [Lid versus open cup cooling study (Ferreira; title not extracted)](https://ciencia.ucp.pt/ws/files/116791893/116791417.pdf) (João Paulo M. Ferreira) — NOT READ: the PDF is binary and the fetch tool could not extract its text. Search snippet lists J. P. M. Ferreira as author and mentions a lid-versus-open comparison. Unverified.

[9] [The cooling of hot aqueous media: contributions of evaporative and convective mechanisms](https://iopscience.iop.org/article/10.1088/1361-6404/ae0dc8) — NOT READ: HTTP 403. Search snippet says evaporative loss and convective loss are modelled separately, with the convective part following Newton's law, and that hot-water experiments test the model. Unverified.

[10] [Studying the Rate of Evaporation Using Pocket and Computer-Supported Weighing Scales](http://kdf.mff.cuni.cz/~kacovsky/clanky/tpt2021.pdf) — NOT READ: search snippet only. Describes weighing hot water while it cools, deriving rates from mass lost per 1 C step. Its rate numbers are not used. Candidate mass-loss source, unverified.

[11] [Mug Cooling: The Lid Effect](https://protonsforbreakfast.wordpress.com/2018/11/12/mug-cooling-the-lid-effect/) — Informal blog snippet only, not peer-reviewed. Reports weighing a mug over time and attributing roughly one third of the extra cooling with the lid removed to evaporation. Single run. Not verified.

## Verification

Numbered citations resolve to unique listed sources. Passage checks test text occurrence, not claim truth or entailment. Author/year metadata and locators are not independently verified. Details: `research_verification.json`.

- Source [1]: text found — is mostly valid if temperature differences are below a certain threshold which depends on the experi
- Source [1]: text found — The latter does not vary linearly with temperature difference, which leads to deviations from Newton
- Source [2]: text found — For any larger temperature differences appreciable deviations occur which need the complete nonlinea
- Source [6]: text found — As expected, the cooling DT is larger when the ambient temperature is high, and the humidity low.

## Follow-up Questions

- Can the Sedláček and Dolejší full text be obtained by another route (current copy, library access, or a corrected certificate store) to verify the chi2/NDF values, the 15.8 and 1.94 evaporation coefficients, the 0.3 C error, and whether humidity is recorded?
- Do the 2025 CFD small-cup paper, the 2025 radiation paper, the IOP 1361-6404 paper, or the soup-bowl study report ambient humidity, cup mass loss, or an evaporation share with numbers once their full text is read?
- Can Vollmer's temperature-difference threshold be evaluated for a cup of coffee, given its Biot number and the radiation share near boiling temperature, and does it hold over a 30-minute window?

---
*Generated by AI Inventor Pipeline*
