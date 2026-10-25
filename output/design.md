# Pivot Desk design

The app looks like a personal recruiting desk: near-black plum navigation, pale paper surfaces and a strong rose-pink accent. DM Serif Display gives the major headings a printed-editorial feel; DM Sans keeps forms and job details readable. Fonts ship locally, so the interface does not call a font CDN.

A fixed desktop sidebar separates discovery, reviewed evidence, application preparation, pipeline and measured usage. Job cards sit beside an evidence panel. Employer initials, source dates and plain pay labels make provenance visible. The score is accompanied by its three components and a warning that it is not a hiring probability. A fictional-profile strip stays visible during demonstrations.

Pink indicates a selected card or primary action; text, borders, check marks and labels carry the same meaning without depending on color. Loading bars and a short agent activity feed show progress. Focus rings are visible, and reduced-motion preferences disable movement. Smaller screens collapse navigation and stack the panels without horizontal scrolling.

The application kit uses a paper-form motif, with manual consent visually separated from reusable facts. The private-data deletion control and usage ledger remain easy to find. Screenshots in `output/screenshots/` come from the running app, including a 390-pixel viewport check.

Company-sector chips now show six choices, with check marks and pressed states for selected sectors. Small role-focus buttons sit immediately below the search box; they reuse the applicant’s existing filters. Both rows wrap on narrow screens. A short note explains that company sector does not establish MBA eligibility, and the exclusion field explains that it scans descriptions too. Current desktop and mobile examples: `screenshots/mba-sectors.png` and `screenshots/mba-sectors-mobile.png`.

The selected-role panel now places “Check before applying” immediately after the overlap breakdown. A pale pink background distinguishes these questions from the numerical score. Each compact disclosure shows its exact employer excerpt on demand; “Review” text avoids implying pass/fail. The panel and expanded exclusion selector wrap on a 390-pixel screen. The existing score is unchanged, making the distinction between similarity and qualifications visible.
