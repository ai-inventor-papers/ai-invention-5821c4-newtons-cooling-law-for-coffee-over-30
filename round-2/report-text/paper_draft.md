# Internal research report: Newton's law of cooling for an open cup of coffee

## Framing

This report records a run that asks how accurately Newton's law of cooling predicts the temperature of an open cup of coffee over 30 minutes, measured against published data. Newton's law, dT/dt = −k (T − T_room), is the standard model for hot drinks, for food-safety timing, and for time-of-death estimates. Its accuracy for real cups is usually stated rather than measured. The run's hypothesis says the constant-rate law discrepancies the early part of the curve, that a two-term model with a nonlinear convective term and a strongly temperature-dependent evaporative term fixes this, and that ambient humidity may enter the evaporative term. The hypothesis was framed around held-out sessions and a covered control. This section records what the first stage could and could not test.

The stage had three analyses. Two of them supplied evidence: a set of eight published cooling curves for held-out tests [ARTIFACT:art_-CfKbDAPDpKm], and a read, fitted analysis of the porcelain pot coffee curve published by Sedlacek and Dolejsi [1] [ARTIFACT:art_UaVOg91elcVt]. The third was a web-only literature search [ARTIFACT:art_S9mDwyLN2pcT]. The sections below follow the order in which the analyses ran.

# Stage 1

## Strategy

The hypothesis names several tests. The first stage had no measured data of its own and no way to collect new sessions, so its task was to find what published evidence exists and to test the constant-rate law on the one curve that could be read with enough precision. The stage ran three analyses in this order.

1. A literature search, to find whether any verified source gives a measured 30-minute accuracy figure for a coffee cup, and whether any open-cup study records ambient humidity or cup mass loss with its curves.
2. A data set of held-out curves, to find the evidence that a later stage can use to test the model without fitting on it.
3. An experiment that read the Sedlacek and Dolejsi porcelain pot curve, fitted the constant-rate law and alternative models to its first 30 minutes, and checked the source's own reported statistics before using them as a ordering.

The experiment was the only analysis that produced fitted values. The data set produced evidence for later use, and the search produced a negative finding about what the literature records.

## Analysis 1: literature search

The search searched for measured accuracy of Newton's law on hot coffee and for humidity or cup mass loss recorded with cooling curves [ARTIFACT:art_S9mDwyLN2pcT]. Its verified findings are narrow. The analysis of Vollmer states that simple exponential cooling holds mostly below a temperature-difference threshold that depends on conditions, and that larger differences show large deviations, attributed to radiation being nonlinear in temperature difference [2]. That study used solid objects up to 300 K, not coffee. A second verified source, Luniachek et al. (2017), uses ambient humidity only as an variable to a theoretical evaporation model, not as a measured cooling-curve variable.

Several other sources could not be read. They returned HTTP 403, a TLS error or no content. The search recorded their search excerpts, including a χ²-per-degree-of-freedom drop from 32.1 to 2.4 for the Sedlacek and Dolejsi pot study, and a claim that a study of a hot vessel found higher evaporation by day than by night. The search states that no number from a excerpt is used. Its conclusion is that no verified source gives a measured 30-minute accuracy figure for a coffee cup, and that no verified source records humidity or cup mass loss with curves. The search notes that this is an absence in what could be read, not proof that such studies do not exist. Its confidence is low, and the search says the answer would change with the full content of the blocked sources.

The search therefore gives no benchmark accuracy number. The benchmark for this run has to come from the read curves.

## Analysis 2: held-out curve set

The data set collect eight published cooling curves from three sources, standardized to one common form, with one source per group so that each source can be held out as a fold [ARTIFACT:art_-CfKbDAPDpKm]. The table below is the source summary written by the analysis.

| Source | Type | Curves | Liquid | Time span (min) | Sampling | Room T | Humidity | Measurement error |
|---|---|---|---|---|---|---|---|---|
| Sedlacek and Dolejsi [1] | article, venue unverified | 1 (Fig. 1) | coffee, china pot | 0 to 138.5 | about 5 min | not reported | not reported | 0.3 C (stated) |
| University of Manitoba workshop | course handout, not peer reviewed | 1 (table) | coffee | 0 to 48 | 1, 1, 1, then 5 min | 71 F (21.7 C) | not reported | not stated |
| Langer, Winkler and Lachenmeier (2018) | peer-reviewed article, DLR 114; CC-BY-4.0 Zenodo record | 6 kept of 10 digitized | hot water at 88 C, not coffee | 1 to 33 | not reported | not reported | not reported | about 3% of reading |

The analysis records four scope limits that bear on the hypothesis. No source records relative humidity, so the humidity term cannot be tested on this set. No source gives a measured covering layer series, so the covered control cannot be run from it. Only one source gives cup geometry, and only for a non-coffee liquid, so the surface-to-volume check cannot be run on coffee. The Langer read crossing times for the 65 C level (18 to 32 min) differ with the times quoted in that paper's own content (11 to 22 min). The analysis notes this difference and leaves it open.

The analysis omitted four Langer curves to remain within its eight-curve target, and it omitted one Sedlacek trace (Fig. 3) whose point times vary and differ from Fig. 1 by up to 5.2 C. Figs. 2, 4 and 5 of the Sedlacek paper repeat the Fig. 1 run, with mean absolute differences of 0.02 to 0.16 C, so they are not counted as extra curves. The search was a sample of about fifteen queries. It was not a systematic review.

This set was not analysed in stage 1. Its curves are the held-out evidence for the next stage. The experiment below used only the Sedlacek porcelain pot curve, which is the one curve in this set that is also the source of the experiment's fits.

## Analysis 3: constant-rate and nonlinear fits to the porcelain pot curve

### Data and method

The experiment read the porcelain pot coffee curve from the vector drawing of Sedlacek and Dolejsi [1] [ARTIFACT:art_UaVOg91elcVt]. Each measured point is a square point whose centre can be read exactly, and the axes were calibrated from axis-name centres, with deviations of 0.03 min in time and 0.07 C in temperature. The read series has 29 points from 0 to 138.9 min. The four figures that repeat this run agree with it to a median RMS of 0.15 C, which is below the stated 0.3 C thermometer error. The experiment therefore used σ = 0.3 C throughout. [Correction, stage 2: the stage 2 readings record the reading error as 0.4 C and a calibration deviation of 0.21 C, and their window times differ from these by up to 0.4 min. See the stage 2 section.]

