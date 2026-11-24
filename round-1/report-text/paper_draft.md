# Internal research report: Newton's law of cooling for an open cup of coffee

## Framing

This report records a run that asks how accurately Newton's law of cooling predicts the temperature of an open cup of coffee over 30 minutes, measured against published data. Newton's law, dT/dt = -k (T - T_room), is the default model for hot drinks, for food-safety timing, and for time-of-death estimates. Its accuracy for real cups is usually asserted rather than measured. The run's hypothesis says the constant-rate law misfits the early part of the curve, that a two-term model with a nonlinear convective term and a steeply temperature-dependent evaporative term fixes this, and that ambient humidity may enter the evaporative term. The hypothesis was framed around held-out sessions and a fat-covered control. This section records what the first iteration could and could not test.

The iteration had three artifacts. Two of them supplied evidence: a set of eight published cooling curves for held-out tests [ARTIFACT:art_-CfKbDAPDpKm], and a digitized, refitted analysis of the china-pot coffee curve published by Sedlacek and Dolejsi [1] [ARTIFACT:art_UaVOg91elcVt]. The third was a web-only literature screen [ARTIFACT:art_S9mDwyLN2pcT]. The sections below follow the order in which the artifacts ran.

# Iteration 1

## Strategy

The hypothesis names several tests. The first iteration had no measured data of its own and no way to collect new sessions, so its job was to find what published evidence exists and to test the constant-rate law on the one curve that could be digitized with enough precision. The iteration ran three artifacts in this order.

1. A literature screen, to learn whether any verified source gives a measured 30-minute accuracy figure for a coffee cup, and whether any open-cup study records ambient humidity or cup mass loss alongside its curves.
2. A dataset of held-out curves, to find the evidence that a later iteration can use to test the model without refitting on it.
3. An experiment that digitized the Sedlacek and Dolejsi china-pot curve, fitted the constant-rate law and rival models to its first 30 minutes, and checked the source's own reported statistics before using them as a ranking.

The experiment was the only artifact that produced fitted values. The dataset produced evidence for later use, and the screen produced a negative finding about what the literature records.

## Artifact 1: literature screen

The screen searched for measured accuracy of Newton's law on hot coffee and for humidity or cup mass loss recorded with cooling curves [ARTIFACT:art_S9mDwyLN2pcT]. Its verified findings are narrow. Vollmer's analysis states that simple exponential cooling holds mostly below a temperature-difference threshold that depends on conditions, and that larger differences show appreciable deviations, attributed to radiation being nonlinear in temperature difference [2]. That study used solid objects up to 300 K, not coffee. A second verified source, Luniachek et al. (2017), uses ambient humidity only as an input to a theoretical evaporation model, not as a measured cooling-curve variable.

Several other sources could not be read. They returned HTTP 403, a TLS error or no text. The screen recorded their search snippets, including a chi-squared-per-degree-of-freedom drop from 32.1 to 2.4 for the Sedlacek and Dolejsi pot study, and a claim that a soup-bowl study found higher evaporation by day than by night. The screen states that no number from a snippet is used. Its conclusion is that no verified source gives a measured 30-minute accuracy figure for a coffee cup, and that no verified source records humidity or cup mass loss alongside curves. The screen notes that this is an absence in what could be read, not proof that such studies do not exist. Its confidence is low, and the screen says the answer would change with the full text of the blocked sources.

The screen therefore gives no benchmark accuracy number. The benchmark for this run has to come from the digitized curves.

## Artifact 2: held-out curve set

The dataset collects eight published cooling curves from three sources, standardized to one schema, with one source per group so that each source can be held out as a fold [ARTIFACT:art_-CfKbDAPDpKm]. The table below is the source summary written by the artifact.

| Source | Type | Curves | Liquid | Time span (min) | Sampling | Room T | Humidity | Measurement error |
|---|---|---|---|---|---|---|---|---|
| Sedlacek and Dolejsi [1] | article, venue unverified | 1 (Fig. 1) | coffee, china pot | 0 to 138.5 | about 5 min | not reported | not reported | 0.3 C (stated) |
| University of Manitoba workshop | course handout, not peer reviewed | 1 (table) | coffee | 0 to 48 | 1, 1, 1, then 5 min | 71 F (21.7 C) | not reported | not stated |
| Langer, Winkler and Lachenmeier (2018) | peer-reviewed article, DLR 114; CC-BY-4.0 Zenodo record | 6 kept of 10 digitized | hot water at 88 C, not coffee | 1 to 33 | not reported | not reported | not reported | about 3% of reading |

