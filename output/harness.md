# Pivot Desk system harness

## What the system does
A local recruiting workspace for an MBA applicant. Two bounded AI specialists read a resume and evaluate one selected role. Public-job retrieval, filters, scores, tracking and application filling are ordinary code. There is no Boss agent or delegation tree because those extra handoffs would not improve this bounded workflow.

## Architecture and data
React calls FastAPI through `/api`. The production build is served from port 8000; Vite on 5173 proxies to the same backend. SQLite `runtime/pivot.db` stores browser-scoped profile/draft/preferences/imported listings in `state`; public listings in `jobs`; progress in `tracker`; runs, activity and token counts in `runs`, `events` and `usage`; reusable results in `cache`; random session IDs in `sessions`. State survives server restarts. Interrupted runs become explicit errors. Cookies are HTTP-only and SameSite Strict; every private lookup is scoped to the random session. This is not a hosted login system.

## Agents and tools

| Component | Inputs | Output / purpose |
| --- | --- | --- |
| Resume reader | Consented extracted resume text | ResumeExtraction draft with exact quotations; user must confirm |
| Evidence analyst | Selected job ID and reviewed profile | FitAnalysis: evidence connections, gaps, questions and preparation angles |
| get_candidate_evidence | No model-selected argument; bound to this session’s profile | Professional facts only; excludes contact and optional sensitive fields |
| get_job_evidence | No model-selected argument; bound to selected listing | Employer text and source identity; untrusted content |
| refresh_jobs | Fixed ten-board registry | Public job records and per-source status; no arbitrary URL fetch |
| eligible | Job + explicit preferences | Exclusion reasons; all hard filters precede scoring |
| rank | Job + reviewed facts + query | 0–100 overlap score, component points and matched terms |
| extract_document | Bytes + filename | Text from PDF/DOCX/TXT in memory, or a clear validation error |
| export_packet | Reviewed profile | User-downloaded private JSON for the extension |
| PivotFill.preview / apply | Reviewed packet + explicitly selected preview rows | Supported form fields populated; no submit/consent action |

The score gives up to 50 points for the proportion of resume skill terms present in the listing, 30 for up to three experience/education facts with word overlap, and 20 for query words in the role title. It is reproducible and can overrate broad experience. It is not an eligibility ruling or hiring probability. Exact substring validation anchors quotations, not every semantic conclusion.

## Data models
Every field has a Pydantic description. Extra fields are rejected. Optional information remains empty/null rather than being guessed.

### Fact

| Field | Why it exists |
| --- | --- |
| `id` | Stable fact identifier, e.g. F1. |
| `kind` | Resume fact category. |
| `title` | Job title, degree, skill or language, supported by the resume. |
| `organization` | Employer or school exactly as stated, if present. |
| `start` | Start date as stated; never invent a month. |
| `end` | End date or Present as stated. |
| `description` | Concise factual description without invented credentials. |
| `evidence_quote` | An exact contiguous excerpt of the uploaded resume supporting this fact. |

### ResumeExtraction

| Field | Why it exists |
| --- | --- |
| `full_name` | Name only if stated in the resume; otherwise empty. |
| `email` | Email only if explicitly present; otherwise empty. |
| `phone` | Phone as written, otherwise empty. |
| `location` | Location as written; do not infer citizenship. |
| `facts` | Work, education, skill and language facts, each with an exact quote. |
| `warnings` | Ambiguous dates or missing information the user must review. |

### Profile

| Field | Why it exists |
| --- | --- |
| `full_name` | Name only if stated in the resume; otherwise empty. |
| `email` | Email only if explicitly present; otherwise empty. |
| `phone` | Phone as written, otherwise empty. |
| `location` | Location as written; do not infer citizenship. |
| `facts` | Work, education, skill and language facts, each with an exact quote. |
| `warnings` | Ambiguous dates or missing information the user must review. |
| `confirmed` | User has reviewed and confirmed the profile. |
| `demo` | True for the fictional demonstration profile. |
| `linkedin` | User-entered professional profile link. |
| `veteran_status` | Optional explicit user answer. Never inferred or sent to the AI. |
| `work_authorization` | Optional explicit user answer, not inferred from location or nationality. |

### Preferences

