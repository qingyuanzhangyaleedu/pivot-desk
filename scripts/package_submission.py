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
    "output/presentation/Pivot_Desk_Submission.pptx": "Pivot_Desk.pptx",
    "output/github_url.txt": "github_url.txt",
    "output/demo.webm": "demo.webm",
    "output/user_trial.html": "user_trial.html",
    "output/submission_checklist.md": "submission_checklist.md",
}
for source, target in files.items():
    shutil.copy2(R / source, OUT / target)
canvas = OUT / "canvas_upload"
canvas.mkdir(exist_ok=True)
canvas_files = ["report.html", "slides.html"]
extras = {p.name for p in canvas.iterdir()} - set(canvas_files)
if extras:
    raise SystemExit("The Canvas upload folder contains unexpected files; preserve them outside that folder before packaging.")
for name in canvas_files:
    shutil.copy2(R / name, canvas / name)
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
repo_url = (R / "output/github_url.txt").read_text().strip()
(OUT / "START_HERE.md").write_text(f"""# Pivot Desk — upload only the two HTML files

The instructor's October 25 announcement changes Canvas to FILE UPLOAD only.
Upload canvas_upload/report.html and canvas_upload/slides.html. Both include the public repository URL: {repo_url}.
The canvas_upload folder contains exactly those two files. A testing video is optional.
Do not upload this README, the PowerPoint, either ZIP, source files, github_url.txt, the manifest or the trial worksheet. Extra attachments may be penalized.

Double-click the two HTML files to review them. Both include their own visuals and work offline.
Pivot_Desk.pptx is an editable nine-slide PowerPoint companion for personal use only.
The captioned demo.webm shows fictional applicant data and a real AI review; it is an automated demonstration, not a human trial.

source.zip and Pivot_Desk_Submission.zip are local backups, not Canvas attachments. See submission_checklist.md for exact instructions and evidence limits.

user_trial.html is a local, anonymous timer worksheet for a real applicant. It contains no completed results. Do not submit empty observations as user evidence.

The source ZIP excludes private runtime state, real .env files, dependencies and virtualenvs. Follow its README to run the app. The owner reports instructor permission to use any model. The documented Astra setup and its measured results are unchanged. No Canvas upload has been performed.
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
    "github_url.txt",
    "canvas_upload/report.html",
    "canvas_upload/slides.html",
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
    "repository_url": repo_url,
    "canvas_submission_mode": "file_upload_only",
    "canvas_upload_directory": "canvas_upload",
    "canvas_required_files": canvas_files,
    "canvas_optional_file": "testing video",
    "canvas_submission_completed": False,
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