The artifact records four coverage limits that bear on the hypothesis. No source records relative humidity, so the humidity term cannot be tested on this set. No source gives a measured fat-layer series, so the fat-covered control cannot be run from it. Only one source gives cup geometry, and only for a non-coffee liquid, so the surface-to-volume check cannot be run on coffee. The Langer digitized crossing times for the 65 C level (18 to 32 min) disagree with the times quoted in that paper's own text (11 to 22 min). The artifact flags this disagreement and leaves it unresolved.

The artifact excluded four Langer curves to stay within its eight-curve target, and it excluded one Sedlacek trace (Fig. 3) whose marker times are irregular and differ from Fig. 1 by up to 5.2 C. Figs. 2, 4 and 5 of the Sedlacek paper repeat the Fig. 1 run, with mean absolute differences of 0.02 to 0.16 C, so they are not counted as extra curves. The search was a convenience sample of about fifteen queries. It was not a systematic review.

This set was not analysed in iteration 1. Its curves are the held-out evidence for the next iteration. The experiment below used only the Sedlacek china-pot curve, which is the one curve in this set that is also the source of the experiment's fits.

## Artifact 3: constant-rate and nonlinear fits to the china-pot curve

### Data and method

The experiment digitized the china-pot coffee curve from the vector drawing of Sedlacek and Dolejsi [1] [ARTIFACT:art_UaVOg91elcVt]. Each measured point is a square marker whose centre can be read exactly, and the axes were calibrated from tick-label centres, with residuals of 0.03 min in time and 0.07 C in temperature. The digitized series has 29 points from 0 to 138.9 min. The four figures that repeat this run agree with it to a median RMS of 0.15 C, which is below the stated 0.3 C thermometer error. The experiment therefore used sigma = 0.3 C throughout.

The fitted window is 0 to 30 min. It contains seven points, the last at 25.9 min, because the next measured point lies at 30.7 min. All window metrics are in-sample. Uncertainty comes from a residual block bootstrap over 5-minute blocks with 2000 repeats and no refit. The window has only six blocks, so those intervals are rough, as the experiment's own checks show (see below).

The candidate models were:

- C0, the constant-rate Newton law, dT/dt = -a (T - T_room), with one parameter.
- C1, nonlinear convection, dT/dt = -a (T - T_room)^x, with two parameters.
- C2, convection plus evaporation in the planned form, dT/dt = -[a (T - T_room)^x + b (T^z - T_room^z)], with four parameters.
- C2p, the source's evaporation form, with a pure power of T and no ambient term.
- C2_fixed_x, C2 with the exponent fixed at 1.25, as a fallback.

C3 (humidity-deficit evaporation) and C4 (surface-to-volume geometry) could not be run, for the reasons given in the dataset section above. T_room was fixed at 20 C, the lower limit of the source's axis. The experiment also varied T_room as a sensitivity check, reported below.

### Window results

[FIGURE:fig1]

Figure 1. Residual (model minus data) against time for the constant-rate law C0, the nonlinear convection law C1, and the source's drawn model 1 curve, over the first 30 minutes of the china-pot curve. The C0 and C1 curves are fitted to the window. The source curve is read from its figure and not refitted. Points are the seven window markers, joined by straight lines. Source: [ARTIFACT:art_UaVOg91elcVt].

Table 1 gives the window metrics for each model, read from the experiment's analysis table. The mean residual columns are model minus data.

| Model | Params | RMS 30 min (K) | 95% block-bootstrap CI (K) | Mean residual 0 to 10 min (K) | Mean residual 20 min and later (K) | chi2/NDF at sigma 0.3 C | AIC | BIC |
|---|---|---|---|---|---|---|---|---|
| C0 constant-rate (baseline) | 1 | 1.067 | 0.601 to 1.526 | +0.618 | -0.866 | 14.76 | 2.91 | 2.86 |
| C1 nonlinear convection | 2 | 0.359 | 0.097 to 0.565 | -0.110 | +0.089 | 2.01 | -10.34 | -10.45 |
| C2 plan form | 4 | 0.359 | 0.097 to 0.565 | -0.110 | +0.089 | 3.34 | -6.34 | -6.55 |
| C2_fixed_x (x = 1.25) | 3 | 0.374 | 0.107 to 0.580 | -0.124 | +0.079 | 2.71 | -7.78 | -7.95 |
| C2p source evaporation form | 4 | 0.359 | 0.097 to 0.565 | -0.110 | +0.089 | 3.34 | -6.34 | -6.55 |
| Source's drawn model 1 curve (not refit) | 1 | 2.422 | not computed | +0.987 | +2.491 | 76.02 | 14.38 | 14.33 |

Table 1. Window metrics for each candidate on the first 30 minutes of the china-pot curve (7 points). Source: analysis table of the experiment [ARTIFACT:art_UaVOg91elcVt].

