"""Public-board adapters, reproducible scoring and memory-only document parsing."""

import asyncio, html, re, io, zipfile, hashlib
from datetime import datetime, timezone
from html.parser import HTMLParser
from xml.etree import ElementTree
import httpx
from pypdf import PdfReader
from .models import Job, Profile, Preferences, ApplicationCheck
from . import storage

BOARDS = [
    {"slug": "heartflowinc", "company": "Heartflow", "industry": "Healthcare"},
    {"slug": "oscar", "company": "Oscar Health", "industry": "Healthcare"},
    {"slug": "figma", "company": "Figma", "industry": "Technology"},
    {"slug": "airbnb", "company": "Airbnb", "industry": "Technology"},
    {"slug": "stripe", "company": "Stripe", "industry": "Technology"},
    {
        "slug": "thebrattlegroup",
        "company": "The Brattle Group",
        "industry": "Consulting",
    },
    {
        "slug": "tworoadsconsulting",
        "company": "Two Roads Consulting",
        "industry": "Consulting",
    },
    {"slug": "chime", "company": "Chime", "industry": "Finance & Fintech"},
    {"slug": "quince", "company": "Quince", "industry": "Consumer & Retail"},
    {
        "slug": "clearwayjobs",
        "company": "Clearway Energy",
        "industry": "Climate & Sustainability",
    },
]
INDUSTRIES = list(dict.fromkeys(board["industry"] for board in BOARDS))
MAX_SOURCE_BYTES = 6500000


class PlainText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        if tag in ("p", "li", "div", "br", "h2", "h3"):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def clean_html(value):
    parser = PlainText()
    parser.feed(html.unescape(value))
    return re.sub(
        r"[ \t]+", " ", re.sub(r"\n\s*\n+", "\n", "".join(parser.parts))
    ).strip()


def classify_type(text):
    if re.search(r"\bintern(?:ship)?\b", text, re.I):
        return "internship"
    if re.search(r"full[- ]time", text, re.I):
        return "full-time"
    return "unknown"


def salary(text):
    # Only explicit USD ranges with an annual/base salary context; no hourly conversion.
    m = re.search(
        r"(?:salary|annual|base pay|base compensation)[^\n]{0,140}?\$([\d,]+)\s*(?:-|–|—|to)\s*\$?([\d,]+)",
        text,
        re.I,
    )
    if not m:
        return None, None
    low, high = [int(v.replace(",", "")) for v in m.groups()]
    return (low, high) if 20000 <= low <= high <= 1500000 else (None, None)


_refresh_lock = asyncio.Lock()
_last_refresh = None