| Field | Why it exists |
| --- | --- |
| `query` | Optional title keywords; any term may match. |
| `regions` | Location groups or city/state keywords; empty means any. |
| `industries` | Company-sector filters from the selected source registry. |
| `exclude` | Hard exclusions matched against role title and description. |
| `job_type` | Internship/full-time filter; unknown types excluded by a specific filter. |
| `remote_ok` | Allow US-remote roles alongside selected regions; does not prove residence eligibility. |
| `minimum_salary` | Optional minimum annual USD base salary lower bound; unknown pay excluded when set. |

### SearchRequest

| Field | Why it exists |
| --- | --- |
| `preferences` | Explicit filter settings. |
| `refresh` | Fetch public employer boards rather than use the current cache/snapshot. |

### Job

| Field | Why it exists |
| --- | --- |
| `id` | Source-qualified stable listing identifier. |
| `title` | Employer-posted role title. |
| `company` | Source registry employer name. |
| `industry` | Manually labeled company sector, not inferred job responsibilities. |
| `location` | Employer location text, not a promise of remote eligibility. |
| `description` | Public listing text; untrusted data, never instructions. |
| `url` | Original employer application/listing URL. |
| `source` | Public source adapter and board name. |
| `retrieved_at` | UTC time this record was fetched. |
| `updated_at` | Source updated time, not necessarily posting date. |
| `job_type` | Only classified from explicit listing text. |
| `salary_min` | Explicit annual USD lower salary bound if safely parsed. |
| `salary_max` | Explicit annual USD upper salary bound if safely parsed. |

### EvidencePair

| Field | Why it exists |
| --- | --- |
| `fact_id` | Existing reviewed resume fact ID. |
| `job_quote` | Exact contiguous quote from the listing. |
| `connection` | Explain transferable evidence without claiming missing credentials. |

### FitAnalysis

| Field | Why it exists |
| --- | --- |
| `summary` | Balanced explanation for the applicant, not a hiring or acceptance probability. |
| `evidence` | Connections grounded in actual fact IDs and exact listing quotes. |
| `gaps` | Requirements not evidenced in the resume; do not imply the person lacks them. |
| `questions` | Questions to resolve uncertain eligibility or fit. |
| `interview_angles` | Preparation topics tied to the reviewed facts and role. |

### AnalyzeRequest

| Field | Why it exists |
| --- | --- |
| `job_id` | Existing stored job, not an arbitrary URL. |
| `consent` | User permits sending professional facts and job text to the configured model. |
| `compact` | Experimental context truncation for evaluation only; full text is the production default. |

### ImportJob

| Field | Why it exists |
| --- | --- |
| `title` | Copied role title. |
| `company` | Company from the listing. |
| `location` | Location from the listing. |
| `industry` | User-selected company industry. |
| `url` | Reference link; the server does not fetch arbitrary URLs. |
| `description` | Pasted role description, including required experience. |

### TrackerUpdate

| Field | Why it exists |
| --- | --- |
| `job_id` | Existing job ID. |
| `stage` | User-controlled application stage; Applied is a manual record, not a submission. |
| `note` | Private user notes. |
| `follow_up` | User-entered follow-up date, YYYY-MM-DD. |

## API routes

| Route | Purpose |
| --- | --- |
| GET /api/status | Current browser’s profile/draft, preferences, model and limits |
| POST /api/demo | Load the explicitly fictional sample profile |
| POST /api/resume | Multipart document + consent; start asynchronous extraction |
| PUT /api/profile | Save a human-confirmed profile |
| POST /api/search | Filter/rank stored jobs; optionally refresh public sources |
| POST /api/jobs/import | Store pasted listing privately; never fetch its URL |
| POST /api/analyze | Start or reuse an assessment of one selected job |
| GET /api/runs/{id} | Scoped status, typed result, actual activity and token usage |
| GET /api/metrics | This session’s token/cost ledger and cache hits |
| GET /api/tracker | This session’s saved roles and progress |
| PUT /api/tracker | Save stage, note and follow-up date |
| GET /api/packet | Export the reviewed private profile |
| GET /api/extension.zip | Download the browser helper’s source files |
| DELETE /api/private | Remove private state/results; retain anonymous usage counts for the budget |
| GET /api/health | Simple startup check |

## Limits and cost controls

