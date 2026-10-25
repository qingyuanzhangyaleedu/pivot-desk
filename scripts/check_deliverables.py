"""Check the report and slides offline, away from the repository. No model calls.

Install requirements.txt, requirements-dev.txt and Playwright Chromium first.
"""

import json
import shutil
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "output/evidence"


def main():
    checks = {"copied_artifacts_open_offline": True}
    repo_url = (ROOT / "output/github_url.txt").read_text().strip()
    screenshots = EVIDENCE / "artifact_checks"
    screenshots.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="pivot-artifacts-") as temp:
        folder = Path(temp)
        for filename in ("report.html", "slides.html"):
            shutil.copy2(ROOT / filename, folder / filename)
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 1440, "height": 1000}, offline=True
            )
            page = context.new_page()
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto((folder / "report.html").as_uri())
            checks["report_public_repository_link"] = page.locator(
                f'.sheet:first-child a[href="{repo_url}"]'
            ).is_visible()
            page.emulate_media(media="print")
            checks["report_images_loaded"] = page.locator("img").evaluate_all(
                "xs => xs.length > 0 && xs.every(x => x.complete && x.naturalWidth > 0)"
            )
            checks["report_sections"] = page.locator(".sheet").count()
            checks["report_overflow"] = page.locator(".sheet").evaluate_all("""
                xs => xs.map((e, i) => ({
                    page: i + 1,
                    overlap: Math.max(...[...e.children]
                        .filter(c => !c.classList.contains('footer'))
                        .map(c => c.getBoundingClientRect().bottom))
                        - e.querySelector('.footer').getBoundingClientRect().top
                })).filter(x => x.overlap > 0)
            """)
            pdf = folder / "report.pdf"
            page.pdf(
                path=str(pdf),
                format="Letter",
                print_background=True,
                prefer_css_page_size=True,
            )
            checks["report_printed_pages"] = len(PdfReader(pdf).pages)
            for index in range(checks["report_sections"]):
                page.locator(".sheet").nth(index).screenshot(
                    path=str(screenshots / f"report-{index + 1}.png")
                )

            page.emulate_media(media="screen")
            page.goto((folder / "slides.html").as_uri())
            page.wait_for_function("window.Reveal && Reveal.isReady()")
            checks["slides_public_repository_link"] = page.locator(
                f'.slides > section:first-child a[href="{repo_url}"]'
            ).is_visible()
            checks["slides"] = page.evaluate("Reveal.getTotalSlides()")
            checks["slide_overflow"] = []
            for index in range(checks["slides"]):
                page.evaluate("i => Reveal.slide(i)", index)
                page.wait_for_timeout(700)
                slide = page.locator(".slides > section.present")
                size = slide.evaluate(
                    "e => ({height: e.scrollHeight, limit: Reveal.getConfig().height})"
                )
                if size["height"] > size["limit"]:
                    checks["slide_overflow"].append({"slide": index + 1, **size})
                page.screenshot(path=str(screenshots / f"slide-{index + 1}.png"))
            page.evaluate("Reveal.slide(0)")
            page.keyboard.press("ArrowRight")
            checks["arrow_navigation"] = page.evaluate("Reveal.getIndices().h") == 1
            page.keyboard.press("f")
            page.wait_for_function("document.fullscreenElement !== null")
            checks["fullscreen"] = True
            checks["slide_images_loaded"] = page.locator("img").evaluate_all(
                "xs => xs.length > 0 && xs.every(x => x.complete && x.naturalWidth > 0)"
            )
            checks["browser_errors"] = errors
            browser.close()

    passed = (
        10 <= checks["report_printed_pages"] <= 15
        and checks["report_printed_pages"] == checks["report_sections"]
        and 1 <= checks["slides"] <= 10
        and checks["report_images_loaded"]
        and checks["slide_images_loaded"]
        and checks["arrow_navigation"]
        and checks["fullscreen"]
        and checks["report_public_repository_link"]
        and checks["slides_public_repository_link"]
        and not checks["report_overflow"]
        and not checks["slide_overflow"]
        and not checks["browser_errors"]
    )
    checks["passed"] = passed
    (EVIDENCE / "artifact_validation.json").write_text(
        json.dumps(checks, indent=2) + "\n"
    )
    print(json.dumps(checks, indent=2))
    if not passed:
        raise SystemExit(
            "Artifact checks failed; inspect output/evidence/artifact_checks/."
        )


if __name__ == "__main__":
    main()
