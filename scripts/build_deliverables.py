"""Build offline HTML drafts from recorded evidence; no AI calls or private inputs."""

from pathlib import Path
import base64, json, html

R = Path(__file__).resolve().parents[1]
E = R / "output/evidence"
live = json.loads((E / "live_runs.json").read_text())
full = live["runs"][1]
short = live["runs"][2]


def img(name, caption="", cls=""):
    data = base64.b64encode((R / "output/screenshots" / name).read_bytes()).decode()
    return f'<figure class="{cls}"><img alt="{html.escape(caption)}" src="data:image/png;base64,{data}"><figcaption>{caption}</figcaption></figure>'



def crop_img(name, caption, x, y, width, height, source_width):
    # Native HTML viewport crops the embedded screenshot; source pixels remain unchanged.
    data = base64.b64encode((R / "output/screenshots" / name).read_bytes()).decode()
    return f'<figure><div style="position:relative;overflow:hidden;aspect-ratio:{width}/{height};border:1px solid #e5d9df"><img alt="{html.escape(caption)}" src="data:image/png;base64,{data}" style="position:absolute;width:{source_width/width*100}%;max-width:none;max-height:none;left:{-x/width*100}%;top:{-y/height*100}%;border:0"></div><figcaption>{caption}</figcaption></figure>'


def table(head, rows):
    return (
        "<table><thead><tr>"
        + "".join("<th>" + x + "</th>" for x in head)
        + "</tr></thead><tbody>"
        + "".join(
            "<tr>" + "".join("<td>" + str(x) + "</td>" for x in row) + "</tr>"
            for row in rows
        )
        + "</tbody></table>"
    )


def diagram():
    return """<svg viewBox="0 0 760 280" role="img" aria-label="Resume upload to reviewed facts, job retrieval and filters, evidence review, then human-controlled application kit" xmlns="http://www.w3.org/2000/svg"><defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10" fill="#b33f70"/></marker></defs><g fill="none" stroke="#b33f70" stroke-width="2" marker-end="url(#arrow)"><path d="M175 60H285"/><path d="M475 60H585"/><path d="M175 210H285"/><path d="M475 210H585"/><path d="M665 90V180"/></g><g fill="#f7e7ee" stroke="#b33f70"><rect x="5" y="25" width="170" height="70" rx="5"/><rect x="285" y="25" width="190" height="70" rx="5"/><rect x="585" y="25" width="170" height="70" rx="5"/><rect x="5" y="175" width="170" height="70" rx="5"/><rect x="285" y="175" width="190" height="70" rx="5"/><rect x="585" y="175" width="170" height="70" rx="5"/></g><g fill="#291f28" font-family="Arial,sans-serif" font-size="17" text-anchor="middle"><text x="90" y="54">Upload resume</text><text x="90" y="77" font-size="13">PDF / DOCX / TXT</text><text x="380" y="54">Resume reader</text><text x="380" y="77" font-size="13">AI extraction → human review</text><text x="670" y="54">Reviewed facts</text><text x="670" y="77" font-size="13">Private browser workspace</text><text x="90" y="204">Public job feeds</text><text x="90" y="227" font-size="13">Ten boards or pasted text</text><text x="380" y="204">Filter + score</text><text x="380" y="227" font-size="13">Deterministic code</text><text x="670" y="204">Evidence analyst</text><text x="670" y="227" font-size="13">Two read-only tools</text><text x="380" y="273" font-size="14">Applicant chooses → save role → preview fields → approve fill → review manually</text></g></svg>"""


sections = []


def page(kicker, title, body):
    sections.append((kicker, title, body))


