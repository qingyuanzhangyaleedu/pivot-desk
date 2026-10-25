"""Older search responses must not replace a newer selection; no model calls."""

import asyncio, json
from pathlib import Path
from playwright.async_api import async_playwright, expect

ROOT = Path(__file__).resolve().parents[1]


async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        c = await b.new_context()
        await c.request.post("http://localhost:8000/api/demo", data={})
        page = await c.new_page()
        status_started = asyncio.Event()
        release_status = asyncio.Event()

        async def status(route):
            response = await route.fetch()
            status_started.set()
            await release_status.wait()
            await route.fulfill(response=response)

        await page.route("**/api/status", status)
        await page.goto("http://localhost:8000")
        await status_started.wait()
        boot_protected = await page.get_by_label(
            "Role keywords", exact=True
        ).is_disabled()
        release_status.set()
        await expect(
            page.get_by_role("button", name="Find roles", exact=True)
        ).to_be_enabled()
        await expect(page.locator(".job-card").first).to_be_visible()
        template = (
            await (
                await c.request.post(
                    "http://localhost:8000/api/search",
                    data={"preferences": {"query": "strategy"}},
                )
            ).json()
        )["jobs"][0]
        older_started = asyncio.Event()
        release_older = asyncio.Event()

        async def search(route):
            query = route.request.post_data_json["preferences"]["query"]
            job = {
                **template,
                "id": "test:" + query,
                "title": "Synthetic " + query + " role",
            }
            if query == "older":
                older_started.set()
                await release_older.wait()
            await route.fulfill(
                json={
                    "jobs": [job],
                    "total_matches": 1,
                    "screened": 1,
                    "excluded": 0,
                    "returned_cap": 100,
                }
            )

        await page.route("**/api/search", search)
        field = page.get_by_label("Role keywords", exact=True)
        await field.fill("older")
        await field.press("Enter")
        await older_started.wait()
        blocked = await page.get_by_role(
            "button", name="Get an AI evidence review", exact=True
        ).is_disabled()
        await field.fill("newer")
        await field.press("Enter")
        await expect(page.locator(".fit-panel")).to_contain_text("Synthetic newer role")
        release_older.set()
        await page.wait_for_timeout(450)
        latest = (await page.locator(".fit-panel").inner_text()).find(
            "Synthetic newer role"
        ) >= 0
        posted = []
        analysis_started = asyncio.Event()
        release_analysis = asyncio.Event()

        async def analyze(route):
            posted.append(route.request.post_data_json["job_id"])
            analysis_started.set()
            await release_analysis.wait()
            await route.fulfill(
                status=503,
                json={"detail": "Controlled regression: no AI request was made."},
            )

        await page.route("**/api/analyze", analyze)
        await page.get_by_role(
            "button", name="Get an AI evidence review", exact=True
        ).click()
        await analysis_started.wait()
        duplicate_blocked = await page.get_by_role(
            "button", name="Get an AI evidence review", exact=True
        ).is_disabled()
        release_analysis.set()
        await page.wait_for_timeout(100)
        result = {
            "keyword_edit_blocked_during_initial_load": boot_protected,
            "analysis_blocked_during_search": blocked,
            "newer_search_survives_late_older_response": latest,
            "analysis_disabled_while_request_pending": duplicate_blocked,
            "submitted_job_id": posted,
            "model_calls": 0,
            "fixture": "Fictional search responses and mocked analysis route; no employer or model call.",
        }
        result["passed"] = (
            boot_protected
            and blocked
            and latest
            and duplicate_blocked
            and posted == ["test:newer"]
        )
        (ROOT / "output/evidence/search_race_regression.json").write_text(
            json.dumps(result, indent=2) + "\n"
        )
        print(json.dumps(result, indent=2))
        await b.close()
        assert result["passed"]


asyncio.run(main())
