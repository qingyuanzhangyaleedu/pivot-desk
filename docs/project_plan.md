# Pivot Desk implementation status

The chosen user is an MBA applicant making an industry or geographic pivot. The core workflow is resume upload → human review → public-job filters → evidence-based fit review → tracked application preparation. The app deliberately separates the user’s facts from an employer’s claims and keeps submission and consent under the applicant’s control.

| Area | Status |
| --- | --- |
| React / FastAPI app | Built and browser-tested locally |
| PDF, DOCX and TXT resume parsing | Built; readable text required, no OCR |
| Structured AI extraction and fit review | Real runs recorded with fictional applicant data |
| Live source adapters | Five public Greenhouse boards; private posting import for other sources |
| Application helper | Shared adapter tested in local lab; extension supplied; actual employer Workday compatibility remains unverified |
| Privacy / safety tests | Offline isolation, consent, input and quote checks; browser field-safety checks |
| Cost evaluation | Full vs truncated source comparison plus identical-result cache test |
| Report and slides | Evidence-backed local drafts; not a completed submission |
| Actual applicant trial | Still needed; automated tests do not substitute for it |
| Course model restriction | User confirmed Astra; the course-key Luna restriction remains a known submission conflict |
| GitHub publication and Canvas submission | Not performed |

Next priorities are a real applicant trial, testing one permitted employer application page without submitting, resolving the model/account requirement, updating measurements if the model changes, and publishing the reviewed source repository. No human teammate has been assigned or contacted.
