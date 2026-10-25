"""Exercise the real shared adapter against controlled ATS-like DOM fixtures."""

import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
packet = json.loads((ROOT / "data/demo_profile.json").read_text())
packet.update(format="pivot-profile-v1", first_name="Avery", last_name="Morgan")
packet["facts"].append(
    dict(
        id="E2",
        kind="education",
        title="BS Economics",
        organization="Example College",
        description="",
        start="2016",
        end="2020",
        evidence_quote="Fictional test entry",
    )
)
checks = []
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    page = b.new_page()

    def prepare(markup):
        page.set_content(markup)
        page.add_script_tag(path=str(ROOT / "extension/content.js"))

    def fill():
        return page.evaluate(
            "(p)=>{const plan=PivotFill.preview(p);return {plan,result:PivotFill.apply(p,plan.filter(r=>r.value&&!r.sensitive))}}",
            packet,
        )

    prepare(
        """<span id="given-label">Given name</span><input id="given" aria-labelledby="given-label"><label>Family name<input id="family"></label><div data-automation-id="educationSection"><label>University<input id="e1"></label></div><div data-automation-id="educationSection"><label>University<input id="e2"></label></div><label>Language<select id="language"><option></option><option value="en">English</option></select></label>"""
    )
    r = fill()
    assert page.locator("#given").input_value() == "Avery"
    assert page.locator("#family").input_value() == "Morgan"
    assert (
        page.locator("#e1").input_value() == "Example School of Management (fictional)"
    )
    assert page.locator("#e2").input_value() == "Example College"
    assert page.locator("#language").input_value() == "en"
    checks += [
        "Explicit given/family names; aria-labelledby; two separate education records; exact native-select option"
    ]
    prepare(
        """<label>Email<input id="email" type="email" value="existing@example.com"></label><label>Password<input id="pw" type="password"></label><label>Privacy agreement<input id="consent" type="checkbox"></label><label>Signature<input id="sign"></label><label>Start date<input id="date" type="date"></label><label>Veteran status<input id="veteran"></label><button role="combobox">Degree custom dropdown</button>"""
    )
    r = fill()
    assert r["result"]["filled"] == 0
    assert page.locator("#email").input_value() == "existing@example.com"
    assert not page.locator("#consent").is_checked()
    assert page.locator("#sign").input_value() == ""
    checks += [
        "Existing different email protected; password, agreement, signature, unknown date, sensitive answer and custom combobox left manual"
    ]
    prepare(
        """<label>Full name<input id="name"></label><label>Email<input id="email" type="email"></label><script>document.querySelector('#name').addEventListener('change',()=>{document.querySelector('#email').outerHTML='<input id="replacement" aria-label="Email">'})</script>"""
    )
    r = fill()
    assert r["result"]["filled"] == 1
    assert page.locator("#replacement").input_value() == ""
    assert r["result"]["skipped"]
    checks += [
        "Framework replaced an input after the first change: stale approval skipped"
    ]
    prepare(
        '<label>Given name<input id="given"></label><label>Family name<input id="family"></label>'
    )
    no_parts = {**packet, "first_name": "", "last_name": ""}
    assert all(
        r["value"] is None for r in page.evaluate("p=>PivotFill.preview(p)", no_parts)
    )
    checks += ["Full name never automatically split when reviewed parts are absent"]
    prepare('<label>Veteran status<input data-pivot-key="email" id="attack"></label>')
    r = fill()
    assert r["result"]["filled"] == 0
    checks += ["Misleading data-pivot-key cannot bypass sensitive-answer review"]
    b.close()
assert (ROOT / "extension/content.js").read_bytes() == (
    ROOT / "frontend/public/form-helper.js"
).read_bytes()
out = {
    "checks": checks,
    "passed": True,
    "fixture_scope": "Controlled DOM, including Workday-style attributes. Not an authenticated Workday compatibility test.",
    "shared_adapter_identical": True,
    "submitted": False,
    "model_calls": 0,
}
(ROOT / "output/evidence/form_regression.json").write_text(
    json.dumps(out, indent=2) + "\n"
)
print(json.dumps(out, indent=2))