async def refresh_jobs():
    global _last_refresh
    async with _refresh_lock:
        if (
            _last_refresh
            and (datetime.now(timezone.utc) - _last_refresh).total_seconds() < 900
        ):
            return {
                "sources": [],
                "cached": True,
                "message": "Employer refresh cached for 15 minutes.",
            }
        semaphore = asyncio.Semaphore(3)
        async with httpx.AsyncClient(
            timeout=20,
            follow_redirects=False,
            headers={"User-Agent": "PivotDesk-course-project/1.0"},
        ) as client:

            async def fetch(board):
                async with semaphore:
                    try:
                        # Fixed host and curated board slug: no user-controlled URL or redirects.
                        url = f"https://boards-api.greenhouse.io/v1/boards/{board['slug']}/jobs"
                        async with client.stream(
                            "GET", url, params={"content": "true"}
                        ) as r:
                            r.raise_for_status()
                            parts = []
                            size = 0
                            async for chunk in r.aiter_bytes():
                                size += len(chunk)
                                if size > MAX_SOURCE_BYTES:
                                    raise ValueError("Source exceeded size cap")
                                parts.append(chunk)
                        import json

                        raw = json.loads(b"".join(parts))
                        jobs = []
                        for row in raw.get("jobs", [])[:1000]:
                            description = clean_html(row.get("content", ""))[:14000]
                            low, high = salary(description)
                            j = Job(
                                id=f"gh:{board['slug']}:{row['id']}",
                                title=row["title"],
                                company=board["company"],
                                industry=board["industry"],
                                location=row.get("location", {}).get(
                                    "name", "Not stated"
                                ),
                                description=description,
                                url=row["absolute_url"],
                                source="Greenhouse / " + board["slug"],
                                retrieved_at=storage.now(),
                                updated_at=row.get("updated_at"),
                                job_type=classify_type(
                                    row["title"] + " " + description
                                ),
                                salary_min=low,
                                salary_max=high,
                            )
                            jobs.append(j.model_dump())
                        # Replace successful boards, removing closed jobs. Keep failures explicitly stale.
                        with storage.db() as c:
                            old = [
                                r[0]
                                for r in c.execute(
                                    "SELECT id FROM jobs WHERE id LIKE ?",
                                    ("gh:" + board["slug"] + ":%",),
                                )
                            ]
                            for ident in old:
                                c.execute("DELETE FROM jobs WHERE id=?", (ident,))
                        storage.save_jobs(jobs)
                        return {
                            "company": board["company"],
                            "status": "ok",
                            "count": len(jobs),
                            "retrieved_at": storage.now(),
                        }
                    except (httpx.HTTPError, ValueError, KeyError, TypeError) as e:
                        return {
                            "company": board["company"],
                            "status": "unavailable",
                            "count": 0,
                            "error": type(e).__name__,
                            "message": "Previous snapshot retained; check the employer link.",
                        }

            results = await asyncio.gather(*(fetch(b) for b in BOARDS))
        if any(r["status"] == "ok" for r in results):
            _last_refresh = datetime.now(timezone.utc)
        return {"sources": results, "cached": False}


STOP = {
    "the",
    "and",
    "for",
    "with",
    "that",
    "this",
    "you",
    "your",
    "our",
    "are",
    "will",
    "from",
    "have",
    "has",
    "was",
    "were",
    "not",
    "can",
    "all",
    "their",
    "they",
    "into",
    "more",
    "work",
    "team",
    "role",
    "years",
    "year",
    "experience",
    "about",
    "such",
    "other",
    "across",
    "within",
    "including",
    "ability",
    "skills",
    "working",
    "business",
    "new",
    "job",
    "would",
    "should",
    "must",
    "which",
    "than",
    "also",
    "both",
}


def tokens(s):
    return {w for w in re.findall(r"[a-z][a-z0-9+]{2,}", s.lower()) if w not in STOP}


REGIONS = {
    "West Coast": [
        "california",
        "oregon",
        "washington",
        "san francisco",
        "san diego",
        "los angeles",
        "seattle",
        "portland",
        "san jose",
        "palo alto",
        "menlo park",
        "redwood city",
        "bellevue",
        "sunnyvale",
        "mountain view",
        "oakland",
        "san mateo",
        "south san francisco",
        "rohnert park",
    ],
    "East Coast": [
        "new york",
        "boston",
        "massachusetts",
        "connecticut",
        "new haven",
        "washington dc",
        "district of columbia",
        "philadelphia",
        "virginia",
        "maryland",
    ],
}


def eligible(job, prefs):
    text = (
        job["title"]
        if prefs.exclude_scope == "title_only"
        else job["title"] + " " + job["description"]
    ).lower()
    loc = job["location"].lower()
    reasons = []
    for word in prefs.exclude:
        if word.strip() and word.lower() in text:
            reasons.append("Excluded phrase: " + word)
    if prefs.industries and job["industry"] not in prefs.industries:
        reasons.append("Industry outside preference")
    if prefs.regions:
        in_region = False
        for region in prefs.regions:
            region_loc = loc
            if region == "West Coast":
                # Washington, D.C. is not Washington state; other listed cities
                # can still qualify a posting with multiple office locations.
                region_loc = re.sub(
                    r"\bwashington(?:,\s*|\s+)(?:district of columbia|d\.?\s*c\.?)\b",
                    "",
                    loc,
                )
            in_region |= any(
                re.search(r"(?<!\w)" + re.escape(term.lower()) + r"(?!\w)", region_loc)
                is not None
                for term in REGIONS.get(region, [region])
            )
        us_remote = bool(
            re.search(r"remote", loc)
            and re.search(r"united states|\busa\b|\bu\.?s\.?\b", loc)
        )
        if not in_region and not (prefs.remote_ok and us_remote):
            reasons.append("Location outside preference (remote geography not assumed)")
    if prefs.job_type != "any" and job["job_type"] != prefs.job_type:
        reasons.append("Employment type not confirmed")
    if prefs.minimum_salary and (
        job.get("salary_min") is None or job["salary_min"] < prefs.minimum_salary
    ):
        reasons.append(
            "Published salary lower bound does not meet filter or is unknown"
        )
    if prefs.query.strip() and not (tokens(prefs.query) & tokens(job["title"])):
        reasons.append("No role keyword match")
    return reasons


