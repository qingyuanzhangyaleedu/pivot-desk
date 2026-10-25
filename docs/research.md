# Product and source research

Reviewed October 25, 2026. Product comparisons describe specific documented capabilities, not an exhaustive market review.

| Source | What it supports | Decision for Pivot Desk |
| --- | --- | --- |
| [Simplify Copilot setup](https://help.simplify.jobs/en/help/articles/1749022-install-and-set-up-copilot) | A reusable profile and browser autofill already exist, including ATS support | Do not claim that application autofill is new. Make reviewed evidence and manual-consent boundaries central; Workday compatibility must be tested |
| [Teal job tracker](https://www.tealhq.com/tools/job-tracker) | Job tracking and application organization are established product features | Tracking alone is not the novelty; use it as a useful supporting workflow |
| [Greenhouse Job Board API](https://docs.greenhouse.io/job-board.html) | Public board GET endpoints expose employer job data without an application-submission credential | Use read-only public feeds. Never call the application POST endpoint |
| [OpenAI Astra model](https://developers.openai.com/api/docs/models/gpt-6-astra) | Structured outputs, function calls, reasoning controls and standard rates | One configured model, bounded requests, actual token counts and dated public cost estimates |
| [PydanticAI agent documentation](https://ai.pydantic.dev/agent/) | Typed agent outputs, tools and runs | Validate model outputs, use a real message/tool loop and record usage |

The proposed distinction is the combination of applicant-controlled hard filters, traceable career-pivot evidence, explicit unknowns and a review-only reusable application profile in a local workspace. It is a focused design contribution, not evidence that no competitor offers similar pieces. Its usefulness over an existing product still needs a real applicant comparison.

Job record used in the measured comparison: [Heartflow — Manager, Corporate Strategy, MBA Grad Summer 2027](https://job-boards.greenhouse.io/heartflowinc/jobs/6218422004). The captured source record is in `output/evidence/live_runs.json`; current availability may change.