Figure 1 plots the residual of each fitted model against time over the window. The constant-rate law's residual is positive over the first 10 minutes, peaks near 10 minutes, and turns negative between about 21 and 26 minutes. This is the pattern the hypothesis predicted for the first 10 minutes. The fitted nonlinear law keeps its residual within about 0.7 K throughout.

The fitted parameters were: for C0, a = 0.0263 per minute with T_room = 20 C; for C1, a = 7.1 x 10^-4 and x = 1.94. In the two-term forms the evaporation coefficient went to zero, so the evaporative term was not identifiable from this window. C2 and C2p therefore reduced to C1: the fitted convection exponent and rate were the same, and the evaporative term contributed nothing. The fixed-exponent form C2_fixed_x (x = 1.25) behaved differently. Its convection coefficient went to its lower bound (about 1 x 10^-6 per minute), and the fit was carried by the evaporative term, with z = 2.68 and b = 1.7 x 10^-5. The fit sits at a bound, so its 0.374 K RMS is recorded but is not read as evidence for evaporation.

The constant-rate law therefore gives a 30-minute RMS of about 1.1 K on this curve, with systematic early underprediction and late overprediction. AIC and BIC both rank C1 above C0 by about 13 units, the same direction as the chi2/NDF values. Both rankings rest on seven points.

### Full-record and sensitivity fits

The full 29-point record was fitted as a check on the window result. Table 2 reports the fits.

| Fit | Result | RSS per NDF (K^2) |
|---|---|---|
| C0, T_room = 20 C | a = 0.0198 per minute | 9.18 |
| C0, T_room free | T_room = 28.4 C, a = 0.0298 per minute | 0.84 |
| C1, T_room = 20 C | x = 1.68 | 0.072 |
| C1, T_room free | x = 1.82, T_room = 17.9 C | 0.066 |
| C2 plan form | b tends to zero; z at its bound of 6 | 0.065 |

Table 2. Full-record fits to all 29 points. Source: analysis results of the experiment [ARTIFACT:art_UaVOg91elcVt].

With sigma = 0.3 C, the full-record nonlinear law gives chi2/NDF of about 0.8, which is consistent with the measurement error. The constant-rate law fits the whole record well only when T_room is free, and then it takes an ambient temperature of 28.4 C. The 30-minute misfit of C0 therefore depends on the assumed ambient temperature and on whether the exponent is free. Ambient temperature is not identifiable from the 30-minute window alone. Freeing it in the window drives the C0 ambient temperature to its upper bound of 35 C, with a = 0.0395 per minute and window RMS 0.54 K. Freeing it in C1 drives the ambient temperature to 30 C, with x = 1.50 and window RMS 0.34 K, against 0.36 K with ambient fixed at 20 C. The nonlinear law's window fit is therefore nearly insensitive to the ambient choice, while the constant-rate law's is not.

An exploratory forecast fitted to the first 15 minutes (4 points) and predicted 15 to 30 minutes (3 points) gave an RMS of 2.9 K for C0 and 0.9 K for C1. Three predicted points cannot support a ranking, and the experiment does not use this result for any claim.

### Reproduction gate: failed

The experiment's plan required the source's reported chi2/NDF values (32.1, 2.4, 81.3 and 1.0) to be reproduced within 30 per cent before the candidates were ranked. They were not reproduced.

| Check | Digitized value | Source value | Ratio |
|---|---|---|---|
| Model 1, drawn curve, RSS per NDF | 3.24 | 32.1 | 0.10 |
| Model 2, drawn curve | 0.69 | 2.4 | 0.29 |
| Model 3, drawn curve | 8.08 | 81.3 | 0.10 |
| Model 4, drawn curve | 0.25 | 1.0 | 0.25 |
| Model 1, own refit, T_room = 20 C | 9.18 | 32.1 | 0.29 |
| Model 2, own refit, T_room = 20 C | 0.072 | 2.4 | 0.03 |

Table 3. Reproduction gate. The source's reported chi2/NDF values against the values computed from its own drawn curves and from the experiment's refits. Source: reproduction gate in the analysis results [ARTIFACT:art_UaVOg91elcVt].

The ratio is not constant across models, so no single rescaling explains the gap. The source does not state its ambient temperature, its initial value or its definition of chi2, so the gap cannot be closed from the paper alone. The gate failed, so the experiment's pre-registered selection rule was not applied. The experiment evaluated the rule anyway, for transparency. C1 would pass it: it has the lowest 30-minute RMS among the candidates within chi2/NDF of 1 of the best, a 66 per cent RMS reduction over C0, and a bootstrap interval for the difference that excludes zero. The experiment reports this as descriptive only. The C1 result is in-sample and cannot be used as a selection result.

### Validation checks

The experiment ran seven checks. Table 4 gives their outcomes as the experiment recorded them.

