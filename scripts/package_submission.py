"""Bundle reviewed tracked source and self-contained deliverables. Never copies runtime/.env."""

import hashlib, json, shutil, subprocess, zipfile
from datetime import datetime, timezone
from pathlib import Path

R = Path(__file__).resolve().parents[1]
OUT = R / "submission"
OUT.mkdir(exist_ok=True)
if subprocess.run(["git", "diff", "--quiet", "HEAD"], cwd=R).returncode:
    raise SystemExit(
        "Commit the reviewed source and document changes before packaging."
    )
revision = subprocess.check_output(
    ["git", "rev-parse", "HEAD"], cwd=R, text=True
).strip()
files = {
    "report.html": "report.html",
    "slides.html": "slides.html",
    "output/presentation/Pivot_Desk.pptx": "Pivot_Desk.pptx",
    "output/demo.webm": "demo.webm",
    "output/user_trial.html": "user_trial.html",
    "output/submission_checklist.md": "submission_checklist.md",
}
for source, target in files.items():
    shutil.copy2(R / source, OUT / target)
subprocess.run(
    [
        "git",
        "archive",
        "--format=zip",
        "--prefix=pivot-desk/",
        "-o",
        str(OUT / "source.zip"),
        "HEAD",
    ],
    cwd=R,
    check=True,
)
with zipfile.ZipFile(OUT / "source.zip") as z:
    names = z.namelist()
    assert not any(
        Path(n).name == ".env"
        or "/runtime/" in n
        or "/node_modules/" in n
        or "/.venv/" in n
        for n in names
    )
    assert "pivot-desk/.env.example" in names
(OUT / "START_HERE.md").write_text("""# Pivot Desk submission package

Double-click report.html and slides.html. Both include their own visuals and work offline.
Pivot_Desk.pptx is an editable nine-slide PowerPoint companion. The required course deck remains slides.html; the PPTX does not replace it.
The captioned demo.webm shows fictional applicant data and a real AI review; it is an automated demonstration, not a human trial.

Canvas requires the GitHub repository URL plus report.html and slides.html. The optional video is included here. source.zip is a clean source backup, not a replacement for the required repository URL. See submission_checklist.md for publication/account requirements and remaining evidence limits.

user_trial.html is a local, anonymous timer worksheet for a real applicant. It contains no completed results. Do not submit empty observations as user evidence.

The source ZIP excludes private runtime state, real .env files, dependencies and virtualenvs. Follow its README to run the app. A personal direct-OpenAI launch option preserves Astra when the course Portkey key cannot be used with that model; the saved workspace default is unchanged.
""")
items = [
    "report.html",
    "slides.html",
    "Pivot_Desk.pptx",
    "demo.webm",
    "user_trial.html",
    "submission_checklist.md",
    "source.zip",
    "START_HERE.md",
]
manifest = {
    "created_at": datetime.now(timezone.utc).isoformat(),
    "source_revision": revision,
    "files": {
        n: {
            "bytes": (OUT / n).stat().st_size,
            "sha256": hashlib.sha256((OUT / n).read_bytes()).hexdigest(),
        }
        for n in items
    },
    "private_files_excluded": True,
    "repository_url": "Pending publication; see checklist",
    "human_trial_completed": False,
    "authenticated_workday_verified": False,
}
(OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
with zipfile.ZipFile(OUT / "Pivot_Desk_Submission.zip", "w", zipfile.ZIP_DEFLATED) as z:
    for n in items + ["manifest.json"]:
        z.write(OUT / n, n)
print(
    json.dumps(
        {
            "package": str(OUT / "Pivot_Desk_Submission.zip"),
            "source_revision": revision,
            "files": items,
            "zip_bytes": (OUT / "Pivot_Desk_Submission.zip").stat().st_size,
        },
        indent=2,
    )
)
