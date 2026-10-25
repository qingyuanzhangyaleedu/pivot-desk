# Final Project - AI Prompt Log

Record one section for each working task, with a number/title, the actual prompt,
any follow-up prompts, and an outcome after the work is done. Preserve the user's
wording; label paraphrases. Do not invent prompts, record secrets, or mark planned
features as completed. Task numbers here track our work, not numbered questions in
the assignment PDF.

## Task 1 - Read the final-project brief and prepare the workspace

**Date:** 2026-10-24

**User prompt (as provided):**

> This is the final project. Make sure you take ur time to understand it and set up the group work like we did before. I will be brainstorming the idea on what we will be doing.

**Attachment:** `Final Project - AI Foundations for Managers.pdf`, copied unchanged
to `docs/assignment_brief.pdf` for local reference.

**Outcome:** Read the full brief and visually checked its sections. Created the
`final_project` folder, local `.venv`, requirements checklist, project plan, prompt
log, starter harness, README and ignore rules. Recorded the solo-submission rule,
deadline, evidence requirements and model/key conflict. The project idea,
architecture and model configuration remain undecided while the user brainstorms.

**Follow-up prompt (as provided):**

> can you set it up like the previous hw structure-wise? like the md files and other stuff

**Follow-up outcome:** Compared HW3, HW4 and HW5, then aligned the project with the
familiar `backend/prompts/`, `frontend/`, `data/`, `tests/` and `output/` folders.
Added a placeholder-only `.env.example`, starter `design.md`, `usability.md` and
`agent_evaluation.md` notes, and screenshot/evidence folders. Updated the README
and harness to describe the structure. Reused the existing local Python environment.
The app-specific files, dependencies and runtime model remain undecided.

## Future tasks

Append new numbered tasks here as work is requested. Keep real tests and outputs
as the evidence supporting each completed outcome.

## Task 2 — Build an MBA recruiting and application workspace

**User prompt (as provided):**

> I am a current MBA student - I want to build a thing that can Help me with recruiting and application processes. For example I want to have a component that scraps/searches web that should first match my resume (maybe give it a job a match score) and also offer a chance to input would I'd like to filter in/out i.e maybe for me I want to focus on westcoast jobs in healthcare and technology and prbably not Investment banking. feel free to also include other features here. Also I want to have this project have something that fills the annoying part of every single application which is fill out the workday thing (previous jobs, language spoken, veteran status, sign data collection agreement. you know what I am talking about) When you are working on this make sure you keep in mind that while we want to make this work we are also completing a project for school so it needs to score as many points as possible so you need to make sure things are documented/created to satisfies the grading criteria. I am going to sleep tonight. please work this

**Follow-up prompt (as provided):**

> it should be a function - a user should be able upload his/her resume

**Outcome:** Implemented Pivot Desk with resume upload/review, five public employer feeds, preference filters, reproducible overlap scoring, a tool-using evidence analyst, private pipeline, usage ledger and a review-before-fill browser helper. Built a fictional demo and tested the real public-data workflow. Agreements, signatures and final application submission remain manual. Detailed evidence and remaining submission decisions are documented; no real-user trial or universal Workday compatibility is claimed. Model choice still conflicts with the assignment: the current explicit workspace instruction uses Astra, while the course-key brief requires Luna. See README.

**Model-choice follow-up (as provided):**

> Keep gpt-6-astra from my workspace instructions

**Outcome:** Retained gpt-6-astra and its actual measured costs. Documented that this user-selected configuration differs from the course-key model restriction.

## Task 3 — Expand the career areas for a Yale SOM MBA student

**User prompt (as provided):**

> I like the fact that you did healthcare and technology maybe add a few that pertains an MBA student at Yale SOM

**Outcome:** Added Consulting, Finance & Fintech, Consumer & Retail, and Climate & Sustainability filters backed by five additional public employer boards. Added title-keyword shortcuts for MBA career searches, preserved existing preferences and exclusions, and expanded the real offline job sample. The selections were informed by Yale SOM’s career reporting and business/environment career resources; no Yale affiliation or eligibility guarantee is implied.

## Task 4 — Keep the project documentation complete as it develops

**User prompt (as provided):**

> and make sure that you update the files and docs along the way so that the project is complete

**Outcome:** Reconciled current source and test counts across the README, evaluation, design notes, grading checklist and report/deck generator. Preserved earlier measurements as historical evidence. Added an ongoing document-maintenance checklist and a reproducible offline artifact check. Outstanding user testing, employer-form validation and submission items remain explicit; they are not marked complete without evidence.

## Task 5 — Evaluate the project against the grading scheme

**User prompt (as provided):**

> can you evaluate according the grading scheme how much this project can score

**Outcome:** Re-read the original rubric and inspected the current code, report, slides and saved evidence. Saved a category-by-category estimate and prioritized gaps in `output/grading_review.md`. The estimate is conditional and not an instructor grade. No model configuration was changed, no new applicant results were invented, and nothing was published or submitted.

## Task 6 — Improve the project and prepare submission

**User prompt (as provided):**

> improve it to the best ability that you can. Prepare everything needed for a successful submission

**Outcome:** Added source-based application checks beside the match score and an explicit title-only exclusion option. Improved reviewed application-name fields, repeated education mapping, accessible labels and protection against dynamic field replacement. Expanded automated tests and recorded a real public Workday account boundary without creating an account. Prepared a timed real-user worksheet, reproducible benchmark, captioned demonstration and submission materials. Human-outcome evidence, authenticated Workday compatibility and the previously selected model/account exception are not fabricated or silently marked complete.

**Publication follow-up (as provided):**

> can you keep preparing local for now

**Outcome:** Kept the repository and submission package local. No GitHub repository was created and no files were published or submitted. The source ZIP is ready for later publication; the required repository URL remains pending by request.

## Task 7 — Private resume test and final submission polish

**User prompt (as provided):**

> You can feel free to review it for me. You can use this resume of mine to test things out. make sure things are looking great for final submission. Again do not upload just yet just make sure things are good to go and we can score as many points as we can. Keep in mind the report and powerpoint slide deck]

**Outcome:** Reviewed the supplied resume privately and exercised the local parser, reviewed profile, search and form helper. Corrected repeated-language mapping and left legal-name questions manual. Added anonymized evidence to the report and slide deck, and prepared a local PowerPoint companion. Personal source text and screenshots remain excluded from the submission package. No repository or coursework was published; local assistant-operated checks are not presented as a human trial or live AI extraction.

**AI-processing follow-up (as provided):**

> Allow AI processing; keep publication on hold

**Outcome:** Ran a live PDF extraction and fit reviews through the configured provider after consent. Reviewed the extracted facts, verified source quotations, tested cache reuse and used the real AI profile in the local form lab. Fixed a search-response race discovered during testing, preserving the extra paid review and its cost in the evidence. Report, HTML slides and an updated PowerPoint copy include aggregate results only. Publication remains on hold; private resume and detailed outputs are excluded.

## Final submission preparation
**Prompt:** “Okay I am ready to submit the project. similar to what we’ve done for hw3, hw4, hw5. just follow the instructions in the pdf.”

**Follow-up:** “it doesn’t matter. the professor said during the class that it can be whatever” (model choice).

**Work:** Reread the brief; retained Astra based on the reported clarification; prepared public GitHub source, repository links, offline report/deck and a fresh remote-clone check. Kept private resumes, personal runtime data and credentials excluded. Canvas upload is a separate final step.
