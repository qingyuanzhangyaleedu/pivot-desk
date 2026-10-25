# Pivot Desk implementation status

The chosen user is an MBA applicant making an industry or geographic pivot. The core workflow is resume upload → human review → public-job filters → evidence-based fit review → tracked application preparation. The app deliberately separates the user’s facts from an employer’s claims and keeps submission and consent under the applicant’s control.

| Area | Status |
| --- | --- |
| React / FastAPI app | Built and browser-tested locally |
| PDF, DOCX and TXT resume parsing | Built; readable text required, no OCR |
| Structured AI extraction and fit review | Real runs recorded with fictional applicant data |
| Live source adapters | Ten public Greenhouse boards; private posting import for other sources |
| Application helper | Shared adapter tested in local lab; extension supplied; actual employer Workday compatibility remains unverified |
| Privacy / safety tests | Offline isolation, consent, input and quote checks; browser field-safety checks |
| Cost evaluation | Full vs truncated source comparison plus identical-result cache test |
| Report and slides | Verified 15-page report, nine-slide deck and captioned demo; submission gates remain |
| Actual applicant trial | Still needed; automated tests do not substitute for it |
| Course model restriction | User reports instructor permission for any model; Astra retained |
| GitHub publication and Canvas submission | Public source: https://github.com/qingyuanzhangyaleedu/pivot-desk; Canvas upload remains outstanding |

Next priorities are a real applicant trial, testing one permitted employer application page without submitting, updating measurements if the model changes, and completing the Canvas handoff. No human teammate has been assigned or contacted.

## Current evidence and document map

The app now covers **10 employer boards, 6 sectors and a 146-record bundled sample**. There are **35 passing offline checks**, plus browser checks for all four new sectors and the original workflow. The report now has 15 printed pages and the deck 9 slides. Earlier five-board, 95-record and 23-test measurements remain labeled as the initial baseline.

| File | Keep current when | Supporting evidence |
| --- | --- | --- |
| `README.md` | Setup, sources, capabilities or limitations change | Verified commands and fresh-copy checks |
| `output/harness.md` | Models, tools, routes, limits or safety controls change | Actual code and tests |
| `output/design.md`, `output/usability.md` | The interface or user workflow changes | Running-app screenshots and browser results |
| `output/agent_evaluation.md` | New model measurements or regressions are recorded | Dated outputs in `output/evidence/`; preserve older runs |
| `docs/requirements.md` | A grading deliverable is completed or its status changes | Link each completed item to real evidence |
| `AI_prompts.md` | A new project request is completed | Actual user prompt and concrete outcome |
| `scripts/build_deliverables.py` → `report.html`, `slides.html` | A report/deck claim or screenshot changes | Rebuild and run `scripts/check_deliverables.py` |

After each meaningful change, update the affected rows/documents, run the relevant checks, save the evidence, and keep completed work separate from planned work. Update the HTML generator before rebuilding so later builds preserve corrections.

## Still needed before calling the project submission-ready

- Record a real applicant trial using `docs/user_trial.md`; do not substitute automated testing for human feedback.
- Test the helper on a permitted real employer form before making an actual Workday-compatibility claim. Submission and agreements remain manual.
- Instructor clarification recorded: the owner reports any model is allowed. The selected Astra configuration remains unchanged.
- Verify the public GitHub clone and final repository links; see output/evidence/remote_clean_setup.json when complete.
- Review the final package and submit it through Canvas. No submission has been made.

## Rubric review

The October 25 assessment in [grading_review.md](../output/grading_review.md) estimates 79/100 for current content (planning range 75–85), conditional on resolving repository access and model/account requirements. This is an internal estimate, not a course grade. Priorities are real applicant evidence, permitted employer-form validation and a measured career-pivot comparison; further cosmetic features alone do not address those gaps.

## Submission preparation update
Added exact-source application checks, explicit exclusion scope, reviewed given/family names, repeated education mapping and dynamic-field safeguards. The current report has 15 printed pages and the deck remains 9 slides. A captioned automated demo and empty timed trial worksheet are ready. See `output/submission_checklist.md` for the exact deliverables and the remaining account, human-trial and publication steps. The earlier 79-point estimate preceded these improvements and is retained as a dated review, not an awarded grade.

Historical publication preference: the user first requested local-only preparation. The latest request authorizes preparing the GitHub/Canvas handoff like the previous homeworks. The current repository is linked above.

## Private document and PowerPoint check
A real resume was tested locally with a manually transcribed, checked profile. A repeated-language bug was fixed and demonstrated with fictional before/after data. The 15-page report includes only aggregate evidence; the required nine-slide HTML deck and a nine-slide editable PowerPoint companion are prepared. No private resume or screenshot is included in source or the submission ZIP. No live model call used this resume during the initial phase.

## Authorized live AI follow-up
The owner then explicitly allowed AI processing while keeping publication on hold. The live reader returned 13 source-supported facts. All four paid runs (including one unintended review caused by a now-fixed selection race) used seven model requests, estimated at $0.36854. Three identical repeats hit the cache. Only aggregate evidence is shared in `output/evidence/private_resume_live_check.json`; raw resume text, personal screenshots and detailed outputs stay ignored. The report and required HTML deck are updated. `output/presentation/Pivot_Desk_Live_Test.pptx` is the updated PowerPoint companion; the original `Pivot_Desk.pptx` remains intact. The package includes the updated copy under the standard filename. That test preceded repository publication. Canvas upload remains outstanding.
