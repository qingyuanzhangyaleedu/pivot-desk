"""Reproducible source-check coverage benchmark. No AI or applicant outcome claims."""

import json, sys, time
from pathlib import Path

R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R))
from backend import tools
from backend.models import Preferences

jobs = {j["id"]: j for j in json.loads((R / "data/demo_jobs.json").read_text())}
profile = json.loads((R / "data/demo_profile.json").read_text())
# Author-labeled topics in fixed public snapshots, selected before this benchmark run.
# Selection is deliberate, not random or independent. No claim of statistical accuracy.
cases = [
    ("gh:heartflowinc:6218422004", ["degree", "experience", "travel", "location"]),
    ("gh:heartflowinc:6218478004", ["degree", "experience", "travel"]),
    ("gh:heartflowinc:6207194004", ["degree", "experience", "license", "location"]),
    ("gh:oscar:8241475", ["degree", "experience", "location", "travel"]),
    ("gh:oscar:8202916", ["degree", "experience", "travel"]),
    ("gh:airbnb:8259920", ["experience"]),
    ("gh:stripe:8078168", ["experience"]),
    ("gh:thebrattlegroup:4738128005", ["degree"]),
    ("gh:tworoadsconsulting:4110370005", ["degree", "travel"]),
    ("gh:chime:8869627002", ["experience", "location"]),
    ("gh:quince:5421994008", ["degree", "experience"]),
    (
        "gh:clearwayjobs:5103138007",
        ["degree", "experience", "travel", "authorization", "location"],
    ),
]
results = []
started = time.perf_counter()
for ident, expected in cases:
    j = jobs[ident]
    checks = tools.application_checks(j)
    found = {c["kind"] for c in checks}
    results.append(
        {
            "id": ident,
            "company": j["company"],
            "title": j["title"],
            "url": j["url"],
            "score": tools.rank(
                j, profile, Preferences(query="strategy product operations")
            )["score"],
            "expected_topics": expected,
            "surfaced_topics": sorted(found),
            "missing_topics": sorted(set(expected) - found),
            "additional_topics": sorted(found - set(expected)),
            "all_quotes_exact": all(
                c["source_quote"] in j["description"] for c in checks
            ),
            "checks": checks,
        }
    )
# Deliberately record a wording the simple numeric-years rule does not cover.
challenge = {"description": "A decade of strategy experience is required."}
challenge_detected = bool(tools.application_checks(challenge))
expected_total = sum(len(c["expected_topics"]) for c in results)
misses = sum(len(c["missing_topics"]) for c in results)
out = {
    "scope": "Development coverage check on 12 deliberately selected real employer snapshots. Author annotations, not an independent benchmark or applicant trial. Categories are prompts to inspect, not mandatory conditions or eligibility decisions.",
    "cases": results,
    "expected_topics": expected_total,
    "surfaced_expected_topics": expected_total - misses,
    "all_quotes_exact": all(c["all_quotes_exact"] for c in results),
    "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
    "model_calls": 0,
    "worded_years_challenge": {
        "text": challenge["description"],
        "detected": challenge_detected,
        "limitation": "Numeric-years pattern does not cover written quantities such as a decade.",
    },
    "baseline": "Original score-only search response contained no separately labeled application checks. AI assessment and the full posting remain available in both versions.",
}
(R / "output/evidence/readiness_benchmark.json").write_text(
    json.dumps(out, indent=2) + "\n"
)
print(json.dumps({k: v for k, v in out.items() if k != "cases"}, indent=2))
for c in results:
    if c["missing_topics"]:
        print("MISSING", c["title"], c["missing_topics"])
