"""Record a captioned, automated demo with fictional data. One live AI review.

Run with both local servers running. No employer application is filled or sent.
"""

import json, time, sys
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

R = Path(__file__).resolve().parents[1]
OUT = R / "output"
OUT.mkdir(exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    c = b.new_context(
        viewport={"width": 1440, "height": 1000},
        record_video_dir=str(OUT / "demo_temp"),
        record_video_size={"width": 1440, "height": 1000},
    )
    page = c.new_page()
    page.goto("http://localhost:5173")
    page.get_by_role("button", name="Explore a fictional demo").click()
    expect(page.locator(".demo-bar")).to_be_visible()

    def caption(text, pause=10):
        page.evaluate(
            """text=>{let e=document.getElementById('demo-caption');if(!e){e=document.createElement('aside');e.id='demo-caption';e.style.cssText='position:fixed;bottom:18px;left:260px;right:25px;z-index:99999;background:#261e29;color:#fff;padding:18px 24px;border:2px solid #efabc8;border-radius:10px;font:18px/1.5 system-ui;box-shadow:0 8px 40px #0003';document.body.append(e)}e.textContent='AUTOMATED DEMO · FICTIONAL APPLICANT — '+text}""",
            text,
        )
        page.wait_for_timeout(pause * 1000)

    caption(
        "Pivot Desk connects reviewed resume facts to real employer listings. No application is submitted.",
        8,
    )
    page.get_by_label("Role keywords").fill("strategy")
    page.get_by_role("button", name="Find roles", exact=True).click()
    expect(page.locator(".job-card").first).to_be_visible()
    page.locator(".job-select").filter(
        has_text="Manager, Corporate Strategy - MBA Grad, Summer 2027"
    ).click()
    caption(
        "Search applies your location, industry and exclusions before scoring. The number measures overlap, not hiring probability.",
        12,
    )
    page.locator(".application-checks").scroll_into_view_if_needed()
    page.locator(".application-checks details").first.locator("summary").click()
    caption(
        "Check before applying: the employer requires a completed MBA. Candidacy alone does not establish that qualification.",
        12,
    )
    with page.expect_response(
        lambda r: "/api/analyze" in r.url and r.request.method == "POST"
    ) as resp:
        page.get_by_role("button", name="Get an AI evidence review").click()
    run_id = resp.value.json()["run_id"]
    caption(
        "The analyst reads reviewed professional facts and the selected employer posting through two bounded tools.",
        3,
    )
    expect(page.locator(".analysis")).to_be_visible(timeout=120000)
    page.locator("#demo-caption").evaluate("e=>e.remove()")
    # Capture the real timeline and result, separate from the video captions.
    page.locator(".analysis").scroll_into_view_if_needed()
    page.screenshot(path=str(OUT / "screenshots/final-analysis.png"))
    run = c.request.get("http://localhost:5173/api/runs/" + run_id).json()
    (OUT / "evidence/final_demo_run.json").write_text(json.dumps(run, indent=2) + "\n")
    c.storage_state(path=str(R / "runtime/demo_browser_state.json"))
    page.get_by_role("button", name="Save role", exact=True).click()
    caption(
        "The result cites exact employer language and resume facts, then names missing evidence and questions to resolve.",
        14,
    )
    page.get_by_role("button", name="My pipeline").click()
    expect(page.locator(".tracker-card")).to_have_count(1)
    page.get_by_label("Stage").select_option("Preparing")
    caption(
        "A saved role and next step stay in this private browser workspace. Preparing is a record, not an application submission.",
        12,
    )
    page.get_by_role("button", name="My evidence", exact=True).click()
    caption(
        "Review the extracted facts before using them. Given and family names for forms are explicit choices, never guessed by splitting a name.",
        12,
    )
    page.get_by_role("button", name="Application kit", exact=True).click()
    caption(
        "The helper previews ordinary fields before filling. Employer logins, agreements, signatures and final submission remain manual.",
        12,
    )
    # Same tab keeps one coherent video. The fixture is hosted locally.
    page.goto("http://localhost:5173/application-lab.html")
    page.locator("#preview").click()
    page.locator("#review").check()
    page.locator("#fill").click()
    expect(page.locator("#status")).to_have_text(
        "13 fields filled. No consent accepted. No application submitted."
    )
    page.locator("#consent").scroll_into_view_if_needed()
    caption(
        "Practice form: 13 fields filled. Consent, signature and unspecified sensitive answers remain untouched. Real Workday compatibility is still unverified.",
        15,
    )
    page.goto("http://localhost:5173")
    page.get_by_role("button", name="Usage & proof", exact=True).click()
    caption(
        "The ledger records actual tokens and estimated cost. This is a local prototype with source evidence, clear limits and human review.",
        12,
    )
    video = page.video
    c.close()
    target = OUT / "demo.webm"
    video.save_as(str(target))
    b.close()
    temp = OUT / "demo_temp"
    for f in temp.glob("*.webm"):
        f.unlink()
    temp.rmdir()
    print(
        json.dumps(
            {
                "video": str(target),
                "run_id": run_id,
                "status": run.get("status"),
                "usage": run.get("usage"),
                "recording": "Automated, captioned, fictional applicant. No human trial or narration claimed.",
            }
        )
    )
