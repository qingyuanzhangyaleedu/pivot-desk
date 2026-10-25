# Working usability improvements

## Review a resume once
Upload PDF, DOCX or TXT, or paste text in My evidence. The extractor returns a draft with source quotations. Edit contact details and fact types, then confirm the profile. This reduces repeated entry while keeping invented credentials out of the approved record. Scanned PDFs return a readable error; OCR is not included.

## Search a career pivot explicitly
Discovery has title keywords, location groups/custom cities, company sector, exclusions, job type and a published-salary threshold. Filters run before scoring. A score breakdown and a separate AI assessment let the applicant distinguish transferable experience from an unsupported qualification. Search `strategy` for the demo and inspect the Heartflow MBA role.

## Keep a private pipeline
Save a job, set its stage, add a note and a follow-up date. A reload preserves the same browser’s state. Another browser session sees none of those records. Changing to Applied is only a personal record; it sends nothing.

## Preview repetitive application answers
Application kit exports the reviewed profile and offers the browser helper. The practice lab demonstrates 13 ordinary fields filled after review. Sensitive answers begin unchecked; agreements and signatures remain manual; differing existing answers are protected. This is tested functionality on a controlled form, not a claim that every Workday tenant is supported.

## Make delays and spending visible
The agent notebook shows real tool activity while an analysis runs. Usage & proof displays actual input, cached-input and output tokens, estimated costs, cache hits and limits. Identical reviewed profile/job/prompt requests reuse a result. A failed model call leaves the saved profile intact and gives a retryable error.

## User testing status
Automated browser checks are recorded in `output/evidence/browser_checks.json`. They are not human feedback. No applicant has yet completed a recruiting trial, and no hiring, time-saving percentage or satisfaction claim has been invented.

## Broader MBA career choices
Company sector now offers four additional areas with real source feeds: Consulting, Finance & Fintech, Consumer & Retail, and Climate & Sustainability. Click a role shortcut to search for MBA, consulting, finance, brand/growth or climate/energy titles. The shortcut keeps the user's geography, sector and exclusions. The existing healthcare/technology focus remains the starting point.

## Check an application before investing time
Each selected role has a “Check before applying” panel with the employer's actual degree, experience and other screening language. A high skill-overlap score cannot erase those questions. The applicant can also scope excluded phrases to titles instead of entire descriptions, preserving consulting roles that mention banking experience while still filtering banking job titles. Both changes work without model calls.

## Keep application names and education accurate
The reviewed profile accepts optional given/family names directly. The helper uses those values without splitting names and maps separate education sections to separate records. It rechecks every target field after earlier change events so dynamic forms cannot redirect an old approval to a replaced field. Controlled DOM tests cover these behaviors; a real employer's authenticated application remains unverified.
