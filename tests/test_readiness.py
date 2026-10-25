"""Application checks preserve source language and never infer applicant eligibility."""

import json
import unittest
from pathlib import Path
from backend import tools
from backend.models import Profile, Preferences

ROOT = Path(__file__).resolve().parents[1]
JOBS = json.loads((ROOT / "data/demo_jobs.json").read_text())


class Readiness(unittest.TestCase):
    def test_travel_benefit_is_not_an_expectation(self):
        self.assertEqual(
            tools.application_checks(
                {"description": "Benefits include Employee Travel Credits."}
            ),
            [],
        )

    def test_explicit_exclusion_scope(self):
        job = {
            "title": "MBA Associate",
            "description": "Prior investment banking experience is useful.",
            "industry": "Consulting",
            "location": "San Francisco",
            "job_type": "full-time",
        }
        strict = Preferences(query="mba", industries=["Consulting"])
        self.assertTrue(tools.eligible(job, strict))
        title = Preferences(
            query="mba", industries=["Consulting"], exclude_scope="title_only"
        )
        self.assertEqual(tools.eligible(job, title), [])
        self.assertTrue(
            tools.eligible({**job, "title": "MBA Investment Banking Associate"}, title)
        )

    def test_real_source_quotes_and_bounds(self):
        for job in JOBS:
            checks = tools.application_checks(job)
            self.assertLessEqual(len(checks), 6)
            self.assertEqual(len({c["kind"] for c in checks}), len(checks))
            for c in checks:
                self.assertIn(c["source_quote"], job["description"])
                self.assertLessEqual(len(c["source_quote"]), 700)
                self.assertNotIn("eligible", c)

    def test_completed_degree_before_intro(self):
        job = {
            "description": "An MBA role for ambitious leaders.\nMBA from an accredited program (required)."
        }
        check = tools.application_checks(job)[0]
        self.assertEqual(
            check["source_quote"], "MBA from an accredited program (required)."
        )

    def test_combined_experience_detected(self):
        checks = tools.application_checks(
            {
                "description": "5+ years of combined pre- and post-MBA experience in corporate strategy."
            }
        )
        self.assertIn("experience", [c["kind"] for c in checks])

    def test_no_qualification_verdict_from_negation(self):
        checks = tools.application_checks(
            {"description": "No travel is required. An MBA is preferred, not required."}
        )
        self.assertTrue(
            any("No travel is required" in c["source_quote"] for c in checks)
        )
        self.assertTrue(
            any("preferred, not required" in c["source_quote"] for c in checks)
        )
        self.assertTrue(
            all(set(c) == {"kind", "label", "source_quote", "question"} for c in checks)
        )

    def test_no_keyword_does_not_invent_a_check(self):
        self.assertEqual(
            tools.application_checks(
                {"description": "Build excellent products with a collaborative team."}
            ),
            [],
        )

    def test_explicit_names_export_without_ai_access(self):
        profile = Profile.model_validate(
            json.loads((ROOT / "data/demo_profile.json").read_text())
        )
        profile.first_name = "Avery"
        profile.last_name = "Morgan"
        packet = tools.export_packet(profile.model_dump())
        self.assertEqual(packet["first_name"], "Avery")
        self.assertEqual(packet["last_name"], "Morgan")
        self.assertEqual(set(tools.professional(profile.model_dump())), {"facts"})

    def test_missing_name_parts_stay_empty(self):
        profile = json.loads((ROOT / "data/demo_profile.json").read_text())
        self.assertEqual(tools.export_packet(profile)["first_name"], "")
        self.assertEqual(tools.export_packet(profile)["last_name"], "")


if __name__ == "__main__":
    unittest.main()