CHECK_PATTERNS = [
    (
        "degree",
        "Degree and graduation timing",
        r"\bMBA\b|\bPh\.?D\.?\b|\b(?:bachelor|master|doctoral)[’'s]*\s+(?:degree|of)|graduat(?:ion|ing)\s+(?:date|between|in|by)",
        "Does your degree or expected graduation date match this wording? A candidate is not yet a graduate.",
    ),
    (
        "experience",
        "Experience and seniority",
        r"\b\d+\s*(?:[-–]\s*\d+|\+)?\s*(?:years?|yrs?)\b[^\n.;]{0,95}\bexperience\b",
        "Which experience qualifies, and can you verify the exact months? Overlapping roles should not be counted twice.",
    ),
    (
        "license",
        "Professional credentials",
        r"\b(?:licensed|licensure|registered nurse|active.{0,30}license|bar admission|admitted to.{0,30}bar|CPA|CFA|board.certified)\b",
        "Is this required or preferred, and do you hold the stated credential? A transferable skill does not establish licensure.",
    ),
    (
        "location",
        "Work arrangement",
        r"\b(?:on[ -]?site|in[ -]person|hybrid|relocat\w*|\d+\s+days?\s+(?:a|per|each)\s+week|remote.{0,35}(?:only|within|residen))\b",
        "Can you meet this location or attendance condition? A remote label alone does not establish state eligibility.",
    ),
    (
        "travel",
        "Travel expectations",
        r"\b(?:travel|traveling|travelling)\b",
        "What travel does the role require, and does it fit your availability?",
    ),
    (
        "authorization",
        "Work authorization wording",
        r"\b(?:sponsorship|work authoriz\w*|authoriz\w*.{0,20}work|security clearance)\b",
        "Read the employer wording and answer personally. We do not infer citizenship, authorization or sponsorship needs.",
    ),
]


def application_checks(job):
    """Surface up to six exact-source checks at zero model cost; never decide eligibility.

    This conservative keyword screen includes preferred and conditional wording.
    It does not establish that a condition is mandatory or that the applicant meets it.
    """
    description = job["description"]
    checks = []
    for kind, label, pattern, question in CHECK_PATTERNS:
        candidates = []
        for match in re.finditer(pattern, description, re.I):
            start = max(
                description.rfind("\n", 0, match.start()),
                description.rfind(". ", 0, match.start()) + 1,
                0,
            )
            stops = [
                p
                for p in (
                    description.find("\n", match.end()),
                    description.find(". ", match.end()),
                )
                if p >= 0
            ]
            end = min(stops) + 1 if stops else len(description)
            start = max(start, match.start() - 220)
            quote = description[start : min(end, start + 700)].strip()
            if (
                kind == "travel"
                and re.search(
                    r"travel (?:credits|reimbursement)|travel.{0,20}stipend",
                    quote,
                    re.I,
                )
                and not re.search(
                    r"required|willing|ability to travel|expected|\d+\s*%", quote, re.I
                )
            ):
                continue
            # Prefer qualification wording to introductory copy. This is still
            # a review prompt, never a claim that a condition is mandatory.
            priority = len(
                re.findall(
                    r"required|must|minimum|before the start|accredited|enrolled|graduat|\d+\+? years",
                    quote,
                    re.I,
                )
            )
            candidates.append((priority, quote))
        if not candidates:
            continue
        quote = max(candidates, key=lambda item: item[0])[1]
        checks.append(
            ApplicationCheck(
                kind=kind, label=label, source_quote=quote, question=question
            ).model_dump()
        )
    return checks


