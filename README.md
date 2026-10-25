# Pivot Desk — MBA recruiting with evidence

Local app: **http://localhost:8000** after the steps below. React development preview: http://localhost:5173.

Upload a PDF, DOCX or text resume, review extracted facts, filter real employer listings, inspect a transparent overlap score and an AI evidence review, then prepare reusable application fields. Nothing applies for a job, sends a message, or accepts an agreement automatically.

## Start after a fresh clone

Prerequisites: Python **3.11+** (tested with 3.13), Node **22.12+**, npm, internet for package installation. Use your own computer; this is a local personal workspace, not a public multi-user service.

```sh
cd final_project
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
npm --prefix frontend ci
npm --prefix frontend run build
```

If you cloned into a different folder, `cd` into that folder instead. No database setup is needed: first startup creates ignored `runtime/pivot.db` and loads a small dated snapshot of real public jobs.

### Configure AI

The app searches `.env` in this repository first, then its parent folder; existing environment values take priority. Copy `.env.example` to `.env` only if you need a local file. Never commit a real key.

- `PORTKEY_API_KEY`: the existing workspace account, through the fixed Portkey endpoint.
- `OPENAI_API_KEY`: optional personal direct-OpenAI alternative if Portkey is unset. Do not set both unless you intend Portkey to take priority.
- `PIVOT_DATA_DIR`: optional private runtime directory; defaults to `runtime/`.

**Model decision confirmed:** the explicit workspace instruction selects **gpt-6-astra**, so that is the current `MODEL_NAME` in `backend/config.py`. The assignment permits **gpt-6-luna only on the course Portkey key**. The user explicitly confirmed Astra on October 25. This preserves the requested model but does not satisfy that course-key restriction; review it with the course before submission. Changing models also requires updating the pricing constants and re-running the measured evaluation. The present evidence measures Astra; it must not be relabeled as Luna. No extra search-service key is required.

Without an AI key, public job search, the fictional demo profile, scoring, tracking and the application practice lab work. Resume AI extraction and AI evidence review show a configuration error instead of pretending to run.

### Run the complete app

```sh
source .venv/bin/activate
cd backend
uvicorn main:app --host 127.0.0.1 --port 8000
```

Open **http://localhost:8000**. The backend serves the compiled frontend. Stop with Ctrl+C. No auto-reloader is needed.

For development, keep that backend running and in a second terminal:

```sh
cd final_project/frontend
npm run dev -- --host 127.0.0.1
```

Open http://localhost:5173. Vite proxies `/api` to port 8000; CORS also allows the localhost Vite origin. Both start commands work from their stated folders.

## Five-minute walkthrough

1. Click **Explore a fictional demo**. Avery Morgan is invented; the jobs are real source snapshots.
2. Set role keywords to `strategy`, West Coast, Healthcare + Technology, exclude `investment banking`. Refresh the employer feeds for current listings.
3. Select Heartflow’s MBA corporate-strategy role if still open. Its overlap score is a keyword signal, **not a hiring probability**. Click **Get an AI evidence review** to see source quotes, gaps and interview questions.
4. In **My evidence**, upload your own PDF/DOCX/TXT or paste text. Consent to AI processing, check each extracted field, edit mistakes, and click **I reviewed these facts — save profile**. Nothing is inferred about veteran status or work authorization.
5. Save a role and update **My pipeline**. Reload: the same browser retains its profile and notes.
6. In **Application kit**, open the practice lab. Preview, review and fill. It handles common contact, work, education and language fields. Consent, signatures, unsupported dates and unknown questions remain manual.
7. Open **Usage & proof** for actual token counts and cost estimates, or delete the private workspace.

## Use the application helper on an employer page

Download the extension in Application kit (or load `extension/` directly). In Chrome: `chrome://extensions` → Developer mode → Load unpacked → select the unzipped extension folder. Export your private profile packet, open the extension and import the JSON. On an employer form, click **Preview this page**, inspect proposed values, select any optional sensitive answers yourself, confirm review and click **Fill selected fields**.

The extension requests `activeTab`, `scripting` and session storage, with no permanent all-site access. It never clicks Submit, signs agreements, answers CAPTCHA, uploads files, or guesses personal answers. Workday portals vary. The local lab and shared adapter are tested; universal compatibility with authenticated employer Workday portals is **not** established. Dates and custom controls often require manual entry. Exported profile packets contain personal information: keep them private and remove them when done. Clear the extension profile to remove its session copy.

## Data and limitations

Five curated public Greenhouse boards: Heartflow, Oscar Health, Figma, Airbnb and Stripe. The app is not a general crawl of the entire job market. `Add a posting` accepts copied text and an HTTPS reference link from another site, including Workday; the server does not fetch arbitrary submitted URLs. A source failure preserves its dated snapshot and displays a warning. The bundled sample contains 95 records fetched October 25, 2026; refresh retrieves current board data, which changes over time.

The location filter uses the employer’s text; US-remote does not establish eligibility in every state. Company sectors are manual source labels. A salary appears only when an explicit annual USD range is parsed. Unknown dates, compensation, employment type and qualifications remain unknown. A high overlap score can still hide a seniority or domain gap: review the source and analyst’s questions.

Resume files are parsed in memory and not saved. Extracted text, profile fields, notes and AI results are stored in the private local database. AI extraction sends resume text after consent; job analysis receives professional facts only. Local browser-session separation is not a substitute for hosted authentication or encryption. Do not expose this server to the internet. The database and profile exports are excluded from Git.

## Verify and inspect

```sh
source .venv/bin/activate
python -m unittest discover -s tests -v
npm --prefix frontend run build
```

Tests are offline and do not charge the model. The live measurements and browser evidence in `output/evidence/` use fictional applicant data. Real-user recruiting outcomes have not been measured.

| Location | Contents |
| --- | --- |
| `backend/` | FastAPI routes, Pydantic contracts, two bounded specialists, storage and public-job tools |
| `backend/prompts/` | Resume reader and evidence analyst instructions |
| `frontend/` | React + Vite + TypeScript interface and local application lab |
| `extension/` | Review-before-fill Chrome extension |
| `data/` | Fictional resume/profile and dated public job sample |
| `tests/` | Offline security and API contract tests |
| `output/harness.md` | Actual fields, tools, routes, limits and safety controls |
| `output/evidence/` | Measured runs, tests and setup evidence |
| `report.html`, `slides.html` | Offline draft submission artifacts; outstanding items clearly stated |
| `AI_prompts.md` | User prompt log |

The course brief stays in `docs/assignment_brief.pdf` for local reference and is excluded from publication. The repository has not been published or submitted on the student’s behalf.
