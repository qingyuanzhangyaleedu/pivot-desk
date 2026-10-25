# Pivot Desk — grading review

Reviewed October 25, 2026 against the original `docs/assignment_brief.pdf`, the current code, report, slides and saved test evidence. This is an internal estimate, not an instructor grade. No new model calls or real applicant trial were performed for this review.

## Estimate

**79/100 for the current work; a reasonable planning range is 75–85.** This assumes the grader receives a runnable, accessible repository and accepts the documented model/account configuration. Neither submission issue is resolved yet, so this is not a predicted grade for submitting the folder exactly as it stands. The brief gives no numeric penalty for the model mismatch or missing repository link; this review does not invent one.

The work has much of the technical evidence described in Tier 2. Novelty is less secure, and there is not yet enough human-outcome evidence to claim Tier 3. The brief does not map tiers to numeric score bands.

| Rubric component | Maximum | Estimate | Evidence and main limitation |
| --- | ---: | ---: | --- |
| Novelty + real-world value | 21 | 14 | A useful MBA career-pivot workflow joins reviewed facts, source-linked analysis and application preparation. Resume review, matching, tracking and autofill are established ideas; the advantage over named alternatives is not yet demonstrated by users. |
| It works | 15 | 12 | Real job feeds and AI runs, resume upload/review, search, pipeline and form lab work. All 26 offline checks passed. Actual Workday compatibility and broader matching quality remain unverified. |
| Teaching staff can run it | 5 | 4 | Initial local clone installed and started in 9.84 seconds with warm caches; parent-folder key discovery was tested. No remote exists, and the final changed version has not had its published-clone rehearsal. This credit is provisional. |
| App look + feel | 10 | 9 | Consistent black/plum and pink design, clear navigation, evidence panel, deliberate empty states and a mobile layout check. Usability for someone new has not been observed. |
| Report motivation + what is new | 8 | 7 | Specific applicant problem and named Simplify/Teal comparisons. The claimed difference needs a direct task comparison, not just a feature description. |
| Report agent design | 10 | 8 | Two bounded PydanticAI specialists, typed outputs, two analyst tools, a diagram and a real Heartflow run. The report could show a clearer visual sequence of extraction, human review and tool activity, and explain why this model is worth its cost. |
| Report tokenomics | 8 | 7 | Real input/output counts, cache evidence, per-run/monthly/scale calculations and a measured truncation trade-off. The controlled quality/cost comparison covers one profile and one role; monthly usage assumptions are not observed behavior. |
| Report safety | 8 | 7 | Actual injection and field-mapping tests, constrained tools, quote checks, manual consent, session separation and spending limits. One completed injection test is narrow coverage; the local app does not provide hosted authentication or encrypted storage. |
| Report impact + metrics | 5 | 2 | The report honestly records 13 fields filled and functional tests. No actual applicant has completed a measured comparison or provided feedback. The rubric's missing-evidence rule caps this row at half credit without the requested real-user evidence. |
| Report design | 2 | 2 | Twelve printed letter-size pages, embedded images, readable layout and no detected overflow. |
| Slides content | 6 | 5 | Nine slides cover the requested story, diagram, screenshots, cost and safety. The impact slide reports functional outputs rather than a measured benefit for an applicant. |
| Slides design | 2 | 2 | Consistent typography/palette, embedded visuals, working arrow navigation and fullscreen offline. |
| **Total** | **100** | **79** | **Judgment-based estimate; submission risks below are separate.** |

## Three scoring issues to take seriously

**Novelty is the largest uncertainty.** The brief specifically identifies resume/cover-letter review as an overdone category and caps the idea at Tier 1 without a real twist. Adding industries or making the interface attractive does not establish that twist. The strongest candidate here is a career-pivot decision supported by exact resume facts, employer quotations and explicitly unresolved eligibility, followed by controlled application preparation. A user comparison must show why that combination is better for a concrete task. A strict grader could award fewer than 14 of the 21 idea points.