The fitted window is 0 to 30 min. It contains seven points, the last at 25.9 min, because the next measured point lies at 30.7 min. All window metrics are in-sample. Uncertainty comes from a deviation block bootstrap over 5-minute blocks with 2000 repeats and no fit. The window has only six blocks, so those intervals are rough, as the experiment's own checks show (see below).

The model models were:

* C0, the constant-rate Newton law, dT/dt = −a (T − T_room), with one parameter.
* C1, nonlinear convection, dT/dt = −a (T − T_room)^x, with two parameters.
* C2, convection plus evaporation in the planned form, dT/dt = −[a (T − T_room)^x + b (T^z − T_room^z)], with four parameters.
* C2p, the source's evaporation form, with a pure power of T and no ambient term.
* C2_fixed_x, C2 with the exponent fixed at 1.25, as an alternative.

C3 (humidity-difference evaporation) and C4 (surface-to-volume geometry) could not be run, for the reasons given in the data set section above. T_room was fixed at 20 C, the lower limit of the source's axis. The experiment also varied T_room as a sensitivity check, reported below.

### Window results

[FIGURE:fig1]

Figure 1. Deviation (model minus data) against time for the constant-rate law C0, the nonlinear convection law C1, and the source's drawn model 1 curve, over the first 30 minutes of the porcelain pot curve. The C0 and C1 curves are fitted to the window. The source curve is read from its figure and not fitted. Points are the seven window points, connected by straight lines. Source: [ARTIFACT:art_UaVOg91elcVt].

Table 1 gives the window metrics for each model, read from the experiment's analysis table. The mean deviation columns are model minus data.

| Model | Params | RMS 30 min (K) | 95% block-bootstrap CI (K) | Mean residual 0 to 10 min (K) | Mean residual 20 min and later (K) | chi2/NDF at sigma 0.3 C | AIC | BIC |
|---|---|---|---|---|---|---|---|---|
| C0 constant-rate (baseline) | 1 | 1.067 | 0.601 to 1.526 | +0.618 | -0.866 | 14.76 | 2.91 | 2.86 |
| C1 nonlinear convection | 2 | 0.359 | 0.097 to 0.565 | -0.110 | +0.089 | 2.01 | -10.34 | -10.45 |
| C2 plan form | 4 | 0.359 | 0.097 to 0.565 | -0.110 | +0.089 | 3.34 | -6.34 | -6.55 |
| C2_fixed_x (x = 1.25) | 3 | 0.374 | 0.107 to 0.580 | -0.124 | +0.079 | 2.71 | -7.78 | -7.95 |
| C2p source evaporation form | 4 | 0.359 | 0.097 to 0.565 | -0.110 | +0.089 | 3.34 | -6.34 | -6.55 |
| Source's drawn model 1 curve (not refit) | 1 | 2.422 | not computed | +0.987 | +2.491 | 76.02 | 14.38 | 14.33 |

Table 1. Window metrics for each model on the first 30 minutes of the porcelain pot curve (7 points). Source: analysis table of the experiment [ARTIFACT:art_UaVOg91elcVt].

Figure 1 plots the deviation of each fitted model against time over the window. The constant-rate law's deviation is positive over the first 10 minutes, peaks near 10 minutes, and turns negative between about 21 and 26 minutes. This is the pattern the hypothesis predicted for the first 10 minutes. The fitted nonlinear law keeps its deviation within about 0.7 K throughout.

[Correction, stage 2: the sign change between 21 and 26 minutes rests on one window point. The C0 deviation at 20.9 min is +0.30 K and at 25.9 min is -2.03 K, so the later mean of -0.87 K is set by the last point alone. The early pattern rests on the points at or before 10 min. Neither is a confirmed shape, and the held-out curves were not tested until stage 2.]

The fitted parameters were: for C0, a = 0.0263 per minute with T_room = 20 C; for C1, a = 7.1 x 10^-4 and x = 1.94. In the two-term forms the evaporation coefficient went to zero, so the evaporative term was not determined from this window. C2 and C2p therefore reduced to C1: the fitted convection exponent and rate were the same, and the evaporative term contributed nothing. The fixed-exponent form C2_fixed_x (x = 1.25) behaved otherwise. Its convection coefficient went to its lower bound (about 1 x 10^-6 per minute), and the fit was carried by the evaporative term, with z = 2.68 and b = 1.7 x 10^-5. The fit sits at a bound, so its 0.374 K RMS is recorded but is not read as evidence for evaporation.

The constant-rate law therefore gives a 30-minute RMS of about 1.1 K on this curve, with systematic early underestimate and later too-high prediction.

[Correction, stage 2: the 1.07 K figure (1.1 K, as stated earlier) holds only with room temperature fixed at 20 C, a value the source does not report. Stage 2 matches the fixed-ambient C0 window fit at 1.26 K, not 1.07 K, and gives 1.12 K with room temperature fitted at its 25 C bound and 1.01 K in a free-ambient benchmark. The 0.54 K free-ambient value stated below could not be matched by any output read in stage 2. See the stage 2 section.] AIC and BIC both order C1 above C0 by about 13 units, the same direction as the χ²/NDF values. Both orders rest on seven points.

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

