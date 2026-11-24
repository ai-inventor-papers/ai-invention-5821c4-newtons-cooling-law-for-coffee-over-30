# gen_paper_draft — report_results

> Phase: `gen_paper_repo` · `gen_paper_draft`
> Run: `run_eF8rkCcKVBKN` — Newton's Cooling Law Fitted to One Coffee Curve Does Not Transfer Between Cups
>
> Full, verbatim record of every prompt the AI Inventor pipeline gave this agent — system-user, human-user and skill-input — in the order they landed. Nothing truncated.

## Task: `gen_paper_draft` (terminal_claude_agent)

### [1] SYSTEM-USER prompt · 2026-11-23 16:46:21 UTC

```
<research_methodology>
Write like an experienced academic. Reviewers judge both the science and the writing.

- Claims must be proportional to evidence. Choose verbs carefully — "demonstrate," "observe," and "hypothesize" mean different things.
- Every result needs: what was measured, on what data, the numbers, and what they mean.
- Methodology must be specific enough to reproduce. Section placement follows <paper_structure> below.
- State limitations honestly. Avoid both overclaiming and excess... [truncated, 97565 chars total]
```

### [2] SKILL-INPUT — aii-paper-writing · 2026-11-23 16:46:25 UTC

The agent loaded the **aii-paper-writing** skill.

```
Tool: Skill
aii-paper-writing
```

### [3] SKILL-INPUT — aii-semscholar-bib · 2026-11-23 16:46:25 UTC

The agent loaded the **aii-semscholar-bib** skill.

```
Tool: Skill
aii-semscholar-bib
```

### [4] SYSTEM-USER prompt · 2026-11-23 16:51:10 UTC

```
The headline does not hold up against the claim ledger and the run record:
- `Held-out curves (Manitoba coffee and six Langer hot-water cups), ambient A` does not appear in the run record. Name each set exactly as the report and iteration records name it, so its every use can be found.

Correct `headline_candidates` first, then the title, abstract, summary and Results so they lead with the ledger's headline, its number, interval, grade and scope. Grade it exactly as the run record grades its test, and state in the abstract the scope the record gives it. Then resubmit every field.
```

### [5] SYSTEM-USER prompt · 2026-11-23 16:52:14 UTC