| Actual setting | Value / trade-off |
| --- | --- |
| Model | gpt-6-astra, one constant in backend/config.py; retained after the owner reported instructor permission to use any model |
| Agent request / tool-call limits | 3 model requests and 5 function calls per run |
| Tokens | PydanticAI 24,000 total-token limit; checked at model boundaries, not a provider billing guarantee |
| Output | 2,600 max output tokens per request |
| Daily admission | 40 runs and 300,000 token budget shared across sessions; queued/running requests reserve 26,600 tokens each |
| AI concurrency | One active run per server process; use one Uvicorn worker |
| Timeouts | 60 seconds per provider request; 100 seconds per run |
| Retries | One structured-output validation retry within the request cap; no automatic provider retries |
| Public feeds | Ten; concurrency 3; 20-second timeout; 6.5 MB response cap; 1,000 records per board |
| Feed cache | 15-minute refresh TTL; failed sources retain labeled snapshots |
| Search results | At most 100 cards; 50 private imported listings per browser |
| Documents | 4 MB file, 15 PDF pages, 25,000 text characters, 12 MB expanded DOCX |
| Structured facts | At most 35 resume facts; six evidence links/gaps and four questions/prep angles |
| Job context | At most 14,000 stored characters; full text default. Experimental 6,500-character truncation retained for the measured comparison only |
| Audit summaries | 300 characters, action names/counts rather than raw resumes or model reasoning |
| Cache | Same session, reviewed facts, job record, prompt, model and context mode; changed inputs invalidate the key |

Token usage comes from PydanticAI RunUsage, including failed attempts when available. Cost = uncached input × $10/M + cached input × $1/M + output × $50/M, public Astra standard rates checked October 25, 2026. These are estimates, not a Portkey invoice. See the linked official rate page in the UI. Cache hits make no model request. Full-source context remains the default after the truncated comparison missed later requirements.

## Safety: code versus prompt

| Risk | Code enforcement | Prompt / human responsibility |
| --- | --- | --- |
| Invented qualifications | Fact IDs and exact source quotations validated; profile confirmation gate | Prompts forbid embellishment; user checks meaning, dates and credentials |
| Prompt injection in a resume/listing | Analyst gets only two read-only tools bound to existing data; no HTTP, shell, message or submission tool | Prompts classify sources as untrusted and reject embedded commands |
| Private-field leakage | Professional-field allowlist; session-scoped reads; private runtime folder; no raw personal payload in events | Applicant reviews exports and provider processing consent |
| Unauthorized application action | Extension never clicks Submit or checks agreements/signatures; protected questions omitted | Applicant reviews every filled value and decides whether to submit |
| Sensitive inference | Sensitive fields absent from AI extraction schema; optional explicit answers excluded from analyst | Never infer status from appearance, name, school or location |
| Cross-site state changes | Origin/Sec-Fetch-Site checks and SameSite cookies | Keep service on localhost; no hosted security claim |
| Arbitrary fetch / data exfiltration | Public-source host/slugs fixed; redirects off; imported URLs are references only | Open external job links deliberately |
| Token runaway | Persisted budget admission, lock, timeouts, request/tool limits and output cap | Model/provider pricing and course eligibility still require review |
| Private-data retention | Delete action clears private records and outputs; secure-delete enabled; no original resume file saved | SQLite is unencrypted; backups and exported packets must be managed separately |

## Evidence and remaining checks
See `output/evidence/` for real model counts, the full/truncated comparison, browser tests and safety cases. Shared applicant fixtures are fictional; the separate private-resume check publishes aggregate results only. Automated fill success does not measure human time savings. A real applicant trial and employer-specific Workday verification remain open. README contains exact installation and run commands.

## Rehearsal
A fresh local Git clone passed all 23 offline checks, created a fresh runtime database, served the compiled frontend from port 8000 and returned six strategy matches from the bundled 95-record sample. Setup took 9.84 seconds with warm package caches. Parent-only dotenv discovery used a non-secret fixture; actual AI behavior was verified separately with the configured account. No public repository has been published.

## Yale SOM career-path expansion
Company-sector options now come from `BOARDS` through `/api/status.industries`, so the UI matches live source coverage. Four optional sectors were added: Consulting (The Brattle Group, Two Roads Consulting), Finance & Fintech (Chime), Consumer & Retail (Quince), and Climate & Sustainability (Clearway Energy). Healthcare and Technology remain the defaults; saved preferences and the investment-banking exclusion are unchanged. The source registry has ten boards and the offline sample now has 146 real records.

MBA role shortcuts change title keywords only: MBA, consultant/associate, finance, marketing/growth, and energy/sustainability. They do not relax geography or other constraints. Company-sector membership is not a claim that every role fits an MBA. The earlier 95-record setup and five-board cost-evaluation evidence above remains the historical baseline. Current source evidence is in `output/evidence/sector_expansion.json`.