| Check | Result | Note |
|---|---|---|
| T1 synthetic recovery of the constant rate | pass | recovered rate 0.03001 against true 0.03; 96% of estimates within 2 SD |
| T2 sign convention | pass | with a nonlinear truth (x = 1.34), early residual +0.070 K and late residual -0.103 K |
| T3 reproduction gate | fail | see Table 3 |
| T4 solver against closed form | pass | maximum relative error 1.1 x 10^-9 |
| T5 bootstrap coverage | fail | 0.77 coverage for block bootstrap, 0.65 for iid, under AR(1) residuals with rho = 0.6; target 0.95 |
| T6 constant-rate residual against digitization error | fail | C0 RMS is 6.9 times the 0.15 C digitization error; interpreted as the law's real misfit |
| T7 selection dry run | pass | forcing every extension equal to C0 returns C0 |

Table 4. Validation checks [ARTIFACT:art_UaVOg91elcVt].

T5 is the check that matters most for the window intervals. The block bootstrap covers only about three quarters of the nominal 95 per cent under autocorrelated residuals, so the bootstrap intervals in Table 1 are probably too narrow. T6 was written in the plan as a test that the constant-rate misfit would be near the digitization error. It was not, and the experiment reads the excess as the law's misfit. The source's own drawn model-1 curve shows the same early-under, late-over pattern, which supports that reading, but it is not proof.

An independent re-derivation from the raw PDF, solving the models with a fixed-step Runge-Kutta integrator and Nelder-Mead rather than the closed form, reproduced the headline window RMS values to within 0.003 K. A permutation placebo that shuffled the window temperatures and refitted both models gave a median relative RMS improvement of 0.03 (maximum 0.19), against 0.66 on the real data, with permutation p = 0.01 [ARTIFACT:art_UaVOg91elcVt].

### What was not tested

- The humidity term (C3) cannot be tested: the source records no humidity and neither does any curve in the held-out set.
- The fat-covered control cannot be run. The source reports a fitted evaporation coefficient for water with fat (1.94 against 15.8 for coffee, in its Table I), but gives no fat-covered curve.
- The geometry check (C4) cannot be run. The source does not give pot dimensions, and the metal and vacuum pots appear only as fitted parameters.
- The held-out sessions in the dataset set were not scored. The Manitoba curve and the Langer curves are the next iteration's evidence.
- The source's full model includes pot and radiation terms whose constants are not in its text. The C2 and C2p forms here are reduced forms, not reproductions of the source's model.
- The ambient temperature was not reported in the source and was fixed at 20 C. The window result depends on this choice, as Table 2 shows.

## Dead ends

- **Measured accuracy from the literature.** The screen found no verified source with a measured 30-minute accuracy figure for coffee [ARTIFACT:art_S9mDwyLN2pcT]. The relevant studies were blocked. This avenue gives no benchmark, and the run falls back on the digitized curve.
- **Humidity as a measured variable.** No verified source records humidity alongside a cooling curve, and the experiment's data cannot supply it. The humidity hypothesis has no test yet.
- **The source's own selection statistics.** The reproduction gate failed, so the source's chi2/NDF ranking was not used to choose a model (Table 3).
- **Pot-geometry and cross-pot checks.** The source's metal and vacuum pot curves are not published as data, so the geometry test has no input.

## What we have learned so far

On the one published china-pot coffee curve that could be digitized precisely, a constant-rate Newton law fitted to the first 30 minutes has an in-sample RMS error of about 1.1 K. Its residual has the early-positive, late-negative shape the hypothesis predicted, and this shape also appears in the source's own drawn curve. A nonlinear convection law fits the same window to about 0.36 K in-sample. The evaporative term is not identifiable from this window, because the fitted evaporation coefficient collapses to zero in the two-term forms.

These results are in-sample, on seven points, from one curve. The source's reported chi2/NDF values could not be reproduced, so no model was selected by the pre-registered rule. The humidity term, the fat-covered control and the geometry check were not testable with the evidence available. The held-out curves collected in the dataset have not yet been scored. The next iteration should score them, and it should treat the constant-rate misfit as the claim to test on held-out data rather than as a result already established.

# Bibliography

[1] Sedlacek, M. and Dolejsi, V. "A physical description of coffee cooling in a pot." Source PDF at https://ipnp-web.troja.mff.cuni.cz/~dolejsi/outreach/sedlacek_ajp.pdf (fetched and digitized by the experiment). NOT YET IN references.bib: the citation tool returned HTTP 429 from Semantic Scholar, then no match from OpenAlex or Crossref, so no BibTeX entry was written. The journal is not shown in the extracted text, so the record must be checked before the paper step cites it.

[2] Vollmer, M. (2009). "Newton's law of cooling revisited." European Journal of Physics 30(5):1063-1084. DOI 10.1088/0143-0807/30/5/014. Read from the abstract-level summary; the full text returned HTTP 403.