```
DOMAIN VOCABULARY, round 1 of 2: the check below ran on your draft with the aii-domain-vocabulary skill's `check` (`domain_vocabulary.json` in your workspace). Fix every listed word as it says, check again, then resubmit.

53 word(s) and 0 phrase(s) are not in the domain vocabulary built from 13 papers of this field (domain_vocabulary.json).
- china (x4): "We fitted Newton's law and a one-term power-law extension to the first 30 minutes of a measured coffee curve in a china pot, froze the cons…"
- scored (x12): "We fitted Newton's law and a one-term power-law extension to the first 30 minutes of a measured coffee curve in a china pot, froze the cons…"
- headline (x7): "The headline is a paired comparison."
- pre (x6): "This is one pre-registered criterion, recorded as passed on its sign threshold, but a sign-flip placebo gives p = 0.06, the advantage rever…"
- flip (x4): "This is one pre-registered criterion, recorded as passed on its sign threshold, but a sign-flip placebo gives p = 0.06, the advantage rever…"
- placebo (x6): "This is one pre-registered criterion, recorded as passed on its sign threshold, but a sign-flip placebo gives p = 0.06, the advantage rever…"
- gap (x2): "This is one pre-registered criterion, recorded as passed on its sign threshold, but a sign-flip placebo gives p = 0.06, the advantage rever…"
- refitted (x6): "When the constant was refitted to the first 10 minutes of each curve, the mean error was 0.64 K over eleven curves, but the one coffee cup…"
- death (x1): "It is the standard model for how a hot drink cools, and it is used in food-safety timing and in time-of-death estimates."
- gaps (x1): "Two gaps follow."
- rarer (x1): "Published cooling curves for hot drinks are few, and a test of a law on curves it was not fitted to is rarer still."
- alongside (x3): "Open cups also lose mass and heat by evaporation, which depends on ambient humidity, but the published curves seldom record humidity or cup…"
- score (x5): "We fit Newton's law and a one-term power-law extension to the first 30 minutes of one measured coffee curve, freeze the fitted constants, a…"
- misses (x2): "The frozen test failed; it misses the target by about an order of magnitude . - **Exponent.** The in-window exponent is 2.18 (profile 95% i…"
- exploratory (x3): "It is a single exploratory estimate, and it does not carry across cups without refitting . - **Refit on early data.** Refitting the constan…"
- refitting (x2): "It is a single exploratory estimate, and it does not carry across cups without refitting . - **Refit on early data.** Refitting the constan…"
- refit (x11): "It is a single exploratory estimate, and it does not carry across cups without refitting . - **Refit on early data.** Refitting the constan…"
- appreciable (x1): "Above that threshold, radiation, which is not linear in temperature difference, produces appreciable deviations."
- chi (x1): "The source reports a fit in which an evaporation term lowers the reduced chi-squared substantially."
- venue (x2): "We could not verify the source's venue, and its reported fit-quality values could not be reproduced from its own drawn curves (Section 3.1)."
- input (x2): "One evaporation-model study, Luniachek et al. (2017), read from its abstract-level summary, uses ambient humidity as an input to a theoreti…"
- readable (x1): "We found no readable source that records humidity or cup mass with a cooling curve ."
- digitized (x8): "**Published hot-water cup curves.** Langer, Winkler and Lachenmeier (2018) published cooling curves for single-use 237 mL cups of hot water…"
- markers (x1): "We read it from the vector markers of the source figure, with axis calibration residuals of 0.06 min in time and 0.21 °C in temperature."
- flag (x1): "The source reports no ambient temperature, so we use 20 °C and flag it."
- workshop (x1): "The first held-out curve is a coffee cup on a workshop table, from the University of Manitoba."
- polylines (x1): "The other six held-out curves are the Langer et al. hot-water cups, digitized from vector polylines."
- dispensed (x1): "Their first recorded temperatures are 80.2 to 82.3 °C, not the 88 °C dispensed temperature, and the source reports no ambient temperature."
- disagree (x2): "The source's 65 °C crossing times, as digitized, disagree with its own text (18 to 32 min against 11 to 22 min)."
- text (x2): "The source's 65 °C crossing times, as digitized, disagree with its own text (18 to 32 min against 11 to 22 min)."
- disagreement (x2): "We record this disagreement and use no crossing time in any fit or score."
- bibliographic (x2): "The source for the fitting curve could not be checked against a bibliographic record, and its drawn curves reproduce its stated fit statist…"
- solver (x1): "The closed-form solution was cross-checked against an ODE solver (LSODA) to within 1.6 × 10⁻⁶ K on every curve."
- scoring (x3): "3.3 fitting and scoring protocol."
- refits (x3): "A leave-one-source-out protocol refits both laws on the other two sources in turn."
- seed (x1): "Intervals are bootstrap intervals from 1000 resamples with seed 0."
- flips (x1): "The paired difference between the two laws is tested with a sign-flip placebo, which randomly flips the sign of each curve's difference and…"
- judged (x1): "Criterion (i) is the accuracy target, and the 8.3 K headline is judged against it."
- statistically (x1): "The sign-flip placebo gives p = 0.0625 for the mean difference and p = 0.23 for the count, so the advantage is not statistically establishe…"
- verdict (x1): "The accuracy target fails, and this is the frozen test's verdict."
- grid (x2): "A first grid that ended at x = 2.00 had its minimum at that edge, so we extended the grid to 3.00 before reporting."
- unchanged (x1): "Under strict transfer, where the exponent and rate are carried unchanged, only the Manitoba curve can be scored, because the Langer cups re…"
- excludes (x1): "The 3.66 K differs from the 3.45 K in Table 1 because this analysis excludes the t = 0 point."
- evaluation (x1): "For those who build and test cooling models, the evaluation implication is that a held-out cup set with a frozen constant is a strict test…"
- miss (x1): "A model that fits its own curve to 0.3 K can still miss a second cup by 8 K."
- evaluations (x1): "Evaluations should report transfer error across cups alongside in-sample error, and should record the ambient temperature and humidity that…"
- fat (x1): "Only one held-out curve is coffee. - **Missing variables.** No source reports relative humidity, and no source reports a covering layer, so…"
- untested (x1): "Only one held-out curve is coffee. - **Missing variables.** No source reports relative humidity, and no source reports a covering layer, so…"
- flagged (x2): "Four of the ten Langer refits in Section 4.4 reach the −10 °C lower bound of the ambient search, and two more fitted ambient temperatures a…"
- credibility (x1): "These fits are flagged in the outputs and reduce the credibility of the refit errors for those cups. - **Reproduction of published values.*…"
- digitization (x3): "These fits are flagged in the outputs and reduce the credibility of the refit errors for those cups. - **Reproduction of published values.*…"
- unresolved (x1): "The cause is unresolved, and the 1.26 K value is used throughout."
- digitizing (x1): "Errors from digitizing are small compared with the 8 K headline but not compared with the 0.3 K refit errors. - **Sensitivity.** Four furth…"
For each one: replace it with a word the field's papers use for the same thing (`lookup` tests candidates against the corpus and shows a sentence for each). When no corpus word fits, find a paper of this field that uses the word, save its text and run `add-word` with it; when many ordinary words are missing, save one or two more full papers of the field into the corpus and rebuild instead. Never substitute wording of your own that is not on the list. A term this paper coins is defined once at first use ("we call ...").
```

### [6] SKILL-INPUT — aii-domain-vocabulary · 2026-11-23 16:52:14 UTC

The agent loaded the **aii-domain-vocabulary** skill.

```
Tool: Skill
aii-domain-vocabulary
```