def rank(job, profile, prefs):
    facts = profile.get("facts", []) if profile else []
    job_words = tokens(job["title"] + " " + job["description"])
    query = tokens(prefs.query)
    matches = []
    skills = set()
    relevant = set()
    for f in facts:
        words = tokens(f["title"] + " " + f.get("description", ""))
        overlap = sorted(words & job_words)
        if overlap:
            matches.append(
                {"fact_id": f["id"], "title": f["title"], "terms": overlap[:8]}
            )
            relevant |= set(overlap)
        if f["kind"] == "skill":
            skills |= words
    if not facts:
        return {
            "application_checks": application_checks(job),
            "score": None,
            "breakdown": {},
            "evidence": [],
            "matched_terms": [],
            "label": "Add a reviewed resume to score fit",
        }
    skill_points = round(50 * len(skills & job_words) / max(1, len(skills)))
    experience_points = round(
        30
        * min(
            len(
                [
                    m
                    for m in matches
                    if next(f["kind"] for f in facts if f["id"] == m["fact_id"])
                    in ("experience", "education")
                ]
            ),
            3,
        )
        / 3
    )
    focus_points = (
        round(20 * len(query & tokens(job["title"])) / max(1, len(query)))
        if query
        else 20
    )
    return {
        "application_checks": application_checks(job),
        "score": min(100, skill_points + experience_points + focus_points),
        "breakdown": {
            "resume_skills": skill_points,
            "transferable_evidence": experience_points,
            "role_focus": focus_points,
        },
        "evidence": matches[:6],
        "matched_terms": sorted(relevant)[:16],
        "label": "Evidence overlap / 100 · not a hiring probability",
    }


def extract_document(data, name):
    if len(data) > 4 * 1024 * 1024:
        raise ValueError("Resume exceeds the 4 MB limit.")
    suffix = name.lower().rsplit(".", 1)[-1]
    if suffix == "pdf":
        reader = PdfReader(io.BytesIO(data))
        if reader.is_encrypted:
            raise ValueError("Unlock the PDF first, or paste the resume text.")
        if len(reader.pages) > 15:
            raise ValueError("Upload a resume of 15 pages or fewer.")
        text = "\n".join(p.extract_text() or "" for p in reader.pages)
    elif suffix == "docx":
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            if sum(x.file_size for x in z.infolist()) > 12 * 1024 * 1024:
                raise ValueError("Expanded document exceeds the limit.")
            xml = z.read("word/document.xml")
            if b"<!DOCTYPE" in xml or b"<!ENTITY" in xml:
                raise ValueError("Unsupported document XML.")
            doc = ElementTree.fromstring(xml)
            text = "\n".join(
                "".join(node.itertext())
                for node in doc.iter(
                    "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"
                )
            )
    elif suffix == "txt":
        text = data.decode("utf-8-sig")
    else:
        raise ValueError("Use PDF, DOCX or UTF-8 TXT.")
    text = text.strip()
    if len(text) < 50:
        raise ValueError(
            "No readable resume text. For scanned PDFs, paste the text instead; OCR is not included."
        )
    if len(text) > 25000:
        raise ValueError(
            "Resume text exceeds 25,000 characters; upload a shorter version."
        )
    return text


def professional(profile):
    # Explicit allowlist prevents any contact or sensitive answer reaching the analyst.
    return {"facts": profile["facts"]}


def export_packet(profile):
    return {
        "format": "pivot-profile-v1",
        "full_name": profile["full_name"],
        "first_name": profile.get("first_name", ""),
        "last_name": profile.get("last_name", ""),
        "email": profile["email"],
        "phone": profile["phone"],
        "location": profile["location"],
        "linkedin": profile.get("linkedin", ""),
        "facts": profile["facts"],
        "veteran_status": profile.get("veteran_status"),
        "work_authorization": profile.get("work_authorization"),
        "review_required": True,
        "consent_policy": "Read and accept each employer agreement yourself. No consent or final submission is automated.",
    }