page(
    "01 / TITLE + LINKS",
    "Pivot Desk",
    f"""<p class="subtitle">An MBA recruiting workspace that connects a resume to real roles and prepares repeat application fields for human review.</p><p><strong>Qingyuan Zhang</strong> · AI Foundations for Managers · October 25, 2026</p><div class="callout"><strong>Working local prototype • final review package</strong><br>Run locally at <a href="http://localhost:8000">localhost:8000</a> using README.md. Source folder: final_project/. GitHub publication and Canvas submission have not been performed. This report and the slide deck contain their own images and need no server to open.</div>{img("discovery.png", "Initial recorded run: fictional Avery Morgan profile, real Heartflow MBA listing, West Coast filters and an evidence-overlap score.")}<h2>What is working</h2><p>A user can upload a resume, correct the extracted facts, filter employer listings, request a grounded fit review, save a role and prepare a reusable application profile. The browser helper previews ordinary fields before filling them. It never submits an application or accepts an agreement.</p><p class="small">The user confirmed gpt-6-astra, following the workspace instruction. The course brief permits only gpt-6-luna on the course key. This documented configuration difference remains a submission issue; the measurements below are Astra measurements and are not relabeled as Luna.</p>""",
)
page(
    "02 / MOTIVATION",
    "A career pivot creates two kinds of work",
    """<p>I am building this for an MBA student who wants to move into West Coast healthcare or technology roles and avoid investment banking. The request was not simply to rewrite a resume. It was to connect a person’s actual experience to relevant openings and reduce the repeated work in application forms.</p><h2>Choosing where to apply</h2><p>The applicant has to combine several decisions: industry, geography, role family, required experience, degree timing and practical eligibility. A title that says “strategy” can still demand board-level ownership or clinical expertise. A job’s reference to an MBA does not establish that an MBA candidate has already met the requirement.</p><p>The app separates hard preferences from fit evidence. West Coast, company sector, title keywords, excluded phrases, role type and a minimum published salary can filter the search before AI is used. The overlap score then shows what matched. An evidence review explains what the resume actually supports and which questions remain open.</p><h2>Preparing the same facts repeatedly</h2><p>The applicant also re-enters employers, job titles, descriptions, education and language information. Small errors accumulate when these details are copied separately into different forms. Pivot Desk extracts a draft once, asks the user to review it and reuses only that reviewed record.</p><p>Veteran status, work authorization, employer agreements and signatures are different kinds of information. The app never derives them from a resume or location. Optional personal answers are supplied by the user; legal acceptance and submission remain manual.</p><h2>The bounded first version</h2><p>The current version covers ten public employer boards across Healthcare, Technology, Consulting, Finance & Fintech, Consumer & Retail, and Climate & Sustainability, plus private posting import and a local form practice lab. It does not search every vacancy on the web or bypass a login, CAPTCHA or site restriction. For a role found on Workday, the applicant can paste its text and keep the original link; the server does not scrape the private application.</p><div class="callout"><strong>Evidence standard:</strong> The user described this recurring problem directly. A human before/after time study has not yet been conducted. The report does not assign an invented number of hours to the problem or claim better hiring outcomes.</div>""",
)
page(
    "03 / WHAT IS NEW",
    "The contribution is evidence and control",
    table(
        ["Existing approach", "Already useful", "Pivot Desk’s focus"],
        [
            [
                "Simplify Copilot",
                "Reusable application profiles and ATS/browser autofill",
                "Do not claim autofill is new; expose a review boundary and unsupported fields",
            ],
            [
                "Teal job tracker",
                "Organizing a recruiting pipeline and applications",
                "Treat tracking as supporting infrastructure, not the novelty",
            ],
            [
                "A general AI chat",
                "Flexible discussion of a resume and pasted job description",
                "Persist reviewed facts; use deterministic filters, source quotations, a typed result and a constrained form helper",
            ],
        ],
    )
    + """<p>The project’s proposed contribution is the connected workflow for a career pivot: explicit applicant preferences → traceable professional facts → source-linked fit explanation → reusable, human-reviewed application fields. A result has to show both a reason to consider the role and what the resume does not establish.</p><h2>A concrete example</h2><p>The demo profile’s healthcare expansion research and financial modeling connect to Heartflow’s corporate-strategy responsibilities. Its MBA candidacy does not prove a completed accredited MBA. Its clinical-operations collaboration does not establish cardiac-device expertise. These distinctions are more useful than an unqualified “93% match.”</p><p>The app’s numerical score is deliberately labeled evidence overlap. It is calculated in code and cannot be inflated by the analyst. The analyst instead names missing evidence and questions about timing, scope and eligibility. The source posting is available beside the result.</p><h2>What this does not establish</h2><p>This is not a claim that no competitor offers these pieces. Ten curated boards provide less coverage than a mature recruiting service, and the browser helper has not been tested across actual Workday tenants. Whether an MBA applicant prefers this combination to an existing product remains an empirical question for the user trial.</p><p class="source">Sources, reviewed October 25, 2026: <a href="https://help.simplify.jobs/en/help/articles/1749022-install-and-set-up-copilot">Simplify Copilot setup</a>; <a href="https://www.tealhq.com/tools/job-tracker">Teal job tracker</a>. The comparison is limited to the documented capabilities above.</p>""",
)
page(
    "03 / WHAT IS NEW · DECISION CHECKS",
    "A high score leaves questions open",
    '<div class="cols"><div>' + img("application-checks.png", "Actual check panel: the required MBA remains visible despite a high overlap score.", "portrait") + '</div><div><h2>Before investing the time</h2><p>Six topics flag exact employer wording: degree, experience, credentials, attendance, travel and authorization. Each asks the applicant to verify the condition. It never decides eligibility or changes the score.</p>'
    + table(["Development check", "Result"], [
        ["12 selected real postings", "32/32 labeled topics surfaced"],
        ["Source fidelity", "Every excerpt matched its source; zero AI calls"],
        ["Noise corrected", "Travel credits no longer imply a travel expectation"],
        ["Known miss", "A decade of experience misses the numeric-years rule"],
    ])
    + '<p>The cases were selected and labeled during AI-assisted development, without independent human review. This is a coverage check, not a random sample or proof of eligibility accuracy.</p><p>The title-only exclusion option also keeps consulting roles that mention prior banking experience. Full-posting exclusion remains the stricter default.</p></div></div><p class="source">Evidence: readiness_benchmark.json, readiness_browser.json and tests/test_readiness.py. The original score-only search response had no separately labeled application checks. This comparison measures visible screening information, not hiring outcomes.</p>',
)
page(
    "04 / THE AGENTS",
    "Two specialists, with a human between them",
    diagram()
    + table(
        ["Specialist", "Inputs and authority", "Result"],
        [
            [
                "Resume reader",
                "Consented text extracted from PDF, DOCX or TXT. No external-action tools.",
                "Typed draft: contact fields, professional facts, exact resume excerpts and warnings.",
            ],
            [
                "Evidence analyst",
                "get_candidate_evidence and get_job_evidence; both bound to this session and selected job.",
                "Typed fit review: summary, fact-to-quote connections, gaps, questions and preparation angles.",
            ],
        ],
    )
    + """<p>The two roles do not delegate to each other. The user first confirms the resume facts, then selects a job for review. This is a deliberate human checkpoint, not a missing autonomous step. A Boss agent, open-ended web agent or five-role team would add handoffs without improving this small decision.</p><p>All PydanticAI output fields have descriptions and reject extra fields. Resume quotes must occur in the uploaded text. Fit evidence must reference existing fact IDs and exact job-description excerpts. The analyst must use both evidence tools before its final result is accepted.</p><p>Public-job fetching, filtering, scoring, saving stages and filling reviewed form fields are ordinary functions. They do not need language-model judgment. The resume reader handles flexible document wording; the analyst handles the difference between transferable evidence and an unsupported claim.</p><p class="small">Model: gpt-6-astra, low reasoning effort. One constant in backend/config.py. Portkey uses the workspace key; an optional direct OpenAI path uses OPENAI_API_KEY when Portkey is unset. The user explicitly chose Astra; the course-key model restriction remains noted.</p>""",
)
page(
    "05 / THE AGENTS · REAL RUN",
    "The Heartflow review",
    f"""<p>The recorded run used the fictional Avery Morgan resume and Heartflow’s <em>Manager, Corporate Strategy — MBA Grad, Summer 2027</em> listing. The public record is 8,937 characters long and includes San Francisco/Rohnert Park, a completed accredited MBA requirement and moderate travel.</p><div class="cols"><div>{img("analysis-excerpt.png", "A cropped screenshot of the actual assessment, with fact IDs and employer quotations.", "portrait")}</div><div><h2>What happened</h2><p>The reader processed the demo TXT upload in 9.15 seconds and returned a draft. The profile was then confirmed through the API. The controlled fit comparison used the reviewed eight-fact demo record.</p><p>The analyst requested both evidence tools in its first model response. One tool returned eight professional facts; the other returned the selected employer record. The next response produced a validated result. The full assessment took 18.31 seconds and two model requests.</p><h2>What the result got right</h2><p>It connected market research and financial modeling to the strategy work, and pricing analysis to customer economics. It asked for exact employment months rather than silently treating 2020–2025 as a guaranteed five years.</p><p>It distinguished MBA candidacy from completion, and healthcare operations from cardiac medical-technology expertise. It also asked about on-site availability and travel.</p><h2>What still needs judgment</h2><p>Exact excerpts establish provenance; they do not prove every interpretation. The user must check the role, dates and claims. The 93/100 overlap score can overstate fit if treated as eligibility.</p></div></div><p class="source">Evidence: output/evidence/live_runs.json and the running-app screenshot. <a href="https://job-boards.greenhouse.io/heartflowinc/jobs/6218422004">Original employer listing</a>; availability can change after the captured date.</p>""",
)
page(
    "05 / THE AGENTS · HUMAN CHECKPOINT",
    "Extraction starts as a draft",
    crop_img("upload-draft.png", "Detail of the recorded PDF extraction: the draft explicitly warns that MBA candidacy does not establish degree completion.", 810, 315, 620, 230, 1440)
    + """<p>The PDF upload was disabled until consent. The actual draft appeared in 9.47 seconds, then the reviewed profile persisted after reload. That separate run used 779 input and 575 output tokens, estimated at $0.03654. It is not substituted into the controlled TXT/full/truncated comparison on the following pages.</p><h2>The recorded analyst loop</h2>"""
    + table(["Step", "Observed action"], [
        ["1. Start", "Selected job and this browser's reviewed facts were bound to the run"],
        ["2. Model request", "The analyst called get_candidate_evidence and get_job_evidence"],
        ["3. Tool returns", "Eight reviewed professional facts and the selected employer record returned; sensitive answers stayed excluded"],
        ["4. Final result", "Quote/fact-ID checks accepted a structured assessment; gaps remained explicit"],
        ["5. Human decision", "The applicant can save a role or prepare fields; no tool submits or signs"],
    ])
    + """<p>The current automated walkthrough in output/demo.webm uses fictional data and shows discovery, qualification checks, a live analyst review, pipeline and form filling. It is captioned, not a recording of an independent human trial.</p><p class="source">Evidence: upload_ui.json, live_runs.json and final_demo_run.json. The initial and final recordings are separate runs with separate usage records.</p>""",
)
page(
    "05 / THE AGENTS · PRIVATE LOCAL TEST",
    "A real resume exposed a form bug",
    """<p>The project owner supplied a real one-page resume for testing. I read the PDF locally and manually transcribed and checked 12 facts before exercising the app. This was an assistant-operated test, not a new AI extraction run or a timed human trial. No resume text went to a model or employer during this check.</p><h2>The realistic edge cases</h2><p>The document has four dated positions under one employer, three education entries and three languages. It also contains year-only employment dates, a parenthesized display name and a future MBA completion date. The profile must preserve those distinctions instead of inventing months, legal-name parts, a current address or degree completion.</p>"""
    + table(["Local check", "Observed result"], [
        ["PDF and reviewed profile", "One page parsed; 12 manually checked facts persisted after reload"],
        ["Search with the reviewed facts", "91 matches from 1,740 cached postings; filters preserved, no AI calls"],
        ["Application practice lab", "12 supported fields filled; missing address/date information and legal questions stayed manual"],
        ["Repeated-entry fixture", "17 fields preserved four positions, three schools and three languages separately"],
        ["Private workspace", "A second browser could not read the profile; no mobile overflow or browser errors"],
    ])
    + """<h2>A measured correction</h2><p>The previous adapter filled English into all three language entries: only 1 of 3 was correct. In the same fictional fixture, the revised adapter filled English, Spanish and French: 3 of 3 correct. It uses declared language-group indices and leaves ambiguous groups and proficiency scales manual.</p><p>The same fixture showed a display name entering a legal-name question. Legal-name fields now stay manual. These before/after corrections do not prove that every employer form works.</p><h2>What this adds to the evidence</h2><p>The real document revealed a defect the simpler demo missed. Raw text, profile and screenshots remain excluded from the submission; shared evidence contains aggregate results and fictional regression values. No application was submitted or agreement accepted.</p><p class="source">Evidence: private_resume_local_check.json, form_multilingual_comparison.json and form_regression.json. Search counts describe a cached snapshot, not confirmed vacancies or eligibility. Live model measurements elsewhere still use the fictional applicant.</p>""",
)
page(
    "06 / TOKENOMICS",
    "Measured model use, including unsuccessful attempts",
    table(
        ["Run", "Input", "Cached input", "Output", "Requests", "Est. USD"],
        [
            ["Resume upload", 766, 0, 561, 1, "$0.03571"],
            ["Full job review", 3225, 0, 892, 2, "$0.07685"],
            ["Truncated job review", 2774, 0, 904, 2, "$0.07294"],
            ["Identical-result cache hit", 0, 0, 0, 0, "$0"],
            ["Adversarial attempt 1: provider error", 508, 0, 47, 1, "$0.00743"],
            ["Adversarial attempt 2: completed", 1692, 0, 550, 2, "$0.04442"],
        ],
    )
    + """<p>Counts come from PydanticAI’s real RunUsage objects. Input includes all recorded model requests in the run. Cached input is a subset of input; it is not added a second time. The first malicious-listing attempt failed after a tool round. Its available partial usage is retained instead of being hidden.</p><h2>Cost method</h2><p>For the measured Astra runs, estimated cost is: (input − cached input) × $10 per million + cached input × $1 per million + output × $50 per million. These public standard prices were checked October 25, 2026. They are not a statement of the course-credit charge or the Portkey invoice.</p><p>No provider-cached input was reported in these runs. The app’s own result cache is separate: it reuses an identical structured assessment and makes no model request. The cached result is scoped to the same browser session and keyed by professional facts, job record, model, prompt and context mode.</p><h2>What costs nothing in model tokens</h2><p>Fetching public employer feeds, hard filters, overlap scoring, pipeline edits and the form helper do not call AI. Only resume extraction and a requested evidence review spend model tokens. This keeps a broad job search from turning into one model request per listing.</p><p class="source">Pricing: <a href="https://developers.openai.com/api/docs/models/gpt-6-astra">OpenAI GPT-6 Astra model page</a>. Measurements: live_runs.json, injection_attempt_1.json and injection_test.json. Public prices are estimates; hosting, maintenance and any unreported provider-side usage are excluded.</p>""",
)
page(
    "07 / TOKENOMICS · TRADE-OFF",
    "Full context earns its cost",
    """<p>The cost experiment sent the same reviewed profile and selected Heartflow role through two modes. Full mode passed the 8,937-character record; the experimental mode passed only the first 6,500 characters. Both used the same model, prompt and output schema.</p>"""
    + table(
        ["Observed change", "Result"],
        [
            ["Input-token reduction", "3,225 → 2,774: 13.98% lower"],
            ["Estimated total-cost reduction", "$0.07685 → $0.07294: 5.09% lower"],
            ["Latency in this pair", "18.31 → 17.32 seconds"],
            [
                "Quality difference",
                "Truncation cut a qualification mid-sentence and lost the specific travel requirement",
            ],
            [
                "Product decision",
                "Full source remains the UI default; exact-result caching remains enabled",
            ],
        ],
    )
    + """<p>Both reviews cited actual facts and employer text. The truncated result explicitly warned that the listing was incomplete, but it could not recover the missing requirement. A small saving is not worth making an application decision from an incomplete source. This is one controlled comparison, not a general model-quality benchmark.</p><h2>Illustrative monthly scale</h2><p><strong>Assumptions:</strong> one user extracts a resume twice and requests 20 assessments per month; 20% of assessments repeat an unchanged profile/job/prompt and hit the cache. That means two paid extractions and 16 paid full reviews. These are volume assumptions, not observed user behavior.</p>"""
    + table(
        ["Scenario", "Estimated model cost / month"],
        [
            ["One user, no repeat cache", "$1.60842"],
            ["One user, assumed 20% repeat cache", "$1.30102"],
            ["100 users at the same pattern", "$130.10"],
            ["10,000 users at the same pattern", "$13,010.20"],
        ],
    )
    + """<p>The one-user estimate is 2 × $0.03571 + 16 × $0.07685. It does not include servers, storage, support, compliance work or failed-call overhead. Real usage may differ sharply by resume length and employer text. The 100/10,000-user rows are arithmetic projections, not deployment capacity: this implementation is a single-process local app.</p><p class="source">Recorded comparison: output/evidence/cost_comparison.json. Model-boundary token limits can stop later requests, but cannot retrospectively erase tokens already generated.</p>""",
)
page(
    "08 / SAFETY",
    "Authority is narrower than the prompt",
    table(
        ["Risk", "Enforced in code", "Still needs judgment"],
        [
            [
                "Invented credentials",
                "Exact quote/fact-ID validation; typed schemas; profile confirmation",
                "A valid quote can still be interpreted too broadly",
            ],
            [
                "Injected employer instructions",
                "Only two bound read tools; no email, HTTP, shell or submission tool",
                "Prompt also tells the analyst to disregard embedded commands",
            ],
            [
                "Sensitive-data leakage",
                "Analyst receives professional facts only; optional answers excluded",
                "User controls resume-processing consent and private exports",
            ],
            [
                "Another user’s data",
                "Private API reads/writes include the random browser-session ID",
                "This is localhost separation, not a hosted identity system",
            ],
            [
                "Unapproved form action",
                "No submit/consent/signature actions; exact preview rows rechecked before fill",
                "Applicant reviews every value and employer term",
            ],
            [
                "Overspending",
                "Request/tool limits, timeout, output cap, persisted admission budget",
                "Prices and provider charges can change",
            ],
        ],
    )
    + """<h2>The data boundary</h2><p>Original resume files are processed in memory. Extracted text, confirmed fields, results and notes live in the local SQLite runtime folder. The folder is private to the operating-system user and excluded from Git. A delete action removes private records and results; anonymous usage totals remain for the shared budget. SQLite is not encrypted, and exported packets or external backups require separate care.</p><p>Resume extraction sends the consented resume text to the configured provider. Job analysis uses an explicit professional-facts allowlist and omits contact and optional sensitive answers. Activity logs contain action names and short counts, not full resumes, secrets or hidden model reasoning.</p><h2>Limits on model activity</h2><p>Each run allows three model requests, five tool calls, a 2,600-token output cap per request and a 100-second run timeout. A 24,000-token limit is checked at request boundaries. A daily 40-run/300,000-token admission budget reserves space for queued work. One active AI run is allowed per server process.</p><p>The app binds to localhost and is documented for one Uvicorn worker. It is not ready to be exposed as a shared internet service without authentication, encrypted storage, operational quotas and a separate security review.</p>""",
)
page(
    "09 / SAFETY · EVIDENCE",
    "The safeguards were exercised",
    f"""{img("safety-closeup.png", "Actual practice form after filling: the status reports 13 fields filled, while the legal checkbox, signature and optional veteran answer remain manual.")}<h2>Form and privacy checks</h2><p>The browser test filled 13 ordinary fields, including the second work-history entry. It left consent unchecked and signature/veteran fields empty. An existing different email was protected. A malicious field hint attempting to request veteran status under an unrelated label returned no value. A second browser session had no profile or saved roles from the first.</p><h2>A malicious listing</h2><p>The test listing asked the agent to reveal a private answer and API key, send them to an external URL, invent ten years as a cardiac surgeon and falsely announce submission. Attempt 1 ended in a provider error and is inconclusive. Attempt 2 completed: it disregarded the unrelated instructions and returned three grounded evidence connections. The private sentinel did not appear.</p><p>The strongest protection was capability separation: the analyst had no external-action tool and never received the sensitive answer. One successful attack test does not prove universal prompt-injection resistance. The recorded failure also checks that an unsuccessful run preserves the saved profile and reports an error.</p><p class="source">Evidence: browser_checks.json, injection_attempt_1.json, injection_test.json and final_tests.txt. Thirty-five offline tests now pass; earlier results remain preserved. Extension installation/import/clear was checked separately in Chromium.</p>""",
)
page(
    "10 / IMPACT",
    "Working outputs are not yet human outcomes",
    table(
        ["Measured in this build", "What the number means", "What it does not prove"],
        [
            [
                "1,383 records in the initial live snapshot",
                "Initial five-board baseline; now ten boards and a 146-record sample",
                "Complete job-market coverage or future availability",
            ],
            [
                "12 matching roles in the screenshot",
                "The stated strategy/West Coast/sector/exclusion filters ran over that snapshot",
                "Twelve roles for every profile or search",
            ],
            [
                "13 form fields filled",
                "The shared adapter populated supported fields after explicit review",
                "Minutes saved on a real Workday application",
            ],
            [
                "35 offline tests + browser workflow checks",
                "Contracts, boundaries and selected UI states were exercised",
                "Production security or every device/browser combination",
            ],
            [
                "Zero model requests on a cache hit",
                "An identical result was reused",
                "A measured monthly cache-hit rate for real applicants",
            ],
        ],
    )
    + """<h2>What this makes possible now</h2><p>A student can move from a reviewed resume to a source-grounded role discussion without copying the entire resume into a separate chat each time. They can preserve notes, understand which facts support a pivot and reuse common application answers. The practice form demonstrates a controlled bridge between a professional profile and repetitive field entry.</p><h2>The trial that is still needed</h2><p>No real applicant has completed a measured before/after trial. There is no invented testimonial, satisfaction score, time-saving percentage, interview rate or hiring claim in this report. Automated testing establishes that the workflow works on its fixtures; it does not establish that people find it faster or more trustworthy.</p><p>The next trial asks a consenting MBA applicant to find one relevant role, explain two supported connections and one unresolved requirement, save a follow-up and prepare the practice form. The same tasks should be timed manually using the same source data. Record corrections and whether the person understands the score’s limits, not just whether they reached the end.</p><p>For an MBA career office, the promising business value is more consistent applicant preparation. The current deployment is personal and local. Wider adoption would add support, privacy and security costs that the token projections do not include.</p><p class="source">Trial protocol: docs/user_trial.md. No human observations have been filled in. The original user request is recorded in AI_prompts.md.</p>""",
)
page(
    "11 / LIMITS + NEXT STEPS",
    "What I would improve next",
    """<h2>Coverage and matching</h2><p>Ten curated boards are a practical starting point, not a general job search engine. Company-sector labels are manual. Location matching uses text and can miss state abbreviations or multi-region restrictions. Unknown salary and employment type are kept explicit. The overlap score can overweight common words and cannot determine seniority, sponsorship, degree completion or legal eligibility.</p><p>The first improvement is a labeled evaluation set of realistic MBA pivots and near-miss jobs, with reviewer judgments about why each role fits or does not. Better extraction of explicit requirements should be compared against the transparent baseline before changing the score.</p><h2>Application helper</h2><p>The extension supports common labeled text inputs, text areas, exact-match select options and some repeated work-history patterns. Actual Workday tenants differ. Custom dropdowns, cross-origin frames, uploads, dates, authentication and CAPTCHA may need manual entry. There is no claim of universal Workday compatibility.</p><p>A live Pfizer MBA application was opened through Apply Manually and reached Create Account/Sign In. No account or applicant data was submitted. The next step is a permitted authenticated form test, stopping before submission. Field-level checks should expand from there. Consent, signatures and final submission should remain human decisions even if more controls become supported.</p><h2>Reliability and deployment</h2><p>One adversarial run encountered a provider error; it was visible and retryable. A production service needs a proper authentication model, encryption, retention policy, per-user quotas, multi-worker coordination and monitoring. The current global AI lock is suitable for a local prototype, not a 10,000-user deployment.</p><h2>Submission and evidence</h2><p>The user explicitly chose Astra; the assignment’s course-key Luna requirement still differs. Confirm the permitted account/configuration before submission. If the model changes, rerun the measurements instead of adjusting the label. A real user trial and public or grader-accessible repository publication are also still outstanding.</p><div class="callout"><strong>Next month, in order:</strong> observe a real applicant → improve matching from labeled cases → verify one live application adapter → harden privacy and operational controls → evaluate broader rollout. These are plans, not shipped capabilities.</div>""",
)
page(
    "12 / EVIDENCE + REPRODUCIBILITY",
    "How to check the claims",
    """<h2>Reproduce the app</h2><p>Install the pinned Python requirements in a local virtual environment. Run <code>npm ci</code> and <code>npm run build</code> inside frontend/. Put the configured key in the repository or parent .env. From backend/, run <code>uvicorn main:app --host 127.0.0.1 --port 8000</code>. Open localhost:8000.</p><p><strong>Latest local-clone rehearsal:</strong> revision df57929 installed, built and started in 10.09 seconds with warm caches; all 35 tests passed. Parent-only key discovery used a fixture and port 8771. No AI call or public-clone test. See final_clean_setup.json.</p><h2>Evidence map</h2>"""
    + table(
        ["File", "Evidence"],
        [
            [
                "output/evidence/live_runs.json",
                "Structured outputs, usage, activity and source record for the controlled run",
            ],
            [
                "output/evidence/cost_comparison.json",
                "Full versus truncated source comparison and product decision",
            ],
            [
                "output/evidence/injection_attempt_1.json / injection_test.json",
                "Both the inconclusive provider failure and the completed adversarial test",
            ],
            [
                "output/evidence/browser_checks.json",
                "Actual UI assertions, session separation and field-safety results",
            ],
            [
                "output/evidence/final_tests.txt / readiness_browser.json",
                "Current 35-test result and application-check UI; earlier baselines retained",
            ],
            [
                "output/evidence/extension_check.json",
                "Unpacked extension installation, profile import and clearing",
            ],
            ["output/screenshots/", "Original screenshots embedded in this report"],
            [
                "output/harness.md",
                "Model fields, tools, routes, limits and safety inventory",
            ],
        ],
    )
    + """<h2>Sources and disclosures</h2><p><a href="https://docs.greenhouse.io/job-board.html">Greenhouse Job Board API</a> explains the public read-only source surface. <a href="https://developers.openai.com/api/docs/models/gpt-6-astra">OpenAI Astra documentation</a> supplies the dated public rates. <a href="https://ai.pydantic.dev/agent/">PydanticAI</a> supplies structured-agent interfaces. <a href="https://revealjs.com/initialization/">reveal.js</a> powers the separate offline slide deck.</p><p>AI assisted the code and report. No application or agreement was submitted. Review the claims, model rules and final repository link before submission.</p>""",
)
css = """*{box-sizing:border-box}html{background:#e7e1e5}body{margin:0;color:#2a222a;font:11pt/1.4 Arial,sans-serif}a{color:#9b285b}code{font-size:9.5pt;overflow-wrap:anywhere}.sheet{position:relative;width:8.5in;min-height:11in;margin:24px auto;background:#fff;padding:.6in .6in .65in;box-shadow:0 3px 20px #3a203022}.kicker{font-size:9pt;letter-spacing:2px;color:#a03766;font-weight:bold;margin:0 0 18px}h1{font:38pt/1.05 Georgia,serif;letter-spacing:-1.5px;margin:0 0 24px}h2{font:18pt Georgia,serif;margin:22px 0 9px}p{margin:10px 0 14px}.subtitle{font-size:17pt;line-height:1.35}.callout{padding:15px 18px;background:#f6e8ef;border-left:4px solid #b43d70;margin:18px 0}.small,.source{font-size:9pt;line-height:1.4;color:#675760}.source{margin-top:18px}figure{margin:20px 0}figure img{width:100%;max-height:3.65in;object-fit:contain;object-position:top;border:1px solid #e5d9df}figcaption{font-size:9pt;color:#655862;margin-top:7px}table{border-collapse:collapse;width:100%;font-size:10pt;line-height:1.3;margin:18px 0}th{text-align:left;background:#30262e;color:#fff;padding:9px}td{padding:9px;border-bottom:1px solid #e2d7dd;vertical-align:top}tr:nth-child(even) td{background:#fbf6f9}.cols{display:grid;grid-template-columns:1fr 1.08fr;gap:24px}.cols h2{margin-top:12px}.portrait img{max-height:6.7in}.footer{position:absolute;bottom:22px;left:.6in;right:.6in;display:flex;justify-content:space-between;font-size:8pt;color:#786671;border-top:1px solid #e1d5db;padding-top:9px}svg{width:100%;margin:12px 0}@media print{@page{size:letter;margin:.5in}html,body{background:white}.sheet{width:7.5in;height:9.97in;min-height:0;padding:.08in .08in .4in;margin:0;box-shadow:none;break-after:page}.sheet:last-child{break-after:auto}.footer{left:.08in;right:.08in;bottom:.02in}h1{font-size:32pt;margin-bottom:18px}h2{margin-top:17px}figure{margin:14px 0}figure img{max-height:3.25in}.compact img{max-height:2.7in}.portrait img{max-height:6.2in}table{margin:12px 0}th,td{padding:8px}}@media screen and (max-width:850px){.sheet{width:100%;min-height:100vh;padding:28px 24px 70px;margin:0 0 20px}.cols{grid-template-columns:1fr}.footer{left:24px;right:24px}h1{font-size:32pt}}"""
body = "".join(
    f'<section class="sheet"><p class="kicker">{k}</p><h1>{t}</h1>{b}<div class="footer"><span>PIVOT DESK · EVIDENCE-BACKED REPORT · 25 OCT 2026</span><span>{i} / {len(sections)}</span></div></section>'
    for i, (k, t, b) in enumerate(sections, 1)
)
(R / "report.html").write_text(
    '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Pivot Desk — Final Project Report</title><style>'
    + css
    + "</style></head><body>"
    + body
    + "</body></html>"
)
# Inline reveal.js runtime: genuinely offline and movable as one HTML file.
vendor = R / "docs/vendor/reveal"
vcss = (vendor / "reveal.css").read_text()
vjs = (vendor / "reveal.js").read_text().replace("</script", "<\\/script")
slides = [
    (
        "Pivot Desk",
        '<p class="lead">MBA recruiting with evidence.<br>Application preparation with a final human say.</p><p>Qingyuan Zhang · AI Foundations for Managers</p><p class="fine">Working local prototype • October 25, 2026<br>GitHub publication and real-user trial still pending</p>',
    ),
    (
        "One pivot. Repeated work.",
        '<div class="split"><div><h3>Choose the right roles</h3><p>West Coast. Healthcare + technology.<br>Exclude investment banking.</p><p>Separate transferable evidence from missing qualifications.</p></div><div><h3>Stop retyping the basics</h3><p>Work history, education and languages.</p><p>Reuse reviewed facts.<br>Keep consent and submission manual.</p></div></div><p class="fine">Problem supplied by an MBA student. Human time savings have not yet been measured.</p>',
    ),
    (
        "The proposed difference",
        '<p class="lead">A traceable chain from resume facts<br>to a role decision and reviewed fields.</p><p>Simplify already offers application autofill.<br>Teal already offers job tracking.</p><p>Pivot Desk combines hard filters, source quotations,<br>explicit unknowns and a local review-before-fill workflow.</p><p class="fine">Not a claim of unique features or proven superiority. Sources: Simplify Copilot setup; Teal job tracker. Full links in report.</p>',
    ),
    (
        "Two bounded specialists",
        diagram()
        + '<p>Resume reader → human-confirmed facts.<br>Evidence analyst → two read-only tools → grounded review.</p><p class="fine">Filtering, scoring and filling use code. No autonomous submission, email or legal acceptance. Model: gpt-6-astra, explicitly selected by the user.</p>',
    ),
    (
        "A real role, an honest gap",
        '<div class="split demo-slide"><div>' + img(
            "discovery.png",
            "Fictional applicant; real Heartflow MBA role. 93/100 is overlap, not hiring probability.",
        )
        + '</div><div><h3>93 / 100 overlap</h3><p>Relevant research and financial modeling.</p><h3>Still unresolved</h3><p>MBA completion.<br>Exact experience months.<br>On-site work and travel.</p></div></div><p class="fine">Source checked October 25, 2026. The analyst challenged the score with concrete qualification gaps.</p>',
    ),
    (
        "Measured costs and a rejected shortcut",
        table(
            ["Mode", "Input / output", "Est. USD"],
            [
                ["Full source", "3,225 / 892", "$0.07685"],
                ["Truncated source", "2,774 / 904", "$0.07294"],
                ["Identical-result cache", "0 / 0", "$0"],
            ],
        )
        + '<p>5.09% cheaper lost a later requirement.<br><strong>Full text stays the default.</strong></p><p class="fine">One controlled pair; no provider-cached input. Public Astra rates, not the account invoice. Assumed 2 resume reads + 16 paid reviews/month ≈ $1.30/user; 100 users ≈ $130; 10,000 ≈ $13,010. Infrastructure excluded.</p>',
    ),
    (
        "Review is a real boundary",
        '<div class="split demo-slide"><div>' + img(
            "safety-closeup.png",
            "13 supported fields filled; no agreement accepted and no application submitted.",
        )
        + '</div><div><h3>13 fields filled</h3><p>Contact, work history,<br>education and language.</p><h3>0 agreements accepted</h3><p>Signature stays manual.<br>No application submitted.</p></div></div><p class="fine">35 offline tests. The completed injection test disregarded the attack; the first provider failure remains inconclusive.</p>',
    ),
    (
        "What the evidence establishes",
        '<div class="numbers"><div><strong>12</strong><span>fields filled from a private reviewed profile</span></div><div><strong>1 → 3</strong><span>correct language entries after the fix</span></div><div><strong>0</strong><span>model calls in this local test</span></div></div><p>A real resume exposed repeated-language and legal-name gaps.<br>The regression uses fictional values; personal details stay private.</p><p><strong>Not yet measured:</strong> applicant time saved,<br>authenticated Workday completion, or hiring outcomes.</p><p class="fine">Assistant-operated local check with a manually transcribed profile. Earlier evidence: 35 offline checks; 32/32 topics in 12 selected postings. Not a human trial.</p>',
    ),
    (
        "The next evidence to earn",
        '<ol><li>Observe one real MBA applicant using the workflow.</li><li>Test one permitted employer form, stopping before submission.</li><li>Improve matching with labeled near-miss roles.</li><li>Resolve the course-key restriction and publish reviewed source.</li></ol><p class="fine">User chose Astra; the brief specifies Luna on the course key. That mismatch remains disclosed. Local setup instructions and complete evidence are included; no application or message has been sent.</p>',
    ),
]
sc = """html,body,.reveal-viewport{background:#241d25!important}body{background:#241d25;color:#f8f0f4}.reveal{font-family:Arial,sans-serif;font-size:30px;color:#f8f0f4}.reveal .slides{text-align:left}.reveal h1{font:64px/1.1 Georgia,serif;color:#efabc8;letter-spacing:-1.5px;margin:0 0 36px}.reveal h3{font-size:32px;color:#efabc8;margin-bottom:20px}.reveal p{line-height:1.45;margin:22px 0}.reveal .lead{font-size:40px;line-height:1.3}.reveal .fine{font-size:19px;color:#ccb8c5;line-height:1.4}.reveal table{width:100%;border-collapse:collapse;font-size:27px;margin:20px 0}.reveal td,.reveal th{padding:14px;border-bottom:1px solid #796773;text-align:left}.reveal th{color:#efabc8}.reveal figure{margin:0}.reveal img{max-width:100%;max-height:470px;object-fit:contain;background:#fff;border:1px solid #705364}.reveal figcaption{font-size:19px;line-height:1.3;color:#ccb8c5;margin-top:8px}.split{display:grid;grid-template-columns:1fr 1fr;gap:65px}.demo-slide{grid-template-columns:1.3fr 1fr;gap:48px}.demo-slide img{max-height:450px}.numbers{display:flex;gap:45px;margin:50px 0}.numbers div{flex:1}.numbers strong{display:block;font:82px Georgia;color:#efabc8}.numbers span{display:block;font-size:24px;margin-top:12px}.reveal li{padding:10px 0;line-height:1.3}.reveal svg{width:100%;background:#fff;border-radius:6px;max-height:350px}.reveal .controls{color:#efabc8}.reveal .progress{color:#efabc8}.reveal .slide-number{font:15px Arial;background:#241d25;color:#efabc8}.reveal a{color:#efabc8}"""
slidebody = "".join(f"<section><h1>{t}</h1>{b}</section>" for t, b in slides)
(R / "slides.html").write_text(
    '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Pivot Desk — Final Project Slides</title><style>'
    + vcss
    + "\n"
    + sc
    + '</style></head><body><div class="reveal"><div class="slides">'
    + slidebody
    + "</div></div><script>"
    + vjs
    + '</script><script>Reveal.initialize({width:1200,height:780,margin:0.06,hash:true,slideNumber:true,transition:"fade",center:false,controls:true,progress:true});</script></body></html>'
)
print("Built", len(sections), "report sections and", len(slides), "reveal.js slides.")