With σ = 0.3 C, the full-record nonlinear law gives χ²/NDF of about 0.8, which is consistent with the measurement error. [Correction, stage 2: freeing T_room lowers the constant-rate law's full-record RSS per NDF from 9.18 to 0.84 K^2. At σ = 0.3 C (0.09 K^2) that is still about nine times the measurement variance, so the constant-rate law does not fit the whole record well under either ambient choice. The nonlinear law remains near 0.07 K^2 (χ²/NDF about 0.8) under both. The fitted ambient temperature with T_room free is 28.4 C.] The 30-minute discrepancy of C0 therefore depends on the assumed ambient temperature and on whether the exponent is free. Ambient temperature is not determined from the 30-minute window alone. Freeing it in the window drives the C0 ambient temperature to its upper bound of 35 C, with a = 0.0395 per minute and window RMS 0.54 K. Freeing it in C1 drives the ambient temperature to 30 C, with x = 1.50 and window RMS 0.34 K, against 0.36 K with ambient fixed at 20 C. The nonlinear law's window fit is therefore nearly the same under the ambient choice, while the constant-rate law's is not.

An preliminary prediction fitted to the first 15 minutes (4 points) and predicted 15 to 30 minutes (3 points) gave an RMS of 2.9 K for C0 and 0.9 K for C1. Three predicted points cannot support a ordering, and the experiment does not use this result for any claim.

### Agreement test: failed

The experiment's plan required the source's reported χ²/NDF values (32.1, 2.4, 81.3 and 1.0) to be matched within 30 percent before the models were ordered. They were not matched.

Origin of the four values, checked in stage 2 by a content search of the source PDF (results in the origin record of the stage 2 experiment analysis [ARTIFACT:art_pamuF8tunauJ]): 32.1 and 2.4 both appear on page 2, in the legend of the source's Fig. 3, as the content reads "χ²/NDF changed from 32.1 for the first model to 2.4 for the second model". The value 1.0 appears on page 3 in the content beside the free-power fit ("χ²/NDF = 1.0"). The value 81.3 appears on page 3 in the content ("the deviation sum χ²/NDF = 81.3 compared to 2/NDF = 32.1 for the first model"). The legends of the source's Fig. 1 and Fig. 2 were not found in the PDF content. The search shows that these numbers appear in the source. It does not show that they are the statistic the test needs, so the test result remains conditional on them.

| Check | Digitized value | Source value | Ratio |
|---|---|---|---|
| Model 1, drawn curve, RSS per NDF | 3.24 | 32.1 | 0.10 |
| Model 2, drawn curve | 0.69 | 2.4 | 0.29 |
| Model 3, drawn curve | 8.08 | 81.3 | 0.10 |
| Model 4, drawn curve | 0.25 | 1.0 | 0.25 |
| Model 1, own refit, T_room = 20 C | 9.18 | 32.1 | 0.29 |
| Model 2, own refit, T_room = 20 C | 0.072 | 2.4 | 0.03 |

Table 3. Agreement test. The source's reported χ²/NDF values against the values computed from its own drawn curves and from the experiment's fits. Source: agreement test in the analysis results [ARTIFACT:art_UaVOg91elcVt].

The ratio is not constant across models, so no single rescaling explains the difference. The source does not state its ambient temperature, its initial value or its definition of χ², so the difference cannot be closed from the paper alone. The test failed, so the experiment's planned in advance selection procedure was not applied. The experiment evaluated the criterion also, for clarity. C1 would pass it: it has the lowest 30-minute RMS among the models within χ²/NDF of 1 of the best, a 66 percent RMS reduction over C0, and a bootstrap interval for the difference that omits zero. The experiment reports this only as a summary. The C1 result is in-sample and cannot be used as a selection result.

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

T5 is the check that matters most for the window intervals. The block bootstrap covers only about three quarters of the stated 95 percent under correlated deviations, so the bootstrap intervals in Table 1 are probably too narrow. T6 was written in the plan as a test that the constant-rate discrepancy would be near the reading error. It was not, and the experiment reads the difference as the law's discrepancy. [Correction, stage 2: the statement this replaces said the source's drawn model-1 curve shows the same early-under, later-over pattern as C0. Table 1 does not support that. The drawn curve predicts too high at both early points (+0.99 K over 0 to 10 min) and later points (+2.49 K at 20 min and later), so it differs from C0 in sign at the end. The source's model therefore does not explain the 6.9 times difference over reading error. That difference is not explained by the source's model and remains an open point.]

An independent re-derivation from the raw PDF, solving the models with a fixed-step Runge-Kutta method and Nelder-Mead rather than the closed form, matched the main window RMS values to within 0.003 K. A permutation control that shuffled the window temperatures and fitted both models gave a median relative RMS gain of 0.03 (maximum 0.19), against 0.66 on the real data, with permutation p = 0.01 [ARTIFACT:art_UaVOg91elcVt].

### What was not tested

* The humidity term (C3) cannot be tested: the source records no humidity and neither does any curve in the held-out set.
* The covered control cannot be run. The source reports a fitted evaporation coefficient for water with a covering layer (1.94 against 15.8 for coffee, in its Table I), but gives no covered curve.
* The geometry check (C4) cannot be run. The source does not give pot dimensions, and the metal and vacuum pots appear only as fitted parameters.
* The held-out sessions in the data set set were not tested. The Manitoba curve and the Langer curves are the next stage's evidence.
* The source's full model includes pot and radiation terms whose constants are not in its content. The C2 and C2p forms here are reduced forms, not copies of the source's model.
* The ambient temperature was not reported in the source and was fixed at 20 C. The window result depends on this choice, as Table 2 shows.

## Dead ends

* **Measured accuracy from the literature.** The search found no verified source with a measured 30-minute accuracy figure for coffee [ARTIFACT:art_S9mDwyLN2pcT]. The relevant studies were blocked. This avenue gives no benchmark, and the run falls back on the read curve.
* **Humidity as a measured variable.** No verified source records humidity with a cooling curve, and the experiment's data cannot supply it. The humidity hypothesis has no test yet.
* **The source's own selection statistics.** The agreement test failed, so the source's χ²/NDF ordering was not used to choose a model (Table 3).
* **Pot-geometry and cross-pot checks.** The source's metal and vacuum pot curves are not published as data, so the geometry test has no variable.

# Stage 2

## Why this stage ran what it ran

The referee's blocking items were the points the stage 1 record could not answer. The eight held-out curves had been collected but not tested, so the report had no out-of-sample accuracy and no comparison with published measurements. The exponent was presented as a fixed value (x = 1.94), while the stage 1 fits themselves gave 1.50 to 1.94. The origin of the four agreement-test values was not recorded. Several statements also stated more than the tables supported: the source's drawn curve was described as sharing the constant-rate pattern, the constant-rate law was said to fit the whole record when ambient was freed, and a later sign change rested on one point.

The strategy had three parts. Two tested the constant-rate and nonlinear laws on the held-out curves, and tested whether the exponent is a stable quantity. The third covered differences in the evidence base, searching for cooling curves with humidity or cup mass logged and for the metal and vacuum pot series. The third part returned a negative result: the search found no humidity, vapour pressure, evaporation or cup mass series, and the source does not publish its metal and vacuum pot curves as data. The re-reading of the porcelain pot curve ran with it, because the held-out testing needs the fitted curve to be read from the same source.

Three analyses ran. The order in which they are described follows their dependencies: the data set first, then the held-out testing, then the exponent analysis. The referee's items on the record are addressed by the corrections already placed in the stage 1 content and by the tables below.

## Analysis 1: re-read porcelain pot curve

The data set re-read the vector points of Fig. 1 of the source [ARTIFACT:art_Wid0Tqzv6Tbp]. It records 29 points from -0.3 to 138.6 min, calibrated from axis-name centres, with calibration deviations of 0.06 min in time and 0.21 C in temperature, inside its 0.5 C acceptance limit. Each point carries empty entries for the fields the source does not state: initial and room temperature, relative humidity, cup mass, pot geometry and lid. The search behind it ran 14 queries across 6 accessible sources, with 4 more returning HTTP 403. It found no series recording humidity, vapour pressure, evaporation rate or cup mass with the cooling curve. That is an absence in what was searched, not proof that none exists. The source PDF was downloaded with the TLS check off, because its server serves a partial chain. The content was read; the transport was not checked.