**The Workday claim is narrower than the original ambition.** The extension and shared adapter exist, and the local lab filled 13 fields after review. We have not established that an actual employer's Workday form accepts and retains the values across navigation. Export/import and extension setup also add friction. The report appropriately states this limit. Workday testing is not a named course requirement; it matters because application preparation is a central promise of this particular project.

**Impact is not established by test counts.** Twenty-six passing checks support reliability; they do not show time saved or better recruiting decisions. Ten feeds and six sectors show coverage, not relevance for a specific applicant. A high overlap score is not an eligibility or hiring probability. The strict exclusion also removes Brattle's MBA role when its description mentions previous investment-banking experience: that behavior respects the chosen filter, but illustrates why relevance needs human evaluation.

## Submission risks outside the point estimate

- The repository has no configured remote. The assignment requires a public or grader-accessible GitHub link. Finish publication, insert the verified link, then rehearse the README from the final remote clone. The explicit ten-minute setup failure rule is zero of the five setup points.
- `backend/config.py` fixes `gpt-6-astra`, and the client prioritizes `PORTKEY_API_KEY`. This follows the user's explicit decision. The brief permits only Luna on the course key and allows other models with a personal paid key. A personal direct-key setup or instructor approval would resolve the mismatch while retaining Astra. Merely disclosing the mismatch does not make it compliant. No configuration was changed during this review.
- Report and slides still label themselves submission drafts. A final human review and Canvas submission remain outstanding.

## Highest-value next work

1. **Measure one real applicant's workflow.** Use the protocol in `docs/user_trial.md`: the same job/profile tasks manually and with the app, task times, corrections, unresolved requirements noticed and actual feedback with consent. Include failures. This directly addresses the impact evidence cap and strengthens the idea, usability and slide story.
2. **Validate one permitted real employer application form.** Preview/fill supported contact, employment and education fields; inspect whether they persist after navigation. Keep agreements and submission manual. Record exactly which controls work and which do not. Do not generalize one successful tenant to all Workday sites.
3. **Make the career-pivot contribution measurable.** Compare a small, manually labeled set of suitable roles and near misses against simple keyword search or a basic resume/job chat. Record missed qualifications and misleading high scores. Improve demonstrated weaknesses before adding more features.
4. **Make the existing evidence easier to grade.** Put extraction → review → analyst tool calls → final result in one readable visual sequence. Add measured user results to report/slides once they exist. An optional short recorded demonstration provides backup evidence.
5. **Close the account and repository requirements.** Confirm an allowed account/model arrangement, publish when authorized, scan the final commits for secrets, and test that exact remote version with the parent-folder `.env` arrangement.

Successful evidence on these items could support a high-80s or low-90s assessment, but that is conditional. Additional pages, sectors or agents by themselves do not justify that score.

## Evidence inspected

- `docs/assignment_brief.pdf`: original rubric, tier language, evidence caps and submission rules.
- `report.html`, `slides.html`, `scripts/build_deliverables.py`: claims and actual presentation content.
- `output/evidence/artifact_validation.json`: 12 printed pages, 9 slides, offline images, no overflow, arrow/fullscreen checks.
- `output/evidence/sector_tests.txt`, `sector_browser.json`, `browser_checks.json`: 26 offline checks and recorded UI behavior.
- `output/evidence/live_runs.json`, `cost_comparison.json`, `injection_test.json`: real structured outputs, token use and the completed adversarial test; the earlier failed attempt remains disclosed.
- `output/evidence/clean_setup.json`: the initial local-clone rehearsal and its warm-cache/no-live-AI limitations.
- `backend/config.py`, `backend/agent.py`, `extension/manifest.json`, `extension/popup.js`: actual model wiring, controls and application-helper scope.
- Current Git remote inspection: no remote configured.

Historical measurements were not rewritten. No grading prediction is presented as an achieved course result.

## Subsequent improvements
After this estimate, the project added visible application checks, a 12-posting development benchmark, title-only exclusions, stronger form mapping, 35 offline tests, a public Workday account-boundary check, a captioned demo and a timed human-trial worksheet. The report now has 14 pages. These strengthen functional evidence but do not substitute for real applicant outcomes or establish authenticated Workday compatibility. No automatic revised grade is claimed.
