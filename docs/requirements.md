# Final-project requirements and grading checklist

Source: the supplied assignment brief (private local copy: `docs/assignment_brief.pdf`, excluded from Git), reviewed in full on
October 24, 2026. Updated October 25 after implementation. Checked items describe verified artifacts; the final report and deck include the repository link. Canvas upload remains outstanding.

## Submission

This is a **solo project**. AI assistance is allowed; the student is responsible
for the accuracy of every word and number submitted.

Due: **Monday, October 26, 2026 at 6:00 PM on Canvas**. The PDF does not state a time
zone; confirm the course deadline in Canvas.

- [x] Public GitHub repository URL visibly linked inside both the report and slides.
- [ ] Upload only `report.html` and `slides.html` to Canvas (testing video optional).
      The October 25 instructor announcement replaces the separate website-URL
      submission step. No PowerPoint, ZIP, URL text file or other extras.
      A private repository would need its status stated in both files and grader access; ours is public.
- [x] `report.html`: one HTML file, 10-15 normal letter-size printed pages,
      including screenshots, with regular readable text and no filler.
- [x] `slides.html`: one HTML file using reveal.js, at most 10 slides.
- [x] Both HTML files open by double-clicking, with screenshots and diagrams
      embedded in the files so they do not disappear when moved or emailed.
- [ ] Optional: a 2-3 minute narrated screen recording of a real end-to-end run.

The optional video may support the "It works" and "Look + feel" points if the app
does not run for graders; it cannot replace the 5 setup points.

## Application and repository

- [x] Solve a useful, concrete problem for identifiable real people.
- [x] Implement an end-to-end workflow with real tools, data and useful outputs.
- [x] Explain each agent and tool; use multiple agents only when justified.
      The brief does not require five agents, MCP, React, FastAPI, a database or
      every feature from the homework assignments.
- [x] Include all code needed to run the app and a step-by-step README.
- [x] Include a small test dataset if the real dataset is large, with instructions
      for switching between demo and full data.
- [x] Include `.env.example` with placeholders and every required key name.
- [x] Exclude real `.env` files and keys from commits, including Git history.
- [x] Choose either an online app that remains available until grades are posted,
      or a local app that works from a fresh clone using the README.
- [ ] If online, put the app URL at the top of the README and report and check it
      on submission day, including any host sleep behavior.
- [x] Timed the initial local Git clone: 9.84 seconds with warm caches; see
      `output/evidence/clean_setup.json`. Recheck the final published version.
      **More than 10 minutes without a running app earns zero of the 5
      "teaching staff can run it" points.**
- [x] Search for `.env` first in the repository root, then one directory above it.
- [x] Test the grader's arrangement with the key file only in the parent folder.
- [ ] If an additional API key beyond the permitted names is needed, the brief
      says to host the app online and consult the professor.

## Model and key constraints

| Option in the brief | Key name | Model rule |
| --- | --- | --- |
| Course account | `PORTKEY_API_KEY` | `gpt-6-luna` only; no other model on the course key. |
| Personal paid account | `OPENAI_API_KEY` for OpenAI | A different model is allowed at the student's own expense. |

The teaching staff's parent `.env` contains `PORTKEY_API_KEY` and `OPENAI_API_KEY`.
Use the exact applicable name. List only the keys the finished application needs.

**User decision:** On October 25, the user explicitly selected `gpt-6-astra` with the existing workspace account. The code and measured evidence follow that instruction. Before publication, the user reported that the instructor allowed any model in class and retained Astra. The printed restriction above remains documented as written; the later clarification is attributed to the user.

## Report sections, in the required order