The re-reading does not match stage 1's time coordinates. Stage 1 placed the window points at 3.1, 5.0 and 10.0 min, and its last window point at 25.9 min. The re-reading places them at 2.75, 4.65 and 9.66 min, and its last window point at 25.59 min. The two readings also record different reading errors, 0.15 C in stage 1 and 0.4 C in the data set. A time shift of this size would move the in-window deviations, so it is a model cause of the difference between the stage 1 the constant-rate law in-sample RMS (1.07 K) and the value matched here (1.26 K). The difference was not tested in this stage. It is the first check for the next one.

The eight held-out curves are listed in Table 5, with the four extra Langer curves read in stage 1 and tested in this stage. The Langer 65 C crossing-time note is attached to the Langer records in the data set code, so it applies to the whole Langer group. No single curve was isolated as the cause, and the note enters no fit or value here.

Table 5. Curves in the held-out set and in this stage's testing. First value is the first recorded temperature. Source: data set outputs [ARTIFACT:art_-CfKbDAPDpKm] and the testing outputs of the two experiments below.

| Curve id | Source and fold | Liquid and vessel | First recorded T (C) | Room T (C) | Role in iteration 2 |
|---|---|---|---|---|---|
| SEDLACEK2010_Fig1 | Sedlacek and Dolejsi, fold 1 | coffee, china pot | 80.25 (t = 0) | 20, default, not reported | fitting curve; in-sample |
| MANITOBA_WORKSHOP_coffee | Manitoba workshop, fold 2 | coffee, table | 85.56 (t = 0) | 21.67, recorded | held out |
| LANGER2018_Abb2-01 | Langer et al., fold 3 | hot water, 237 mL cup | 80.17 (t = 1 min) | 20, default | held out |
| LANGER2018_Abb2-02 | Langer et al., fold 3 | hot water, 237 mL cup | 80.60 | 20, default | held out |
| LANGER2018_Abb2-03 | Langer et al., fold 3 | hot water, 237 mL cup | 82.28 | 20, default | held out |
| LANGER2018_Abb2-04 | Langer et al., fold 3 | hot water, 237 mL cup | 80.63 | 20, default | held out |
| LANGER2018_Abb2-05 | Langer et al., fold 3 | hot water, 237 mL cup | 80.86 | 20, default | held out |
| LANGER2018_Abb2-06 | Langer et al., fold 3 | hot water, 237 mL cup | 81.90 | 20, default | held out |
| LANGER2018_Abb2-07 | Langer et al., fold 3 | hot water, 237 mL cup | 81.34 | 20, default | scored in the exponent analysis only |
| LANGER2018_Abb2-08 | Langer et al., fold 3 | hot water, 237 mL cup | 81.12 | 20, default | scored in the exponent analysis only |
| LANGER2018_Abb2-09 | Langer et al., fold 3 | hot water, 237 mL cup | 81.41 | 20, default | scored in the exponent analysis only |
| LANGER2018_Abb2-10 | Langer et al., fold 3 | hot water, 237 mL cup | 79.03 | 20, default | scored in the exponent analysis only |

The Langer curves were read from a paper whose served temperature is 88 C. The first recorded values are 79.0 to 82.3 C, so the 88 C figure is not the starting temperature. The held-out testing uses the recorded values.

## Analysis 2: held-out testing of the constant-rate and nonlinear laws

### Method

The testing fitted the two laws to the first 30 minutes of the porcelain pot curve, froze the parameters, and tested them on the held-out curves by 30-minute root-mean-square error (RMS, K). The two laws are the constant-rate Newton law and the one-term nonlinear convection law dT/dt = −kc (T − T_room)^x, with kc and x fitted. The two ambient settings were handled as follows. Ambient A uses the recorded room temperature where a source reports one (Manitoba, 21.67 C) and 20 C where none is reported. Ambient B fits room temperature as a shared parameter bounded to 5 K around the 20 C reference. A leave-one-source-out (LOSO) protocol fits both laws on the other two sources in turn. Intervals are bootstraps with 1000 replicates and random start 0: between-curve where a set has two or more curves, and within-curve block bootstrap (block length 3) for single curves, which the analysis names as not comparable to the between-curve intervals. The the nonlinear law closed form agrees with an ODE program (LSODA) to 1.6e-6 K. Deviations in this analysis are model minus observed, so a positive value means the model is warmer than the liquid. The opposite convention is used in the exponent analysis below.

### In-sample fits

Table 6. In-sample fits to the porcelain pot curve, first 30 minutes (7 points). Source: fitted-parameter and block outputs of the testing analysis [ARTIFACT:art_YY3zHfdcKluB] (`results/fold_summary.json`).

| Law | Ambient | Scale | x | Room T (C) | RMS (K) | Within-curve 95% interval (K) |
|---|---|---|---|---|---|---|
| C0 | A, fixed 20 C | k = 0.02650 per min | 1 | 20 | 1.261 | 0.939 to 1.374 |
| C1 | A, fixed 20 C | kc = 2.819e-4 | 2.182 | 20 | 0.328 | 0.053 to 0.457 |
| C0 | B, fitted | k = 0.02978 per min | 1 | 25.0 (at bound) | 1.124 | 0.823 to 1.232 |
| C1 | B, fitted | kc = 8.94e-4 | 1.940 | 25.0 (at bound) | 0.323 | 0.057 to 0.450 |

The paired difference nonlinear minus constant-rate is -0.933 K under ambient A, with interval -1.255 to -0.616 K, and -0.801 K under ambient B. Under both settings the nonlinear law fits this one window better, and the in-sample comparison is not a test of scope. Under ambient B the room temperature sits at the 25 C edge of its bound, so the B fits are constrained by the bound.

### Held-out values

Figure 3 and Table 7 give the per-curve results for the seven held-out curves. Under ambient A, the constant-rate law is off by 3.45 K RMS over 30 minutes on the Manitoba coffee curve, and the nonlinear law by 2.66 K.

[FIGURE:fig3]

Figure 3. Held-out 30-minute RMS for the constant-rate law and the nonlinear law (x = 2.182 fixed from the porcelain pot fit), under ambient A. Bars are per-curve RMS over 0 to 30 min for the seven held-out curves, with no interval drawn. Parameters were fixed from the porcelain pot fit. Source: [ARTIFACT:art_YY3zHfdcKluB] (`results/fold_summary.json`).

