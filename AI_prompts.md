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
