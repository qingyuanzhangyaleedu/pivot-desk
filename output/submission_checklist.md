# Submission handoff — Pivot Desk

## Files for Canvas

1. A public GitHub repository link, or a private repository accessible to `zlisto`. **Publication is pending; do not substitute localhost or a ZIP for the required link.**
2. `report.html` — self-contained report, with embedded screenshots and diagrams.
3. `slides.html` — self-contained reveal.js deck, nine slides.
4. Optional `output/demo.webm` — captioned automated walkthrough with a fictional applicant and a real AI review. It has no human narration and is not a user study.

The submission folder and ZIP are convenience copies of these materials plus a source ZIP. The GitHub link remains required. Open the HTML files in that copied folder before uploading. The course deadline is October 26, 2026 at 6:00 PM; the brief does not specify a timezone, so use Canvas to confirm it.

## Run the app for a grader

Follow README.md from a fresh checkout. The pinned Python environment and `npm ci` are required; the built React app is served by FastAPI on localhost:8000. The optional Vite development server runs on localhost:5173. The fictional profile and 146 dated public-job records are bundled. No private runtime database, real resume or credential belongs in the repository.

The submitted code uses `gpt-6-astra`, as explicitly requested. The default workspace mode uses Portkey. The brief permits Luna only on the course Portkey key. For an allowed personal direct-OpenAI arrangement with Astra, set the personal paid `OPENAI_API_KEY`, then launch from backend/ with:

```sh
PORTKEY_API_KEY='' ../.venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
```

The empty process variable prevents the parent dotenv from selecting Portkey. It does not expose or change either key. No API key is bundled. This command does not establish that a suitable personal key exists; confirm the allowed account or obtain an instructor exception. The user's saved default configuration has not been changed.

## Final gates

- [x] Functional tests and browser evidence, including the application helper's controlled fixtures.
- [x] Exact-source application checks, documented benchmark and known miss.
- [x] Self-contained HTML generator and reproducible offline layout checks.
- [x] Anonymous timed trial worksheet, ready for an actual participant.
- [ ] A real applicant completes the trial. Record observations rather than inventing time savings.
- [ ] Authenticated employer-form test if claiming live Workday compatibility. Current evidence stops at the account gate.
- [ ] Confirm an allowed model/account arrangement.
- [ ] Publish the reviewed repository, verify access, and put its URL in README/report/Canvas.
- [ ] Clone the published revision and repeat the README rehearsal. Local-clone evidence is separate.
- [ ] Review the report's claims personally and upload the required files to Canvas.

## Suggested two-minute presentation

- Show the applicant's concrete problem: career-pivot evidence and repeated applications.
- Search a real role, then show why a high overlap score still requires checking graduation timing.
- Show the analyst's exact source connections and unresolved questions.
- Demonstrate preview/review/fill on the practice form; explicitly state the real Workday limit.
- Show real tokens and the rejected truncation experiment, then the safety controls.
- Finish with the development benchmark and the remaining human-impact measurement.

No grade, hiring outcome, time saving or universal Workday compatibility is guaranteed.