Table 7. Per-curve 30-minute RMS (K) for the held-out curves, under ambient A and ambient B. Source: per-curve blocks of the testing analysis (`results/fold_summary.json`).

| Curve | C0, A | C1, A | C0, B | C1, B |
|---|---|---|---|---|
| Manitoba coffee | 3.454 | 2.659 | 2.885 | 1.883 |
| Langer 01 | 6.864 | 6.572 | 6.832 | 6.569 |
| Langer 02 | 8.951 | 8.768 | 8.938 | 8.765 |
| Langer 03 | 11.927 | 12.092 | 11.963 | 12.085 |
| Langer 04 | 8.896 | 8.685 | 8.879 | 8.682 |
| Langer 05 | 8.309 | 8.182 | 8.302 | 8.178 |
| Langer 06 | 9.944 | 10.034 | 9.969 | 10.028 |

The mean across the seven held-out curves is summarized in Table 8. The mean difference is small against the spread across curves. On the Manitoba curve the constant-rate law is warm by 2 to 5 K at every point in the window, so the error is one-signed there. On the Langer curves the sign is reversed: the fitted law is colder than the observed liquid in the first ten minutes, so the porcelain pot constant rate predicts too much heat loss for those cups.

Table 8. Summary of the held-out transfer and the leave-one-source-out fits. Intervals are 95% bootstrap over curves, as reported by the analysis. Paired difference is nonlinear minus constant-rate. Source: [ARTIFACT:art_YY3zHfdcKluB] (`results/fold_summary.json`).

| Protocol | Held-out set | C0 mean RMS (K) | C1 mean RMS (K) | Paired C1 minus C0 (K) | C1 lower on |
|---|---|---|---|---|---|
| Transfer, ambient A | 7 curves | 8.335 (6.539 to 9.928) | 8.142 (5.932 to 9.964) | -0.193 | 5 of 7 |
| Transfer, ambient B | 7 curves | 8.252 (6.292 to 9.935) | 8.027 (5.552 to 9.959) | -0.225 | 5 of 7 |
| Langer only, ambient A | 6 curves | 9.149 | 9.056 | -0.093 | not reported |
| LOSO, held out Sedlacek, ambient A | 1 curve | 7.207 | 7.195 | -0.012 | 1 of 1 |
| LOSO, held out Manitoba, ambient A | 1 curve | 10.770 | 11.036 | +0.265 | 0 of 1 |
| LOSO, held out Langer, ambient A | 6 curves | 11.231 | 10.728 | -0.503 | 6 of 6 |
| LOSO, held out Sedlacek, ambient B | 1 curve | 7.201 | 7.190 | -0.012 | 1 of 1 |
| LOSO, held out Manitoba, ambient B | 1 curve | 10.557 | 10.929 | +0.372 | 0 of 1 |
| LOSO, held out Langer, ambient B | 6 curves | 10.806 | 10.146 | -0.660 | 6 of 6 |

The Langer-only row is computed from the six per-curve values in Table 7. The LOSO fits fit the laws on the two other sources. The Langer LOSO fit gives the nonlinear law a lower error on all six curves, but its Manitoba fit reverses the sign. Taken together, the nonlinear law's advantage is not stable across the choice of held-out source.

### Criteria planned in advance

The testing analysis planned in advance four criteria. Table 9 gives their outcomes as the analysis recorded them.

Table 9. Criteria planned in advance and outcomes for the held-out testing. Source: criteria block of [ARTIFACT:art_YY3zHfdcKluB] (`results/fold_summary.json`).

| Criterion | Result | Outcome |
|---|---|---|
| C1 held-out 30-min RMS under 0.5 K | Manitoba 2.66 K (ambient A), 1.88 K (B); Langer mean 9.06 K (A), 9.05 K (B) | fail |
| C1 beats C0 on the held-out mean | -0.19 K (A), -0.23 K (B); C1 lower on 5 of 7 curves | pass; a sign-flip placebo gives p = 0.0625 for the mean and 0.23 for the count |
| C1 beats C0 in at least 2 of 3 source folds | lower on the Sedlacek and Langer folds, higher on the Manitoba fold | pass |
| C0 early residual positive on held-out curves | model minus observed over 0 to 10 min averages -3.20 K (A) and -3.38 K (B); positive on 1 of 7 curves | fail |

A fifth check in the analysis asked whether the constant-rate law is already adequate on the held-out curves. Its mean RMS is 8.33 K, so it is not. The criteria show that the nonlinear law's mean advantage on held-out curves is small, not significant under the control, and that no held-out accuracy target is met. The 0.5 K target is a long way off on this set.

The analysis's results are also checked. An independent calculation from the raw data, with an ODE program rather than the closed form, matches every stored RMS and signed deviation within 1.2e-6 K. The the nonlinear law closed form matches the program to 1.6e-6 K.

### Limits

Eight curves come from three sources. The six Langer curves come from one lab and one protocol, so they are not six independent sessions. No held-out curve records humidity or a covering layer, so the evaporative term cannot be tested here. Several fits end on parameter bounds, and those fits are noted in the outputs. The room temperature of the Sedlacek and Langer curves was not reported, so the 20 C standard is an assumption. Results for these curves depend on it. Moving from ambient A to ambient B changes the held-out means by 0.08 K for the constant-rate law and 0.12 K for the nonlinear law, but it moves the Manitoba curve by 0.57 K (the constant-rate law) and 0.78 K (the nonlinear law). The cause of the Manitoba shift is not isolated in the outputs.

The testing analysis also ran a sensitivity extension that values all ten read Langer curves with the frozen planned parameters. The main numbers do not change. The extension's results are in `results/sensitivity_langer10.json` in the analysis.

## Analysis 3: stability of the exponent x

### Question and method

Stage 1 fitted x = 1.94 on the porcelain pot window and reported the one-term law as the leading model. The exponent analysis asks whether x is a stable quantity or an analysis of a free power fitted to seven points [ARTIFACT:art_pamuF8tunauJ]. It ran fixed-x fits at x = 1.00, 1.25, 1.34 and 1.50; a profile of the in-window fit over a 0.01 step from 1.00 to 3.00 (the plan step to 2.00 was extended because its minimum sat at 2.00); free-x fits in the window and over the full record; a 200-replicate moving-block bootstrap; and held-out testing on Manitoba and the ten Langer curves (twelve curves in all). In this analysis the deviation is observed minus model. A negative value means the model is warmer than the liquid.

Table 10 gives the fixed-x and profile values. Figure 2 plots the in-window RMS against x.