| Section | Required content | Evidence to collect |
| --- | --- | --- |
| 1. Title + links | Project and student names, repo URL, online app URL if applicable, and a one-sentence explanation. | Final verified links and actual app behavior. |
| 2. Motivation | Who has the problem, how it is handled today, and the cost in time, money or frustration. | A specific user/workflow and sourced baseline. |
| 3. What is new here | Existing apps, startups and ChatGPT alternatives; an honest account of the meaningful difference. | Named existing products and comparisons. Research after the idea is chosen. |
| 4. The agents | Each agent's role and tools, organization/delegation diagram where applicable, model choice and rationale. | One real run traced step by step with screenshots of agent activity. |
| 5. Tokenomics | Measured input, cached input and output tokens; cost/run; cost/user/month; cost at 100 and 10,000 users; cost controls and any quality trade-off. | Real usage logs or screenshots, dated model prices, explicit volume assumptions, and a before/after comparison for cost changes. |
| 6. Safety | Relevant prompt-injection/data-leak risks, invented facts or wrong actions, runaway loops and token overspending; implemented defenses. | At least one test or screenshot showing a defense actually stopping an attack or malfunction. Distinguish code enforcement from prompt instructions. |
| 7. Impact | Measurable time, cost, turnaround, quality, reach or newly possible work; identify the source of every number. | A real user trial, quote, screenshot or measured before/after result. Label estimates separately. |
| 8. Limits + next steps | What does not work and what another month would enable. | Actual failures, limitations and prioritized improvements. |

Write for a smart manager who has not seen the app. Make the report match what
was built and tested. For report rows with specified evidence, missing that
evidence limits the row to at most half credit.

## Slide deck

The brief suggests this sequence (nine slides, with a maximum of ten): title;
problem/user; novelty; agent diagram; demo screenshots; cost; safety; impact
numbers; next steps. Use reveal.js, readable large text and a consistent visual
style. Test every slide with the arrow keys and fullscreen with F.

The example in the brief loads reveal.js from a CDN while requiring embedded
screenshots and diagrams. For dependable offline delivery, our proposed packaging
is to embed the required reveal.js code/styles as well. This is a proposed
implementation choice, not an additional quoted grading rule. The nine-slide deck is built and tested offline.

## Rubric: 100 points

| Area | Component | Points |
| --- | --- | ---: |
| Idea | Novelty + real-world value | 21 |
| App | It works | 15 |
| App | Teaching staff can run it | 5 |
| App | Look + feel | 10 |
| Report | Motivation + what is new | 8 |
| Report | Agent design | 10 |
| Report | Tokenomics | 8 |
| Report | Safety | 8 |
| Report | Impact + metrics | 5 |
| Report | Design | 2 |
| Slides | Content | 6 |
| Slides | Design | 2 |
| **Total** | | **100** |

Tier 1 is a working familiar idea with a basic report. Tier 2 adds a thoughtful,
distinctive idea and design, measured costs, real safety evidence and screenshots.
Tier 3 adds a convincing real-world improvement supported by actual user/testing
evidence and consideration of organizational costs. No grade is guaranteed.

The brief identifies these as overdone without a substantive twist: resume/cover
letter reviewers, chat with documents, travel planners, email/meeting summaries,
meal planners, generic study/flashcard tools, and a class/homework app without a
real new addition. Their **idea** is capped at Tier 1 without that new contribution.

## Final evidence checks

- [x] Current feature counts match code; screenshots and measurements from the
      initial baseline are identified as historical rather than presented as new runs.
- [x] Measured values are separated from assumptions and future plans.
- [ ] A real user trial is documented without fabricated quotes or results.
- [x] Token costs are derived from real usage; cached tokens are not double-counted.
- [x] One or more relevant safety defenses are demonstrated, not merely described.
- [x] Both HTML files remain complete when copied away from the project folder.
- [x] Report print preview is 10-15 letter-size pages; deck has no more than 10 slides.
- [x] Local Git clone, parent-folder key discovery and README startup steps tested; public GitHub-clone startup, parent dotenv discovery, all 35 tests and one live fictional-profile review now pass; see `remote_clean_setup.json`.
- [x] Final repository link is public; staged files and Git history passed credential/private-value scans.

## Current handoff

Report: 15 letter-size printed pages. Deck: 9 offline reveal.js slides. Application: working local prototype with live model runs and automated evidence. Outstanding evidence limits: independent applicant trial and authenticated employer Workday test. The user reported an instructor model clarification. Repository publication is complete; the final Canvas upload remains a student step. No video or human testimonial has been fabricated.

Current verification: 10 boards, 6 sectors, 146 bundled source records, and 35 passing offline tests. The source-expansion browser results are in `output/evidence/sector_browser.json`. Report/deck image loading, layout and navigation checks are in `output/evidence/artifact_validation.json`. `docs/project_plan.md` tracks the remaining completion work.