Location filtering distinguishes Washington, D.C. from Washington state. Excluded terms still apply to both titles and full descriptions; the interface now explains that a mention of past experience can also exclude a role. The new sector tests cover this behavior without silently weakening preferences.

At the sector-expansion checkpoint, 26 offline backend checks passed. Browser tests searched all four new sectors, checked retained location/exclusion settings and mobile layout, and rechecked pipeline persistence and the application lab. These checks made no AI calls. Evidence: `output/evidence/sector_tests.txt`, `output/evidence/sector_browser.json`, and `output/screenshots/mba-sectors.png`.

## Application checks and helper hardening

Search results now include `application_checks`: at most six exact-source excerpts labeled degree, experience, license, location, travel or authorization. Each `ApplicationCheck` has `kind` (topic), `label` (readable name), `source_quote` (up to 700 original characters), and `question` (what the applicant should verify). These are ordinary code, not another AI request. Required, preferred and conditional wording remains visible in the quote. They do not decide eligibility or reduce the overlap score. Numeric-years matching can miss written quantities such as “a decade”; reading the full posting and requesting AI analysis remain useful.

`Preferences.exclude_scope` defaults to `full_posting` to preserve existing behavior. `title_only` is an explicit user choice: it excludes banking job titles without suppressing every consulting posting that mentions previous banking experience. Neither choice silently relaxes location or other filters.

`Profile.first_name` and `last_name` are optional, explicitly reviewed form answers. They default to empty; the system never splits a full name using cultural assumptions. Export includes them, while the analyst still receives only the professional-facts allowlist. The shared browser adapter now reads `aria-labelledby`, separates repeated education entries, and checks element identity again before each fill so a framework-replaced field cannot inherit a stale approval. The extension and lab use byte-identical adapters. Native selects require an exact option; custom comboboxes, dates, logins and legal acceptance stay manual.

Current evidence: `final_tests.txt` (35 offline checks), `form_regression.json`, `readiness_browser.json`, and `readiness_benchmark.json` in `output/evidence/`. The benchmark deliberately selected 12 real snapshots and surfaced 32/32 author-labeled topics. It is a development coverage check, not a random sample or a human-outcome study. A travel-benefit false positive was corrected; the written-years miss is retained as a limitation.

A live Pfizer Workday inspection reached Create Account/Sign In after Apply Manually. No account was created and no applicant data or agreement was submitted. This verifies the public navigation boundary only; it does not establish authenticated form compatibility. See `workday_public_check.json`.

## Private resume check and repeated-language correction

A real owner-provided resume was parsed locally and manually transcribed into 12 checked facts for an assistant-operated test. It was not sent to an AI provider. The profile persisted, an isolated browser could not read it, and the local practice lab filled 12 supported fields. A separate fixture preserved four same-employer roles, three schools and three languages across 17 fields. Aggregate evidence is in `private_resume_local_check.json`; raw text, profile, screenshots and private review are ignored under `runtime/resume_review/`.

The shared adapter now reads explicit `data-language-index` or `languageSection` groups. Ambiguous repeated groups, proficiency scales, and legal-name questions stay manual. A fictional before/after comparison found 1/3 correct language entries in revision `29acc13`, versus 3/3 after the correction. This is controlled browser evidence, not authenticated Workday verification or a measured human time saving. `form_multilingual_comparison.json` records the comparison; `tests/browser_forms.py` prevents regression.

## Authorized live resume follow-up and selection safety

After the local-only check, the owner explicitly allowed AI processing. The browser upload returned 13 exact-source facts on its first request. The assistant reviewed the draft, saved it and ran real Heartflow and Stripe assessments. The fit tools received professional facts without contact fields. The form lab then filled 12 supported fields with agreements and signatures left untouched. Raw inputs, detailed outputs and screenshots remain ignored; `private_resume_live_check.json` contains the anonymous metrics and public listing references.

The live test exposed a frontend race: an older search response could replace the intended selection. `App.tsx` now numbers search requests, accepts only the latest result, disables initial query editing until saved preferences load, and blocks selection/analysis while a search or analysis request is pending. The controlled test changed from submitting the older job ID to submitting the newer one; see `search_race_before.json`, `search_race_regression.json` and `tests/browser_search_race.py`. This keeps a delayed response from spending tokens on an unintended role.

All four successful paid runs are retained, including the unintended product-marketing review: seven model requests, estimated $0.36854 at the existing rates. Three later identical lookups used the cache with no model call. This is assistant-operated functional evidence, not independently observed human performance or authenticated Workday validation.