Table 10. In-window fit of the one-term law on the porcelain pot curve (7 points, T_room = 20 C), as a function of the fixed exponent x. The scale a is fitted at each x. Source: profile block of [ARTIFACT:art_pamuF8tunauJ] (`results/exponent_profile.json`).

| x | a (per min) | 30-min window RMS (K) |
|---|---|---|
| 1.00 | 0.026495 | 1.2608 |
| 1.25 | 0.010157 | 0.9969 |
| 1.34 | 0.0071906 | 0.9059 |
| 1.50 | 0.0038900 | 0.7509 |
| 1.75 | 0.001488 | 0.5325 |
| 2.00 | 0.000569 | 0.3707 |
| 2.18 | 0.000284 | 0.3275 |
| 2.25 | 0.000217 | 0.3335 |
| 2.50 | 0.0000830 | 0.4381 |
| 2.75 | 0.0000320 | 0.6063 |
| 3.00 | 0.0000120 | 0.7920 |

[FIGURE:fig2]

Figure 2. In-window RMS of the one-term law against the fixed convective exponent x on the porcelain pot curve, first 30 minutes, with the scale a fitted at each x. The profile minimum is at x = 2.18, with a 95% interval, set by an increment in χ² (Δχ²) of 3.84, from 1.95 to 2.42 at σ = 0.3 C. The line is drawn through the ten profile points in Table 10. Source: [ARTIFACT:art_pamuF8tunauJ] (`results/exponent_profile.json`).

The profile minimum is at x = 2.18. Its 95% interval from the Δχ² threshold runs from 1.95 to 2.42. The moving-block bootstrap gives a median of 2.21 and a 95% interval of 2.03 to 2.36 over 200 replicates. The RMS curve is flat between about 2.0 and 2.4, and it rises on both sides. At x = 1.00 the same window gives 1.26 K, which is the constant-rate law. The sample is seven points, so these intervals are narrow only in the sense that the analysis computed them from seven points.

### The exponent is not stable across fits

Table 11 lists every fit of the one-term law that this stage or the first produced. It gives the exponent, the scale and the room temperature, so the reader can see how far x moves when a setting changes.

Table 11. The one-term law's fitted exponent across fits. Rows marked "stage 1" are the stage 1 values, which this stage could not match as stated. Sources: [ARTIFACT:art_YY3zHfdcKluB] (`results/fold_summary.json`), [ARTIFACT:art_pamuF8tunauJ] (`results/exponent_profile.json` and `results/benchmark_checks.json`), and the stage 1 analysis [ARTIFACT:art_UaVOg91elcVt].

| Fit | Data | Ambient setting | x | Scale | Room T (C) | RMS (K) |
|---|---|---|---|---|---|---|
| C0, window | 7 points | fixed 20 C | 1 | a = 0.02650 per min | 20 | 1.261 |
| C0, window | 7 points | fitted, bounded 15 to 25 C | 1 | a = 0.02978 per min | 25.0 (bound) | 1.124 |
| C0, window | 7 points | free, benchmark run | 1 | not printed in output | not printed in output | 1.007 |
| C1, window | 7 points | fixed 20 C | 2.182 | kc = 2.819e-4 | 20 | 0.328 |
| C1, window | 7 points | fitted, bounded 15 to 25 C | 1.940 | kc = 8.94e-4 | 25.0 (bound) | 0.323 |
| C1, window | 7 points | freed, bounded near 40 C | 1.201 | a = 0.02458 | 40.0 (bound) | 0.307 |
| C1, full record | 29 points | not labelled in output | 1.751 | a = 1.474e-3 | not labelled in output | 0.303 |
| C1, window, iteration 1 | 7 points | fixed 20 C | 1.94 | not in summary | 20 | 0.36, not reproduced |
| C1, full record, iteration 1 | 29 points | fixed 20 C | 1.68 | not in summary | 20 | RSS/NDF 0.072, not recomputed |
| C1, full record, iteration 1 | 29 points | fitted | 1.82 | not in summary | 17.9 | RSS/NDF 0.066, not recomputed |
| C1, window, iteration 1 | 7 points | freed | 1.50 | not in summary | 30 (bound) | 0.34, not recomputed |

The fitted exponent runs from 1.20 to 2.18 across the in-window rows, and from 1.75 to 1.82 across the full-record rows. Its value depends on the room temperature choice, the window, and whether the ambient is free. The stage 1 value of 1.94 is matched in this table as an ambient-B fit at a room temperature bound, which is a different setting from the fixed 20 C window it was reported under. The benchmark range check on the exponent (1.8 to 2.1) and on the constant-rate RMS (0.95 to 1.20 K) was not met under the measured setting, and the benchmark test is recorded as failed. The test-origin and benchmark values are in the analysis's results files.

The implication is that x is a fitted curve shape, not a stable physical constant on this evidence. The one-term law describes the window well, but its exponent moves across reasonable choices. the nonlinear law is therefore a lead for the window, not a model of coffee cooling. Claiming the nonlinear law as the better model would require the exponent to hold across windows and room temperatures, and that does not yet hold.

### Held-out testing of the exponent

The held-out testing used two schemes. The strict transfer scheme applies the porcelain pot scale the same to a held-out curve, with its recorded room temperature. Only Manitoba can be tested this way, because the Langer curves report no room temperature. The fit scheme fits the scale on the first ten minutes of each held-out curve and values minutes 10 to 30. The fit scheme fits two quantities to about eleven points, and for the Langer curves the room temperature is fitted as well.

Table 12. Held-out testing under strict transfer (Manitoba only) and fit (eleven curves, Manitoba plus ten Langer curves), by fixed exponent. Source: summary block of [ARTIFACT:art_pamuF8tunauJ] (`results/heldout_scores.json`).

| Scheme | x | Curves scored | Mean RMS (K) | C1 lower than C0 on |
|---|---|---|---|---|
| S1, Manitoba | 1.00 (C0) | 1 | 3.664 | not applicable |
| S1, Manitoba | 1.25 | 1 | 3.391 | 1 of 1 |
| S1, Manitoba | 1.50 | 1 | 3.168 | 1 of 1 |
| S1, Manitoba | 2.18 | 1 | 2.821 | 1 of 1 |
| S2, eleven curves | 1.00 (C0) | 11 | 0.641 | not applicable |
| S2, eleven curves | 1.25 | 11 | 0.642 | 3 of 11 |
| S2, eleven curves | 1.50 | 11 | 0.670 | 4 of 11 |
| S2, eleven curves | 2.18 | 11 | 0.603 | 2 of 11 |

