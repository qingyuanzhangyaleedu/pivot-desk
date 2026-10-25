"""Current UI regression: qualification prompts and an explicit exclusion scope."""

import json
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

R = Path(__file__).resolve().parents[1]
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    c = b.new_context(viewport={"width": 1440, "height": 1000})
    page = c.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto("http://localhost:5173")
    page.get_by_role("button", name="Explore a fictional demo").click()
    expect(page.locator(".demo-bar")).to_be_visible()
    page.get_by_role("textbox", name="Role keywords").fill("strategy")
    page.get_by_role("button", name="Find roles", exact=True).click()
    expect(page.locator(".job-card").first).to_be_visible()
    page.locator(".job-select").filter(
        has_text="Manager, Corporate Strategy - MBA Grad, Summer 2027"
    ).click()
    expect(page.get_by_role("region", name="Check before applying")).to_be_visible()
    page.locator(".application-checks details").first.locator("summary").click()
    expect(page.locator(".application-checks")).to_contain_text(
        "MBA from an accredited program"
    )
    page.locator(".application-checks").screenshot(
        path=str(R / "output/screenshots/application-checks.png")
    )
    page.locator(".fit-panel").scroll_into_view_if_needed()
    page.screenshot(path=str(R / "output/screenshots/readiness-desktop.png"))
    sectors = page.locator(".chips").nth(1)
    for name in ["Healthcare", "Technology", "Consulting"]:
        sectors.get_by_role("button", name=name, exact=True).click()
    page.get_by_label("Exclusion scope").select_option("title_only")
    with page.expect_response(
        lambda r: "/api/search" in r.url and r.request.method == "POST"
    ) as response:
        page.get_by_role("button", name="MBA roles", exact=True).click()
    jobs = response.value.json()["jobs"]
    assert jobs and all("investment banking" not in j["title"].lower() for j in jobs)
    expect(page.get_by_label("Excluded terms")).to_have_value("investment banking")
    page.set_viewport_size({"width": 390, "height": 844})
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    page.screenshot(
        path=str(R / "output/screenshots/readiness-mobile.png"), full_page=True
    )
    trial = c.new_page()
    trial.goto((R / "output/user_trial.html").as_uri())
    trial.get_by_role("button", name="Download anonymous observations").click()
    expect(trial.locator("#status")).to_contain_text("Complete both timed rounds")
    assert not errors
    out = {
        "application_checks_visible": True,
        "exact_degree_requirement_visible": True,
        "title_only_exclusion_keeps_phrase": True,
        "consulting_mba_matches": len(jobs),
        "mobile_no_overflow": True,
        "trial_requires_completed_observations": True,
        "errors": errors,
        "model_calls": 0,
    }
    (R / "output/evidence/readiness_browser.json").write_text(
        json.dumps(out, indent=2) + "\n"
    )
    print(json.dumps(out))
    b.close()
