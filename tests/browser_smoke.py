"""Run against the app on port 8000. Uses fictional demo data; no AI calls."""
from playwright.sync_api import sync_playwright, expect

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 1000})
        page = context.new_page()
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto("http://localhost:8000")
        page.get_by_role("button", name="Explore a fictional demo").click()
        expect(page.locator(".demo-bar")).to_be_visible()
        page.get_by_role("textbox", name="Role keywords").fill("strategy")
        page.get_by_role("button", name="Find roles", exact=True).click()
        expect(page.locator(".job-card").first).to_be_visible()
        page.locator(".save-job").first.click()
        page.get_by_role("button", name="My pipeline").click()
        expect(page.locator(".tracker-card")).to_have_count(1)
        page.get_by_label("Stage").select_option("Preparing")
        expect(page.get_by_label("Stage")).to_have_value("Preparing")
        page.reload()
        page.get_by_role("button", name="My pipeline").click()
        expect(page.get_by_label("Stage")).to_have_value("Preparing")
        lab = context.new_page()
        lab.goto("http://localhost:8000/application-lab.html")
        lab.locator("#preview").click()
        expect(lab.locator("#status")).to_contain_text("fields available")
        lab.locator("#review").check()
        lab.locator("#fill").click()
        expect(lab.locator("#status")).to_have_text("13 fields filled. No consent accepted. No application submitted.")
        expect(lab.locator("#consent")).not_to_be_checked()
        expect(lab.locator("#signature")).to_have_value("")
        expect(lab.locator("#veteran")).to_have_value("")
        page.get_by_role("button", name="Discover roles", exact=True).click()
        page.set_viewport_size({"width": 390, "height": 844})
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        assert not errors, errors
        browser.close()
        print("Browser smoke passed: search, pipeline persistence, 13 reviewed fields, manual consent and mobile layout. No AI calls.")

if __name__ == "__main__":
    main()