The fit mean at x = 2.18 is 0.60 K against 0.64 K for the constant-rate law, and it is a small difference. Table 13 breaks the fit result down by curve. It shows that the mean is carried by the Manitoba curve, where the fitted constant-rate law values 5.30 K and the nonlinear law at x = 2.18 values 0.77 K. On the ten Langer curves alone, the constant-rate fit has a mean of 0.18 K and the nonlinear law at x = 2.18 has a mean of 0.59 K. The nonlinear law is better on two of the eleven curves at x = 2.18, and on nine of the ten Langer curves it is worse.

Table 13. Fit values at x = 2.18 by curve, with the constant-rate fit beside it. The room temperature column is the value fitted for the nonlinear law. Four Langer values sit at the -10 C lower bound of the search, and two more lie outside a plausible range for a room. On Langer curve 01 the constant-rate law fitted a room temperature of 40 C, its upper bound. Source: [ARTIFACT:art_pamuF8tunauJ] (`results/heldout_scores.json`).

| Curve | C0 RMS (K) | C1 RMS at x = 2.18 (K) | C1 minus C0 (K) | Fitted room T for C1 (C) |
|---|---|---|---|---|
| Manitoba coffee | 5.301 | 0.767 | -4.534 | 21.67 (recorded) |
| Langer 01 | 0.294 | 0.595 | +0.301 | 21.0 |
| Langer 02 | 0.146 | 0.228 | +0.081 | -10.0 (bound) |
| Langer 03 | 0.258 | 0.315 | +0.056 | -10.0 (bound) |
| Langer 04 | 0.223 | 1.092 | +0.869 | 30.8 |
| Langer 05 | 0.192 | 0.031 | -0.160 | -2.9 |
| Langer 06 | 0.086 | 1.421 | +1.335 | 34.0 |
| Langer 07 | 0.063 | 0.723 | +0.659 | 24.0 |
| Langer 08 | 0.076 | 0.253 | +0.177 | -10.0 (bound) |
| Langer 09 | 0.226 | 0.855 | +0.629 | 17.9 |
| Langer 10 | 0.191 | 0.350 | +0.160 | -10.0 (bound) |
| Mean, eleven curves | 0.641 | 0.603 | -0.038 | not applicable |
| Mean, ten Langer curves | 0.176 | 0.586 | +0.411 | not applicable |

The fit scheme is a calibrated prediction over minutes 10 to 30. It is not the accuracy that the 0.5 K target, planned in advance, describes, and its advantage for the nonlinear law rests on one coffee curve. The Langer room temperatures are not reported, and the fitted values hit the search bounds or fall outside the range of a room, so those rows carry little information. The Manitoba strict transfer result is the only strict transfer to coffee with a recorded room temperature in this stage: 2.82 K at x = 2.18 against 3.66 K for the constant-rate law.

### Benchmark, control and validation checks

Table 14 gives the checks the exponent analysis ran. The simulated recovery shows that the fitting code recovers a known exponent. The shuffled-time control shows that the window fit is not produced by the fitting procedure on noise.

Table 14. Checks from [ARTIFACT:art_pamuF8tunauJ] (`results/benchmark_checks.json`, `results/audit_headline.json`).

| Check | Result | Note |
|---|---|---|
| Synthetic recovery, x = 1.25 | median 1.248; 94% of replicates within 0.1 of truth | 50 replicates |
| Synthetic recovery, x = 1.94 | median 1.944; 98% within 0.1 | 50 replicates |
| Closed form against ODE solver | maximum absolute difference 2.9e-10 K (x = 1.25), 1.5e-10 K (x = 1.94) | solver check |
| Shuffled-time placebo, C0 RMS | 13.50 K | the real window fit is 1.26 K for C0 |
| Moving-block bootstrap of x | median 2.209; 95% interval 2.031 to 2.359 | 200 replicates, block length 3 |
| Profile interval, delta chi-squared 3.84 | 1.95 to 2.42 | sigma = 0.3 C |
| Independent audit | C0 RMS agrees within 0.02 K; free-x RMS within 0.05 K | audit headline checks, both true |
| Prior-target benchmark, C0 | 1.261 K against target 1.07 K (tolerance 0.95 to 1.20) | not within tolerance |
| Prior-target benchmark, C1 free x | 2.182 against 1.94 (tolerance 1.80 to 2.10) | not within tolerance |

The prior-target benchmark fails for both laws. The difference is not explained by these outputs. The reading shift noted in Analysis 1 is the first model, and the benchmark has not been repeat against it.

### Dead ends and the evidence against them

* **The 0.54 K free-ambient constant-rate RMS (stage 1).** No output read in this stage matches it. The free-ambient constant-rate fits in stage 2 give 1.01 K (benchmark run) and 1.12 K with room temperature at the 25 C bound. The 0.54 K value is dropped until its source is found.
* **Strict transfer of the porcelain pot parameters to the Langer hot-water cups.** Applying the porcelain pot scale and exponent to Langer curves with a 20 C room gives about 9 K RMS for both laws (Table 8). The hot-water cups are a different liquid in a different cup, and the porcelain pot rate does not describe them. The dead end is the transfer of one fitted rate across liquids, not the nonlinear law itself.
* **Fit-based advantage of the nonlinear law.** The fit advantage of the nonlinear law over the constant-rate law is carried by the Manitoba curve. On the ten Langer curves the constant-rate fit is better than the nonlinear law at x = 2.18 on nine of ten. The claim that the nonlinear law improves a 10-minute-calibrated prediction is not supported beyond the Manitoba curve.
* **Fixed exponent 1.94 as a stable value.** Table 11 shows that the one-term law's x runs from 1.20 to 2.18 across the reasonable choices. The fixed value is dropped as a reported constant.

### What this stage established, and what it did not

It established four things. The constant-rate law is off the Manitoba coffee curve by about 3.5 K RMS over 30 minutes under strict transfer, with its error one-signed over the window. The nonlinear law at x = 2.18 reduces that to 2.7 K under ambient A and 1.9 K under ambient B, and the reduction is the largest effect in the held-out set. The exponent is not stable. The window's shape is well fitted by the one-term law, but no single exponent holds across fits.

It did not establish that Newton's law predicts coffee to 0.5 K over 30 minutes. It did not test humidity, the covering layer or pot geometry, because no series with those variables exists in the sources read. It did not resolve the difference between the stage 1 and stage 2 in-sample constant-rate RMS, which the reading shift may explain.

### Contribution against the nearest published work

