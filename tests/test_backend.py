"""Offline safety and contract checks. No model calls and no personal data."""

import unittest, tempfile, json, io, zipfile
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient
from pydantic_ai import ModelRetry
from pydantic import ValidationError
from backend import storage, tools, agent, config
from backend.models import Preferences, ResumeExtraction, FitAnalysis, Job
from backend.main import app

ROOT = Path(__file__).resolve().parents[1]
DEMO = json.loads((ROOT / "data/demo_profile.json").read_text())
JOBS = json.loads((ROOT / "data/demo_jobs.json").read_text())


class Core(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old = storage.DB
        storage.DB = Path(self.tmp.name) / "test.db"
        storage.initialize()

    def tearDown(self):
        storage.DB = self.old
        self.tmp.cleanup()

    def test_new_sector_search_contract(self):
        # Use the bundled real listings so a fresh installation exercises the new filters.
        with TestClient(app) as client:
            options = client.get("/api/status").json()["industries"]
            for sector in [
                "Consulting",
                "Finance & Fintech",
                "Consumer & Retail",
                "Climate & Sustainability",
            ]:
                with self.subTest(sector=sector):
                    self.assertIn(sector, options)
                    result = client.post(
                        "/api/search",
                        json={"preferences": {"query": "", "industries": [sector]}},
                    ).json()
                    self.assertGreater(len(result["jobs"]), 0)
                    self.assertTrue(
                        all(j["industry"] == sector for j in result["jobs"])
                    )
                    self.assertTrue(
                        all(
                            "investment banking"
                            not in (j["title"] + " " + j["description"]).lower()
                            for j in result["jobs"]
                        )
                    )
            self.assertEqual(Preferences().industries, ["Healthcare", "Technology"])
            self.assertEqual(Preferences().exclude, ["investment banking"])

    def test_mba_consulting_keeps_location_constraint(self):
        with TestClient(app) as client:
            result = client.post(
                "/api/search",
                json={
                    "preferences": {
                        "query": "mba",
                        "industries": ["Consulting"],
                        "exclude": [],
                    }
                },
            ).json()
            self.assertTrue(any("MBA" in j["title"] for j in result["jobs"]))
            self.assertFalse(
                any(j["company"] == "Two Roads Consulting" for j in result["jobs"])
            )
            self.assertTrue(
                all("San Francisco" in j["location"] for j in result["jobs"])
            )
            # The strict exclusion also catches descriptions that mention prior
            # banking experience; never silently relax a shopper's preference.
            strict = client.post(
                "/api/search",
                json={"preferences": {"query": "mba", "industries": ["Consulting"]}},
            ).json()
            self.assertEqual(strict["jobs"], [])
            widened = client.post(
                "/api/search",
                json={
                    "preferences": {
                        "query": "mba",
                        "industries": ["Consulting"],
                        "regions": [],
                    }
                },
            ).json()
            self.assertTrue(
                any(j["company"] == "Two Roads Consulting" for j in widened["jobs"])
            )

    def test_washington_dc_is_not_west_coast(self):
        job = {
            **JOBS[0],
            "title": "MBA Associate",
            "description": "Consulting",
            "industry": "Consulting",
        }
        prefs = Preferences(query="mba", industries=["Consulting"], exclude=[])
        for location in [
            "Washington, District of Columbia, United States",
            "Washington, DC",
            "Washington D.C.",
        ]:
            self.assertTrue(tools.eligible({**job, "location": location}, prefs))
        for location in [
            "Seattle, Washington, United States",
            "San Francisco; Washington, DC",
        ]:
            self.assertEqual(tools.eligible({**job, "location": location}, prefs), [])

    def test_sensitive_fields_not_in_analyst(self):
        p = {**DEMO, "veteran_status": "private", "work_authorization": "private"}
        self.assertEqual(set(tools.professional(p)), {"facts"})
        self.assertNotIn("avery", json.dumps(tools.professional(p)).lower())

    def test_exact_quote_validation(self):
        bad = ResumeExtraction(
            full_name="",
            facts=[
                dict(DEMO["facts"][0], evidence_quote="Invented employer achievement")
            ],
            warnings=[],
        )
        with self.assertRaises(ModelRetry):
            agent.validate_extraction(bad, "Only an unrelated source line here.")

    def test_unknown_fact_rejected(self):
        bad = FitAnalysis(
            summary="Test",
            evidence=[
                {
                    "fact_id": "FAKE",
                    "job_quote": JOBS[0]["description"][:30],
                    "connection": "Claim",
                }
            ],
            gaps=[],
            questions=[],
            interview_angles=[],
        )
        with self.assertRaises(ModelRetry):
            agent.validate_analysis(bad, DEMO, JOBS[0])

    def test_invented_job_quote_rejected(self):
        bad = FitAnalysis(
            summary="Test",
            evidence=[
                {
                    "fact_id": DEMO["facts"][0]["id"],
                    "job_quote": "Completely fabricated job qualification",
                    "connection": "Claim",
                }
            ],
            gaps=[],
            questions=[],
            interview_angles=[],
        )
        with self.assertRaises(ModelRetry):
            agent.validate_analysis(bad, DEMO, JOBS[0])

    def test_queue_reserves_budget(self):
        s = storage.session(None)
        with patch.object(
            config, "DAILY_TOKEN_LIMIT", 2 * (config.TOKEN_LIMIT + config.OUTPUT_LIMIT)
        ):
            agent.reserve(s, "fit")
            agent.reserve(s, "fit")
            with self.assertRaises(ValueError):
                agent.reserve(s, "fit")

    def test_filters_exclusion(self):
        j = {
            **JOBS[0],
            "description": "Requires investment banking experience",
            "location": "San Francisco",
            "title": "Strategy manager",
        }
        self.assertTrue(
            any("Excluded phrase" in x for x in tools.eligible(j, Preferences()))
        )

    def test_remote_not_assumed(self):
        j = {**JOBS[0], "location": "Remote - Canada", "title": "Strategy manager"}
        self.assertTrue(
            any("Location" in x for x in tools.eligible(j, Preferences(exclude=[])))
        )

    def test_unknown_salary_not_invented(self):
        self.assertEqual(
            tools.salary("Competitive salary and an annual bonus"), (None, None)
        )
        self.assertTrue(
            any(
                "salary" in x
                for x in tools.eligible(
                    {**JOBS[0], "salary_min": None},
                    Preferences(
                        regions=[],
                        industries=[],
                        exclude=[],
                        query="",
                        minimum_salary=100000,
                    ),
                )
            )
        )

    def test_title_query_not_boilerplate(self):
        self.assertTrue(
            any(
                "keyword" in x
                for x in tools.eligible(
                    {
                        **JOBS[0],
                        "title": "Software engineer",
                        "description": "Our product strategy team is great",
                    },
                    Preferences(
                        query="strategy", regions=[], industries=[], exclude=[]
                    ),
                )
            )
        )

    def test_rank_is_deterministic(self):
        a = tools.rank(JOBS[0], DEMO, Preferences())
        self.assertEqual(a, tools.rank(JOBS[0], DEMO, Preferences()))
        self.assertTrue(0 <= a["score"] <= 100)

    def test_absent_profile_no_score(self):
        self.assertIsNone(tools.rank(JOBS[0], None, Preferences())["score"])

    def test_dangerous_url_rejected(self):
        with self.assertRaises(ValidationError):
            Job.model_validate({**JOBS[0], "url": "javascript:alert(1)"})

    def test_text_upload(self):
        self.assertIn(
            "fictional",
            tools.extract_document(
                (ROOT / "data/demo_resume.txt").read_bytes(), "resume.txt"
            ).lower(),
        )

    def test_pdf_upload(self):
        self.assertIn(
            "Avery Morgan",
            tools.extract_document(
                (ROOT / "data/demo_resume.pdf").read_bytes(), "resume.pdf"
            ),
        )

    def test_docx_upload(self):
        b = io.BytesIO()
        with zipfile.ZipFile(b, "w") as z:
            z.writestr(
                "word/document.xml",
                '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:p><w:t>A fictional resume with more than fifty characters and explicit SQL experience.</w:t></w:p></w:document>',
            )
        self.assertIn("SQL", tools.extract_document(b.getvalue(), "resume.docx"))

    def test_bad_upload_rejected(self):
        for data, name in [
            (b"hi", "resume.txt"),
            (b"x" * 4194305, "resume.txt"),
            (b"fake", "resume.exe"),
        ]:
            with self.assertRaises(ValueError):
                tools.extract_document(data, name)

    def test_api_isolation_and_delete(self):
        with TestClient(app) as a, TestClient(app) as b:
            a.post("/api/demo")
            self.assertIsNone(b.get("/api/status").json()["profile"])
            self.assertEqual(b.get("/api/packet").status_code, 409)
            self.assertEqual(
                a.get("/api/packet").json()["full_name"], DEMO["full_name"]
            )
            self.assertEqual(a.delete("/api/private").status_code, 200)
            self.assertIsNone(a.get("/api/status").json()["profile"])

    def test_consent_required(self):
        with TestClient(app) as c:
            r = c.post(
                "/api/resume",
                files={
                    "file": ("resume.txt", (ROOT / "data/demo_resume.txt").read_bytes())
                },
                data={"consent": "false"},
            )
            self.assertEqual(r.status_code, 400)
            self.assertEqual(
                c.post(
                    "/api/analyze", json={"job_id": JOBS[0]["id"], "consent": False}
                ).status_code,
                422,
            )

    def test_cross_site_change_blocked(self):
        with TestClient(app) as c:
            self.assertEqual(
                c.post(
                    "/api/demo", headers={"Origin": "https://evil.example"}
                ).status_code,
                403,
            )

    def test_tracker_persistence(self):
        with TestClient(app) as c:
            c.post("/api/demo")
            r = c.put(
                "/api/tracker",
                json={
                    "job_id": JOBS[0]["id"],
                    "stage": "Preparing",
                    "note": "Draft only",
                    "follow_up": "2026-11-01",
                },
            )
            self.assertEqual(r.status_code, 200)
            self.assertEqual(c.get("/api/tracker").json()[0]["note"], "Draft only")

    def test_private_import_isolation(self):
        with TestClient(app) as a, TestClient(app) as b:
            body = {
                "title": "MBA strategy role",
                "company": "Fictional test only",
                "industry": "Technology",
                "location": "Seattle",
                "url": "https://example.com/job",
                "description": "Private fixture. "
                + ("SQL and product strategy required. " * 5),
            }
            j = a.post("/api/jobs/import", json=body)
            self.assertEqual(j.status_code, 200)
            self.assertEqual(
                b.put(
                    "/api/tracker",
                    json={
                        "job_id": j.json()["id"],
                        "stage": "Saved",
                        "note": "",
                        "follow_up": "",
                    },
                ).status_code,
                404,
            )

    def test_no_unreviewed_profile_use(self):
        with TestClient(app) as c:
            self.assertEqual(
                c.put("/api/profile", json={**DEMO, "confirmed": False}).status_code,
                400,
            )

    def test_budget_persists_in_db(self):
        s = storage.session(None)
        agent.reserve(s, "fit")
        storage.initialize()
        with storage.db() as c:
            self.assertEqual(c.execute("SELECT COUNT(*) FROM runs").fetchone()[0], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