This stage does not add a new cooling law. The nearest published neighbours are Vollmer (2009) and the source paper itself. Vollmer reports that the simple exponential law holds mainly below a temperature-difference threshold that depends on conditions, with radiation producing the deviation at larger differences, and that study uses solid objects up to 300 K [2]. The source paper fits a free exponent to a coffee curve (χ²/NDF 2.4 with x = 1.34, against 32.1 for the constant-rate law) and reports a fitted evaporation power on the same curve [1].

What this stage adds is limited. It applies the free-exponent form to published curves that the source did not fit, under a leave-one-source-out protocol, with bootstrap intervals and a failed agreement test recorded. The added result is a negative one on scope: the held-out error of the nonlinear law is large, and its advantage depends on the held-out set. The stage does not claim a new contribution for the law, and it does not claim a general accuracy figure for coffee.

### Agreement-test state

The source values 32.1 and 2.4 are on page 2 in the legend of Fig. 3, and 1.0 and 81.3 are on page 3 in the content, as recorded in stage 1. The source's Fig. 3 legend also gives "Fitted k = 0.17 J.s-1.K-x, x = 1, 34". The hypothesis update gives k = 0.54 for model 1 in its motivation. That k value does not appear in the content search, so the two differ. This is open and the next stage should check the source's figure directly.

## Stage 2 summary of the corrections to stage 1

The corrections placed in the stage 1 content cover the later sign change, the 1.07 K and 0.54 K values, the ambient-free fit of the whole record, the drawn-curve pattern, and the origin of the test values. Each is marked in place. The stage 1 numbers in Tables 1 to 4 are the same, and the in-sample values they report are now shown to depend on the room temperature setting.

## What the next stage takes from this one

The open question is whether the held-out error of the one-term law is a property of coffee or of the one porcelain pot fit. The next stage should:

1. Re-run the in-sample the constant-rate law and the nonlinear law fits on a single agreed reading, and test whether the time shift between the two readings accounts for the 1.07 K against 1.26 K difference.
2. Find the source of the 0.54 K free-ambient value, or drop it from the hypothesis.
3. Test whether the Manitoba error is a rate difference between cups or a room-temperature effect, using the recorded room temperature for that curve only.
4. Check the source's Fig. 1 to Fig. 3 legends directly, including the k value, so that the test statistics are linked to the figure they came from.
5. Keep humidity, covering layer and geometry as not tested. No source read so far provides those series.

The hypothesis's x range (1.50 to 1.94) should be replaced by the 1.20 to 2.18 range this stage reports.

# What we have found so far

The question is how accurately Newton's law predicts a coffee cup over 30 minutes, compared with published measurements. The question is answered in part. Its in-sample part and its one held-out coffee curve are answered. Its general part is not.

In sample, on the one porcelain pot coffee curve, the constant-rate law has a 30-minute RMS of 1.26 K with room temperature fixed at 20 C. The figure depends on that choice: it is 1.12 K with room temperature fitted at a bound, and 1.01 K in a free-ambient benchmark. The 1.07 K of stage 1 and the 0.54 K free-ambient value could not be matched. The early deviation has the sign the hypothesis predicted, and the later sign rests on one point. The one-term nonlinear law fits the same window to 0.33 K, with its exponent at 2.18 and a profile interval of 1.95 to 2.42. Its exponent is not stable across fits, which range from 1.20 to 2.18. The evaporative term is not determined from this window.

Out of sample, the porcelain pot parameters transfer poorly. On the Manitoba coffee curve, the only held-out coffee curve, the constant-rate law is off by 3.45 K RMS over 30 minutes under ambient A, and the nonlinear law by 2.66 K. On six Langer hot-water curves with a 20 C standard ambient, both laws are off by about 9 K. Over the seven held-out curves, the nonlinear law's mean advantage is 0.19 K, with a paired permutation test p of 0.0625. A leave-one-source-out fit reverses the sign on Manitoba. The 0.5 K accuracy target is not met under any strict transfer. A 10-minute fit gives a 0.6 K mean, but that result is carried by Manitoba, and on the ten Langer curves the constant-rate fit does better than the nonlinear law at x = 2.18.

The evidence does not test humidity, the covering layer or pot geometry. No source read so far records a humidity, evaporation or cup-mass series with a cooling curve. The agreement test for the source's χ²/NDF values is conditional, since the values appear in the source content but their role is not confirmed. The source's own drawn curve predicts too high at both early and later points, so the source's model does not explain the constant-rate discrepancy, and the 6.9 times difference over the reading error is open. The reading itself is not settled: two readings of the same figure differ in their window times by up to 0.4 min, which is a model cause of the 1.07 K to 1.26 K difference.

The claim that survives this stage is narrow. On published coffee data, a constant-rate law with the porcelain pot rate is off by 2.7 to 3.5 K RMS over the first half hour of the Manitoba cup, and a single held-out coffee curve cannot establish how wide that error is across cups. Any accuracy figure for coffee in general needs more held-out coffee curves with recorded room temperature.

# Bibliography

[1] Sedlacek, M. and Dolejsi, V. "A physical description of coffee cooling in a pot." Source PDF at https://ipnp-web.troja.mff.cuni.cz/~dolejsi/outreach/sedlacek_ajp.pdf (fetched and digitized by the experiments). NOT IN references.bib. Iteration 2 retried the Semantic Scholar lookup by title twice; the first attempt was rate-limited and the second returned no match, so no BibTeX entry exists and none was written. The journal is not shown in the extracted text, so the venue is unverified and must be checked before the paper step cites it.

[2] Vollmer, M. (2009). "Newton's law of cooling revisited." European Journal of Physics 30(5):1063-1084. DOI 10.1088/0143-0807/30/5/014. In references.bib as Vollmer2009, fetched by DOI in iteration 2. Read from the abstract-level summary; the full text returned HTTP 403.

[3] Luniachek et al. (2017), evaporation model for a cooling liquid, cited from the iteration 1 literature screen [ARTIFACT:art_S9mDwyLN2pcT]. NOT IN references.bib and no DOI or URL was recorded in the screen's outputs that this iteration read. Verification status: unverified bibliographic record. It is cited here only for the statement that it uses ambient humidity as an input to a theoretical model and not as a measured variable.

[4] Langer, Winkler and Lachenmeier (2018), hot-water cup cooling curves, DLR 114, with a CC BY 4.0 Zenodo record. Source of the six Langer curves in [ARTIFACT:art_-CfKbDAPDpKm]. NOT IN references.bib. No BibTeX lookup was run for it in iteration 2, and the Zenodo record has no raw series. Verification status: the curves were digitized from the article's vector polylines, and the article's own crossing-time text disagrees with the digitized 65 C crossings, so the article's figures are cited for the curves only.
